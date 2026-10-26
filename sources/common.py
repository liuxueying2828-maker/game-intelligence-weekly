import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape


TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def clean_text(value):
    if not value:
        return ""
    text = TAG_RE.sub(" ", str(value))
    text = unescape(text)
    return SPACE_RE.sub(" ", text).strip()


def parse_date(entry):
    date_value = (
        entry.get("published")
        or entry.get("updated")
        or entry.get("created")
        or entry.get("pubDate")
    )
    if not date_value:
        return None

    try:
        parsed = parsedate_to_datetime(date_value)
        if parsed and not parsed.tzinfo:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (TypeError, ValueError, IndexError, OverflowError):
        return None


def iso_date(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value or ""


def coerce_datetime(value):
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    else:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_within_days(value, days, now=None):
    parsed = coerce_datetime(value)
    if not parsed:
        return True
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return parsed >= current.astimezone(timezone.utc) - timedelta(days=days)


def make_item(
    source,
    title,
    summary,
    link="",
    published_date=None,
    domain="retail",
    origin_type="rss",
    priority=1,
    search_window_days=None,
):
    return {
        "source": source,
        "title": clean_text(title),
        "summary": clean_text(summary),
        "link": link or "",
        "published_date": iso_date(published_date),
        "domain": domain,
        "origin_type": origin_type,
        "priority": priority,
        "search_window_days": search_window_days,
    }


def text_contains_any(text, keywords):
    lower_text = text.lower()
    return any(keyword.lower() in lower_text for keyword in keywords)

def keyword_match_count(text, keywords):
    lower_text = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lower_text)


def score_section_item(title, summary, profile):
    text = f"{title} {summary}"
    hard_exclude_any = profile.get("hard_exclude_any", [])
    if hard_exclude_any and text_contains_any(text, hard_exclude_any):
        return -1

    include_score = keyword_match_count(text, profile.get("include_any", []))
    require_score = keyword_match_count(text, profile.get("require_any", []))
    override_score = keyword_match_count(text, profile.get("override_any", []))
    exclude_score = keyword_match_count(text, profile.get("exclude_any", []))

    score = include_score * 3 + require_score * 4 + override_score * 5 - exclude_score * 6
    if include_score == 0 and profile.get("include_any"):
        score -= 5
    if require_score == 0 and profile.get("require_any"):
        score -= 4
    return score


def should_keep_section_item(title, summary, profile):
    text = f"{title} {summary}"
    include_any = profile.get("include_any", [])
    require_any = profile.get("require_any", [])
    exclude_any = profile.get("exclude_any", [])
    hard_exclude_any = profile.get("hard_exclude_any", [])
    override_any = profile.get("override_any", [])

    if hard_exclude_any and text_contains_any(text, hard_exclude_any):
        return False

    if include_any and not text_contains_any(text, include_any):
        return False
    if require_any and not text_contains_any(text, require_any):
        return False

    has_override = text_contains_any(text, override_any)
    if exclude_any and text_contains_any(text, exclude_any) and not has_override:
        return False

    return True


# Backward-compatible wrapper for older tests/imports.
def contains_signal_keyword(title, summary, keywords):
    return text_contains_any(f"{title} {summary}", keywords)


def should_keep_auto_item(
    title,
    summary,
    signal_keywords=None,
    excluded_keywords=None,
    override_keywords=None,
    low_value_keywords=None,
    high_relevance_keywords=None,
    profile=None,
):
    if profile is not None:
        return should_keep_section_item(title, summary, profile)

    legacy_profile = {
        "include_any": signal_keywords or [],
        "require_any": [],
        "exclude_any": (excluded_keywords or []) + (low_value_keywords or []),
        "override_any": (override_keywords or []) + (high_relevance_keywords or []),
    }
    return should_keep_section_item(title, summary, legacy_profile)
