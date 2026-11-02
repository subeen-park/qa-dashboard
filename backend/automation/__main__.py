"""
automation 패키지 CLI — TC 하나를 직접 실행해보는 테스트 도구
──────────────────────────────────
Flask API 올리기 전에 러너가 제대로 돌아가는지 터미널에서 확인용.

사용:
    python -m automation TC-001                # 백그라운드 (headless)
    python -m automation TC-001 --headed       # 브라우저 창 띄움 (실시간 눈으로 봄)
    python -m automation TC-005 --headed       # 실패 재현 (버그 검출 데모)
"""

import argparse
import sys
from db import get_conn
from automation.runners.web import WebRunner


def get_tc(tc_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM testcases WHERE id = %s", (tc_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"TC '{tc_id}' not found in DB")
        return dict(row)


def main():
    parser = argparse.ArgumentParser(description="QA Hub 자동화 테스트 러너 (CLI)")
    parser.add_argument("tc_id", help="실행할 TC ID (예: TC-001)")
    parser.add_argument(
        "--headed",
        action="store_true",
        help="브라우저 창 띄움 (실시간으로 눈으로 보기). 생략 시 백그라운드.",
    )
    args = parser.parse_args()

    try:
        tc = get_tc(args.tc_id)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"▶ Running {tc['id']}: {tc['title']}")
    print(f"  Target : {tc['target_url']}")
    print(f"  Steps  : {len(tc['steps'])}")
    print(f"  Mode   : {'Headed (창 뜸)' if args.headed else 'Headless (백그라운드)'}")
    print(f"{'=' * 60}\n")

    runner = WebRunner(
        run_id="cli-test",  # CLI 테스트용 임시 ID
        target_url=tc["target_url"],
        headless=not args.headed,
    )
    result = runner.run(tc)

    # 결과 출력
    print(f"\n{'=' * 60}")
    icon = "✅" if result["status"] == "pass" else "❌"
    print(f"{icon} Result: {result['status'].upper()}")
    print(f"   Duration : {result['duration_ms']}ms")

    pass_count = sum(1 for s in result["step_results"] if s["status"] == "pass")
    total = len(result["step_results"])
    print(f"   Steps    : {pass_count}/{total} passed")

    if result.get("error_message"):
        print(f"\n   Fatal Error: {result['error_message']}")

    print(f"\n   📸 Screenshots : backend/automation/output/{result['screenshot_dir']}")
    if result.get("video_path"):
        print(f"   🎬 Video       : backend/automation/output/{result['video_path']}")

    print(f"\n{'─' * 60}")
    print("스텝 상세:")
    for s in result["step_results"]:
        icon = "✓" if s["status"] == "pass" else "✗"
        desc = s.get("description", "")
        print(f"   {icon} Step {s['index'] + 1:>2}: [{s['action']:15}] "
              f"{s['duration_ms']:>5}ms  {desc}")
        if s.get("error"):
            print(f"       └─ Error: {s['error']}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()