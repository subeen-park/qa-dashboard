"""
공용 베이스 러너 (BaseRunner)
──────────────────────────────────
웹/모바일 러너의 공용 실행 흐름을 정의한 추상 클래스.
- 스텝 하나씩 실행
- 스텝마다 스크린샷 저장
- 결과 포맷 통일 (DB test_runs 테이블 포맷에 맞춤)
- 에러 발생 시 중단 + 그 지점에서 스크린샷

각 러너(WebRunner, MobileRunner)는 _setup, _teardown, _execute_step,
_save_screenshot 4개 메서드만 구현하면 됨.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path


# 출력 디렉토리 (backend/automation/output/)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
SCREENSHOT_DIR = OUTPUT_DIR / "screenshots"
VIDEO_DIR = OUTPUT_DIR / "videos"


class BaseRunner(ABC):
    def __init__(self, run_id, headless=True):
        self.run_id = run_id
        self.headless = headless
        self.screenshot_dir = SCREENSHOT_DIR / str(run_id)
        self.video_path = VIDEO_DIR / f"{run_id}.webm"
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    # ─── 공용 실행 흐름 ──────────────────────────
    def run(self, tc):
        """TC 하나 실행하고 결과 dict 반환."""
        started_at = datetime.now()
        step_results = []
        status = "pass"
        error_message = None

        try:
            self._setup()
            for i, step in enumerate(tc["steps"]):
                step_result = self._run_step(i, step)
                step_results.append(step_result)
                if step_result["status"] == "fail":
                    status = "fail"
                    break
        except Exception as e:
            status = "error"
            error_message = str(e)
        finally:
            try:
                self._teardown()
            except Exception as e:
                print(f"[teardown warning] {e}")

        ended_at = datetime.now()
        duration_ms = int((ended_at - started_at).total_seconds() * 1000)

        return {
            "status": status,
            "started_at": started_at,
            "ended_at": ended_at,
            "duration_ms": duration_ms,
            "step_results": step_results,
            "error_message": error_message,
            "screenshot_dir": f"screenshots/{self.run_id}",
            "video_path": f"videos/{self.run_id}.webm" if self.video_path.exists() else None,
        }

    def _run_step(self, idx, step):
        """스텝 하나 실행 + 결과 포맷."""
        started = datetime.now()
        screenshot_name = f"step_{idx + 1:02d}.png"

        try:
            self._execute_step(step)
            self._save_screenshot(screenshot_name)
            return {
                "index": idx,
                "action": step["action"],
                "description": step.get("description", ""),
                "status": "pass",
                "duration_ms": int((datetime.now() - started).total_seconds() * 1000),
                "screenshot": screenshot_name,
            }
        except Exception as e:
            # 실패 시에도 스크린샷 저장 시도 (실패 지점 캡처)
            try:
                self._save_screenshot(screenshot_name)
            except Exception:
                pass
            return {
                "index": idx,
                "action": step["action"],
                "description": step.get("description", ""),
                "status": "fail",
                "duration_ms": int((datetime.now() - started).total_seconds() * 1000),
                "screenshot": screenshot_name,
                "error": str(e),
            }

    # ─── 서브클래스가 구현할 메서드 ───────────────
    @abstractmethod
    def _setup(self):
        """브라우저/드라이버 초기화."""

    @abstractmethod
    def _teardown(self):
        """브라우저/드라이버 정리."""

    @abstractmethod
    def _execute_step(self, step):
        """스텝 하나의 실제 액션 수행."""

    @abstractmethod
    def _save_screenshot(self, name):
        """현재 화면 스크린샷 저장."""