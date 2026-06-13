# QA Dashboard

🔗 **[https://qa-dashboard-flax.vercel.app](https://qa-dashboard-flax.vercel.app)**

---

## 개요

QA Dashboard는 QA 엔지니어가 릴리즈마다 반복되는 검증 작업을 체계적으로 관리할 수 있도록 설계한 풀스택 대시보드입니다. 
릴리즈별 테스트 진행 상황, 결함 분석, 필드 이슈 추적, 품질 지표 시각화까지 QA 업무 전반을 하나의 화면에서 다룰 수 있어요.

---

## 주요 기능

### 릴리즈 보드
- 릴리즈별 검증 진행 상황과 마감일 관리
- 그룹별 태스크 배치 및 드래그앤드롭 이동
- 진행률 일괄 수정 / 자동 백업 / 시점 복원

### 릴리즈 캘린더
- 전체 릴리즈 마감일을 월별 캘린더로 시각화
- 상태별 색상 구분 (완료/진행중/리스크/지연/대기)
- 날짜 클릭 시 해당 일자 릴리즈 상세 패널

### 릴리즈 체크리스트
- 릴리즈 전 QA 게이트 항목 체크
- 배포 / 롤백 플랜 / 모니터링 항목 관리

### 머지 트래커
- 브랜치/버전별 머지 현황 단계 관리 (미빌드 → 빌드완료 → 머지요청 → 머지완료)
- 메트릭 카드 클릭 시 해당 단계로 즉시 포커싱

### Jira 레이더
- Jira 티켓 정체 구간 분석 (정체 일수 기준 필터)
- 병목 담당자 Top 10 · 막대 그래프
- 기한 누락 / 기한 지연 티켓 별도 추적

### 자동화테스트
- 개발 진행중

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Vue 3 (Options API), Vite |
| Backend  | Flask (Python 3.11) |
| Database | PostgreSQL |
| 배포     | Vercel + Render |

---

## 프로젝트 구조

```
qa-dashboard/
├── backend/
│   ├── app.py              # Flask API + PostgreSQL
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.vue              # GNB + 라우팅
        ├── api/index.js
        ├── utils.js
        └── components/
            ├── WBSList.vue          # 릴리즈 목록
            ├── WBSDetail.vue        # 릴리즈 상세
            ├── TaskTable.vue        # 태스크 테이블
            ├── GanttChart.vue       # 간트 차트
            ├── TaskForm.vue
            ├── ProjectForm.vue
            ├── MergeTracker.vue     # 머지 트래커
            ├── JiraRadar.vue        # Jira 정체 분석
            ├── ReleaseCalendar.vue  # 캘린더
            ├── ReleaseChecklist.vue # 체크리스트
            └── NotifPanel.vue
```

---

## 로컬 실행

### 백엔드

```bash
cd backend
pip install -r requirements.txt
flask --app app run --port 5000
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5173` 접속.

`.env`에 API 주소 지정 가능:

```
VITE_API_URL=http://localhost:5000/api
```

---

## 배포 환경

| 항목 | 값 |
|------|------|
| Frontend | Vercel (main 브랜치 자동 배포) |
| Backend  | Render (Python 3.11, gunicorn) |
| DB       | Render PostgreSQL |
| 슬립 방지 | UptimeRobot 5분 핑 |

---

## 데이터베이스 테이블

| 테이블 | 설명 |
|--------|------|
| `projects`       | 릴리즈 프로젝트 |
| `tasks`          | 태스크 (그룹·담당자·진행률) |
| `task_snapshots` | 자동 백업 (업로드/삭제 전) |
| `webhook`        | 알림 웹훅 설정 |
| `logs`           | 활동 로그 |

---

## 엑셀 업로드 양식

릴리즈 보드 내 **업로드 ▾ → 업로드 양식 다운받기** 에서 CSV 템플릿을 받을 수 있어요.

| 컬럼 | 설명 | 예시 |
|------|------|------|
| Group | 그룹명 | QA |
| Task | 태스크명 | 회귀 테스트 |
| Note | 메모 | 핵심 결제 플로우 검증 |
| JIRA | Jira 티켓 번호 | DEVICE-001 |
| Assignee | 담당자 | 박수빈 |
| Start Date | 시작일 | 2026-05-20 |
| End Date | 마감일 | 2026-05-28 |
| Progress | 진행률 (0~100) | 80 |

---

## 개발자

**박수빈** — [@subeen-park](https://github.com/subeen-park)
