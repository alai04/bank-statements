"""Tests for the HSBC Global Private Banking parser."""

from __future__ import annotations

from pathlib import Path

from bank_statements.parsers.hsbc_pdf import hsbc_pdf2tx
from bank_statements.registry import parse_file

DOCS = Path(__file__).resolve().parents[1] / "docs"
FILE_620351 = DOCS / "HSBC-8088-620351-0001_Trade Confirmation as of 28 July 2025.pdf"
FILE_624122 = DOCS / "HSBC-8088-624122-0001_Trade Confirmation as of 28 July 2025.pdf"


def test_620351_account_name_maps_to_hsbc() -> None:
    expected = [
        {
            "broker": "HSBC",
            "type": "S",
            "date": "2025-07-28",
            "settlement_date": "2025-07-30",
            "ticker": "0386.HK",
            "volume": 13582000,
            "price": 4.521900,
            "net_amount": 61257683.75,
            "trans_fee": 158762.05,
            "tax": 0.0,
        }
    ]
    assert hsbc_pdf2tx(str(FILE_620351)) == expected


def test_624122_account_name_maps_to_hsbc_hk() -> None:
    expected = [
        {
            "broker": "HSBC HK",
            "type": "S",
            "date": "2025-07-28",
            "settlement_date": "2025-07-30",
            "ticker": "0386.HK",
            "volume": 6250000,
            "price": 4.522800,
            "net_amount": 28194428.02,
            "trans_fee": 73071.98,
            "tax": 0.0,
        }
    ]
    assert hsbc_pdf2tx(str(FILE_624122)) == expected


def test_dispatch_routes_hsbc_files() -> None:
    assert parse_file(str(FILE_620351)) == hsbc_pdf2tx(str(FILE_620351))
    assert parse_file(str(FILE_624122)) == hsbc_pdf2tx(str(FILE_624122))
