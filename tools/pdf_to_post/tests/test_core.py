from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pdf_to_post.config import AppConfig
from pdf_to_post.extract import ExtractedDocument, ExtractedPage
from pdf_to_post.normalize import normalize_text, slugify
from pdf_to_post.render import escape_liquid, render_draft
from pdf_to_post.validate import validate_markdown


class NormalizeTests(unittest.TestCase):
    def test_normalize_text_collapses_blank_lines(self) -> None:
        self.assertEqual(normalize_text("첫 줄  \r\n\r\n\r\n둘째 줄\f"), "첫 줄\n\n둘째 줄")

    def test_slugify_supports_korean_and_blocks_path_characters(self) -> None:
        self.assertEqual(slugify("../LLM 강의 자료.pdf"), "llm-강의-자료-pdf")


class RenderAndValidationTests(unittest.TestCase):
    def test_escape_liquid_preserves_literal_tokens(self) -> None:
        escaped = escape_liquid("{{ value }} {% include file.html %}")
        self.assertIn("{% raw %}{{{% endraw %}", escaped)
        self.assertIn("{% raw %}{%{% endraw %}", escaped)

    def test_rendered_draft_passes_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "_config.yml").write_text("title: test\n", encoding="utf-8")
            draft = root / "_drafts" / "sample.md"
            draft.parent.mkdir()

            document = ExtractedDocument(
                source=Path("sample.pdf"),
                pages=(ExtractedPage(number=1, text="첫 페이지 내용"),),
                warnings=(),
            )
            content = render_draft(
                document,
                title="샘플 강의",
                layout="post",
                source_heading="강의 내용",
                use_math=True,
            )
            draft.write_text(content, encoding="utf-8")

            result = validate_markdown(draft, root)
            self.assertTrue(result.is_valid, result.errors)
            self.assertIn("자동 생성된 초안", result.warnings[0])

    def test_missing_image_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "_drafts" / "sample.md"
            draft.parent.mkdir()
            draft.write_text(
                "---\nlayout: post\ntitle: Sample\n---\n\n![missing](/assets/missing.png)\n",
                encoding="utf-8",
            )

            result = validate_markdown(draft, root)
            self.assertFalse(result.is_valid)
            self.assertIn("이미지 파일", result.errors[0])

    def test_utf8_bom_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "sample.md"
            draft.write_text(
                "---\nlayout: post\ntitle: Sample\n---\nBody\n",
                encoding="utf-8-sig",
            )

            result = validate_markdown(draft, root)
            self.assertFalse(result.is_valid)
            self.assertIn("BOM", result.errors[0])


class ConfigShapeTests(unittest.TestCase):
    def test_app_config_paths_are_relative(self) -> None:
        config = AppConfig(
            drafts_dir=Path("_drafts"),
            assets_dir=Path("assets/img/posts"),
            layout="post",
            source_heading="강의 내용",
        )
        self.assertFalse(config.drafts_dir.is_absolute())


if __name__ == "__main__":
    unittest.main()
