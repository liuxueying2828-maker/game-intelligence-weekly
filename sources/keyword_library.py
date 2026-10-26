import json


def load_keyword_library(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unable to load keyword library: {path}") from exc

    required = ("event_keywords", "priority_companies", "tracked_games", "source_priorities", "search_rules")
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise RuntimeError(f"Keyword library is missing required sections: {', '.join(missing)}")
    return data


def build_search_tasks(library):
    return [
        {
            "id": "zh_product_pipeline",
            "language": "zh",
            "sections": ["release_and_testing", "major_updates"],
            "goal": "发现中国游戏的首曝、测试、公测、OB、定档、上线、发售及大版本更新，尤其关注未来六个月节点。",
        },
        {
            "id": "zh_overseas_opportunity",
            "language": "zh",
            "sections": ["overseas_launch", "early_overseas_signals", "marketing_and_partnerships"],
            "goal": "发现国产游戏出海节点、海外发行前置信号、展会曝光、品牌联名和海外广告机会。",
        },
        {
            "id": "en_global_pipeline",
            "language": "en",
            "sections": ["release_and_testing", "major_updates", "overseas_launch"],
            "goal": "Find English-language evidence of global launches, tests, release dates and major updates for China-developed games.",
        },
        {
            "id": "en_global_marketing",
            "language": "en",
            "sections": ["early_overseas_signals", "marketing_and_partnerships"],
            "goal": "Find overseas store pages, social accounts, trade-show appearances, publishing deals, collaborations and marketing campaigns for China-developed games.",
        },
    ]


def format_keywords(library, task):
    groups = []
    for section in task["sections"]:
        words = library["event_keywords"][section][task["language"]]
        groups.append(f"{section}: {', '.join(words)}")
    return "\n".join(groups)


def format_companies(library):
    return "; ".join(
        " / ".join(filter(None, [company.get("name_cn"), company.get("name_en"), *company.get("aliases", [])]))
        for company in library["priority_companies"]
    )


def format_games(library):
    return "\n".join(
        f"- {game.get('company', '')}: {game.get('title_cn', '')} / {game.get('title_en', '')}; aliases: {', '.join(game.get('aliases', []))}"
        for game in library["tracked_games"]
    )


def format_sources(library):
    return "\n".join(
        f"{group}: {', '.join(sources)}"
        for group, sources in library["source_priorities"].items()
    )
