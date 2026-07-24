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

## 추출 엔진 실험

문자 매핑이 깨진 PDF는 대표 페이지를 먼저 비교합니다. 기본 대표 페이지는 표지(1),
본문 목록(4), 표(19), 명령어(24), 화면 캡처(40)입니다.

```powershell
.venv\Scripts\pdf-to-post benchmark lecture-pdfs\lecture.pdf --engine native
```

OCR 엔진은 의존성이 크고 서로 충돌할 수 있으므로 별도 가상환경에서 같은 명령을
`--engine paddle` 또는 `--engine docling`으로 실행합니다. 결과는 기본적으로
`.work/pdf-to-post/benchmark/` 아래에 원본 렌더링, 엔진별 Markdown과 JSON 지표,
`comparison.md`로 생성됩니다.

```powershell
pdf-to-post benchmark PDF --engine ENGINE --pages 1,4,19,24,40 --dpi 200
```

자동 지표만으로 OCR 정확도를 확정하지 않습니다. `comparison.md`에서 각 페이지의
원본 렌더링과 결과 Markdown을 함께 열어 글자, 읽기 순서, 목록, 표를 검수합니다.

Windows CPU 실험 환경 예시는 다음과 같습니다. PaddlePaddle은 공식 CPU 패키지를
먼저 설치합니다. Docling은 Windows 경로 길이 제한을 피하도록 짧은 경로의
가상환경을 권장합니다.

```powershell
python -m venv .work\pdf-to-post\venvs\paddle
.work\pdf-to-post\venvs\paddle\Scripts\python -m pip install paddlepaddle==3.3.0 `
  -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
.work\pdf-to-post\venvs\paddle\Scripts\python -m pip install -e "tools/pdf_to_post[paddle]"

python -m venv C:\Temp\pdf-to-post-docling
C:\Temp\pdf-to-post-docling\Scripts\python -m pip install -e "tools/pdf_to_post[docling]"
```

모델은 첫 실행 때 `.work/pdf-to-post/cache/`에 다운로드됩니다. 비교표의 시간은
모델 다운로드와 일부 초기화를 제외한 페이지 처리 시간의 합계입니다.

## Paddle 텍스트와 Docling 구조 병합

두 엔진의 최종 Markdown을 직접 합치지 않고 좌표가 포함된 공통 중간 형식을 먼저
생성합니다. Paddle 환경은 OCR 텍스트·신뢰도·좌표를, Docling 환경은 제목·목록·표
셀·코드·이미지 구조를 추출합니다.

```powershell
$pdf = "lecture-pdfs\lecture.pdf"

.work\pdf-to-post\venvs\paddle\Scripts\pdf-to-post `
  hybrid-extract $pdf --engine paddle --pages 4,19,24

C:\Temp\pdf-to-post-docling\Scripts\pdf-to-post `
  hybrid-extract $pdf --engine docling --pages 4,19,24

.venv\Scripts\pdf-to-post hybrid-merge `
  .work\pdf-to-post\hybrid\paddle.json `
  .work\pdf-to-post\hybrid\docling.json
```

기본 출력은 다음과 같습니다.

- `.work/pdf-to-post/hybrid/hybrid.md`: 병합된 Markdown
- `.work/pdf-to-post/hybrid/hybrid.report.json`: 블록별 텍스트 출처, 신뢰도와 검수 경고

병합 규칙은 Docling의 읽기 순서와 블록 종류를 유지하면서 동일 좌표의 텍스트를
PaddleOCR 결과로 교체합니다. 표는 Docling 셀 경계 안의 Paddle 텍스트를 사용합니다.
두 엔진의 단어가 다르거나, 낮은 신뢰도·누락 구조·추론한 목록 항목이 있으면 결과에
`<!-- review: ... -->` 주석을 남깁니다. 이미지 영역은 본문으로 OCR하지 않고 원본
이미지를 연결할 수 있는 좌표 주석으로 유지합니다.
