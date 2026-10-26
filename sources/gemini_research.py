from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import os
import re
import time

from config import (
    GEMINI_DEEP_RESEARCH_AGENT,
    GEMINI_DEEP_RESEARCH_TIMEOUT_SECONDS,
    GEMINI_SEARCH_MAX_ITEMS_PER_TASK,
    GEMINI_SEARCH_MODEL,
)
from sources.keyword_library import (
    build_search_tasks,
    format_companies,
    format_games,
    format_keywords,
    format_sources,
    load_keyword_library,
)


def fetch_gemini_research_items(keyword_library_path):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable.")

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("Missing google-genai package. Run: python3 -m pip install -r requirements.txt") from exc

    library = load_keyword_library(keyword_library_path)
    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_SEARCH_MODEL") or GEMINI_SEARCH_MODEL
    items = _run_google_search_tasks(client, model, library)

    if _env_true("ENABLE_GEMINI_DEEP_RESEARCH"):
        items.extend(_run_deep_research_tasks(api_key, library))
    else:
        print("  Gemini Deep Research: disabled (set ENABLE_GEMINI_DEEP_RESEARCH=true to run Chinese + English research)")

    return _deduplicate(items)


def _run_google_search_tasks(client, model, library):
    items = []
    for task in build_search_tasks(library):
        try:
            response = client.interactions.create(
                model=model,
                input=_build_search_prompt(library, task, deep=False),
                tools=[{"type": "google_search"}, {"type": "url_context"}],
            )
            task_items = _parse_items(response.output_text)[:GEMINI_SEARCH_MAX_ITEMS_PER_TASK]
            items.extend(_to_source_item(item, task, "gemini_google_search") for item in task_items)
            print(f"  Gemini Google Search {task['id']}: {len(task_items)} items")
        except Exception as exc:
            print(f"  Gemini Google Search {task['id']} failed: {exc}")
    return items


def _run_deep_research_tasks(api_key, library):
    language_tasks = [
        {
            "id": "deep_research_zh",
            "language": "zh",
            "sections": list(library["event_keywords"]),
            "goal": "深度搜索中文互联网中未来六个月值得跟进的国产游戏发行、出海和营销机会。",
        },
        {
            "id": "deep_research_en",
            "language": "en",
            "sections": list(library["event_keywords"]),
            "goal": "Deeply research English-language sources for overseas launch and marketing opportunities involving China-developed games in the next six months.",
        },
    ]
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(_run_one_deep_research, api_key, library, task): task
            for task in language_tasks
        }
        for future in as_completed(futures):
            task = futures[future]
            try:
                task_items = future.result()
                results.extend(task_items)
                print(f"  Gemini Deep Research {task['language']}: {len(task_items)} items")
            except Exception as exc:
                print(f"  Gemini Deep Research {task['language']} failed: {exc}")
    return results


def _run_one_deep_research(api_key, library, task):
    from google import genai

    client = genai.Client(api_key=api_key)
    agent = os.getenv("GEMINI_DEEP_RESEARCH_AGENT") or GEMINI_DEEP_RESEARCH_AGENT
    interaction = client.interactions.create(
        agent=agent,
        input=_build_search_prompt(library, task, deep=True),
        tools=[{"type": "google_search"}, {"type": "url_context"}],
        agent_config={
            "type": "deep-research",
            "thinking_summaries": "auto",
            "collaborative_planning": False,
        },
        background=True,
        store=True,
    )
    deadline = time.monotonic() + GEMINI_DEEP_RESEARCH_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        interaction = client.interactions.get(interaction.id)
        if interaction.status == "completed":
            raw_text = interaction.output_text or interaction.steps[-1].content[0].text
            parsed = _parse_items(raw_text)
            if parsed:
                return [_to_source_item(item, task, "gemini_deep_research") for item in parsed]
            return [_report_fallback_item(raw_text, task)]
        if interaction.status == "failed":
            raise RuntimeError(str(getattr(interaction, "error", "unknown Deep Research error")))
        time.sleep(10)
    raise TimeoutError(f"Deep Research exceeded {GEMINI_DEEP_RESEARCH_TIMEOUT_SECONDS} seconds")


def _build_search_prompt(library, task, deep):
    today = datetime.now().strftime("%Y-%m-%d")
    rules = library["search_rules"]
    mode = "Perform iterative deep research" if deep else "Use Google Search and URL Context repeatedly"
    return f"""
You are the web discovery stage for Game Intelligence Weekly. Today is {today}.
{mode}. Target language: {task['language']}.

Goal: {task['goal']}

Search official game and publisher sites, stores, official social channels, Chinese game-industry media, global trade media and event sites. Do not rely only on Google News. Search priority companies and tracked games, but also find newly announced China-developed games not yet in the library.

Time scope: publications from the last {rules['lookback_days']} days and events in the next {rules['forward_days']} days. Include still-active undated overseas-release signals.

Rules:
- A Chinese developer/publisher or China-developed game must be verifiably involved.
- Include first reveals, first gameplay, technical tests, CBT/OB/open beta, launches, major versions, overseas stores/social accounts, localization, ratings, publishing deals, exhibitions, brand/IP collaborations and overseas campaigns.
- OB means open beta only when a game or game company is identified.
- Prefer direct original URLs and keep each materially distinct event.
- Never translate or invent an English game title. Use an empty game_en and english_name_missing when no official match exists.
- Return every qualifying item found, up to {GEMINI_SEARCH_MAX_ITEMS_PER_TASK}.

Return only one JSON object in this exact shape, without Markdown:
{{"items":[{{"company_cn":"","company_en":"","game_cn":"","game_en":"","event_type":"","section":"platform|ai|sports|retail","title":"","summary":"","url":"https://direct-source","source_name":"","published_date":"","event_date":"","regions":[],"name_match_status":"matched|english_name_missing|chinese_name_missing|company_missing|unmatched","evidence_level":"official|reliable_media|secondary"}}]}}

Section mapping: platform=domestic product/reveal/test/update; ai=confirmed overseas launch/test/date/region; sports=early overseas signal/store/social/localization/event; retail=overseas marketing/brand collaboration/campaign.

Keywords:
{format_keywords(library, task)}

Companies:
{format_companies(library)}

Tracked games:
{format_games(library)}

Priority sources:
{format_sources(library)}
""".strip()


def _parse_items(raw_text):
    text = str(raw_text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    candidates = [text]
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        candidates.append(text[start:end + 1])
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
            if isinstance(payload, dict) and isinstance(payload.get("items"), list):
                return payload["items"]
        except json.JSONDecodeError:
            continue
    return []


def _to_source_item(item, task, origin_type):
    identity = _identity(item)
    return {
        "source": f"Gemini {'Deep Research' if origin_type == 'gemini_deep_research' else 'Google Search'} ({task['language']}): {item.get('source_name') or 'Unknown source'}",
        "domain": item.get("section") if item.get("section") in {"platform", "ai", "sports", "retail"} else "platform",
        "origin_type": origin_type,
        "published_date": item.get("published_date") or "",
        "search_language": task["language"],
        "search_task": task["id"],
        "title": f"{identity} {item.get('title', '').strip()}",
        "summary": " ".join(filter(None, [
            item.get("summary", "").strip(),
            f"事件：{item.get('event_type') or '未分类'}。",
            f"事件日期：{item.get('event_date') or '未公布'}。",
            f"地区：{', '.join(item.get('regions') or []) or '未公布'}。",
            f"名称匹配：{item.get('name_match_status') or 'unmatched'}。",
        ])),
        "link": item.get("url") or "",
        "priority": 6 if origin_type == "gemini_deep_research" else (5 if item.get("evidence_level") == "official" else 4),
        "identity": identity,
        "company_cn": item.get("company_cn") or "",
        "company_en": item.get("company_en") or "",
        "game_cn": item.get("game_cn") or "",
        "game_en": item.get("game_en") or "",
        "name_match_status": item.get("name_match_status") or "unmatched",
    }


def _report_fallback_item(report, task):
    urls = re.findall(r"https?://[^\s)\]}>\"]+", report or "")
    return {
        "source": f"Gemini Deep Research ({task['language']})",
        "domain": "sports",
        "origin_type": "gemini_deep_research",
        "published_date": datetime.now().strftime("%Y-%m-%d"),
        "search_language": task["language"],
        "search_task": task["id"],
        "title": "[未找到厂商-未找到中文名-English name not found] Deep Research 补充报告",
        "summary": (report or "")[:12000],
        "link": urls[0] if urls else "",
        "priority": 5,
    }


def _identity(item):
    company = item.get("company_cn") or item.get("company_en") or "未找到厂商"
    game_cn = item.get("game_cn") or "未找到中文名"
    game_en = item.get("game_en") or "English name not found"
    return f"[{company}-{game_cn}-{game_en}]"


def _deduplicate(items):
    result, seen = [], set()
    # When normal Search and Deep Research discover the same source, keep the
    # more deeply researched record while retaining distinct source URLs.
    for item in sorted(items, key=lambda value: value.get("priority", 0), reverse=True):
        key = item.get("link") or item.get("title", "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _env_true(name):
    return (os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "on"}
