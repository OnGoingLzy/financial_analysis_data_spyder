from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import datetime


MISSING_MARKERS = {"", "--", "-", "N/A", "None", "null"}


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).replace(",", "").strip()
    return None if text in MISSING_MARKERS else text


def parse_amount_to_yuan(value: object) -> int | None:
    text = _clean(value)
    if text is None:
        return None
    multiplier = Decimal(1)
    if text.endswith("亿"):
        text, multiplier = text[:-1], Decimal(100_000_000)
    elif text.endswith("万"):
        text, multiplier = text[:-1], Decimal(10_000)
    try:
        amount = Decimal(text) * multiplier
    except InvalidOperation:
        return None
    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def parse_percentage_points(value: object) -> float | None:
    text = _clean(value)
    if text is None:
        return None
    if text.endswith("%"):
        text = text[:-1]
    try:
        return float(Decimal(text))
    except InvalidOperation:
        return None


def normalize_report_period(value: object) -> str | None:
    text = _clean(value)
    if text is None:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def infer_report_type(period: str | None) -> str | None:
    if not period:
        return None
    return {"03-31": "Q1", "06-30": "H1", "09-30": "Q3", "12-31": "FY"}.get(period[5:])


def normalize_security_code(value: object) -> tuple[str, str]:
    digits = "".join(character for character in str(value) if character.isdigit())[-6:]
    if len(digits) != 6:
        raise ValueError("证券代码必须包含六位数字")
    market = "SH" if digits[0] in {"5", "6", "9"} else "SZ"
    return f"{market}{digits}", market
