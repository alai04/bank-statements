"""Helpers for reading ``.eml`` files."""

from __future__ import annotations

import email
import re
from email import policy


def read_message(filename: str):
    with open(filename, "rb") as fh:
        return email.message_from_bytes(fh.read(), policy=policy.default)


def plain_text(filename: str) -> str:
    """Return the plain-text body, falling back to HTML stripped of tags."""
    msg = read_message(filename)
    body = msg.get_body(preferencelist=("plain", "html"))
    if body is None:
        return ""
    text = body.get_content()
    if body.get_content_type() == "text/html":
        text = re.sub(r"<[^>]+>", " ", text)
        text = text.replace("&nbsp;", " ").replace("\xa0", " ")
    return text


def html_body(filename: str) -> str | None:
    """Return the HTML body if present, else ``None``."""
    msg = read_message(filename)
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_content()
    return None
