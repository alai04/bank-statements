"""Broker/bank trade-confirmation parsers.

Each parser exposes an ``xxx_yyy2tx(filename) -> list[dict]`` function where
``xxx`` is the broker/bank abbreviation and ``yyy`` is the source format
(``pdf`` or ``eml``).
"""

from .gf_pdf import gf_pdf2tx
from .hsbc_pdf import hsbc_pdf2tx
from .huatai_hk_pdf import huatai_hk_pdf2tx
from .huatai_pdf import huatai_pdf2tx
from .iifl_pdf import iifl_pdf2tx
from .jpmorgan_eml import jpmorgan_eml2tx
from .jpmorgan_pdf import jpmorgan_pdf2tx
from .maybank_pdf import maybank_pdf2tx
from .scb_pdf import scb_pdf2tx

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
]
