"""Build persistent overseas social profiles separately from weekly events."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import os
import re
from urllib.parse import urlparse

from config import BLUEAI_BASE_URL, BLUEAI_MODEL, SOCIAL_PROFILE_BATCH_SIZE, SOCIAL_PROFILE_REGISTRY_PATH


SOCIAL_PLATFORMS = (
    "official_website", "steam", "steamdb", "x", "facebook", "youtube",
    "instagram", "tiktok", "discord", "bilibili", "weibo", "taptap",
)


def fetch_social_profiles(library):
    """Return one durable profile for every tracked title.

    The weekly event pipeline intentionally drops static social presence. This
    separate pass keeps that presence visible and refreshes it with targeted
    web searches. A checked-in registry provides continuity if a search batch
    fails or a public social page cannot be fetched without login.
    """
    registry = _load_registry()
    api_key = os.getenv("BLUEAI_API_KEY")
    games = library.get("tracked_games") or []
    if not api_key:
        return _merge_profiles(games, [], registry)

    batches = [games[i:i + SOCIAL_PROFILE_BATCH_SIZE] for i in range(0, len(games), SOCIAL_PROFILE_BATCH_SIZE)]
    discovered = []
    with ThreadPoolExecutor(max_workers=min(3, len(batches) or 1)) as executor:
        futures = {executor.submit(_search_batch, api_key, batch, i): i for i, batch in enumerate(batches, 1)}
        for future in as_completed(futures):
            index = futures[future]
            try:
                records = future.result()
                discovered.extend(records)
                print(f"  Social profile batch {index}/{len(batches)}: {len(records)} games checked")
            except Exception as exc:
                print(f"  Social profile batch {index}/{len(batches)} failed: {exc}")
    return _merge_profiles(games, discovered, registry)


def _search_batch(api_key, games, index):
    from openai import OpenAI

    labels = "\n".join(
        f"- {g.get('company', '')}: {g.get('title_cn', '')} / {g.get('title_en', '')}"
        for g in games
    )
    prompt = f"""
Today is {datetime.now():%Y-%m-%d}. Build the persistent overseas social-account profile for EVERY game below.
This is account discovery, not weekly news discovery. Existing accounts must be returned even when they have no recent post.

Games:
{labels}

For each game, issue targeted web searches for its official website, Steam, SteamDB Social Media field, X/Twitter, Facebook, YouTube, Instagram, TikTok, Discord, Bilibili, Weibo and TapTap.
Search the Chinese and official English title separately with site: filters. Use SteamDB only to DISCOVER possible links. Confirm an account through the official game site, official Steam page, the public account page itself, or another reliable directory that identifies the exact game.
Public pages that expose only a URL because of login restrictions may still be recorded as discovered. Never claim to have read private posts or groups.
Return every requested game even if no account is found. Do not invent handles or translate game names.

Return JSON only:
{{"profiles":[{{"company":"","title_cn":"","title_en":"","checked_at":"YYYY-MM-DD","accounts":[{{"platform":"official_website|steam|steamdb|x|facebook|youtube|instagram|tiktok|discord|bilibili|weibo|taptap","url":"https://...","status":"official_confirmed|discovered|access_limited","evidence_url":"https://page-that-supports-the-match","discovery_source":"official_site|steam|steamdb|public_account|reliable_directory|web_search"}}],"notes":""}}]}}
"""
    with OpenAI(
        api_key=api_key,
        base_url=os.getenv("BLUEAI_BASE_URL") or BLUEAI_BASE_URL,
        timeout=180.0,
        max_retries=2,
    ) as client:
        response = client.responses.create(
            model=os.getenv("BLUEAI_MODEL") or BLUEAI_MODEL,
            tools=[{"type": "web_search", "search_context_size": "high"}],
            include=["web_search_call.action.sources"],
            input=prompt,
        )
    if not any(getattr(item, "type", "") == "web_search_call" for item in (getattr(response, "output", []) or [])):
        raise RuntimeError(f"social profile batch {index} did not call web_search")
    return _parse_profiles(response.output_text)


def _parse_profiles(raw):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(raw or "").strip())
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []
    return [p for p in payload.get("profiles", []) if isinstance(p, dict)]


def _load_registry():
    try:
        payload = json.loads(SOCIAL_PROFILE_REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [p for p in payload.get("profiles", []) if isinstance(p, dict)]


def _merge_profiles(games, discovered, registry):
    by_key = {}
    for profile in [*registry, *discovered]:
        key = _profile_key(profile)
        if not key:
            continue
        current = by_key.setdefault(key, {**profile, "accounts": []})
        current.update({k: v for k, v in profile.items() if k != "accounts" and v})
        accounts = {(_account_key(a)): a for a in current.get("accounts", []) if _valid_account(a)}
        for account in profile.get("accounts") or []:
            if _valid_account(account):
                accounts[_account_key(account)] = _normalize_account(account)
        current["accounts"] = sorted(accounts.values(), key=lambda a: SOCIAL_PLATFORMS.index(a["platform"]))

    result = []
    for game in games:
        key = _profile_key(game)
        profile = by_key.get(key, {})
        result.append({
            "company": game.get("company") or profile.get("company") or "",
            "title_cn": game.get("title_cn") or profile.get("title_cn") or "",
            "title_en": game.get("title_en") or profile.get("title_en") or "",
            "checked_at": profile.get("checked_at") or "尚未自动检查",
            "accounts": profile.get("accounts") or [],
            "notes": profile.get("notes") or ("尚未发现公开海外账号" if not profile.get("accounts") else ""),
        })
    return result


def _profile_key(profile):
    return str(profile.get("title_en") or profile.get("title_cn") or "").strip().lower()


def _account_key(account):
    return (str(account.get("platform") or "").lower(), str(account.get("url") or "").rstrip("/").lower())


def _valid_account(account):
    platform = str(account.get("platform") or "").lower()
    url = str(account.get("url") or "").strip()
    return platform in SOCIAL_PLATFORMS and urlparse(url).scheme in {"http", "https"}


def _normalize_account(account):
    platform = str(account.get("platform") or "").lower()
    status = str(account.get("status") or "discovered")
    if status not in {"official_confirmed", "discovered", "access_limited"}:
        status = "discovered"
    if platform == "steamdb" and status == "official_confirmed":
        status = "discovered"
    return {
        "platform": platform,
        "url": str(account.get("url") or "").strip(),
        "status": status,
        "evidence_url": str(account.get("evidence_url") or "").strip(),
        "discovery_source": str(account.get("discovery_source") or "web_search"),
    }
