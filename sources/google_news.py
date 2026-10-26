from urllib.parse import quote_plus

import feedparser

from config import (
    EXPANDED_SEARCH_QUERIES,
    FILTER_PROFILES,
    GOOGLE_NEWS_ITEMS_PER_QUERY,
    MAX_SECTION_CANDIDATES,
    MIN_SECTION_CANDIDATES,
    SEARCH_WINDOWS_DAYS,
)
from sources.common import make_item, parse_date, score_section_item, should_keep_section_item


GOOGLE_NEWS_RSS_URL = (
    "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
)


def fetch_google_news_items(search_queries):
    items = []

    for section, queries in _iter_section_queries(search_queries):
        items.extend(_fetch_section_items(section, queries))

    return items


def _fetch_section_items(section, queries):
    profile = FILTER_PROFILES.get(section)
    if not profile:
        return []

    section_items = []
    fallback_items = []
    seen = set()
    fallback_seen = set()
    minimum = MIN_SECTION_CANDIDATES.get(section, 2)
    maximum = MAX_SECTION_CANDIDATES.get(section, 8)

    for window_days in SEARCH_WINDOWS_DAYS:
        _collect_window_items(
            section_items=section_items,
            fallback_items=fallback_items,
            seen=seen,
            fallback_seen=fallback_seen,
            section=section,
            queries=queries,
            profile=profile,
            window_days=window_days,
            maximum=maximum,
            strict=True,
        )
        if len(section_items) >= minimum:
            return section_items[:maximum]

    if len(section_items) < minimum:
        _collect_window_items(
            section_items=section_items,
            fallback_items=fallback_items,
            seen=seen,
            fallback_seen=fallback_seen,
            section=section,
            queries=EXPANDED_SEARCH_QUERIES.get(section, []),
            profile=profile,
            window_days=max(SEARCH_WINDOWS_DAYS),
            maximum=maximum,
            strict=True,
        )

    if len(section_items) < minimum:
        _reuse_highest_scored_items(section_items, fallback_items, seen, minimum, maximum)

    return section_items[:maximum]


def _collect_window_items(
    section_items,
    fallback_items,
    seen,
    fallback_seen,
    section,
    queries,
    profile,
    window_days,
    maximum,
    strict,
):
    for query in queries:
        if len(section_items) >= maximum:
            return

        windowed_query = f"{query} when:{window_days}d"
        url = GOOGLE_NEWS_RSS_URL.format(query=quote_plus(windowed_query))
        parsed_feed = feedparser.parse(url)

        for entry in parsed_feed.entries[:GOOGLE_NEWS_ITEMS_PER_QUERY]:
            title = entry.get("title", "")
            summary = entry.get("summary", "") or entry.get("description", "")
            score = score_section_item(title, summary, profile)
            if score < 0:
                continue

            item = _make_google_news_item(
                entry=entry,
                query=query,
                section=section,
                window_days=window_days,
                score=score,
                priority=2,
                fallback=False,
            )
            dedupe_key = _dedupe_key(item["title"], item["link"])

            if should_keep_section_item(title=title, summary=summary, profile=profile):
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                section_items.append(item)
                if len(section_items) >= maximum:
                    return
                continue

            if strict and dedupe_key not in seen and dedupe_key not in fallback_seen:
                fallback_seen.add(dedupe_key)
                fallback_items.append(
                    _make_google_news_item(
                        entry=entry,
                        query=query,
                        section=section,
                        window_days=window_days,
                        score=score,
                        priority=1.5,
                        fallback=True,
                    )
                )


def _reuse_highest_scored_items(section_items, fallback_items, seen, minimum, maximum):
    ranked_items = sorted(
        fallback_items,
        key=lambda item: (
            item.get("relevance_score", 0),
            -(item.get("search_window_days") or max(SEARCH_WINDOWS_DAYS)),
            item.get("published_date", ""),
        ),
        reverse=True,
    )

    for item in ranked_items:
        if len(section_items) >= minimum or len(section_items) >= maximum:
            return
        dedupe_key = _dedupe_key(item["title"], item["link"])
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        section_items.append(item)


def _make_google_news_item(entry, query, section, window_days, score, priority, fallback):
    item = make_item(
        source=f"Google News: {query}",
        title=entry.get("title", ""),
        summary=entry.get("summary", "") or entry.get("description", ""),
        link=entry.get("link", ""),
        published_date=parse_date(entry),
        domain=section,
        origin_type="google_news",
        priority=priority,
        search_window_days=window_days,
    )
    item["relevance_score"] = score
    if fallback:
        item["fallback_reason"] = "highest_scored_recent_candidate"
    return item


def _dedupe_key(title, link):
    normalized_title = " ".join(str(title).lower().split())
    normalized_link = str(link).strip()
    return normalized_title, normalized_link


def _iter_section_queries(search_queries):
    if isinstance(search_queries, dict):
        for section, queries in search_queries.items():
            yield section, queries
        return

    # Backward compatibility with old [{query, domain}] shape.
    grouped = {}
    for query_config in search_queries:
        grouped.setdefault(query_config.get("domain", "retail"), []).append(query_config["query"])
    for section, queries in grouped.items():
        yield section, queries
