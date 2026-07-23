from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pdf_to_post import __version__
from pdf_to_post.config import ConfigError, find_site_root, load_config
from pdf_to_post.extract import ExtractionError
from pdf_to_post.pipeline import ConversionError, convert_pdf
from pdf_to_post.validate import validate_markdown


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf-to-post",
        description="텍스트형 PDF를 검수 가능한 Jekyll 초안으로 변환합니다.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="PDF에서 Jekyll 초안을 생성합니다.")
    convert.add_argument("pdf", type=Path, help="변환할 PDF 경로")
    convert.add_argument("--title", help="게시물 제목. 기본값은 PDF 파일명입니다.")
    convert.add_argument("--slug", help="초안 파일명에 사용할 slug")
    convert.add_argument("--use-math", action="store_true", help="MathJax를 활성화합니다.")
    convert.add_argument("--force", action="store_true", help="기존 초안을 덮어씁니다.")
    convert.add_argument("--site-root", type=Path, help="Jekyll 저장소 루트")
    convert.add_argument("--config", type=Path, help="변환 설정 YAML 경로")

    validate = subparsers.add_parser("validate", help="생성된 Markdown을 검증합니다.")
    validate.add_argument("markdown", type=Path, help="검증할 Markdown 경로")
    validate.add_argument("--site-root", type=Path, help="Jekyll 저장소 루트")
    return parser


def _site_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    return find_site_root()


def _print_validation(errors: tuple[str, ...], warnings: tuple[str, ...]) -> None:
    for warning in warnings:
        print(f"경고: {warning}", file=sys.stderr)
    for error in errors:
        print(f"오류: {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    try:
        root = _site_root(args.site_root)

        if args.command == "convert":
            config = load_config(args.config)
            result = convert_pdf(
                args.pdf,
                site_root=root,
                config=config,
                title=args.title,
                slug=args.slug,
                use_math=args.use_math,
                force=args.force,
            )
            _print_validation(
                (), result.extraction_warnings + result.validation.warnings
            )
            print(f"초안 생성 완료: {result.output_path}")
            print(f"추출 페이지: {result.page_count}")
            return 0

        result = validate_markdown(args.markdown, root)
        _print_validation(result.errors, result.warnings)
        if result.is_valid:
            print(f"검증 통과: {args.markdown.resolve()}")
            return 0
        return 1
    except (ConfigError, ConversionError, ExtractionError, ValueError) as error:
        print(f"오류: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
