"""Jalali (Shamsi) date formatting for blog dates."""

from __future__ import annotations

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
