"""Tests for the J.P. Morgan "Unofficial Order Summary" email parser."""

from __future__ import annotations

from pathlib import Path

from bank_statements.parsers.jpmorgan_eml import jpmorgan_eml2tx
from bank_statements.registry import parse_file

DOCS = Path(__file__).resolve().parents[1] / "docs"
FILE_1 = DOCS / "JPM- Unofficial Order Summary.eml"
FILE_2 = DOCS / "JPM- Unofficial Order Summary[1].eml"


def test_first_email_returns_two_records() -> None:
    expected = [
        {
            "broker": "JPM HK",
            "type": "B",
            "date": "2026-09-02",
            "settlement_date": "2026-09-04",
            "sec_name": "MEITUAN",
            "ticker": "3690.HK",
            "volume": 100000,
            "price": 78.0840,
        },
        {
            "broker": "JPM HK",
            "type": "B",
            "date": "2026-09-02",
            "settlement_date": "2026-09-04",
            "sec_name": "MEITUAN",
            "ticker": "3690.HK",
            "volume": 200000,
            "price": 78.5935,
        },
    ]
    assert jpmorgan_eml2tx(str(FILE_1)) == expected


def test_second_email_returns_two_records() -> None:
    expected = [
        {
            "broker": "JPM HK",
            "type": "B",
            "date": "2026-09-01",
            "settlement_date": "2026-09-03",
            "sec_name": "DONGFANG ELECTRIC CORP LTD-H",
            "ticker": "1072.HK",
            "volume": 200000,
            "price": 20.4473,
        },
        {
            "broker": "JPM",
            "type": "B",
            "date": "2026-09-01",
            "settlement_date": "2026-09-01",
            "sec_name": "ZHEJIANG JIULI HI-TECH-A",
            "ticker": "002318",
            "volume": 235600,
            "price": 20.6448,
        },
    ]
    assert jpmorgan_eml2tx(str(FILE_2)) == expected


def test_dispatch_routes_jpmorgan_eml_files() -> None:
    assert parse_file(str(FILE_1)) == jpmorgan_eml2tx(str(FILE_1))
    assert parse_file(str(FILE_2)) == jpmorgan_eml2tx(str(FILE_2))
