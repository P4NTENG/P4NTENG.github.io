from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pdf_to_post.config import AppConfig
from pdf_to_post.extract import extract_pdf_text
from pdf_to_post.normalize import slugify
from pdf_to_post.render import render_draft
from pdf_to_post.validate import ValidationResult, validate_markdown


class ConversionError(RuntimeError):
    """Raised when a draft cannot be safely generated."""


@dataclass(frozen=True)
class ConversionResult:
    output_path: Path
    page_count: int
    extraction_warnings: tuple[str, ...]
    validation: ValidationResult


def convert_pdf(
    pdf_path: Path,
    *,
    site_root: Path,
    config: AppConfig,
    title: str | None = None,
    slug: str | None = None,
    use_math: bool = False,
    force: bool = False,
) -> ConversionResult:
    root = site_root.resolve()
    if not (root / "_config.yml").is_file():
        raise ConversionError(f"Jekyll 저장소가 아닙니다: {root}")

    document = extract_pdf_text(pdf_path)
    post_title = (title or document.source.stem).strip()
    if not post_title:
        raise ConversionError("게시물 제목이 비어 있습니다.")

    post_slug = slugify(slug or document.source.stem)
    drafts_dir = (root / config.drafts_dir).resolve()
    try:
        drafts_dir.relative_to(root)
    except ValueError as error:
        raise ConversionError("초안 디렉터리가 저장소 밖을 가리킵니다.") from error

    output_path = drafts_dir / f"{post_slug}.md"
    if output_path.exists() and not force:
        raise ConversionError(
            f"초안이 이미 존재합니다: {output_path}. 덮어쓰려면 --force를 사용하세요."
        )

    content = render_draft(
        document,
        title=post_title,
        layout=config.layout,
        source_heading=config.source_heading,
        use_math=use_math,
    )
    drafts_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8", newline="\n")

    validation = validate_markdown(output_path, root)
    if not validation.is_valid:
        output_path.unlink(missing_ok=True)
        detail = "; ".join(validation.errors)
        raise ConversionError(f"생성된 초안이 검증에 실패했습니다: {detail}")

    return ConversionResult(
        output_path=output_path,
        page_count=document.page_count,
        extraction_warnings=document.warnings,
        validation=validation,
    )
