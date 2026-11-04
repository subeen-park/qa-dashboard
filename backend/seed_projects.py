"""
QA Hub 테스트 플랜 (projects + tasks) Seed
──────────────────────────────────────────
샘플 QA 프로젝트 5개와 각 프로젝트의 WBS 태스크를 삽입.

실행 방법:
  cd backend
  python seed_projects.py

주의:
  - DATABASE_URL 환경변수가 세팅되어 있어야 함
  - 기존 샘플 데이터(이름이 같은 프로젝트)는 건드리지 않음
  - 추가로 넣고 싶으면 PROJECTS 리스트에 항목 추가
"""

import os
import sys
import uuid
import psycopg2
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


TODAY = datetime.now().date()


def d(offset_days):
    """오늘 기준 offset_days 뒤 날짜 문자열 (YYYY-MM-DD)"""
    return (TODAY + timedelta(days=offset_days)).strftime('%Y-%m-%d')


# ─────────── 샘플 프로젝트 5개 ───────────
PROJECTS = [
    {
        'name': 'v2.4.0 소셜 로그인 리뉴얼',
        'description': '카카오·구글·애플 로그인 추가 및 기존 이메일 로그인 플로우 개편',
        'pm': '박수빈',
        'end_date': d(14),
        'tasks': [
            # Smoke
            {'grp': 'Smoke', 'task': '로그인 화면 진입 확인', 'assignee': '박수빈',
             'start_date': d(-7), 'end_date': d(-5), 'progress': 100, 'jira': 'QA-1201'},
            {'grp': 'Smoke', 'task': '카카오 로그인 성공 플로우', 'assignee': '박수빈',
             'start_date': d(-5), 'end_date': d(-3), 'progress': 100, 'jira': 'QA-1202'},
            {'grp': 'Smoke', 'task': '애플 로그인 성공 플로우', 'assignee': '김민지',
             'start_date': d(-5), 'end_date': d(-2), 'progress': 100, 'jira': 'QA-1203'},
            {'grp': 'Smoke', 'task': '구글 로그인 성공 플로우', 'assignee': '김민지',
             'start_date': d(-3), 'end_date': d(-1), 'progress': 100, 'jira': 'QA-1204'},
            # Regression
            {'grp': 'Regression', 'task': '기존 이메일 로그인 정상 동작', 'assignee': '박수빈',
             'start_date': d(-2), 'end_date': d(2), 'progress': 70, 'jira': 'QA-1205'},
            {'grp': 'Regression', 'task': '자동 로그인 유지 확인', 'assignee': '한지원',
             'start_date': d(0), 'end_date': d(4), 'progress': 40, 'jira': 'QA-1206'},
            {'grp': 'Regression', 'task': '세션 만료 시 재로그인 유도', 'assignee': '한지원',
             'start_date': d(2), 'end_date': d(6), 'progress': 10, 'jira': 'QA-1207'},
            # E2E
            {'grp': 'E2E', 'task': '소셜 로그인 → 프로필 생성 → 첫 시청', 'assignee': '박수빈',
             'start_date': d(4), 'end_date': d(10), 'progress': 0, 'jira': 'QA-1208'},
            {'grp': 'E2E', 'task': '로그아웃 후 재로그인 시나리오', 'assignee': '김민지',
             'start_date': d(6), 'end_date': d(12), 'progress': 0, 'jira': 'QA-1209'},
        ],
    },
    {
        'name': 'v2.4.0 결제 플로우 개선',
        'description': '간편결제(카카오페이·네이버페이) 추가, 결제 실패 복구 개선',
        'pm': '박수빈',
        'end_date': d(18),
        'tasks': [
            {'grp': 'Smoke', 'task': '결제 화면 진입 확인', 'assignee': '정하늘',
             'start_date': d(-6), 'end_date': d(-4), 'progress': 100, 'jira': 'QA-1301'},
            {'grp': 'Smoke', 'task': '카카오페이 결제 성공', 'assignee': '정하늘',
             'start_date': d(-4), 'end_date': d(-1), 'progress': 100, 'jira': 'QA-1302'},
            {'grp': 'Smoke', 'task': '네이버페이 결제 성공', 'assignee': '김민지',
             'start_date': d(-2), 'end_date': d(2), 'progress': 80, 'jira': 'QA-1303'},
            {'grp': 'Regression', 'task': '기존 신용카드 결제 정상', 'assignee': '박수빈',
             'start_date': d(0), 'end_date': d(4), 'progress': 50, 'jira': 'QA-1304'},
            {'grp': 'Regression', 'task': '결제 취소/환불 플로우', 'assignee': '정하늘',
             'start_date': d(2), 'end_date': d(7), 'progress': 20, 'jira': 'QA-1305'},
            {'grp': 'Integration', 'task': 'PG사 연동 응답 지연 복구', 'assignee': '박수빈',
             'start_date': d(4), 'end_date': d(9), 'progress': 0, 'jira': 'QA-1306'},
            {'grp': 'E2E', 'task': '결제 실패 → 재시도 → 성공 End-to-End', 'assignee': '한지원',
             'start_date': d(7), 'end_date': d(14), 'progress': 0, 'jira': 'QA-1307'},
            {'grp': 'E2E', 'task': '쿠폰 적용 + 결제 금액 검증', 'assignee': '김민지',
             'start_date': d(10), 'end_date': d(17), 'progress': 0, 'jira': 'QA-1308'},
        ],
    },
    {
        'name': 'v2.3.0 다크 모드 지원',
        'description': '전체 화면 다크 테마 대응, 시스템 설정 자동 감지',
        'pm': '김민지',
        'end_date': d(3),
        'tasks': [
            {'grp': 'UI', 'task': '메인 화면 다크 테마 적용', 'assignee': '김민지',
             'start_date': d(-14), 'end_date': d(-10), 'progress': 100, 'jira': 'QA-1101'},
            {'grp': 'UI', 'task': '상세 페이지 다크 테마 적용', 'assignee': '김민지',
             'start_date': d(-10), 'end_date': d(-7), 'progress': 100, 'jira': 'QA-1102'},
            {'grp': 'UI', 'task': '마이페이지 다크 테마 적용', 'assignee': '한지원',
             'start_date': d(-7), 'end_date': d(-4), 'progress': 100, 'jira': 'QA-1103'},
            {'grp': 'UI', 'task': '모달·알림창 다크 테마 적용', 'assignee': '한지원',
             'start_date': d(-5), 'end_date': d(-2), 'progress': 90, 'jira': 'QA-1104'},
            {'grp': 'Smoke', 'task': '시스템 설정 자동 감지', 'assignee': '박수빈',
             'start_date': d(-3), 'end_date': d(0), 'progress': 80, 'jira': 'QA-1105'},
            {'grp': 'Smoke', 'task': '테마 전환 시 화면 새로고침 없이 반영', 'assignee': '박수빈',
             'start_date': d(-2), 'end_date': d(1), 'progress': 60, 'jira': 'QA-1106'},
            {'grp': 'Regression', 'task': '라이트 모드 정상 동작 확인', 'assignee': '정하늘',
             'start_date': d(0), 'end_date': d(3), 'progress': 20, 'jira': 'QA-1107'},
        ],
    },
    {
        'name': 'v2.3.0 푸시 알림 설정 추가',
        'description': '알림 카테고리별 on/off, 방해 금지 시간 설정 기능',
        'pm': '한지원',
        'end_date': d(-1),  # 오늘 기준 어제 종료 (완료 상태)
        'tasks': [
            {'grp': 'Smoke', 'task': '알림 설정 화면 진입', 'assignee': '한지원',
             'start_date': d(-18), 'end_date': d(-16), 'progress': 100, 'jira': 'QA-1001'},
            {'grp': 'Smoke', 'task': '카테고리별 on/off 토글', 'assignee': '한지원',
             'start_date': d(-16), 'end_date': d(-13), 'progress': 100, 'jira': 'QA-1002'},
            {'grp': 'Smoke', 'task': '방해 금지 시간 설정 저장', 'assignee': '정하늘',
             'start_date': d(-13), 'end_date': d(-10), 'progress': 100, 'jira': 'QA-1003'},
            {'grp': 'Regression', 'task': '기존 알림 수신 정상 동작', 'assignee': '박수빈',
             'start_date': d(-10), 'end_date': d(-7), 'progress': 100, 'jira': 'QA-1004'},
            {'grp': 'E2E', 'task': '방해 금지 시간 내 알림 차단 검증', 'assignee': '한지원',
             'start_date': d(-7), 'end_date': d(-3), 'progress': 100, 'jira': 'QA-1005'},
            {'grp': 'E2E', 'task': '설정 → 알림 수신 → 재설정 전체 플로우', 'assignee': '김민지',
             'start_date': d(-5), 'end_date': d(-1), 'progress': 100, 'jira': 'QA-1006'},
        ],
    },
    {
        'name': 'Hotfix v2.2.1 세션 토큰 처리',
        'description': '세션 만료 시 무한 로딩 버그 긴급 수정',
        'pm': '박수빈',
        'end_date': d(-12),
        'tasks': [
            {'grp': 'Smoke', 'task': '세션 만료 재현 확인', 'assignee': '박수빈',
             'start_date': d(-18), 'end_date': d(-17), 'progress': 100, 'jira': 'QA-0991'},
            {'grp': 'Smoke', 'task': '만료 시 로그인 화면 이동', 'assignee': '박수빈',
             'start_date': d(-16), 'end_date': d(-14), 'progress': 100, 'jira': 'QA-0992'},
            {'grp': 'Regression', 'task': '기존 세션 유지 정상 동작', 'assignee': '정하늘',
             'start_date': d(-14), 'end_date': d(-12), 'progress': 100, 'jira': 'QA-0993'},
        ],
    },
]


def main():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ DATABASE_URL 환경변수가 없어요.")
        print("   .env 파일에 DATABASE_URL 설정하거나 export 하세요.")
        sys.exit(1)

    print(f"🔌 연결 중: {dsn.split('@')[-1].split('/')[0]}")
    conn = psycopg2.connect(dsn)

    try:
        with conn.cursor() as cur:
            # 중복 방지: 같은 이름의 프로젝트가 이미 있으면 skip
            cur.execute("SELECT name FROM projects")
            existing = {row[0] for row in cur.fetchall()}

            inserted_projects = 0
            inserted_tasks = 0

            for proj in PROJECTS:
                if proj['name'] in existing:
                    print(f"⏭  이미 존재: {proj['name']} — skip")
                    continue

                pid = str(uuid.uuid4())[:8]
                now = datetime.now().strftime('%Y-%m-%d')

                cur.execute(
                    "INSERT INTO projects (id, name, description, pm, end_date, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (pid, proj['name'], proj['description'], proj['pm'], proj['end_date'], now)
                )
                inserted_projects += 1
                print(f"✅ Project: {proj['name']}  (end: {proj['end_date']}, PM: {proj['pm']})")

                for t in proj['tasks']:
                    tid = str(uuid.uuid4())[:8]
                    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cur.execute(
                        "INSERT INTO tasks (id, project_id, grp, task, assignee, start_date, end_date, progress, note, jira, created_at) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (tid, pid, t['grp'], t['task'], t['assignee'],
                         t['start_date'], t['end_date'], t['progress'], '', t.get('jira', ''), created)
                    )
                    inserted_tasks += 1

                print(f"   └─ {len(proj['tasks'])}개 태스크 삽입")

        conn.commit()
        print()
        print(f"🎉 완료: 프로젝트 {inserted_projects}개, 태스크 {inserted_tasks}개 추가")

    finally:
        conn.close()


if __name__ == "__main__":
    main()