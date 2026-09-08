"""Parser for Huatai Financial Holdings (Hong Kong) confirmations
(``Huatai_HK_*.pdf``).

Free-text layout, e.g.::

    We have SOLD for you as AGENT
    500,000 shares in I/MONGOLIA YILI IN 'A'CNY1 at a gross price of CNY 27.1436
    Traded on 22 Jul 2026 ... Settlement due on 22 Jul 2026.
    Gross Consideration: CNY 13,571,800.00
    Stamp Duty:         CNY 6,785.90
    Net Consideration:  CNY 13,554,372.45
    Local Code:         600887
"""

from __future__ import annotations

import re

import pymupdf

from ..records import build_record, normalize, parse_date, to_float, to_int


def huatai_hk_pdf2tx(filename: str) -> list[dict]:
    doc = pymupdf.open(filename)
    try:
        text = normalize("\n".join(page.get_text() for page in doc))
    finally:
        doc.close()

    side = "S" if re.search(r"We have (SOLD|BOUGHT) for you as AGENT", text).group(1) == "SOLD" else "B"
    date = parse_date(re.search(r"Traded on (\d{1,2} \w{3} \d{4})", text).group(1))
    settlement_date = parse_date(re.search(r"Settlement due on (\d{1,2} \w{3} \d{4})", text).group(1))
    ticker = re.search(r"Local Code:\s*(\d+)", text).group(1)
    volume = to_int(re.search(r"([\d,]+) shares in", text).group(1))
    price = to_float(re.search(r"gross price of CNY ([\d.]+)", text).group(1))
    net = to_float(re.search(r"Net Consideration:\s*CNY\s*([\d,.]+)", text).group(1))
    tax = to_float(re.search(r"Stamp Duty:\s*CNY\s*([\d,.]+)", text).group(1))

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
