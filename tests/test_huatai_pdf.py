"""Tests for the Huatai A-share statement parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from bank_statements.parsers.huatai_pdf import huatai_pdf2tx
from bank_statements.records import compute_trans_fee, date_from_filename
from bank_statements.registry import parse_file

DOCS = Path(__file__).resolve().parents[1] / "docs"

SELL_FILE = DOCS / "OtherAT_Huatai_2026.08.26 江苏神通 & 华明装备.pdf"
BUY_FILE = DOCS / "OtherAT_Huatai_2026.05.14 中际旭创.pdf"
FOR_TEST_FILE = DOCS / "for_test" / "OtherAT_Huatai_2026.09.04 中际旭创.pdf"


def test_sell_returns_two_records() -> None:
    expected = [
        {
            "type": "S",
            "date": "2026-08-26",
            "ticker": "002438",
            "volume": 327100,
            "price": 13.938,
            "net_amount": 4556193.90,
            "trans_fee": 646.11,
            "tax": 2279.79,
        },
        {
            "type": "S",
            "date": "2026-08-26",
            "ticker": "002270",
            "volume": 562000,
            "price": 19.382,
            "net_amount": 10886129.53,
            "trans_fee": 1107.68,
            "tax": 5446.79,
        },
    ]
    assert huatai_pdf2tx(str(SELL_FILE)) == expected


def test_buy_returns_one_record() -> None:
    expected = [
        {
            "type": "B",
            "date": "2026-05-14",
            "ticker": "300308",
            "volume": 9400,
            "price": 1055.351,
            "net_amount": 9921541.03,
            "trans_fee": 1241.63,
            "tax": 0.0,
        }
    ]
    assert huatai_pdf2tx(str(BUY_FILE)) == expected


def test_for_test_buy_returns_one_record() -> None:
    expected = [
        {
            "type": "B",
            "date": "2026-09-04",
            "ticker": "300308",
            "volume": 12000,
            "price": 823.562,
            "net_amount": 9883979.28,
            "trans_fee": 1235.28,
            "tax": 0.0,
        }
    ]
    assert huatai_pdf2tx(str(FOR_TEST_FILE)) == expected


def test_dispatch_routes_huatai_files() -> None:
    assert parse_file(str(SELL_FILE)) == huatai_pdf2tx(str(SELL_FILE))
    assert parse_file(str(BUY_FILE)) == huatai_pdf2tx(str(BUY_FILE))


def test_unsupported_file_raises() -> None:
    # EML files are not supported yet.
    other = DOCS / "(8_4) 513887 Trade Done - SCB Private Bank - Equity Order.eml"
    with pytest.raises(ValueError):
        parse_file(str(other))


def test_date_from_filename() -> None:
    assert date_from_filename(SELL_FILE.name) == "2026-08-26"
    assert date_from_filename(BUY_FILE.name) == "2026-05-14"


def test_compute_trans_fee_sell_and_buy() -> None:
    assert compute_trans_fee("S", 13.938, 327100, 4556193.90, 2279.79) == 646.11
    assert compute_trans_fee("B", 1055.351, 9400, 9921541.03, 0.0) == 1241.63
