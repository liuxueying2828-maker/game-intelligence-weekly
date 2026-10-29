from datetime import datetime
from html import escape

from utils.date_utils import report_date_parts


_DIRECT_TO_CONSUMER_ABBR = "D" + "TC"
_DECA_DIRECT_PHRASE = "对" + "迪卡侬而言"


TEXT_REPLACEMENTS = (
    (_DECA_DIRECT_PHRASE + "，", "给迪卡侬的启示是，"),
    (_DECA_DIRECT_PHRASE, "给迪卡侬的启示"),
    (_DIRECT_TO_CONSUMER_ABBR + " Opportunity", "业务启示"),
    (_DIRECT_TO_CONSUMER_ABBR + " opportunity", "业务启示"),
    (_DIRECT_TO_CONSUMER_ABBR + "机会", "业务启示"),
    (_DIRECT_TO_CONSUMER_ABBR + " 策略", "数字商业能力"),
    (_DIRECT_TO_CONSUMER_ABBR + "策略", "数字商业能力"),
    (_DIRECT_TO_CONSUMER_ABBR, "数字商业"),
)


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return ", ".join(part for part in (safe_text(item) for item in value) if part)
    if isinstance(value, dict):
        return ", ".join(
            f"{safe_text(key)}: {safe_text(item)}"
            for key, item in value.items()
            if safe_text(key) or safe_text(item)
        )
    return str(value)


def sanitize_text(text):
    for old, new in TEXT_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def safe_escape(value, quote=True):
    return escape(safe_text(value), quote=quote)


def safe_cards(value):
    return value if isinstance(value, list) else []


OPPORTUNITY_SECTION_ORDER = (
    "ai_technology",
    "retail_innovation",
    "sports_outdoor",
    "platform_intelligence",
)


def render_dashboard(data, output_path, archive_href="./archive/"):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    review_mode = "preview" in output_path.parts
    html = build_dashboard_html(data, archive_href=archive_href, review_mode=review_mode)
    html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def build_dashboard_html(data, archive_href="./archive/", review_mode=True):
    date = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    date_parts = report_date_parts(date)
    report_date_label = f"{date_parts['iso_week']} · {date_parts['formatted_date']}"

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Weekly Industry Intelligence</title>
  <style>
    :root {{
      --bg: #f7f7f8;
      --card: #ffffff;
      --ink: #111111;
      --muted: #656565;
      --line: #d9d9dc;
      --soft-line: #ececef;
      --blue: #002fa7;
      --blue-soft: #eef2ff;
      --dark: #111111;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
      line-height: 1.5;
    }}

    .page {{
      width: min(1180px, calc(100% - 40px));
      margin: 0 auto;
      padding: 44px 0 44px;
    }}

    .topbar {{
      display: flex;
      justify-content: space-between;
      gap: 24px;
      align-items: flex-start;
      margin-bottom: 22px;
      padding-bottom: 22px;
      border-bottom: 1px solid var(--ink);
    }}

    .eyebrow {{
      margin: 0 0 8px;
      color: var(--blue);
      font-size: 13px;
      font-weight: 750;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(31px, 4.2vw, 52px);
      line-height: .96;
      letter-spacing: -.045em;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 0 0 auto;
      padding-top: 2px;
    }}

    .date {{
      color: var(--muted);
      font-size: 15px;
    }}

    .archive-link {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 36px;
      padding: 7px 12px;
      border: 1px solid var(--line);
      border-radius: 0;
      background: var(--card);
      color: var(--ink);
      text-decoration: none;
      font-size: 14px;
      font-weight: 760;
      white-space: nowrap;
    }}

    .archive-link:hover {{
      border-color: #c8ced8;
    }}

    .section {{
      margin-top: 18px;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 0;
      padding: 26px;
    }}

    .section-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--soft-line);
      margin-bottom: 18px;
    }}

    h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: 0;
    }}

    .subtitle {{
      margin-top: 2px;
      color: var(--muted);
      font-size: 14px;
      font-weight: 650;
    }}

    .section-badge {{
      border-radius: 0;
      padding: 6px 11px;
      font-size: 12px;
      font-weight: 760;
      white-space: nowrap;
    }}

    .blue, .violet, .green, .orange {{ color: var(--blue); background: var(--blue-soft); }}

    .cards {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
      align-items: start;
    }}

    .card {{
      display: flex;
      flex-direction: column;
      gap: 0;
      border: 1px solid var(--line);
      border-radius: 0;
      padding: 0;
      background: #fff;
      min-height: 0;
    }}

    .card-title {{
      margin: 0;
      font-size: clamp(20px, 2.2vw, 27px);
      line-height: 1.18;
      letter-spacing: -.025em;
    }}

    .field {{
      padding-top: 12px;
      border-top: 1px solid var(--soft-line);
    }}

    .field-label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 780;
      letter-spacing: .04em;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}

    .field p {{
      margin: 0;
      font-size: 15.5px;
      line-height: 1.62;
    }}

    .summary-list {{
      margin: 0;
      padding-left: 1.15em;
      font-size: 15.5px;
      line-height: 1.72;
    }}

    .summary-list li {{
      margin: 0 0 8px;
    }}

    .summary-list li:last-child {{
      margin-bottom: 0;
    }}

    .trend {{
      display: inline-flex;
      width: fit-content;
      border-radius: 0;
      padding: 6px 10px;
      background: #f3f5f8;
      color: #344054;
      font-size: 13px;
      font-weight: 720;
    }}

    .stage-chip {{
      display: inline-flex;
      width: fit-content;
      border-radius: 0;
      padding: 6px 10px;
      font-size: 12px;
      font-weight: 780;
      border: 1px solid var(--blue);
      background: #fff;
      color: var(--blue);
    }}
    .stage-chip[class*="stage-"] {{ color: var(--blue); background: #fff; }}

    .mode-note {{ margin: -12px 0 18px; color: var(--muted); font-size: 14px; }}

    .brief-lead {{
      display: grid;
      grid-template-columns: 140px 1fr;
      gap: 28px;
      padding: 20px 0 28px;
      border-bottom: 1px solid var(--line);
      margin-bottom: 20px;
    }}
    .brief-label {{ color: var(--blue); font-size: 12px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
    .brief-copy {{ margin: 0; max-width: 820px; font-size: clamp(20px, 2.5vw, 30px); line-height: 1.28; letter-spacing: -.025em; }}

    .card-head {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 20px; padding: 22px 24px 18px; }}
    .card-kicker {{ display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }}
    .evidence-label {{ color: var(--muted); font-size: 12px; font-weight: 720; }}
    .stage-rail {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }}
    .stage-step {{ position: relative; padding: 10px 8px; color: #969696; font-size: 11px; text-align: center; border-right: 1px solid var(--soft-line); }}
    .stage-step:last-child {{ border-right: 0; }}
    .stage-step.is-current {{ color: #fff; background: var(--blue); font-weight: 780; }}
    .facts {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-bottom: 1px solid var(--line); }}
    .fact {{ min-height: 86px; padding: 16px 18px; border-right: 1px solid var(--soft-line); }}
    .fact:last-child {{ border-right: 0; }}
    .fact-label {{ margin-bottom: 7px; color: var(--muted); font-size: 11px; font-weight: 780; letter-spacing: .06em; text-transform: uppercase; }}
    .fact-value {{ margin: 0; font-size: 15px; line-height: 1.42; }}
    .opportunity {{ display: grid; grid-template-columns: 140px 1fr; gap: 20px; padding: 17px 20px; background: var(--blue-soft); color: var(--ink); }}
    .opportunity strong {{ color: var(--blue); font-size: 12px; letter-spacing: .04em; }}
    .opportunity p {{ margin: 0; font-size: 15px; line-height: 1.5; }}
    .review-details {{ border-top: 1px solid var(--line); }}
    .review-details summary {{ padding: 13px 20px; color: var(--blue); font-size: 13px; font-weight: 760; cursor: pointer; list-style-position: inside; }}
    .review-details .details-body {{ padding: 0 20px 18px; }}

    .read-button {{
      margin-top: auto;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: fit-content;
      min-height: 38px;
      padding: 8px 13px;
      border-radius: 0;
      background: var(--dark);
      color: #fff;
      text-decoration: none;
      font-size: 14px;
      font-weight: 760;
    }}

    .card-actions {{
      margin-top: auto;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
    }}

    .card-actions .read-button {{
      margin-top: 0;
    }}

    .confirm-button {{
      min-height: 38px;
      padding: 8px 13px;
      border: 1px solid var(--blue);
      border-radius: 0;
      background: var(--blue);
      color: #fff;
      font: inherit;
      font-size: 14px;
      font-weight: 760;
      cursor: pointer;
    }}

    .confirm-button:disabled {{
      border-color: var(--line);
      background: #eef1f5;
      color: #8792a2;
      cursor: not-allowed;
    }}

    .undo-button {{
      border-color: var(--line);
      background: #fff;
      color: var(--muted);
    }}

    .confirmation-status {{
      display: none;
      width: fit-content;
      padding: 5px 9px;
      border-radius: 999px;
      background: var(--blue-soft);
      color: var(--blue);
      font-size: 12px;
      font-weight: 760;
    }}

    .card.is-confirmed .confirmation-status {{
      display: inline-flex;
    }}

    .workflow-note {{
      margin: 0 0 16px;
      color: var(--muted);
      font-size: 14px;
    }}

    .read-button.disabled {{
      background: #eef1f5;
      color: #8792a2;
      pointer-events: none;
    }}

    .empty {{
      color: var(--muted);
      border: 1px dashed var(--line);
      border-radius: 8px;
      padding: 18px;
      background: #fbfcfe;
    }}

    .warning {{
      margin-top: 14px;
      color: #8a5a00;
      background: #fff7e6;
      border: 1px solid #ffe1a6;
      border-radius: 8px;
      padding: 12px 14px;
      font-size: 13px;
    }}

    @media (max-width: 760px) {{
      .page {{
        width: min(100% - 24px, 1180px);
        padding-top: 28px;
      }}

      .topbar {{
        display: block;
        margin-bottom: 20px;
      }}

      .header-actions {{
        margin-top: 14px;
        justify-content: space-between;
      }}

      .section {{
        padding: 18px;
      }}

      .section-head {{
        display: block;
      }}

      .section-badge {{
        display: inline-flex;
        margin-top: 10px;
      }}

      .cards {{
        grid-template-columns: 1fr;
      }}

      .brief-lead, .opportunity {{ grid-template-columns: 1fr; gap: 8px; }}
      .card-head {{ grid-template-columns: 1fr; }}
      .facts {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .fact:nth-child(2) {{ border-right: 0; }}
      .fact:nth-child(-n+2) {{ border-bottom: 1px solid var(--soft-line); }}
      .stage-step {{ font-size: 9px; padding-inline: 3px; }}

      .card {{
        min-height: auto;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="topbar">
      <div>
        <p class="eyebrow">Game Intelligence Weekly</p>
        <h1>AI Game Industry Intelligence</h1>
      </div>
      <div class="header-actions">
        <div class="date">{safe_escape(report_date_label)}</div>
        <a class="archive-link" href="{safe_escape(archive_href, quote=True)}">历史周报</a>
      </div>
    </section>

    <div class="brief-lead">
      <div class="brief-label">本期判断</div>
      <p class="brief-copy">{safe_escape(data.get('headline') or data.get('one_thing_worth_watching') or '本期游戏出海机会已更新')}</p>
    </div>
    <p class="mode-note">{safe_escape('审核版：先看节点与市场机会，展开后核验来源' if review_mode else '团队分享版：只保留关键发行与营销信息')}</p>
    {_render_sections(data, review_mode=review_mode)}

    {_render_warning(data)}
  </main>
  {_render_confirmation_script() if review_mode else ''}
</body>
</html>
"""


def _render_sections(data, review_mode=True):
    opportunity_cards = _collect_opportunity_cards(data)
    pending_cards = safe_cards(data.get("pending_confirmation", []))
    return "\n".join([
        _render_opportunity_section(opportunity_cards, review_mode=review_mode),
        _render_pending_section(pending_cards, review_mode=review_mode) if review_mode else "",
    ])


def _collect_opportunity_cards(data):
    cards = []
    seen_titles = set()
    for section_key in OPPORTUNITY_SECTION_ORDER:
        for card in safe_cards(data.get(section_key, [])):
            title = safe_text(_card_title(card, section_key)).strip().lower()
            if title in seen_titles:
                continue
            seen_titles.add(title)
            cards.append((card, section_key))
    return cards


def _render_opportunity_section(cards, review_mode=True):
    rendered_cards = "\n".join(_render_card(card, section_key, review_mode=review_mode) for card, section_key in cards)
    if not rendered_cards:
        rendered_cards = '<div class="empty" data-empty-state>本期尚未抓取到有原文链接的游戏出海机会。</div>'

    return f"""
    <section class="section">
      <div class="section-head">
        <div>
          <h2>游戏出海机会</h2>
          <div class="subtitle">China Game Overseas Opportunities</div>
        </div>
        <span class="section-badge blue" id="opportunity-count">{len(cards)} 条</span>
      </div>
      <div class="cards" id="opportunity-list">
        {rendered_cards}
      </div>
    </section>
    """


def _render_pending_section(cards, review_mode=True):
    rendered_cards = "\n".join(_render_card(card, "pending_confirmation", pending=True, review_mode=review_mode) for card in cards)
    if not rendered_cards:
        rendered_cards = '<div class="empty" data-empty-state>当前没有待人工确认的情报。</div>'

    return f"""
    <section class="section">
      <div class="section-head">
        <div>
          <h2>待人工确认</h2>
          <div class="subtitle">Needs Human Review</div>
        </div>
        <span class="section-badge orange" id="pending-count">{len(cards)} 条</span>
      </div>
      <p class="workflow-note">请先打开原文核对事件、日期和游戏名称，返回本页后再点击确认。</p>
      <div class="cards" id="pending-list">
        {rendered_cards}
      </div>
    </section>
    """


def _render_card(card, section_key, pending=False, review_mode=True):
    if isinstance(card, str):
        card = {"name": "Signal", "news": card, "summary_points": [card], "link": ""}

    link = safe_text(card.get("link", ""))
    read_button = (
        f'<a class="read-button" data-read-source href="{safe_escape(link, quote=True)}" target="_blank" rel="noopener noreferrer">查看原文</a>'
        if link
        else '<span class="read-button disabled">暂无原文链接</span>'
    )
    confirmation_button = (
        '<button class="confirm-button" data-confirm-source type="button" disabled>确认这条情报</button>'
        if pending and link else ""
    )
    stage = _canonical_stage(card.get("normalized_stage"), card.get("official_event_name"))
    stage_label = _display_stage_label(card, stage)
    stage_chip = f'<span class="stage-chip stage-{safe_escape(stage, quote=True)}">{safe_escape(stage_label)}</span>' if stage_label else ""
    points = _summary_points(card, section_key)
    date_value = safe_text(card.get("event_date") or _point_value(points, "时间：") or "未公布")
    region_value = safe_text(_field_from_points(points, "地区：", "｜") or card.get("regions") or "未公布")
    platform_value = safe_text(_field_from_points(points, "平台：", "｜") or card.get("platforms") or "未公布")
    evidence_value = safe_text(_point_value(points, "证据：") or card.get("verification_status") or "待核验")
    opportunity_value = safe_text(card.get("marketing_opportunity") or _opportunity_from_points(points) or "暂无明确海外营销窗口")
    readiness_value = safe_text(card.get("marketing_readiness") or _field_from_points(points, "营销成熟度：", "｜") or "未判断")
    detail_block = _render_review_details(card, section_key, read_button, confirmation_button) if review_mode else _render_compact_actions(read_button)

    return f"""
    <article class="card" data-source-id="{safe_escape(link, quote=True)}" data-review-card="{'true' if pending else 'false'}">
      <div class="card-head">
        <div>
          <div class="card-kicker">{stage_chip}<span class="evidence-label">{safe_escape(evidence_value)}</span><span class="confirmation-status">已人工确认</span></div>
          <h3 class="card-title">{safe_escape(_card_title(card, section_key))}</h3>
        </div>
        <div class="date">{safe_escape(date_value)}</div>
      </div>
      {_render_stage_rail(stage)}
      <div class="facts">
        {_render_fact("节点", stage_label or "未分类")}
        {_render_fact("地区", region_value)}
        {_render_fact("平台", platform_value)}
        {_render_fact("营销成熟度", readiness_value)}
      </div>
      <div class="opportunity"><strong>海外营销机会</strong><p>{safe_escape(opportunity_value)}</p></div>
      {detail_block}
    </article>
    """


def _display_stage_label(card, stage):
    if stage == "cbt":
        return safe_text(card.get("sequence_label") or "测试轮次未确认")
    return safe_text(_stage_label(stage) or card.get("official_event_name") or "")


def _render_stage_rail(stage):
    steps = [
        ("first_reveal", "首曝"), ("technical_test", "技术测试"), ("cbt", "封闭测试"),
        ("preregistration", "预约"), ("open_beta_or_launch", "公测/上线"), ("live_ops", "长线运营"),
    ]
    current = stage if stage in {item[0] for item in steps} else "live_ops" if stage in {"major_update", "anniversary", "collaboration", "regional_expansion", "platform_expansion"} else ""
    rendered = "".join(
        f'<div class="stage-step{" is-current" if step_id == current else ""}">{safe_escape(label)}</div>'
        for step_id, label in steps
    )
    return f'<div class="stage-rail" aria-label="游戏发行阶段">{rendered}</div>'


def _render_fact(label, value):
    return f'<div class="fact"><div class="fact-label">{safe_escape(label)}</div><p class="fact-value">{safe_escape(value)}</p></div>'


def _render_review_details(card, section_key, read_button, confirmation_button):
    return f"""
      <details class="review-details">
        <summary>查看核验详情与来源</summary>
        <div class="details-body">
          {_render_summary_points(card, section_key)}
          <div class="card-actions">{read_button}{confirmation_button}</div>
        </div>
      </details>
    """


def _render_compact_actions(read_button):
    return f'<div class="card-actions" style="padding:16px 20px">{read_button}</div>'


def _point_value(points, prefix):
    for point in points:
        text = safe_text(point)
        if prefix in text:
            return text.split(prefix, 1)[1].strip()
    return ""


def _field_from_points(points, prefix, delimiter):
    value = _point_value(points, prefix)
    return value.split(delimiter, 1)[0].strip() if value else ""


def _opportunity_from_points(points):
    for point in points:
        text = safe_text(point)
        if "｜机会：" in text:
            return text.split("｜机会：", 1)[1].strip()
        if text.startswith("机会："):
            return text.split("机会：", 1)[1].strip()
    return ""


def _render_confirmation_script():
    return """
  <script>
    (() => {
      const storageKey = "game-intelligence-confirmed-sources-v1";
      const viewedKey = "game-intelligence-viewed-sources-v1";
      const readSet = (key) => {
        try { return new Set(JSON.parse(localStorage.getItem(key) || "[]")); }
        catch (_) { return new Set(); }
      };
      const writeSet = (key, values) => localStorage.setItem(key, JSON.stringify([...values]));
      const confirmed = readSet(storageKey);
      const viewed = readSet(viewedKey);
      const opportunityList = document.getElementById("opportunity-list");
      const pendingList = document.getElementById("pending-list");

      function updateCounts() {
        const opportunities = opportunityList.querySelectorAll(".card").length;
        const pending = pendingList.querySelectorAll(".card").length;
        document.getElementById("opportunity-count").textContent = `${opportunities} 条`;
        document.getElementById("pending-count").textContent = `${pending} 条`;
        pendingList.querySelector("[data-empty-state]")?.remove();
        if (!pending) {
          pendingList.insertAdjacentHTML("beforeend", '<div class="empty" data-empty-state>当前没有待人工确认的情报。</div>');
        }
      }

      function setConfirmed(card, isConfirmed) {
        const sourceId = card.dataset.sourceId;
        const button = card.querySelector("[data-confirm-source]");
        card.classList.toggle("is-confirmed", isConfirmed);
        if (isConfirmed) {
          confirmed.add(sourceId);
          opportunityList.appendChild(card);
          if (button) {
            button.disabled = false;
            button.textContent = "取消确认";
            button.classList.add("undo-button");
          }
        } else {
          confirmed.delete(sourceId);
          pendingList.appendChild(card);
          if (button) {
            button.textContent = "确认这条情报";
            button.classList.remove("undo-button");
            button.disabled = !viewed.has(sourceId);
          }
        }
        writeSet(storageKey, confirmed);
        updateCounts();
      }

      document.querySelectorAll("[data-review-card='true']").forEach((card) => {
        const sourceId = card.dataset.sourceId;
        const readLink = card.querySelector("[data-read-source]");
        const confirmButton = card.querySelector("[data-confirm-source]");
        if (viewed.has(sourceId) && confirmButton) confirmButton.disabled = false;
        readLink?.addEventListener("click", () => {
          viewed.add(sourceId);
          writeSet(viewedKey, viewed);
          if (confirmButton) confirmButton.disabled = false;
        });
        confirmButton?.addEventListener("click", () => {
          setConfirmed(card, !card.classList.contains("is-confirmed"));
        });
        if (confirmed.has(sourceId)) setConfirmed(card, true);
      });
      updateCounts();
    })();
  </script>
    """


def _card_title(card, section_key):
    if not isinstance(card, dict):
        return card or "Signal"
    if section_key == "ai_technology":
        return card.get("title") or card.get("name") or "AI 能力变化"
    return card.get("name") or card.get("title") or "Signal"


def _render_summary_points(card, section_key, compact=False):
    points = _summary_points(card, section_key)
    if compact:
        preferred = [point for point in points if any(prefix in point for prefix in ("节点：", "地区：", "海外节点：", "营销成熟度：", "机会："))]
        points = (preferred or points)[:4]
    if not points:
        return "<p></p>"
    if len(points) == 1:
        return f"<p>{safe_escape(points[0])}</p>"
    rendered = "\n".join(f"<li>{safe_escape(point)}</li>" for point in points)
    return f'<ul class="summary-list">{rendered}</ul>'


def _summary_points(card, section_key):
    if not isinstance(card, dict):
        return [safe_text(card)]

    raw_points = card.get("summary_points")
    if isinstance(raw_points, list):
        return [
            safe_text(point).strip()
            for point in raw_points
            if safe_text(point).strip() and not _is_unsupported_status_line(safe_text(point))
        ]
    if raw_points:
        return _split_points(raw_points)

    if section_key == "ai_technology":
        values = [
            card.get("capability") or card.get("news") or "",
            card.get("industry_impact") or card.get("why_this_matters") or "",
        ]
    else:
        values = [
            card.get("news") or "",
            card.get("why_this_matters") or "",
        ]
    return [safe_text(value).strip() for value in values if safe_text(value).strip()]


def _is_unsupported_status_line(value):
    text = safe_text(value).strip()
    return text.startswith("状态：") or any(
        phrase in text
        for phrase in ("本周新增", "本周更新", "持续关注", "新增/更新或持续关注")
    )


def _stage_label(stage):
    return {
        "first_reveal": "首曝", "technical_test": "技术测试", "cbt": "封闭测试",
        "preregistration": "预约", "open_beta_or_launch": "公测/上线", "soft_launch": "区域试发行",
        "major_update": "大版本更新", "anniversary": "周年", "collaboration": "联名/联动",
        "regional_expansion": "新地区发行", "platform_expansion": "新平台上线",
    }.get(stage, "")


def _canonical_stage(value, official_name=""):
    text = f"{safe_text(value)} {safe_text(official_name)}".lower()
    canonical = {
        "first_reveal", "technical_test", "cbt", "preregistration", "open_beta_or_launch",
        "soft_launch", "major_update", "anniversary", "collaboration", "regional_expansion",
        "platform_expansion",
    }
    if safe_text(value) in canonical:
        return safe_text(value)
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


def _split_points(value):
    text = safe_text(value).strip()
    if not text:
        return []
    if isinstance(value, str):
        parts = [part.strip(" -•\t") for part in text.splitlines() if part.strip(" -•\t")]
        if len(parts) > 1:
            return parts
    return [text]


def _render_warning(data):
    warning = data.get("parse_warning")
    if not warning:
        return ""
    return f'<div class="warning">{safe_escape(warning)}</div>'
