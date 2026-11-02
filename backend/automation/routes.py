"""
Flask Blueprint — 자동화 테스트 API
──────────────────────────────────
TC CRUD + 러너 실행(비동기) + 실행 이력 + 라이브 스크린샷 폴링 + 결과물 서빙.

Blueprint 등록은 app.py에서:
    from automation.routes import automation_bp
    app.register_blueprint(automation_bp)

엔드포인트:
    GET    /api/testcases                               — TC 목록
    GET    /api/testcases/<tc_id>                       — TC 상세
    POST   /api/testcases                               — TC 생성
    PUT    /api/testcases/<tc_id>                       — TC 수정
    DELETE /api/testcases/<tc_id>                       — TC 삭제
    POST   /api/testcases/<tc_id>/run                   — 러너 실행 (즉시 run_id 반환, 백그라운드 실행)
    GET    /api/test-runs?tc_id=&limit=                 — 실행 이력
    GET    /api/test-runs/<run_id>                      — 실행 상세
    GET    /api/test-runs/<run_id>/latest-screenshot    — 라이브 폴링용 (가장 최근 스크린샷)
    GET    /api/output/screenshots/<run_id>/<filename>  — 특정 스크린샷
    GET    /api/output/videos/<filename>                — 녹화 영상
"""

import threading
from pathlib import Path
from flask import Blueprint, request, jsonify, send_from_directory, abort

from automation import queries
from automation.runners.web import WebRunner


automation_bp = Blueprint("automation", __name__)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


# ─────────────────────────────────────────────
# Testcases CRUD
# ─────────────────────────────────────────────

@automation_bp.route("/api/testcases", methods=["GET"])
def api_list_testcases():
    return jsonify(queries.list_testcases())


@automation_bp.route("/api/testcases/<tc_id>", methods=["GET"])
def api_get_testcase(tc_id):
    tc = queries.get_testcase(tc_id)
    if not tc:
        return jsonify({"error": "Testcase not found"}), 404
    return jsonify(tc)


@automation_bp.route("/api/testcases", methods=["POST"])
def api_create_testcase():
    data = request.get_json() or {}
    required = ["id", "title", "target_url", "steps"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    try:
        tc = queries.create_testcase(data)
        return jsonify(tc), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@automation_bp.route("/api/testcases/<tc_id>", methods=["PUT"])
def api_update_testcase(tc_id):
    data = request.get_json() or {}
    tc = queries.update_testcase(tc_id, data)
    if not tc:
        return jsonify({"error": "Testcase not found"}), 404
    return jsonify(tc)


@automation_bp.route("/api/testcases/<tc_id>", methods=["DELETE"])
def api_delete_testcase(tc_id):
    if not queries.delete_testcase(tc_id):
        return jsonify({"error": "Testcase not found"}), 404
    return "", 204


# ─────────────────────────────────────────────
# 러너 실행 (비동기 — 백그라운드 스레드)
# ─────────────────────────────────────────────

@automation_bp.route("/api/testcases/<tc_id>/run", methods=["POST"])
def api_run_testcase(tc_id):
    tc = queries.get_testcase(tc_id)
    if not tc:
        return jsonify({"error": "Testcase not found"}), 404

    # Run 레코드 먼저 생성 (status='queued')
    run_id = queries.create_test_run(tc_id)

    # 백그라운드 스레드에서 러너 실행
    thread = threading.Thread(
        target=_run_in_background,
        args=(run_id, tc),
        daemon=True,
    )
    thread.start()

    return jsonify({"run_id": run_id, "status": "queued"}), 202


def _run_in_background(run_id, tc):
    """백그라운드 스레드에서 러너 실행 + DB 업데이트."""
    try:
        queries.update_test_run(run_id, status="running")

        runner = WebRunner(
            run_id=run_id,
            target_url=tc["target_url"],
            headless=True,   # 서버는 항상 headless
        )
        result = runner.run(tc)

        queries.update_test_run(
            run_id,
            status=result["status"],
            started_at=result["started_at"],
            ended_at=result["ended_at"],
            duration_ms=result["duration_ms"],
            step_results=result["step_results"],
            error_message=result.get("error_message"),
            screenshot_dir=result["screenshot_dir"],
            video_path=result.get("video_path"),
        )
    except Exception as e:
        queries.update_test_run(
            run_id,
            status="error",
            error_message=str(e),
        )


# ─────────────────────────────────────────────
# Test Runs 조회
# ─────────────────────────────────────────────

@automation_bp.route("/api/test-runs", methods=["GET"])
def api_list_test_runs():
    tc_id = request.args.get("tc_id")
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        limit = 50
    return jsonify(queries.list_test_runs(limit=limit, tc_id=tc_id))


@automation_bp.route("/api/test-runs/<int:run_id>", methods=["GET"])
def api_get_test_run(run_id):
    run = queries.get_test_run(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(run)


# ─────────────────────────────────────────────
# 라이브 폴링 — 가장 최근 스크린샷
# ─────────────────────────────────────────────

@automation_bp.route("/api/test-runs/<int:run_id>/latest-screenshot", methods=["GET"])
def api_latest_screenshot(run_id):
    """실행 중인 Run의 최신 스크린샷을 반환. 프론트가 500ms마다 폴링."""
    screenshot_dir = OUTPUT_DIR / "screenshots" / str(run_id)
    if not screenshot_dir.exists():
        return "", 204

    pngs = sorted(screenshot_dir.glob("step_*.png"))
    if not pngs:
        return "", 204

    latest = pngs[-1]
    return send_from_directory(
        str(screenshot_dir),
        latest.name,
        mimetype="image/png",
    )


# ─────────────────────────────────────────────
# 결과물 (스크린샷 · 영상) 서빙
# ─────────────────────────────────────────────

@automation_bp.route("/api/output/screenshots/<int:run_id>/<filename>", methods=["GET"])
def api_serve_screenshot(run_id, filename):
    folder = OUTPUT_DIR / "screenshots" / str(run_id)
    if not folder.exists():
        abort(404)
    return send_from_directory(str(folder), filename, mimetype="image/png")


@automation_bp.route("/api/output/videos/<filename>", methods=["GET"])
def api_serve_video(filename):
    folder = OUTPUT_DIR / "videos"
    if not folder.exists():
        abort(404)
    return send_from_directory(str(folder), filename, mimetype="video/webm")