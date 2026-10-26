# Digital Commerce Intelligence Hub

A weekly industry intelligence dashboard for BluefocusAI_Madhouse_Game Brand intelligence and opportunity discovery.

This project has been upgraded from a simple news push bot into a weekly web-based intelligence dashboard:

GitHub Actions -> Python source collectors -> Unified Information Pool -> Gemini JSON analysis -> HTML Dashboard -> GitHub Pages + Email notification

## What It Does

The system collects automatic and manual signals, then asks Gemini to produce short structured dashboard content focused on:

- 国内电商平台 / Platform Intelligence
- AI 技术前沿 / AI Technology
- 体育与户外行业 / Sports & Outdoor
- 传统零售创新 / Retail Innovation
- One Thing Worth Watching

The dashboard is designed for BluefocusAI_Madhouse_Game Brand leaders to scan in 2-3 minutes. Gemini may return empty sections when no reliable source-backed signals are available.

## Information Sources

Automatic sources:

- RSS feeds filtered by section profile
- Google News RSS keyword searches grouped by section
- Official blogs

Automatic retrieval is sectioned before Gemini analysis. Each section uses its own keywords and searches recent information in widening windows: 3 days first, then 7 days, then 14 days. The four automatic sections are:

- 国内电商平台 / Platform Intelligence
- AI 能力与行业影响 / AI Capabilities & Industry Impact
- 体育与户外行业 / Sports & Outdoor
- 传统零售创新 / Retail Innovation

Manual source:

- `manual_sources/daily_input.md`

Automatic filtering ranks usefulness over recency. It excludes low-relevance retail media, ad-network, campaign, celebrity, sponsorship, and weak product-only items. AI filtering is business-first: pure model releases, parameter counts, benchmarks, papers, and low-level infrastructure details are ignored unless the item clearly introduces a business-understandable capability for retail, ecommerce, customer experience, operations, workflow, or enterprise adoption.

Future sources can be added as new modules under `sources/`, such as PDF, Feishu Docs, or internal business data.

## Project Structure

```text
.
├── main.py
├── config.py
├── requirements.txt
├── .github/
│   └── workflows/
│       └── daily.yml
├── sources/
│   ├── common.py
│   ├── rss.py
│   ├── google_news.py
│   └── manual.py
├── manual_sources/
│   ├── daily_input.md
│   └── examples.md
├── intelligence/
│   ├── prompt.py
│   └── gemini.py
└── output/
    ├── email.py
    ├── feishu.py
    ├── html.py
    └── index.html
```

## Dashboard Output

Running the script generates:

```text
output/index.html
```

GitHub Actions publishes this file to GitHub Pages.

Email notification sends a plain-text brief after each GitHub Actions run. It does not send the full HTML dashboard code.

```text
Subject: Digital Commerce Intelligence Brief - YYYY-MM-DD

Today's Focus
...

Platform Intelligence
News: ...
Why this matters: ...
Trend: ...
```

## GitHub Secrets

Add these repository secrets:

- `GEMINI_API_KEY`
- `EMAIL_TO`
- `EMAIL_API_KEY`
- `EMAIL_FROM` optional, depending on your email API sender setup

The API keys are loaded from environment variables. Do not hard-code them in the project. The existing Feishu module is retained for optional testing with `ENABLE_FEISHU_TEST=true` and `FEISHU_WEBHOOK_URL`.

## Run Locally

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-gemini-api-key"
export EMAIL_TO="xueying.liu@bluefocus.cn"
export EMAIL_API_KEY="your-email-api-key"
export EMAIL_FROM="Digital Commerce Intelligence <your-verified-sender@example.com>"
export DASHBOARD_URL="https://your-name.github.io/your-repo/"
python main.py
```

Local output will be written to `output/index.html`.

## GitHub Actions

The workflow supports:

- Manual run through `workflow_dispatch`
- Weekly scheduled run every Tuesday through cron in UTC
- GitHub Pages deployment from `output/index.html`

Before the first deployment, set repository Pages source to GitHub Actions in GitHub:

Settings -> Pages -> Build and deployment -> Source -> GitHub Actions

See `.github/workflows/daily.yml`.


## History Archive

Each run generates the latest dashboard at `output/index.html` and saves the same day into:

```text
output/archive/YYYY-MM-DD/index.html
output/data/YYYY-MM-DD.json
```

`output/archive/index.html` lists all saved intelligence briefs in reverse date order. GitHub Actions commits `output/archive` and `output/data` back to the repository so GitHub Pages keeps historical pages across runs.
