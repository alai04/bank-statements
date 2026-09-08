"""Parser for J.P. Morgan "Unofficial Order Summary" emails (``JPM-*.eml``).

The HTML body contains a table; each data row holds one order with primary /
secondary cell values (e.g. ticker cell = "3690 HK" / "MEITUAN").  These
emails are unofficial summaries, so each record only carries ``broker, type,
date, settlement_date, sec_name, ticker, volume, price``.

``broker`` is decided by the account number: ``JPM HK`` for ``51***60``,
otherwise ``JPM``.  ``ticker`` is converted from the ``Ticker`` cell
(``3690 HK`` -> ``3690.HK``; a non-HK suffix such as ``002318 C2`` keeps just
the numeric code).
"""

from __future__ import annotations

import re
from html import unescape

from ..emailio import html_body
from ..records import parse_date, to_float, to_int

_ISIN = re.compile(r"^[A-Z]{2}[A-Z0-9]{10}$")
_NUMBER = re.compile(r"^[\d,]+(?:\.\d+)?$")


def jpmorgan_eml2tx(filename: str) -> list[dict]:
    html = html_body(filename)
    if not html:
        raise ValueError(f"no HTML body in {filename!r}")
    return _parse(html)


def _strip(html: str) -> str:
    s = re.sub(r"<[^>]+>", " ", html)
    s = unescape(s).replace("\xa0", " ").replace("\u200b", "")
    return re.sub(r"\s+", " ", s).strip()


def _cell(td_html: str) -> tuple[str, str]:
    """Split a ``<td>`` into its (primary, secondary) values."""
    parts = re.split(r"<br[^>]*>", td_html, maxsplit=1)
    primary = _strip(parts[0])
    secondary = _strip(parts[1]) if len(parts) > 1 else ""
    return primary, secondary


def _rows(html: str) -> list[list[tuple[str, str]]]:
    rows: list[list[tuple[str, str]]] = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if tds:
            rows.append([_cell(td) for td in tds])
    return rows


def _columns(header: list[tuple[str, str]]) -> dict[str, int]:
    # Drop the empty padding cells so labels align 1:1 with data-row cells.
    labels = [f"{p} {s}" for p, s in header if p or s]

    def find(*keywords: str) -> int:
        for i, text in enumerate(labels):
            if all(k in text for k in keywords):
                return i
        raise ValueError(f"column not found: {keywords}")

    return {
        "acc": find("Acc Number"),
        "side": find("Side"),
        "ticker": find("Ticker"),
        "isin": find("ISIN"),
        "qty": find("Executed Qty"),
        "price": find("Avg. Executed Price (Market)"),
        "trade_date": find("Trade Date", "Settlement Date"),
    }


def _parse(html: str) -> list[dict]:
    rows = _rows(html)
    header = next(
        (r for r in rows if any("Acc Number" in c[0] + c[1] for c in r)),
        None,
    )
    if header is None:
        raise ValueError("J.P. Morgan order table header not found")

    cols = _columns(header)
    records: list[dict] = []
    for row in rows:
        record = _data_row(row, cols)
        if record is not None:
            records.append(record)
    return records


def _data_row(row: list[tuple[str, str]], cols: dict[str, int]) -> dict | None:
    if len(row) <= cols["trade_date"]:
        return None
    isin = row[cols["isin"]][0].strip()
    price_raw = row[cols["price"]][0].strip()
    if not _ISIN.match(isin) or not _NUMBER.match(price_raw):
        return None

    acc = row[cols["acc"]][0].strip()
    ticker_raw = row[cols["ticker"]][0].strip()

    return {
        "broker": "JPM HK" if acc == "51***60" else "JPM",
        "type": "S" if "Sell" in row[cols["side"]][0] else "B",
        "date": parse_date(row[cols["trade_date"]][0]),
        "settlement_date": parse_date(row[cols["trade_date"]][1]),
        "sec_name": row[cols["ticker"]][1].strip(),
        "ticker": _ticker(ticker_raw),
        "volume": to_int(row[cols["qty"]][0]),
        "price": to_float(price_raw),
    }


def _ticker(raw: str) -> str:
    parts = raw.split()
    if not parts:
        return ""
    code = parts[0]
    return f"{code}.HK" if len(parts) > 1 and parts[1] == "HK" else code
