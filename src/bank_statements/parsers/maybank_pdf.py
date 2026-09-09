"""Parser for Maybank Securities trade confirmations (``Maybank*.pdf``).

A single PDF may contain one or more preliminary confirmations.  Each trade
starts with the ``We confirm you having SOLD/BOUGHT`` marker::

    We confirm you having
    SOLD
    (ISIN. Code: MYL8583OO006)
    450,000
    MAH SING GROUP BHD
    at MYR 1.0691
    ...
    Stamp Duty: 482.00
    TOTAL:      479,867.30

The ``ticker`` is derived from the ISIN: the 4-digit Bursa Malaysia stock code
is embedded in it (e.g. ``MYL8583OO006`` -> ``8583.KL``).  ``date`` and
``settlement_date`` appear once in the header and apply to every trade.
"""

from __future__ import annotations

import re

import pymupdf

from ..records import build_record, normalize, parse_date, to_float, to_int

_TRADE_MARKER = "We confirm you having"


def maybank_pdf2tx(filename: str) -> list[dict]:
    doc = pymupdf.open(filename)
    try:
        text = normalize("\n".join(page.get_text() for page in doc))
    finally:
        doc.close()

    date = parse_date(re.search(r"Trade Date:\s*(\d{1,2}-[A-Za-z]{3}-\d{2,4})", text).group(1))
    settlement_date = parse_date(
        re.search(r"Settlement Date:\s*(\d{1,2}-[A-Za-z]{3}-\d{2,4})", text).group(1)
    )

    return [
        _parse_block(block, date, settlement_date)
        for block in text.split(_TRADE_MARKER)[1:]
    ]


def _parse_block(block: str, date: str, settlement_date: str) -> dict:
    side = {"BOUGHT": "B", "SOLD": "S"}[
        re.match(r"\s*(BOUGHT|SOLD)", block).group(1)
    ]
    isin = re.search(r"ISIN\.\s*Code:\s*([A-Z0-9]+)", block).group(1)
    code = re.search(r"\d{4}", isin).group(0)
    ticker = f"{code}.KL"
    volume = to_int(re.search(r"ISIN\.\s*Code:\s*[A-Z0-9]+\)\s*([\d,]+)", block).group(1))
    price = to_float(re.search(r"at\s*[A-Z]{3}\s*([\d.]+)", block).group(1))
    tax = to_float(re.search(r"Stamp Duty:\s*([\d,.]+)", block).group(1))
    net = to_float(re.search(r"TOTAL:\s*([\d,.]+)", block).group(1))

    return build_record(
        side=side,
        date=date,
        ticker=ticker,
        volume=volume,
        price=price,
        net_amount=net,
        tax=tax,
        settlement_date=settlement_date,
    )
