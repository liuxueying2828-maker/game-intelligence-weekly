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
    html = build_dashboard_html(data, archive_href=archive_href)
    html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def build_dashboard_html(data, archive_href="./archive/"):
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
      --bg: #f7f8fb;
      --card: #ffffff;
      --ink: #172033;
      --muted: #687386;
      --line: #e6e9ef;
      --soft-line: #f0f2f6;
      --blue: #2357d9;
      --blue-soft: #edf3ff;
      --green: #078365;
      --green-soft: #eaf8f2;
      --orange: #b25a00;
      --orange-soft: #fff3e6;
      --violet: #6f52d4;
      --violet-soft: #f2effc;
      --dark: #111827;
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
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 44px 0 44px;
    }}

    .topbar {{
      display: flex;
      justify-content: space-between;
      gap: 24px;
      align-items: flex-start;
      margin-bottom: 28px;
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
      font-size: clamp(30px, 4.4vw, 48px);
      line-height: 1;
      letter-spacing: 0;
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
      border-radius: 8px;
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
      margin-top: 22px;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 22px;
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
      border-radius: 999px;
      padding: 6px 11px;
      font-size: 12px;
      font-weight: 760;
      white-space: nowrap;
    }}

    .blue {{ color: var(--blue); background: var(--blue-soft); }}
    .violet {{ color: var(--violet); background: var(--violet-soft); }}
    .green {{ color: var(--green); background: var(--green-soft); }}
    .orange {{ color: var(--orange); background: var(--orange-soft); }}

    .cards {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      align-items: start;
    }}

    .card {{
      display: flex;
      flex-direction: column;
      gap: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      background: #fff;
      min-height: 0;
    }}

    .card-title {{
      margin: 0;
      font-size: 20px;
      line-height: 1.25;
      letter-spacing: 0;
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
      border-radius: 999px;
      padding: 6px 10px;
      background: #f3f5f8;
      color: #344054;
      font-size: 13px;
      font-weight: 720;
    }}

    .read-button {{
      margin-top: auto;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: fit-content;
      min-height: 38px;
      padding: 8px 13px;
      border-radius: 8px;
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
      border-radius: 8px;
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
      background: var(--green-soft);
      color: var(--green);
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
        width: min(100% - 24px, 1120px);
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

    {_render_sections(data)}

    {_render_warning(data)}
  </main>
  {_render_confirmation_script()}
</body>
</html>
"""


def _render_sections(data):
    opportunity_cards = _collect_opportunity_cards(data)
    pending_cards = safe_cards(data.get("pending_confirmation", []))
    return "\n".join([
        _render_opportunity_section(opportunity_cards),
        _render_pending_section(pending_cards),
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


def _render_opportunity_section(cards):
    rendered_cards = "\n".join(_render_card(card, section_key) for card, section_key in cards)
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


def _render_pending_section(cards):
    rendered_cards = "\n".join(_render_card(card, "pending_confirmation", pending=True) for card in cards)
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


def _render_card(card, section_key, pending=False):
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

    return f"""
    <article class="card" data-source-id="{safe_escape(link, quote=True)}" data-review-card="{'true' if pending else 'false'}">
      <span class="confirmation-status">已人工确认</span>
      <h3 class="card-title">{safe_escape(_card_title(card, section_key))}</h3>
      <div class="field">
        <div class="field-label">摘要要点</div>
        {_render_summary_points(card, section_key)}
      </div>
      <div class="card-actions">
        {read_button}
        {confirmation_button}
      </div>
    </article>
    """


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


def _render_summary_points(card, section_key):
    points = _summary_points(card, section_key)
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
