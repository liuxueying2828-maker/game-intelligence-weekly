# Game Intelligence Weekly

An automated release, globalization, and marketing intelligence radar for BluefocusAI_Madhouse_Game Brand.

GitHub Actions → Industry Knowledge Base → BlueAI Web Search → Independent Verification → Event History → Editorial Preview → Compact Team Edition

The discovery layer runs a bilingual query matrix through the company BlueAI Relay and the Responses API `web_search` tool. It combines broad industry searches with batched priority-company searches, tracked-game searches, and dedicated public-social searches. A second web-search pass verifies direct sources, dates, numbers, title matching, regions, and later corrections before the report is written. Search vocabulary, priority companies, tracked games, trade events, and source families are maintained in `data/keyword_library.json`.

## Intelligence Scope

The dashboard is a rolling six-month China-game overseas opportunity radar. Purely overseas titles and general global-industry news are excluded. Confirmed future milestones remain visible until they happen, even when the original announcement is older than the current week. The preview is a detailed editorial review surface; the published page is a compact team-sharing edition.

1. **国内游戏产品动态 / China Game Pipeline**
   - Chinese-developed titles at reveal, license, reservation, testing, launch, or domestic release stages.
2. **海外发行确定节点 / Confirmed Overseas Launches**
   - Confirmed overseas registration, tests, launch windows, dates, and region-by-region releases.
3. **海外发行前置信号 / Early Overseas Signals**
   - English sites, overseas stores/social accounts, localization hiring, publishing partners, ratings, trademarks, and overseas exhibitions.
4. **海外营销与广告机会 / Overseas Marketing Opportunities**
   - Overseas user acquisition, launch campaigns, creators, communities, media buying, brand/IP collaborations, and regional growth opportunities.
5. **待确认情报 / Needs Confirmation**
   - Conflicting, leaked, or insufficiently supported candidates kept outside the four main report sections.

Platforms are tags rather than top-level sections: `PC`, `Mobile`, `Console`, `Multi-platform`, `Mini Game`, `Cloud Gaming`, and `Unknown`.

## Editorial Rules

- Every item is identified as `[游戏厂商-游戏中文名-English Name]`.
- Missing identities are shown explicitly as `未找到厂商`, `未找到中文名`, or `English name not found`; English names are never invented or translated.
- China and overseas milestones must be recorded separately.
- First reveal, license approval, exhibition appearance, test, open beta, and official launch are different event types.
- Branded test names are preserved, but tests are normalized to technical test / CBT / open beta / launch. A numbered test is emitted only when same-region player-facing history supports it; otherwise it is labeled `测试轮次未确认`.
- Domestic and overseas test sequences are counted separately. SteamDB is secondary discovery evidence and cannot independently verify an event.
- A quarter, year, or approximate window must remain approximate; the system must not invent a precise date.
- Search expands from recent updates to announcements published in the last 180 days and tracks relevant events in the coming 180 days.
- Only candidates actually found by BlueAI Web Search may appear as news; every published card must include a source URL.
- Overseas opportunity is classified as High, Medium, Low, No current signal, or Insufficient evidence, with the supporting evidence shown.
- Manual reference text and catalog tracking notes are excluded from the news candidate pool.
- `已验证` requires two genuinely independent sources; an official announcement plus an independent reliable report qualifies.
- A credible single non-official source is labeled `据报道/尚未获官方确认`; conflicting or weak evidence goes to `待确认情报`.

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
│   └── blueai_intelligence.py
├── manual_sources/
│   ├── daily_input.md
│   └── examples.md
├── data/
│   ├── keyword_library.json
│   ├── game_catalog.json
│   ├── event_taxonomy.json
│   ├── source_registry.json
│   ├── marketing_rules.json
│   ├── event_history.json
│   └── review_state.json
└── output/
    ├── preview/
    ├── archive/
    ├── data/
    ├── email.py
    └── html.py
```

## GitHub Secrets

- `BLUEAI_API_KEY`
- `EMAIL_TO`
- `EMAIL_API_KEY`
- `EMAIL_FROM` (optional; use a verified sender when available)

Real keys must only be stored as GitHub Secrets or in a local ignored `.env` file. Never commit them.

## Maintaining Coverage

- Maintain bilingual event terms (`OB`, first reveal, tests, launches, major updates, collaborations), priority companies, tracked games, event names, and source families in `data/keyword_library.json`.
- `data/event_taxonomy.json` defines normalized marketing nodes and sequence policy. `event_history.json` contains externally sourced event history; catalog notes and user examples never enter it as evidence.
- `source_registry.json` records access and evidence rules for official sites, social pages, Bilibili, TapTap, stores, Steam, and SteamDB.
- `sources/keyword_library.py` converts that library into four Chinese/English search tasks; `sources/blueai_research.py` runs candidate discovery and independent verification through the Relay.
- Official sites, stores, social accounts, event sites, Chinese game media, global trade media, and reliable wire services are searched directly; Google News is not the sole pool.
- Public social discovery targets Weibo, WeChat articles, Bilibili, TapTap, YouTube, X, Facebook, public Discord invite pages, and Reddit. Private groups and login-only content are outside the web-search boundary.
- Social-account presence is maintained separately from weekly events. Every tracked game receives a persistent storefront/social profile, so an existing X, Facebook or YouTube account remains visible even when it has no new post that week. SteamDB may discover links but is never labeled as official confirmation by itself.
- The primary timeline is overseas-only: preparation, reveal, test, pre-registration, public launch, and live operations. Domestic milestones are retained only as background references and cannot advance the overseas stage or enter the main list without overseas evidence.
- Search and verification requests ask the Responses API for `web_search_call.action.sources`, allowing each run to audit how many source URLs the search tool actually consulted.
- Maintain official Chinese/English names and aliases in `data/game_catalog.json`; it is used only for name matching, never as a news source.
- `manual_sources/daily_input.md` may retain working notes, but its contents are not included in generated reports.
- Each workflow run prints BlueAI search and verification diagnostics without printing the API key.

## Running the Workflow

The `Game Intelligence Weekly` GitHub Actions workflow supports:

- `preview`: collect news, generate a draft, email it, commit `output/preview`, and deploy Pages.
- `publish`: promote a reviewed report to the official archive and deploy Pages.
- `deploy_only`: re-render the current checked-in preview data with the latest UI code and deploy it without calling BlueAI or sending email.

Preview URL:

```text
https://liuxueying2828-maker.github.io/game-intelligence-weekly/preview/index.html
```

GitHub Pages must use `Settings → Pages → Source → GitHub Actions`.

## Local Run

```bash
pip install -r requirements.txt
export BLUEAI_API_KEY="your-company-relay-api-key"
export BLUEAI_BASE_URL="https://bmc-llm-relay.bluemediagroup.cn/v1"
export BLUEAI_MODEL="gpt-4.1"
export EMAIL_TO="xueying.liu@bluefocus.cn"
export EMAIL_API_KEY="your-email-api-key"
export EMAIL_FROM="Game Intelligence Weekly <your-verified-sender@example.com>"
export REPORT_MODE="preview"
python main.py
```
