from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path
from time import perf_counter
from typing import Callable

from pdf_to_post.quality import TextQuality, assess_text_quality


DEFAULT_PAGES = (1, 4, 19, 24, 40)
SUPPORTED_ENGINES = ("native", "paddle", "docling")


class BenchmarkError(RuntimeError):
    """Raised when the extraction benchmark cannot run."""


@dataclass(frozen=True)
class PageResult:
    page: int
    seconds: float
    output: str
    quality: TextQuality

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["quality"] = self.quality.to_dict()
        return data


def parse_pages(value: str) -> tuple[int, ...]:
    try:
        pages = tuple(dict.fromkeys(int(item.strip()) for item in value.split(",")))
    except ValueError as error:
        raise BenchmarkError("페이지는 1,4,19처럼 쉼표로 구분해 지정하세요.") from error
    if not pages or any(page < 1 for page in pages):
        raise BenchmarkError("페이지 번호는 1 이상의 정수여야 합니다.")
    return pages


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unknown"


def _safe_output_dir(output: Path, site_root: Path) -> Path:
    root = site_root.resolve()
    resolved = (root / output).resolve() if not output.is_absolute() else output.resolve()
    if not resolved.is_relative_to(root):
        raise BenchmarkError(f"벤치마크 출력은 저장소 안에 있어야 합니다: {resolved}")
    return resolved


def _validate_input(pdf_path: Path, pages: tuple[int, ...]) -> tuple[Path, int]:
    source = pdf_path.resolve()
    if not source.is_file():
        raise BenchmarkError(f"PDF 파일을 찾을 수 없습니다: {source}")
    if source.suffix.lower() != ".pdf":
        raise BenchmarkError(f"PDF 파일만 벤치마크할 수 있습니다: {source}")
    try:
        import pymupdf
    except ModuleNotFoundError as error:
        raise BenchmarkError("PyMuPDF가 설치되어 있지 않습니다.") from error
    try:
        with pymupdf.open(source) as document:
            page_count = document.page_count
    except Exception as error:
        raise BenchmarkError(f"PDF를 읽지 못했습니다: {error}") from error
    invalid = [page for page in pages if page > page_count]
    if invalid:
        raise BenchmarkError(
            f"PDF는 {page_count}페이지인데 범위를 벗어난 페이지가 있습니다: {invalid}"
        )
    return source, page_count


def _write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise BenchmarkError(f"출력 파일이 이미 있습니다. --force를 사용하세요: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def _render_pages(
    source: Path, pages: tuple[int, ...], output_dir: Path, dpi: int, force: bool
) -> dict[int, Path]:
    import pymupdf

    page_dir = output_dir / "pages"
    page_dir.mkdir(parents=True, exist_ok=True)
    rendered: dict[int, Path] = {}
    with pymupdf.open(source) as document:
        for page_number in pages:
            target = page_dir / f"page-{page_number:03d}.png"
            if target.exists() and not force:
                rendered[page_number] = target
                continue
            pixmap = document[page_number - 1].get_pixmap(dpi=dpi, alpha=False)
            pixmap.save(target)
            rendered[page_number] = target
    return rendered


def _run_native(source: Path, pages: tuple[int, ...]) -> tuple[list[PageResult], str]:
    import pymupdf

    results: list[PageResult] = []
    with pymupdf.open(source) as document:
        for page_number in pages:
            started = perf_counter()
            text = document[page_number - 1].get_text("text", sort=True)
            elapsed = perf_counter() - started
            results.append(
                PageResult(page_number, elapsed, text, assess_text_quality(text))
            )
    return results, _package_version("PyMuPDF")


def _configure_paddle_cache(output_dir: Path) -> None:
    cache_root = output_dir.parent / "cache" / "paddle"
    home = cache_root / "home"
    for directory in (home, cache_root / "paddlex", cache_root / "huggingface"):
        directory.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HOME", str(home))
    os.environ.setdefault("USERPROFILE", str(home))
    os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(cache_root / "paddlex"))
    os.environ.setdefault("HF_HOME", str(cache_root / "huggingface"))


def _run_paddle(
    rendered: dict[int, Path], output_dir: Path
) -> tuple[list[PageResult], str]:
    _configure_paddle_cache(output_dir)
    try:
        from paddleocr import PPStructureV3
    except ModuleNotFoundError as error:
        raise BenchmarkError(
            "PaddleOCR 환경이 아닙니다. paddleocr와 paddlepaddle을 설치하세요."
        ) from error

    try:
        pipeline = PPStructureV3(
            lang="korean",
            device="cpu",
            # PaddlePaddle 3.3의 Windows oneDNN 경로는 일부 레이아웃 모델의
            # ArrayAttribute를 변환하지 못하므로 재현 가능한 일반 CPU 경로를 쓴다.
            enable_mkldnn=False,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            use_seal_recognition=False,
            use_table_recognition=True,
            use_formula_recognition=False,
            use_chart_recognition=False,
            use_region_detection=False,
            format_block_content=True,
        )
    except Exception as error:
        raise BenchmarkError(f"PaddleOCR 모델을 초기화하지 못했습니다: {error}") from error

    results: list[PageResult] = []
    for page_number, image_path in rendered.items():
        started = perf_counter()
        try:
            predictions = list(pipeline.predict(str(image_path)))
            if not predictions:
                raise BenchmarkError(f"PaddleOCR가 {page_number}페이지 결과를 만들지 못했습니다.")
            markdown = predictions[0].markdown.get("markdown_texts", "")
        except BenchmarkError:
            raise
        except Exception as error:
            raise BenchmarkError(
                f"PaddleOCR {page_number}페이지 처리 실패: {error}"
            ) from error
        elapsed = perf_counter() - started
        results.append(
            PageResult(page_number, elapsed, markdown, assess_text_quality(markdown))
        )
    return results, _package_version("paddleocr")


def _run_docling(
    source: Path, pages: tuple[int, ...], output_dir: Path
) -> tuple[list[PageResult], str]:
    cache_root = output_dir.parent / "cache" / "docling"
    for directory in (
        cache_root,
        cache_root / "artifacts",
        cache_root / "easyocr",
        cache_root / "huggingface",
        cache_root / "torch",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("EASYOCR_MODULE_PATH", str(cache_root / "easyocr"))
    os.environ.setdefault("HF_HOME", str(cache_root / "huggingface"))
    os.environ.setdefault("TORCH_HOME", str(cache_root / "torch"))
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.accelerator_options import AcceleratorDevice
        from docling.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ModuleNotFoundError as error:
        raise BenchmarkError(
            "Docling 환경이 아닙니다. `docling[easyocr]`를 설치하세요."
        ) from error

    options = PdfPipelineOptions()
    options.do_ocr = True
    options.do_table_structure = True
    options.accelerator_options.device = AcceleratorDevice.CPU
    options.ocr_options = EasyOcrOptions(
        lang=["ko", "en"],
        force_full_page_ocr=True,
        model_storage_directory=str(cache_root / "easyocr"),
    )
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )

    results: list[PageResult] = []
    for page_number in pages:
        started = perf_counter()
        try:
            document = converter.convert(
                source, page_range=(page_number, page_number)
            ).document
            markdown = document.export_to_markdown()
        except Exception as error:
            raise BenchmarkError(
                f"Docling {page_number}페이지 처리 실패: {error}"
            ) from error
        elapsed = perf_counter() - started
        results.append(
            PageResult(page_number, elapsed, markdown, assess_text_quality(markdown))
        )
    return results, _package_version("docling")


def _write_summary(
    engine: str,
    engine_version: str,
    source: Path,
    page_count: int,
    dpi: int,
    results: list[PageResult],
    output_dir: Path,
    force: bool,
) -> Path:
    engine_dir = output_dir / engine
    engine_dir.mkdir(parents=True, exist_ok=True)
    for result in results:
        _write_text(
            engine_dir / f"page-{result.page:03d}.md", result.output, force=force
        )
    summary = {
        "engine": engine,
        "engine_version": engine_version,
        "source": source.name,
        "source_page_count": page_count,
        "dpi": dpi,
        "total_seconds": round(sum(item.seconds for item in results), 3),
        "pages": [item.to_dict() | {"output": f"page-{item.page:03d}.md"} for item in results],
    }
    summary_path = engine_dir / "summary.json"
    if summary_path.exists() and not force:
        raise BenchmarkError(f"출력 파일이 이미 있습니다: {summary_path}")
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return summary_path


def write_comparison(output_dir: Path) -> Path:
    summaries: list[dict[str, object]] = []
    for engine in SUPPORTED_ENGINES:
        path = output_dir / engine / "summary.json"
        if path.is_file():
            summaries.append(json.loads(path.read_text(encoding="utf-8")))

    lines = [
        "# PDF 추출 엔진 비교",
        "",
        "> 자동 지표는 오류 징후와 구조 보존 정도를 보여줄 뿐 정확도 순위가 아닙니다. 페이지 이미지와 결과 Markdown을 함께 대조해야 합니다.",
        "",
        "| 엔진 | 버전 | 페이지 처리 합계(초) | OCR 필요 판정 | 의심 문자 | Markdown 제목/목록/표 |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        pages = summary["pages"]
        assert isinstance(pages, list)
        qualities = [page["quality"] for page in pages]
        ocr_required = sum(q["decision"] == "ocr-required" for q in qualities)
        suspicious = sum(q["suspicious_count"] for q in qualities)
        structures = sum(
            q["heading_count"] + q["list_item_count"] + q["table_row_count"]
            for q in qualities
        )
        lines.append(
            f"| {summary['engine']} | {summary['engine_version']} | "
            f"{summary['total_seconds']} | {ocr_required}/{len(pages)} | "
            f"{suspicious} | {structures} |"
        )

    all_pages = sorted(
        {
            page["page"]
            for summary in summaries
            for page in summary["pages"]
        }
    )
    lines.extend(["", "## 페이지별 결과", ""])
    for page in all_pages:
        links = []
        for summary in summaries:
            engine = summary["engine"]
            if any(item["page"] == page for item in summary["pages"]):
                links.append(f"[{engine}]({engine}/page-{page:03d}.md)")
        lines.append(
            f"- {page}페이지: [원본 렌더링](pages/page-{page:03d}.png) · "
            + " · ".join(links)
        )

    path = output_dir / "comparison.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def run_benchmark(
    pdf_path: Path,
    *,
    site_root: Path,
    output: Path,
    engine: str,
    pages: tuple[int, ...] = DEFAULT_PAGES,
    dpi: int = 200,
    force: bool = False,
) -> tuple[Path, Path]:
    if engine not in SUPPORTED_ENGINES:
        raise BenchmarkError(f"지원하지 않는 엔진입니다: {engine}")
    if not 100 <= dpi <= 600:
        raise BenchmarkError("DPI는 100 이상 600 이하로 지정하세요.")

    source, page_count = _validate_input(pdf_path, pages)
    output_dir = _safe_output_dir(output, site_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    engine_dir = output_dir / engine
    expected_outputs = [engine_dir / "summary.json", *(
        engine_dir / f"page-{page:03d}.md" for page in pages
    )]
    existing_outputs = [path for path in expected_outputs if path.exists()]
    if existing_outputs and not force:
        raise BenchmarkError(
            "기존 벤치마크 결과가 있습니다. --force를 사용하세요: "
            + ", ".join(str(path) for path in existing_outputs)
        )
    rendered = _render_pages(source, pages, output_dir, dpi, force)

    runners: dict[str, Callable[[], tuple[list[PageResult], str]]] = {
        "native": lambda: _run_native(source, pages),
        "paddle": lambda: _run_paddle(rendered, output_dir),
        "docling": lambda: _run_docling(source, pages, output_dir),
    }
    results, engine_version = runners[engine]()
    summary = _write_summary(
        engine,
        engine_version,
        source,
        page_count,
        dpi,
        results,
        output_dir,
        force,
    )
    comparison = write_comparison(output_dir)
    return summary, comparison
