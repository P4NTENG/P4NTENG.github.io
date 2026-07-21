---
layout: page
title: Markdown hint
---

<p class="message">
  Markdown 문서를 작성할 때 활용할 서식 태그 정리
</p>

# 강조 및 하이라이트 태그
- `<mark>`: 텍스트 형광펜 효과

중요한 키워드나 강조하고 싶은 부분에 노란색 형광펜을 칠한 효과를 준다.  
`이 부분은 <mark>중요한 개념</mark>입니다.`  
이 부분은 <mark>중요한 개념</mark>입니다.  

- `<sub>` / `<sup>`: 아래 첨자 / 위 첨자

화학식, 수학 공식, 단위, 주석 번호 등을 깔끔하게 표현할 때 유용하다.  
`물 공식: H<sub>2</sub>O | 제곱: 10<sup>2</sup> = 100`  
물 공식: H<sub>2</sub>O | 제곱: 10<sup>2</sup> = 100  

- `<kbd>`: 키보드 단축키 스타일

키보드 자판 모양의 회색 박스를 만들어 준다.  
`저장하려면 <kbd>Ctrl</kbd> + <kbd>S</kbd>를 누르세요.`  
저장하려면 <kbd>Ctrl</kbd> + <kbd>S</kbd>를 누르세요.  

# 레이아웃 및 영역 구분 태그

- `<hr>`: 구분선(Horizontal Rule)

마크다운의 ---과 같지만, 인라인 스타일을 더해 색상이나 두께를 바꿀 수 있다.  
`<hr style="border: 2px solid #3b82f6; margin: 20px 0;">`  
<hr style="border: 2px solid #3b82f6; margin: 20px 0;">

- `<fieldset>` & `<legend>`: 테두리 박스와 제목

관련 내용을 네모 상자로 감싸고 상단 테두리에 박스 제목을 배치.  

```
<fieldset>
  <legend>💡 참고 사항</legend>
  이 박스는 관련된 중요 정보를 하나로 묶어 보여줄 때 유용합니다.
</fieldset>
```

<fieldset>
  <legend>💡 참고 사항</legend>
  이 박스는 관련된 중요 정보를 하나로 묶어 보여줄 때 유용합니다.
</fieldset>

# 인라인 스타일을 활용한 알림(Alert) 박스

- `<div>`에 간단한 CSS 스타일을 적용하여 노션(Notion)의 콜아웃 박스 같은 서식 만들기.  

```
<!-- 안내 박스 -->
<div style="background-color: #e0f2fe; border-left: 5px solid #0284c7; padding: 12px; margin: 10px 0; border-radius: 4px;">
  ℹ️ <strong>안내:</strong> 이 작업은 완료하는 데 약 5분이 소요됩니다.
</div>

<!-- 경고 박스 -->
<div style="background-color: #fee2e2; border-left: 5px solid #dc2626; padding: 12px; margin: 10px 0; border-radius: 4px;">
  ⚠️ <strong>주의:</strong> 데이터를 삭제하면 복구할 수 없습니다.
</div>
```

<!-- 안내 박스 -->
<div style="background-color: #e0f2fe; border-left: 5px solid #0284c7; padding: 12px; margin: 10px 0; border-radius: 4px;">
  ℹ️ <strong>안내:</strong> 이 작업은 완료하는 데 약 5분이 소요됩니다.
</div>

<!-- 경고 박스 -->
<div style="background-color: #fee2e2; border-left: 5px solid #dc2626; padding: 12px; margin: 10px 0; border-radius: 4px;">
  ⚠️ <strong>주의:</strong> 데이터를 삭제하면 복구할 수 없습니다.
</div>

# 텍스트 정렬 및 레이아웃

- HTML을 사용하여 텍스트 중앙/우측 정렬

```
<!-- 중앙 정렬 -->
<p align="center">
  <img src="https://via.placeholder.com/150" alt="이미지"><br>
  <sub>그림 1. 이미지 중앙 정렬 및 캡션</sub>
</p>
```

<!-- 중앙 정렬 -->
<p align="center">
  <img src="https://via.placeholder.com/150" alt="이미지"><br>
  <sub>그림 1. 이미지 중앙 정렬 및 캡션</sub>
</p>