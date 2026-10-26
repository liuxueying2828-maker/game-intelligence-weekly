import os

import requests


def send_text_message(text):
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("Missing FEISHU_WEBHOOK_URL environment variable.")

    payload = {
        "msg_type": "text",
        "content": {
            "text": text,
        },
    }

    response = requests.post(webhook_url, json=payload, timeout=30)
    response.raise_for_status()
    print(f"Feishu response: {response.status_code} {response.text}")
