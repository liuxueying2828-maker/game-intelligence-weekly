# Game Intelligence Weekly

An automated release, globalization, and marketing intelligence radar for BluefocusAI_Madhouse_Game Brand.

GitHub Actions → Bilingual Keyword Library → Gemini Google Search + optional Gemini Deep Research + RSS + Google News + Manual Inputs → Gemini Analysis → HTML Dashboard → GitHub Pages and Email

The discovery layer runs separate Chinese and English Gemini Google Search tasks. An optional Deep Research mode adds two longer-running Chinese/English research agents. Direct RSS feeds and separate Chinese/English Google News editions remain supplementary sources. Search vocabulary, priority companies, tracked games, trade events, and source families are maintained in `data/keyword_library.json`.

## Intelligence Scope

The dashboard is a rolling six-month China-game overseas opportunity radar. Purely overseas titles and general global-industry news are excluded. Confirmed future milestones remain visible until they happen, even when the original announcement is older than the current week. It contains four sections:

1. **国内游戏产品动态 / China Game Pipeline**
   - Chinese-developed titles at reveal, license, reservation, testing, launch, or domestic release stages.
2. **海外发行确定节点 / Confirmed Overseas Launches**
   - Confirmed overseas registration, tests, launch windows, dates, and region-by-region releases.
3. **海外发行前置信号 / Early Overseas Signals**
   - English sites, overseas stores/social accounts, localization hiring, publishing partners, ratings, trademarks, and overseas exhibitions.
4. **海外营销与广告机会 / Overseas Marketing Opportunities**
   - Overseas user acquisition, launch campaigns, creators, communities, media buying, brand/IP collaborations, and regional growth opportunities.

Platforms are tags rather than top-level sections: `PC`, `Mobile`, `Console`, `Multi-platform`, `Mini Game`, `Cloud Gaming`, and `Unknown`.

## Editorial Rules

- Every item is identified as `[游戏厂商-游戏中文名-English Name]`.
- Missing identities are shown explicitly as `未找到厂商`, `未找到中文名`, or `English name not found`; English names are never invented or translated.
- China and overseas milestones must be recorded separately.
- First reveal, license approval, exhibition appearance, test, open beta, and official launch are different event types.
- A quarter, year, or approximate window must remain approximate; the system must not invent a precise date.
- Search expands from recent updates to announcements published in the last 180 days and tracks relevant events in the coming 180 days.
- Curated pipeline records remain visible as `持续关注`; new dates, regions, or status changes are marked `本周新增/更新`.
- Overseas opportunity is classified as High, Medium, Low, No current signal, or Insufficient evidence, with the supporting evidence shown.
- Verified manual inputs in `manual_sources/daily_input.md` take priority over automatic sources.

See [`manual_sources/examples.md`](manual_sources/examples.md) for the editorial input format.

## Project Structure

```text
.
├── main.py
├── config.py
├── requirements.txt
├── .github/workflows/daily.yml
├── sources/
├── intelligence/
│   ├── prompt.py
│   └── gemini_intelligence.py
├── manual_sources/
│   ├── daily_input.md
│   └── examples.md
├── data/
│   ├── keyword_library.json
│   └── game_catalog.json
└── output/
    ├── preview/
    ├── archive/
    ├── data/
    ├── email.py
    └── html.py
```

## GitHub Secrets

- `GEMINI_API_KEY`
- `EMAIL_TO`
- `EMAIL_API_KEY`
- `EMAIL_FROM` (optional; use a verified sender when available)

Real keys must only be stored as GitHub Secrets or in a local ignored `.env` file. Never commit them.

## Maintaining Coverage

- Maintain bilingual event terms (`OB`, first reveal, tests, launches, major updates, collaborations), priority companies, tracked games, event names, and source families in `data/keyword_library.json`.
- `sources/keyword_library.py` converts that library into four Chinese/English search tasks; `sources/gemini_research.py` runs Google Search Grounding and, when enabled, separate Chinese/English Deep Research tasks.
- RSS and Google News queries in `config.py` are supplementary coverage and fallback inputs, not the only information pool.
- Maintain official Chinese/English names and known regional milestones in `data/game_catalog.json`.
- Add verified one-off intelligence to `manual_sources/daily_input.md`.
- Each workflow run prints Gemini search and candidate diagnostics by source, section, and search language before final analysis.

## Running the Workflow

The `Game Intelligence Weekly` GitHub Actions workflow supports:

- `preview`: collect news, generate a draft, email it, commit `output/preview`, and deploy Pages.
- `publish`: promote a reviewed report to the official archive and deploy Pages.
- `deploy_only`: deploy the current checked-in preview without calling Gemini or sending email.

The workflow has a second `research_mode` input:

- `google_search`: four regular Chinese/English Google Search tasks. This is the recommended default for weekly runs.
- `google_search_and_deep_research`: adds one Chinese and one English Deep Research task. These run in parallel but can take several minutes and incur materially higher API cost.

Preview URL:

```text
https://liuxueying2828-maker.github.io/game-intelligence-weekly/preview/index.html
```

GitHub Pages must use `Settings → Pages → Source → GitHub Actions`.

## Local Run

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-gemini-api-key"
export GEMINI_MODEL="gemini-2.5-flash"
export GEMINI_SEARCH_MODEL="gemini-3.8-flash"
export ENABLE_GEMINI_DEEP_RESEARCH="false"
export EMAIL_TO="xueying.liu@bluefocus.cn"
export EMAIL_API_KEY="your-email-api-key"
export EMAIL_FROM="Game Intelligence Weekly <your-verified-sender@example.com>"
export REPORT_MODE="preview"
python main.py
```
