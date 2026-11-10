"""
testcases 테이블 마이그레이션 — level 컬럼 추가 + 기존 TC 재매핑

Level (테스트 티어): Smoke / Regression / E2E
Domain (대상): category 컬럼 재활용 (로그인/결제/장바구니/이미지/...)

실행:
  cd backend
  python migrate_add_level.py
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ─────────── 기존 TC 재매핑 규칙 ───────────
# 기존 Seed TC 5개를 2단 체계로 수동 매핑.
# AI 생성 TC는 이미 category 들어가 있으므로 건드리지 않음.
LEGACY_MAPPING = {
    "TC-001": {"level": "Smoke",      "category": "로그인"},
    "TC-002": {"level": "Smoke",      "category": "로그인"},
    "TC-003": {"level": "Regression", "category": "장바구니"},
    "TC-004": {"level": "E2E",        "category": "결제"},
    "TC-005": {"level": "Regression", "category": "이미지"},
}


def main():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ DATABASE_URL 환경변수가 없어요.")
        sys.exit(1)

    print(f"🔌 연결: {dsn.split('@')[-1].split('/')[0]}")
    conn = psycopg2.connect(dsn)

    try:
        with conn.cursor() as cur:
            # 1. level 컬럼 추가 (이미 있으면 skip)
            print("\n[1/3] level 컬럼 추가...")
            cur.execute("""
                ALTER TABLE testcases
                ADD COLUMN IF NOT EXISTS level VARCHAR(16);
            """)
            print("   ✓ 완료")

            # 2. 기존 TC 재매핑
            print("\n[2/3] 기존 Seed TC 재매핑...")
            updated = 0
            for tc_id, mapping in LEGACY_MAPPING.items():
                cur.execute("""
                    UPDATE testcases
                    SET level = %s, category = %s, updated_at = NOW()
                    WHERE id = %s
                    RETURNING id
                """, (mapping["level"], mapping["category"], tc_id))
                if cur.fetchone():
                    print(f"   ✓ {tc_id}  →  level={mapping['level']}, category={mapping['category']}")
                    updated += 1
                else:
                    print(f"   ⏭ {tc_id} 없음 (skip)")
            print(f"   총 {updated}개 재매핑")

            # 3. level이 비어있는 다른 TC (AI 생성 등) 는 기본값 Smoke
            print("\n[3/3] level 미설정 TC 기본값 Smoke 로...")
            cur.execute("""
                UPDATE testcases
                SET level = 'Smoke'
                WHERE level IS NULL OR level = ''
                RETURNING id
            """)
            rows = cur.fetchall()
            print(f"   {len(rows)}개 TC level = Smoke 로 설정")

        conn.commit()
        print("\n🎉 마이그레이션 완료")

    finally:
        conn.close()


if __name__ == "__main__":
    main()