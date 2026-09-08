"""Detection and dispatch: route a file to the right ``xxx_yyy2tx`` parser."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pymupdf

from . import emailio
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

Parser = Callable[[str], list[dict]]


def _text_of(filename: str) -> str:
    """Return the searchable text of a file (used for parser detection)."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        doc = pymupdf.open(filename)
        try:
            return "\n".join(page.get_text() for page in doc)
        finally:
            doc.close()
    if suffix == ".eml":
        return emailio.plain_text(filename)
    return ""


def _detectors() -> list[tuple[str, str, Parser, Callable[[str, str], bool]]]:
    """Return ``(broker, format, parser, detector)`` entries in priority order.

    Extend this list when adding support for further brokers/banks.
    """
    return [
        # Huatai A-share statements: "OtherAT_Huatai_YYYY.MM.DD ...pdf"
        (
            "huatai", "pdf", huatai_pdf2tx,
            lambda f, t: Path(f).name.lower().startswith("otherat_huatai")
            or ("资产账号" in t and "成交均价" in t),
        ),
        # Huatai Financial Holdings (Hong Kong) confirmations.
        (
            "huatai_hk", "pdf", huatai_hk_pdf2tx,
            lambda f, t: "huatai_hk" in Path(f).name.lower()
            or "HUATAI FINANCIAL HOLDINGS" in t,
        ),
        # HSBC Global Private Banking equity advices.
        (
            "hsbc", "pdf", hsbc_pdf2tx,
            lambda f, t: "hsbc" in Path(f).name.lower()
            or "HSBC Global Private Banking" in t,
        ),
        # Maybank Securities confirmations.
        (
            "maybank", "pdf", maybank_pdf2tx,
            lambda f, t: "maybank" in Path(f).name.lower()
            or "Maybank Securities" in t,
        ),
        # GF Securities (Hong Kong) confirmations.
        (
            "gf", "pdf", gf_pdf2tx,
            lambda f, t: "gf-" in Path(f).name.lower()
            or "GF Securities" in t,
        ),
        # J.P. Morgan Private Bank confirmations.
        (
            "jpmorgan", "pdf", jpmorgan_pdf2tx,
            lambda f, t: Path(f).name.lower().startswith("jpm_")
            or ("JPMorgan" in t and "Confirmation" in t),
        ),
        # IIFL Capital Services contract notes.
        (
            "iifl", "pdf", iifl_pdf2tx,
            lambda f, t: "iifl" in Path(f).name.lower()
            or "IIFL Capital Services" in t,
        ),
        # Standard Chartered Private Bank eAdvice.
        (
            "scb", "pdf", scb_pdf2tx,
            lambda f, t: Path(f).name.lower().startswith("scb")
            or "Standard Chartered Bank (Hong Kong)" in t,
        ),
        # J.P. Morgan "Unofficial Order Summary" emails.
        (
            "jpmorgan", "eml", jpmorgan_eml2tx,
            lambda f, t: "jpm-" in Path(f).name.lower()
            or "Unofficial Order Summary" in t,
        ),
    ]


def detect_parser(filename: str) -> Parser:
    """Return the parser function suitable for ``filename``."""
    suffix = Path(filename).suffix.lower().lstrip(".")
    text = _text_of(filename)

    for _, fmt, parser, detector in _detectors():
        if fmt != suffix:
            continue
        if detector(filename, text):
            return parser

    raise ValueError(f"cannot detect a parser for {filename!r}")


def parse_file(filename: str) -> list[dict]:
    """Detect the right parser and return its trade records."""
    return detect_parser(filename)(filename)
