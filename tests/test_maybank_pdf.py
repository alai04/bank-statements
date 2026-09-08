"""Tests for the Maybank Securities parser."""

from __future__ import annotations

from pathlib import Path

from bank_statements.parsers.maybank_pdf import maybank_pdf2tx
from bank_statements.registry import parse_file

DOCS = Path(__file__).resolve().parents[1] / "docs"
BUY_FILE = DOCS / "Maybank_0114460klsusd_eml_20260225174351.pdf"
SELL_FILE = DOCS / "Maybank_0114460klsusd_eml_20260505175106.pdf"


def test_buy_returns_one_record() -> None:
    expected = [
        {
            "type": "B",
            "date": "2026-02-25",
            "settlement_date": "2026-02-27",
            "ticker": "0215.KL",
            "volume": 165000,
            "price": 2.3302,
            "net_amount": 385463.95,
            "trans_fee": 595.95,
            "tax": 385.0,
        }
    ]
    assert maybank_pdf2tx(str(BUY_FILE)) == expected


def test_sell_returns_one_record() -> None:
    expected = [
        {
            "type": "S",
            "date": "2026-05-05",
            "settlement_date": "2026-05-07",
            "ticker": "5264.KL",
            "volume": 1020800,
            "price": 0.9038,
            "net_amount": 920246.01,
            "trans_fee": 1430.03,
            "tax": 923.0,
        }
    ]
    assert maybank_pdf2tx(str(SELL_FILE)) == expected


def test_dispatch_routes_maybank_files() -> None:
    assert parse_file(str(BUY_FILE)) == maybank_pdf2tx(str(BUY_FILE))
    assert parse_file(str(SELL_FILE)) == maybank_pdf2tx(str(SELL_FILE))
