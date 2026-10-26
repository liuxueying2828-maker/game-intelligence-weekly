from pathlib import Path


PROJECT_NAME = "Game Intelligence Weekly"
BASE_DIR = Path(__file__).resolve().parent
MANUAL_INPUT_PATH = BASE_DIR / "manual_sources" / "daily_input.md"
HTML_OUTPUT_PATH = BASE_DIR / "output" / "index.html"
PREVIEW_OUTPUT_PATH = BASE_DIR / "output" / "preview" / "index.html"
PREVIEW_DATA_PATH = BASE_DIR / "output" / "preview" / "data.json"

MAX_ITEMS_FOR_GEMINI = 80
RSS_ITEMS_PER_FEED = 12
GOOGLE_NEWS_ITEMS_PER_QUERY = 6
SECTION_ORDER = ["platform", "ai", "sports", "retail"]
# Publication windows widen to 30 days; articles may announce future 30/90-day events.
SEARCH_WINDOWS_DAYS = [7, 14, 30]
MIN_SECTION_CANDIDATES = {"platform": 5, "ai": 5, "sports": 4, "retail": 4}
MAX_SECTION_CANDIDATES = {"platform": 16, "ai": 16, "sports": 14, "retail": 12}

FEEDS = [
    {"source": "GamesIndustry.biz", "url": "https://www.gamesindustry.biz/feed", "domain": "retail"},
    {"source": "Game Developer", "url": "https://www.gamedeveloper.com/rss.xml", "domain": "retail"},
    {"source": "PocketGamer.biz", "url": "https://www.pocketgamer.biz/rss/", "domain": "platform"},
    {"source": "Gematsu", "url": "https://www.gematsu.com/feed", "domain": "platform"},
    {"source": "Video Games Chronicle", "url": "https://www.videogameschronicle.com/feed/", "domain": "platform"},
    {"source": "PlayStation Blog", "url": "https://blog.playstation.com/feed/", "domain": "platform"},
    {"source": "Xbox Wire", "url": "https://news.xbox.com/en-us/feed/", "domain": "platform"},
    {"source": "MobileGamer.biz", "url": "https://mobilegamer.biz/feed/", "domain": "retail"},
]

# Google News uses separate editions so Chinese queries are not ranked through
# the US English index. Query language is selected automatically by script.
GOOGLE_NEWS_EDITIONS = {
    "en": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
    "zh": {"hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"},
}

PRIORITY_COMPANIES = [
    "腾讯游戏", "网易游戏", "米哈游", "莉莉丝", "叠纸游戏", "库洛游戏", "鹰角网络",
    "蛮啾网络", "灵犀互娱", "雷霆游戏", "西山居", "朝夕光年",
    "Tencent Games", "NetEase Games", "HoYoverse", "Lilith Games", "Papergames",
    "Kuro Games", "Hypergryph", "Manjuu Network", "Seasun Games",
]

GAME_CATALOG_PATH = BASE_DIR / "data" / "game_catalog.json"

SEARCH_QUERIES = {
    # Release & Test Calendar
    "platform": [
        "upcoming video game release date closed beta open beta global launch", "new game announcement pre-registration release calendar",
        "PC mobile console game launches this month", "Steam upcoming game demo playtest release date",
        "China game release date public beta closed beta", "Chinese game license new title release",
        "Tencent Games upcoming release beta", "NetEase Games upcoming global launch", "HoYoverse new game test release",
        "Kuro Games new title beta release", "Papergames new game launch", "Lilith Games new title launch",
        "新游上线 公测 测试 预约", "游戏发售日历 PC 手游 主机", "Steam 新游 Demo 测试",
        "腾讯游戏 上线 公测 封测", "网易游戏 新作 预约 公测", "米哈游 新作 测试 上线",
        "国产游戏 版号 上线日期", "游戏 展会试玩 核聚变",
    ],
    # Global Launch Opportunities
    "ai": [
        "Chinese game overseas launch global pre-registration", "China game global closed beta English release",
        "Chinese mobile game launch North America Europe", "Chinese game launch Japan Korea Southeast Asia",
        "game English official website global social media launch", "game localization global publishing partnership",
        "Tencent game overseas beta global launch", "NetEase game overseas release", "HoYoverse global beta release",
        "国产游戏 出海 海外上线 海外封测", "游戏 全球预约 英文官网 海外社媒",
        "游戏 欧美服 上线", "游戏 日服 韩服 上线", "游戏 东南亚 发行",
        "游戏 海外代理 本地化", "中国游戏 国服 海外 不同步上线",
    ],
    # Marketing & Collaborations
    "sports": [
        "video game brand collaboration announcement", "game IP crossover collaboration event", "gaming brand partnership campaign",
        "game fashion food automotive collaboration", "game anime movie music artist crossover", "game pop-up store offline event collaboration",
        "Fortnite brand collaboration", "Roblox branded experience partnership", "mobile game IP collaboration event",
        "游戏 品牌联名 合作", "游戏 IP 联动 活动", "游戏 快闪店 线下活动",
        "游戏 动漫 影视 艺人 联动", "游戏 汽车 服饰 餐饮 联名", "游戏 品牌营销 案例",
    ],
    # Companies, Platforms & AI
    "retail": [
        "game publisher studio strategy investment acquisition", "Steam Epic PlayStation Xbox platform policy developers",
        "game industry AI production workflow", "generative AI game art video voice localization", "AI NPC game testing player support",
        "Unity AI game development Unreal Engine AI", "NVIDIA ACE game characters", "Roblox AI creation tools",
        "Tencent NetEase game studio strategy", "global game company restructuring publishing strategy",
        "游戏公司 产品线 投资 并购", "游戏发行平台 政策", "AI 游戏开发 美术 视频 配音",
        "AI NPC 游戏测试 本地化", "游戏公司 AI 工作流",
    ],
}

# Add focused watch-list searches without maintaining dozens of near-identical
# strings by hand. Groups keep Google News query length and workflow time sane.
_priority_platform_queries = []
_priority_global_queries = []
for _company_group in [PRIORITY_COMPANIES[index:index + 4] for index in range(0, len(PRIORITY_COMPANIES), 4)]:
    _companies = " OR ".join(f'"{company}"' for company in _company_group)
    _priority_platform_queries.append(
        f"({_companies}) release launch beta playtest 公测 封测 上线 定档"
    )
    _priority_global_queries.append(
        f"({_companies}) global overseas localization 海外 出海 全球预约"
    )

_event_platform_queries = [
    'game "release date" OR "launches on" OR "open beta" OR "closed beta"',
    '游戏 定档 OR 公测 OR 封测 OR 三测 OR 预约开启 OR 全平台上线',
    'Steam "coming soon" demo playtest early access release',
]
SEARCH_QUERIES["platform"] = _priority_platform_queries + _event_platform_queries + SEARCH_QUERIES["platform"]
SEARCH_QUERIES["ai"] = _priority_global_queries + SEARCH_QUERIES["ai"]
SEARCH_QUERIES["sports"] = [
    '游戏 联名 OR 联动 OR 品牌合作 OR 快闪店 OR 主题店',
    'game collaboration OR crossover OR branded experience OR pop-up',
] + SEARCH_QUERIES["sports"]

EXPANDED_SEARCH_QUERIES = {
    "platform": ["upcoming games release beta calendar", "新游 测试 上线 日期"],
    "ai": ["Chinese games global launch overseas", "国产游戏 海外发行"],
    "sports": ["game collaboration brand partnership", "游戏 联名 IP 合作"],
    "retail": ["game company platform AI industry news", "游戏厂商 平台 AI 动向"],
}
GOOGLE_NEWS_QUERIES = SEARCH_QUERIES

LOW_VALUE_KEYWORDS = [
    "walkthrough", "cheat", "tier list", "giveaway code", "gacha result", "unconfirmed leak", "plot spoiler",
    "攻略", "剧透", "礼包码", "抽卡结果", "未证实爆料", "玩家传闻",
]

FILTER_PROFILES = {
    "platform": {
        "include_any": ["game", "gaming", "release", "launch", "beta", "playtest", "demo", "pre-registration", "coming soon", "游戏", "新游", "上线", "公测", "封测", "测试", "预约", "版号", "发售"],
        "require_any": ["release", "launch", "beta", "test", "demo", "pre-registration", "license", "date", "quarter", "上线", "公测", "封测", "测试", "预约", "版号", "日期", "季度"],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["release date", "global launch", "open beta", "closed beta", "上线日期", "公测", "封测", "全球预约"],
    },
    "ai": {
        "include_any": ["overseas", "global", "international", "north america", "europe", "japan", "korea", "southeast asia", "localization", "english website", "出海", "海外", "全球", "欧美", "日服", "韩服", "东南亚", "本地化"],
        "require_any": ["game", "launch", "release", "beta", "pre-registration", "publisher", "social media", "游戏", "上线", "发行", "测试", "预约", "代理", "社媒"],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["global launch", "overseas beta", "global pre-registration", "海外上线", "海外封测", "全球预约"],
    },
    "sports": {
        "include_any": ["collaboration", "crossover", "partnership", "brand", "campaign", "pop-up", "licensed", "activation", "联名", "联动", "合作", "品牌", "快闪", "共创", "ip"],
        "require_any": ["game", "gaming", "player", "event", "experience", "content", "store", "游戏", "玩家", "活动", "内容", "门店", "体验"],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["game collaboration", "game crossover", "branded experience", "游戏联名", "游戏联动", "品牌合作"],
    },
    "retail": {
        "include_any": ["game studio", "game publisher", "steam", "epic games", "playstation", "xbox", "nintendo", "unity", "unreal", "generative ai", "ai npc", "nvidia ace", "investment", "acquisition", "游戏厂商", "游戏工作室", "游戏平台", "生成式 ai", "ai npc", "投资", "并购"],
        "require_any": ["game", "gaming", "developer", "studio", "publisher", "platform", "workflow", "testing", "localization", "游戏", "开发", "工作室", "发行", "平台", "工作流", "测试", "本地化"],
        "exclude_any": LOW_VALUE_KEYWORDS + ["benchmark", "model leaderboard", "模型排行榜", "参数规模"],
        "override_any": ["game development ai", "ai npc", "game testing", "game platform policy", "游戏开发 ai", "游戏平台政策"],
    },
}
