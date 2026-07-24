from __future__ import annotations

from dataclasses import dataclass, replace
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
from typing import Any

from pdf_to_post.quality import OcrPlan


SCHEMA_VERSION = 1
IGNORED_BLOCK_TYPES = {"page_header", "page_footer"}
HEADING_BLOCK_TYPES = {"title", "section_header"}


class HybridError(RuntimeError):
    """Raised when hybrid intermediate data cannot be extracted or merged."""


@dataclass(frozen=True)
class BBox:
    left: float
    top: float
    right: float
    bottom: float

    def __post_init__(self) -> None:
        if self.right < self.left or self.bottom < self.top:
            raise ValueError(f"잘못된 좌표입니다: {self}")

    @property
    def area(self) -> float:
        return max(0.0, self.right - self.left) * max(0.0, self.bottom - self.top)

    @property
    def center(self) -> tuple[float, float]:
        return ((self.left + self.right) / 2, (self.top + self.bottom) / 2)

    @property
    def height(self) -> float:
        return self.bottom - self.top

    def intersection_area(self, other: "BBox") -> float:
        width = max(0.0, min(self.right, other.right) - max(self.left, other.left))
        height = max(0.0, min(self.bottom, other.bottom) - max(self.top, other.top))
        return width * height

    def contains_center(self, other: "BBox") -> bool:
        x, y = other.center
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def span_overlap(self, span: "BBox") -> float:
        return self.intersection_area(span) / span.area if span.area else 0.0

    def vertical_overlap(self, other: "BBox") -> float:
        overlap = max(0.0, min(self.bottom, other.bottom) - max(self.top, other.top))
        return overlap / other.height if other.height else 0.0

    def to_list(self) -> list[float]:
        return [self.left, self.top, self.right, self.bottom]

    def union(self, other: "BBox") -> "BBox":
        return BBox(
            min(self.left, other.left),
            min(self.top, other.top),
            max(self.right, other.right),
            max(self.bottom, other.bottom),
        )

    @classmethod
    def from_value(cls, value: list[float] | tuple[float, ...]) -> "BBox":
        if len(value) != 4:
            raise ValueError(f"좌표는 네 값이어야 합니다: {value}")
        return cls(*(float(item) for item in value))


@dataclass(frozen=True)
class OcrSpan:
    bbox: BBox
    text: str
    confidence: float

    def to_dict(self) -> dict[str, object]:
        return {
            "bbox": self.bbox.to_list(),
            "text": self.text,
            "confidence": round(self.confidence, 6),
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "OcrSpan":
        return cls(
            bbox=BBox.from_value(value["bbox"]),
            text=str(value["text"]),
            confidence=float(value["confidence"]),
        )


@dataclass(frozen=True)
class TableCell:
    bbox: BBox | None
    row: int
    column: int
    row_span: int
    column_span: int
    text: str
    is_header: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "bbox": self.bbox.to_list() if self.bbox else None,
            "row": self.row,
            "column": self.column,
            "row_span": self.row_span,
            "column_span": self.column_span,
            "text": self.text,
            "is_header": self.is_header,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "TableCell":
        bbox = value.get("bbox")
        return cls(
            bbox=BBox.from_value(bbox) if bbox else None,
            row=int(value["row"]),
            column=int(value["column"]),
            row_span=int(value.get("row_span", 1)),
            column_span=int(value.get("column_span", 1)),
            text=str(value.get("text", "")),
            is_header=bool(value.get("is_header", False)),
        )


@dataclass(frozen=True)
class StructureBlock:
    block_type: str
    bbox: BBox
    order: int
    text: str = ""
    cells: tuple[TableCell, ...] = ()
    rows: int = 0
    columns: int = 0
    enumerated: bool = False
    marker: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.block_type,
            "bbox": self.bbox.to_list(),
            "order": self.order,
            "text": self.text,
            "rows": self.rows,
            "columns": self.columns,
            "enumerated": self.enumerated,
            "marker": self.marker,
            "cells": [cell.to_dict() for cell in self.cells],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "StructureBlock":
        return cls(
            block_type=str(value["type"]),
            bbox=BBox.from_value(value["bbox"]),
            order=int(value["order"]),
            text=str(value.get("text", "")),
            rows=int(value.get("rows", 0)),
            columns=int(value.get("columns", 0)),
            enumerated=bool(value.get("enumerated", False)),
            marker=str(value.get("marker", "")),
            cells=tuple(TableCell.from_dict(cell) for cell in value.get("cells", [])),
        )


@dataclass(frozen=True)
class PageIR:
    number: int
    width: float
    height: float
    spans: tuple[OcrSpan, ...] = ()
    blocks: tuple[StructureBlock, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "number": self.number,
            "width": self.width,
            "height": self.height,
            "spans": [span.to_dict() for span in self.spans],
            "blocks": [block.to_dict() for block in self.blocks],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "PageIR":
        return cls(
            number=int(value["number"]),
            width=float(value["width"]),
            height=float(value["height"]),
            spans=tuple(OcrSpan.from_dict(span) for span in value.get("spans", [])),
            blocks=tuple(
                StructureBlock.from_dict(block) for block in value.get("blocks", [])
            ),
        )


@dataclass(frozen=True)
class EngineIR:
    engine: str
    source: str
    pages: tuple[PageIR, ...]
    schema_version: int = SCHEMA_VERSION
    ocr_plan: OcrPlan | None = None

    def to_dict(self) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": self.schema_version,
            "engine": self.engine,
            "source": self.source,
            "pages": [page.to_dict() for page in self.pages],
        }
        if self.ocr_plan is not None:
            value["ocr_plan"] = self.ocr_plan.to_dict()
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "EngineIR":
        schema_version = int(value.get("schema_version", 0))
        if schema_version != SCHEMA_VERSION:
            raise HybridError(
                f"지원하지 않는 중간 형식 버전입니다: {schema_version}"
            )
        return cls(
            engine=str(value["engine"]),
            source=str(value["source"]),
            pages=tuple(PageIR.from_dict(page) for page in value["pages"]),
            schema_version=schema_version,
            ocr_plan=(
                OcrPlan.from_dict(value["ocr_plan"])
                if value.get("ocr_plan") is not None
                else None
            ),
        )


@dataclass(frozen=True)
class MergedBlock:
    block_type: str
    bbox: BBox
    order: float
    text: str
    confidence: float | None
    text_source: str
    warnings: tuple[str, ...] = ()
    table: tuple[tuple[str, ...], ...] = ()
    marker: str = ""


@dataclass(frozen=True)
class MergedPage:
    number: int
    blocks: tuple[MergedBlock, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class HybridResult:
    source: str
    pages: tuple[MergedPage, ...]

    @property
    def warnings(self) -> tuple[str, ...]:
        return tuple(
            warning
            for page in self.pages
            for warning in (*page.warnings, *(w for block in page.blocks for w in block.warnings))
        )


def save_engine_ir(document: EngineIR, path: Path, force: bool = False) -> Path:
    target = path.resolve()
    if target.exists() and not force:
        raise HybridError(f"중간 결과가 이미 있습니다. --force를 사용하세요: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(document.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return target


def load_engine_ir(path: Path) -> EngineIR:
    source = path.resolve()
    if not source.is_file():
        raise HybridError(f"중간 결과를 찾을 수 없습니다: {source}")
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise HybridError(f"중간 결과 JSON을 읽지 못했습니다: {source}: {error}") from error
    return EngineIR.from_dict(value)


def _normalize_for_compare(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", text).lower()


def _disagreement(left: str, right: str) -> float:
    normalized_left = _normalize_for_compare(left)
    normalized_right = _normalize_for_compare(right)
    if not normalized_left and not normalized_right:
        return 0.0
    return 1.0 - SequenceMatcher(None, normalized_left, normalized_right).ratio()


def _token_disagreement(left: str, right: str) -> float:
    pattern = re.compile(r"[A-Za-z]+|[가-힣]+|\d+")
    left_tokens = pattern.findall(left)
    right_tokens = pattern.findall(right)
    if len(left_tokens) != len(right_tokens) or not left_tokens:
        return _disagreement(left, right)
    return max(
        _disagreement(left_token, right_token)
        for left_token, right_token in zip(left_tokens, right_tokens)
    )


def _sort_spans_into_lines(spans: list[OcrSpan]) -> list[list[OcrSpan]]:
    if not spans:
        return []
    ordered = sorted(spans, key=lambda span: (span.bbox.top, span.bbox.left))
    lines: list[list[OcrSpan]] = []
    for span in ordered:
        center_y = span.bbox.center[1]
        best_line: list[OcrSpan] | None = None
        best_distance = float("inf")
        for line in lines:
            line_center = sum(item.bbox.center[1] for item in line) / len(line)
            tolerance = max(
                span.bbox.height,
                sum(item.bbox.height for item in line) / len(line),
            ) * 0.65
            distance = abs(center_y - line_center)
            if distance <= tolerance and distance < best_distance:
                best_line = line
                best_distance = distance
        if best_line is None:
            lines.append([span])
        else:
            best_line.append(span)
    lines.sort(key=lambda line: min(span.bbox.top for span in line))
    for line in lines:
        line.sort(key=lambda span: span.bbox.left)
    return lines


def _join_spans(spans: list[OcrSpan], block_type: str) -> str:
    lines = _sort_spans_into_lines(spans)
    rendered_lines = [" ".join(span.text.strip() for span in line if span.text.strip()) for line in lines]
    separator = "\n" if block_type in {"code", "list_item"} else "\n"
    return separator.join(line for line in rendered_lines if line).strip()


def _mean_confidence(spans: list[OcrSpan]) -> float | None:
    if not spans:
        return None
    return sum(span.confidence for span in spans) / len(spans)


def _spans_for_bbox(
    spans: tuple[OcrSpan, ...],
    bbox: BBox,
    claimed: set[int],
    *,
    allow_long_line: bool = False,
) -> list[tuple[int, OcrSpan]]:
    matches: list[tuple[int, OcrSpan]] = []
    for index, span in enumerate(spans):
        if index in claimed:
            continue
        is_long_anchored_line = (
            allow_long_line
            and bbox.vertical_overlap(span.bbox) >= 0.5
            and abs(bbox.left - span.bbox.left) <= 0.05
        )
        if (
            bbox.contains_center(span.bbox)
            or bbox.span_overlap(span.bbox) >= 0.5
            or is_long_anchored_line
        ):
            matches.append((index, span))
    return matches


def _merge_table(
    block: StructureBlock,
    spans: tuple[OcrSpan, ...],
    claimed: set[int],
) -> tuple[tuple[tuple[str, ...], ...], list[OcrSpan], tuple[str, ...]]:
    rows = max(block.rows, max((cell.row + cell.row_span for cell in block.cells), default=0))
    columns = max(
        block.columns,
        max((cell.column + cell.column_span for cell in block.cells), default=0),
    )
    if rows == 0 or columns == 0:
        return (), [], ("표의 행·열 정보를 복원하지 못함",)

    grid = [["" for _ in range(columns)] for _ in range(rows)]
    used: list[OcrSpan] = []
    warnings: list[str] = []
    for cell in block.cells:
        matches = _spans_for_bbox(spans, cell.bbox, claimed) if cell.bbox else []
        cell_spans = [span for _, span in matches]
        text = _join_spans(cell_spans, "table") or cell.text.strip()
        if not cell_spans and cell.text.strip():
            warnings.append(f"표 {cell.row + 1}행 {cell.column + 1}열은 Docling 텍스트 사용")
        confidence = _mean_confidence(cell_spans)
        if confidence is not None and confidence < 0.8:
            warnings.append(
                f"표 {cell.row + 1}행 {cell.column + 1}열의 낮은 OCR 신뢰도: {confidence:.2f}"
            )
        if (
            cell_spans
            and cell.text.strip()
            and _token_disagreement(text, cell.text) >= 0.15
        ):
            warnings.append(
                f"표 {cell.row + 1}행 {cell.column + 1}열의 PaddleOCR·Docling 불일치"
            )
        if cell.row < rows and cell.column < columns:
            grid[cell.row][cell.column] = text
        for index, span in matches:
            claimed.add(index)
            used.append(span)
    return tuple(tuple(row) for row in grid), used, tuple(warnings)


def merge_page(paddle_page: PageIR, docling_page: PageIR) -> MergedPage:
    if paddle_page.number != docling_page.number:
        raise HybridError(
            f"페이지 번호가 일치하지 않습니다: {paddle_page.number}, {docling_page.number}"
        )
    claimed: set[int] = set()
    merged: list[MergedBlock] = []

    for ignored in (
        block for block in docling_page.blocks if block.block_type in IGNORED_BLOCK_TYPES
    ):
        for index, _ in _spans_for_bbox(
            paddle_page.spans, ignored.bbox, claimed, allow_long_line=True
        ):
            claimed.add(index)

    for block in sorted(docling_page.blocks, key=lambda item: item.order):
        if block.block_type in IGNORED_BLOCK_TYPES:
            continue
        if block.block_type == "table":
            table, used_spans, table_warnings = _merge_table(
                block, paddle_page.spans, claimed
            )
            merged.append(
                MergedBlock(
                    block_type="table",
                    bbox=block.bbox,
                    order=float(block.order),
                    text="",
                    confidence=_mean_confidence(used_spans),
                    text_source="paddle" if used_spans else "docling",
                    warnings=table_warnings,
                    table=table,
                )
            )
            continue

        if block.block_type in {"picture", "chart"}:
            matches = _spans_for_bbox(paddle_page.spans, block.bbox, claimed)
            picture_spans = [span for _, span in matches]
            for index, _ in matches:
                claimed.add(index)
            merged.append(
                MergedBlock(
                    block_type=block.block_type,
                    bbox=block.bbox,
                    order=float(block.order),
                    text="",
                    confidence=_mean_confidence(picture_spans),
                    text_source="image",
                )
            )
            continue

        matches = _spans_for_bbox(
            paddle_page.spans,
            block.bbox,
            claimed,
            allow_long_line=block.block_type not in {"picture", "chart"},
        )
        block_spans = [span for _, span in matches]
        paddle_text = _join_spans(block_spans, block.block_type)
        docling_text = block.text.strip()
        warnings: list[str] = []
        if paddle_text:
            text = paddle_text
            text_source = "paddle"
            for index, _ in matches:
                claimed.add(index)
            confidence = _mean_confidence(block_spans)
            if confidence is not None and confidence < 0.8:
                warnings.append(f"낮은 PaddleOCR 평균 신뢰도: {confidence:.2f}")
            if docling_text and _disagreement(paddle_text, docling_text) >= 0.35:
                warnings.append("PaddleOCR와 Docling 텍스트 불일치")
        else:
            text = docling_text
            text_source = "docling"
            confidence = None
            if docling_text:
                warnings.append("대응하는 PaddleOCR 텍스트가 없어 Docling 텍스트 사용")

        marker = ""
        if block.block_type == "list_item":
            leading_number = re.match(r"^\s*(\d+)(?=[가-힣A-Za-z])", text)
            if block.enumerated or leading_number:
                marker = f"{leading_number.group(1) if leading_number else '1'}."
                text = re.sub(
                    r"^\s*(?:[①②③④⑤⑥⑦⑧⑨⑩]|\d+[.)]?)\s*", "", text
                )

        merged.append(
            MergedBlock(
                block_type=block.block_type,
                bbox=block.bbox,
                order=float(block.order),
                text=text,
                confidence=confidence,
                text_source=text_source,
                warnings=tuple(warnings),
                marker=marker,
            )
        )

    unmatched = [
        (index, span)
        for index, span in enumerate(paddle_page.spans)
        if index not in claimed
        and span.bbox.bottom < 0.92
        and not (span.bbox.top < 0.08 and span.bbox.left > 0.7)
    ]
    for offset, (_, span) in enumerate(
        sorted(unmatched, key=lambda item: (item[1].bbox.top, item[1].bbox.left))
    ):
        merged.append(
            MergedBlock(
                block_type="text",
                bbox=span.bbox,
                order=10_000.0 + offset,
                text=span.text.strip(),
                confidence=span.confidence,
                text_source="paddle",
                warnings=("Docling 구조에 대응하지 않는 PaddleOCR 텍스트",),
            )
        )

    ordered = sorted(
        merged,
        key=lambda block: (block.bbox.top, block.bbox.left, block.order),
    )
    repaired: list[MergedBlock] = []
    for index, block in enumerate(ordered):
        is_unmatched = "Docling 구조에 대응하지 않는 PaddleOCR 텍스트" in block.warnings
        next_block = ordered[index + 1] if index + 1 < len(ordered) else None
        if (
            is_unmatched
            and block.block_type == "text"
            and repaired
            and repaired[-1].block_type == "list_item"
            and next_block is not None
            and next_block.block_type == "list_item"
        ):
            looks_like_new_item = bool(
                re.match(r"^[A-Za-z][A-Za-z0-9 /_-]{1,40}:", block.text)
            )
            if looks_like_new_item:
                repaired.append(
                    replace(
                        block,
                        block_type="list_item",
                        warnings=("Docling이 누락한 목록 항목으로 추정",),
                    )
                )
            else:
                previous = repaired[-1]
                repaired[-1] = replace(
                    previous,
                    bbox=previous.bbox.union(block.bbox),
                    text=f"{previous.text} {block.text}".strip(),
                    warnings=(*previous.warnings, "다음 OCR 행을 목록 항목에 병합"),
                )
            continue
        if (
            block.block_type == "code"
            and repaired
            and repaired[-1].block_type == "code"
            and block.bbox.top <= repaired[-1].bbox.bottom + 0.02
        ):
            previous = repaired[-1]
            repaired[-1] = replace(
                previous,
                bbox=previous.bbox.union(block.bbox),
                text=f"{previous.text}\n{block.text}".strip(),
                confidence=(
                    min(previous.confidence, block.confidence)
                    if previous.confidence is not None and block.confidence is not None
                    else previous.confidence or block.confidence
                ),
                warnings=(*previous.warnings, *block.warnings),
            )
            continue
        repaired.append(block)

    return MergedPage(number=paddle_page.number, blocks=tuple(repaired))


def _docling_native_table(
    block: StructureBlock,
) -> tuple[tuple[tuple[str, ...], ...], tuple[str, ...]]:
    rows = max(
        block.rows,
        max((cell.row + cell.row_span for cell in block.cells), default=0),
    )
    columns = max(
        block.columns,
        max((cell.column + cell.column_span for cell in block.cells), default=0),
    )
    if rows == 0 or columns == 0:
        return (), ("표의 행·열 정보를 복원하지 못함",)
    grid = [["" for _ in range(columns)] for _ in range(rows)]
    for cell in block.cells:
        if cell.row < rows and cell.column < columns:
            grid[cell.row][cell.column] = cell.text.strip()
    return tuple(tuple(row) for row in grid), ()


def merge_docling_native_page(docling_page: PageIR) -> MergedPage:
    merged: list[MergedBlock] = []
    for block in sorted(docling_page.blocks, key=lambda item: item.order):
        if block.block_type in IGNORED_BLOCK_TYPES:
            continue
        if block.block_type == "table":
            table, warnings = _docling_native_table(block)
            merged.append(
                MergedBlock(
                    block_type="table",
                    bbox=block.bbox,
                    order=float(block.order),
                    text="",
                    confidence=None,
                    text_source="docling-native",
                    warnings=warnings,
                    table=table,
                )
            )
            continue
        if block.block_type in {"picture", "chart"}:
            merged.append(
                MergedBlock(
                    block_type=block.block_type,
                    bbox=block.bbox,
                    order=float(block.order),
                    text="",
                    confidence=None,
                    text_source="image",
                )
            )
            continue

        text = block.text.strip()
        marker = block.marker
        if block.block_type == "list_item" and block.enumerated and not marker:
            marker = "1."
        merged.append(
            MergedBlock(
                block_type=block.block_type,
                bbox=block.bbox,
                order=float(block.order),
                text=text,
                confidence=None,
                text_source="docling-native",
                marker=marker,
            )
        )
    return MergedPage(number=docling_page.number, blocks=tuple(merged))


def merge_documents(paddle: EngineIR, docling: EngineIR) -> HybridResult:
    if paddle.engine != "paddle" or docling.engine != "docling":
        raise HybridError("Paddle 중간 결과와 Docling 중간 결과가 필요합니다.")
    if paddle.source != docling.source:
        raise HybridError(
            f"서로 다른 PDF 결과는 병합할 수 없습니다: {paddle.source}, {docling.source}"
        )
    paddle_pages = {page.number: page for page in paddle.pages}
    docling_pages = {page.number: page for page in docling.pages}
    if paddle_pages.keys() != docling_pages.keys():
        raise HybridError(
            "두 중간 결과의 페이지가 일치하지 않습니다: "
            f"Paddle={sorted(paddle_pages)}, Docling={sorted(docling_pages)}"
        )
    ocr_pages = (
        set(paddle.ocr_plan.ocr_pages)
        if paddle.ocr_plan is not None
        else set(paddle_pages)
    )
    return HybridResult(
        source=paddle.source,
        pages=tuple(
            (
                merge_page(paddle_pages[number], docling_pages[number])
                if number in ocr_pages
                else merge_docling_native_page(docling_pages[number])
            )
            for number in sorted(paddle_pages)
        ),
    )


def _escape_table_cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def _render_table(table: tuple[tuple[str, ...], ...]) -> str:
    if not table:
        return "<!-- 표 구조 복원 실패 -->"
    width = max(len(row) for row in table)
    normalized = [tuple((*row, *("" for _ in range(width - len(row))))) for row in table]
    lines = ["| " + " | ".join(_escape_table_cell(cell) for cell in normalized[0]) + " |"]
    lines.append("| " + " | ".join("---" for _ in range(width)) + " |")
    lines.extend(
        "| " + " | ".join(_escape_table_cell(cell) for cell in row) + " |"
        for row in normalized[1:]
    )
    return "\n".join(lines)


def render_hybrid_markdown(result: HybridResult) -> str:
    parts: list[str] = [
        "<!-- hybrid-source: PaddleOCR text + Docling structure -->",
        "<!-- 자동 병합 결과이며 경고 영역은 원본 PDF 대조가 필요합니다. -->",
    ]
    for page in result.pages:
        parts.extend(["", f"<!-- source-page: {page.number} -->"])
        for block in page.blocks:
            if block.warnings:
                parts.append(
                    "<!-- review: " + "; ".join(block.warnings).replace("--", "—") + " -->"
                )
            if block.block_type in HEADING_BLOCK_TYPES and block.text:
                parts.extend(["", f"## {block.text.replace(chr(10), ' ')}"])
            elif block.block_type == "list_item" and block.text:
                lines = block.text.splitlines()
                prefix = block.marker or "-"
                parts.extend(["", *[f"{prefix} {line}" for line in lines if line.strip()]])
            elif block.block_type == "code" and block.text:
                parts.extend(["", "```text", block.text, "```"])
            elif block.block_type == "table":
                parts.extend(["", _render_table(block.table)])
            elif block.block_type in {"picture", "chart"}:
                coordinates = ",".join(f"{value:.4f}" for value in block.bbox.to_list())
                parts.extend(
                    ["", f"<!-- image: page={page.number} bbox={coordinates} -->"]
                )
            elif block.text:
                parts.extend(["", block.text])
    return "\n".join(parts).strip() + "\n"


def hybrid_report(result: HybridResult) -> dict[str, object]:
    return {
        "source": result.source,
        "page_count": len(result.pages),
        "warning_count": len(result.warnings),
        "pages": [
            {
                "number": page.number,
                "block_count": len(page.blocks),
                "warning_count": sum(len(block.warnings) for block in page.blocks),
                "blocks": [
                    {
                        "type": block.block_type,
                        "bbox": block.bbox.to_list(),
                        "text_source": block.text_source,
                        "confidence": (
                            round(block.confidence, 6)
                            if block.confidence is not None
                            else None
                        ),
                        "warnings": list(block.warnings),
                        "marker": block.marker,
                    }
                    for block in page.blocks
                ],
            }
            for page in result.pages
        ],
    }
