# PDF to Jekyll Draft

텍스트형 강의자료 PDF를 검수 가능한 Jekyll 초안으로 변환하는 최소 버전입니다.
OCR, 이미지 추출, LLM 기반 재구성 및 자동 게시는 아직 포함하지 않습니다.

## 설치

저장소 루트에서 다음 명령을 실행합니다.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e tools/pdf_to_post
```

## 변환

```powershell
.venv\Scripts\pdf-to-post convert lecture-pdfs/lecture.pdf --title "강의 제목"
```

기본 출력 위치는 `_drafts/<pdf-file-name>.md`입니다. 사용할 수 있는 주요 옵션은 다음과 같습니다.

```text
--slug SLUG       출력 파일명 지정
--use-math        Jekyll front matter에 use_math: true 추가
--force           기존 초안 덮어쓰기
--site-root PATH  Jekyll 저장소 루트 지정
```

## 검증

```powershell
.venv\Scripts\pdf-to-post validate _drafts/lecture.md
```

검증은 YAML front matter, 필수 필드, 본문 존재 여부와 로컬 이미지 링크를 확인합니다.
