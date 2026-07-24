from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pdf_to_post import __version__
from pdf_to_post.benchmark import (
    DEFAULT_PAGES,
    BenchmarkError,
    parse_pages,
    run_benchmark,
)
from pdf_to_post.config import ConfigError, find_site_root, load_config
from pdf_to_post.extract import ExtractionError
from pdf_to_post.hybrid import (
    HybridError,
    hybrid_report,
    load_engine_ir,
    merge_documents,
    render_hybrid_markdown,
    save_engine_ir,
)
from pdf_to_post.hybrid_extract import extract_engine_ir
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

    benchmark = subparsers.add_parser(
        "benchmark", help="대표 페이지에서 PDF 추출 엔진을 비교합니다."
    )
    benchmark.add_argument("pdf", type=Path, help="실험할 PDF 경로")
    benchmark.add_argument(
        "--engine", choices=("native", "paddle", "docling"), required=True
    )
    benchmark.add_argument(
        "--pages",
        type=parse_pages,
        default=DEFAULT_PAGES,
        help="쉼표로 구분한 1부터 시작하는 페이지 번호",
    )
    benchmark.add_argument("--dpi", type=int, default=200, help="OCR 렌더링 DPI")
    benchmark.add_argument(
        "--output", type=Path, default=Path(".work/pdf-to-post/benchmark")
    )
    benchmark.add_argument("--force", action="store_true", help="기존 결과 덮어쓰기")
    benchmark.add_argument("--site-root", type=Path, help="Jekyll 저장소 루트")

    hybrid_extract = subparsers.add_parser(
        "hybrid-extract", help="Paddle 또는 Docling 좌표 기반 중간 결과를 생성합니다."
    )
    hybrid_extract.add_argument("pdf", type=Path, help="추출할 PDF 경로")
    hybrid_extract.add_argument(
        "--engine", choices=("paddle", "docling"), required=True
    )
    hybrid_extract.add_argument(
        "--pages",
        type=parse_pages,
        default=(4, 19, 24),
        help="쉼표로 구분한 1부터 시작하는 페이지 번호",
    )
    hybrid_extract.add_argument("--dpi", type=int, default=200)
    hybrid_extract.add_argument("--output", type=Path)
    hybrid_extract.add_argument("--force", action="store_true")
    hybrid_extract.add_argument("--site-root", type=Path, help="Jekyll 저장소 루트")

    hybrid_merge = subparsers.add_parser(
        "hybrid-merge", help="Paddle 텍스트와 Docling 구조를 Markdown으로 병합합니다."
    )
    hybrid_merge.add_argument("paddle", type=Path, help="Paddle 중간 결과 JSON")
    hybrid_merge.add_argument("docling", type=Path, help="Docling 중간 결과 JSON")
    hybrid_merge.add_argument(
        "--output",
        type=Path,
        default=Path(".work/pdf-to-post/hybrid/hybrid.md"),
    )
    hybrid_merge.add_argument("--force", action="store_true")
    hybrid_merge.add_argument("--site-root", type=Path, help="Jekyll 저장소 루트")
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


def _safe_repository_path(path: Path, root: Path) -> Path:
    resolved = (root / path).resolve() if not path.is_absolute() else path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise HybridError(f"출력 경로는 저장소 안에 있어야 합니다: {resolved}")
    return resolved


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

        if args.command == "benchmark":
            summary, comparison = run_benchmark(
                args.pdf,
                site_root=root,
                output=args.output,
                engine=args.engine,
                pages=args.pages,
                dpi=args.dpi,
                force=args.force,
            )
            print(f"{args.engine} 벤치마크 완료: {summary}")
            print(f"비교 보고서: {comparison}")
            return 0

        if args.command == "hybrid-extract":
            output = args.output or Path(
                f".work/pdf-to-post/hybrid/{args.engine}.json"
            )
            output_path = _safe_repository_path(output, root)
            if output_path.exists() and not args.force:
                raise HybridError(
                    f"중간 결과가 이미 있습니다. --force를 사용하세요: {output_path}"
                )
            document = extract_engine_ir(
                args.pdf,
                engine=args.engine,
                pages=args.pages,
                work_dir=root / ".work" / "pdf-to-post",
                dpi=args.dpi,
            )
            save_engine_ir(document, output_path, force=args.force)
            print(f"{args.engine} 중간 결과 생성 완료: {output_path}")
            return 0

        if args.command == "hybrid-merge":
            output_path = _safe_repository_path(args.output, root)
            report_path = output_path.with_suffix(".report.json")
            existing = [path for path in (output_path, report_path) if path.exists()]
            if existing and not args.force:
                raise HybridError(
                    "병합 결과가 이미 있습니다. --force를 사용하세요: "
                    + ", ".join(str(path) for path in existing)
                )
            paddle = load_engine_ir(args.paddle)
            docling = load_engine_ir(args.docling)
            result = merge_documents(paddle, docling)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                render_hybrid_markdown(result),
                encoding="utf-8",
                newline="\n",
            )
            report_path.write_text(
                json.dumps(hybrid_report(result), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            print(f"하이브리드 Markdown 생성 완료: {output_path}")
            print(f"검수 보고서: {report_path}")
            print(f"검수 경고: {len(result.warnings)}개")
            return 0

        result = validate_markdown(args.markdown, root)
        _print_validation(result.errors, result.warnings)
        if result.is_valid:
            print(f"검증 통과: {args.markdown.resolve()}")
            return 0
        return 1
    except (
        BenchmarkError,
        ConfigError,
        ConversionError,
        ExtractionError,
        HybridError,
        ValueError,
    ) as error:
        print(f"오류: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
