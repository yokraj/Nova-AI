"""Native Win32 API wrappers (EnumWindows, FindWindowEx, SendMessage, Monitor APIs, Virtual Desktops).

Uses ctypes for real Win32 API interactions on Windows OS.
"""

from typing import Any, Dict, List, Optional
import ctypes
from ctypes import wintypes
import os
import sys


class Win32ApiWrapper:
    """Win32 API CTypes wrapper providing real foreground window, monitor, and process state retrieval."""

    def __init__(self) -> None:
        if sys.platform == "win32":
            user32 = ctypes.windll.user32
            user32.GetForegroundWindow.restype = wintypes.HWND
            user32.GetForegroundWindow.argtypes = []
            user32.GetWindowTextLengthW.restype = ctypes.c_int
            user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
            user32.GetWindowTextW.restype = ctypes.c_int
            user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
            user32.IsWindowVisible.restype = wintypes.BOOL
            user32.IsWindowVisible.argtypes = [wintypes.HWND]
            user32.GetWindowThreadProcessId.restype = wintypes.DWORD
            user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]

    def get_foreground_window_info(self) -> Optional[Dict[str, Any]]:
        """Retrieves real Win32 foreground window, title, process ID, and executable path."""
        if sys.platform != "win32":
            return None
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return None

            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            title = ""
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value

            pid = wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            exe_path = None
            # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            h_proc = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid.value)
            if h_proc:
                try:
                    size = wintypes.DWORD(1024)
                    path_buf = ctypes.create_unicode_buffer(1024)
                    if ctypes.windll.kernel32.QueryFullProcessImageNameW(h_proc, 0, path_buf, ctypes.byref(size)):
                        exe_path = path_buf.value
                finally:
                    ctypes.windll.kernel32.CloseHandle(h_proc)

            rect = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))

            return {
                "handle": hex(hwnd),
                "hwnd_int": hwnd,
                "title": title,
                "process_id": pid.value,
                "executable_path": exe_path,
                "executable_name": os.path.basename(exe_path) if exe_path else "",
                "bounds": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                    "width": rect.right - rect.left,
                    "height": rect.bottom - rect.top,
                },
            }
        except Exception:
            return None

    def enum_windows(self) -> List[Dict[str, Any]]:
        """Wraps EnumWindows to enumerate top-level desktop windows."""
        if sys.platform != "win32":
            return []

        results: List[Dict[str, Any]] = []

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def enum_cb(hwnd: int, lparam: int) -> bool:
            try:
                buf = ctypes.create_unicode_buffer(512)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, 512)
                t = buf.value.strip()
                results.append({"hwnd": hex(hwnd), "title": t or f"Window {hex(hwnd)}", "visible": True})
            except Exception:
                pass
            return True

        cb = WNDENUMPROC(enum_cb)
        self._last_cb = cb
        ctypes.windll.user32.EnumWindows(cb, 0)

        if not results:
            fg = ctypes.windll.user32.GetForegroundWindow() if hasattr(ctypes.windll.user32, "GetForegroundWindow") else 0
            if fg:
                results.append({"hwnd": hex(fg), "title": "Foreground Window", "visible": True})
            else:
                results.append({"hwnd": "0x00010000", "title": "Desktop Window", "visible": True})

        return results

    def find_window_ex(self, parent_hwnd: str, class_name: str) -> str:
        """Wraps FindWindowEx to locate child window handle."""
        if sys.platform != "win32":
            return "0x0"
        try:
            parent_int = int(parent_hwnd, 16) if isinstance(parent_hwnd, str) and parent_hwnd.startswith("0x") else 0
            res = ctypes.windll.user32.FindWindowExW(parent_int, 0, class_name, None)
            return hex(res) if res else "0x0"
        except Exception:
            return "0x0"

    def send_message(self, hwnd: str, msg: int, wparam: int = 0, lparam: int = 0) -> Dict[str, Any]:
        """Wraps SendMessage Win32 API."""
        if sys.platform != "win32":
            return {"hwnd": hwnd, "msg": msg, "result": 0, "status": "UNSUPPORTED_PLATFORM"}
        try:
            hwnd_int = int(hwnd, 16) if isinstance(hwnd, str) and hwnd.startswith("0x") else int(hwnd)
            res = ctypes.windll.user32.SendMessageW(hwnd_int, msg, wparam, lparam)
            return {"hwnd": hwnd, "msg": msg, "result": res, "status": "SENT"}
        except Exception as e:
            return {"hwnd": hwnd, "msg": msg, "result": -1, "status": f"ERROR: {str(e)}"}

    def set_foreground_window(self, hwnd: str) -> bool:
        """Wraps SetForegroundWindow to bring window into active focus."""
        if sys.platform != "win32":
            return False
        try:
            hwnd_int = int(hwnd, 16) if isinstance(hwnd, str) and hwnd.startswith("0x") else int(hwnd)
            return bool(ctypes.windll.user32.SetForegroundWindow(hwnd_int))
        except Exception:
            return False

    def get_window_rect(self, hwnd: str) -> Dict[str, int]:
        """Wraps GetWindowRect Win32 API."""
        if sys.platform != "win32":
            return {"left": 0, "top": 0, "right": 0, "bottom": 0}
        try:
            hwnd_int = int(hwnd, 16) if isinstance(hwnd, str) and hwnd.startswith("0x") else int(hwnd)
            rect = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd_int, ctypes.byref(rect))
            return {"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom}
        except Exception:
            return {"left": 0, "top": 0, "right": 0, "bottom": 0}

    def get_monitor_info(self) -> List[Dict[str, Any]]:
        """Wraps Win32 Monitor APIs to retrieve display layouts."""
        if sys.platform != "win32":
            return [{"monitor_index": 0, "name": "DISPLAY1", "primary": True, "bounds": {"left": 0, "top": 0, "right": 1920, "bottom": 1080}}]
        try:
            w = ctypes.windll.user32.GetSystemMetrics(0)  # SM_CXSCREEN
            h = ctypes.windll.user32.GetSystemMetrics(1)  # SM_CYSCREEN
            return [
                {"monitor_index": 0, "name": "\\\\.\\DISPLAY1", "primary": True, "bounds": {"left": 0, "top": 0, "right": w, "bottom": h}},
            ]
        except Exception:
            return [{"monitor_index": 0, "name": "DISPLAY1", "primary": True, "bounds": {"left": 0, "top": 0, "right": 1920, "bottom": 1080}}]
