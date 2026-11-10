"""
AI 자동화 TC 생성기
────────────────────
자연어 설명 → Playwright TC JSON.

지원 Provider:
- Gemini 2.0 Flash (환경변수 GEMINI_API_KEY)
- Demo 모드 폴백 (키 없을 때 샘플 TC 반환)

Provider 추상화를 가볍게 두고, 공개 저장소에서도 데모 모드로
기본 작동하게 설계. 포폴 관점에서 "AI Native 설계"와 "키 없이도
동작하는 폴백"을 동시에 어필.
"""

import json
import os
import re
from typing import Any, Dict

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# ─────────── Playwright 액션 포맷 (자동화 엔진과 동일) ───────────
ACTIONS_DOC = """
- goto           { "url": "..." }
- fill           { "selector": "...", "value": "..." }
- click          { "selector": "..." }
- wait           { "ms": 1000 }
- wait_for       { "selector": "..." }
- assert_visible { "selector": "..." }
- assert_text    { "selector": "...", "expected": "..." }
- assert_url     { "expected": "..." }
- assert_attribute { "selector": "...", "attribute": "src", "contains": "..." }
- screenshot     (추가 필드 없음)
"""


PROMPT_TEMPLATE = """당신은 QA 자동화 전문가입니다.
주어진 요구사항으로 Playwright 기반 웹 자동화 테스트 케이스를 JSON으로 생성하세요.

## 대상
- URL: {url}
- 요청: {description}
- Level (테스트 티어): {level}
- Domain (대상 영역): {category}

## 지원 액션 (steps 배열)
{actions}

## 응답 형식 (JSON만, 코드블록이나 설명 없이)
{{
  "title": "TC의 짧은 제목 (한국어)",
  "description": "TC가 검증하는 시나리오 1-2줄",
  "level": "{level}",
  "category": "{category}",
  "priority": "P1" | "P2" | "P3",
  "expected_result": "pass" | "fail",
  "steps": [
    {{"action": "goto", "url": "{url}"}},
    ...
  ]
}}

주의:
1. steps는 반드시 goto로 시작
2. selector는 CSS 선택자 (id는 #, class는 ., data-test는 [data-test='...'])
3. 검증 단계(assert_*)를 반드시 포함
4. JSON 외 다른 텍스트 쓰지 말 것
"""


# ─────────── 데모 모드용 샘플 ───────────
# 공개 저장소에서 API 키 없이도 동작하도록 키워드 매칭으로 샘플 반환.
# saucedemo.com 기반 (자동화 엔진의 Seed TC와 같은 사이트).
DEMO_SAMPLES = [
    {
        "keywords": ["로그인", "login", "signin", "성공"],
        "tc": {
            "title": "로그인 성공 - 유효한 자격증명",
            "description": "유효한 아이디/비밀번호로 로그인 시 메인 페이지로 이동",
            "level": "Smoke",
            "category": "로그인",
            "priority": "P1",
            "expected_result": "pass",
            "steps": [
                {"action": "goto", "url": "__URL__"},
                {"action": "fill", "selector": "#user-name", "value": "standard_user"},
                {"action": "fill", "selector": "#password", "value": "secret_sauce"},
                {"action": "click", "selector": "#login-button"},
                {"action": "assert_url", "expected": "/inventory.html"},
                {"action": "assert_visible", "selector": ".inventory_list"},
            ],
        },
    },
    {
        "keywords": ["잠긴", "locked", "실패", "fail", "invalid"],
        "tc": {
            "title": "로그인 실패 - 잠긴 계정",
            "description": "잠긴 계정으로 로그인 시 에러 메시지 표시",
            "level": "Smoke",
            "category": "로그인",
            "priority": "P1",
            "expected_result": "pass",
            "steps": [
                {"action": "goto", "url": "__URL__"},
                {"action": "fill", "selector": "#user-name", "value": "locked_out_user"},
                {"action": "fill", "selector": "#password", "value": "secret_sauce"},
                {"action": "click", "selector": "#login-button"},
                {"action": "assert_text", "selector": "[data-test='error']", "expected": "Epic sadface"},
            ],
        },
    },
    {
        "keywords": ["장바구니", "cart", "추가", "add"],
        "tc": {
            "title": "장바구니 상품 추가 - 뱃지 반영",
            "description": "상품을 장바구니에 추가하면 상단 뱃지에 수량 반영",
            "level": "Regression",
            "category": "장바구니",
            "priority": "P1",
            "expected_result": "pass",
            "steps": [
                {"action": "goto", "url": "__URL__"},
                {"action": "fill", "selector": "#user-name", "value": "standard_user"},
                {"action": "fill", "selector": "#password", "value": "secret_sauce"},
                {"action": "click", "selector": "#login-button"},
                {"action": "click", "selector": "[data-test='add-to-cart-sauce-labs-backpack']"},
                {"action": "assert_text", "selector": ".shopping_cart_badge", "expected": "1"},
            ],
        },
    },
    {
        "keywords": ["결제", "checkout", "payment", "주문"],
        "tc": {
            "title": "결제 완료 End-to-End",
            "description": "로그인 → 상품 추가 → 결제 정보 입력 → 주문 완료",
            "level": "E2E",
            "category": "결제",
            "priority": "P1",
            "expected_result": "pass",
            "steps": [
                {"action": "goto", "url": "__URL__"},
                {"action": "fill", "selector": "#user-name", "value": "standard_user"},
                {"action": "fill", "selector": "#password", "value": "secret_sauce"},
                {"action": "click", "selector": "#login-button"},
                {"action": "click", "selector": "[data-test='add-to-cart-sauce-labs-backpack']"},
                {"action": "click", "selector": ".shopping_cart_link"},
                {"action": "click", "selector": "#checkout"},
                {"action": "fill", "selector": "#first-name", "value": "Subeen"},
                {"action": "fill", "selector": "#last-name", "value": "Park"},
                {"action": "fill", "selector": "#postal-code", "value": "12345"},
                {"action": "click", "selector": "#continue"},
                {"action": "click", "selector": "#finish"},
                {"action": "assert_text", "selector": ".complete-header", "expected": "Thank you"},
            ],
        },
    },
    {
        "keywords": ["이미지", "image", "깨짐", "problem"],
        "tc": {
            "title": "이미지 깨짐 검증 - problem_user",
            "description": "problem_user 계정에서 상품 이미지가 기본 404 이미지로 치환되는 결함 검출",
            "level": "Regression",
            "category": "이미지",
            "priority": "P1",
            "expected_result": "fail",
            "steps": [
                {"action": "goto", "url": "__URL__"},
                {"action": "fill", "selector": "#user-name", "value": "problem_user"},
                {"action": "fill", "selector": "#password", "value": "secret_sauce"},
                {"action": "click", "selector": "#login-button"},
                {"action": "assert_attribute", "selector": ".inventory_item_img img", "attribute": "src", "contains": "sl-404"},
            ],
        },
    },
]


# ─────────── 메인 API ───────────

def generate_testcase(url: str, description: str, level: str = "Smoke", category: str = "기타") -> Dict[str, Any]:
    """자연어 → Playwright TC JSON.

    - level: 테스트 티어 (Smoke / Regression / E2E)
    - category: 도메인 (로그인/결제/장바구니/이미지/...)
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key and GEMINI_AVAILABLE:
        try:
            tc = _generate_with_gemini(url, description, level, category, api_key)
            return tc
        except Exception as e:
            print(f"[AI] Gemini 호출 실패 → 데모 폴백: {e}")
            return _generate_demo(url, description, level, category)
    return _generate_demo(url, description, level, category)


def _generate_with_gemini(url: str, description: str, level: str, category: str, api_key: str) -> Dict[str, Any]:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = PROMPT_TEMPLATE.format(
        url=url,
        description=description,
        level=level,
        category=category,
        actions=ACTIONS_DOC,
    )
    response = model.generate_content(prompt)
    text = (response.text or "").strip()

    # 마크다운 코드 펜스 제거
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    data = json.loads(text)
    data["_source"] = "gemini-2.0-flash"
    return data


def _generate_demo(url: str, description: str, level: str, category: str) -> Dict[str, Any]:
    desc_lower = description.lower()
    best_match = None
    best_score = 0
    for sample in DEMO_SAMPLES:
        score = sum(1 for kw in sample["keywords"] if kw.lower() in desc_lower)
        if score > best_score:
            best_score = score
            best_match = sample

    if best_match and best_score > 0:
        tc = json.loads(json.dumps(best_match["tc"]))  # deep copy
        # 샘플의 level/category 유지 (매칭된 TC의 원래 분류가 자연스러움)
    else:
        tc = {
            "title": f"[데모] {description[:40]}",
            "description": description,
            "level": level,
            "category": category,
            "priority": "P2",
            "expected_result": "pass",
            "steps": [
                {"action": "goto", "url": url},
                {"action": "assert_visible", "selector": "body"},
            ],
        }

    # URL 치환
    for step in tc["steps"]:
        if step.get("action") == "goto" and step.get("url") == "__URL__":
            step["url"] = url

    tc["_source"] = "demo"
    return tc