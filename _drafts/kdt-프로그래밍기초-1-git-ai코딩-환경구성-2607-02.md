---
layout: "post"
title: "KDT 프로그래밍기초_1.Git&AI코딩&환경구성-2607_02"
---

> 이 글은 `KDT 프로그래밍기초_1.Git&AI코딩&환경구성-2607_02.pdf`에서 자동 생성된 초안입니다. 원문과 대조하여 검수하세요.

## 강의 내용

<!-- source-page: 1 -->

KDT 프로그래밍기초
1. 개발환경설정㏙Git 㖈 AI 코딩맛보기㏚
 ㎿맥북장비대상

2026.07

본문서는SK AX의컨텐츠자산으로, 무단사용및불법배포시법적조치를받을수있습니다.

<!-- source-page: 2 -->

1.  IT 용어

2. 기본개념이해

3. 개발환경구성

4. IDE 환경설정

5. AI 코딩맛보기

<!-- source-page: 3 -->

IT 용어

본문서는SK AX의컨텐츠자산으로, 무단사용및불법배포시법적조치를받을수있습니다.

<!-- source-page: 4 -->

IT 용어
UI/UX 기획용어

  §  Wireframe: 화면의뼈대㏙구조㏚에만집중한설계도㎿색상, 폰트, 이미지등모든시각적요소를의도적으로배제

  §  Mock㎿up: 시각적요소를완성한정적인디자인시안㎿와이어프레임위에색상, 타이포그래피, 이미지, 아이콘등
   실제디자인을입힌것

  §  Prototype: 사용자흐름을검증하기위한동적인시제품㎿실제작동하는것처럼상호작용㏙Interaction㏚을연결
  §  Persona: 사용자모델㎿우리제품을사용할가상의, 그러나구체적인대표사용자
  §   UI: 사용자인터페이스㎿버튼, 아이콘, 레이아웃, 색상, 글꼴. 즉, 목업에서만든시각적디자인결과물

  §  UX: 사용자가제품을사용하며느끼는모든경험의총합
  §  Storyboard : 화면흐름을순서대로설명한문서
  §  Navigation : 사용자가서비스안에서이동하는방식
  §  Design System : 일관된UI 설계체계
  §  Information Architecture : 메뉴, 페이지, 콘텐츠의전체구조
  § GNB : Global Navigation Bar. 전체서비스공통상단메뉴
  §  LNB : Local Navigation Bar. 특정영역안에서사용하는세부메뉴

                                                                                                                                         4

<!-- source-page: 5 -->

IT 용어
서비스출시/관리

 §  MVP㏙Minimum Viable Product㏚ : 시장에먹힐지㑄검증㑄하기위한, 최소한의㑄핵심가치㑄를담은제품
 §  Release : 개발된기능이나수정사항을㑄버전㑄을붙여사용자에게공식적으로내보내는것

 §  Launch : 새로운서비스나제품을공식적으로공개하는것

 §  Go㎿Live : 실제운영환경에서서비스가시작되는시점
 §  Hotfix : 정규릴리즈절차를무시하고㑄즉시㑄 배포하는긴급버그수정
 §  Deployment : 개발된코드를서버나클라우드환경에배포하는작업
 §  Rollout : 기능이나서비스를단계적으로사용자에게공개하는방식

 §  Rolling Update : 서버를순차적으로업데이트해무중단배포하는방식

 §  Beta Release : 정식출시전테스트목적의공개버전
 §  Rollback : 새버전배포후심각한문제가생겼을때, 㑄직전의안정적인버전으로㑄 되돌리는조치
 §  Patch : 버그수정이나보안개선을위한작은업데이트
 §  Versioning : 서비스나API의버전을관리하는것

 §  Issue : 해결해야할모든㑄일감㑄을추적하고관리하는단위㏙티켓㏚

 §  Roadmap : 제품이나아갈방향을보여주는㑄전략적인상위레벨계획지도

                                                                                                                                         5

<!-- source-page: 6 -->

IT 용어
인프라, 시스템운영

 § 시스템인프라㎕서비스를운영하기위한서버, 네트워크, 스토리지, 보안, 운영환경전체
 §  Physical Server : 실제장비형태의물리서버
 §  Virtual Machine : 물리서버위에서가상화로생성한서버㏙클라우드환경㏚

 §  Bare Metal : 가상화없이물리서버를직접사용하는환경
 §  Data Center : 서버와네트워크장비를운영하는전산센터
 §  On㎿Premise : 기업내부또는자체데이터센터에서운영하는방식
 §  서버다운㏙Server Down㏚㎕ 서버㏙또는프로그램㏚가비정상적으로멈춰서비스가불가능해진상태
 §  트래픽㏙Traffic㏚㎕ 일정시간동안네트워크를통해㑄오고가는데이터의총량㏙흐름㏚

 §  로깅㏙Logging㏚㎕ 시스템이작동하며발생하는모든㑄사건㏙이벤트㏚㑄을시간순서대로기록㏙Log㏚하는행위
 §  모니터링㏙Monitoring㏚㎕ 시스템이㑄현재㑄 정상적으로작동하는지실시간으로㑄지켜보고감시㑄하는행위
 §  백업㏙Backup㏚㎕ 데이터유실㏙사고, 실수㏚에대비해, 원본데이터를㑄별도의안전한장소㑄에복제해두는것
 §  복구㏙Restore㏚㎕ 데이터나시스템에문제가생겼을때, 㑄백업㑄해둔데이터를이용해특정시점으로되돌리는작업
 §  배치㏙Batch㏚㎕ 사용자와실시간상호작용없이, 대량의데이터를㑄한꺼번에모아㑄 정해진시간에자동처리하는작업

                                                                                                                                         6

<!-- source-page: 7 -->

IT 용어
애자일, 조직문화

 §  Agile : 계획에얽매이지않고, 㑄일단해보고피드백받아고치는㑄 방식의총집합㏙철학㏚
 §  Agile Framework : 애자일원칙을실제조직과프로젝트에적용하기위한실행체계입니다.
    즉, 㐱애자일하게일한다㐲는추상적인생각을역할, 회의, 산출물, 업무흐름, 의사결정방식으로구체화한

   방법론이며, Scrum, Kanban, XP 등이대표적인Agile Framework이다.
 §  Scrum : 애자일을실천하기위한, 정해진㑄규칙㏙경기룰㏚㑄이있는협업프레임워크
 §  Sprint Planning : 스프린트시작시목표와작업범위를정하는회의
 §  Sprint : 짧게정해진기간㏙1㚕4주㏚ 동안㑄완결된기능㑄을만들기위해전력질주하는주기
 §  Daily Scrum Meeting : 매일15분이내로㑄서서㑄 진행하며서로의㑄진행상황㑄과㑄걸림돌㑄을공유하는회의

 §  Product Backlog : 제품에필요한기능, 개선사항, 버그등을우선순위로정리한목록
 §  Sprint Backlog : 이번스프린트에서수행하기로선택한작업목록
 §  Sprint Review : 스프린트결과물을이해관계자와함께검토하는회의
 §  Definition of Done㏙DoD㏚ : 작업이완료되었다고판단하는기준
 §  Sprint Retrospective : 스프린트가끝난뒤, 㑄다음엔더잘하기위해㑄 팀이함께돌아보는회의

 §  Product Owner㏙PO㏚ : 제품방향, 요구사항, 우선순위를책임지는역할
 §  Scrum Master : 스크럼이잘운영되도록돕고장애물을제거하는역할
 §  Stakeholder : 제품에영향을주거나제품의영향을받는이해관계자
 §  킥오프㏙Kick㎿off㏚: 프로젝트㏙또는새스프린트㏚의시작을㑄공식선언㑄하고모두의방향성을맞추는첫회의

                                                                                                                                         7

<!-- source-page: 8 -->

IT 용어
트러블대응, 문제해결

§  트러블슈팅㏙Troubleshooting㏚: 발생한문제의㑄진짜원인㑄을찾아내기위한㑄체계적인탐정활동㐴

§  장애㏙Incident㏚: 사용자가서비스를㑄정상적으로못쓰게된㑄 모든비상사태
§  패치㏙Patch㏚: 일단급한불부터끄기위해, 특정버그나보안취약점만㑄땜질㑄하는작은수정코드

§  이슈트래킹㏙Issue Tracking㏚: 발생한모든㑄할일㏙이슈㏚㑄을등록하고, 㑄누가/언제까지/어떻게㑄 처리하는지전과정에대한
  추적관리
§  SLA㏙Service Level Agreement㏚: 만약우리서비스가이㑄최소보장품질㑄 밑으로떨어지면, 보상해드립니다.㑃라는

  㑄공식약속㏙계약㏚
§ 로그분석㏙Log Analysis㏚: 장애원인을찾기위해, 시스템이남긴㑄어마어마한양의기록㏙로그㏚㑄을뒤지는행위

§  유지보수㏙Maintenance㏚: 새로운기능개발은아니지만, 기존시스템이㑄죽지않고잘돌아가게㑄 계속돌보는모든활동

                                                                                                                                          8

<!-- source-page: 9 -->

IT 용어
클라우드용어

  §  Hybrid Cloud : 온프레미스와클라우드를함께사용하는구조

  §  Multi Cloud : AWS, Azure, GCP 등여러클라우드를함께사용하는구조
  §  Region : 클라우드데이터센터가위치한지리적지역

  §  Availability Zone㏙AZ㏚ : 하나의Region 안에있는독립적인데이터센터구역
  §  Edge Location : CDN, 캐싱, 보안처리등을위해사용자가까이에위치한거점
  §  CI/CD : 코드를커밋하는순간, 테스트부터배포까지알아서다해주는㐱자동화공장㐲 라인

  §  Container : 애플리케이션을실행하는데필요한것들을하나로묶어, 어느환경에서나동일하게실행할수있게
   만든격리된실행단위

  §  Docker : 그㐱컨테이너㐲라는상자를만들고, 배에싣고, 내리는일을해주는㐱사실상의표준도구㐲
  §  Kubernetes㏙k8s㏚: 여러개의컨테이너를자동으로배포하고, 실행하고, 확장하고, 복구해주는컨테이너
   오케스트레이션플랫폼

  §  클러스터㏙Cluster㏚: 여러대의컴퓨터를묶어서㑄하나의초강력컴퓨터㑄처럼쓰기위한팀
  §  Auto㎿scaling : 트래픽에따라서버자원을자동으로늘리고줄이는행위

  §  IaC ㏙Infrastructure as Code㏚: 서버와네트워크를㑄마우스클릭㑄이아닌㑄코딩㐴으로찍어내는기술

                                                                                                                                         9

<!-- source-page: 10 -->

IT 용어
개발용어

§  빌드㏙Build㏚: 소스코드를실행가능한소프트웨어로변환하는전체공정
§  배포㏙Deployment㏚: 빌드된결과물을사용자가접근가능한환경에가져다놓고실행하는행위
§  디버깅㏙Debugging㏚: 오류의원인㏙Bug㏚을찾아내고분석하여해결하는전과정

§ 테스트커버리지㏙Test Coverage㏚: 작성한테스트코드가실제프로덕션코드를얼마나실행했는지나타내는지표㏙㚠㏚

§  로직㏙Logic㏚: 애플리케이션의동작흐름을결정하는핵심규칙과조건, 계산식
§  파라미터㏙Parameter㏚: 함수를정의할때받아들일값을임시로담는변수명㏙자리표시자㏚
§  리턴값㏙Return Value㏚: 함수가모든작업을마친뒤, 자신을호출한곳으로돌려주는최종결과값

                                                                                                                                      10

<!-- source-page: 11 -->

IT 용어
GIT 협업용어

  §  레포㏙Repository㏚: 프로젝트의코드와㑄모든변경이력㐴을함께저장하는공간

  §  커밋㏙Commit㏚: 현재까지의변경사항을㑄하나의의미있는작업단위㑄로묶어이력에저장하는행위
  §  푸시㏙Push㏚: 내로컬레포에쌓인커밋들을㑄원격레포㏙GitHub㏚㑄로밀어올려공유하는것

  §  풀㏙Pull㏚: 원격레포의최신변경사항㏙다른팀원의커밋㏚을내로컬레포로㑄당겨와합치는㑄 것
  §  브랜치㏙Branch㏚: 기존코드㏙원본㏚에영향을주지않고㑄독립적으로㑄 작업을진행할수있는작업흐름
  §  머지㏙Merge㏚: 하나의브랜치에서완료된작업을다른브랜치로㑄합치는㑄 과정

  §  컨플릭트㏙Conflict㏚: 머지시, 두브랜치에서㑄같은파일의같은줄㑄을서로다르게수정했을때발생하는㑄충돌㑄
  §  Pull Request: 내가작업한브랜치를검토하고머지해달라고요청하는행위

                                                                                                                                      11

<!-- source-page: 12 -->

IT 기본개념

본문서는SK AX의컨텐츠자산으로, 무단사용및불법배포시법적조치를받을수있습니다.

<!-- source-page: 13 -->

IT 용어
프론트엔드㏙Frontend㏚

§ 사용자가실제로눈으로보고, 손으로조작하는웹화면을만드는영역
§ 사용자와직접맞닿는인터페이스㏙UI㏚ 와사용경험㏙UX㏚ 을설계하고구현하는일

         역할                             설명

  구조만들기㏙HTML㏚          웹페이지의뼈대㎿예: 제목, 단락, 버튼, 이미지위치등

  꾸미기㏙CSS㏚                 색깔, 글꼴, 여백, 애니메이션등디자인요소

  동작넣기㏙JavaScript㏚           클릭, 입력, 드래그등사용자행동에반응하도록기능을추가

 데이터불러오기㏙API 연동㏚       백엔드서버에데이터를요청하고, 받은정보를화면에노출

 사용자경험개선㏙UX㏚        더편리하고빠르게사용할수있도록화면흐름과반응을최적화

§ 프론트엔드에서자주쓰는기술

         구분                             예시

 기본언어                     HTML, CSS, JavaScript

 프레임워크/라이브러리               React, Vue.js ㏙더효율적으로화면개발㏚

 패키지관리자                   npm, yarn ㏙필요한라이브러리설치도구㏚

 빌드도구                      Webpack, Vite ㏙코드를빠르게묶고최적화㏚

                                                                                                                                      13

<!-- source-page: 14 -->

IT 용어
백엔드㏙Backend㏚

§ 웹서비스의보이지않는뒷단에서모든기능이제대로작동하도록만드는영역
§ 프론트엔드의요청을받아서데이터를처리하고결과를돌려주는역할

        역할                             설명

 서버운영             사용자의요청을받는서버㏙컴퓨터프로그램㏚를관리하고실행

  DB연동, 데이터처리        사용자가입력한정보를계산·검증·분석하고필요한처리를수행

  API 제공             프론트엔드가데이터를주고받을수있도록API를만들어제공

 보안및권한관리           로그인, 암호화, 접근제한등사용자정보보호기능을담당

 성능관리및로깅         서버가빠르고안정적으로동작하도록최적화하고, 오류를기록

§ 백엔드에서자주쓰는기술

        구분                             예시

 프로그래밍언어                  Java, Python, JavaScript㏙Node.js㏚, Go, Kotlin

 프레임워크                     Spring Boot㏙Java㏚, Django㏙Python㏚, Express㏙Node.js㏚, FastAPI㏙Python㏚

  데이터베이스㏙DB㏚             MySQL, PostgreSQL, MongoDB, Redis

  API 형식                   REST API, GraphQL

 서버/배포환경               AWS, Docker, Nginx, GitHub Actions 등

                                                                                                                                      14

<!-- source-page: 15 -->

IT 용어
프론트엔드와백엔드연동㏙MPA㏚

§  MPA ㏙Multi㎿Page Application㏚ 㚉 WAS 기반

§  Server side에서화면에필요한변수데이터생성및처리작업㏙JSP㏚

         Frontend                        Backend

                                                                      xx.jsp                    HTTP GET
       Web Browser                                 Web Server           WAS             WAS         Mobile Appl.
                   HTML, Static Resource
                                                                 text/html      HTML                                                            JSP/spring
                                                 JS, CSS, image      CSS
                                                                    Content㎿Type
        Javascript
                                                                      ㎿text/html
                                                                          ㎿text/plain
                                                                         ㎿application/xml

                     HTTP GET
        PC Web                               BFF
                  HTML, Static Resource
                                                   WAS             WAS
                    HTTP GET
       Mobile App                              BFF       node.js     UI Rendering
                  HTML, Static Resource
                                                                spring     API 분리㏙composition API㏚

                                                                                                                                      15

<!-- source-page: 16 -->

IT 용어
Frontend와Backend 연동㏙SPA㏚

§  SPA ㏙Single Page Application㏚ 㚉 Rest API Backend

§   Client side에서화면에필요한변수데이터생성및처리작업㏙JS㏚

           Frontend                         Backend

                                                 nginx
                                                                static resource
                                                                 •  vue.js           ㎿javascript, html, css, image
                                                                 •  react           최초접속시              페이지정보GET
                                                               Content㎿Type
                                                                      ㎿application/json
                    HTTP Request              HTTP Request
                                                  API                  Rest API      Web Client                                                     WAS                                           Gateway                 Server                                 json                                                                  json
      HTML                                            •  kong,                       •  spring boot
      CSS                                              •  haproxy,                   •  node.js
         Javascript                                      •  nignx                       • python
                                                               •  spring cloud gateway

                                                                                                                                      16

<!-- source-page: 17 -->

IT 용어
JSON 포맷

§ JSON은데이터표현및저장을위한형식㎿주로데이터교환및API 응답등에사용

 v JSON ㏙JavaScript Object Notation㏚
   정의:                                                  {
                                                           "name": "John Doe",
     • JSON은데이터를키㎿값쌍형식의경량데이터교환형식
                                                           "age": 30,
     • 언어에구애받지않고대부분의프로그래밍언어에서사용             "isMarried": false,
     • 사람이읽기쉽고, 기계가처리하기도간단                        "children": ["Anna", "Ben"],
                                                           "address": {  기본구조:
                                                             "city": "Seoul",
     •  객체㏙Object㏚: ㏛㏜로묶이고, 키㎿값쌍으로구성
                                                             "zipCode": "12345"
     •  배열㏙Array㏚: ㏝㏞로묶이고, 값들의리스트를포함                                                           }
     •  값㏙Value㏚: 문자열, 숫자, 객체, 배열, true, false, null 지원          }

                                                                                                                                      17

<!-- source-page: 18 -->

IT 용어
YAML 포맷

§ YAML은데이터표현및저장을위한형식㎿주로설정파일에사용

 v YAML ㏙YAML Ain㑄t Markup Language㏚
   정의:
                                                         name: John Doe
     • YAML은사람이읽기쉽도록설계된데이터직렬화형식                                                         age: 30
     • 들여쓰기를통해데이터계층을표현                          isMarried: false
     • JSON보다간결하고가독성이높음                          children:
                                                           - Anna
     • 주로구성파일㏙config㏚에서많이사용
                                                           - Ben
  기본구조:
                                                         address:
     • 키㎿값쌍㏙Key㎿Value Pair㏚: 㐱:㐲으로구분                        city: Seoul
     •  리스트㏙List㏚: 㐱㎿㐲로시작                                    zipCode: "12345"
     • 들여쓰기: 계층구조를나타내는데사용

     • 주석: #로작성

                                                                                                                                      18

<!-- source-page: 19 -->

IT 용어
동기와비동기

    구분             동기식㏙Synchronous㏚                       비동기식㏙Asynchronous㏚

  처리방식  요청à 응답까지기다림          요청à 응답대기없이다음작업수행, 결과는나중에수신

  흐름제어    직렬/순차적㏙Blocking㏚ 처리              병렬적㏙Non㎿blocking㏚ 처리

  구현복잡도  단순함㏙순차적코드흐름㏚            복잡함㏙콜백지옥, 상태관리필요㏚

   신뢰성   높은일관성㏙순서대로처리됨㏚         처리순서불확실성㏙재시도, 실패감지필요㏚

  적용상황  트랜잭션이중요한금융/결제시스템등     대규모사용자이벤트처리, 알림, 대기열등

                                                                                                                                      19

<!-- source-page: 20 -->

IT 용어
소프트웨어아키텍처

   구분                   Monolith Architecture                         Micro Service Architecture

   응집도   낮아질수있음㏙여러책임이한곳에모임㏚          높음㏙기능별책임분리㏚

   복잡도   코드량이증가하며내부복잡도상승            네트워크/운영복잡성증가㏙분산시스템㏚

  단독실행  낮음㛳 부분실행어려움, 통째로빌드/실행         높음㛳 개별서비스단독실행/테스트가능

   결합도    높음㏙Tightly㎿Coupled㏚㛳 하나변경시전체영향       낮음㏙Loosely㎿Coupled㏚㛳 독립적배포·확장가능

 v Monolith는하나의프로그램이므로응집도가더높지않을까?
  à 하나의모듈이얼마나일관된책임을가지고있는가의측면

                                                                                                                                      20

<!-- source-page: 21 -->

개발환경구성

본문서는SK AX의컨텐츠자산으로, 무단사용및불법배포시법적조치를받을수있습니다.

<!-- source-page: 22 -->

개발서버구성
맥북에서는일괄설치/세팅

 ⭐Xcode, Homebrew, Git, Oh My Zsh, JDK21, Python3.11, Node.js,
   PostgreSQL, VSCode, Docker Desktop, awscli, kubectl, iTerm2 등SKALA 과정에서
   필요한SW/Tool 일괄설치

✅슬랙을통해전달받은쉘스크립트를터미널에서실행하기

   1⃣‍ skala㎿config㎿setup.sh, skala㎿config㎿setup㎿check.sh 을다운로드받기
   2⃣‍ 터미널을오픈하면홈디렉터리가/Users/OOOOOOOO

   3⃣‍ 터미널에서다음명령어순차수행
    㙌mkdir ㎿p skala/skala㎿config㎿setup
   㙌 cd 㚕/skala/skala㎿config㎿setup
   㙌mv 㚕/Downloads/skala㎿config㎿setup.sh .
   㙌 chmod 㚉x skala㎿config㎿setup.sh
   㙌 ./skala㎿config㎿setup.sh

                                                                                                                             22

<!-- source-page: 23 -->

개발서버구성
맥북일괄설치/세팅
        •  skala㎿config㎿setup.sh 다운로드받는다. ㏙Slack 이나훈련생포털㏚
        • 특정위치로Move 한다.

               • 홈디렉토리하위에skala 폴더생성

            㙌mkdir ㎿p skala/skala㎿config㎿setup

           㙌cd 㚕/skala/skala㎿config㎿setup

               •  㙌mv 㚕/Downloads/skala㎿config㎿setup.sh .
        • 실행권한을부여한다.

       㙌chmod 㚉x skala㎿config㎿setup.sh

        • 실행한다.

         㙌./skala㎿config㎿setup.sh

        • 설치가정상적으로끝날때까지계속진행을하면서요청에의해㐱Y㐲 를클릭하고
      맥북계정Password 를입력한다.

        • 설치이후마무리안내메시지를확인하고명령어를실행한다.

           git config 㚕㚕㚕 명령어의본인의이름과이메일로처리할것

                                                                                                                             23

<!-- source-page: 24 -->

개발환경구성
㏝참고㏞ 설치검증㎿도구버전확인

§ ①설치완료후마무리(터미널을새로열거나아래실행)

 $ source ~/.zprofile
 $ source ~/.zshrc
 $ open -a Docker        # Docker Desktop은최초1회실행필요

§ ②주요도구버전확인- 모든명령이값을출력하면정상

 $ git --version     $ java -version       $ python3 --version
 $ node -v           $ docker --version    $ code --version
 $ aws --version     $ kubectl version --client

                                                                                                                                      24

<!-- source-page: 25 -->

IDE 환경설정

본문서는SK AX의컨텐츠자산으로, 무단사용및불법배포시법적조치를받을수있습니다.

<!-- source-page: 26 -->

IDE 환경설정
VS Code 메뉴

§ 상단메뉴바와사이드메뉴로구성
§ 명령팔레트: 모든기능을키보드로검색후실행
§ 상태바: 현재상태, 오류, 언어, Git 브랜치등실시간정보표시

        파일목록

          검색

         GIT 형상관리

       Run 㖈 Debug

          Extensions

                                                                                                                             26

<!-- source-page: 27 -->

IDE 환경설정
VS Code 터미널열기

§  VSCode 화면에서터미널메뉴나단축키㏙cmd 㚉 j㏚를사용해서터미널을오픈한다.

                                                                                                                             27

<!-- source-page: 28 -->

IDE 환경설정
㏝참고㏞ 터미널에서유용한명령어

    Linux 명령어        설명             Windows CMD 명령어              비고

   ls ㎿al      디렉토리목록상세보기         dir ㎿Force          숨김파일포함상세목록

  cd       디렉토리이동             cd               동일

  mkdir      디렉토리생성               mkdir             동일

  rm        파일/디렉토리삭제            del ㏙파일㏚, rmdir ㏙디렉토리㏚      rmdir /s로하위디렉토리포함삭제가능

  cp       복사                    copy             파일복사

  mv      이동또는이름변경        move            파일이동또는이름변경

   cat      파일내용보기              type             텍스트파일내용출력

  pwd      현재디렉토리경로확인      cd ㏙아무인자없이실행㏚     현재경로출력

  touch     빈파일생성                type nul 㚏 파일명            예: type nul 㚏 test.txt

  echo      문자열출력               echo              동일

                                                                                                                             28

<!-- source-page: 29 -->

IDE 환경설정
Git 개요

 § 버전관리시스템(VCS): 파일의변경이력을저장하고, 필요할때예전상태로되돌리는기능을제공.
 § 협업도구: 여러사람이동시에하나의프로젝트를안전하게작업할수있도록도와줌.

                           용어              설명

                                                      Repository  Git으로관리되는폴더- 코드와변경기록저장

                                              Commit   변경사항을저장하는스냅샷(“사진찍기”)

                                                  Branch   다른작업을위해갈라지는가지

                                               Merge    갈라진작업(branch)을다시합치는것.

                                             Remote   인터넷에있는저장소– GitHub, GitLab 등

                                                   Clone   원격저장소를내컴퓨터로복사하는것.

                                                                                                                                        29

<!-- source-page: 30 -->

IDE 환경설정
 Git 흐름도

 §  clone: 원격저장소를내컴퓨터로복사㏙프로젝트처음복제㏚
 §   pull: 원격저장소의최신변경사항을내로컬로가져오기

 §  push: 내로컬에서커밋한내용을원격저장소로업로드

https://geo-python-site.readthedocs.io/en/lih/lessons/L2/git-basics.html                                                                                       30

<!-- source-page: 31 -->

IDE 환경설정
Git 사용자정보설정

§  Git 설치확인및사용자정보설정

    ㏝Git 설치확인㏞
    git ㎿㎿version

    ㏝ 사용자이름설정㏞
    git config ㎿㎿global user.name 㑃홍길동㑃

  ㏝이메일주소설정㏞ GitHub에등록된이메일주소와일치하는지확인필요
    git config ㎿㎿global user.email 㑃gildong㖇example.com㑃

  ㏝설정확인㏞
    git config ㎿㎿global ㎿㎿list

  v 필요하다면.gitconfig 파일을직접편집㏊맥기준위치㎕ 㚴/.gitconfig ㏙/Users/사용자이름/.gitconfig㏚

                                                                                                                                      31

<!-- source-page: 32 -->

IDE 환경설정
㏝참고㏞ .gitignore 파일

   §  Git 버전관리시스템에서특정파일이나디렉터리를추적하지않도록설정
   § 불필요한파일이Git 리포지토리에추가되거나추적되지않도록방지

     < Node.js UI 프로젝트예시>       < Java API 프로젝트예시>

      # Logs                                 HELP.md                                                • 빌드아티팩트및임시파일제외
      logs                                   target/
      *.log                                  !.mvn/wrapper/maven-wrapper.jar            • 환경설정파일제외
      npm-debug.log*                         !**/src/main/**/target/
                                                                                                                            • 로그파일및캐시제외
      yarn-debug.log*                        !**/src/test/**/target/
      yarn-error.log*                                                                                             • 예외처리㎕ !를사용해.gitignore에추가된폴더의
      pnpm-debug.log*                        ### STS ###
      lerna-debug.log*                       .apt_generated               예외제외파일을지정
                                             .classpath
      node_modules                           .factorypath
      dist                                   .project
      dist-ssr                               .settings
      *.local                                .springBeans
                                             .sts4-cache
      # Editor directories and files
      .vscode/*                              ### VS Code ###
      !.vscode/extensions.json               .vscode/
      .idea
      .DS_Store
      *.suo
      *.ntvs*
      *.njsproj
      *.sln
      *.sw?

                                                                                                                                      32

<!-- source-page: 33 -->

IDE 환경설정
㏝실습㏞ 작업폴더㏙skala㎿workspace㏚만들기

   § 터미널열기à 사용자홈㏙home㏚ 디렉토리로이동㏙cd 명령㏚
   §  작업폴더㏙skala㎿workspace㏚ 생성

   $ cd
   $ mkdir skala-workspace

   § 작업폴더로이동

   §  프로젝트폴더㏙skala㎿intro㏚ 생성후이동
   §  VS Code 실행

   $ cd skala-workspace
   $ mkdir skala-intro
   $ cd skala-intro
   $ code .

                                                  2
 Restricted Mode 일경우
                           1

                                                                                                                                      33

<!-- source-page: 34 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

Index.html 를생성하고SKALA 소개페이지를만들어줘

                                                                                                                                      34

<!-- source-page: 35 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

.gitignore 파일을생성하고, .env 파일은git 에서관리되지않도록해줘

                                                                                                                                      35

<!-- source-page: 36 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

서비스로띄우기위한확장플러그인설치㏁Live Server

                                                                                                                                      36

<!-- source-page: 37 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

Live Server 확장플러그인설치후우측하단Go Live 클릭

                                                                                                                                      37

<!-- source-page: 38 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

해당서비스를중단하려면우측하단Port:5500 부근클릭

                                                                                                                                      38

<!-- source-page: 39 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

Github.com 내나만의소스코드저장소생성하기
㏁먼저Github 로그인하고VSCode 에서Initialize 㚕 버튼클릭

                                                                                                                                      39

<!-- source-page: 40 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

커밋버튼까지클릭하면스테이징㚴㚴㚴팝업나오고여기에서＂예㐲or 㐱항상㐲으로

                           특정한Repository 생성을선택하고게시하도록

                                                                                                                                      40

<!-- source-page: 41 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

Github 에서확인해보면게시한코드가보이네요….

                                                                                                                                      41

<!-- source-page: 42 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

추가적인뉴스레터페이지하나생성해줘

                                                                                                                                      42

<!-- source-page: 43 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

생성된페이지를Github 에올리기위한커밋하고동기화

                                                                                                                                      43

<!-- source-page: 44 -->

4. Git 환경설정
㏝실습㏞ Vibe Coding 으로코드생성하기

Github 에서확인해보면방금추가한뉴스레터페이지가보이네요….

                                                                                                                                      44

<!-- source-page: 45 -->

IDE 환경설정
㏝참고㏞ 로컬GIT Repository 생성㏙CLI㏚

§ 로컬저장소초기화및파일생성

 $ mkdir skala-intro
 $ cd skala-intro
 $ git init
 $ echo “# SKALA codes” > readme.md
 $ git add .
 $ git commit -m “Initial message”

§ 원격저장소로push

 $ git remote add origin https://github.com/your-username/skala-intro.git
 $ git branch -M main #main branch 가main인경우
 $ git push -u origin main

                                                                                                                                      45

<!-- source-page: 46 -->

IDE 환경설정
㏝참고㏞ Git 주요명령어㏙1㏚ ㎿저장소·커밋·동기화

§ ①저장소만들기& 상태확인
 $ git init                     # 현재폴더를Git 저장소로초기화
 $ git clone <원격주소>          # 원격저장소를통째로복제
 $ git remote -v                # 연결된원격저장소확인
 $ git status                   # 변경/스테이징상태확인

§ ②커밋& 원격동기화

 $ git add .                    # 변경분스테이징(git add <파일>도가능)
 $ git commit -m "메시지"        # 스냅샷저장(커밋)
 $ git push origin main         # 로컬커밋을원격으로업로드
 $ git pull origin main         # 원격최신내용을로컬로반영
 $ git log --oneline            # 커밋이력한줄로보기

                                                                                                                                      46

<!-- source-page: 47 -->

IDE 환경설정
㏝참고㏞ Git 주요명령어㏙2㏚ ㎿브랜치·병합·되돌리기

§ ①브랜치& 병합
 $ git branch                   # 브랜치목록확인
 $ git switch -c feature/login  # 새브랜치생성후이동(=checkout -b)
 $ git switch main              # 브랜치이동(=git checkout)
 $ git merge feature/login      # 현재브랜치에지정브랜치병합

§ ②되돌리기& 임시저장

 $ git restore <파일>           # 워킹트리변경취소
 $ git reset --soft HEAD~1      # 직전커밋취소(변경내용은유지)
 $ git revert <커밋>            # 특정커밋을되돌리는새커밋생성(안전)
 $ git stash / git stash pop    # 작업임시저장/ 복원

                                                                                                                                      47

<!-- source-page: 48 -->

IDE 환경설정
㏝참고㏞ Git Flow ㎿브랜치전략

§ ①브랜치5종의역할
 main     : 배포(운영) 가능한안정버전- 태그로버전관리
 develop  : 다음릴리즈를위한통합브랜치
 feature/*: 기능단위개발(develop에서분기→ develop으로병합)
 release/*: 출시준비(버그픽스) - 완료시main·develop에병합
 hotfix/* : 운영긴급수정(main에서분기→ main·develop에병합)
§ ②브랜치흐름다이어그램(Git Flow)
                                                                                                      v1.0                               v1.0.1
           main

             hotfix

           release

         develop

           feature

            → 시간(commit) 흐름

 ※ feature·release·hotfix 는작업후develop/main 으로병합  |  소규모·CI/CD 환경은GitHub Flow(main
 + feature + PR)를선호

                                                                                                                                      48

<!-- source-page: 49 -->

IDE 환경설정
㏝참고㏞ Github 토큰관리

 Personal Access Token (PAT) 생성

 1. GitHub 로그인
         : GitHub에로그인한다.

 2. Settings로이동
         : 오른쪽상단프로필사진을클릭한후, Settings를선택한다.

 3. Developer Settings로이동
         : 왼쪽메뉴에서Developer settings를클릭한다.

 4. Personal Access Token 생성
         : **Personal access tokens > Tokens (classic)**로이동한후, Generate new token을클릭한다.
      Note: 토큰의이름을입력한다. (예: "MyToken")
       Expiration: 토큰의만료기간을설정한다. (예: 30일, 90일등)
      Scopes: 필요한권한을선택한다. Private repository에접근하려면repo 권한을반드시선택해야한다.
    설정이완료되면Generate token을클릭한다.

 5. 토큰복사
         : 생성된토큰을복사한다. (이토큰은한번만표시되므로안전한곳에저장하세요.)

                                                                                                                                      49

<!-- source-page: 50 -->

IDE 환경설정
㏝참고㏞ GitHub 인증㏙PAT㏚으로push 㖈 보안주의

§  ①push 시인증- 비밀번호칸에PAT 입력

 Username: your-github-id
 Password: <생성한PAT 붙여넣기>   ← GitHub 계정비밀번호아님
 # macOS 키체인에저장되어이후자동인증

§ ②더쉬운대안& 보안주의사항

 $ gh auth login          # GitHub CLI 브라우저인증(권장)
 ※ API 키·토큰·비밀번호는절대커밋금지  (.env → .gitignore)
 ※ 실수로올렸다면즉시해당키를폐기후재발급

                                                                                                                                      50

<!-- source-page: 51 -->

IDE 환경설정
㏝참고㏞ Github에서저장소직접생성

§  Private Repository 생성

                                                                                     • 설정하지마세요.
                                                                                     • 설정하는경우
                                                                                     • 로컬과remote 간데이터불일치로
                                                                                     •  git pull origin main --rebase 과정이필요하게됩니다.

                                                                                                                                      51

<!-- source-page: 52 -->

AI 코딩맛보기

본문서는SK AX의컨텐츠자산으로, 무단사용및불법배포시법적조치를받을수있습니다.

<!-- source-page: 53 -->

AI 코딩맛보기
㏝실습㏞ OpenAI Codex CLI 설치및실행

§ ①설치(Node.js·npm은배치스크립트로이미설치됨)

 $ mkdir codex-intro && cd codex-intro
 $ npm install -g @openai/codex
 $ codex –version

§ ②실행및로그인(최초1회인증)

 $ codex                 # 실행후로그인/인증진행
 # 이후자연어로요청→ "python3.11 기반Hello World 출력프로그램만들어줘”

                                                                                                                                      53

<!-- source-page: 54 -->

AI 코딩맛보기
㏝실습1㏞ OpenAI Codex

특정폴더생성하고codex cli 설치및codex 명령어실행하기

                                                                                                                                      54

<!-- source-page: 55 -->

AI 코딩맛보기
[실습2] / 명령어활용

 /init 를실행시지침서목적의AGENTS.md 파일생성됨.

 /명령어에대해서는업데이트가빈번히발생하기에상황에맞추어확인후사용하기바람.

                                                                                                                                      55

<!-- source-page: 56 -->

AI 코딩맛보기
[실습3] 프로그램코드생성

 첫번째요청㐱python3.11 기반에서Hello World!!! 가출력되는프로그램생성해줘㐲

                                                                                                                                      56

<!-- source-page: 57 -->

AI 코딩맛보기
[실습4] 프로그램코드이해

다음요청㐱프로그램코드를설명해줘㐲

                                                                                                                                      57

<!-- source-page: 58 -->

5. AI 코딩맛보기
[실습5] 코드리뷰

다음요청㐱코드리뷰를진행해줘㐲

                                                                                                                                      58

<!-- source-page: 59 -->

AI 코딩맛보기
[실습6] 코드테스트

다음요청㐱테스트를진행해줘㐲

                                                                                                                                      59

<!-- source-page: 60 -->

AI 코딩맛보기
[실습7] 일반적인설명및비교
다음요청㐱정규표현식에대해설명하고일반적인정규표현식과파이썬에서사용하는정규표현식의
 차이가있으면표로비교㐲

                                                                                                                                      60

<!-- source-page: 61 -->

AI 코딩맛보기
[실습8] 새로운코드생성

 다음요청㐱정규표현식을사용하여비밀번호검증하는코드를작성해줘. 비밀번호는영문대문자,
 영문소문자, 숫자와특수문자가포함되어야함.㐲

                                                                                                                                      61

<!-- source-page: 62 -->

AI 코딩맛보기
[실습9] 새로운키워드설명

 다음요청㐱mermaid 다이어그램이란?㐲

                                                                                                                                      62

<!-- source-page: 63 -->

AI 코딩맛보기
[실습10] 샘플화면및특정js 적용해서브라우저조회

 다음요청㐱mermaid 다이어그램샘플화면?㐲, 㐱mermaid.js 를적용해서보여줘㐲

                                                                                                                                      63

<!-- source-page: 64 -->

SKALA의첫날수고하셨습니다.
  ⭐끝까지함께해요🏃‍
