"""
웹 러너 (WebRunner) — Playwright 기반
──────────────────────────────────
TC JSON의 steps를 읽어 saucedemo.com 같은 웹 사이트에서 실제로 실행.
- Chromium 자동 조종 (slow_mo로 실무 수동 QA처럼 느리게)
- 각 스텝마다 스크린샷 + 스텝 간 wait (라이브 뷰 가독성)
- 전체 과정 영상 녹화 (.webm)
- 액션 매핑: fill / click / goto / wait / assert_* 등
"""

from playwright.sync_api import sync_playwright, expect
from .base import BaseRunner, VIDEO_DIR


# 러너 설정 — 포폴 데모 가독성 우선
SLOW_MO_MS = 500           # 모든 Playwright action에 500ms 지연 (사람이 조작하는 것처럼)
STEP_WAIT_MS = 300         # 각 스텝 완료 후 추가 대기 (스크린샷 폴링 간격 맞춤)
FINAL_WAIT_MS = 1500       # 마지막 스텝 후 teardown 전까지 대기 (녹화 안정화)


class WebRunner(BaseRunner):
    def __init__(self, run_id, target_url, headless=True):
        super().__init__(run_id, headless)
        self.target_url = target_url
        self._pw = None
        self._browser = None
        self._context = None
        self._page = None

    def _setup(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=self.headless,
            slow_mo=SLOW_MO_MS,     # ← 모든 action을 500ms 느리게
        )
        self._context = self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(VIDEO_DIR / f"{self.run_id}_tmp"),
            record_video_size={"width": 1280, "height": 720},
        )
        self._page = self._context.new_page()
        self._page.goto(self.target_url, wait_until="domcontentloaded")
        # 첫 페이지 로드 후 1초 대기 (녹화 시작 안정화)
        self._page.wait_for_timeout(1000)

    def _teardown(self):
        try:
            # 마지막 스텝 후 대기 (녹화에 마지막 상태 포함)
            if self._page:
                try:
                    self._page.wait_for_timeout(FINAL_WAIT_MS)
                except Exception:
                    pass

            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._pw:
                self._pw.stop()
        finally:
            # 녹화된 비디오를 올바른 이름으로 이동
            temp_dir = VIDEO_DIR / f"{self.run_id}_tmp"
            if temp_dir.exists():
                videos = list(temp_dir.glob("*.webm"))
                if videos:
                    try:
                        videos[0].rename(self.video_path)
                    except Exception:
                        pass
                try:
                    temp_dir.rmdir()
                except Exception:
                    pass

    def _execute_step(self, step):
        action = step["action"]

        if action == "goto":
            self._page.goto(step["url"], wait_until="domcontentloaded")

        elif action == "fill":
            self._page.fill(step["selector"], step["value"])

        elif action == "click":
            self._page.click(step["selector"])

        elif action == "wait":
            self._page.wait_for_timeout(step["ms"])

        elif action == "wait_for":
            self._page.wait_for_selector(step["selector"], timeout=5000)

        elif action == "assert_visible":
            expect(self._page.locator(step["selector"])).to_be_visible(timeout=5000)

        elif action == "assert_text":
            expect(self._page.locator(step["selector"])).to_contain_text(
                step["expected"], timeout=5000
            )

        elif action == "assert_url":
            current = self._page.url
            if step["expected"] not in current:
                raise AssertionError(
                    f"URL '{current}' does not contain '{step['expected']}'"
                )

        elif action == "assert_attribute":
            element = self._page.locator(step["selector"]).first
            attr_value = element.get_attribute(step["attribute"]) or ""
            needle = step.get("contains", "")
            if needle not in attr_value:
                raise AssertionError(
                    f"Attribute '{step['attribute']}' value '{attr_value}' "
                    f"does not contain '{needle}'"
                )

        elif action == "screenshot":
            pass

        else:
            raise ValueError(f"Unknown action: {action}")

        # 각 스텝 완료 후 추가 wait — 라이브 뷰에서 스크린샷 폴링이 캐치할 시간
        self._page.wait_for_timeout(STEP_WAIT_MS)

    def _save_screenshot(self, name):
        path = self.screenshot_dir / name
        self._page.screenshot(path=str(path), full_page=False)