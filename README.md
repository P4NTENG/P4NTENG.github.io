# 디렉터리 구조

```
P4NTENG.github.io/
├─ _posts/                         # 검수 완료된 게시물
├─ _drafts/                        # 자동 생성된 검수 대기 초안
├─ assets/
│  └─ img/
│     └─ posts/
│        └─ <slug>/                # 게시물별 그림·슬라이드 이미지
│
├─ tools/
│  └─ pdf_to_post/
│     ├─ pyproject.toml            # Python 의존성 및 실행 명령
│     ├─ config.yml                # 공통 변환 설정
│     ├─ src/
│     │  └─ pdf_to_post/
│     │     ├─ cli.py              # 명령행 인터페이스
│     │     ├─ pipeline.py         # 전체 변환 순서
│     │     ├─ extract.py          # PDF 텍스트·이미지 추출
│     │     ├─ ocr.py              # 스캔 문서 OCR
│     │     ├─ normalize.py        # 머리글·줄바꿈 등 정리
│     │     ├─ compose.py          # 블로그 포스트 형태로 재구성
│     │     ├─ render.py           # Jekyll Markdown 생성
│     │     └─ validate.py         # 결과 검증
│     ├─ prompts/
│     │  ├─ compose.md             # 글 작성 규칙
│     │  └─ review.md              # 누락·왜곡 검사 규칙
│     └─ tests/
│        └─ fixtures/              # 테스트용 소형 PDF
│
├─ lecture-pdfs/                   # 원본 PDF, Git 제외
├─ .work/
│  └─ pdf-to-post/                 # 추출 결과·페이지별 중간 자료
└─ .github/workflows/
   └─ validate-posts.yml           # Jekyll 빌드와 링크 검증
```