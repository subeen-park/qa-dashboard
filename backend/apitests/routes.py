"""
API 테스트 Flask Blueprint

- /api/apitests/collections              GET/POST
- /api/apitests/collections/:id          GET/DELETE
- /api/apitests/collections/:id/run      POST   (백그라운드 실행)
- /api/apitests/runs                     GET
- /api/apitests/runs/:id                 GET
"""

import threading
from datetime import datetime

from flask import Blueprint, jsonify, request

from . import queries
from .parser import parse_collection
from .runner import run_collection


apitests_bp = Blueprint("apitests", __name__, url_prefix="/api/apitests")


# ───────── Collections ─────────

@apitests_bp.route("/collections", methods=["GET"])
def list_colls():
    return jsonify(queries.list_collections())


@apitests_bp.route("/collections/<int:coll_id>", methods=["GET"])
def get_coll(coll_id):
    coll = queries.get_collection(coll_id)
    if not coll:
        return jsonify({"error": "not found"}), 404
    # 파싱된 request 목록도 함께
    parsed = parse_collection(coll["raw_json"])
    coll["parsed"] = parsed
    return jsonify(coll)


@apitests_bp.route("/collections", methods=["POST"])
def upload_coll():
    """Postman Collection v2.1 JSON 업로드.

    Body (JSON): { "raw_json": { ... Postman Collection ... } }
    """
    body = request.get_json(silent=True) or {}
    raw = body.get("raw_json")
    if not raw or not isinstance(raw, dict):
        return jsonify({"error": "raw_json (Postman Collection) 필수"}), 400

    try:
        parsed = parse_collection(raw)
    except Exception as e:
        return jsonify({"error": f"파싱 실패: {e}"}), 400

    saved = queries.create_collection(
        name=parsed["name"],
        description=parsed.get("description") or "",
        raw_json=raw,
        request_count=len(parsed.get("requests") or []),
    )
    return jsonify(saved), 201


@apitests_bp.route("/collections/<int:coll_id>", methods=["DELETE"])
def delete_coll(coll_id):
    ok = queries.delete_collection(coll_id)
    return jsonify({"ok": ok})


# ───────── Runs ─────────

@apitests_bp.route("/collections/<int:coll_id>/run", methods=["POST"])
def start_run(coll_id):
    coll = queries.get_collection(coll_id)
    if not coll:
        return jsonify({"error": "collection not found"}), 404

    run_id = queries.create_run(coll_id)
    # 백그라운드 스레드로 실행
    t = threading.Thread(target=_run_background, args=(run_id, coll["raw_json"]), daemon=True)
    t.start()
    return jsonify({"run_id": run_id, "status": "queued"}), 202


def _run_background(run_id, raw_json):
    try:
        queries.update_run(run_id, status="running")
        parsed = parse_collection(raw_json)
        summary = run_collection(parsed)
        queries.update_run(
            run_id,
            status="done",
            total=summary["total"],
            passed=summary["passed"],
            failed=summary["failed"],
            results=summary["results"],
            ended_at=datetime.utcnow(),
        )
    except Exception as e:
        queries.update_run(
            run_id,
            status="error",
            error_message=str(e)[:500],
            ended_at=datetime.utcnow(),
        )


@apitests_bp.route("/runs", methods=["GET"])
def list_runs():
    coll_id = request.args.get("collection_id", type=int)
    limit = request.args.get("limit", default=30, type=int)
    return jsonify(queries.list_runs(limit=limit, collection_id=coll_id))


@apitests_bp.route("/runs/<int:run_id>", methods=["GET"])
def get_run(run_id):
    run = queries.get_run(run_id)
    if not run:
        return jsonify({"error": "not found"}), 404
    return jsonify(run)