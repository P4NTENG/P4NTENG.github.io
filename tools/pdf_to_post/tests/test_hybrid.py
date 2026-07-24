from __future__ import annotations

import unittest
from types import SimpleNamespace

from pdf_to_post.hybrid import (
    BBox,
    EngineIR,
    HybridError,
    OcrSpan,
    PageIR,
    StructureBlock,
    TableCell,
    merge_documents,
    render_hybrid_markdown,
)
from pdf_to_post.hybrid_extract import _docling_bbox
from pdf_to_post.quality import PageTextQuality, assess_text_quality, build_ocr_plan


def _span(box: tuple[float, float, float, float], text: str) -> OcrSpan:
    return OcrSpan(BBox(*box), text, 0.95)


class HybridMergeTests(unittest.TestCase):
    def test_converts_docling_bottom_left_coordinates(self) -> None:
        bbox = SimpleNamespace(
            l=10,
            t=90,
            r=50,
            b=60,
            coord_origin=SimpleNamespace(value="BOTTOMLEFT"),
        )
        converted = _docling_bbox(bbox, width=100, height=100)
        self.assertEqual(converted, BBox(0.1, 0.1, 0.5, 0.4))

    def test_uses_paddle_text_and_docling_list_structure(self) -> None:
        paddle = EngineIR(
            engine="paddle",
            source="lecture.pdf",
            pages=(
                PageIR(
                    number=4,
                    width=100,
                    height=100,
                    spans=(_span((0.1, 0.2, 0.5, 0.3), "신뢰성 높은 시스템"),),
                ),
            ),
        )
        docling = EngineIR(
            engine="docling",
            source="lecture.pdf",
            pages=(
                PageIR(
                    number=4,
                    width=100,
                    height=100,
                    blocks=(
                        StructureBlock(
                            "list_item",
                            BBox(0.05, 0.15, 0.8, 0.35),
                            0,
                            text="신회성 높은 시스템",
                        ),
                    ),
                ),
            ),
        )

        result = merge_documents(paddle, docling)
        markdown = render_hybrid_markdown(result)

        self.assertIn("- 신뢰성 높은 시스템", markdown)
        self.assertNotIn("- 신회성", markdown)
        self.assertEqual(result.pages[0].blocks[0].text_source, "paddle")

    def test_preserves_enumerated_list_style(self) -> None:
        paddle = EngineIR(
            "paddle",
            "lecture.pdf",
            (
                PageIR(
                    24,
                    100,
                    100,
                    spans=(_span((0.1, 0.1, 0.8, 0.2), "1 설치 완료 후 마무리"),),
                ),
            ),
        )
        docling = EngineIR(
            "docling",
            "lecture.pdf",
            (
                PageIR(
                    24,
                    100,
                    100,
                    blocks=(
                        StructureBlock(
                            "list_item",
                            BBox(0.05, 0.05, 0.9, 0.25),
                            0,
                            enumerated=True,
                            marker="①",
                        ),
                    ),
                ),
            ),
        )

        markdown = render_hybrid_markdown(merge_documents(paddle, docling))

        self.assertIn("1. 설치 완료 후 마무리", markdown)

    def test_uses_docling_cells_and_paddle_cell_text(self) -> None:
        paddle = EngineIR(
            engine="paddle",
            source="lecture.pdf",
            pages=(
                PageIR(
                    number=19,
                    width=100,
                    height=100,
                    spans=(
                        _span((0.1, 0.1, 0.4, 0.2), "구분"),
                        _span((0.6, 0.1, 0.9, 0.2), "동기식"),
                        _span((0.1, 0.3, 0.4, 0.4), "신뢰성"),
                        _span((0.6, 0.3, 0.9, 0.4), "높은 일관성"),
                    ),
                ),
            ),
        )
        cells = (
            TableCell(BBox(0, 0, 0.5, 0.25), 0, 0, 1, 1, "구분", True),
            TableCell(BBox(0.5, 0, 1, 0.25), 0, 1, 1, 1, "동기석", True),
            TableCell(BBox(0, 0.25, 0.5, 0.5), 1, 0, 1, 1, "신회성"),
            TableCell(BBox(0.5, 0.25, 1, 0.5), 1, 1, 1, 1, "높은 일관성"),
        )
        docling = EngineIR(
            engine="docling",
            source="lecture.pdf",
            pages=(
                PageIR(
                    number=19,
                    width=100,
                    height=100,
                    blocks=(
                        StructureBlock(
                            "table", BBox(0, 0, 1, 0.5), 0, cells=cells, rows=2, columns=2
                        ),
                    ),
                ),
            ),
        )

        markdown = render_hybrid_markdown(merge_documents(paddle, docling))

        self.assertIn("| 구분 | 동기식 |", markdown)
        self.assertIn("| 신뢰성 | 높은 일관성 |", markdown)
        self.assertNotIn("신회성", markdown)

    def test_keeps_unmatched_paddle_text_with_review_warning(self) -> None:
        paddle = EngineIR(
            engine="paddle",
            source="lecture.pdf",
            pages=(
                PageIR(
                    number=1,
                    width=100,
                    height=100,
                    spans=(_span((0.1, 0.8, 0.4, 0.9), "누락 방지"),),
                ),
            ),
        )
        docling = EngineIR(
            engine="docling",
            source="lecture.pdf",
            pages=(PageIR(number=1, width=100, height=100),),
        )

        result = merge_documents(paddle, docling)

        self.assertEqual(result.pages[0].blocks[0].text, "누락 방지")
        self.assertIn("대응하지 않는", result.pages[0].blocks[0].warnings[0])

    def test_selective_plan_uses_docling_native_text_on_clean_page(self) -> None:
        broken = assess_text_quality("구조 ㏙구조㏚ § 㑄")
        clean = assess_text_quality(
            "Git은 변경 이력을 관리하는 분산 버전 관리 시스템입니다. "
            "저장소를 만들고 변경 내용을 기록합니다."
        )
        plan = build_ocr_plan(
            (
                PageTextQuality(1, broken),
                PageTextQuality(2, clean),
            )
        )
        paddle = EngineIR(
            engine="paddle",
            source="lecture.pdf",
            pages=(
                PageIR(1, 100, 100, spans=(_span((0.1, 0.1, 0.5, 0.2), "OCR"),)),
                PageIR(2, 100, 100),
            ),
            ocr_plan=plan,
        )
        docling = EngineIR(
            engine="docling",
            source="lecture.pdf",
            pages=(
                PageIR(
                    1,
                    100,
                    100,
                    blocks=(StructureBlock("text", BBox(0.1, 0.1, 0.5, 0.2), 0, "깨진"),),
                ),
                PageIR(
                    2,
                    100,
                    100,
                    blocks=(StructureBlock("text", BBox(0.1, 0.1, 0.5, 0.2), 0, "정상"),),
                ),
            ),
        )

        loaded = EngineIR.from_dict(paddle.to_dict())
        result = merge_documents(loaded, docling)

        self.assertEqual(result.pages[0].blocks[0].text_source, "paddle")
        self.assertEqual(result.pages[1].blocks[0].text, "정상")
        self.assertEqual(result.pages[1].blocks[0].text_source, "docling-native")
        self.assertEqual(result.pages[1].blocks[0].warnings, ())

    def test_rejects_different_page_sets(self) -> None:
        paddle = EngineIR("paddle", "lecture.pdf", (PageIR(1, 1, 1),))
        docling = EngineIR("docling", "lecture.pdf", (PageIR(2, 1, 1),))
        with self.assertRaises(HybridError):
            merge_documents(paddle, docling)


if __name__ == "__main__":
    unittest.main()
