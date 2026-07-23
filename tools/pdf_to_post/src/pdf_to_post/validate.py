from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml


FRONT_MATTER_PATTERN = re.compile(
    r"\A---[ \t]*\n(?P<yaml>.*?)\n---[ \t]*\n(?P<body>.*)\Z",
    re.DOTALL,
)
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\((?P<target>[^)]+)\)")


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _local_image_path(target: str, markdown_path: Path, site_root: Path) -> Path | None:
    value = target.strip().split(maxsplit=1)[0].strip("<>")
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or value.startswith(("#", "data:")):
        return None

    path_text = unquote(parsed.path)
    if path_text.startswith("/"):
        return site_root / path_text.lstrip("/")
    return markdown_path.parent / path_text


def validate_markdown(markdown_path: Path, site_root: Path) -> ValidationResult:
    path = markdown_path.resolve()
    root = site_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return ValidationResult(
            errors=(f"Markdown 파일을 찾을 수 없습니다: {path}",), warnings=()
        )

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ValidationResult(
            errors=("Markdown 파일은 BOM 없는 UTF-8이어야 합니다.",), warnings=()
        )

    if content.startswith("\ufeff"):
        return ValidationResult(
            errors=("Markdown 파일에 UTF-8 BOM이 포함되어 있습니다.",), warnings=()
        )

    match = FRONT_MATTER_PATTERN.match(content)
    if not match:
        return ValidationResult(
            errors=("파일 맨 앞에 유효한 YAML front matter가 필요합니다.",), warnings=()
        )

    try:
        metadata = yaml.safe_load(match.group("yaml")) or {}
    except yaml.YAMLError as error:
        errors.append(f"YAML front matter 형식이 올바르지 않습니다: {error}")
        metadata = {}

    if not isinstance(metadata, dict):
        errors.append("YAML front matter는 매핑이어야 합니다.")
        metadata = {}

    for key in ("layout", "title"):
        value = metadata.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"front matter에 비어 있지 않은 {key} 값이 필요합니다.")

    if not match.group("body").strip():
        errors.append("Markdown 본문이 비어 있습니다.")

    for image_match in IMAGE_PATTERN.finditer(match.group("body")):
        target = image_match.group("target")
        image_path = _local_image_path(target, path, root)
        if image_path is not None and not image_path.is_file():
            errors.append(f"이미지 파일을 찾을 수 없습니다: {target}")

    if "자동 생성된 초안" in content:
        warnings.append("자동 생성된 초안입니다. 게시 전에 원문 대조 검수가 필요합니다.")

    return ValidationResult(errors=tuple(errors), warnings=tuple(warnings))
