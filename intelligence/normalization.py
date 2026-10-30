import json
import re
from datetime import date
from urllib.parse import urlparse

from config import MIN_SECTION_CANDIDATES, SECTION_ORDER


SECTION_ALIASES = {
    "platform_intelligence": ["platform", "platform_intelligence", "platform_watch"],
    "ai_technology": ["ai", "ai_technology", "ai_watch"],
    "sports_outdoor": ["sports", "sports_outdoor", "sports_and_outdoor"],
    "retail_innovation": ["retail", "retail_innovation", "retail_trends", "retail_watch"],
    "pending_confirmation": ["pending", "pending_confirmation", "needs_confirmation"],
}


_DIRECT_TO_CONSUMER_ABBR = "D" + "TC"
_DECA_DIRECT_PHRASE = "对" + "迪卡侬而言"


FORBIDDEN_OUTPUT_REPLACEMENTS = (
    (_DECA_DIRECT_PHRASE + "，", "给迪卡侬的启示是，"),
    (_DECA_DIRECT_PHRASE, "给迪卡侬的启示"),
    (_DIRECT_TO_CONSUMER_ABBR + " Opportunity", "业务启示"),
    (_DIRECT_TO_CONSUMER_ABBR + " opportunity", "业务启示"),
    (_DIRECT_TO_CONSUMER_ABBR + "机会", "业务启示"),
    (_DIRECT_TO_CONSUMER_ABBR + " 策略", "数字商业能力"),
    (_DIRECT_TO_CONSUMER_ABBR + "策略", "数字商业能力"),
    (_DIRECT_TO_CONSUMER_ABBR, "数字商业"),
)


def parse_dashboard_json(raw_text):
    text = _strip_json_fence(raw_text)
    try:
        return normalize_dashboard_data(json.loads(text))
    except json.JSONDecodeError:
        extracted = _extract_json_object(text)
        if extracted:
            try:
                return normalize_dashboard_data(json.loads(extracted))
            except json.JSONDecodeError:
                pass
        return build_dashboard_fallback(raw_text)


def normalize_dashboard_data(data):
    normalized = {
        "date": data.get("date", ""),
        "headline": data.get("headline") or data.get("one_thing_worth_watching") or "今日信号已更新",
        "platform_intelligence": _filter_overseas_cards(_filter_reliable_cards(_normalize_cards(_first_section(data, "platform_intelligence")))),
        "ai_technology": _filter_overseas_cards(_filter_reliable_cards(_normalize_ai_cards(_first_section(data, "ai_technology")))),
        "sports_outdoor": _filter_overseas_cards(_filter_reliable_cards(_normalize_cards(_first_section(data, "sports_outdoor")))),
        "retail_innovation": _filter_overseas_cards(_filter_reliable_cards(_normalize_cards(_first_section(data, "retail_innovation")))),
        "pending_confirmation": _filter_reliable_cards(_normalize_cards(_first_section(data, "pending_confirmation"))),
        "one_thing_worth_watching": data.get("one_thing_worth_watching") or data.get("headline") or "今日信号已更新",
    }
    if data.get("parse_warning"):
        normalized["parse_warning"] = data["parse_warning"]
    normalized = _ensure_identity_format(_sanitize_dashboard_terms(normalized))
    normalized = remove_unidentified_game_cards(normalized)
    return refresh_time_sensitive_recommendations(normalized)


_QUARTER_RANGE_RE = re.compile(
    r"Q([1-4])\s*[-–—~至]\s*Q([1-4])(?:\s*(20\d{2}))?",
    re.IGNORECASE,
)
_QUARTER_SINGLE_RE = re.compile(
    r"(?<![A-Za-z0-9])Q([1-4])(?![A-Za-z0-9])(?:\s*(20\d{2}))?",
    re.IGNORECASE,
)


def refresh_time_sensitive_recommendations(data, today=None):
    """Refresh quarter-based advice without changing factual event dates.

    Source dates such as ``Q4 2026`` remain untouched. Only recommendation
    fields are rewritten, so an old planning window cannot be presented as a
    current call to action in a previously generated preview.
    """
    today = today or date.today()
    for section_key in SECTION_ALIASES:
        for card in data.get(section_key, []):
            if not isinstance(card, dict):
                continue
            opportunity = str(card.get("marketing_opportunity") or "").strip()
            if opportunity:
                opportunity = _clean_legacy_stale_suffix(opportunity)
                refreshed = _refresh_quarter_advice(opportunity, today)
                card["marketing_opportunity"] = refreshed
                points = card.get("summary_points") or []
                card["summary_points"] = [
                    _refresh_marketing_summary_point(point, opportunity, refreshed)
                    for point in points
                ]
    return data


def _clean_legacy_stale_suffix(text):
    return re.sub(
        r"[；;]\s*原(?:\s*Q[1-4](?:\s*[-–—~至]\s*Q[1-4])?)?\s*建议窗口已结束，"
        r"当前需依据最新官方节点重新评估。?$",
        "。",
        text,
        flags=re.IGNORECASE,
    )


def _refresh_quarter_advice(text, today):
    current_quarter = (today.month - 1) // 3 + 1
    current_key = (today.year, current_quarter)
    range_match = _QUARTER_RANGE_RE.search(text)
    if range_match:
        start_quarter = int(range_match.group(1))
        end_quarter = int(range_match.group(2))
        year = int(range_match.group(3) or today.year)
        if (year, end_quarter) < current_key:
            action = _remove_quarter_intervention_phrase(text, range_match.span())
            return _stale_window_recommendation(action)
        if year == today.year and start_quarter <= current_quarter <= end_quarter:
            return _replace_current_quarter_phrase(text, range_match.span())

    single_match = _QUARTER_SINGLE_RE.search(text)
    if single_match:
        quarter = int(single_match.group(1))
        year = int(single_match.group(2) or today.year)
        if (year, quarter) < current_key:
            action = _remove_quarter_intervention_phrase(text, single_match.span())
            return _stale_window_recommendation(action)
        if (year, quarter) == current_key:
            return _replace_current_quarter_phrase(text, single_match.span())
    return text


def _stale_window_recommendation(action):
    if action:
        return f"当前需依据最新官方节点重新评估：{action}。"
    return "当前需依据最新官方节点重新评估营销机会。"


def _remove_quarter_intervention_phrase(text, span):
    start, end = span
    before = text[:start].rstrip(" ，、；;：:")
    after = text[end:]
    after = re.sub(r"^\s*(?:时间段|期间|窗口)?\s*(?:重点)?\s*(?:介入|跟进|投放)?", "", after)
    result = f"{before}{after}".strip(" ，、；;：:。")
    result = re.sub(r"(?:建议|计划)\s*$", "", result).strip(" ，、；;：:。")
    return result


def _replace_current_quarter_phrase(text, span):
    start, end = span
    before = text[:start]
    after = text[end:]
    after = re.sub(r"^\s*(?:时间段|期间|窗口)?", "", after)
    separator = "" if not after or after.startswith(("，", "。", "；", ";", "：", ":")) else " "
    return f"{before}本季度剩余窗口{separator}{after}"


def _refresh_marketing_summary_point(point, old, new):
    if not isinstance(point, str) or old not in point:
        return point
    return point.replace(old, new)


def _ensure_identity_format(data):
    missing_prefix = "[未找到厂商-未找到中文名-English name not found]"
    for section_key in SECTION_ALIASES:
        valid_cards = []
        for card in data.get(section_key, []):
            if not isinstance(card, dict):
                continue
            key = "title" if section_key == "ai_technology" else "name"
            value = str(card.get(key) or "").strip()
            if not value.startswith("["):
                # Models occasionally follow the requested identity fields but
                # omit only the square brackets. Preserve that useful identity
                # instead of incorrectly labeling every field as missing.
                if value.count("-") >= 2:
                    card[key] = f"[{value}]"
                else:
                    card[key] = f"{missing_prefix} {value}".strip()
            if section_key == "ai_technology":
                card["name"] = card[key]
            # Reject source snippets or truncated model output masquerading as
            # an identity. Every published card must have all three fields and
            # a closing bracket: [company-Chinese title-English title].
            if not re.match(r"^\[[^\]]+-.+-.+\]", str(card.get(key) or "")):
                continue
            valid_cards.append(card)
        data[section_key] = valid_cards
    return data


def remove_unidentified_game_cards(data):
    """Drop records that cannot be tied to a concrete game product."""
    for section_key in SECTION_ALIASES:
        retained = []
        for card in data.get(section_key, []):
            if not isinstance(card, dict):
                continue
            identity = str(card.get("title") or card.get("name") or "")
            if _has_identifiable_game_name(identity):
                retained.append(card)
        data[section_key] = retained
    return data


def _has_identifiable_game_name(identity):
    match = re.match(r"^\[([^\]]+)\]", identity.strip())
    if not match:
        return False
    parts = [part.strip().lower() for part in match.group(1).split("-", 2)]
    if len(parts) < 3:
        return False
    chinese_missing = parts[1] in {"", "未找到中文名", "中文名未公布", "unknown"}
    english_missing = parts[2] in {
        "", "english name not found", "english name not announced", "unknown"
    }
    return not (chinese_missing and english_missing)


def _first_section(data, canonical_key):
    for key in SECTION_ALIASES[canonical_key]:
        if data.get(key):
            return data[key]
    return []


def _normalize_cards(items):
    cards = []
    for item in items[:8]:
        if isinstance(item, str):
            cards.append(
                {
                    "name": "Signal",
                    "news": _clean_text(item),
                    "summary_points": _summary_points(item),
                    "why_this_matters": "该信号值得进一步阅读原文确认。",
                    "trend": "Signal",
                    "link": "",
                }
            )
            continue

        cards.append(
            {
                "name": item.get("name") or item.get("platform") or item.get("topic") or "Signal",
                "news": _clean_text(item.get("news") or item.get("signal") or ""),
                "summary_points": _summary_points(
                    item.get("summary_points")
                    or item.get("summary")
                    or item.get("news")
                    or item.get("signal")
                    or item.get("why_this_matters")
                    or item.get("why")
                    or ""
                ),
                "why_this_matters": _clean_text(item.get("why_this_matters") or item.get("why") or ""),
                "trend": item.get("trend") or "Trend",
                "link": item.get("link") or "",
                **_event_fields(item),
            }
        )
    return cards


def _normalize_ai_cards(items):
    cards = []
    for item in items[:8]:
        if isinstance(item, str):
            cards.append(
                {
                    "name": "AI 能力变化",
                    "title": "AI 能力变化",
                    "capability": _clean_text(item),
                    "summary_points": _summary_points(item),
                    "industry_impact": "该技术信号需要结合原文进一步判断行业影响。",
                    "trend": "AI 能力",
                    "link": "",
                }
            )
            continue

        title = item.get("title") or item.get("name") or item.get("topic") or item.get("platform") or "AI 能力变化"
        capability = item.get("capability") or item.get("news") or item.get("signal") or ""
        industry_impact = item.get("industry_impact") or item.get("why_this_matters") or item.get("why") or ""
        cards.append(
            {
                "name": title,
                "title": title,
                "capability": _clean_text(capability),
                "summary_points": _summary_points(
                    item.get("summary_points")
                    or item.get("summary")
                    or [capability, industry_impact]
                ),
                "industry_impact": _clean_text(industry_impact),
                "trend": item.get("trend") or "AI 能力",
                "link": item.get("link") or "",
                **_event_fields(item),
            }
        )
    return cards


def _event_fields(item):
    normalized_stage = _canonical_stage(item.get("normalized_stage"), item.get("official_event_name"))
    return {
        "candidate_id": item.get("candidate_id") or "",
        "official_event_name": item.get("official_event_name") or "",
        "normalized_stage": normalized_stage,
        "overseas_stage": _normalize_overseas_stage(item.get("overseas_stage"), normalized_stage),
        "domestic_reference": item.get("domestic_reference") or "",
        "sequence_label": item.get("sequence_label") if normalized_stage == "cbt" else "不适用",
        "access_type": item.get("access_type") or "unknown",
        "test_goal": item.get("test_goal") or "unknown",
        "event_date": item.get("event_date") or "",
        "regions": item.get("regions") or [],
        "platforms": item.get("platforms") or [],
        "verification_status": item.get("verification_status") or "",
        "source_urls": item.get("source_urls") or [],
        "marketing_readiness": item.get("marketing_readiness") or "",
        "marketing_opportunity": item.get("marketing_opportunity") or "",
    }


def _normalize_overseas_stage(value, normalized_stage):
    allowed = {
        "overseas_preparation", "overseas_reveal", "overseas_test",
        "overseas_preregistration", "overseas_launch", "overseas_live_ops",
    }
    if value in allowed:
        return value
    return ""


def _canonical_stage(value, official_name=""):
    text = f"{value or ''} {official_name or ''}".lower()
    canonical = {"first_reveal", "technical_test", "cbt", "preregistration", "open_beta_or_launch", "soft_launch", "major_update", "anniversary", "collaboration", "regional_expansion", "platform_expansion"}
    if value in canonical:
        return value
    rules = (
        (("公测", "上线", "launch", "open beta", "obt", "release"), "open_beta_or_launch"),
        (("预约", "pre-registration", "pre-register", "wishlist"), "preregistration"),
        (("首曝", "曝光", "first reveal", "gameplay reveal", "实机演示"), "first_reveal"),
        (("封测", "closed beta", "cbt", "测试招募", "终测", "一测", "二测", "三测"), "cbt"),
        (("技术测试", "压力测试", "试玩", "playtest", "technical test"), "technical_test"),
        (("大版本", "资料片", "赛季", "major update", "expansion"), "major_update"),
        (("周年", "anniversary"), "anniversary"),
        (("联名", "联动", "collaboration", "crossover"), "collaboration"),
        (("海外发行", "地区发行", "regional"), "regional_expansion"),
        (("新平台", "platform"), "platform_expansion"),
    )
    for terms, stage in rules:
        if any(term in text for term in terms):
            return stage
    return "unknown"


def build_dashboard_fallback(raw_text):
    return {
        "date": "",
        "headline": "AI 返回内容未能解析为标准 JSON",
        "platform_intelligence": [],
        "ai_technology": [],
        "sports_outdoor": [],
        "retail_innovation": [],
        "pending_confirmation": [],
        "one_thing_worth_watching": "AI 返回内容未能解析为标准 JSON，已按 empty 结果处理。",
        "parse_warning": "AI JSON parse failed; rendered source-based fallback content.",
    }


def build_source_fallback(source_items, warning):
    data = build_dashboard_fallback("")
    data["headline"] = "AI 暂时不可用，已基于真实候选来源生成临时预览"
    data["one_thing_worth_watching"] = data["headline"]
    data["parse_warning"] = warning
    return ensure_minimum_dashboard_signals(data, source_items)


def ensure_minimum_dashboard_signals(data, source_items):
    normalized = normalize_dashboard_data(data)
    items_by_domain = _items_by_domain(source_items)

    for domain in SECTION_ORDER:
        section_key = _canonical_section_key(domain)
        cards = normalized.get(section_key, [])
        minimum = MIN_SECTION_CANDIDATES.get(domain, 0)
        if len(cards) >= minimum:
            continue

        used_links = {card.get("link") for card in cards if isinstance(card, dict) and card.get("link")}
        for item in items_by_domain.get(domain, []):
            if len(cards) >= minimum:
                break
            if item.get("link") in used_links:
                continue
            cards.append(_fallback_card_from_item(domain, item))
            if item.get("link"):
                used_links.add(item.get("link"))

        normalized[section_key] = cards

    return _sanitize_dashboard_terms(normalized)


def _sanitize_dashboard_terms(value):
    if isinstance(value, str):
        text = value
        for old, new in FORBIDDEN_OUTPUT_REPLACEMENTS:
            text = text.replace(old, new)
        return text
    if isinstance(value, list):
        return [_sanitize_dashboard_terms(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_dashboard_terms(item) for key, item in value.items()}
    return value


def _filter_reliable_cards(cards):
    # A publishable card must be traceable to a page found by Web Search.
    # This also prevents manual notes or name-catalog facts from leaking into
    # the report if the analysis model emits them without source evidence.
    return [card for card in cards if str(card.get("link") or "").strip()]


def _filter_overseas_cards(cards):
    """Keep domestic milestones out of the primary overseas timeline."""
    accepted = []
    for card in cards:
        if card.get("overseas_stage"):
            accepted.append(card)
            continue
        text = " ".join([
            str(card.get("news") or ""), str(card.get("capability") or ""),
            str(card.get("marketing_opportunity") or ""),
            " ".join(str(point) for point in (card.get("summary_points") or [])),
        ]).lower()
        if "海外节点：未公布" in text or "海外节点: 未公布" in text:
            continue
        signals = ("海外", "全球", "英文区", "欧美", "北美", "欧洲", "日本", "韩国", "东南亚", "global", "overseas")
        if any(signal in text for signal in signals):
            accepted.append(card)
    return accepted


def _is_google_news_redirect(link):
    host = urlparse(str(link or "")).netloc.lower()
    return host == "news.google.com"


def _items_by_domain(items):
    grouped = {section: [] for section in SECTION_ORDER}
    for item in items:
        domain = item.get("domain")
        if domain not in grouped:
            continue
        grouped[domain].append(item)

    for section_items in grouped.values():
        section_items.sort(
            key=lambda item: (
                1 if item.get("origin_type") == "manual" else 0,
                item.get("priority", 1),
                item.get("relevance_score", 0),
                -(item.get("search_window_days") or 0),
                item.get("published_date", ""),
            ),
            reverse=True,
        )
    return grouped


def _canonical_section_key(domain):
    return {
        "platform": "platform_intelligence",
        "ai": "ai_technology",
        "sports": "sports_outdoor",
        "retail": "retail_innovation",
        "pending": "pending_confirmation",
    }[domain]


def _fallback_card_from_item(domain, item):
    title = item.get("title") or "Signal"
    if not title.startswith("["):
        title = f"{item.get('identity') or '[未找到厂商-未找到中文名-English name not found]'} {title}"
    raw_summary = item.get("summary") or title
    summary = _clean_text(raw_summary)
    link = item.get("link") or ""
    trend = _fallback_trend(item)
    points = _summary_points(raw_summary)

    if domain == "ai":
        return {
            "name": _shorten(title, 42),
            "title": _shorten(_business_ai_title(title), 42),
            "capability": summary,
            "summary_points": points,
            "industry_impact": "",
            "trend": trend,
            "link": link,
        }

    return {
        "name": _shorten(_company_or_topic(title), 32),
        "news": summary,
        "summary_points": points,
        "why_this_matters": "",
        "trend": trend,
        "link": link,
    }


def _business_ai_title(title):
    lowered = title.lower()
    if "search" in lowered:
        return "AI 搜索能力进入业务流程"
    if "customer service" in lowered or "客服" in title:
        return "AI 客服能力继续增强"
    if "shopping" in lowered or "购物" in title:
        return "AI 购物助手能力继续增强"
    if "agent" in lowered:
        return "AI Agent 可处理连续业务任务"
    if "workflow" in lowered or "operations" in lowered or "运营" in title:
        return "AI 正在进入企业工作流"
    return title


def _company_or_topic(title):
    return re.split(r"[-|:：]", title, maxsplit=1)[0].strip() or title


def _fallback_trend(item):
    if item.get("fallback_reason"):
        return "高相关候选;周度补充"
    window_days = item.get("search_window_days")
    if window_days:
        return f"近{window_days}天;行业情报"
    return "行业情报"


def _strip_json_fence(raw_text):
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_json_object(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start : end + 1]


def _shorten(text, limit):
    text = re.sub(r"\s+", " ", str(text)).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _clean_text(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def _summary_points(value):
    text = ""
    if isinstance(value, list):
        points = [_clean_text(item) for item in value if _clean_text(item)]
        text = " ".join(points)
    else:
        raw_text = str(value or "").strip()
        line_points = _manual_structured_points(raw_text)
        if line_points:
            points = line_points
        else:
            text = _clean_text(raw_text)
            points = [part.strip() for part in re.split(r"(?<=[。！？.!?])\s*", text) if part.strip()]
        if len(points) <= 1 and text:
            points = [text]
    return points[:6]


def _manual_structured_points(text):
    points = []
    metadata_prefixes = ("Category:", "Keywords:", "Company:", "Source:", "Date:")
    for raw_line in text.splitlines():
        line = _clean_text(raw_line)
        if not line or line.startswith(metadata_prefixes):
            continue
        if line.startswith("Content:"):
            line = line[len("Content:") :].strip()
        line = re.sub(r"^(?:[-*•]|\d+[.)、]|[一二三四五六七八九十]+[、.])\s*", "", line).strip()
        if line:
            points.append(line)
    return points if len(points) > 1 else []
