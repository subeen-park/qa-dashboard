"""
Postman Collection v2.1 파서

Collection JSON을 받아 평평한 request 리스트로 변환.
folder (하위 item[]) 재귀 순회 지원.
"""

from typing import Any, Dict, List


def parse_collection(data: Dict[str, Any]) -> Dict[str, Any]:
    """Postman Collection v2.1 → 메타 + 평평한 request 리스트."""
    info = data.get("info", {})
    items = data.get("item", []) or []

    requests = []
    _walk_items(items, requests, folder_path=[])

    return {
        "name": info.get("name", "Untitled Collection"),
        "description": info.get("description") or "",
        "schema": info.get("schema", ""),
        "requests": requests,
    }


def _walk_items(items: List[Dict[str, Any]], out: List[Dict[str, Any]], folder_path: List[str]):
    """item[] 재귀 순회. folder는 하위에 다시 item[] 가짐."""
    for item in items:
        if "item" in item:
            _walk_items(item["item"], out, folder_path + [item.get("name", "")])
        elif "request" in item:
            parsed = _parse_request(item, folder_path)
            if parsed:
                out.append(parsed)


def _parse_request(item: Dict[str, Any], folder_path: List[str]) -> Dict[str, Any]:
    req = item.get("request", {})
    if isinstance(req, str):
        # 간단한 "GET https://..." 형태
        parts = req.split(" ", 1)
        return {
            "name": item.get("name", "request"),
            "method": parts[0] if parts else "GET",
            "url": parts[1] if len(parts) > 1 else "",
            "headers": {},
            "body": None,
            "folder": " / ".join(folder_path) if folder_path else "",
        }

    method = (req.get("method") or "GET").upper()
    url = _extract_url(req.get("url"))
    headers = _extract_headers(req.get("header") or [])
    body = _extract_body(req.get("body"))

    return {
        "name": item.get("name", "request"),
        "method": method,
        "url": url,
        "headers": headers,
        "body": body,
        "folder": " / ".join(folder_path) if folder_path else "",
    }


def _extract_url(url_field: Any) -> str:
    if isinstance(url_field, str):
        return url_field
    if isinstance(url_field, dict):
        raw = url_field.get("raw")
        if raw:
            return raw
        # 재조립
        proto = url_field.get("protocol", "https")
        host = url_field.get("host") or []
        if isinstance(host, list):
            host_str = ".".join(host)
        else:
            host_str = str(host)
        path = url_field.get("path") or []
        if isinstance(path, list):
            path_str = "/" + "/".join(path)
        else:
            path_str = "/" + str(path)
        base = f"{proto}://{host_str}{path_str}"
        query = url_field.get("query") or []
        if query:
            qs = "&".join(
                f"{q.get('key','')}={q.get('value','')}"
                for q in query if not q.get("disabled")
            )
            if qs:
                base = f"{base}?{qs}"
        return base
    return ""


def _extract_headers(headers: List[Dict[str, Any]]) -> Dict[str, str]:
    result = {}
    for h in headers:
        if h.get("disabled"):
            continue
        key = h.get("key")
        value = h.get("value", "")
        if key:
            result[key] = value
    return result


def _extract_body(body_field: Any) -> Any:
    if not body_field:
        return None
    mode = body_field.get("mode")
    if mode == "raw":
        return body_field.get("raw") or None
    if mode == "urlencoded":
        pairs = body_field.get("urlencoded") or []
        return {p.get("key"): p.get("value") for p in pairs if not p.get("disabled")}
    if mode == "formdata":
        pairs = body_field.get("formdata") or []
        return {p.get("key"): p.get("value") for p in pairs if not p.get("disabled")}
    return None