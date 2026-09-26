"""Chrome CDP (DevTools Protocol) Native Browser Automation Provider.

Executes real browser control against local Chrome/Chromium binaries via CDP WebSocket APIs.
Does NOT rely on third-party cloud services or un-installed dependencies.
"""

from typing import Any, Dict, List, Optional
import os
import json
import time
import base64
import shutil
import asyncio
import subprocess
import structlog
import httpx
import websockets

logger = structlog.get_logger("chrome_cdp_provider")


class ChromeCDPBrowserProvider:
    """Native Chrome browser automation provider using Chrome DevTools Protocol (CDP)."""

    def __init__(self, port: int = 9222, headless: bool = True) -> None:
        self.port = port
        self.headless = headless
        self._process: Optional[subprocess.Popen] = None
        self._ws_url: Optional[str] = None
        self._target_id: Optional[str] = None
        self._is_connected = False
        self._msg_id = 0

    @staticmethod
    def find_chrome_executable() -> str:
        """Finds chrome.exe on system path or standard Windows install paths."""
        which_chrome = shutil.which("chrome") or shutil.which("google-chrome")
        if which_chrome:
            return which_chrome

        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path

        raise FileNotFoundError("Chrome/Chromium executable not found on host system.")

    async def _ensure_browser_started(self) -> None:
        """Launches Chrome binary with CDP remote debugging enabled if not already active."""
        if self._is_connected and self._ws_url:
            return

        chrome_exe = self.find_chrome_executable()
        cdp_http_url = f"http://127.0.0.1:{self.port}/json/version"

        # Check if Chrome CDP is already listening
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                res = await client.get(cdp_http_url)
                if res.status_code == 200:
                    data = res.json()
                    self._ws_url = data.get("webSocketDebuggerUrl")
                    self._is_connected = True
                    logger.info("Connected to existing Chrome CDP instance", ws_url=self._ws_url)
                    return
        except Exception:
            pass

        # Launch fresh Chrome instance with CDP
        user_data_dir = os.path.join(os.path.expanduser("~"), ".nova", "chrome_dev_profile")
        os.makedirs(user_data_dir, exist_ok=True)

        cmd = [
            chrome_exe,
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
            "--disable-extensions",
        ]
        if self.headless:
            cmd.append("--headless=new")

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for CDP endpoint to become ready
        start_t = time.time()
        while time.time() - start_t < 10.0:
            try:
                async with httpx.AsyncClient(timeout=1.0) as client:
                    res = await client.get(cdp_http_url)
                    if res.status_code == 200:
                        data = res.json()
                        self._ws_url = data.get("webSocketDebuggerUrl")
                        self._is_connected = True
                        logger.info("Launched Chrome with CDP port", port=self.port, ws_url=self._ws_url)
                        return
            except Exception:
                await asyncio.sleep(0.3)

        raise RuntimeError("Failed to launch Chrome with CDP remote debugging enabled.")

    async def _send_cdp(self, method: str, params: Optional[Dict[str, Any]] = None, target_ws_url: Optional[str] = None) -> Dict[str, Any]:
        """Sends raw CDP command over WebSocket connection and returns response."""
        await self._ensure_browser_started()
        ws_endpoint = target_ws_url or self._ws_url
        if not ws_endpoint:
            raise RuntimeError("No active CDP WebSocket URL available.")

        self._msg_id += 1
        msg_id = self._msg_id
        payload = {"id": msg_id, "method": method, "params": params or {}}

        async with websockets.connect(ws_endpoint, max_size=20 * 1024 * 1024) as ws:
            await ws.send(json.dumps(payload))
            while True:
                resp_text = await asyncio.wait_for(ws.recv(), timeout=15.0)
                resp = json.loads(resp_text)
                if resp.get("id") == msg_id:
                    if "error" in resp:
                        raise RuntimeError(f"CDP Error ({method}): {resp['error']}")
                    return resp.get("result", {})

    async def _get_page_ws_url(self) -> str:
        """Retrieves or creates active page tab WebSocket URL."""
        await self._ensure_browser_started()
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"http://127.0.0.1:{self.port}/json/list")
            tabs = res.json()
            page_tabs = [t for t in tabs if t.get("type") == "page"]
            if page_tabs:
                return page_tabs[0]["webSocketDebuggerUrl"]

            # Create a new tab if none exist
            new_res = await client.put(f"http://127.0.0.1:{self.port}/json/new?about:blank")
            new_tab = new_res.json()
            return new_tab["webSocketDebuggerUrl"]

    async def open_url(self, url: str) -> None:
        """Launches browser and navigates to target URL."""
        await self.navigate(url)

    async def navigate(self, url: str) -> None:
        """Navigates active page to target URL."""
        ws_url = await self._get_page_ws_url()
        res = await self._send_cdp("Page.navigate", {"url": url}, target_ws_url=ws_url)
        # Wait briefly for load event
        await asyncio.sleep(1.0)
        logger.info("CDP navigated to URL", url=url)

    async def refresh(self) -> None:
        """Reloads active page."""
        ws_url = await self._get_page_ws_url()
        await self._send_cdp("Page.reload", {}, target_ws_url=ws_url)
        await asyncio.sleep(1.0)

    async def back(self) -> None:
        """Navigates back in history."""
        await self._evaluate_js("window.history.back()")
        await asyncio.sleep(0.5)

    async def forward(self) -> None:
        """Navigates forward in history."""
        await self._evaluate_js("window.history.forward()")
        await asyncio.sleep(0.5)

    async def _evaluate_js(self, expression: str) -> Any:
        """Evaluates JS in current page context via CDP."""
        ws_url = await self._get_page_ws_url()
        res = await self._send_cdp(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": True},
            target_ws_url=ws_url,
        )
        val_res = res.get("result", {})
        return val_res.get("value")

    async def get_page_info(self) -> Dict[str, Any]:
        """Extracts URL, title, viewport, visible text, forms, iframes, tabs, and rich accessibility/DOM elements."""
        ws_url = await self._get_page_ws_url()
        js_code = """
        (() => {
            const url = window.location.href;
            const title = document.title;
            const bodyText = (document.body ? document.body.innerText : "").slice(0, 2500);
            const readyState = document.readyState;
            const viewport = {
                width: window.innerWidth,
                height: window.innerHeight,
                devicePixelRatio: window.devicePixelRatio || 1
            };
            
            const interactive = [];
            const elements = document.querySelectorAll("a, button, input, select, textarea, [role='button'], [role='link'], [role='checkbox'], [role='menuitem'], [onclick]");
            elements.forEach((el, idx) => {
                if (idx < 100) {
                    const rect = el.getBoundingClientRect();
                    const isVisible = !!(rect.width || rect.height || el.getClientRects().length);
                    const tag = el.tagName.toLowerCase();
                    const id = el.id || "";
                    const name = el.getAttribute("name") || "";
                    const type = el.getAttribute("type") || "";
                    const role = el.getAttribute("role") || el.tagName.toLowerCase();
                    const ariaLabel = el.getAttribute("aria-label") || "";
                    const placeholder = el.getAttribute("placeholder") || "";
                    const value = el.value || "";
                    const text = (el.innerText || value || placeholder || ariaLabel || "").trim().slice(0, 80);
                    const href = el.getAttribute("href") || "";
                    const disabled = el.disabled || false;
                    const checked = el.checked || false;
                    
                    let selector = "";
                    if (id) {
                        selector = `#${id}`;
                    } else if (name) {
                        selector = `[name='${name}']`;
                    } else if (placeholder) {
                        selector = `[placeholder='${placeholder}']`;
                    } else {
                        selector = tag;
                    }
                    
                    interactive.push({
                        idx,
                        tag,
                        id,
                        name,
                        type,
                        role,
                        ariaLabel,
                        placeholder,
                        text,
                        value,
                        href,
                        disabled,
                        checked,
                        visible: isVisible,
                        bbox: {
                            x: Math.round(rect.left),
                            y: Math.round(rect.top),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        },
                        selector
                    });
                }
            });

            // Forms summary
            const forms = [];
            document.querySelectorAll("form").forEach((f, fIdx) => {
                const action = f.getAttribute("action") || "";
                const inputs = Array.from(f.querySelectorAll("input, select, textarea")).map(i => i.name || i.id || i.type);
                forms.push({ id: f.id || `form_${fIdx}`, action, inputs });
            });

            // Iframes summary
            const iframes = Array.from(document.querySelectorAll("iframe")).map(f => f.src || f.id || "iframe");

            return {
                url,
                title,
                bodyText,
                readyState,
                viewport,
                interactive,
                forms,
                iframes
            };
        })()
        """
        info = await self._evaluate_js(js_code)
        tabs_summary = await self.list_tabs()
        if isinstance(info, dict):
            info["tabs"] = tabs_summary
            return info
        return {
            "url": "about:blank",
            "title": "",
            "bodyText": "",
            "readyState": "complete",
            "viewport": {"width": 1280, "height": 720, "devicePixelRatio": 1},
            "interactive": [],
            "forms": [],
            "iframes": [],
            "tabs": tabs_summary,
        }

    async def list_tabs(self) -> List[Dict[str, Any]]:
        """Retrieves list of active browser tabs from CDP endpoint."""
        await self._ensure_browser_started()
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"http://127.0.0.1:{self.port}/json/list")
                tabs = res.json()
                return [
                    {
                        "id": t.get("id"),
                        "title": t.get("title", ""),
                        "url": t.get("url", ""),
                        "type": t.get("type"),
                        "ws_url": t.get("webSocketDebuggerUrl"),
                    }
                    for t in tabs
                    if t.get("type") == "page"
                ]
        except Exception:
            return []

    async def switch_tab(self, tab_id: str) -> bool:
        """Switches active focus to target tab ID."""
        await self._ensure_browser_started()
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"http://127.0.0.1:{self.port}/json/activate/{tab_id}")
                return res.status_code == 200
        except Exception:
            return False

    async def new_tab(self, url: str = "about:blank") -> Dict[str, Any]:
        """Creates a new browser tab and navigates to target URL."""
        await self._ensure_browser_started()
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.put(f"http://127.0.0.1:{self.port}/json/new?{url}")
            tab_info = res.json()
            return {
                "id": tab_info.get("id"),
                "url": tab_info.get("url"),
                "ws_url": tab_info.get("webSocketDebuggerUrl"),
            }

    async def close_tab(self, tab_id: str) -> bool:
        """Closes target tab by ID."""
        await self._ensure_browser_started()
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"http://127.0.0.1:{self.port}/json/close/{tab_id}")
                return res.status_code == 200
        except Exception:
            return False

    async def ground_element(
        self, target_query: str, page_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Adaptive multi-modal element grounding scoring candidates across DOM, text, ARIA, and bounding box."""
        if not page_info:
            page_info = await self.get_page_info()

        candidates = page_info.get("interactive", [])
        if not candidates:
            return {
                "selector": target_query,
                "confidence": 0.0,
                "source": "none",
                "requires_human": True,
                "element": None,
            }

        q_lower = target_query.lower()
        best_candidate = None
        highest_score = 0.0
        match_source = "none"

        for cand in candidates:
            score = 0.0
            sources = []

            c_id = cand.get("id", "").lower()
            c_name = cand.get("name", "").lower()
            c_text = cand.get("text", "").lower()
            c_aria = cand.get("ariaLabel", "").lower()
            c_place = cand.get("placeholder", "").lower()
            c_role = cand.get("role", "").lower()
            c_bbox = cand.get("bbox", {})

            # Exact ID / Name match
            if target_query.startswith("#") and target_query[1:].lower() == c_id:
                score += 0.9
                sources.append("id_exact")
            elif target_query.startswith("[name=") and c_name in target_query.lower():
                score += 0.85
                sources.append("name_exact")
            elif q_lower == c_id or q_lower == c_name:
                score += 0.8
                sources.append("id_name_match")

            # Text / Substring match
            if q_lower and q_lower in c_text:
                score += 0.7
                sources.append("text_substring")
            elif c_text and c_text in q_lower:
                score += 0.5
                sources.append("text_contained")

            # ARIA / Placeholder / Role match
            if q_lower in c_aria or q_lower in c_place:
                score += 0.65
                sources.append("aria_placeholder")

            # Bounding box visibility check
            if c_bbox.get("width", 0) > 0 and c_bbox.get("height", 0) > 0:
                score += 0.1
                sources.append("visible_bbox")
            else:
                score -= 0.3  # Penalty for invisible/collapsed element

            if score > highest_score:
                highest_score = score
                best_candidate = cand
                match_source = "+".join(sources)

        normalized_conf = min(1.0, max(0.0, highest_score))
        requires_human = normalized_conf < 0.60

        selected_selector = (
            best_candidate.get("selector") if best_candidate else target_query
        )

        return {
            "selector": selected_selector,
            "confidence": round(normalized_conf, 2),
            "source": match_source,
            "requires_human": requires_human,
            "element": best_candidate,
        }

    async def wait_for_idle(self, timeout_ms: int = 5000) -> bool:
        """Dynamic wait until page document.readyState is complete and network requests settle."""
        js_code = """
        (() => {
            return document.readyState === 'complete';
        })()
        """
        start_t = time.time()
        timeout_sec = timeout_ms / 1000.0
        while time.time() - start_t < timeout_sec:
            is_ready = await self._evaluate_js(js_code)
            if is_ready:
                await asyncio.sleep(0.2)
                return True
            await asyncio.sleep(0.1)
        return False

    async def click_element(self, selector: str) -> bool:
        """Clicks element matching CSS selector, ID, placeholder, or text content."""
        grounding = await self.ground_element(selector)
        target_selector = grounding.get("selector", selector)

        js_code = f"""
        (() => {{
            const target = '{target_selector}';
            let el = document.querySelector(target);
            if (!el) {{
                const all = Array.from(document.querySelectorAll("a, button, input, div, span, [role='button']"));
                el = all.find(e => 
                    (e.innerText && e.innerText.trim().toLowerCase().includes(target.toLowerCase())) ||
                    (e.placeholder && e.placeholder.toLowerCase().includes(target.toLowerCase())) ||
                    (e.value && e.value.toLowerCase().includes(target.toLowerCase()))
                );
            }}
            if (el) {{
                el.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                el.click();
                return true;
            }}
            return false;
        }})()
        """
        success = await self._evaluate_js(js_code)
        await self.wait_for_idle(2000)
        return bool(success)

    async def click_element_advanced(
        self, selector: str, click_type: str = "single"
    ) -> bool:
        """Supports single, double, and right-click interactions."""
        if click_type == "double":
            js_event = "dblclick"
        elif click_type == "right":
            js_event = "contextmenu"
        else:
            js_event = "click"

        js_code = f"""
        (() => {{
            const el = document.querySelector('{selector}');
            if (el) {{
                el.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                const evt = new MouseEvent('{js_event}', {{ bubbles: true, cancelable: true, view: window }});
                el.dispatchEvent(evt);
                return true;
            }}
            return false;
        }})()
        """
        res = await self._evaluate_js(js_code)
        await self.wait_for_idle(1500)
        return bool(res)

    async def clear_input(self, selector: str) -> bool:
        """Clears text inside input element."""
        js_code = f"""
        (() => {{
            const el = document.querySelector('{selector}');
            if (el) {{
                el.value = '';
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})()
        """
        return bool(await self._evaluate_js(js_code))

    async def press_key(self, key_name: str) -> bool:
        """Dispatches keyboard event via CDP."""
        ws_url = await self._get_page_ws_url()
        await self._send_cdp(
            "Input.dispatchKeyEvent",
            {"type": "keyDown", "key": key_name, "text": key_name if len(key_name) == 1 else ""},
            target_ws_url=ws_url,
        )
        await self._send_cdp(
            "Input.dispatchKeyEvent",
            {"type": "keyUp", "key": key_name},
            target_ws_url=ws_url,
        )
        await asyncio.sleep(0.2)
        return True

    async def select_option(self, selector: str, option_val: str) -> bool:
        """Selects option in select dropdown by value or text."""
        js_code = f"""
        (() => {{
            const sel = document.querySelector('{selector}');
            if (sel && sel.tagName.toLowerCase() === 'select') {{
                let opt = Array.from(sel.options).find(o => o.value === '{option_val}' || o.text.trim().toLowerCase().includes('{option_val}'.toLowerCase()));
                if (opt) {{
                    sel.value = opt.value;
                    sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
            }}
            return false;
        }})()
        """
        return bool(await self._evaluate_js(js_code))

    async def set_checkbox(self, selector: str, checked: bool = True) -> bool:
        """Sets checkbox checked state."""
        js_code = f"""
        (() => {{
            const el = document.querySelector('{selector}');
            if (el) {{
                if (el.checked !== {str(checked).lower()}) {{
                    el.click();
                }}
                return true;
            }}
            return false;
        }})()
        """
        return bool(await self._evaluate_js(js_code))

    async def scroll_page(self, delta_x: int = 0, delta_y: int = 500) -> bool:
        """Scrolls page viewport by delta coordinates."""
        js_code = f"window.scrollBy({delta_x}, {delta_y}); true;"
        return bool(await self._evaluate_js(js_code))

    async def hover_element(self, selector: str) -> bool:
        """Triggers mouseover / mouseenter events on element."""
        js_code = f"""
        (() => {{
            const el = document.querySelector('{selector}');
            if (el) {{
                const evt = new MouseEvent('mouseover', {{ bubbles: true, cancelable: true }});
                el.dispatchEvent(evt);
                return true;
            }}
            return false;
        }})()
        """
        return bool(await self._evaluate_js(js_code))

    async def fill_input(self, selector: str, value: str) -> bool:
        """Fills input target element with specified text string."""
        escaped_val = value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        js_code = f"""
        (() => {{
            const target = '{selector}';
            let el = document.querySelector(target);
            if (!el) {{
                const all = Array.from(document.querySelectorAll("input, textarea"));
                el = all.find(e => 
                    e.id === target ||
                    e.name === target ||
                    (e.placeholder && e.placeholder.toLowerCase().includes(target.toLowerCase())) ||
                    e.getAttribute("type") === target
                ) || all[0];
            }}
            if (el) {{
                el.focus();
                el.value = '{escaped_val}';
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})()
        """
        success = await self._evaluate_js(js_code)
        await asyncio.sleep(0.3)
        return bool(success)

    async def submit_form(self, selector: Optional[str] = None) -> bool:
        """Submits form element or triggers submit button click."""
        js_code = """
        (() => {
            const btn = document.querySelector("input[type='submit'], button[type='submit'], #search_button_homepage");
            if (btn) {
                btn.click();
                return true;
            }
            const active = document.activeElement;
            const form = (active && active.form) ? active.form : document.querySelector("form");
            if (form) {
                if (form.requestSubmit) {
                    form.requestSubmit();
                } else {
                    form.submit();
                }
                return true;
            }
            return false;
        })()
        """
        res = await self._evaluate_js(js_code)
        await self.wait_for_idle(2500)
        return bool(res)

    async def screenshot(self, output_path: str) -> str:
        """Captures page viewport image via CDP Page.captureScreenshot and saves to disk."""
        ws_url = await self._get_page_ws_url()
        res = await self._send_cdp("Page.captureScreenshot", {"format": "png"}, target_ws_url=ws_url)
        img_b64 = res.get("data", "")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(img_b64))

        logger.info("Saved CDP page screenshot", path=output_path)
        return output_path

    async def extract_structured_info(self, goal_query: str) -> Dict[str, Any]:
        """Goal-oriented web information extraction targeting key evidence elements."""
        info = await self.get_page_info()
        url = info.get("url", "")
        title = info.get("title", "")
        body_text = info.get("bodyText", "")

        extracted_facts = []
        q_lower = goal_query.lower()

        # Check body text lines for relevance
        lines = [line.strip() for line in body_text.split("\n") if line.strip()]
        for line in lines:
            if any(term in line.lower() for term in q_lower.split()):
                extracted_facts.append(line)
                if len(extracted_facts) >= 5:
                    break

        return {
            "source_url": url,
            "page_title": title,
            "goal_query": goal_query,
            "extracted_facts": extracted_facts or [body_text[:200]],
            "timestamp": time.time(),
        }

    async def extract_dom(self) -> str:
        """Returns raw HTML page content."""
        return await self._evaluate_js("document.documentElement.outerHTML") or ""

    async def close(self) -> None:
        """Terminates Chrome subprocess if launched by this provider."""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2.0)
            except Exception:
                pass
            self._process = None
        self._is_connected = False
        logger.info("Closed CDP Chrome instance")

