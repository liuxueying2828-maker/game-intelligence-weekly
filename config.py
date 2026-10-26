from pathlib import Path


PROJECT_NAME = "Game Intelligence Weekly"
BASE_DIR = Path(__file__).resolve().parent
MANUAL_INPUT_PATH = BASE_DIR / "manual_sources" / "daily_input.md"
HTML_OUTPUT_PATH = BASE_DIR / "output" / "index.html"
PREVIEW_OUTPUT_PATH = BASE_DIR / "output" / "preview" / "index.html"
PREVIEW_DATA_PATH = BASE_DIR / "output" / "preview" / "data.json"

MAX_ITEMS_FOR_ANALYSIS = 120
EVENT_HORIZON_DAYS = 180
RSS_ITEMS_PER_FEED = 12
GOOGLE_NEWS_ITEMS_PER_QUERY = 6
SECTION_ORDER = ["platform", "ai", "sports", "retail"]
# Search recent updates first, then recover older announcements whose event is
# still relevant to the rolling six-month opportunity pipeline.
SEARCH_WINDOWS_DAYS = [14, 30, 90, 180]
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
KEYWORD_LIBRARY_PATH = BASE_DIR / "data" / "keyword_library.json"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_SEARCH_MODEL = "gemini-2.5-flash"
GEMINI_DEEP_RESEARCH_AGENT = "deep-research-preview-04-2026"
GEMINI_SEARCH_MAX_ITEMS_PER_TASK = 18
GEMINI_DEEP_RESEARCH_TIMEOUT_SECONDS = 1200

CHINA_RELEVANCE_KEYWORDS = [
    "china", "chinese game", "china-developed", "中国", "国产游戏", "中国游戏", "国服",
] + PRIORITY_COMPANIES

DOMESTIC_EVENT_KEYWORDS = [
    "announcement", "reveal", "license", "approval", "pre-registration", "beta", "test", "launch", "release",
    "首曝", "版号", "获批", "预约", "测试", "封测", "公测", "定档", "上线", "发售",
]
CONFIRMED_OVERSEAS_KEYWORDS = [
    "global launch", "overseas launch", "global release", "global pre-registration", "overseas beta",
    "north america", "europe", "japan", "korea", "southeast asia", "launches in",
    "海外上线", "海外发行", "全球上线", "全球预约", "海外封测", "海外公测", "欧美服", "日服", "韩服", "东南亚",
]
EARLY_OVERSEAS_SIGNAL_KEYWORDS = [
    "english website", "global website", "official discord", "official youtube", "overseas social media",
    "localization", "regional rating", "trademark", "publishing partner", "global publisher", "gamescom", "gdc", "tgs", "g-star",
    "英文官网", "海外官网", "海外社媒", "海外账号", "本地化", "海外代理", "海外招聘", "海外商标", "地区评级", "海外展会",
]
OVERSEAS_MARKETING_KEYWORDS = [
    "user acquisition", "global campaign", "overseas marketing", "creator campaign", "influencer", "brand partnership",
    "crossover", "collaboration", "community campaign", "launch campaign", "media buying",
    "海外营销", "海外投放", "买量", "品牌联名", "IP 联动", "达人营销", "创作者", "海外社区", "发行营销", "预注册营销",
]

SEARCH_QUERIES = {"platform": [], "ai": [], "sports": [], "retail": []}
for _company_group in [PRIORITY_COMPANIES[index:index + 4] for index in range(0, len(PRIORITY_COMPANIES), 4)]:
    _companies = " OR ".join(f'"{company}"' for company in _company_group)
    _chinese_group = any("\u3400" <= char <= "\u9fff" for company in _company_group for char in company)
    if _chinese_group:
        SEARCH_QUERIES["platform"].append(f"({_companies}) 首曝 版号 预约 测试 公测 定档 上线")
        SEARCH_QUERIES["ai"].append(f"({_companies}) 海外上线 全球预约 海外测试 欧美服 日服 韩服 东南亚")
        SEARCH_QUERIES["sports"].append(f"({_companies}) 英文官网 海外社媒 本地化 海外代理 海外招聘")
        SEARCH_QUERIES["retail"].append(f"({_companies}) 海外营销 海外投放 买量 联名 达人营销")
    else:
        SEARCH_QUERIES["platform"].append(f"({_companies}) announcement license beta release")
        SEARCH_QUERIES["ai"].append(f"({_companies}) global launch overseas release global pre-registration")
        SEARCH_QUERIES["sports"].append(f"({_companies}) English website overseas social localization publishing partner")
        SEARCH_QUERIES["retail"].append(f"({_companies}) overseas marketing creator campaign user acquisition")

SEARCH_QUERIES["platform"] += ["国产游戏 新作 首曝 版号 预约 测试 公测 定档 上线", "Chinese developed game announcement beta release"]
SEARCH_QUERIES["ai"] += ["国产游戏 海外上线 全球预约 欧美服 日服 韩服 东南亚", "Chinese developed game global launch overseas beta pre-registration"]
SEARCH_QUERIES["sports"] += ["国产游戏 英文官网 海外社媒 海外代理 本地化 海外招聘", "Chinese game global website Discord localization publishing partner"]
SEARCH_QUERIES["retail"] += ["国产游戏 海外营销 投放 买量 达人 联名", "Chinese game overseas marketing user acquisition influencer campaign"]

EXPANDED_SEARCH_QUERIES = {
    "platform": ["中国游戏 新品 版号 测试 上线", "Chinese game new title beta release"],
    "ai": ["国产游戏 出海 上线", "Chinese game overseas launch"],
    "sports": ["国产游戏 海外官网 社媒 本地化", "Chinese game overseas signals"],
    "retail": ["国产游戏 海外推广 营销", "Chinese game global marketing campaign"],
}
GOOGLE_NEWS_QUERIES = SEARCH_QUERIES

LOW_VALUE_KEYWORDS = [
    "walkthrough", "cheat", "tier list", "giveaway code", "gacha result", "unconfirmed leak", "plot spoiler",
    "攻略", "剧透", "礼包码", "抽卡结果", "未证实爆料", "玩家传闻",
]

FILTER_PROFILES = {
    "platform": {
        "include_any": CHINA_RELEVANCE_KEYWORDS + DOMESTIC_EVENT_KEYWORDS,
        "require_any": DOMESTIC_EVENT_KEYWORDS,
        "required_groups": [CHINA_RELEVANCE_KEYWORDS, DOMESTIC_EVENT_KEYWORDS],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["版号", "定档", "公测", "上线", "release date", "open beta"],
    },
    "ai": {
        "include_any": CHINA_RELEVANCE_KEYWORDS + CONFIRMED_OVERSEAS_KEYWORDS,
        "require_any": CONFIRMED_OVERSEAS_KEYWORDS,
        "required_groups": [CHINA_RELEVANCE_KEYWORDS, CONFIRMED_OVERSEAS_KEYWORDS],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["global launch", "overseas beta", "global pre-registration", "海外上线", "海外封测", "全球预约"],
    },
    "sports": {
        "include_any": CHINA_RELEVANCE_KEYWORDS + EARLY_OVERSEAS_SIGNAL_KEYWORDS,
        "require_any": EARLY_OVERSEAS_SIGNAL_KEYWORDS,
        "required_groups": [CHINA_RELEVANCE_KEYWORDS, EARLY_OVERSEAS_SIGNAL_KEYWORDS],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["english website", "official discord", "publishing partner", "英文官网", "海外社媒", "海外代理"],
    },
    "retail": {
        "include_any": CHINA_RELEVANCE_KEYWORDS + OVERSEAS_MARKETING_KEYWORDS,
        "require_any": OVERSEAS_MARKETING_KEYWORDS,
        "required_groups": [CHINA_RELEVANCE_KEYWORDS, OVERSEAS_MARKETING_KEYWORDS],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["user acquisition", "overseas marketing", "creator campaign", "海外投放", "买量", "达人营销"],
    },
}
