"""
QA Hub 자동화 테스트 — Seed 스크립트
──────────────────────────────────────────────────
TC 5개를 이 파일에 하드코딩한 뒤 DB에 UPSERT.
이후 TC는 QA Hub UI에서 추가/수정/삭제하면 됩니다.

실행:
  export DATABASE_URL="postgresql://..."
  python seed_testcases.py
"""

import os
import sys
import psycopg2
from psycopg2.extras import Json


# ──────────── Seed TC 데이터 ────────────
TESTCASES = [
    {
        "id": "TC-001",
        "title": "로그인 성공 - 유효한 자격증명",
        "category": "smoke",
        "priority": "P1",
        "target_url": "https://www.saucedemo.com/",
        "description": "표준 사용자(standard_user)로 정상 로그인 시 상품 목록 페이지 노출 확인",
        "expected_result": "pass",
        "note": None,
        "steps": [
            {"action": "fill",           "selector": "#user-name",      "value": "standard_user", "description": "아이디 입력"},
            {"action": "fill",           "selector": "#password",       "value": "secret_sauce",  "description": "비밀번호 입력"},
            {"action": "click",          "selector": "#login-button",                             "description": "로그인 버튼 클릭"},
            {"action": "assert_url",     "expected": "/inventory.html",                           "description": "상품 목록 페이지 URL 전환 확인"},
            {"action": "assert_visible", "selector": ".inventory_list",                           "description": "상품 리스트 노출 확인"},
        ],
    },
    {
        "id": "TC-002",
        "title": "로그인 실패 - 잠긴 계정",
        "category": "regression",
        "priority": "P2",
        "target_url": "https://www.saucedemo.com/",
        "description": "잠긴 계정(locked_out_user)으로 로그인 시도 시 적절한 에러 메시지가 노출되는지 확인",
        "expected_result": "pass",
        "note": None,
        "steps": [
            {"action": "fill",           "selector": "#user-name",          "value": "locked_out_user",                           "description": "잠긴 계정 아이디 입력"},
            {"action": "fill",           "selector": "#password",           "value": "secret_sauce",                              "description": "비밀번호 입력"},
            {"action": "click",          "selector": "#login-button",                                                             "description": "로그인 버튼 클릭"},
            {"action": "assert_visible", "selector": "[data-test='error']",                                                       "description": "에러 메시지 영역 노출 확인"},
            {"action": "assert_text",    "selector": "[data-test='error']", "expected": "Sorry, this user has been locked out",  "description": "에러 메시지 내용 검증"},
            {"action": "assert_url",     "expected": "saucedemo.com/",                                                            "description": "로그인 페이지에 그대로 머무는지 확인"},
        ],
    },
    {
        "id": "TC-003",
        "title": "장바구니 상품 추가 - 뱃지 개수 반영",
        "category": "smoke",
        "priority": "P1",
        "target_url": "https://www.saucedemo.com/",
        "description": "로그인 후 상품을 장바구니에 추가하면 상단 뱃지에 수량이 정상 반영되는지 확인",
        "expected_result": "pass",
        "note": None,
        "steps": [
            {"action": "fill",           "selector": "#user-name",                                     "value": "standard_user", "description": "아이디 입력"},
            {"action": "fill",           "selector": "#password",                                      "value": "secret_sauce",  "description": "비밀번호 입력"},
            {"action": "click",          "selector": "#login-button",                                                            "description": "로그인"},
            {"action": "click",          "selector": "[data-test='add-to-cart-sauce-labs-backpack']",                            "description": "백팩 상품 Add to cart"},
            {"action": "assert_visible", "selector": ".shopping_cart_badge",                                                     "description": "장바구니 뱃지 노출 확인"},
            {"action": "assert_text",    "selector": ".shopping_cart_badge",                           "expected": "1",          "description": "장바구니 뱃지 수량 '1' 확인"},
            {"action": "click",          "selector": "[data-test='add-to-cart-sauce-labs-bike-light']",                          "description": "자전거 라이트 상품 Add to cart"},
            {"action": "assert_text",    "selector": ".shopping_cart_badge",                           "expected": "2",          "description": "장바구니 뱃지 수량 '2'로 증가 확인"},
        ],
    },
    {
        "id": "TC-004",
        "title": "결제 완료 플로우 (End-to-End)",
        "category": "e2e",
        "priority": "P1",
        "target_url": "https://www.saucedemo.com/",
        "description": "로그인 → 장바구니 담기 → 체크아웃 정보 입력 → 결제 완료까지 전체 결제 플로우 검증",
        "expected_result": "pass",
        "note": None,
        "steps": [
            {"action": "fill",        "selector": "#user-name",                                     "value": "standard_user", "description": "아이디 입력"},
            {"action": "fill",        "selector": "#password",                                      "value": "secret_sauce",  "description": "비밀번호 입력"},
            {"action": "click",       "selector": "#login-button",                                                            "description": "로그인"},
            {"action": "click",       "selector": "[data-test='add-to-cart-sauce-labs-backpack']",                            "description": "상품 장바구니 추가"},
            {"action": "click",       "selector": ".shopping_cart_link",                                                      "description": "장바구니 페이지 이동"},
            {"action": "assert_url",  "expected": "/cart.html",                                                               "description": "장바구니 URL 확인"},
            {"action": "click",       "selector": "[data-test='checkout']",                                                   "description": "Checkout 버튼 클릭"},
            {"action": "fill",        "selector": "[data-test='firstName']",                        "value": "수빈",          "description": "성 입력"},
            {"action": "fill",        "selector": "[data-test='lastName']",                         "value": "박",            "description": "이름 입력"},
            {"action": "fill",        "selector": "[data-test='postalCode']",                       "value": "13529",         "description": "우편번호 입력 (판교)"},
            {"action": "click",       "selector": "[data-test='continue']",                                                   "description": "Continue 버튼 클릭"},
            {"action": "click",       "selector": "[data-test='finish']",                                                     "description": "Finish 버튼 클릭"},
            {"action": "assert_url",  "expected": "/checkout-complete.html",                                                  "description": "결제 완료 URL 확인"},
            {"action": "assert_text", "selector": ".complete-header",                               "expected": "Thank you for your order!", "description": "결제 완료 메시지 확인"},
        ],
    },
    {
        "id": "TC-005",
        "title": "상품 이미지 검증 - problem_user (버그 재현)",
        "category": "regression",
        "priority": "P2",
        "target_url": "https://www.saucedemo.com/",
        "description": "problem_user 계정으로 로그인 시 상품 이미지가 올바르게 로드되는지 검증. 해당 계정은 '모든 상품 이미지가 404 placeholder로 치환되는' 버그가 심어져 있어 자동화가 이슈를 검출하는 사례. FAIL이 '정상 결과'.",
        "expected_result": "fail",
        "note": "포트폴리오 하이라이트 TC — '자동화가 실제 이슈를 검출하는 모습'을 보여주는 케이스. 통과하면 오히려 자동화가 버그를 못 잡은 것.",
        "steps": [
            {"action": "fill",             "selector": "#user-name",                                       "value": "problem_user", "description": "problem_user 아이디 입력"},
            {"action": "fill",             "selector": "#password",                                        "value": "secret_sauce", "description": "비밀번호 입력"},
            {"action": "click",            "selector": "#login-button",                                                             "description": "로그인"},
            {"action": "assert_visible",   "selector": ".inventory_list",                                                           "description": "상품 리스트 노출 확인"},
            {"action": "assert_attribute", "selector": ".inventory_item:first-child .inventory_item_img img", "attribute": "src", "contains": "backpack", "description": "첫 상품(백팩) 이미지 src에 'backpack' 포함 여부 검증 — problem_user에선 sl-404.jpg로 치환되어 FAIL 예상"},
        ],
    },
]


# ──────────── UPSERT 로직 ────────────
UPSERT_SQL = """
INSERT INTO testcases
    (id, title, category, priority, target_url, description, expected_result, steps, note)
VALUES
    (%(id)s, %(title)s, %(category)s, %(priority)s, %(target_url)s,
     %(description)s, %(expected_result)s, %(steps)s, %(note)s)
ON CONFLICT (id) DO UPDATE SET
    title           = EXCLUDED.title,
    category        = EXCLUDED.category,
    priority        = EXCLUDED.priority,
    target_url      = EXCLUDED.target_url,
    description     = EXCLUDED.description,
    expected_result = EXCLUDED.expected_result,
    steps           = EXCLUDED.steps,
    note            = EXCLUDED.note,
    updated_at      = NOW();
"""


def main():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ DATABASE_URL 환경변수가 없어요.")
        print("   PowerShell:  $env:DATABASE_URL = \"postgresql://...\"")
        sys.exit(1)

    print(f"🔌 Connecting to {dsn.split('@')[-1].split('/')[0]}...")
    conn = psycopg2.connect(dsn)
    try:
        for tc in TESTCASES:
            params = {**tc, "steps": Json(tc["steps"])}
            with conn.cursor() as cur:
                cur.execute(UPSERT_SQL, params)
            conn.commit()
            print(f"   ✓ {tc['id']} — {tc['title']}")
    finally:
        conn.close()

    print(f"\n✅ Seed done: {len(TESTCASES)}개 TC가 DB에 저장됨")
    print("   이후 TC 추가/수정/삭제는 QA Hub UI에서 하세요.")


if __name__ == "__main__":
    main()