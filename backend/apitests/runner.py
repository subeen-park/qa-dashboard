"""
API 테스트 실행 엔진

Postman Collection에서 파싱된 request 리스트를 순차 실행하고
각 request별 status/duration/pass 결과 반환.
"""

import time
from typing import Any, Dict, List

import requests


# 기본 Assertion: 2xx~3xx 를 pass 로 간주
DEFAULT_PASS_STATUS_MAX = 400
DEFAULT_TIMEOUT_SEC = 15


def run_collection(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """파싱된 collection 전체 실행. 결과 요약 반환."""
    requests_list = parsed.get("requests") or []
    results: List[Dict[str, Any]] = []
    passed = 0
    failed = 0

    for idx, req in enumerate(requests_list):
        result = _execute_request(req, idx + 1)
        results.append(result)
        if result["pass"]:
            passed += 1
        else:
            failed += 1

    return {
        "total": len(requests_list),
        "passed": passed,
        "failed": failed,
        "results": results,
    }


def _execute_request(req: Dict[str, Any], seq: int) -> Dict[str, Any]:
    method = (req.get("method") or "GET").upper()
    url = req.get("url") or ""
    headers = req.get("headers") or {}
    body = req.get("body")

    start = time.time()
    status_code = None
    duration_ms = 0
    error = None
    response_preview = None

    try:
        kwargs: Dict[str, Any] = {
            "headers": headers,
            "timeout": DEFAULT_TIMEOUT_SEC,
            "allow_redirects": True,
        }
        if isinstance(body, dict):
            # urlencoded / formdata
            content_type = (headers.get("Content-Type") or "").lower()
            if "json" in content_type:
                kwargs["json"] = body
            else:
                kwargs["data"] = body
        elif isinstance(body, str):
            # raw body (대개 JSON 문자열)
            kwargs["data"] = body.encode("utf-8")

        resp = requests.request(method, url, **kwargs)
        status_code = resp.status_code
        duration_ms = int((time.time() - start) * 1000)
        text = resp.text or ""
        response_preview = text[:300] + ("..." if len(text) > 300 else "")
    except requests.exceptions.Timeout:
        error = f"Timeout ({DEFAULT_TIMEOUT_SEC}s)"
        duration_ms = int((time.time() - start) * 1000)
    except requests.exceptions.ConnectionError as e:
        error = f"Connection error: {str(e)[:120]}"
        duration_ms = int((time.time() - start) * 1000)
    except Exception as e:
        error = f"{type(e).__name__}: {str(e)[:120]}"
        duration_ms = int((time.time() - start) * 1000)

    is_pass = (
        status_code is not None
        and status_code < DEFAULT_PASS_STATUS_MAX
        and error is None
    )

    return {
        "seq": seq,
        "name": req.get("name", "request"),
        "folder": req.get("folder", ""),
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "pass": is_pass,
        "error": error,
        "response_preview": response_preview,
    }