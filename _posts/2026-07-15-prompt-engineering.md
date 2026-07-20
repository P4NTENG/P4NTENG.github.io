---
layout: post
title: Prompt 설계와 Context Engineering
---

#### Token

텍스트 처리의 기본 단위
- 정의
    - 텍스트를 구성하는 조각을 의미
    - 이 조각은 보통 단어를 나타내는데, 단어의 일부, 공백이나 구두점까지 포함될 수 있음
    - Tokenizer를 이용해 subword로 분해함

#### LLM의 작동방식

- 순차적인 텍스트를 입력으로 받아, 훈련된 데이를 기반으로 다음 토큰이 무엇이야 하는지 예측
- Given sequence로 next token을 auto-regressive 방식으로 예측

#### Prompt Engineering이란?

- LLM이 정확한 결과를 생성하도록 안내하는 고품질 프롬프트를 설계하는 과정
- 이 과정에는 최적의 프롬프트를 찾기 위한 수정, 프롬프트 길이 최적화, 프롬프트의 글쓰기 스타일을 지정하는 작업이 포함됨
- 자연어 처리와 LLM의 맥락에서 프롬프트는 응답이나 예측을 생성하기 위해 모델에게 제공되는 입력임

#### LLM 출력의 다양성 조정


### Prompt Engineering 실습

RICE??
Role
In
