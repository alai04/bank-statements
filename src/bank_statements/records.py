"""Unified trade-record schema and shared parsing utilities.

Every broker/bank parser returns a ``list[dict]``.  The core keys (always
present, in this order) are::

    "type"       # "B" | "S"
    "date"       # trade date, "YYYY-MM-DD"
    "ticker"     # security code / identifier
    "volume"     # number of shares/units (int)
    "price"      # unit price (float)
    "net_amount" # net cash amount (2 dp)
    "trans_fee"  # transaction fees excluding tax (2 dp)
    "tax"        # stamp duty / transaction tax (2 dp)

Some brokers add optional keys:

* ``settlement_date`` ("YYYY-MM-DD") — inserted right after ``date``;
* ``sec_name`` — inserted after ``date``/``settlement_date`` (security name);
* ``broker`` — inserted before ``type`` (e.g. HSBC / HSBC HK, JPM / JPM HK).

``trans_fee`` is *derived* (see :func:`compute_trans_fee`):

* sell: ``trans_fee = price * volume - net_amount - tax``
* buy:  ``trans_fee = net_amount - price * volume - tax``

A parser may pass an explicit ``trans_fee`` when the confirmation carries an
exact gross amount (e.g. HSBC, where ``tax`` is 0 and all charges fold into
``trans_fee``).
"""

from __future__ import annotations

import re
from datetime import datetime

#: Canonical key order used when serialising a trade record.
FIELDS = ("type", "date", "ticker", "volume", "price", "net_amount", "trans_fee", "tax")


def clean(value: str) -> str:
    """Remove *all* whitespace from a string (useful for table cells)."""
    return re.sub(r"\s+", "", value or "")


def normalize(value: str) -> str:
    """Collapse runs of whitespace into single spaces and strip the ends."""
    return re.sub(r"\s+", " ", value or "").strip()


def to_float(value: str) -> float:
    """Parse a number, tolerating thousands separators and stray whitespace."""
    s = re.sub(r"[,\s]", "", str(value or ""))
    if not s or s in ("-", "--"):
        return 0.0
    return float(s)


def to_int(value: str) -> int:
    return int(round(to_float(value)))


def round2(value: float) -> float:
    """Round a monetary value to 2 decimal places, normalising ``-0.0``."""
    rounded = round(value, 2)
    return 0.0 if rounded == 0 else rounded


def compute_trans_fee(side: str, price: float, volume: int,
                      net_amount: float, tax: float) -> float:
    """Derive ``trans_fee`` from the other trade fields.

    * ``side == "S"``: ``price * volume - net_amount - tax``
    * ``side == "B"``: ``net_amount - price * volume - tax``
    """
    gross = price * volume
    fee = gross - net_amount - tax if side == "S" else net_amount - gross - tax
    return round2(fee)


#: ``strptime`` formats tried (in order) by :func:`parse_date`.
_DATE_FORMATS = (
    "%d-%b-%y",   # 25-Feb-26, 8-Apr-2026, 02-Sep-2026
    "%d-%b-%Y",   # 23-JUN-2026
    "%d %b %Y",   # 22 Jul 2026, 01 Sep 2026
    "%d %B %Y",   # 8 April 2026, 28 July 2025
    "%d-%B-%Y",
    "%m/%d/%Y",   # 8/26/2026
    "%d%b%Y",     # 28JUL2025
    "%Y.%m.%d",   # 2026.08.26
    "%Y-%m-%d",
    "%d-%m-%Y",
)


def parse_date(value: str) -> str:
    """Normalise a date string to ``YYYY-MM-DD``."""
    s = normalize(value).strip(".")
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"cannot parse date: {value!r}")


def date_from_filename(filename: str) -> str:
    """Extract a ``YYYY-MM-DD`` date embedded in a file name.

    Accepts ``2026.08.26``, ``2026.05.14`` and even the typo'd ``026.08.26``.
    """
    match = re.search(r"(\d{2,4})\.(\d{1,2})\.(\d{1,2})", filename)
    if not match:
        raise ValueError(f"no date found in filename: {filename!r}")
    year, month, day = match.groups()
    return f"{2000 + (int(year) % 100):04d}-{int(month):02d}-{int(day):02d}"


def build_record(side: str, date: str, ticker: str, volume: int, price: float,
                 net_amount: float, tax: float, *,
                 settlement_date: str | None = None,
                 broker: str | None = None,
                 sec_name: str | None = None,
                 trans_fee: float | None = None) -> dict:
    """Assemble a single trade record.

    ``trans_fee`` is derived from the other fields unless an explicit value is
    passed.  ``settlement_date``, ``sec_name`` and ``broker`` are optional
    extras some brokers provide.
    """
    net_amount = round2(net_amount)
    tax = round2(tax)
    if trans_fee is None:
        trans_fee = compute_trans_fee(side, price, volume, net_amount, tax)
    else:
        trans_fee = round2(trans_fee)

    record: dict = {}
    if broker is not None:
        record["broker"] = broker
    record["type"] = side
    record["date"] = date
    if settlement_date is not None:
        record["settlement_date"] = settlement_date
    if sec_name is not None:
        record["sec_name"] = sec_name
    record["ticker"] = str(ticker)
    record["volume"] = int(volume)
    record["price"] = float(price)
    record["net_amount"] = net_amount
    record["trans_fee"] = trans_fee
    record["tax"] = tax
    return record
