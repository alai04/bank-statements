"""bank-statements: parse broker/bank trade confirmations into JSON records.

CLI usage::

    bank-statements path/to/confirmation.pdf [--pretty]

Library usage::

    from bank_statements import parse_file, huatai_pdf2tx
    records = parse_file("path/to/confirmation.pdf")
"""

from __future__ import annotations

import argparse
import json
import sys

from .parsers import (
    gf_pdf2tx,
    hsbc_pdf2tx,
    huatai_hk_pdf2tx,
    huatai_pdf2tx,
    iifl_pdf2tx,
    jpmorgan_eml2tx,
    jpmorgan_pdf2tx,
    maybank_pdf2tx,
    scb_pdf2tx,
)
from .registry import parse_file

__all__ = [
    "gf_pdf2tx",
    "hsbc_pdf2tx",
    "huatai_hk_pdf2tx",
    "huatai_pdf2tx",
    "iifl_pdf2tx",
    "jpmorgan_eml2tx",
    "jpmorgan_pdf2tx",
    "maybank_pdf2tx",
    "scb_pdf2tx",
    "parse_file",
]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="bank-statements",
        description="Parse a trade confirmation (PDF/EML) into JSON stock trade records.",
    )
    parser.add_argument("filename", help="path to the confirmation file")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print the JSON output",
    )
    args = parser.parse_args(argv)

    records = parse_file(args.filename)
    print(json.dumps(records, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    sys.exit(main())
