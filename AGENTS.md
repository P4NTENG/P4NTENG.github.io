# AGENTS.md

## 1. Core Operating Principles (Andrej Karpathy Guidelines)

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.


## 프로젝트 목적

이 저장소는 두 가지 목적을 가진다.

1. Jekyll 기반 TIL 블로그를 운영한다.
2. 강의자료 PDF를 검수 가능한 블로그 초안으로 변환하는 `pdf-to-post` 도구를 개발한다.

자동화의 우선순위는 처리 속도보다 원문 충실도, 추적 가능성, 게시 전 사람 검수다. 생성된 초안을 자동으로 게시하거나 원문에 없는 내용을 추가하지 않는다.

### 주요 디렉터리 책임

- `_posts/`: 사람이 검수하고 게시를 승인한 글만 둔다.
- `_drafts/`: 자동 생성되었거나 검수 중인 글을 둔다.
- `assets/img/posts/<slug>/`: 게시물별 이미지와 그림을 둔다.
- `lecture-pdfs/`: 로컬 원본 PDF를 둔다. Git에 원본 PDF를 추가하지 않는다.
- `.work/pdf-to-post/`: 추출 텍스트, 페이지 렌더링, 진단 자료 등 재생성 가능한 중간 산출물을 둔다.
- `tools/pdf_to_post/`: PDF 변환 CLI, 설정, 프롬프트와 테스트를 둔다.
- `_site/`, `.jekyll-cache/`, `.venv/`: 생성 산출물이므로 직접 편집하거나 커밋하지 않는다.

### 콘텐츠 규칙

- 게시 파일명은 `_posts/YYYY-MM-DD-slug.md` 형식을 따른다.
- 초안 파일명은 `_drafts/slug.md` 형식을 따른다.
- Jekyll front matter에는 최소한 `layout: post`와 비어 있지 않은 `title`이 있어야 한다.
- 수식이 있는 글만 `use_math: true`를 사용한다.
- 게시물 이미지는 가능하면 `/assets/img/posts/<slug>/...` 절대 경로로 참조한다.
- 기본 작성 언어는 한국어이며, 기술 용어는 의미가 분명할 때 영문을 병기한다.
- 자동 생성 문서에는 원본 페이지를 추적할 수 있는 정보를 검수 완료 전까지 유지한다.
- 원본 PDF의 저작권 안내, 개인정보, 비밀정보를 그대로 공개하지 않는다.

### PDF 변환 방향

변환 파이프라인은 다음 단계를 분리한다.

1. 입력 파일과 메타데이터 검증
2. 텍스트, 레이아웃, 이미지 추출
3. 텍스트 계층 품질 검사와 필요한 페이지의 OCR 대체
4. 반복 머리글, 바닥글, 페이지 번호와 인코딩 오류 정리
5. 제목, 문단, 목록, 표 등 문서 구조 복원
6. 블로그 글 형태로 재구성
7. Jekyll Markdown 렌더링과 자동 검증
8. 사람의 원문 대조 및 게시 승인

PDF 화면이 정상이어도 내부 `ToUnicode` 매핑이 잘못될 수 있다. 호환용 Unicode 문자, 사설 영역 문자, 대체 문자, 비정상적으로 사라진 공백 등을 검사하고 품질이 낮은 페이지는 일반 텍스트 추출 결과를 신뢰하지 않는다.

문자 치환은 근거가 명확한 경우에만 사용한다. 문맥 복원이나 LLM 단계가 원문에 없는 사실, 예제, 결론을 만들면 안 된다. 불확실한 부분은 숨기지 말고 검수 경고와 원본 페이지 번호를 남긴다.

현재 최소 버전은 텍스트형 PDF의 평문 추출과 초안 검증까지만 지원한다. 다음 개발 우선순위는 추출 품질 판정, 한국어·영어 OCR fallback, 레이아웃 기반 구조 복원, 블로그 글 재구성 순서다.

### Python 구현 규칙

- Python 3.11 이상을 기준으로 한다.
- 공개 함수에는 타입 힌트를 사용하고, 경로는 `pathlib.Path`로 다룬다.
- 설정과 결과처럼 구조가 명확한 값은 dataclass 등 명시적인 자료형으로 표현한다.
- CLI 오류는 사용자가 조치할 수 있는 한국어 메시지와 0이 아닌 종료 코드로 반환한다.
- 의존성은 `tools/pdf_to_post/pyproject.toml`에 선언한다.
- 원본 PDF는 수정하지 않고 중간 산출물은 `.work/pdf-to-post/`에 저장한다.
- 사용자 파일을 기본적으로 덮어쓰지 않는다. 명시적인 `--force` 같은 선택이 있을 때만 덮어쓴다.
- 저장소 밖으로 출력 경로가 벗어나지 않도록 검증한다.
- 생성하는 Markdown은 BOM 없는 UTF-8과 LF 줄바꿈을 사용한다.

### 작업 범위와 안전성

- 요청과 무관한 테마, 레이아웃, 게시물 내용은 변경하지 않는다.
- 기존 작업 트리의 사용자 변경사항을 보존한다.
- `_drafts`의 결과를 `_posts`로 이동하거나 게시하는 작업은 사용자의 명시적 요청이 있을 때만 수행한다.
- 원본 강의자료나 대용량 테스트 파일을 커밋하지 않는다. 자동 테스트는 작고 재현 가능한 fixture를 사용한다.
- API 키와 개인 설정은 환경 변수로 받고 저장소에 기록하지 않는다.
- 자동 게시보다 초안 생성과 검수 보고서 생성을 우선한다.

## 검증 명령

Python 변경 후 저장소 루트에서 실행한다.

```powershell
.venv\Scripts\python -m unittest discover -s tools\pdf_to_post\tests -v
```

CLI 동작과 대상 Markdown을 확인한다.

```powershell
.venv\Scripts\pdf-to-post --help
.venv\Scripts\pdf-to-post validate _drafts\<slug>.md --site-root .
```

Jekyll 관련 변경이나 생성 결과가 있으면 전체 사이트를 빌드한다.

```powershell
bundle exec jekyll build --trace
```

### 완료 기준

- 요청한 동작이 구현되고 사용법이 문서화되어 있다.
- 관련 자동 테스트가 통과한다.
- Jekyll 빌드가 성공한다.
- 원본 PDF와 사용자 작성물을 손상시키지 않는다.
- 자동 생성 결과의 누락, OCR 필요 페이지, 불확실한 변환을 사용자에게 명확히 알린다.
- 의도하지 않은 파일이 `_site/` 또는 Git 변경사항에 포함되지 않는다.
