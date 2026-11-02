"""
공용 DB 커넥션 모듈
──────────────────────────────────
.env 자동 로드 + psycopg2 커넥션 컨텍스트 매니저.

사용:
    from db import get_conn
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM testcases")
        rows = cur.fetchall()
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv


# backend/.env 자동 로드
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "❌ DATABASE_URL 환경변수가 없어요.\n"
        "   backend/.env 파일에 다음을 추가하세요:\n"
        "   DATABASE_URL=postgresql://..."
    )


@contextmanager
def get_conn():
    """DB 커넥션 컨텍스트 매니저. 자동 commit/rollback/close."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()