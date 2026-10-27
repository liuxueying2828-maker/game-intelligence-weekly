import os

from config import BLUEAI_BASE_URL, BLUEAI_MODEL
from intelligence.normalization import build_source_fallback, ensure_minimum_dashboard_signals, parse_dashboard_json
from intelligence.prompt import build_dashboard_prompt


def generate_dashboard_data(items):
    api_key = os.getenv("BLUEAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing BLUEAI_API_KEY environment variable.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Missing openai package. Run: python3 -m pip install -r requirements.txt") from exc

    try:
        with OpenAI(
            api_key=api_key,
            base_url=os.getenv("BLUEAI_BASE_URL") or BLUEAI_BASE_URL,
            timeout=180.0,
            max_retries=2,
        ) as client:
            response = client.responses.create(
                model=os.getenv("BLUEAI_MODEL") or BLUEAI_MODEL,
                input=build_dashboard_prompt(items),
            )
        parsed = parse_dashboard_json(response.output_text.strip())
        return ensure_minimum_dashboard_signals(parsed, items)
    except Exception as exc:
        return build_source_fallback(
            items,
            f"BlueAI analysis failed; rendered source-based fallback content. Error: {exc}",
        )
