"""Parser for Huatai A-share statements (``OtherAT_Huatai_*.pdf``).

These statements are a single wide table whose columns include
``证券代码``, ``业务标志``, ``发生金额``, ``发生数量``, ``成交均价`` and
``印花税``.  The trade date is not present in the table itself and is taken
from the file name (e.g. ``OtherAT_Huatai_2026.08.26 ...pdf``).
"""

from __future__ import annotations

import pymupdf

from ..records import clean, build_record, date_from_filename, to_float, to_int

# ``find_tables()`` prints an installation suggestion to stdout; silence it so
# the CLI's JSON output stays clean.
pymupdf.no_recommend_layout()


def huatai_pdf2tx(filename: str) -> list[dict]:
    doc = pymupdf.open(filename)
    try:
        table = _find_table(doc)
        rows = table.extract()
        header = [clean(c) for c in rows[0]]
        col = {name: i for i, name in enumerate(header)}

        date = date_from_filename(filename)
        records: list[dict] = []
        for row in rows[1:]:
            cells = [clean(c) for c in row]
            if not any(cells):
                continue

            side_raw = cells[col["业务标志"]]
            side = "S" if "卖" in side_raw else "B"

            records.append(build_record(
                side=side,
                date=date,
                ticker=cells[col["证券代码"]],
                volume=abs(to_int(cells[col["发生数量"]])),
                price=to_float(cells[col["成交均价"]]),
                net_amount=abs(to_float(cells[col["发生金额"]])),
                tax=to_float(cells[col["印花税"]]),
            ))
        return records
    finally:
        doc.close()


def _find_table(doc: pymupdf.Document):
    """Return the table whose header row contains ``证券代码``."""
    for page in doc:
        for table in page.find_tables().tables:
            if table.row_count < 2:
                continue
            header = [clean(c) for c in table.extract()[0]]
            if "证券代码" in header:
                return table
    raise ValueError("no Huatai trade table found")
