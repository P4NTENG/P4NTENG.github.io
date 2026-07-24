from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any


_HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
_HANGUL_RUN_RE = re.compile(r"[\uac00-\ud7a3]{8,}")
FULL_DOCUMENT_OCR_RATIO = 0.8


def _is_suspicious(character: str) -> bool:
    codepoint = ord(character)
    return (
        character in {"\u00a7", "\ufffd"}
        or 0x3300 <= codepoint <= 0x33FF  # CJK 호환 문자
        or 0x3400 <= codepoint <= 0x4DBF  # 이 PDF에서 오매핑된 CJK 확장 A
        or 0xE000 <= codepoint <= 0xF8FF  # 사설 영역
    )


@dataclass(frozen=True)
class TextQuality:
    character_count: int
    non_whitespace_count: int
    hangul_count: int
    suspicious_count: int
    suspicious_ratio: float
    longest_unspaced_hangul_run: int
    heading_count: int
    list_item_count: int
    table_row_count: int
    decision: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "TextQuality":
        return cls(
            character_count=int(value["character_count"]),
            non_whitespace_count=int(value["non_whitespace_count"]),
            hangul_count=int(value["hangul_count"]),
            suspicious_count=int(value["suspicious_count"]),
            suspicious_ratio=float(value["suspicious_ratio"]),
            longest_unspaced_hangul_run=int(value["longest_unspaced_hangul_run"]),
            heading_count=int(value["heading_count"]),
            list_item_count=int(value["list_item_count"]),
            table_row_count=int(value["table_row_count"]),
            decision=str(value["decision"]),
            reasons=tuple(str(reason) for reason in value["reasons"]),
        )


@dataclass(frozen=True)
class PageTextQuality:
    page: int
    quality: TextQuality

    def to_dict(self) -> dict[str, object]:
        return {"page": self.page, "quality": self.quality.to_dict()}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "PageTextQuality":
        return cls(
            page=int(value["page"]),
            quality=TextQuality.from_dict(value["quality"]),
        )


@dataclass(frozen=True)
class OcrPlan:
    mode: str
    requested_pages: tuple[int, ...]
    required_pages: tuple[int, ...]
    ocr_pages: tuple[int, ...]
    required_ratio: float
    full_document_threshold: float
    page_quality: tuple[PageTextQuality, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "requested_pages": list(self.requested_pages),
            "required_pages": list(self.required_pages),
            "ocr_pages": list(self.ocr_pages),
            "required_ratio": self.required_ratio,
            "full_document_threshold": self.full_document_threshold,
            "page_quality": [item.to_dict() for item in self.page_quality],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "OcrPlan":
        return cls(
            mode=str(value["mode"]),
            requested_pages=tuple(int(page) for page in value["requested_pages"]),
            required_pages=tuple(int(page) for page in value["required_pages"]),
            ocr_pages=tuple(int(page) for page in value["ocr_pages"]),
            required_ratio=float(value["required_ratio"]),
            full_document_threshold=float(value["full_document_threshold"]),
            page_quality=tuple(
                PageTextQuality.from_dict(item) for item in value["page_quality"]
            ),
        )


def assess_text_quality(text: str) -> TextQuality:
    non_whitespace_count = sum(not character.isspace() for character in text)
    hangul_count = len(_HANGUL_RE.findall(text))
    suspicious_count = sum(_is_suspicious(character) for character in text)
    suspicious_ratio = (
        suspicious_count / non_whitespace_count if non_whitespace_count else 0.0
    )
    hangul_runs = _HANGUL_RUN_RE.findall(text)
    longest_run = max((len(run) for run in hangul_runs), default=0)

    reasons: list[str] = []
    if non_whitespace_count < 20:
        reasons.append("추출된 문자가 너무 적음")
    if suspicious_count >= 3 or suspicious_ratio >= 0.003:
        reasons.append(
            f"의심 문자 {suspicious_count}개({suspicious_ratio:.2%}) 감지"
        )
    if hangul_count >= 30 and longest_run >= 18:
        reasons.append(f"공백 없는 한글 연속 문자열 {longest_run}자 감지")

    return TextQuality(
        character_count=len(text),
        non_whitespace_count=non_whitespace_count,
        hangul_count=hangul_count,
        suspicious_count=suspicious_count,
        suspicious_ratio=round(suspicious_ratio, 6),
        longest_unspaced_hangul_run=longest_run,
        heading_count=sum(line.lstrip().startswith("#") for line in text.splitlines()),
        list_item_count=sum(
            line.lstrip().startswith(("- ", "* ", "+ "))
            for line in text.splitlines()
        ),
        table_row_count=sum(
            line.strip().startswith("|") and line.strip().endswith("|")
            for line in text.splitlines()
        ),
        decision="ocr-required" if reasons else "native-usable",
        reasons=tuple(reasons),
    )


def build_ocr_plan(
    page_quality: tuple[PageTextQuality, ...],
    full_document_threshold: float = FULL_DOCUMENT_OCR_RATIO,
) -> OcrPlan:
    if not page_quality:
        raise ValueError("OCR 계획을 만들 페이지가 없습니다.")
    requested_pages = tuple(item.page for item in page_quality)
    required_pages = tuple(
        item.page for item in page_quality if item.quality.decision == "ocr-required"
    )
    required_ratio = len(required_pages) / len(requested_pages)
    if required_pages and required_ratio >= full_document_threshold:
        mode = "full"
        ocr_pages = requested_pages
    elif required_pages:
        mode = "selective"
        ocr_pages = required_pages
    else:
        mode = "native"
        ocr_pages = ()
    return OcrPlan(
        mode=mode,
        requested_pages=requested_pages,
        required_pages=required_pages,
        ocr_pages=ocr_pages,
        required_ratio=round(required_ratio, 6),
        full_document_threshold=full_document_threshold,
        page_quality=page_quality,
    )


def plan_pdf_ocr(
    pdf_path: Path,
    pages: tuple[int, ...],
    full_document_threshold: float = FULL_DOCUMENT_OCR_RATIO,
) -> OcrPlan:
    import pymupdf

    with pymupdf.open(pdf_path) as document:
        page_quality = tuple(
            PageTextQuality(
                page=page,
                quality=assess_text_quality(
                    document[page - 1].get_text("text", sort=True)
                ),
            )
            for page in pages
        )
    return build_ocr_plan(page_quality, full_document_threshold)
