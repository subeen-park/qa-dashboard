"""
API 테스트 DB 쿼리 레이어
"""

from db import get_conn
from psycopg2.extras import Json


# ───────────── Collections ─────────────

def list_collections():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, description, request_count, created_at
            FROM api_collections
            ORDER BY created_at DESC
        """)
        return [dict(r) for r in cur.fetchall()]


def get_collection(coll_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM api_collections WHERE id = %s", (coll_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_collection(name, description, raw_json, request_count):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_collections (name, description, raw_json, request_count)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, description, request_count, created_at
        """, (name, description, Json(raw_json), request_count))
        return dict(cur.fetchone())


def delete_collection(coll_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM api_collections WHERE id = %s RETURNING id", (coll_id,))
        return cur.fetchone() is not None


# ───────────── Runs ─────────────

def create_run(collection_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_runs (collection_id, status)
            VALUES (%s, 'queued')
            RETURNING id
        """, (collection_id,))
        return cur.fetchone()["id"]


def update_run(run_id, **fields):
    if not fields:
        return
    if "results" in fields and fields["results"] is not None:
        fields["results"] = Json(fields["results"])

    set_parts = ", ".join(f"{k} = %({k})s" for k in fields.keys())
    params = {**fields, "run_id": run_id}
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE api_runs SET {set_parts} WHERE id = %(run_id)s", params)


def list_runs(limit=30, collection_id=None):
    query = """
        SELECT r.id, r.collection_id, r.status, r.total, r.passed, r.failed,
               r.started_at, r.ended_at, c.name AS collection_name
        FROM api_runs r
        LEFT JOIN api_collections c ON r.collection_id = c.id
    """
    params = []
    if collection_id:
        query += " WHERE r.collection_id = %s"
        params.append(collection_id)
    query += " ORDER BY r.started_at DESC LIMIT %s"
    params.append(limit)

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]


def get_run(run_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT r.*, c.name AS collection_name
            FROM api_runs r
            LEFT JOIN api_collections c ON r.collection_id = c.id
            WHERE r.id = %s
        """, (run_id,))
        row = cur.fetchone()
        return dict(row) if row else None