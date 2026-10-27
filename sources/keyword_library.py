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
    tasks = [
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

    # Broad prompts are useful for discovery, but they do not guarantee that
    # every priority company or tracked title is searched. Add an explicit
    # bilingual query matrix in bounded batches so coverage remains affordable.
    for language in ("zh", "en"):
        for index, companies in enumerate(_chunks(library["priority_companies"], 4), start=1):
            tasks.append({
                "id": f"{language}_companies_{index}",
                "language": language,
                "sections": ["release_and_testing", "overseas_launch", "early_overseas_signals", "marketing_and_partnerships"],
                "goal": _company_goal(companies, language),
                "focus_entities": [_company_label(company) for company in companies],
                "search_mode": "priority_company_matrix",
            })

        for index, games in enumerate(_chunks(library["tracked_games"], 3), start=1):
            tasks.append({
                "id": f"{language}_games_{index}",
                "language": language,
                "sections": ["release_and_testing", "major_updates", "overseas_launch", "early_overseas_signals", "marketing_and_partnerships"],
                "goal": _game_goal(games, language),
                "focus_entities": [_game_label(game) for game in games],
                "search_mode": "tracked_game_matrix",
            })

    tasks.extend([
        {
            "id": "zh_social_signals",
            "language": "zh",
            "sections": ["early_overseas_signals", "marketing_and_partnerships", "release_and_testing"],
            "goal": "专项搜索国产游戏官方微博、微信公众号、Bilibili、TapTap和好游快爆中的首曝、预约、测试、海外账号、联名和创作者计划。",
            "focus_entities": ["weibo.com", "mp.weixin.qq.com", "bilibili.com", "taptap.cn", "3839.com"],
            "search_mode": "public_social_web",
        },
        {
            "id": "en_social_signals",
            "language": "en",
            "sections": ["early_overseas_signals", "marketing_and_partnerships", "release_and_testing"],
            "goal": "Search public official YouTube, X, Facebook, Discord invite and Reddit announcement pages for overseas launch, pre-registration, creator and collaboration signals from Chinese games.",
            "focus_entities": ["youtube.com", "x.com", "facebook.com", "discord.com", "reddit.com"],
            "search_mode": "public_social_web",
        },
    ])
    return tasks


def _chunks(items, size):
    return [items[index:index + size] for index in range(0, len(items), size)]


def _company_label(company):
    return " / ".join(filter(None, [company.get("name_cn"), company.get("name_en"), *company.get("aliases", [])]))


def _game_label(game):
    return " / ".join(filter(None, [game.get("title_cn"), game.get("title_en"), *game.get("aliases", [])]))


def _company_goal(companies, language):
    entities = "; ".join(_company_label(company) for company in companies)
    if language == "zh":
        return f"逐一搜索这些中国游戏厂商最近180天和未来180天的产品、出海和营销信号，不得只搜索其中一家：{entities}"
    return f"Search every listed Chinese game company separately for global release and marketing signals; do not stop after the first company: {entities}"


def _game_goal(games, language):
    entities = "; ".join(_game_label(game) for game in games)
    if language == "zh":
        return f"逐一用中英文名搜索这些重点游戏的发行、测试、版本、展会、社媒和联名动态：{entities}"
    return f"Search every tracked game by both its Chinese and official English names for releases, tests, updates, events, social accounts and collaborations: {entities}"


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
