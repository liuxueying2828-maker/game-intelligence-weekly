from pathlib import Path


PROJECT_NAME = "Game Intelligence Weekly"

BASE_DIR = Path(__file__).resolve().parent
MANUAL_INPUT_PATH = BASE_DIR / "manual_sources" / "daily_input.md"
HTML_OUTPUT_PATH = BASE_DIR / "output" / "index.html"
PREVIEW_OUTPUT_PATH = BASE_DIR / "output" / "preview" / "index.html"
PREVIEW_DATA_PATH = BASE_DIR / "output" / "preview" / "data.json"

MAX_ITEMS_FOR_GEMINI = 28
RSS_ITEMS_PER_FEED = 8
GOOGLE_NEWS_ITEMS_PER_QUERY = 5

# The keys stay unchanged for compatibility with the existing renderer.
SECTION_ORDER = ["platform", "ai", "sports", "retail"]
SEARCH_WINDOWS_DAYS = [3, 7, 14]
MIN_SECTION_CANDIDATES = {"platform": 4, "ai": 4, "sports": 3, "retail": 3}
MAX_SECTION_CANDIDATES = {"platform": 12, "ai": 12, "sports": 10, "retail": 10}

FEEDS = [
    {"source": "GamesIndustry.biz", "url": "https://www.gamesindustry.biz/feed", "domain": "sports"},
    {"source": "Game Developer", "url": "https://www.gamedeveloper.com/rss.xml", "domain": "sports"},
    {"source": "PocketGamer.biz", "url": "https://www.pocketgamer.biz/rss/", "domain": "retail"},
    {"source": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "domain": "ai"},
]

SEARCH_QUERIES = {
    "platform": [
        "Tencent Games new game strategy revenue", "NetEase Games new title global launch", "miHoYo game business overseas",
        "China game industry regulation license", "China game market revenue report", "Chinese game studios global expansion",
        "Tencent NetEase game investment studio", "TapTap game platform developer", "Bilibili game publishing",
        "腾讯游戏 新游戏 战略", "网易游戏 新作 出海", "米哈游 新游戏 业务",
        "中国游戏市场 收入 报告", "游戏版号 政策", "国产游戏 出海",
        "莉莉丝 叠纸 鹰角 库洛", "TapTap 开发者 发行", "B站游戏 发行",
    ],
    "ai": [
        "generative AI game development", "AI NPC video games", "AI game testing automation", "AI game art production",
        "AI game animation voice localization", "AI game coding tools", "AI player support moderation gaming",
        "Unity AI game development", "Unreal Engine generative AI", "Roblox AI creation tools", "NVIDIA ACE game characters",
        "game studio AI workflow", "AI procedural game content", "AI personalization live service games",
        "AI 游戏开发 生成式", "AI NPC 游戏", "AI 游戏美术 动画", "AI 游戏测试",
        "游戏公司 AI 工具 工作流", "AI 游戏本地化 配音", "AI 游戏客服 内容安全",
    ],
    "sports": [
        "Nintendo game business financial results", "Sony PlayStation game strategy", "Microsoft Xbox game studio strategy",
        "Valve Steam platform policy", "Epic Games business strategy", "EA game financial results", "Take-Two Rockstar game release",
        "Ubisoft studio restructuring", "Activision Blizzard game strategy", "Riot Games new title esports",
        "Krafton Nexon Netmarble game business", "Capcom Sega Square Enix financial results", "global video game industry mergers acquisitions",
        "任天堂 游戏 财报", "PlayStation 游戏 战略", "Xbox 工作室 战略", "Steam 平台 政策",
    ],
    "retail": [
        "global video game market report", "mobile game market revenue users", "PC console game market trends",
        "game subscription business model", "cloud gaming market", "game creator economy UGC", "game live streaming esports business",
        "in-game advertising brand partnership", "game user acquisition marketing trends", "game monetization regulation",
        "Steam Epic mobile app store game distribution", "Roblox Fortnite creator economy", "WeChat mini games market",
        "游戏行业 市场规模 用户", "手游 收入 趋势", "小游戏 市场 广告", "游戏 营销 品牌合作",
        "游戏直播 电竞 商业", "UGC 游戏 创作者经济", "游戏发行 渠道 政策",
    ],
}

EXPANDED_SEARCH_QUERIES = {
    "platform": ["China gaming industry news", "Chinese game companies overseas", "国内游戏公司 行业动态"],
    "ai": ["AI in video games industry", "game development AI tools", "游戏行业 AI 应用"],
    "sports": ["global game studio business news", "video game publishers financial results", "全球游戏公司 新闻"],
    "retail": ["video game business market trends", "gaming platform creator economy", "游戏商业化 市场趋势"],
}

GOOGLE_NEWS_QUERIES = SEARCH_QUERIES

LOW_VALUE_KEYWORDS = [
    "walkthrough", "guide", "cheat", "rumor", "leak", "giveaway", "discount", "sale", "tier list", "patch notes",
    "攻略", "剧透", "爆料", "传闻", "礼包码", "抽卡", "折扣", "下载奖励", "版本更新公告",
]

FILTER_PROFILES = {
    "platform": {
        "include_any": ["tencent", "netease", "mihoyo", "hoyoverse", "lilith", "papergames", "hypergryph", "kuro games", "taptap", "bilibili", "china game", "腾讯游戏", "网易游戏", "米哈游", "莉莉丝", "叠纸", "鹰角", "库洛", "游戏版号", "国产游戏"],
        "require_any": ["game", "gaming", "studio", "publisher", "launch", "revenue", "strategy", "license", "overseas", "游戏", "工作室", "发行", "收入", "战略", "版号", "出海"],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["game", "gaming", "studio", "publisher", "游戏", "工作室", "发行", "版号"],
    },
    "ai": {
        "include_any": ["artificial intelligence", "generative ai", "ai npc", "ai agent", "machine learning", "nvidia ace", "unity ai", "unreal ai", "roblox ai", "人工智能", "生成式 ai", "ai npc", "智能体"],
        "require_any": ["game", "gaming", "player", "studio", "developer", "npc", "animation", "art", "testing", "localization", "游戏", "玩家", "工作室", "开发", "美术", "测试", "本地化"],
        "exclude_any": LOW_VALUE_KEYWORDS + ["benchmark", "parameters", "model leaderboard", "模型排行榜", "参数规模"],
        "override_any": ["game development", "ai npc", "game testing", "game art", "游戏开发", "游戏美术", "游戏测试"],
    },
    "sports": {
        "include_any": ["nintendo", "playstation", "xbox", "valve", "steam", "epic games", "electronic arts", "take-two", "rockstar", "ubisoft", "activision", "blizzard", "riot games", "krafton", "nexon", "capcom", "sega", "square enix", "bandai namco", "supercell"],
        "require_any": ["game", "gaming", "studio", "publisher", "platform", "release", "revenue", "earnings", "strategy", "acquisition", "游戏", "工作室", "平台", "发行", "财报", "战略", "并购"],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["game", "gaming", "studio", "publisher", "platform", "游戏", "工作室", "平台"],
    },
    "retail": {
        "include_any": ["video game market", "mobile game", "pc game", "console game", "cloud gaming", "esports", "live streaming", "creator economy", "ugc", "subscription", "in-game", "game advertising", "mini game", "游戏市场", "手游", "主机游戏", "云游戏", "电竞", "游戏直播", "创作者经济", "小游戏"],
        "require_any": ["revenue", "users", "business", "market", "monetization", "platform", "distribution", "growth", "regulation", "收入", "用户", "商业", "市场", "变现", "平台", "发行", "增长", "监管"],
        "exclude_any": LOW_VALUE_KEYWORDS,
        "override_any": ["market report", "revenue", "creator economy", "monetization", "市场报告", "收入", "创作者经济", "商业化"],
    },
}
