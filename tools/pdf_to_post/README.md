# PDF to Jekyll Draft

텍스트형 강의자료 PDF를 검수 가능한 Jekyll 초안으로 변환하는 최소 버전입니다.
하이브리드 경로는 OCR과 문서 구조 추출을 지원하며, LLM 기반 재구성과 자동 게시는
아직 포함하지 않습니다.

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

## OpenVINO 준비

하이브리드 추출의 PaddleOCR 검출 모델은 OpenVINO GPU FP32, 인식 모델은 OpenVINO
CPU FP32로 실행합니다. 동적 shape 검출 모델은 반복 실행 중 OpenCL 이벤트 오류가
발생하므로 첫 입력 텐서 크기로 정적 컴파일합니다. 이후 입력 크기가 바뀌면 해당
크기로 다시 컴파일합니다.
PaddleOCR CPU 벤치마크와 의존성을 분리하기 위해 전용 환경을 사용합니다.

```powershell
py -3.11 -m venv .work\pdf-to-post\venvs\openvino
.work\pdf-to-post\venvs\openvino\Scripts\python -m pip install paddlepaddle==3.3.0 `
  -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
.work\pdf-to-post\venvs\openvino\Scripts\python -m pip install `
  -e "tools/pdf_to_post[paddle,openvino]"
```

OpenVINO가 현재 Paddle PIR 모델의 `inference.json`을 직접 읽지 못하므로 ONNX 모델을
한 번 생성해 `.work/pdf-to-post/cache/openvino/models/`에 둡니다. 먼저 Paddle
벤치마크를 한 번 실행해 원본 모델 캐시를 준비한 뒤 변환합니다.

```powershell
$paddlePython = ".work\pdf-to-post\venvs\paddle\Scripts\python"
& $paddlePython -m pdf_to_post.cli benchmark lecture-pdfs\lecture.pdf `
  --engine paddle --pages 1 --force

py -3.11 -m venv .work\pdf-to-post\venvs\paddle2onnx
$converter = ".work\pdf-to-post\venvs\paddle2onnx\Scripts"
& "$converter\python" -m pip install packaging paddle2onnx==2.1.0
& "$converter\python" -m pip install --force-reinstall --no-deps `
  paddlepaddle==3.0.0.dev20250427 `
  -i https://www.paddlepaddle.org.cn/packages/nightly/cpu/

$source = ".work\pdf-to-post\cache\paddle\paddlex\official_models"
$target = ".work\pdf-to-post\cache\openvino\models"
New-Item -ItemType Directory -Force $target | Out-Null

& "$converter\paddle2onnx" `
  --model_dir "$source\PP-OCRv5_server_det" `
  --model_filename inference.json --params_filename inference.pdiparams `
  --save_file "$target\PP-OCRv5_server_det.onnx" `
  --opset_version 11 --enable_onnx_checker True --optimize_tool None

& "$converter\paddle2onnx" `
  --model_dir "$source\korean_PP-OCRv5_mobile_rec" `
  --model_filename inference.json --params_filename inference.pdiparams `
  --save_file "$target\korean_PP-OCRv5_mobile_rec.onnx" `
  --opset_version 11 --enable_onnx_checker True --optimize_tool None
```

실행 시 Intel GPU를 감지하지 못하거나 GPU·CPU 배치와 FP32 강제가 적용되지 않으면
오류를 반환합니다.

## Paddle 텍스트와 Docling 구조 병합

두 엔진의 최종 Markdown을 직접 합치지 않고 좌표가 포함된 공통 중간 형식을 먼저
생성합니다. Paddle 환경은 OCR 텍스트·신뢰도·좌표를, Docling 환경은 제목·목록·표
셀·코드·이미지 구조를 추출합니다.

`--pages`를 생략하면 문서 전체를 품질 검사합니다. OCR 필요 페이지가 요청 범위의
80% 이상이면 전체 범위를 PaddleOCR로 처리하고, 그보다 적으면 문제 페이지만
OCR합니다. 정상 페이지는 Docling이 PDF 텍스트 계층에서 추출한 내용을 사용합니다.
Docling 내부 OCR는 중복 인식을 피하기 위해 비활성화됩니다. `--pages 4,19,24`처럼
명시하면 해당 범위 안에서만 같은 정책을 적용합니다.

```powershell
$pdf = "lecture-pdfs\lecture.pdf"

.work\pdf-to-post\venvs\openvino\Scripts\pdf-to-post `
  hybrid-extract $pdf --engine paddle

C:\Temp\pdf-to-post-docling\Scripts\pdf-to-post `
  hybrid-extract $pdf --engine docling

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
