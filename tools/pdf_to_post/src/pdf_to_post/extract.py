from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class ExtractionError(RuntimeError):
    """Raised when text cannot be extracted from a PDF."""


@dataclass(frozen=True)
class ExtractedPage:
    number: int
    text: str


@dataclass(frozen=True)
class ExtractedDocument:
    source: Path
    pages: tuple[ExtractedPage, ...]
    warnings: tuple[str, ...]

    @property
    def page_count(self) -> int:
        return len(self.pages)


def extract_pdf_text(pdf_path: Path) -> ExtractedDocument:
    source = pdf_path.resolve()
    if not source.is_file():
        raise ExtractionError(f"PDF 파일을 찾을 수 없습니다: {source}")
    if source.suffix.lower() != ".pdf":
        raise ExtractionError(f"PDF 파일만 변환할 수 있습니다: {source}")

    try:
        import pymupdf
    except ModuleNotFoundError as error:
        raise ExtractionError(
            "PyMuPDF가 설치되어 있지 않습니다. "
            "`python -m pip install -e tools/pdf_to_post`를 먼저 실행하세요."
        ) from error

    pages: list[ExtractedPage] = []
    warnings: list[str] = []

    try:
        with pymupdf.open(source) as document:
            if document.page_count == 0:
                raise ExtractionError("페이지가 없는 PDF입니다.")

            for index, page in enumerate(document, start=1):
                text = page.get_text("text", sort=True)
                if not text.strip():
                    warnings.append(
                        f"{index}페이지에서 텍스트를 찾지 못했습니다. OCR 검토가 필요합니다."
                    )
                pages.append(ExtractedPage(number=index, text=text))
    except ExtractionError:
        raise
    except Exception as error:
        raise ExtractionError(f"PDF를 읽지 못했습니다: {source}: {error}") from error

    return ExtractedDocument(
        source=source,
        pages=tuple(pages),
        warnings=tuple(warnings),
    )
