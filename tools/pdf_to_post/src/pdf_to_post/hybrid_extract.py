from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pdf_to_post.hybrid import (
    BBox,
    EngineIR,
    HybridError,
    OcrSpan,
    PageIR,
    StructureBlock,
    TableCell,
)
from pdf_to_post.openvino_backend import (
    DETECTION_MODEL,
    RECOGNITION_MODEL,
    configure_openvino_gpu_fp32,
)
from pdf_to_post.quality import plan_pdf_ocr


def _normalize_bbox(
    values: list[float] | tuple[float, ...], width: float, height: float
) -> BBox:
    left, top, right, bottom = (float(value) for value in values)
    return BBox(left / width, top / height, right / width, bottom / height)


def _configure_paddle_cache(work_dir: Path) -> None:
    cache_root = work_dir / "cache" / "paddle"
    home = cache_root / "home"
    for directory in (home, cache_root / "paddlex", cache_root / "huggingface"):
        directory.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HOME", str(home))
    os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(cache_root / "paddlex"))
    os.environ.setdefault("HF_HOME", str(cache_root / "huggingface"))


def _render_pages(
    source: Path, pages: tuple[int, ...], work_dir: Path, dpi: int
) -> dict[int, Path]:
    try:
        import pymupdf
    except ModuleNotFoundError as error:
        raise HybridError("PyMuPDF가 설치되어 있지 않습니다.") from error

    page_dir = work_dir / "hybrid" / "pages"
    page_dir.mkdir(parents=True, exist_ok=True)
    rendered: dict[int, Path] = {}
    with pymupdf.open(source) as document:
        for page_number in pages:
            target = page_dir / f"page-{page_number:03d}-{dpi}dpi.png"
            if not target.exists():
                document[page_number - 1].get_pixmap(dpi=dpi, alpha=False).save(target)
            rendered[page_number] = target
    return rendered


def extract_paddle_ir(
    source: Path, pages: tuple[int, ...], work_dir: Path, dpi: int
) -> EngineIR:
    try:
        plan = plan_pdf_ocr(source, pages)
        import pymupdf
    except Exception as error:
        raise HybridError(f"페이지 텍스트 품질 검사에 실패했습니다: {error}") from error

    if not plan.ocr_pages:
        with pymupdf.open(source) as document:
            native_pages = tuple(
                PageIR(
                    number=page_number,
                    width=float(document[page_number - 1].rect.width),
                    height=float(document[page_number - 1].rect.height),
                )
                for page_number in pages
            )
        return EngineIR(
            engine="paddle",
            source=source.name,
            pages=native_pages,
            ocr_plan=plan,
        )

    _configure_paddle_cache(work_dir)
    try:
        from paddleocr import PaddleOCR
    except ModuleNotFoundError as error:
        raise HybridError(
            "PaddleOCR 환경이 아닙니다. paddlepaddle과 paddleocr를 설치하세요."
        ) from error

    rendered = _render_pages(source, plan.ocr_pages, work_dir, dpi)
    try:
        pipeline = PaddleOCR(
            device="cpu",
            enable_mkldnn=False,
            text_detection_model_name=DETECTION_MODEL,
            text_recognition_model_name=RECOGNITION_MODEL,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
        configure_openvino_gpu_fp32(pipeline, work_dir)
    except HybridError:
        raise
    except Exception as error:
        raise HybridError(f"PaddleOCR 모델 초기화 실패: {error}") from error

    extracted_by_page: dict[int, PageIR] = {}
    for page_number, image_path in rendered.items():
        try:
            results = list(pipeline.predict(str(image_path)))
            if not results:
                raise HybridError(f"PaddleOCR {page_number}페이지 결과가 없습니다.")
            result = results[0]
            pixmap = pymupdf.Pixmap(image_path)
            width, height = pixmap.width, pixmap.height
            spans = tuple(
                OcrSpan(
                    bbox=_normalize_bbox(box.tolist(), width, height),
                    text=str(text),
                    confidence=float(score),
                )
                for box, text, score in zip(
                    result["rec_boxes"], result["rec_texts"], result["rec_scores"]
                )
                if str(text).strip()
            )
        except HybridError:
            raise
        except Exception as error:
            raise HybridError(f"PaddleOCR {page_number}페이지 추출 실패: {error}") from error
        extracted_by_page[page_number] = PageIR(
            number=page_number,
            width=width,
            height=height,
            spans=spans,
        )

    with pymupdf.open(source) as document:
        extracted_pages = tuple(
            extracted_by_page.get(page_number)
            or PageIR(
                number=page_number,
                width=float(document[page_number - 1].rect.width),
                height=float(document[page_number - 1].rect.height),
            )
            for page_number in pages
        )
    return EngineIR(
        engine="paddle",
        source=source.name,
        pages=extracted_pages,
        ocr_plan=plan,
    )


def _configure_docling_cache(work_dir: Path) -> None:
    cache_root = work_dir / "cache" / "docling"
    for directory in (
        cache_root / "huggingface",
        cache_root / "torch",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(cache_root / "huggingface"))
    os.environ.setdefault("TORCH_HOME", str(cache_root / "torch"))


def _docling_bbox(bbox: Any, width: float, height: float) -> BBox:
    origin = getattr(getattr(bbox, "coord_origin", None), "value", "TOPLEFT")
    if origin == "BOTTOMLEFT":
        values = (bbox.l, height - bbox.t, bbox.r, height - bbox.b)
    else:
        values = (bbox.l, bbox.t, bbox.r, bbox.b)
    return _normalize_bbox(values, width, height)


def extract_docling_ir(
    source: Path, pages: tuple[int, ...], work_dir: Path, dpi: int
) -> EngineIR:
    del dpi  # Docling은 PDF 좌표계에서 직접 처리한다.
    _configure_docling_cache(work_dir)
    try:
        from docling.datamodel.accelerator_options import AcceleratorDevice
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ModuleNotFoundError as error:
        raise HybridError(
            "Docling 환경이 아닙니다. docling을 설치하세요."
        ) from error

    options = PdfPipelineOptions()
    options.do_ocr = False
    options.do_table_structure = True
    options.accelerator_options.device = AcceleratorDevice.CPU
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )

    extracted_pages: list[PageIR] = []
    for page_number in pages:
        try:
            document = converter.convert(
                source, page_range=(page_number, page_number)
            ).document
            page_item = next(iter(document.pages.values()))
            width, height = page_item.size.width, page_item.size.height
            blocks: list[StructureBlock] = []
            body_items = document.iterate_items(with_groups=False)
            furniture_items = document.iterate_items(
                root=document.furniture, with_groups=False
            )
            for order, (item, _) in enumerate((*body_items, *furniture_items)):
                provenance = getattr(item, "prov", None) or []
                if not provenance:
                    continue
                block_type = getattr(getattr(item, "label", None), "value", None)
                if not block_type:
                    continue
                bbox = _docling_bbox(provenance[0].bbox, width, height)
                text = str(getattr(item, "text", "") or "")
                cells: tuple[TableCell, ...] = ()
                rows = columns = 0
                data = getattr(item, "data", None)
                if block_type == "table" and data is not None:
                    rows, columns = int(data.num_rows), int(data.num_cols)
                    cells = tuple(
                        TableCell(
                            bbox=(
                                _docling_bbox(cell.bbox, width, height)
                                if cell.bbox is not None
                                else None
                            ),
                            row=int(cell.start_row_offset_idx),
                            column=int(cell.start_col_offset_idx),
                            row_span=int(cell.row_span),
                            column_span=int(cell.col_span),
                            text=str(cell.text or ""),
                            is_header=bool(cell.column_header or cell.row_header),
                        )
                        for cell in data.table_cells
                    )
                blocks.append(
                    StructureBlock(
                        block_type=block_type,
                        bbox=bbox,
                        order=order,
                        text=text,
                        cells=cells,
                        rows=rows,
                        columns=columns,
                        enumerated=bool(getattr(item, "enumerated", False)),
                        marker=str(getattr(item, "marker", "") or ""),
                    )
                )
        except Exception as error:
            raise HybridError(f"Docling {page_number}페이지 추출 실패: {error}") from error
        extracted_pages.append(
            PageIR(number=page_number, width=width, height=height, blocks=tuple(blocks))
        )
    return EngineIR(engine="docling", source=source.name, pages=tuple(extracted_pages))


def extract_engine_ir(
    source: Path,
    *,
    engine: str,
    pages: tuple[int, ...] | None,
    work_dir: Path,
    dpi: int,
) -> EngineIR:
    pdf = source.resolve()
    if not pdf.is_file():
        raise HybridError(f"PDF 파일을 찾을 수 없습니다: {pdf}")
    if pdf.suffix.lower() != ".pdf":
        raise HybridError(f"PDF 파일만 처리할 수 있습니다: {pdf}")
    if not 100 <= dpi <= 600:
        raise HybridError("DPI는 100 이상 600 이하로 지정하세요.")
    if pages is not None and (not pages or any(page < 1 for page in pages)):
        raise HybridError("페이지 번호는 1 이상의 정수여야 합니다.")

    try:
        import pymupdf

        with pymupdf.open(pdf) as document:
            if pages is None:
                pages = tuple(range(1, document.page_count + 1))
            invalid = [page for page in pages if page > document.page_count]
    except Exception as error:
        raise HybridError(f"PDF를 읽지 못했습니다: {error}") from error
    if invalid:
        raise HybridError(f"PDF 범위를 벗어난 페이지입니다: {invalid}")

    if engine == "paddle":
        return extract_paddle_ir(pdf, pages, work_dir, dpi)
    if engine == "docling":
        return extract_docling_ir(pdf, pages, work_dir, dpi)
    raise HybridError(f"지원하지 않는 하이브리드 추출 엔진입니다: {engine}")
