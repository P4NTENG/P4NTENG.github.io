from __future__ import annotations

import tempfile
import unittest
from importlib.util import find_spec
from pathlib import Path

from pdf_to_post.config import AppConfig
from pdf_to_post.extract import extract_pdf_text
from pdf_to_post.pipeline import ConversionError, convert_pdf


@unittest.skipUnless(find_spec("pymupdf"), "PyMuPDF가 설치되어 있지 않습니다.")
class ExtractTests(unittest.TestCase):
    def test_extracts_text_from_pdf(self) -> None:
        import pymupdf

        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "sample.pdf"
            document = pymupdf.open()
            page = document.new_page()
            page.insert_text((72, 72), "Lecture sample")
            document.save(pdf_path)
            document.close()

            extracted = extract_pdf_text(pdf_path)
            self.assertEqual(extracted.page_count, 1)
            self.assertIn("Lecture sample", extracted.pages[0].text)

    def test_end_to_end_conversion_and_overwrite_guard(self) -> None:
        import pymupdf

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "_config.yml").write_text("title: test\n", encoding="utf-8")
            pdf_path = root / "lecture.pdf"

            document = pymupdf.open()
            page = document.new_page()
            page.insert_text((72, 72), "End-to-end lecture")
            document.save(pdf_path)
            document.close()

            config = AppConfig(
                drafts_dir=Path("_drafts"),
                assets_dir=Path("assets/img/posts"),
                layout="post",
                source_heading="강의 내용",
            )
            result = convert_pdf(
                pdf_path,
                site_root=root,
                config=config,
                title="통합 테스트",
                use_math=True,
            )

            self.assertTrue(result.validation.is_valid)
            self.assertTrue(result.output_path.is_file())
            self.assertIn("End-to-end lecture", result.output_path.read_text(encoding="utf-8"))

            with self.assertRaises(ConversionError):
                convert_pdf(pdf_path, site_root=root, config=config)


if __name__ == "__main__":
    unittest.main()
