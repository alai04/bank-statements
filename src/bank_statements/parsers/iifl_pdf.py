"""Parser for IIFL Capital Services contract notes (India, NSE)
(``IIFL_*.PDF``).

The contract note has a trade row plus a fees/obligation block.  Per the
project README, ``trans_fee`` is read directly from the file
(``*Brokerage Amount``) rather than derived, and ``tax`` is the sum of
``GST Amount`` and ``STT Amount``.  ``ticker`` is converted from the ISIN via
a lookup table (falling back to ``""`` for unknown ISINs).
"""

from __future__ import annotations

import re

import pymupdf

from ..records import normalize, parse_date, round2, to_float, to_int

pymupdf.no_recommend_layout()

_ISIN = re.compile(r"\bINE[A-Z0-9]+\b")
_ISIN_TO_TICKER = {
    "INE752E01010": "POWERGRID.NS",  # Power Grid Corporation of India
}


def iifl_pdf2tx(filename: str) -> list[dict]:
    doc = pymupdf.open(filename)
    try:
        rows = _rows(doc)
    finally:
        doc.close()

    date = parse_date(_find_label(rows, "TRADE DATE"))
    settlement_date = parse_date(_find_label(rows, "Settlement Date"))
    trade = _trade(rows)

    isin = _ISIN.search(trade["security"]).group(0)
    sec_name = re.sub(r"\bINE[A-Z0-9]+\b", "", trade["security"]).strip(" -")

    return [{
        "type": "S" if trade["side"] == "Sell" else "B",
        "date": date,
        "settlement_date": settlement_date,
        "sec_name": sec_name,
        "isin": isin,
        "ticker": _ISIN_TO_TICKER.get(isin, ""),
        "volume": to_int(trade["quantity"]),
        "price": to_float(trade["gross_rate"]),
        "trans_fee": round2(to_float(trade["brokerage"])),
        "tax": round2(to_float(trade["gst"]) + to_float(trade["stt"])),
    }]


def _rows(doc: pymupdf.Document) -> list[list[str]]:
    rows: list[list[str]] = []
    for page in doc:
        for table in page.find_tables().tables:
            for row in table.extract():
                rows.append([normalize(c) for c in row])
    return rows


def _find_label(rows: list[list[str]], label: str) -> str:
    for row in rows:
        for i, cell in enumerate(row):
            if cell == label:
                for value in row[i + 1:]:
                    if value:
                        return value
    raise ValueError(f"label not found: {label}")


def _trade(rows: list[list[str]]) -> dict[str, str]:
    header = next(
        (r for r in rows if any("Security" in c and "Description" in c for c in r)),
        None,
    )
    if header is None:
        raise ValueError("IIFL trade header not found")

    def col(*keywords: str) -> int:
        for i, cell in enumerate(header):
            if all(k in cell for k in keywords):
                return i
        raise ValueError(f"column not found: {keywords}")

    idx = {
        "security": col("Security", "Description"),
        "side": col("Buy", "Sell"),
        "quantity": col("Quantity"),
        "gross_rate": col("Gross Rate"),
        "brokerage": col("Brokerage Amount"),
        "gst": col("GST"),
        "stt": col("STT"),
    }

    for row in rows:
        if any(_ISIN.search(c) for c in row):
            return {key: row[i] for key, i in idx.items()}
    raise ValueError("IIFL trade row not found")
