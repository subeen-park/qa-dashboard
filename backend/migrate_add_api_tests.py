"""
API 테스트 테이블 마이그레이션

- api_collections: Postman Collection 업로드 보관
- api_runs: 실행 결과 (요청별 status/duration 포함)

실행:
  cd backend
  python migrate_add_api_tests.py
"""

import os
import sys
import psycopg2

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


SCHEMA_SQL = """
-- ─────────── api_collections ───────────
CREATE TABLE IF NOT EXISTS api_collections (
    id          SERIAL       PRIMARY KEY,
    name        TEXT         NOT NULL,
    description TEXT,
    raw_json    JSONB        NOT NULL,
    request_count INT        DEFAULT 0,
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);

-- ─────────── api_runs ───────────
CREATE TABLE IF NOT EXISTS api_runs (
    id            SERIAL       PRIMARY KEY,
    collection_id INT          REFERENCES api_collections(id) ON DELETE CASCADE,
    status        VARCHAR(16)  DEFAULT 'queued',
    total         INT          DEFAULT 0,
    passed        INT          DEFAULT 0,
    failed        INT          DEFAULT 0,
    results       JSONB,
    started_at    TIMESTAMPTZ  DEFAULT NOW(),
    ended_at      TIMESTAMPTZ,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_api_runs_collection ON api_runs(collection_id);
CREATE INDEX IF NOT EXISTS idx_api_runs_started ON api_runs(started_at DESC);
"""


def main():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("DATABASE_URL 환경변수 필요")
        sys.exit(1)

    print(f"연결: {dsn.split('@')[-1].split('/')[0]}")
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()
        print("완료: api_collections, api_runs 생성됨")
    finally:
        conn.close()


if __name__ == "__main__":
    main()