"""
자동화 테스트 DB 쿼리 레이어
──────────────────────────────────
testcases, test_runs 테이블 CRUD.
routes.py에서 import해서 사용. (SQL은 여기만 있음)
"""

from db import get_conn
from psycopg2.extras import Json


# ───────────── Testcases ─────────────

def list_testcases():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, category, priority, target_url, description,
                   expected_result, steps, note, created_at, updated_at
            FROM testcases
            ORDER BY id
        """)
        return [dict(r) for r in cur.fetchall()]


def get_testcase(tc_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM testcases WHERE id = %s", (tc_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_testcase(data):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO testcases
                (id, title, category, priority, target_url, description,
                 expected_result, steps, note)
            VALUES
                (%(id)s, %(title)s, %(category)s, %(priority)s, %(target_url)s,
                 %(description)s, %(expected_result)s, %(steps)s, %(note)s)
            RETURNING *
        """, {
            "id":              data["id"],
            "title":           data["title"],
            "category":        data.get("category"),
            "priority":        data.get("priority"),
            "target_url":      data["target_url"],
            "description":     data.get("description"),
            "expected_result": data.get("expected_result"),
            "steps":           Json(data["steps"]),
            "note":            data.get("note"),
        })
        return dict(cur.fetchone())


def update_testcase(tc_id, data):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE testcases SET
                title           = %(title)s,
                category        = %(category)s,
                priority        = %(priority)s,
                target_url      = %(target_url)s,
                description     = %(description)s,
                expected_result = %(expected_result)s,
                steps           = %(steps)s,
                note            = %(note)s,
                updated_at      = NOW()
            WHERE id = %(id)s
            RETURNING *
        """, {
            "id":              tc_id,
            "title":           data["title"],
            "category":        data.get("category"),
            "priority":        data.get("priority"),
            "target_url":      data["target_url"],
            "description":     data.get("description"),
            "expected_result": data.get("expected_result"),
            "steps":           Json(data["steps"]),
            "note":            data.get("note"),
        })
        row = cur.fetchone()
        return dict(row) if row else None


def delete_testcase(tc_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM testcases WHERE id = %s RETURNING id", (tc_id,))
        return cur.fetchone() is not None


# ───────────── Test Runs ─────────────

def create_test_run(tc_id):
    """새 실행 레코드 만들고 id 반환."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO test_runs (tc_id, status)
            VALUES (%s, 'queued')
            RETURNING id
        """, (tc_id,))
        return cur.fetchone()["id"]


def update_test_run(run_id, **fields):
    """실행 결과 업데이트. JSONB 필드는 자동 wrap."""
    if not fields:
        return

    # step_results는 JSONB
    if "step_results" in fields and fields["step_results"] is not None:
        fields["step_results"] = Json(fields["step_results"])

    set_parts = ", ".join(f"{k} = %({k})s" for k in fields.keys())
    params = {**fields, "run_id": run_id}

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(f"""
            UPDATE test_runs SET {set_parts}
            WHERE id = %(run_id)s
        """, params)


def list_test_runs(limit=50, tc_id=None):
    """실행 이력. tc_id 지정 시 그 TC의 이력만."""
    query = """
        SELECT tr.id, tr.tc_id, tr.status, tr.started_at, tr.ended_at,
               tr.duration_ms, tr.error_message, tr.video_path, tr.screenshot_dir,
               tc.title AS tc_title, tc.category AS tc_category,
               tc.priority AS tc_priority, tc.expected_result AS tc_expected
        FROM test_runs tr
        LEFT JOIN testcases tc ON tr.tc_id = tc.id
    """
    params = []
    if tc_id:
        query += " WHERE tr.tc_id = %s"
        params.append(tc_id)
    query += " ORDER BY tr.started_at DESC LIMIT %s"
    params.append(limit)

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]


def get_test_run(run_id):
    """실행 상세 (step_results 포함)."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT tr.*, tc.title AS tc_title, tc.target_url AS tc_target_url,
                   tc.expected_result AS tc_expected
            FROM test_runs tr
            LEFT JOIN testcases tc ON tr.tc_id = tc.id
            WHERE tr.id = %s
        """, (run_id,))
        row = cur.fetchone()
        return dict(row) if row else None