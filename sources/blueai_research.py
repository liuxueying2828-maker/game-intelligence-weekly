from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import os
import re
from urllib.parse import urlparse

from config import (
    BLUEAI_BASE_URL,
    BLUEAI_MODEL,
    BLUEAI_SEARCH_MAX_ITEMS_PER_TASK,
    BLUEAI_SEARCH_WORKERS,
    BLUEAI_VERIFICATION_BATCH_SIZE,
    BLUEAI_VERIFICATION_WORKERS,
)
from sources.keyword_library import (
    build_search_tasks,
    format_companies,
    format_games,
    format_keywords,
    format_sources,
    load_keyword_library,
)


def fetch_blueai_research_items(keyword_library_path):
    """Discover candidates with web search, then independently verify them."""
    api_key = os.getenv("BLUEAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing BLUEAI_API_KEY environment variable.")

    library = load_keyword_library(keyword_library_path)
    candidates = _run_discovery_tasks(api_key, library)
    if not candidates:
        return []
    verified = _run_verification_batches(api_key, candidates)
    return _deduplicate(_to_source_item(item) for item in verified)


def _client(api_key):
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Missing openai package. Run: python3 -m pip install -r requirements.txt") from exc
    return OpenAI(
        api_key=api_key,
        base_url=os.getenv("BLUEAI_BASE_URL") or BLUEAI_BASE_URL,
        timeout=180.0,
        max_retries=2,
    )


def _run_discovery_tasks(api_key, library):
    items = []
    tasks = build_search_tasks(library)
    with ThreadPoolExecutor(max_workers=BLUEAI_SEARCH_WORKERS) as executor:
        futures = {
            executor.submit(_run_discovery, api_key, library, task): task
            for task in tasks
        }
        for future in as_completed(futures):
            task = futures[future]
            try:
                task_items = future.result()
                items.extend(task_items)
                print(f"  BlueAI Web Search {task['id']}: {len(task_items)} candidates")
            except Exception as exc:
                print(f"  BlueAI Web Search {task['id']} failed: {exc}")
    return _deduplicate(items)


def _run_discovery(api_key, library, task):
    with _client(api_key) as client:
        response = client.responses.create(
            model=os.getenv("BLUEAI_MODEL") or BLUEAI_MODEL,
            tools=[{"type": "web_search", "search_context_size": "high"}],
            include=["web_search_call.action.sources"],
            input=_build_discovery_prompt(library, task),
        )
    _require_web_search(response, task["id"])
    records = _parse_records(response.output_text, "items")
    consulted_urls = _extract_web_search_sources(response)
    print(f"  BlueAI Web Search {task['id']}: consulted {len(consulted_urls)} source URLs")
    for record in records:
        record["search_language"] = task["language"]
        record["search_task"] = task["id"]
        # Kept as audit evidence for the verification stage. These URLs are
        # never published as if they all supported every candidate.
        record["search_audit_urls"] = consulted_urls[:40]
    return records[:BLUEAI_SEARCH_MAX_ITEMS_PER_TASK]


def _run_verification_batches(api_key, candidates):
    batches = [
        candidates[index:index + BLUEAI_VERIFICATION_BATCH_SIZE]
        for index in range(0, len(candidates), BLUEAI_VERIFICATION_BATCH_SIZE)
    ]
    results_by_index = {}
    with ThreadPoolExecutor(max_workers=BLUEAI_VERIFICATION_WORKERS) as executor:
        futures = {
            executor.submit(_verify_batch, api_key, batch, index): index
            for index, batch in enumerate(batches, start=1)
        }
        for future in as_completed(futures):
            index = futures[future]
            results_by_index[index] = future.result()
            print(f"  BlueAI verification batch {index}/{len(batches)}: {len(results_by_index[index])} checked")

    results = []
    for index in sorted(results_by_index):
        results.extend(results_by_index[index])
    return results


def _verify_batch(api_key, batch, index):
    verified = []
    last_error = None
    for attempt in range(1, 3):
        try:
            with _client(api_key) as client:
                response = client.responses.create(
                    model=os.getenv("BLUEAI_MODEL") or BLUEAI_MODEL,
                    tools=[{"type": "web_search", "search_context_size": "high"}],
                    include=["web_search_call.action.sources"],
                    input=_build_verification_prompt(batch, retry=attempt > 1),
                )
            _require_web_search(response, f"verification_{index}")
            verified = _parse_records(response.output_text, "items")
            consulted_urls = _extract_web_search_sources(response)
            print(f"  BlueAI verification batch {index}: consulted {len(consulted_urls)} source URLs")
            if verified:
                return verified
            last_error = "verification response contained no parseable items"
        except Exception as exc:
            last_error = str(exc)
            print(f"  BlueAI verification batch {index} attempt {attempt} failed: {exc}")
    print(f"  BlueAI verification batch {index}: moved {len(batch)} candidates to pending confirmation")
    return [_pending_from_candidate(item, last_error) for item in batch]


def _build_discovery_prompt(library, task):
    rules = library["search_rules"]
    return f"""
You are the candidate-discovery stage for Game Intelligence Weekly. Today is {datetime.now():%Y-%m-%d}.
Search the public web in {task['language']} using multiple queries. Do not limit yourself to Google News.

Business goal: find China-developed games and Chinese publishers with domestic milestones, overseas release plans, overseas preparation signals, exhibitions, major updates, or brand/IP collaborations that may create overseas advertising demand.
Time scope: announcements from the last {rules['lookback_days']} days plus events expected in the next {rules['forward_days']} days. Keep active undated signals.

Discovery rules:
- Search official publisher/studio/game sites, official social accounts and store pages first; then reputable Chinese and international trade media and event sites.
- Keep domestic and overseas launch dates separate. Search Chinese and English names and regional releases independently.
- Include first reveal, first gameplay, license approval, pre-registration, technical test, CBT, OB/open beta, launch, major version, overseas store/social/localization/rating/publishing deal, exhibition, brand/IP collaboration and overseas campaign.
- Never invent or translate an English title. Mark it missing if no official match is found.
- This is candidate discovery, not publication approval. Preserve source URLs for later verification.
- A static store page, wishlist, long-existing website/social account, localization support page or undated pre-registration page is not a new event. Keep it only when a source establishes that it was newly opened/updated in the last {rules['lookback_days']} days or it supports a specific event in the next {rules['forward_days']} days.
- Exclude past launches and old campaigns that have no newly announced change or future confirmed milestone. “Ongoing marketing potential” alone is not an event.
- Return every qualifying event found, up to {BLUEAI_SEARCH_MAX_ITEMS_PER_TASK}.
- For matrix tasks, cover EVERY entity in Focus entities. Run separate searches as needed and do not stop after finding results for the first entity.
- For public_social_web tasks, use site-specific searches. Public official posts, video descriptions, channel announcements, store pages and Discord invite pages are valid early signals; never claim access to private groups or login-only content.

Return only JSON:
{{"items":[{{"candidate_id":"stable short id","company_cn":"","company_en":"","game_cn":"","game_en":"","event_type":"","section":"platform|ai|sports|retail","title":"","summary":"","published_date":"YYYY-MM-DD or original wording","event_date":"YYYY-MM-DD/quarter/window/original wording","regions":[],"name_match_status":"matched|english_name_missing|chinese_name_missing|company_missing|unmatched","source_urls":[{{"url":"https://direct-page","source_name":"","source_type":"official|wire|reliable_media|trade_media|store|event|aggregator|social"}}]}}]}}

Goal: {task['goal']}

Search mode: {task.get('search_mode', 'broad_discovery')}

Focus entities or domains:
{chr(10).join('- ' + value for value in task.get('focus_entities', [])) or '- Broad industry discovery'}

Keywords:
{format_keywords(library, task)}

Priority companies:
{format_companies(library)}

Tracked games:
{format_games(library)}

Priority source families:
{format_sources(library)}
""".strip()


def _build_verification_prompt(batch, retry=False):
    payload = json.dumps(batch, ensure_ascii=False, indent=2)
    return f"""
You are the independent fact-checking stage for Game Intelligence Weekly. Today is {datetime.now():%Y-%m-%d}.
For every candidate below, use web search again. Open or locate direct sources, verify the event date, publication date, regions, numbers, Chinese/English title match, and any later correction.
You MUST issue web_search calls in this response; do not answer from model memory.{" This is a retry because the previous response did not call web search." if retry else ""}

Evidence policy:
- Prefer publisher/studio/game official announcements, official stores and official event pages.
- Next prefer Reuters, AP, Bloomberg and established game-industry media.
- A record is verified only when two genuinely independent sources support the material claim. An official primary announcement plus an independent reliable report qualifies; copied/aggregated reports do not count as independent.
- A credible claim with only one non-official source is reported_unconfirmed and must say 据报道/尚未获官方确认.
- A single official social post, official channel/video description, official store page or official game site may be retained as reported_unconfirmed early evidence. Do not discard it merely because a second report does not exist.
- Social evidence must be public and directly accessible. Never claim to have read private Discord channels, closed groups or login-only posts.
- Verification must establish the actual change and its date. Existing store/social presence without a dated opening, update or future milestone must be pending_confirmation or excluded from the publishable result.
- A leak, conflicting dates/numbers/names, an inaccessible claim, or otherwise insufficient evidence is pending_confirmation and must not enter a main section.
- Correct candidate errors rather than repeating them. Never invent an English title.
- Return direct article/announcement URLs, not search-result URLs, whenever available.

Return only JSON, one output for every input candidate:
{{"items":[{{"candidate_id":"","company_cn":"","company_en":"","game_cn":"","game_en":"","event_type":"","section":"platform|ai|sports|retail","title":"","summary":"","published_date":"","event_date":"","regions":[],"name_match_status":"matched|english_name_missing|chinese_name_missing|company_missing|unmatched","verification_status":"verified|reported_unconfirmed|pending_confirmation","verification_notes":"brief evidence decision and conflicts/corrections","sources":[{{"url":"https://direct-page","source_name":"","source_type":"official|wire|reliable_media|trade_media|store|event|social","independent":true}}]}}]}}

Candidates:
{payload}
""".strip()


def _pending_from_candidate(candidate, error):
    sources = []
    for source in candidate.get("source_urls") or []:
        if not isinstance(source, dict):
            continue
        sources.append({**source, "independent": False})
    return {
        **candidate,
        "verification_status": "pending_confirmation",
        "verification_notes": f"二次网页核验未完成：{error or 'unknown verification error'}",
        "sources": sources,
    }


def _require_web_search(response, label):
    output = getattr(response, "output", []) or []
    if not any(getattr(item, "type", "") == "web_search_call" for item in output):
        raise RuntimeError(f"BlueAI response for {label} did not contain a web_search_call")


def _extract_web_search_sources(response):
    """Return the complete URL list exposed by Responses web_search calls."""
    urls = []
    seen = set()
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", "") != "web_search_call":
            continue
        action = getattr(item, "action", None)
        for source in getattr(action, "sources", []) or []:
            url = getattr(source, "url", None)
            if url is None and isinstance(source, dict):
                url = source.get("url")
            url = str(url or "").strip()
            if url and url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def _parse_records(raw_text, key):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(raw_text or "").strip())
    candidates = [text]
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        candidates.append(text[start:end + 1])
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
            records = payload.get(key) if isinstance(payload, dict) else None
            if isinstance(records, list):
                return [item for item in records if isinstance(item, dict)]
        except json.JSONDecodeError:
            continue
    return []


def _to_source_item(item):
    sources = [source for source in (item.get("sources") or []) if isinstance(source, dict)]
    status = _enforce_verification_status(item.get("verification_status"), sources)
    direct_urls = [source.get("url") for source in sources if source.get("url")]
    identity = _identity(item)
    notes = item.get("verification_notes") or ""
    if status == "reported_unconfirmed":
        notes = f"据报道/尚未获官方确认。{notes}"
    return {
        "source": "BlueAI verified web search: " + "; ".join(source.get("source_name", "Unknown") for source in sources),
        "domain": "pending" if status == "pending_confirmation" else (item.get("section") if item.get("section") in {"platform", "ai", "sports", "retail"} else "platform"),
        "origin_type": f"blueai_{status}",
        "published_date": item.get("published_date") or "",
        "title": f"{identity} {item.get('title', '').strip()}",
        "summary": " ".join(filter(None, [
            item.get("summary", "").strip(),
            f"核验状态：{status}。",
            f"核验说明：{notes}" if notes else "",
            f"事件：{item.get('event_type') or '未分类'}。",
            f"事件日期：{item.get('event_date') or '未公布'}。",
            f"地区：{', '.join(item.get('regions') or []) or '未公布'}。",
            "来源：" + "；".join(direct_urls) if direct_urls else "来源链接待确认。",
        ])),
        "link": direct_urls[0] if direct_urls else "",
        "source_urls": direct_urls,
        "verification_status": status,
        "verification_notes": notes,
        "priority": {"verified": 7, "reported_unconfirmed": 4, "pending_confirmation": 2}.get(status, 2),
        "identity": identity,
        "company_cn": item.get("company_cn") or "",
        "company_en": item.get("company_en") or "",
        "game_cn": item.get("game_cn") or "",
        "game_en": item.get("game_en") or "",
        "name_match_status": item.get("name_match_status") or "unmatched",
    }


def _enforce_verification_status(requested_status, sources):
    """Do not trust the model label unless the returned evidence supports it."""
    independent_sources = set()
    for source in sources:
        if source.get("independent") is not True:
            continue
        url = str(source.get("url") or "").strip()
        host = urlparse(url).netloc.lower().removeprefix("www.") if url else ""
        identity = host or str(source.get("source_name") or "").strip().lower()
        if identity:
            independent_sources.add(identity)

    if requested_status == "verified" and len(independent_sources) >= 2:
        return "verified"
    if requested_status in {"verified", "reported_unconfirmed"} and len(independent_sources) == 1:
        return "reported_unconfirmed"
    return "pending_confirmation"


def _identity(item):
    company = item.get("company_cn") or item.get("company_en") or "未找到厂商"
    game_cn = item.get("game_cn") or "未找到中文名"
    game_en = item.get("game_en") or "English name not found"
    return f"[{company}-{game_cn}-{game_en}]"


def _deduplicate(items):
    result, seen = [], set()
    for item in items:
        key = item.get("link") or (item.get("candidate_id"), item.get("event_type")) or item.get("title", "").lower()
        if not key or str(key) in seen:
            continue
        seen.add(str(key))
        result.append(item)
    return result
