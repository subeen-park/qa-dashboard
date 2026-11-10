"""
AI 기반 TC 생성 Flask Blueprint
"""

import os
import uuid

from flask import Blueprint, request, jsonify

from .generator import generate_testcase
from automation.queries import create_testcase

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.route("/generate-tc", methods=["POST"])
def generate_tc():
    """자연어 → TC 생성 + DB 저장."""
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    description = (data.get("description") or "").strip()
    category = data.get("category") or "Smoke"

    if not description:
        return jsonify({"error": "자연어 설명을 입력해주세요"}), 400
    if not url:
        return jsonify({"error": "target URL을 입력해주세요"}), 400

    try:
        tc_data = generate_testcase(url, description, category)
        source = tc_data.pop("_source", "unknown")

        tc_id = f"TC-AI-{uuid.uuid4().hex[:6].upper()}"
        saved = create_testcase({
            "id": tc_id,
            "title": tc_data.get("title", "[AI] 생성 TC"),
            "category": tc_data.get("category", category),
            "priority": tc_data.get("priority", "P2"),
            "target_url": url,
            "description": tc_data.get("description", description),
            "expected_result": tc_data.get("expected_result", "pass"),
            "steps": tc_data["steps"],
            "note": f"AI 생성 · source={source} · request={description[:60]}",
        })

        return jsonify({
            "ok": True,
            "testcase": saved,
            "source": source,
        })
    except Exception as e:
        return jsonify({"error": f"생성 실패: {e}"}), 500


@ai_bp.route("/health", methods=["GET"])
def health():
    """현재 AI 모드 상태 확인."""
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    return jsonify({
        "mode": "gemini" if has_key else "demo",
        "provider": "gemini-2.0-flash" if has_key else "demo-samples",
        "available_providers": ["gemini-2.0-flash", "demo"],
    })