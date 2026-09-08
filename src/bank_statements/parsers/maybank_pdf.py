"""Parser for Maybank Securities trade confirmations (``Maybank_*.pdf``).

Layout::

    We confirm you having
    BOUGHT
    (ISIN. Code: MYQ0215OO002)
    165,000
    SOLARVEST HOLDINGS BERHAD
    at MYR 2.3302
    ...
    Stamp Duty: 385.00
    TOTAL:      385,463.95

The ``ticker`` is derived from the ISIN: the 4-digit Bursa Malaysia stock code
is embedded at ``ISIN[2:6]`` (e.g. ``MYQ0215OO002`` -> ``0215.KL``).
"""

from __future__ import annotations

import re

import pymupdf

from ..records import build_record, normalize, parse_date, to_float, to_int


def maybank_pdf2tx(filename: str) -> list[dict]:
    doc = pymupdf.open(filename)
    try:
        text = normalize("\n".join(page.get_text() for page in doc))
    finally:
        doc.close()

    side = {"BOUGHT": "B", "SOLD": "S"}[
        re.search(r"We confirm you having\s*(BOUGHT|SOLD)", text).group(1)
    ]

    isin = re.search(r"ISIN\.\s*Code:\s*([A-Z0-9]+)", text).group(1)
    # Bursa Malaysia ISIN embeds the 4-digit stock code (e.g. MYQ0215OO002 -> 0215).
    code = re.search(r"\d{4}", isin).group(0)
    ticker = f"{code}.KL"
    volume = to_int(re.search(r"ISIN\.\s*Code:\s*[A-Z0-9]+\)\s*([\d,]+)", text).group(1))
    price = to_float(re.search(r"at\s*[A-Z]{3}\s*([\d.]+)", text).group(1))
    tax = to_float(re.search(r"Stamp Duty:\s*([\d,.]+)", text).group(1))
    net = to_float(re.search(r"TOTAL:\s*([\d,.]+)", text).group(1))
    date = parse_date(re.search(r"Trade Date:\s*(\d{1,2}-[A-Za-z]{3}-\d{2,4})", text).group(1))
    settlement_date = parse_date(re.search(r"Settlement Date:\s*(\d{1,2}-[A-Za-z]{3}-\d{2,4})", text).group(1))

    return [build_record(
        side=side,
        date=date,
        ticker=ticker,
        volume=volume,
        price=price,
        net_amount=net,
        tax=tax,
        settlement_date=settlement_date,
    )]
