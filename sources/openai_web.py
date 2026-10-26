from datetime import datetime
import json
import os

from config import OPENAI_MODEL, OPENAI_WEB_SEARCH_MAX_ITEMS_PER_TASK
from sources.keyword_library import (
    build_search_tasks,
    format_companies,
    format_games,
    format_keywords,
    format_sources,
    load_keyword_library,
)


SEARCH_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company_cn": {"type": "string"},
                    "company_en": {"type": "string"},
                    "game_cn": {"type": "string"},
                    "game_en": {"type": "string"},
                    "event_type": {"type": "string"},
                    "section": {"type": "string", "enum": ["platform", "ai", "sports", "retail"]},
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "url": {"type": "string"},
                    "source_name": {"type": "string"},
                    "published_date": {"type": "string"},
                    "event_date": {"type": "string"},
                    "regions": {"type": "array", "items": {"type": "string"}},
                    "name_match_status": {
                        "type": "string",
                        "enum": ["matched", "english_name_missing", "chinese_name_missing", "company_missing", "unmatched"],
                    },
                    "evidence_level": {"type": "string", "enum": ["official", "reliable_media", "secondary"]},
                },
                "required": [
                    "company_cn", "company_en", "game_cn", "game_en", "event_type", "section", "title",
                    "summary", "url", "source_name", "published_date", "event_date", "regions",
                    "name_match_status", "evidence_level"
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}


def fetch_openai_web_items(keyword_library_path):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Missing openai package. Run: python3 -m pip install -r requirements.txt") from exc

    library = load_keyword_library(keyword_library_path)
    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL") or OPENAI_MODEL
    items = []

    for task in build_search_tasks(library):
        try:
            response = client.responses.create(
                model=model,
                tools=[{"type": "web_search", "search_context_size": "high"}],
                tool_choice="required",
                include=["web_search_call.action.sources"],
                input=_build_search_prompt(library, task),
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "game_intelligence_web_results",
                        "strict": True,
                        "schema": SEARCH_RESULT_SCHEMA,
                    }
                },
                max_output_tokens=12000,
            )
            payload = json.loads(response.output_text)
            task_items = payload.get("items", [])[:OPENAI_WEB_SEARCH_MAX_ITEMS_PER_TASK]
            items.extend(_to_source_item(item, task) for item in task_items)
            print(f"  OpenAI web search {task['id']}: {len(task_items)} items")
        except Exception as exc:
            print(f"  OpenAI web search {task['id']} failed: {exc}")

    return _deduplicate(items)


def _build_search_prompt(library, task):
    rules = library["search_rules"]
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""
You are the web discovery stage for Game Intelligence Weekly. Today is {today}.

Goal: {task['goal']}

Use web search repeatedly, in both the target language ({task['language']}) and the other language when useful. Search the open web, not only Google News. Prioritize official game/publisher pages, official social posts and store pages, then specialist industry media and trade-event sites. Search both listed priority companies/games and newly announced China-developed games not yet in the library.

Time window:
- Publications from the last {rules['lookback_days']} days.
- Events scheduled during the next {rules['forward_days']} days.
- Undated or later plans may be included only when they are still-active overseas-release signals.

Hard inclusion rules:
- A China-based developer/publisher or a China-developed game must be verifiably involved.
- Include concrete first reveals, tests, OB/open beta, launches, major updates, overseas store/social/localization signals, trade-show appearances, publishing deals, brand/IP collaborations and overseas marketing activity.
- “OB” means open beta/open testing only when the page also identifies a game or game company.
- Every item must have a direct source URL. Prefer the original announcement over an aggregator.
- Do not invent or translate an English game name. If no reliable official English title is found, return an empty game_en and set name_match_status to english_name_missing.
- If a Chinese title or company cannot be matched, leave that field empty and mark the corresponding status.
- Return all qualifying, materially distinct items found, up to {OPENAI_WEB_SEARCH_MAX_ITEMS_PER_TASK}. Deduplicate syndicated copies.

Section mapping:
- platform = China product pipeline: reveal, license, test, domestic launch, major version.
- ai = confirmed overseas/global launch, pre-registration, test, region or date.
- sports = early overseas signal: English/global site, store/social account, localization, rating, partner, trade show.
- retail = overseas marketing, media buying, creators, brand/IP collaboration or campaign.

Keyword groups (search concepts, not exact-match requirements):
{format_keywords(library, task)}

Priority companies and aliases:
{format_companies(library)}

Tracked game-name reference:
{format_games(library)}

Priority source families:
{format_sources(library)}

The title field should describe the event only; identity formatting will be applied by code. Keep dates exactly as the source states when precision is uncertain.
""".strip()


def _to_source_item(item, task):
    identity = _identity(item)
    regions = ", ".join(item.get("regions") or []) or "未公布"
    summary = " ".join(filter(None, [
        item.get("summary", "").strip(),
        f"事件：{item.get('event_type') or '未分类'}。",
        f"事件日期：{item.get('event_date') or '未公布'}。",
        f"地区：{regions}。",
        f"名称匹配：{_match_label(item.get('name_match_status'))}。",
        f"证据级别：{item.get('evidence_level') or '未标注'}。",
    ]))
    return {
        "source": f"OpenAI Web ({task['language']}): {item.get('source_name') or 'Unknown source'}",
        "domain": item.get("section") or "platform",
        "origin_type": "openai_web",
        "published_date": item.get("published_date") or "",
        "search_language": task["language"],
        "search_task": task["id"],
        "title": f"{identity} {item.get('title', '').strip()}",
        "summary": summary,
        "link": item.get("url") or "",
        "priority": 5 if item.get("evidence_level") == "official" else 4,
        "identity": identity,
        "company_cn": item.get("company_cn") or "",
        "company_en": item.get("company_en") or "",
        "game_cn": item.get("game_cn") or "",
        "game_en": item.get("game_en") or "",
        "name_match_status": item.get("name_match_status") or "unmatched",
    }


def _identity(item):
    company = item.get("company_cn") or item.get("company_en") or "未找到厂商"
    game_cn = item.get("game_cn") or "未找到中文名"
    game_en = item.get("game_en") or "English name not found"
    return f"[{company}-{game_cn}-{game_en}]"


def _match_label(status):
    return {
        "matched": "中英文名已匹配",
        "english_name_missing": "未找到可靠英文名",
        "chinese_name_missing": "未找到可靠中文名",
        "company_missing": "未找到可靠厂商",
        "unmatched": "名称未完全匹配",
    }.get(status, "名称未完全匹配")


def _deduplicate(items):
    result = []
    seen = set()
    for item in items:
        key = item.get("link") or item.get("title", "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
