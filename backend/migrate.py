"""
QA Hub 자동화 테스트 — DB 마이그레이션 스크립트
──────────────────────────────────────────────────
2개 테이블 생성:
  1. testcases  — TC 저장 (steps는 JSONB로 통째 보관)
  2. test_runs  — TC 실행 결과 이력

실행 방법 (로컬 또는 Render shell):
  export DATABASE_URL="postgresql://..."
  python migrate.py

Render 배포 환경이면 Render 대시보드에서 Shell 열고 그대로 실행.
"""

import os
import sys
import psycopg2


SCHEMA_SQL = """
-- ─────────── testcases ───────────
CREATE TABLE IF NOT EXISTS testcases (
    id              VARCHAR(32)  PRIMARY KEY,
    title           TEXT         NOT NULL,
    category        VARCHAR(32),               -- smoke / regression / e2e
    priority        VARCHAR(8),                -- P1 / P2 / P3
    target_url      TEXT,
    description     TEXT,
    expected_result VARCHAR(16),               -- pass / fail (의도된 결과)
    steps           JSONB        NOT NULL,     -- 스텝 배열 통째 저장
    note            TEXT,
    created_at      TIMESTAMPTZ  DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  DEFAULT NOW()
);

-- ─────────── test_runs ───────────
CREATE TABLE IF NOT EXISTS test_runs (
    id              SERIAL       PRIMARY KEY,
    tc_id           VARCHAR(32)  REFERENCES testcases(id) ON DELETE CASCADE,
    status          VARCHAR(16),               -- queued / running / pass / fail / error
    started_at      TIMESTAMPTZ  DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,
    duration_ms     INTEGER,
    step_results    JSONB,                     -- 스텝별 결과·스크린샷·로그
    error_message   TEXT,
    video_path      TEXT,                      -- Playwright 녹화 영상 경로
    screenshot_dir  TEXT                       -- 폴링용 스크린샷 디렉토리
);

CREATE INDEX IF NOT EXISTS idx_test_runs_tc_id      ON test_runs(tc_id);
CREATE INDEX IF NOT EXISTS idx_test_runs_started_at ON test_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_test_runs_status     ON test_runs(status);

-- ─────────── updated_at 자동 갱신 트리거 ───────────
CREATE OR REPLACE FUNCTION trg_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_testcases_updated_at ON testcases;
CREATE TRIGGER trg_testcases_updated_at
    BEFORE UPDATE ON testcases
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();
"""


def main():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ DATABASE_URL 환경변수가 없어요.")
        print("   export DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
        sys.exit(1)

    print(f"🔌 Connecting to {dsn.split('@')[-1].split('/')[0]}...")
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()
        print("✅ Migration done: testcases, test_runs 테이블 생성 완료")
    finally:
        conn.close()


if __name__ == "__main__":
    main()