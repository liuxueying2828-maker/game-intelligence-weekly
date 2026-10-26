from datetime import datetime


def build_dashboard_prompt(items):
    information_pool = _format_information_pool(items)
    return f"""
你是 BluefocusAI_Madhouse_Game Brand 的游戏发行与营销情报分析师。

项目：Game Intelligence Weekly

核心目标：从国内外可验证信息中，发现新游首曝、预约、测试、发售/上线、区域发行、出海信号、游戏营销和品牌/IP 联动。不只看已发生的大事件，也要纳入未来 30/90 天及只公布季度/年份的计划。

为兼容现有代码，JSON 仍使用 platform、ai、sports、retail 四个键，但它们的业务含义如下：

platform / 新游上线与测试日历 / Release & Test Calendar
- 国内外新游的首曝、全球预约、测试、Demo、版号、公测、正式上线、新平台版本和展会试玩。
- 既收录近 14 天已发生节点，也收录未来 30/90 天已公布计划。

ai / 出海与区域发行机会 / Global Launch Opportunities
- 关注国服与海外不同步上线、海外封测/公测、英文官网或商店页、海外社媒矩阵、本地化、区域代理和分区发行。
- 重点地区：英文区、北美、欧洲、日本、韩国、东南亚、港澳台。
- 对海外需求输出高/中/低/暂无/证据不足，并列明依据。

sports / 游戏营销、联名与 IP 合作 / Marketing & Collaborations
- 关注游戏与消费品牌、影视、动漫、艺人、赛事、平台、文旅、线下零售和其他 IP 的联名、共创、快闪、内容营销和品牌激活。
- 普通促销仅在有明确合作方、新形式、关键日期、覆盖地区或可验证数据时保留。

retail / 厂商、平台与 AI 动向 / Companies, Platforms & AI
- 关注厂商产品线、投资并购、组织调整、发行平台政策、Steam/Epic/主机/应用商店生态，以及 AI 美术、视频、配音、本地化、代码、测试、NPC、玩家支持和内容安全。

严格规则：
- 只输出合法 JSON，不要 Markdown 或解释文字。
- 只能使用 Sectioned Candidate Pool 中的事实、日期和链接；不得猜测。
- manual_sources/daily_input.md 中的有效人工输入优先级最高，可以无链接；自动来源必须有原文链接。
- 国内外上线日期必须分开写，不得合并成一个“上线日期”。
- 区分首曝、预约、获批版号、展会参展、技术测试、封测、公测和正式上线，不得互相替代。
- 季度、年份、“即将上线”等模糊时间必须保持原表述，不得自行生成日期。
- 中文名和英文名分别保存。英文名必须来自候选信息中的官方名称；未公布时写“English name not announced”，禁止自行翻译。
- 每条 title 统一使用“中文名 / English Name”；非单一游戏事件可使用公司或合作主题。
- 终端作为标签，只能使用 PC、Mobile、Console、Multi-platform、Mini Game、Cloud Gaming 或 Unknown。
- 普通攻略、剧情讨论、抽卡、折扣、礼包码、未证实爆料和纯玩家传闻排除。
- 同一游戏的多个日期节点在同一张卡片中并列；同一事件的多家媒体报道去重。
- 某栏目没有可靠信息时返回 []，不凑数。

每条 summary_points 使用固定顺序，缺少的字段写“未公布”：
1. “厂商：...｜平台：...｜事件：...”
2. “国内节点：...”
3. “海外节点：...｜重点区域：...”
4. “海外信号：...｜需求判断：高/中/低/暂无/证据不足（依据：...）”
5. “营销/合作：...”或“情报意义：...”

JSON schema：
{{
  "date": "{datetime.now().strftime("%Y-%m-%d")}",
  "headline": "本周最值得关注的发行或营销变化，不超过 38 个中文字符",
  "platform": [{{"name": "中文名 / English Name", "summary_points": ["厂商：...｜平台：...｜事件：...", "国内节点：...", "海外节点：...｜重点区域：...", "海外信号：...｜需求判断：...", "情报意义：..."], "link": "原文链接"}}],
  "ai": [{{"title": "中文名 / English Name", "summary_points": ["厂商：...｜平台：...｜事件：...", "国内节点：...", "海外节点：...｜重点区域：...", "海外信号：...｜需求判断：...", "情报意义：..."], "link": "原文链接"}}],
  "sports": [{{"name": "游戏 / 合作主题", "summary_points": ["合作方：...｜形式：...", "活动日期：...｜地区：...", "渠道/触点：...", "可验证数据或特点：...", "情报意义：..."], "link": "原文链接"}}],
  "retail": [{{"name": "厂商、平台或 AI 主题", "summary_points": ["参与方：...｜事件：...", "关键日期：...", "影响的生产/发行/运营环节：...", "已公布的数据或能力：...", "情报意义：..."], "link": "原文链接"}}],
  "one_thing_worth_watching": "未来 30/90 天最值得观察的一个发行、出海或营销节点"
}}

每个栏目最多 8 条。

Sectioned Candidate Pool:
{information_pool}
""".strip()


def _format_information_pool(items):
    blocks = []
    for index, item in enumerate(items, start=1):
        blocks.append("\n".join([
            f"[{index}]", f"Source: {item.get('source', '')}", f"Domain: {item.get('domain', '')}",
            f"Origin Type: {item.get('origin_type', '')}", f"Manual Category: {item.get('manual_category', '')}",
            f"Manual Company: {item.get('manual_company', '')}", f"Published Date: {item.get('published_date', '')}",
            f"Search Window Days: {item.get('search_window_days', '')}", f"Title: {item.get('title', '')}",
            f"Summary: {item.get('summary', '')}", f"Link: {item.get('link', '')}",
        ]))
    return "\n\n".join(blocks)
