"""Tests for the IIFL Capital Services parser."""

from __future__ import annotations

from pathlib import Path

from bank_statements.parsers.iifl_pdf import iifl_pdf2tx
from bank_statements.registry import parse_file

DOCS = Path(__file__).resolve().parents[1] / "docs"
FILE = DOCS / "IIFL_23062026.PDF"


def test_buy_returns_one_record() -> None:
    expected = [
        {
            "type": "B",
            "date": "2026-06-23",
            "settlement_date": "2026-06-24",
            "sec_name": "POWER GRID CORP. LTD.",
            "isin": "INE752E01010",
            "ticker": "POWERGRID.NS",
            "volume": 613689,
            "price": 291.811,
            "trans_fee": 268621.80,
            "tax": 228454.75,
        }
    ]
    assert iifl_pdf2tx(str(FILE)) == expected


def test_dispatch_routes_iifl_files() -> None:
    assert parse_file(str(FILE)) == iifl_pdf2tx(str(FILE))
