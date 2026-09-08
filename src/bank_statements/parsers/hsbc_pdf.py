"""Parser for HSBC Global Private Banking equity advices (``HSBC-*.pdf``).

The ``EQUITIES ADVICE`` page uses a value-then-label layout::

    CHINA PETROLEUM AND CHEMICAL CORP H SHS 386   : Security Name
    Unit Price   HKD4.521900
    13,582,000   No. Of Shares
    Consideration
    28JUL2025    HKD61,416,445.80                 : Trade Date
    Settlement Amount   HKD61,257,683.75
    : 30JUL2025  Settlement

``broker`` is decided by ``ACCOUNT NAME``: ``IKARIA GROUP (HK) LIMITED`` maps
to ``HSBC HK``, anything else to ``HSBC``.  ``tax`` is 0.0 (all charges,
including stamp duty, are folded into ``trans_fee`` which is computed as the
exact gross consideration minus the net amount).
"""

from __future__ import annotations

import re

import pymupdf

from ..records import build_record, normalize, parse_date, round2, to_float, to_int


def hsbc_pdf2tx(filename: str) -> list[dict]:
    doc = pymupdf.open(filename)
    try:
        text = normalize("\n".join(page.get_text() for page in doc))
    finally:
        doc.close()

    account = re.search(
        r"ACCOUNT NAME:\s*.*?(IKARIA GROUP(?: \(HK\))? LIMITED)", text, re.S
    ).group(1)
    broker = "HSBC HK" if "(HK)" in account else "HSBC"

    side = "S" if re.search(
        r"instruction to (sell|buy|purchase) the following", text, re.I
    ).group(1).lower() == "sell" else "B"

    code = re.search(r"SHS\s*(\d+)", text).group(1)
    ticker = f"{int(code):04d}.HK"
    date = parse_date(re.search(r"(\d{1,2}[A-Za-z]{3}\d{4})\s*HKD", text).group(1))
    settlement_date = parse_date(
        re.search(r"(\d{1,2}[A-Za-z]{3}\d{4})\s*Settlement\s*:", text).group(1)
    )
    price = to_float(re.search(r"Unit Price\s*HKD\s*([\d.]+)", text).group(1))
    volume = to_int(re.search(r"([\d,]+)\s*No\.\s*Of Shares", text).group(1))
    net = to_float(re.search(r"Settlement Amount\s*HKD\s*([\d,.]+)", text).group(1))
    consideration = to_float(re.search(r"HKD\s*([\d,.]+)\s*:?\s*Trade Date", text).group(1))

    return [build_record(
        side=side,
        date=date,
        ticker=ticker,
        volume=volume,
        price=price,
        net_amount=net,
        tax=0.0,
        settlement_date=settlement_date,
        broker=broker,
        trans_fee=round2(consideration - net),
    )]
