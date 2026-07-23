from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


class ConfigError(ValueError):
    """Raised when the converter configuration is invalid."""


@dataclass(frozen=True)
class AppConfig:
    drafts_dir: Path
    assets_dir: Path
    layout: str
    source_heading: str


def default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config.yml"


def find_site_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (candidate / "_config.yml").is_file():
            return candidate

    raise ConfigError(
        "Jekyll 저장소 루트를 찾지 못했습니다. --site-root를 지정하세요."
    )


def _safe_relative_path(value: object, key: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key}는 비어 있지 않은 문자열이어야 합니다.")

    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ConfigError(f"{key}는 저장소 내부의 상대 경로여야 합니다: {value}")
    return path


def _non_empty_string(value: object, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{key}는 비어 있지 않은 문자열이어야 합니다.")
    return value.strip()


def load_config(path: Path | None = None) -> AppConfig:
    config_path = (path or default_config_path()).resolve()
    if not config_path.is_file():
        raise ConfigError(f"설정 파일을 찾을 수 없습니다: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as error:
        raise ConfigError(f"설정 파일의 YAML 형식이 올바르지 않습니다: {error}") from error

    if not isinstance(raw, dict):
        raise ConfigError("설정 파일의 최상위 값은 매핑이어야 합니다.")

    site = raw.get("site", {})
    post = raw.get("post", {})
    if not isinstance(site, dict) or not isinstance(post, dict):
        raise ConfigError("site와 post 설정은 매핑이어야 합니다.")

    return AppConfig(
        drafts_dir=_safe_relative_path(site.get("drafts_dir"), "site.drafts_dir"),
        assets_dir=_safe_relative_path(site.get("assets_dir"), "site.assets_dir"),
        layout=_non_empty_string(post.get("layout"), "post.layout"),
        source_heading=_non_empty_string(
            post.get("source_heading"), "post.source_heading"
        ),
    )
