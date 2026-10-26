import json

from sources.common import make_item


CONFIRMED_NODE_TERMS = (
    "上线", "发行", "公测", "封测", "预约", "q1", "q2", "q3", "q4",
    "launch", "release", "beta", "pre-registration",
)
EARLY_SIGNAL_TERMS = (
    "官网", "社媒", "矩阵", "代理", "本地化", "招聘", "商标", "评级", "展会",
    "website", "social", "discord", "publisher", "localization", "trademark", "rating",
)


def fetch_catalog_items(path):
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    items = []
    for entry in entries:
        title = _display_title(entry)
        company = entry.get("company") or "未录入"
        platforms = ", ".join(entry.get("platforms", [])) or "Unknown"
        china_status = entry.get("china_status") or "未录入"
        overseas_status = entry.get("overseas_status") or "未录入"
        last_verified = entry.get("last_verified") or "2026-10-26"
        base_summary = (
            f"Rolling six-month pipeline record. Company: {company}. Platforms: {platforms}. "
            f"China status: {china_status}. Overseas status: {overseas_status}. "
            f"Last verified: {last_verified}. Treat as ongoing monitoring, not a new announcement."
        )

        domestic_item = make_item(
            source="Curated Game Pipeline",
            title=f"[{company}-{entry.get('title_cn') or '未找到中文名'}-{entry.get('title_en') or 'English name not found'}] Domestic Pipeline",
            summary=base_summary,
            domain="platform",
            origin_type="catalog",
            priority=3,
            search_window_days=180,
        )
        domestic_item.update(_identity_fields(entry, company))
        items.append(domestic_item)

        overseas_lower = overseas_status.lower()
        if any(term in overseas_lower for term in ("未公布", "暂无", "no date", "not announced")) and any(
            term in overseas_lower for term in EARLY_SIGNAL_TERMS
        ):
            domain = "sports"
            suffix = "Early Overseas Signal"
        elif any(term in overseas_lower for term in CONFIRMED_NODE_TERMS):
            domain = "ai"
            suffix = "Confirmed Overseas Node"
        elif any(term in overseas_lower for term in EARLY_SIGNAL_TERMS):
            domain = "sports"
            suffix = "Early Overseas Signal"
        else:
            continue

        overseas_item = make_item(
            source="Curated Game Pipeline",
            title=f"[{company}-{entry.get('title_cn') or '未找到中文名'}-{entry.get('title_en') or 'English name not found'}] {suffix}",
            summary=base_summary,
            domain=domain,
            origin_type="catalog",
            priority=3,
            search_window_days=180,
        )
        overseas_item.update(_identity_fields(entry, company))
        items.append(overseas_item)
    return items


def _display_title(entry):
    title_cn = entry.get("title_cn") or "未命名产品"
    title_en = entry.get("title_en") or "English name not announced"
    return f"{title_cn} / {title_en}"


def _identity_fields(entry, company):
    return {
        "identity": f"[{company}-{entry.get('title_cn') or '未找到中文名'}-{entry.get('title_en') or 'English name not found'}]",
        "company_cn": company,
        "company_en": "",
        "game_cn": entry.get("title_cn") or "",
        "game_en": entry.get("title_en") or "",
        "name_match_status": "matched" if entry.get("title_en") else "english_name_missing",
    }
