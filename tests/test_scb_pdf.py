"""Tests for the Standard Chartered Private Bank eAdvice parser."""

from __future__ import annotations

from pathlib import Path

from bank_statements.parsers.scb_pdf import scb_pdf2tx
from bank_statements.registry import parse_file

DOCS = Path(__file__).resolve().parents[1] / "docs"
FILE = DOCS / "SCB-08-Apr-2026.pdf"


def test_sell_returns_one_record() -> None:
    expected = [
        {
            "type": "S",
            "date": "2026-04-08",
            "settlement_date": "2026-04-10",
            "ticker": "0857.HK",
            "volume": 2000000,
            "amount": 21066200.0,
            "price": 10.5331,
            "trans_fee": 48137.07,
            "tax": 0.0,
        }
    ]
    assert scb_pdf2tx(str(FILE)) == expected


def test_dispatch_routes_scb_files() -> None:
    assert parse_file(str(FILE)) == scb_pdf2tx(str(FILE))
