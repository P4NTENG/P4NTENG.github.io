---
layout: post
title: LLM과 Transformer 아키텍처
use_math: true
---

## Software 3.0

### 개발 방식의 진화

<ins>Software 1.0</ins>: 사람이 규칙을 코드로 직접 작성

- 프로그래머가 Python, C++, JS, CSS 등의 언어로 작성
- 컴파일러/인터프리터에 대한 명시적(선언적 또는 명령적) 명령으로 구성
- 프로그래머는 각 코드/ 명령어 줄을 작성함으로써 프로그램 내에서 원하는 동작을 수행
- 인간이 만든 소스 코드(예: 일부. cpp 파일)가 가치 있는 작업을 수행하는 바이너리 파일로 컴파일

<ins>Software 2.0</ins>: 사람이 데이터를 주고 모델을 학습

- 신경망의 가중치처럼 훨씬 더 추상적이고 인간 친화적이지 않은 언어로 작성
- 일반적인 신경망은 수백만 개의 가중치를 가질 수 있음
- 가중치가 매우 많기 때문에 이 코드 작성에는 인간이 관여하지 않음
- 소스 코드는 대부분 1) 비즈니스 로직, 데이터 전처리 등의 S/W 1.0 코드, 2) 데이터와의 상호작용, 3) 신경망(NN) 아키텍처, 4) 신경망을 컴파일 하기 위한 코드로 구성

**한계**: 모든 문제마다 모델을 새로 만들어야 하기 때문에 Task마다 AI 모델이 필요함

> Transformer의 등장으로 Task-specific AI에서 General-purpose AI로 패러다임 전환

<ins>Software 3.0</ins>: 사람이 목표를 정의하면 모델이 스스로 사고하고 행동

- 소프트웨어 3.0에서는 프로그래머가 프로그램의 원하는 동작을 정의하는 일련의 명령어와 데이터 셋을 제공
- AI agent가 이러한 명령어와 데이터 세트를 기반으로 프로그램을 생성
- 생성 과정에는 AI agent가 코드를 생성하고 신경망 모델을 학습하는 과정이 포함될 수 있음
- 필요한 부분을 AI agent에 의해 부분적으로 또는 완전히 생성

Program space

- 세상에 존재할 수 있는 모든 프로그램의 집합
- SW 3.0의 표현력은 SW 1.0과 SW 2.0 프로그램을 포함

즉, SW 3.0은

- 프로그램을 더 잘 만드는 기술이 아니라, 하나의 거대한 모델이 대부분의 프로그램 공간을 포괄하도록 만든 패러다임의 변화
- 이미 존재하는 거대한 Program Space에서 Prompt를 통해 원하는 프로그램을 즉시 끌어내는 방식으로 진화


<fieldset>
  <legend>Software 1.0</legend>
  <ul>
    <li>전체 애플리케이션의 상당 부분을 프로그래머가 수동으로 작성</li>
    <li>대부분의 논리와 코드는 최적화 프로세스 중에 기계에 의해 제안되지 않음</li>
  </ul>
</fieldset>
<fieldset>
  <legend>Software 2.0</legend>
  <ul>
    <li>전체 애플리케이션의 상당 부분을 프로그래머가 수동으로 작성</li>
    <li>대부분의 논리와 코드는 최적화 프로세스 중에 기계에 의해 제안되지 않음</li>
  </ul>
</fieldset>
<fieldset>
  <legend>Software 3.0</legend>
  <ul>
    <li>전체 애플리케이션의 상당 부분을 프로그래머가 수동으로 작성</li>
    <li>대부분의 논리와 코드는 최적화 프로세스 중에 기계에 의해 제안되지 않음</li>
  </ul>
</fieldset>
<br/>

Traditional S/W의
- 코드
- 함수
- 프로그램

에서  
Software 3.0은
- 자연어
- 프롬프트
- 모델 + 컨텍스트

로 옮겨감

> 이제 소프트웨어의 인터페이스는 API가 아니라 언어(Language)다


<ins>Key message</ins>
- 개발자는 코드 작성자에서 문제 장의자 혹은 사고 설계자로 역할 변화
- 소프트웨어는 더 이상 컴파일 하지 않고 대화, 지시로만 실행 가능할지도 모름


**LLM의 역할**  
- 단순한 AI가 아니라 사고를 실행하는 플랫폼
- 추론엔진, 지식 인터페이스, 자연어 컴파일러, 에이전트의 두뇌 등...

**LLM의 한계**
- Black Box: 수십억 개의 파라미터가 어떻게 특정 답변을 내놓았는지 설명하기 어려움. 잘못된 결과가 나왔을 때 원인을 추적하기 쉽지 않음
- Bias: LLM은 웹 수집 데이터를 바탕으로 데이터 편향, 문화적 편향, 오래된 정보, 잘못된 정보까지 함께 학습. Prompt를 아무리 잘 작성해도 근본적인 편향은 완전히 제거되지 않음, silently fail
- Hallucination: 확률이 가장 높은 토큰을 내놓는 LLM의 특성상 존재하지 않는 논문, 잘못된 수치, 틀린 코드를 매우 자연스럽게 생성할 수 있음
- Non-deterministic: 같은 Prompt, 동일한 입력에도 조금씩 다른 결과로 항상 동일한 프로그램처럼 동작하지 않음

**증강 지능, Augmented Intelligence**
- 증강 지능은 AI가 인간을 대체하는 기술이 아니라, 인간의 능력을 확장하고 보완하는 기술로 보는 개념
- AI가 인간의 지식, 경험, 판단, 의사결정을 지원하여 더 나은 성과를 내도록 하는 협업 중심의 AI 활용 방식

---

## NLP Technical Summary

### 언어 이해의 시작

사람이 사용하는 언어를 Machine이 어떻게 이해할 수 있을까?  
#### Machine이 이해할 수 있는 언어의 형식
- 언어를 Machine이 이해하려면 수치로 변환해야 함
- 어떻게 수치로 변환할 수 있을까?
- 수집하여 가지고 있는 모든 단어들 → Corpus
- NLP Task를 위해 Corpus로부터 뽑은 단어들 → Vocabulary

#### Bit를 활용해 연속형 수치(Vector)로 변환
- 모든 단어에 Indexing 하는 것과 유사
- 이진법을 활용해서 N * 1의 column vector으로 표현 → One-hot vector

#### 단어의 빈도를 활용한 문장 표현
- 문장을 단어의 빈도수 롤 표현한 것이 BoW(Bag of Words) vector
- 각 단어가 몇 번 사용되었는지는 알 수 있지만, 사용된 단어의 순서는 알 수 없음

#### N-Gram: 순서를 고려
- 연속된 n 개의 단어 뭉치
- 순서 정보를 일부 보존하여 국소적 의미를 알 수 있음
- bi-gram(n=2)을 만든다면 데이터 속 순차적인 모든 단어 pair를 vocab에 넣어야 함
- n이 커질수록 너무 많은 단어 쌍이 생김

#### TF-IDF: 중요한 단어 고려
- Term Frequency - Inverse Document Frequency
- Term Frequency: 많이 출현하는 단어가 중요
- Inverse Document Frequency: 다른 문서에도 자주 출현하는 단어는 중요도가 떨어짐

<center>
$TF(t, d) = \frac{Number\ of\ occurrences\ of\ term\ t\ in\ document\ d}{Total\ number\ of\ terms\ in\ the\ document\ d}$<br/><br/>
$IDF(t, D) = \frac{Total\ number\ of\ documents\ in\ the\ corpus}{Number\ of\ documents\ with\ term\ t\ in\ them}$<br/><br/>
$TF-IDF(t, d, D) = TF(t, d)\times IDF(t, D)$  
</center>

#### 빈도 기반 언어 표현의 한계
- 순서가 중요하지 않은 Task(Topic classification, 문서 검색 등)에서는 강점을 가짐
- 단어 나열의 순서가 중요한 Task에서는 활용이 어려움
- 사용되는 Corpus의 크기가 커질수록 vector size는 매우 커짐 → 차원의 저주(Curse of Dimensionality)
- 단어 간의 관계 표현에 취약, 즉 의미를 알 수 없음


### 맥락의 이해

모든 단어들의 관계를 사람이 직접 정의할 수 있을까?

#### 직접적인 시도

<ins>Thesaurus</ins>
- 단어의 의미를 정의하여 저장하고 있는 사전
- 기본적으로 동의어 또는 유의어가 한 그룹으로 분류되어 있음
- 단어 간 다양한 관계를 그래프 구조로 정의함

<ins>WordNet</ins>
- 프린스턴 대학교에서 1985년부터 구축하기 시작한 Thesaurus
- 표제어를 통해 특정 단어가 갖는 다양한 의미 표현(하나의 의미 그룹에 여러 단어가 포함)
- Synset(동의어 집합), Hypernym(상위의), Hyponym(하위여), Meronym(부분 관계) 등을 그래프로 연결
- 단어 네트워크를 사용하여 유의어를 찾거나 단어 간 유사도를 구할 수 있음
- 신조어 또는 의미가 변하는 어휘에 대응하기 어려움
- Thesaurus 구축에 비용이 많이 듦

> 세상의 모든 단어를 직접 정의하는 것은 불가능

#### 맥락을 이해한다는 것
<ins>분포 가설(Distributional hypothesis)</ins>
- 단어의 의미는 그 단어가 나타나는 문맥에 의해 정의된다
- 즉, 비슷한 문맥에서 쓰이는 단어들은 의미도 비슷하다
- 언어학적으로 단어의 의미를 그 분포, 즉 주변 문맥을 기반으로 분석할 수 있음을 시사

의미적 추론을 가능하게 한 워드 임베딩  
Deep Learning을 통한 분포 가설의 구현, Word2Vec  
<ins>Word2Vec 학습 과정</ins>
- 함께 출연한 단어로 이루어진 Train Data를 구성한 후 주변 단어와 타깃 단어 간의 분류 문제로 정의한 후 학습
- Neural Network를 통해 학습이 진행될수록 주변 단어들과의 관계가 임베딩 공간에 투영됨

단어 간의 관계는 수많은 문장 읽기를 통해 형성됨

### What is LM(Language Model)?

LM은 가장 자연스러운 단어 시퀀스를 찾아내는 모델
- 가장 자연스러운 단어 시퀀스를 찾아낸다 = 단어 시퀀스에 확률을 할당한다
- 어떤 문장(단어 시퀀스)이 주어졌을 때, 얼마나 그럴듯하냐를 확률적으로 나타내거나 문장의 앞부분이 주어졌을 때 다음 단어를 예측할 수 있음

<ins>다음 단어를 예측하는 방법</ins>
- 앞에 어떤 단어들이 나왔는지를 고려하여 후보가 될 수 있는 여러 단어들에 대하여 등장 확률을 추정하고 가장 높은 호감률을 가진 단어를 선택
- 등장 확률은 가지고 있는 데이터로부터 계산할 수 있음. 마치 사람이 지속적으로 읽고 듣는 것을 통해서 언어를 배우는 것과 유사

#### RNN(Recurrent Neural Network)

현재와 과거의 의존성을 모델링

- 글을 읽고 맥락을 파악하는 행위는 한 단어씩 순차적으로 보고 이해하는 것
- RNN은 앞선 단어의 기록을 hidden state(h)를 통해 기억하고 있고, 이를 현재의 예측에 활용
- hidden state(h)는 input들 간의 의존성을 저장하는 메모리

문제점

- Neural Network의 학습과정에서 기울기가 점점 작아져 앞 시점이 거의 학습되지 않는 현상(Vanishing gradient)
- 과거 정보가 현재까지 전달되지 않아 시계열이 길수록 장기 의존성(long-term dependency) 학습에 실패함

#### 장기 의존성 소실 문제를 해결하기 위한 후속 연구

LSTM(Long Short-Term Memory)
- 모델 안의 여러 개의 gate를 추가하여 input, output, memory 간 흐르는 정보를 보다 섬세하게 제어
- RNN보다 구조가 복잡하고 더 많은 연산 비용이 필요

GRU(Gated Recurrent Unit)
- LSTM과 유사한 성능을 유지하면서 연산 비용을 경량화

#### 전체 맥락을 하나로 압축하여 전달
Sequence-to-Sequence Based LM
- Encoder의 전체 단어의 맥락을 가지고 있는 Hidden state vector(Context vector)를 Decoder로 전달함
- Decoder에서는 Input과 Encoder의 Context vector를 고려하여 출력
- 입력 Sequence가 길어지면, 출력 Sequence의 정확도가 떨어짐 → 너무 많은 단어가 하나의 sentence vector로 압축되어 정보가 소실

#### Attention
장기 의존성 문제, 병렬처리 문제의 한계를 극복한 메커니즘  
순서의 파괴, 전체를 조망하는 Attention Based LM, Transformer
- Decoder에서 단어 출력 시마다 매 시점 Encoder의 전체 입력 문장을 다시 봄
- 입력 Sequence를 하나로 압축한 context vector를 보지 않고, 매 시점 Encoder의 hidden state를 전부 참고
- 지금 출력하고 있는 단어에 따라 살펴봐야 할 단어들은 다르다
- 각 단어가 출력할 때 도움이 되는 정도를 Scoring 하여 함께 전달(Attention Score)
- Attention 기반의 병렬처리가 가능한 생성 모델 구조인 Transformer는 대규모 사전 학습 모델(LLM)의 시대를 엶

#### Word Embedding의 한계
- Word2Vec, GloVe 같은 워드 임베딩은 "한 단어 = 하나의 고정 벡터", 즉 고정 임베딩
- 동음이의어 구분 불가: "배" = 과일/선박/신체 → 항상 같은 벡터
- 다의어 표현 불가 → 하나의 벡터에 섞임
- 문맥 변화 반영 불가

<ins>반면 Transformer는...</ins>
- 같은 단어라도 문맥에 따라 다른 벡터를 생성, 보다 정교한 Context를 내포

### 전이 학습(Transfer Learning)
- 딥러닝 모델이 스스로 풀기 위한 최종 문제를 위해 중간 단계의 개념들을 구조화하는 것 (Representative learning)
- 풀어야 할 문제가 유사한 중간 단계의 개념들을 미리 구조화해둠
- 이렇게 유사한 데이터로 미리 학습된 모델을 Pretrained Model이라 함
- 사전에 학습된 Pretrained Model을 바탕으로 최종 문제를 풀어내는 접근 = Transfer learning

### GPT(Generative Pretrained Transformer)
- Transformer는 기존 모델과는 다르게 분산 컴퓨팅을 가능하게 한다는 점에서 큰 의미가 있음
- 그 결과 GPT-2, 3 같은 큰 모델이 나올 수 있었음
- GPT가 다른 모델보다 월등하게 좋은 성능을 보이는 가장 큰 이유는 학습 데이터의 양에 있음

---

## Math Essentials for Transformer

### Distance

<ins>Similarity</ins>
- 두 객체는 얼마나 닮았는가? 유사한가?
- 0~1 사이의 값을 가짐, 서로 비슷할수록 값이 큼
- 0: No Similarity, 1: Completely Similar

<ins>Dissimilarity</ins>
- 두 객체는 얼마나 닮지 않았는가? 떨어져 있는가?
- 최솟값은 0, 서로 비슷하지 않을수록 값이 큼
- 0: No Distance

<ins>Similarity vs Distance</ins>
- 유사도와 거리는 닮음의 서로 다른 표현
- 1 - Similarity = Distance

#### Euclidean Distance

두 데이터 간의 직선거리

<ins>Concept</ins>
- 직관적이고 구현이 간단하기 때문에 가장 많이 사용되는 척도의 하나
- 벡터의 크기를 측정하는 것이 중요한 경우 효과적
- 각 차원의 차를 제곱해서 모두 더한 값의 제곱근, 피타고라스 정리

<center>
$d(i, j) = \sqrt{(x_{i1} - x_{j1})^2 + (x_{i2} - x_{j2})^2 + \cdots + (x_{in} - x_{jn})^2}$
</center>

### Inner Product

#### Cosine Similarity

각도 기반의 유사도 측정

<ins>산출 원리</ins>
- 코사인(cosine) 삼각함수를 이용
- 코사인은 2차원 평면에서 볼 때 한 지점에서 출발한 방향을 가진 두 값(벡터)의 길이에 대한 비율을 의미

<ins>Concept</ins>
- 두 벡터가 가리키는 방향이 얼마나 유사한지 측정 (벡터 크기 무관)
- 방향이 완전히 일치하면 1, 완전히 반대이면 -1
- 벡터의 모든 원소가 양수라면, 코사인 유사도의 최솟값은 0
- $1 - Cosine\ Similarity = Cosine\ Distance$

<ins>Calculation</ins>
- 내적의 결과를 총 벡터 크기로 정규화(L2 Normalization)

<center>
$similarity = cos(\Theta) = \frac{A\cdot B}{\Vert A \Vert \Vert B \Vert} = \frac{\sum_{i=1}^n A_i \times B_i}{\sqrt{\sum_{i=1}^n (A_i)^2} \times \sqrt{\sum_{i=1}^n (B_i)^2}}$
</center>

<ins>사용 이유?</ins>
- 유사도를 기준으로 거리를 사용한다면? → 벡터의 방향과 크기를 고려하는 것
- 유사도를 기준으로 코사인 값을 사용한다면? → 벡터의 방향만을 고려하는 것
- 코사인 유사도 → 문서의 길이가 다르기 때문에 벡터 간 거리를 벡터의 크기로 정규화 하여 사용 

#### Dot Product

내적의 의미

<ins>계산</ins>
- 두 벡터 a, b가 이루는 각이 $\theta$일 때 다음을 두 벡터 a, b의 내적이라 함

<center>
$\vec{a}\cdot \vec{b} = \vert \vec{a} \vert \vert \vec{b} \vert cos\theta = \sum\limits_{i=1}^d a_i b_i$
</center>

<ins>implicit meaning</ins>
- 벡터의 내적은 기하학적으로 한 벡터를 다른 벡터 위로 정사 영시 킨 길이와 그 다른 벡터의 길이를 곱한 것을 의미
- 크기와 방향을 모두 고려한 유사도 개념
- 정사영 된 길이가 짧다는 것 = 벡터 간 각도가 크다 = 유사도가 작다
- 정사영 된 길이가 길다는 것 = 벡터 간 각도가 작다 = 유사도가 크다


### Linear Transformation

#### Definition
- 선형변환은 벡터의 덧셈과 배수 관계를 유지하면서, 벡터를 다른 벡터로 매핑하는 함수
- 행렬 곱은 이러한 선형변환을 계산하는 방법
- 벡터를 회전, 확대, 축소, 반사하거나 다른 차원의 벡터로 바꾸되, 공간의 직선 성과 원점을 보존하는 변환

#### Weight Matrix를 행렬곱 하는 의미
- 딥러닝의 학습이란, Weight Matrix를 조금씩 수정하여 데이터가 의미 있는 위치에 놓이도록 벡터 공간을 계속 재배치하는 과정
- 단어가 변하는 게 아니라, 단어를 표현하는 벡터가 변하는 것

### Softmax function

Scores to Probabilities

#### Concept
- Softmax는 여러 실수 점수를 비교 가능한 확률 분포로 변환
- 각 점수가 전체에서 차지하는 상대적 비중을 계산
- 모든 출력값은 0과 1사이
- 출력값의 합은 1
- 입력값의 상대적인 크기 관계를 유지

<center>
$Softmax(z_i) = \frac{e^{z_i}}{\sum\limits_{j=1}^n e^{z_j}}$
</center>

---

## Transformer

### Attention Is All You Need

현대 Transformer 기반 모델(BERT, GPT 등)의 출발점

#### Motivation
- 2017년 Google Brain 팀에서 "Neural Machine Translation(NMT)" 프로젝트를 하던 연구자들에 의해 작성
- 당시 주류 기계번역 모델은 한계를 가지고 있었음
  - RNN/LSTM/GRU 기반 Seq2Seq 모델: 병렬화 어려움, 장기 의존성 문제
  - CNN 기반 모델: 멀리 떨어진 토큰 간 관계 위해 너무 많은 계층 필요

#### Proposal
- Transformer Architecture
- RNN이나 CNN 없이 Self-Attention 만으로 시퀀스를 처리

#### Result by the paper
- WMT 2014 English-German와 English-French 데이터를 통해 성과 측정
- English-German → BLEU 28.4
- English-French → BLEU 41.8
- 기존 모델들과 비교해 훨씬 적은 연산 비용으로 SOTA 달성

#### Contribution
- Self-Attention 만으로 이루어진 최초의 Seq2Seq 모델 제안
- RNN/CNN 의존 없이 병렬 학습 + 장기 의존성 처리 가능함을 ㄹ증명
- 이후 모든 대규모 언어 모델(BERT, GPT 등)의 기반 아키텍처가 됨

#### Transformer Architecture
- 인코더-디코더 구조
- Encoder: 입력 문장을 여러 층의 self-attention + feed forward network를 통해 벡터로 추출
- Decoder: 인코딩된 벡터와 자기 자신의 출력에 대한 masked self-attention을 통해 목표 문장을 생성

<p align="center">
  <img src="/assets/img/transformer-architecture.jpg">
</p>

**Encoder**  
Scaled Dot-Product Attention - Self Attention  
- Q와 Transpose된 K 간 matrix multiplication
- Score Matrix의 첫 row는 Q의 첫 번째 벡터와 K의 각 토큰 벡터가 매칭돼서 만들어짐 (Dot Product)
- 단어 간 문맥상 관계가 높을수록 큰 값
- (i, j) 셀 값의 의미: i 번째 토큰이 j 번째 토큰을 얼마나 주목하는지

Attention Score
- Q, K 벡터 차원($d_k$)이 커질수록 내적 값의 분산이 커져서 softmax 함수의 기울기(gradient)가 매우 작아지는 문제를 해소하기 위해 K 차원 수의 제곱근으로 나누어 줌. 일종의 scaling
- 이후 softmax를 통해 확률화를 진행
- 이로써 내적값의 크기 범위가 안정화되고, softmax가 적당한 기울기를 유지

Attention Output
- 토큰간 연관성(유사도)를 담고있는 Attention Score Matrix는 각 토큰이 다른 토큰을 얼마나 주목해야 하는지에 대한 가중치 행렬
- 이에 실제 정보(V)를 행렬곱하여 문맥 벡터를 생성
- 각 토큰이 다른 토큰들의 정보를 비율대로 섞어 만든 새 표현

<center>
$Attention(Q,K,V) = Softmax(\frac{QK^T}{\sqrt{d_k}})V$
</center>

Multi-head Attention
- 입력 시퀀스를 서로 다른 관점에서 Attention
- 여러 관점을 합쳐서 다시 하나의 통합 표현으로 만들기

> 다양한 관점인 이유는 각 head가 random initialize 되었기 때문

> 만약 같은 값으로 초기화 되었다면 다양한 관점의 효과를 보지 못할 것

<ins>Why linear layer?</ins>
- Concatenated vector는 헤드별 특징이 흩어져 있음
- 이를 재조합해서 모델이 사용하기 적절한 표현 공간으로 투영
- 다양한 관점의 정보를 통합하고, 차원을 맞추며, 다음 레이어가 쓸 수 있는 형태로 재배치하는 과정

Normalization
- LayerNorm은 각 토큰의 벡터 차원별 평균과 분산을 정규화해서, 입력 분포가 일정하게 유지되도록 도움
- 빠르고 안정적인 학습, 그래디언트 소실 방지

잔차 연결, Residual Connection
- 정보 보존: 어텐션이 계산한 값만 쓰면 원래 입력 정보가 손실될 수 있음
- 기존 정보 위에 어텐션이 계산한 추가적인 관계 정보를 보강하는 방식
- 입력을 그대로 출력에 더해줌으로써 Gradient 소실 문제를 방지하고 학습이 안정화됨

<center>
$Output = LayerNorm(Input + MultiHeadAttention(Input))$
</center>

Feed Forward
- Attention은 거의 선형변환의 조합이므로, 모델 표현력이 부족할 수 있음
- 문맥이 반영된 벡터 표현을 더 풍부하게 하기 위해 비선형성 추가(ReLU, Sigmoid 등)

Positional Encoding
<ins>Problem</ins>
- Transformer는 '모든 토큰을 함께 보는 컨셉' → 토큰 간의 순서를 직접 알 수 없음
- Query, Key, Value로 이루어진 어텐션 구조 자체가 토큰의 순서와는 상관없이 모두 연결되어 있어 추가적 정보없이 두 문장의 차이 구분이 어려움
<ins>Solution</ins>
- Positional Embedding Layer 학습
- 학습 없이 삼각함수를 활용, 정해잔 계산식에 따라 결과값을 인코딩 값으로 사용

**Decoder**  
어텐션 메커니즘은 모든 단어들이 나와 있을 때 서로간의 문맥을 파악하는 것이지 그 주어진 문장 그 다음에 토큰을 예상하기 위한 구조는 아님

Masked Self Attention
- 주어진 토큰들 사이의 문맥을 학습하여 다음 토큰 예측
- Training step마다 Attention Score와 Ground Truth와 비교하여 Loss 계산
