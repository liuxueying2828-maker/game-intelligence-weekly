# Game Intelligence Weekly

An automated release, globalization, and marketing intelligence radar for BluefocusAI_Madhouse_Game Brand.

GitHub Actions → RSS and Google News → Manual Editorial Inputs → Gemini Analysis → HTML Dashboard → GitHub Pages and Email

The MVP source layer uses separate Chinese and English Google News editions, a priority-company watch list, direct industry/official RSS feeds, and a maintained bilingual game-name catalog in `data/game_catalog.json`.

## Intelligence Scope

The weekly dashboard contains four sections:

1. **新游上线与测试日历 / Release & Test Calendar**
   - First reveal, pre-registration, license approval, playtest, closed beta, open beta, demo, public launch, official release, exhibition demo, and new platform releases.
2. **出海与区域发行机会 / Global Launch Opportunities**
   - Separate China and overseas schedules, global pre-registration, overseas tests, localization, regional publishing, official English presence, and overseas social signals.
3. **游戏营销、联名与 IP 合作 / Marketing & Collaborations**
   - Brand partnerships, IP crossovers, co-created content, pop-ups, retail activations, entertainment collaborations, and platform campaigns.
4. **厂商、平台与 AI 动向 / Companies, Platforms & AI**
   - Publisher and studio strategy, platform policy, investment and acquisition, and AI in game production, localization, testing, NPCs, and player operations.

Platforms are tags rather than top-level sections: `PC`, `Mobile`, `Console`, `Multi-platform`, `Mini Game`, `Cloud Gaming`, and `Unknown`.

## Editorial Rules

- Chinese and official English game names are shown together as `中文名 / English Name`.
- If no official English name exists, use `English name not announced`; never invent a translation.
- China and overseas milestones must be recorded separately.
- First reveal, license approval, exhibition appearance, test, open beta, and official launch are different event types.
- A quarter, year, or approximate window must remain approximate; the system must not invent a precise date.
- The radar covers announcements published in the last 30 days and may include confirmed events in the coming 30/90 days.
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
│   └── gemini.py
├── manual_sources/
│   ├── daily_input.md
│   └── examples.md
├── data/
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

- Add or tune event searches, priority companies, feeds, and filtering rules in `config.py`.
- Maintain official Chinese/English names and known regional milestones in `data/game_catalog.json`.
- Add verified one-off intelligence to `manual_sources/daily_input.md`.
- Each workflow run prints candidate diagnostics by source, section, and search language before Gemini is called.

## Running the Workflow

The `Game Intelligence Weekly` GitHub Actions workflow supports:

- `preview`: collect news, generate a draft, email it, commit `output/preview`, and deploy Pages.
- `publish`: promote a reviewed report to the official archive and deploy Pages.
- `deploy_only`: deploy the current checked-in preview without calling Gemini or sending email.

Preview URL:

```text
https://liuxueying2828-maker.github.io/game-intelligence-weekly/preview/index.html
```

GitHub Pages must use `Settings → Pages → Source → GitHub Actions`.

## Local Run

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-gemini-api-key"
export EMAIL_TO="xueying.liu@bluefocus.cn"
export EMAIL_API_KEY="your-email-api-key"
export EMAIL_FROM="Game Intelligence Weekly <your-verified-sender@example.com>"
export REPORT_MODE="preview"
python main.py
```
