"""Tests for the GF Securities (Hong Kong) parser."""

from __future__ import annotations

from pathlib import Path

from bank_statements.parsers.gf_pdf import gf_pdf2tx
from bank_statements.registry import parse_file

DOCS = Path(__file__).resolve().parents[1] / "docs"
FILE = DOCS / "GF-20260826-10821237-BG20260826000033-2026051200000011.pdf"


def test_returns_two_records() -> None:
    # The PDF contains two bargain blocks; the first matches the README example.
    expected = [
        {
            "type": "B",
            "date": "2026-08-26",
            "settlement_date": "2026-08-27",
            "ticker": "002270",
            "volume": 562000,
            "price": 19.3949,
            "net_amount": 10909589.65,
            "trans_fee": 9655.85,
            "tax": 0.0,
        },
        {
            "type": "B",
            "date": "2026-08-26",
            "settlement_date": "2026-08-27",
            "ticker": "002438",
            "volume": 860900,
            "price": 13.9591,
            "net_amount": 12028014.57,
            "trans_fee": 10625.38,
            "tax": 0.0,
        },
    ]
    assert gf_pdf2tx(str(FILE)) == expected


def test_dispatch_routes_gf_files() -> None:
    assert parse_file(str(FILE)) == gf_pdf2tx(str(FILE))
