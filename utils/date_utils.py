from datetime import datetime


def parse_report_date(value=None):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value.strip():
        text = value.strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(text[: len(fmt)], fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now()
    return datetime.now()


def report_date_parts(value=None):
    report_date = parse_report_date(value)
    formatted = report_date.strftime("%b %d, %Y").replace(" 0", " ")
    return {
        "date": report_date.strftime("%Y-%m-%d"),
        "formatted_date": formatted,
        "iso_week": f"Week {report_date.isocalendar()[1]}",
    }
