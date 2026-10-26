import os

from config import GEMINI_MODEL
from intelligence.normalization import build_source_fallback, ensure_minimum_dashboard_signals, parse_dashboard_json
from intelligence.prompt import build_dashboard_prompt


def generate_dashboard_data(items):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable.")

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError("Missing google-genai package. Run: python3 -m pip install -r requirements.txt") from exc

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL") or GEMINI_MODEL
    try:
        response = client.models.generate_content(
            model=model,
            contents=build_dashboard_prompt(items),
            config={"response_mime_type": "application/json", "max_output_tokens": 16384},
        )
        parsed = parse_dashboard_json(response.text.strip())
        return ensure_minimum_dashboard_signals(parsed, items)
    except Exception as exc:
        return build_source_fallback(
            items,
            f"Gemini analysis failed; rendered source-based fallback content. Error: {exc}",
        )
