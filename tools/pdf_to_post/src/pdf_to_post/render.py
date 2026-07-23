from __future__ import annotations

import json
import re

from pdf_to_post.extract import ExtractedDocument
from pdf_to_post.normalize import normalize_text


LIQUID_OPEN_PATTERN = re.compile(r"\{[{%]")


def escape_liquid(text: str) -> str:
    return LIQUID_OPEN_PATTERN.sub(
        lambda match: "{% raw %}" + match.group(0) + "{% endraw %}", text
    )


def render_draft(
    document: ExtractedDocument,
    *,
    title: str,
    layout: str,
    source_heading: str,
    use_math: bool,
) -> str:
    front_matter = [
        "---",
        f"layout: {json.dumps(layout, ensure_ascii=False)}",
        f"title: {json.dumps(title.strip(), ensure_ascii=False)}",
    ]
    if use_math:
        front_matter.append("use_math: true")
    front_matter.extend(["---", ""])

    body = [
        f"> 이 글은 `{document.source.name}`에서 자동 생성된 초안입니다. 원문과 대조하여 검수하세요.",
        "",
        f"## {source_heading}",
        "",
    ]

    for page in document.pages:
        text = escape_liquid(normalize_text(page.text))
        body.append(f"<!-- source-page: {page.number} -->")
        body.append("")
        body.append(text or f"> {page.number}페이지: 추출된 텍스트가 없습니다.")
        body.append("")

    return "\n".join(front_matter + body).rstrip() + "\n"
