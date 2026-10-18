"""Stable comment identity helpers shared by imports and database matching."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date, datetime

import pandas as pd


def normalize_text(value) -> str:
    if value is None:
        return ''
    text = unicodedata.normalize('NFKC', str(value))
    if text.casefold() in {'nan', 'none', 'null'}:
        return ''
    return re.sub(r'\s+', ' ', text).strip().casefold()


def normalize_date(value) -> str:
    if value is None:
        return ''
    if isinstance(value, (datetime, date, pd.Timestamp)):
        return value.strftime('%Y-%m-%d')
    text = unicodedata.normalize('NFKC', str(value)).strip()
    if not text or text.casefold() in {'nan', 'none', 'null'}:
        return ''
    # Recognize common Chinese and delimited absolute date formats first.
    match = re.search(r'(20\d{2})\s*[年./-]\s*(\d{1,2})\s*[月./-]\s*(\d{1,2})', text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3))).isoformat()
        except ValueError:
            return text
    parsed = pd.to_datetime(text, errors='coerce')
    if pd.notna(parsed):
        return parsed.strftime('%Y-%m-%d')
    return re.sub(r'\s+', ' ', text).casefold()


def identity_parts(row) -> tuple[str, str, str, str]:
    return (
        normalize_text(row.get('spot_name')),
        normalize_text(row.get('comment')),
        normalize_text(row.get('user_name')),
        normalize_date(row.get('comment_date')),
    )


def has_stable_identity(row) -> bool:
    spot, comment, user, posted = identity_parts(row)
    return bool(spot and comment and user and posted)


def identity_key(row) -> str:
    payload = json.dumps(identity_parts(row), ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def content_key(row) -> str:
    spot, comment, _, _ = identity_parts(row)
    payload = json.dumps((spot, comment), ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()
