import json
import os

from config import OPENAI_MODEL
from intelligence.normalization import build_source_fallback, ensure_minimum_dashboard_signals, normalize_dashboard_data
from intelligence.prompt import build_dashboard_prompt


CARD_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "summary_points": {"type": "array", "items": {"type": "string"}},
        "link": {"type": "string"},
    },
    "required": ["name", "summary_points", "link"],
    "additionalProperties": False,
}

AI_CARD_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary_points": {"type": "array", "items": {"type": "string"}},
        "link": {"type": "string"},
    },
    "required": ["title", "summary_points", "link"],
    "additionalProperties": False,
}

DASHBOARD_SCHEMA = {
    "type": "object",
    "properties": {
        "date": {"type": "string"},
        "headline": {"type": "string"},
        "platform": {"type": "array", "items": CARD_SCHEMA},
        "ai": {"type": "array", "items": AI_CARD_SCHEMA},
        "sports": {"type": "array", "items": CARD_SCHEMA},
        "retail": {"type": "array", "items": CARD_SCHEMA},
        "one_thing_worth_watching": {"type": "string"},
    },
    "required": ["date", "headline", "platform", "ai", "sports", "retail", "one_thing_worth_watching"],
    "additionalProperties": False,
}


def generate_dashboard_data(items):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Missing openai package. Run: python3 -m pip install -r requirements.txt") from exc

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL") or OPENAI_MODEL
    try:
        response = client.responses.create(
            model=model,
            input=build_dashboard_prompt(items),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "game_intelligence_dashboard",
                    "strict": True,
                    "schema": DASHBOARD_SCHEMA,
                }
            },
            max_output_tokens=16000,
        )
        data = normalize_dashboard_data(json.loads(response.output_text))
        return ensure_minimum_dashboard_signals(data, items)
    except Exception as exc:
        return build_source_fallback(
            items,
            f"OpenAI analysis failed; rendered source-based fallback content. Error: {exc}",
        )
