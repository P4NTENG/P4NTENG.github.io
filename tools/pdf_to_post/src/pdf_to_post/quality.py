from __future__ import annotations

from dataclasses import asdict, dataclass
import re


_HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
_HANGUL_RUN_RE = re.compile(r"[\uac00-\ud7a3]{8,}")


def _is_suspicious(character: str) -> bool:
    codepoint = ord(character)
    return (
        character in {"\u00a7", "\ufffd"}
        or 0x3300 <= codepoint <= 0x33FF  # CJK 호환 문자
        or 0x3400 <= codepoint <= 0x4DBF  # 이 PDF에서 오매핑된 CJK 확장 A
        or 0xE000 <= codepoint <= 0xF8FF  # 사설 영역
    )


@dataclass(frozen=True)
class TextQuality:
    character_count: int
    non_whitespace_count: int
    hangul_count: int
    suspicious_count: int
    suspicious_ratio: float
    longest_unspaced_hangul_run: int
    heading_count: int
    list_item_count: int
    table_row_count: int
    decision: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def assess_text_quality(text: str) -> TextQuality:
    non_whitespace_count = sum(not character.isspace() for character in text)
    hangul_count = len(_HANGUL_RE.findall(text))
    suspicious_count = sum(_is_suspicious(character) for character in text)
    suspicious_ratio = (
        suspicious_count / non_whitespace_count if non_whitespace_count else 0.0
    )
    hangul_runs = _HANGUL_RUN_RE.findall(text)
    longest_run = max((len(run) for run in hangul_runs), default=0)

    reasons: list[str] = []
    if non_whitespace_count < 20:
        reasons.append("추출된 문자가 너무 적음")
    if suspicious_count >= 3 or suspicious_ratio >= 0.003:
        reasons.append(
            f"의심 문자 {suspicious_count}개({suspicious_ratio:.2%}) 감지"
        )
    if hangul_count >= 30 and longest_run >= 18:
        reasons.append(f"공백 없는 한글 연속 문자열 {longest_run}자 감지")

    return TextQuality(
        character_count=len(text),
        non_whitespace_count=non_whitespace_count,
        hangul_count=hangul_count,
        suspicious_count=suspicious_count,
        suspicious_ratio=round(suspicious_ratio, 6),
        longest_unspaced_hangul_run=longest_run,
        heading_count=sum(line.lstrip().startswith("#") for line in text.splitlines()),
        list_item_count=sum(
            line.lstrip().startswith(("- ", "* ", "+ "))
            for line in text.splitlines()
        ),
        table_row_count=sum(
            line.strip().startswith("|") and line.strip().endswith("|")
            for line in text.splitlines()
        ),
        decision="ocr-required" if reasons else "native-usable",
        reasons=tuple(reasons),
    )
