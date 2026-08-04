"""Jalali (Shamsi) date formatting for blog dates."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional, Union

import jdatetime

_FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


def to_fa_digits(value: object) -> str:
    return "".join(_FA_DIGITS[int(ch)] if ch.isdigit() else ch for ch in str(value))


def format_jalali(value: Optional[Union[datetime, date]]) -> str:
    """Format a Gregorian datetime/date as a Persian '۱۵ تیر ۱۴۰۵' string."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        j = jdatetime.datetime.fromgregorian(datetime=value)
    else:
        j = jdatetime.date.fromgregorian(date=value)
    return to_fa_digits(f"{j.day} {jdatetime.date.j_months_fa[j.month - 1]} {j.year}")


def format_reading_time(value: Optional[str]) -> str:
    """Format stored reading time as Persian, e.g. '2' → '۲ ساعت', '20m' → '۲۰ دقیقه'."""
    if not value:
        return ""
    raw = value.strip()
    if not raw:
        return ""

    if "ساعت" in raw or "دقیقه" in raw:
        return to_fa_digits(raw)

    lower = raw.lower()
    if lower in {"ongoing", "continuous"}:
        return "مداوم"

    minute_match = re.match(r"^(\d+(?:[.,]\d+)?)\s*m(?:in(?:ute)?s?)?$", lower)
    if minute_match:
        return f"{to_fa_digits(minute_match.group(1).replace(',', '.'))} دقیقه"

    hour_match = re.match(r"^(\d+(?:[.,]\d+)?)\s*h(?:ours?)?$", lower)
    if hour_match:
        return f"{to_fa_digits(hour_match.group(1).replace(',', '.'))} ساعت"

    if re.match(r"^\d+(?:[.,]\d+)?$", raw):
        return f"{to_fa_digits(raw.replace(',', '.'))} ساعت"

    return to_fa_digits(raw)


def format_reading_hours(hours: Optional[float]) -> str:
    """Format numeric reading hours for competency summaries."""
    if hours is None:
        return "—"
    if hours == 0:
        return "—"
    if hours == int(hours):
        return f"{to_fa_digits(int(hours))} ساعت"
    normalized = f"{hours:.1f}".rstrip("0").rstrip(".")
    return f"{to_fa_digits(normalized)} ساعت"


def parse_reading_time_to_hours(value: Optional[str]) -> float:
    """Parse stored reading_time to hours for summing, e.g. '3h' → 3.0, '20m' → 0.33."""
    if not value:
        return 0.0
    raw = value.strip()
    if not raw:
        return 0.0

    if "دقیقه" in raw:
        num = re.sub(r"[^\d.,]", "", raw).replace(",", ".")
        return float(num) / 60 if num else 0.0

    if "ساعت" in raw:
        num = re.sub(r"[^\d.,]", "", raw).replace(",", ".")
        return float(num) if num else 0.0

    lower = raw.lower()
    if lower in {"ongoing", "continuous"}:
        return 0.0

    minute_match = re.match(r"^(\d+(?:[.,]\d+)?)\s*m(?:in(?:ute)?s?)?$", lower)
    if minute_match:
        return float(minute_match.group(1).replace(",", ".")) / 60

    hour_match = re.match(r"^(\d+(?:[.,]\d+)?)\s*h(?:ours?)?$", lower)
    if hour_match:
        return float(hour_match.group(1).replace(",", "."))

    if re.match(r"^\d+(?:[.,]\d+)?$", raw):
        return float(raw.replace(",", "."))

    return 0.0
