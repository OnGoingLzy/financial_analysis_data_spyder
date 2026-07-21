from selenium_spyder import build_statement_rows


def test_build_statement_rows_uses_candidate_labels_and_keeps_missing_values():
    rows = build_statement_rows(
        periods=["2026-03-31", "2025-12-31"],
        table_rows={
            "经营活动产生的现金流量净额": ["12亿", "20亿"],
            "购建固定资产、无形资产和其他长期资产支付的现金": ["2亿", "3亿"],
        },
        field_labels={
            "net_operating_cash_flow": ("经营活动产生的现金流量净额",),
            "capital_expenditure": ("资本性支出", "购建固定资产、无形资产和其他长期资产支付的现金"),
            "ending_cash_and_equivalents": ("期末现金及现金等价物余额",),
        },
    )
    assert rows == [
        {"disclosure_date": "2026-03-31", "net_operating_cash_flow": "12亿", "capital_expenditure": "2亿", "ending_cash_and_equivalents": None},
        {"disclosure_date": "2025-12-31", "net_operating_cash_flow": "20亿", "capital_expenditure": "3亿", "ending_cash_and_equivalents": None},
    ]
