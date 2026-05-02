import os
import allure
from datetime import datetime
from playwright.sync_api import Page


class BasePage:

    _run_folders = {}

    def __init__(self, page: Page):
        self.page = page

    def _handle_bot_detection(self):
        try:
            banner = self.page.locator("text=unusual traffic")
            if banner.is_visible(timeout=2000):
                print("\n[BOT DETECTION] Attempting automated slider solve...")
                solved = self._try_solve_nc_slider()
                if not solved:
                    print("[BOT DETECTION] Automated solve failed — please solve manually (2 min timeout)...")
                    banner.wait_for(state="hidden", timeout=120000)
                self.page.wait_for_load_state("load")
        except Exception:
            pass

    def _try_solve_nc_slider(self) -> bool:
        try:
            handle = self.page.locator("#nc_1_n1z")
            track = self.page.locator("#nc_1_n1t")
            handle.wait_for(state="visible", timeout=5000)

            handle_box = handle.bounding_box()
            track_box = track.bounding_box()
            if not handle_box or not track_box:
                return False

            start_x = handle_box["x"] + handle_box["width"] / 2
            start_y = handle_box["y"] + handle_box["height"] / 2
            end_x = track_box["x"] + track_box["width"] - handle_box["width"] / 2
            distance = end_x - start_x

            # JS evaluate bypasses Playwright's slow_mo, which would add 500ms per mouse.move call
            self.page.evaluate(f"""
                (function() {{
                    function fire(type, x, y) {{
                        document.dispatchEvent(new MouseEvent(type, {{
                            bubbles: true, cancelable: true,
                            clientX: x, clientY: y, screenX: x, screenY: y
                        }}));
                    }}
                    const sx = {start_x}, sy = {start_y}, dist = {distance};
                    fire('mousedown', sx, sy);
                    let i = 0;
                    const id = setInterval(function() {{
                        if (i > 30) {{ fire('mouseup', sx + dist, sy); clearInterval(id); return; }}
                        const t = i / 30;
                        const ease = 1 - Math.pow(1 - t, 3);
                        fire('mousemove', sx + dist * ease + (Math.random() - 0.5) * 2, sy + (Math.random() - 0.5) * 3);
                        i++;
                    }}, 40);
                }})()
            """)

            self.page.wait_for_timeout(2500)
            return not self.page.locator("text=unusual traffic").is_visible(timeout=1000)
        except Exception:
            return False

    def close_popup(self):
        self._handle_bot_detection()
        self.page.wait_for_timeout(1500)
        for selector in [
            "img.pop-close-btn",       # center promo popup
            "div._1-SOk",              # notification popup (primary)
            "img._24EHh",              # notification popup (fallback)
            "img[aria-label='close']", # post-login popup
        ]:
            try:
                btn = self.page.locator(selector).first
                if btn.is_visible():
                    btn.click()
                    self.page.wait_for_timeout(500)
            except Exception:
                pass

    def navigate(self, url: str, retries: int = 3):
        for attempt in range(retries):
            try:
                self.page.goto(url)
                self.page.wait_for_load_state("load")
                return
            except Exception as e:
                if attempt < retries - 1:
                    print(f"\n[RETRY] Navigation failed (attempt {attempt + 1}/{retries}), retrying in 3s...")
                    self.page.wait_for_timeout(3000)
                else:
                    raise

    def wait_for_element(self, selector: str):
        self.page.wait_for_selector(selector, timeout=15000)

    def take_screenshot(self, name: str, root: str = "screenshots/items-screenshots"):
        if root not in BasePage._run_folders:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            BasePage._run_folders[root] = os.path.join(root, timestamp)
        folder = BasePage._run_folders[root]
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{name}.png")
        self.page.screenshot(path=path)
        allure.attach.file(path, name=name, attachment_type=allure.attachment_type.PNG)
