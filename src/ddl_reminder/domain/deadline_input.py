"""Strict, local wall-clock input shared by QML and MCP."""

import re
from datetime import date, time


def parse_deadline(date_text: str, time_text: str) -> tuple[date, time]:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date_text):
        raise ValueError("日期必须使用 YYYY-MM-DD 格式")
    if not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", time_text):
        raise ValueError("时间必须使用 HH:MM 格式，范围为 00:00–23:59")
    return date.fromisoformat(date_text), time.fromisoformat(time_text)
