"""
웹 러너 (WebRunner) — Playwright 기반
──────────────────────────────────
Render Free tier (0.1 CPU, 512MB RAM) 극한 최적화:
- Chromium 메모리/CPU 플래그
- slow_mo 거의 0 (라이브 뷰 보이는 최소치만)
- step_wait 축소
"""

from playwright.sync_api import sync_playwright, expect
from .base import BaseRunner, VIDEO_DIR


# Free tier 속도 우선 — 라이브 뷰는 "보이기만 함" 수준
SLOW_MO_MS = 50            # 사실상 지연 없음 (액션 간 50ms)
STEP_WAIT_MS = 100         # 스크린샷 폴링 캐치 최소치
FINAL_WAIT_MS = 500        # 녹화 안정화 최소치


# Render Free tier에서 Chromium 메모리/CPU 절약
CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-features=TranslateUI,BlinkGenPropertyTrees",
    "--disable-extensions",
    "--disable-component-extensions-with-background-pages",
    "--disable-ipc-flooding-protection",
    "--metrics-recording-only",
    "--mute-audio",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-blink-features=AutomationControlled",
    "--disable-sync",
    "--disable-translate",
    "--hide-scrollbars",
]


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
            slow_mo=SLOW_MO_MS,
            args=CHROMIUM_ARGS,
        )
        self._context = self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(VIDEO_DIR / f"{self.run_id}_tmp"),
            record_video_size={"width": 1280, "height": 720},
        )
        self._page = self._context.new_page()
        self._page.goto(self.target_url, wait_until="domcontentloaded")
        self._page.wait_for_timeout(300)

    def _teardown(self):
        try:
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

        self._page.wait_for_timeout(STEP_WAIT_MS)

    def _save_screenshot(self, name):
        path = self.screenshot_dir / name
        self._page.screenshot(path=str(path), full_page=False)