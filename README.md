# QA Hub

> 서비스 품질을 하나의 흐름으로.

QA 엔지니어링의 전 과정 — **테스트 플랜 → 자동화 실행 → 디바이스팜 → CI/CD → 결함 추적 → 품질 지표** — 을 하나의 콘솔로 통합한 포트폴리오 프로젝트.

**Live Demo** · [qa-dashboard-flax.vercel.app](https://qa-dashboard-flax.vercel.app)

![QA Hub Preview](./preview.png)

This project is tested with BrowserStack.

---

## 왜 만들었나

QA 업무는 보통 여러 도구에 분산되어 있습니다. 테스트 플랜은 스프레드시트, 자동화는 별도 리포, 결함 추적은 Jira, 코드 변경은 GitLab, 디바이스 검증은 수동, 품질 지표는 수동 집계.

**모든 흐름을 하나의 콘솔로 통합하면, QA 엔지니어가 설계 · 실행 · 추적 · 분석에 집중할 수 있다**는 가설에서 시작했습니다.

---

## 주요 기능 (7개 메뉴)

### 1. 홈
서비스 포지셔닝 + 라이브 메트릭(통과율, 자동화율) 미니 대시보드.

### 2. 테스트 플랜
리스크 기반 TC 설계, Smoke / Regression / Integration 카테고리 관리, 담당자별 진행률 추적.

### 3. 자동화 테스트 ⭐
**실제로 돌아가는 Playwright 자동화 엔진.**

- TC는 DB(`testcases` 테이블)에 저장, UI에서 CRUD
- Run 버튼 → Flask 백엔드가 **백그라운드 스레드**로 Playwright 실행 → saucedemo.com 조작
- **라이브 스크린샷 500ms 폴링**으로 실행 중인 테스트 실시간 모니터링
- 각 스텝별 통과/실패 상태 + 실행 시간 + 에러 메시지
- 실행 결과는 `test_runs` 테이블에 영구 저장

**샘플 TC 5개**:

| TC | 시나리오 | 예상 |
|----|---------|------|
| TC-001 | 로그인 성공 - 유효한 자격증명 | Pass |
| TC-002 | 로그인 실패 - 잠긴 계정 | Pass (에러 메시지 검증) |
| TC-003 | 장바구니 상품 추가 - 뱃지 반영 | Pass |
| TC-004 | 결제 완료 End-to-End (14스텝) | Pass |
| TC-005 | 이미지 깨짐 검증 (`problem_user`) | **의도된 Fail** |

**TC-005가 포트폴리오 하이라이트** — saucedemo의 `problem_user` 계정에 심어진 "상품 이미지 404 치환 버그"를 자동화가 정확히 검출. **QA 자동화의 본질은 통과율이 아니라 결함 검출**임을 증명하는 사례.

### 4. 디바이스팜
iPhone 14 · 15 Pro · iPad Air · Pixel 7/8 · Galaxy S23/S24 — **7대 디바이스 실시간 상태 모니터링** UI.
- 디바이스별 미러링 뷰 (Live Preview)
- 배터리 · 가동 시간 메트릭
- 실행 중 TC + 진행률
- 디바이스별 최근 실행 이력

### 5. CI/CD 파이프라인
PR 머지 → 빌드 → 디바이스팜 배포 → pytest / Appium 병렬 실행 → Slack 리포트까지 **6단계 파이프라인 시각화**.

### 6. 결함 트래커 — Jira × GitLab 교차 검증
릴리즈 범위 자동 매칭 + 리스크 선제 탐지.
- `fixVersion` 기준으로 Jira 티켓 수집
- `release/{version}` 브랜치의 머지된 MR 수집
- MR 제목 · 브랜치 · 커밋에서 `[A-Z]+-\d+` 패턴으로 Jira 키 추출
- **매칭 / 누락 / 범위 외 / 상태 불일치** 네 가지로 자동 분류
- Slack · 이메일 자동 알림

### 7. 품질 대시보드
릴리즈별 통과율 · 결함 밀도 · 자동화율 추이를 **자체 SVG 차트**로 시각화.

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Vue 3 (Options API), Vite, Pretendard Variable |
| Backend | Flask (Python 3.11), psycopg2, python-dotenv |
| Database | PostgreSQL (Supabase, Tokyo region) |
| 자동화 엔진 | Playwright (Chromium) |
| 배포 | Vercel (Frontend), Render (Backend Web Service) |
| 모니터링 | UptimeRobot (keep-alive, cold start 제거) |
| 외부 연동 설계 | Jira REST API, GitLab API, GitHub Actions, Appium, Firebase Test Lab |

---

## 자동화 테스트 아키텍처

```
┌─────────────────────┐
│   Frontend (Vue)    │  ← Run 버튼
└──────────┬──────────┘
           │ POST /api/testcases/:id/run
┌──────────▼──────────┐
│  Flask Backend      │  ← run_id 즉시 반환, 백그라운드 스레드로 실행
├─────────────────────┤
│  BaseRunner (abstract)
│       ├── WebRunner (Playwright, 구현)
│       └── MobileRunner (Appium, 자리만)
└──────────┬──────────┘
           │ 결과 저장
┌──────────▼──────────┐
│ PostgreSQL (Supabase)│  testcases + test_runs
└─────────────────────┘
```

### 설계 포인트

**1. `BaseRunner` 추상 클래스로 웹/모바일 러너 통일**
- 새 러너 추가 = 파일 하나 (`runners/mobile.py`에 Appium 구현)
- 액션 포맷 통일 (`fill`, `click`, `assert_*`) → TC 하나로 **웹·모바일 둘 다** 돌릴 수 있는 여지

**2. 백그라운드 비동기 실행**
- Run 요청은 즉시 `run_id` 반환, Playwright는 백그라운드 스레드로 실행
- 창을 닫고 다른 TC도 실행 가능 → 멀티태스킹 UX

**3. TC는 DB(JSONB)에 저장**
- 파일 1개당 TC 1개면 200개 TC = 200개 파일 → 운영 불가능
- `steps`를 JSONB로 저장 → UI에서 CRUD, 스케일 걱정 없음

---

## 환경별 라이브 뷰 전략

| 환경 | 라이브 뷰 방식 | 이유 |
|------|-------------|------|
| **공개 데모** (Vercel + Render Free) | Playwright 실행 + 스크린샷 500ms 폴링 | 서버 자원 보호 + 라이브 느낌 유지 |
| **로컬 개발** | Playwright `headless=False`로 실제 창 | 디버깅 편의 |
| **사내 환경** (확장 가능성) | Xvfb + noVNC로 서버 Chromium 화면 공유 | 사내망 접근으로 보안 제약 없음, QA 팀 전체가 하나의 자동화 서버 공유 |

### Render Free (512MB RAM) 최적화

- Chromium 런칭 플래그 20개+ (메모리 / CPU 절약)
- Viewport 1024x576 축소
- 영상 녹화 비활성화 (환경변수 `RECORD_VIDEO=1`로 로컬에선 켬)
- `slow_mo` 50ms로 라이브 뷰 가독성 vs 속도 균형
- UptimeRobot 5분 ping으로 cold start 제거

---

## 실무 운영 확장 아키텍처

### 디바이스팜
- **로컬 저비용**: Android Studio Emulator + Appium
- **클라우드 무료**: Firebase Test Lab Spark Plan (하루 Android 5대 + iOS 10대 실기기)
- **엔터프라이즈**: BrowserStack / Sauce Labs / AWS Device Farm 연동

### CI/CD
GitHub Actions 워크플로우로 PR → 빌드 → 디바이스팜 호출 → Slack 리포트.

---

## 프로젝트 구조

```
qa-dashboard/
├─ backend/
│  ├─ app.py                       # Flask 진입점
│  ├─ db.py                        # DB 커넥션 (python-dotenv)
│  ├─ migrate.py                   # DB 테이블 생성
│  ├─ seed_testcases.py            # Seed TC 5개
│  ├─ requirements.txt
│  ├─ .env.example
│  └─ automation/                  # 자동화 테스트 전용
│     ├─ __init__.py
│     ├─ __main__.py               # CLI (python -m automation TC-001)
│     ├─ routes.py                 # Flask Blueprint
│     ├─ queries.py                # DB 쿼리 레이어
│     ├─ actions.py                # 액션 매핑
│     ├─ runners/
│     │  ├─ base.py                # 공용 추상 러너
│     │  ├─ web.py                 # Playwright (웹)
│     │  └─ mobile.py              # Appium (자리만)
│     └─ output/                   # gitignore
│
└─ frontend/
   └─ src/
      ├─ App.vue
      ├─ api/index.js
      └─ components/
         ├─ WBSList.vue
         ├─ WBSDetail.vue
         ├─ AutomationTest.vue      # 실제 돌아가는 자동화 콘솔
         ├─ DeviceFarm.vue
         ├─ CICDPipeline.vue
         └─ DefectCrossCheck.vue
```

---

## 로컬 실행

**백엔드**
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
cp .env.example .env         # DATABASE_URL 입력
python migrate.py            # 테이블 생성
python seed_testcases.py     # TC 5개 삽입
python app.py
```

**프론트엔드**
```bash
cd frontend
npm install
npm run dev
```

**CLI로 TC 직접 실행** (디버깅용)
```bash
cd backend
python -m automation TC-001 --headed    # 실제 창 뜨면서 실행
python -m automation TC-005 --headed    # 버그 검출 재현
```

---

## 설계 노트

**공개 저장소 데모의 한계**
Jira · GitLab 실제 토큰은 공개 불가 → 결함 트래커는 **모의 데이터로 UI 시연**. 실제 API 호출 모듈은 설계되어 있으며 `.env`에 토큰만 세팅하면 실 데이터로 전환.

**자체 SVG 차트**
차트 라이브러리 의존성 없이 직접 SVG로. 번들 크기 최소화 + 디자인 완전 제어.

**Supabase + Render Free 조합의 이유**
30일 만료되는 Render PostgreSQL 대신 Supabase 영구 Free 사용 (Tokyo region). Flask 서버는 Render Free Web Service(Oregon). 데이터 지역성과 비용 최적화 사이의 균형.

---

## 라이선스

MIT License — [LICENSE](./LICENSE)

---

## Developer

**박수빈 (Subeen Park)**
QA Engineer @ SOOP (ex. Nexon Networks)
[mas_jaypark@naver.com](mailto:mas_jaypark@naver.com) · [@subeen-park](https://github.com/subeen-park)