"""Parser for J.P. Morgan Private Bank trade confirmations (``JPM_*.pdf``).

Layout is a ``label`` / ``value`` block::

    PURCHASE SPOT - SHARES
    Trade date / time (CET)   01 Sep 2026 08:51:00
    Security Name             ZHEJIANG JIULI HI-TECH METALS CO LT
    ISIN number               CNE100000HX2
    Price                     20.6448 CNH
    Quantity                  235,600
    ...
    Stamp duty                15,719.00   (HK trades only)
    Net amount                4,871,619.81 CNH

``broker`` is decided by the client name (same rule as HSBC): ``JPM HK`` when
it contains ``(HK)``, otherwise ``JPM``.  ``ticker`` is converted from the
ISIN via a lookup table (falling back to ``""`` for unknown ISINs, as allowed
by the project README).
"""

from __future__ import annotations

import re

import pymupdf

from ..records import build_record, normalize, parse_date, to_float, to_int

# ISIN -> "code.exchange" lookup.  Extend as new securities appear.
_ISIN_TO_TICKER = {
    "CNE100000HX2": "002318.SZ",   # Zhejiang Jiuli Hi-Tech Metals
    "KYG596691041": "3690.HK",     # Meituan
}


def jpmorgan_pdf2tx(filename: str) -> list[dict]:
    doc = pymupdf.open(filename)
    try:
        text = normalize("\n".join(page.get_text() for page in doc))
    finally:
        doc.close()

    client = re.search(r"IKARIA GROUP(?: \(HK\))? LIMITED", text).group(0)
    broker = "JPM HK" if "(HK)" in client else "JPM"

    side = "B" if re.search(r"\b(PURCHASE|SALE|SELL)\s+SPOT", text).group(1) == "PURCHASE" else "S"
    date = parse_date(re.search(r"Trade date / time \(CET\)\s*(\d{1,2} \w{3} \d{4})", text).group(1))
    sec_name = re.search(r"Security Name\s+(.*?)\s+ISIN number", text).group(1)
    isin = re.search(r"ISIN number\s*(\S+)", text).group(1)
    ticker = _ISIN_TO_TICKER.get(isin, "")
    volume = to_int(re.search(r"Quantity\s*([\d,]+)", text).group(1))
    price = to_float(re.search(r"Price\s*([\d.]+)\s*[A-Z]{3}", text).group(1))
    net = to_float(re.search(r"Net amount\s*([\d,.]+)", text).group(1))
    tax = _optional(re.search(r"Stamp duty\s*([\d,.]+)", text))

    return [build_record(
        side=side,
        date=date,
        ticker=ticker,
        volume=volume,
        price=price,
        net_amount=net,
        tax=tax,
        broker=broker,
        sec_name=sec_name,
    )]


def _optional(match: re.Match | None) -> float:
    return to_float(match.group(1)) if match else 0.0
