"""Parser for Standard Chartered Private Bank eAdvice PDFs (``SCB-*.pdf``).

Only the ``Transaction Advice`` sections (equity orders) are parsed; the
``Time Deposit Rollover`` sections are not stock trades and are skipped.

Per the project README, ``price`` is computed as ``amount / volume`` and
``trans_fee`` is the ``Total commission & expenses`` from the file.
"""

from __future__ import annotations

import re

import pymupdf

from ..records import normalize, parse_date, round2, to_float, to_int

_SIDE = re.compile(r"We (sold|bought) for your account")


def scb_pdf2tx(filename: str) -> list[dict]:
    doc = pymupdf.open(filename)
    try:
        text = normalize("\n".join(page.get_text() for page in doc))
    finally:
        doc.close()

    records: list[dict] = []
    for match in _SIDE.finditer(text):
        side = "S" if match.group(1) == "sold" else "B"
        records.append(_parse_block(side, text[match.end():]))
    return records


def _parse_block(side: str, block: str) -> dict:
    # Labels (Value Date / Trade Date / At) are followed by their values.
    dates = re.search(
        r"Value Date\s*Trade Date\s*At\s*(\d{1,2} \w+ \d{4})\s*(\d{1,2} \w+ \d{4})",
        block,
    )
    settlement_date = parse_date(dates.group(1))
    date = parse_date(dates.group(2))

    ticker = f"{re.search(r'Security[\s\S]*?\((\d+)\)', block).group(1)}.HK"
    volume = to_int(re.search(r"([\d,]+) at [\d.]+", block).group(1))
    amount = round2(to_float(re.search(r"Total amount\s*HKD\s*([\d,.]+)", block).group(1)))
    trans_fee = round2(to_float(
        re.search(r"Total commission & expenses.*?HKD\s*([\d,.]+)", block).group(1)
    ))
    price = round(amount / volume, 6)

    return {
        "type": side,
        "date": date,
        "settlement_date": settlement_date,
        "ticker": ticker,
        "volume": int(volume),
        "amount": amount,
        "price": price,
        "trans_fee": trans_fee,
        "tax": 0.0,
    }
