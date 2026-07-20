from financial_normalization import parse_amount_to_yuan, parse_percentage_points
from financial_normalization import infer_report_type, normalize_report_period, normalize_security_code


def test_parse_amount_to_yuan_preserves_negative_amount():
    assert parse_amount_to_yuan("-2181万") == -21_810_000


def test_parse_amount_to_yuan_supports_yi_and_commas():
    assert parse_amount_to_yuan("752.60亿") == 75_260_000_000
    assert parse_amount_to_yuan("1,234.5万") == 12_345_000


def test_parse_amount_to_yuan_returns_none_for_missing_or_invalid():
    assert parse_amount_to_yuan("--") is None
    assert parse_amount_to_yuan("") is None
    assert parse_amount_to_yuan("无法解析") is None


def test_parse_percentage_points_keeps_percentage_points():
    assert parse_percentage_points("6.36%") == 6.36
    assert parse_percentage_points(-19.39) == -19.39


def test_normalize_report_period_and_type():
    assert normalize_report_period("2026/03/31") == "2026-03-31"
    assert infer_report_type("2026-03-31") == "Q1"
    assert infer_report_type("2025-12-31") == "FY"


def test_normalize_security_code_corrects_market_prefix():
    assert normalize_security_code("SZ600998") == ("SH600998", "SH")
    assert normalize_security_code("002788") == ("SZ002788", "SZ")
