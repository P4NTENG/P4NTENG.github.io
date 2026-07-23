from __future__ import annotations

import re
import unicodedata


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    lines = [re.sub(r"[ \t]+$", "", line) for line in text.splitlines()]

    normalized: list[str] = []
    previous_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and previous_blank:
            continue
        normalized.append("" if is_blank else line)
        previous_blank = is_blank

    return "\n".join(normalized).strip()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).lower().strip()
    pieces: list[str] = []
    pending_separator = False

    for character in normalized:
        if character.isalnum():
            if pending_separator and pieces:
                pieces.append("-")
            pieces.append(character)
            pending_separator = False
        else:
            pending_separator = True

    slug = "".join(pieces).strip("-")
    if not slug or slug in {".", ".."}:
        raise ValueError("안전한 slug를 만들 수 없습니다. --slug를 지정하세요.")
    return slug
