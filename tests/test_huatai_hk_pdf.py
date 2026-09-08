"""Tests for the Huatai Financial Holdings (Hong Kong) parser."""

from __future__ import annotations

from pathlib import Path

from bank_statements.parsers.huatai_hk_pdf import huatai_hk_pdf2tx
from bank_statements.registry import parse_file

DOCS = Path(__file__).resolve().parents[1] / "docs"
FILE = DOCS / "Huatai_HK_1.pdf"


def test_sell_returns_one_record() -> None:
    expected = [
        {
            "type": "S",
            "date": "2026-07-22",
            "settlement_date": "2026-07-22",
            "ticker": "600887",
            "volume": 500000,
            "price": 27.1436,
            "net_amount": 13554372.45,
            "trans_fee": 10641.65,
            "tax": 6785.90,
        }
    ]
    assert huatai_hk_pdf2tx(str(FILE)) == expected


def test_dispatch_routes_huatai_hk_files() -> None:
    assert parse_file(str(FILE)) == huatai_hk_pdf2tx(str(FILE))
