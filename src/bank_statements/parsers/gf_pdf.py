"""Parser for GF Securities (Hong Kong) trade confirmations (``GF-*.pdf``).

A single PDF may contain several trades, each starting with a
``Bargain Number`` block.  Each block lists the instrument, a per-price
quantity breakdown, the ``Total`` quantity, the ``(Average)`` price and the
``Settlement Amount (CNY)``.  No stamp duty is itemised, so ``tax`` is 0.
"""

from __future__ import annotations

import re

import pymupdf

from ..records import build_record, normalize, parse_date, to_float, to_int


def gf_pdf2tx(filename: str) -> list[dict]:
    doc = pymupdf.open(filename)
    try:
        text = normalize("\n".join(page.get_text() for page in doc))
    finally:
        doc.close()

    records: list[dict] = []
    # Each trade starts with "Bargain Number"; drop the (empty) leading chunk.
    for block in text.split("Bargain Number")[1:]:
        records.append(_parse_block(block))
    return records


def _parse_block(block: str) -> dict:
    ticker = re.search(r"Instrument Name\s*:\s*[^(]*\((\d+)\)", block).group(1)
    # Values follow the header labels in order: Bargain No, Trade Date,
    # Settlement Date, ...
    dates = re.findall(r"\d{1,2}/\d{1,2}/\d{4}", block)
    date = parse_date(dates[0])
    settlement_date = parse_date(dates[1])
    side = "S" if re.search(r"Trade Type\s*:\s*SOLD", block) else "B"
    volume = to_int(re.search(r"Total:\s*([\d,]+)", block).group(1))
    price = to_float(re.search(r"([\d.]+)\(Average\)", block).group(1))
    net = to_float(re.search(r"Settlement Amount \(CNY\)\s*([\d,]+(?:\.\d+)?)", block).group(1))

    return build_record(
        side=side,
        date=date,
        ticker=ticker,
        volume=volume,
        price=price,
        net_amount=net,
        tax=0.0,
        settlement_date=settlement_date,
    )
