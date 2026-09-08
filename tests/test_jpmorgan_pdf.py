"""Tests for the J.P. Morgan Private Bank parser."""

from __future__ import annotations

from pathlib import Path

from bank_statements.parsers.jpmorgan_pdf import jpmorgan_pdf2tx
from bank_statements.registry import parse_file

DOCS = Path(__file__).resolve().parents[1] / "docs"
JPM_CNH = DOCS / "JPM_62856134_3839260_2026-09-01.pdf"
JPM_HKD = DOCS / "JPM_62884986_5179260_2026-09-02.pdf"


def test_jiuli_maps_to_jpm() -> None:
    expected = [
        {
            "broker": "JPM",
            "type": "B",
            "date": "2026-09-01",
            "sec_name": "ZHEJIANG JIULI HI-TECH METALS CO LT",
            "ticker": "002318.SZ",
            "volume": 235600,
            "price": 20.6448,
            "net_amount": 4871619.81,
            "trans_fee": 7704.93,
            "tax": 0.0,
        }
    ]
    assert jpmorgan_pdf2tx(str(JPM_CNH)) == expected


def test_meituan_maps_to_jpm_hk() -> None:
    expected = [
        {
            "broker": "JPM HK",
            "type": "B",
            "date": "2026-09-02",
            "sec_name": "MEITUAN",
            "ticker": "3690.HK",
            "volume": 200000,
            "price": 78.5935,
            "net_amount": 15759333.14,
            "trans_fee": 24914.14,
            "tax": 15719.0,
        }
    ]
    assert jpmorgan_pdf2tx(str(JPM_HKD)) == expected


def test_dispatch_routes_jpmorgan_files() -> None:
    assert parse_file(str(JPM_CNH)) == jpmorgan_pdf2tx(str(JPM_CNH))
    assert parse_file(str(JPM_HKD)) == jpmorgan_pdf2tx(str(JPM_HKD))
