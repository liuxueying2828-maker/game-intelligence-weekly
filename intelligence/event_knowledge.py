import json
from datetime import datetime


def load_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def format_event_knowledge(taxonomy_path, source_registry_path, marketing_rules_path, history_path):
    taxonomy = load_json(taxonomy_path, {})
    sources = load_json(source_registry_path, {})
    marketing = load_json(marketing_rules_path, {})
    history = load_json(history_path, {"events": []})
    return "\n\n".join([
        "EVENT TAXONOMY:\n" + json.dumps(taxonomy, ensure_ascii=False),
        "SOURCE REGISTRY:\n" + json.dumps(sources, ensure_ascii=False),
        "MARKETING RULES:\n" + json.dumps(marketing, ensure_ascii=False),
        "KNOWN EXTERNALLY SOURCED EVENT HISTORY:\n" + json.dumps(history.get("events", [])[-300:], ensure_ascii=False),
    ])


def update_event_history(path, records):
    payload = load_json(path, {"version": 1, "events": []})
    events = payload.setdefault("events", [])
    indexed = {str(item.get("candidate_id") or ""): item for item in events if item.get("candidate_id")}
    for record in records:
        if record.get("verification_status") not in {"verified", "reported_unconfirmed"}:
            continue
        candidate_id = str(record.get("candidate_id") or "").strip()
        sources = [source.get("url") for source in record.get("sources", []) if isinstance(source, dict) and source.get("url")]
        if not candidate_id or not sources:
            continue
        event = {
            "candidate_id": candidate_id,
            "company_cn": record.get("company_cn", ""),
            "company_en": record.get("company_en", ""),
            "game_cn": record.get("game_cn", ""),
            "game_en": record.get("game_en", ""),
            "official_event_name": record.get("official_event_name", ""),
            "normalized_stage": record.get("normalized_stage", "unknown"),
            "test_sequence": record.get("test_sequence", "unknown"),
            "access_type": record.get("access_type", "unknown"),
            "test_goal": record.get("test_goal", "unknown"),
            "regions": record.get("regions", []),
            "platforms": record.get("platforms", []),
            "published_date": record.get("published_date", ""),
            "event_date": record.get("event_date", ""),
            "verification_status": record.get("verification_status", ""),
            "source_urls": sources,
            "last_seen_at": datetime.now().strftime("%Y-%m-%d"),
        }
        if candidate_id in indexed:
            indexed[candidate_id].update(event)
        else:
            events.append(event)
            indexed[candidate_id] = event
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
