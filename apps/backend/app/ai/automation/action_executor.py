"""Action Executor dispatches step instructions to domain controllers.
"""

import structlog
import json
from datetime import datetime
from typing import Any

from app.ai.automation.interfaces import ActionExecutor as IActionExecutor
from app.ai.automation.models import ActionStep, ExecutionResult

logger = structlog.get_logger("action_executor")

class ActionExecutor(IActionExecutor):
    """Translates step payload properties into controllers method calls."""

    def __init__(
        self,
        mouse_ctrl: Any,
        keyboard_ctrl: Any,
        clipboard_mgr: Any,
        window_mgr: Any,
        browser_ctrl: Any,
        explorer_ctrl: Any,
        terminal_ctrl: Any,
        process_mgr: Any
    ) -> None:
        self.mouse = mouse_ctrl
        self.keyboard = keyboard_ctrl
        self.clipboard = clipboard_mgr
        self.window = window_mgr
        self.browser = browser_ctrl
        self.explorer = explorer_ctrl
        self.terminal = terminal_ctrl
        self.process = process_mgr

    async def execute_step(self, step: ActionStep, context: Any) -> ExecutionResult:
        """Invokes matching methods and packages stdout/stderr in ExecutionResult."""
        logger.info("Executing action step", step_id=step.step_id, domain=step.domain)
        result = ExecutionResult(step_id=step.step_id, status="success")

        try:
            if step.domain == "mouse" and step.mouse_action:
                act = step.mouse_action
                if act.action_type == "move":
                    if act.dx is not None and act.dy is not None:
                        self.mouse.move_relative(act.dx, act.dy)
                    elif act.x is not None and act.y is not None:
                        self.mouse.move_to(act.x, act.y)
                elif act.action_type == "click":
                    self.mouse.click(act.x, act.y, act.button, act.clicks)
                elif act.action_type == "double_click":
                    self.mouse.double_click(act.x, act.y)
                elif act.action_type == "right_click":
                    self.mouse.right_click(act.x, act.y)
                elif act.action_type == "middle_click":
                    self.mouse.middle_click(act.x, act.y)
                elif act.action_type == "drag":
                    if act.dx is not None and act.dy is not None:
                        self.mouse.drag_relative(act.dx, act.dy)
                    elif act.x is not None and act.y is not None:
                        self.mouse.drag_to(act.x, act.y)
                elif act.action_type == "scroll" and act.scroll_amount is not None:
                    if act.scroll_amount > 0:
                        self.mouse.scroll_up(act.scroll_amount)
                    else:
                        self.mouse.scroll_down(abs(act.scroll_amount))

            elif step.domain == "keyboard" and step.keyboard_action:
                act = step.keyboard_action
                if act.action_type == "type" and act.text:
                    self.keyboard.type_text(act.text, act.delay)
                elif act.action_type == "press" and act.key:
                    self.keyboard.press_key(act.key)
                elif act.action_type == "release" and act.key:
                    self.keyboard.release_key(act.key)
                elif act.action_type == "combination" and act.keys:
                    self.keyboard.key_combination(act.keys)
                elif act.action_type == "hold" and act.key:
                    self.keyboard.hold_key(act.key, act.delay)

            elif step.domain == "clipboard" and step.clipboard_action:
                act = step.clipboard_action
                if act.action_type == "copy" and act.text:
                    self.clipboard.copy(act.text)
                elif act.action_type == "paste":
                    result.stdout = self.clipboard.paste()
                elif act.action_type == "cut":
                    result.stdout = self.clipboard.cut()
                elif act.action_type == "read":
                    result.stdout = self.clipboard.read()
                elif act.action_type == "clear":
                    self.clipboard.clear()
                elif act.action_type == "restore":
                    self.clipboard.restore_history()

            elif step.domain == "window" and step.window_action:
                act = step.window_action
                if act.action_type == "focus" and act.title:
                    self.window.focus_window(act.title)
                    context.active_window_title = act.title
                elif act.action_type == "maximize" and act.title:
                    self.window.maximize(act.title)
                elif act.action_type == "minimize" and act.title:
                    self.window.minimize(act.title)
                elif act.action_type == "restore" and act.title:
                    self.window.restore(act.title)
                elif act.action_type == "resize" and act.title and act.width and act.height:
                    self.window.resize(act.title, act.width, act.height)
                elif act.action_type == "move" and act.title and act.x and act.y:
                    self.window.move(act.title, act.x, act.y)
                elif act.action_type == "close" and act.title:
                    self.window.close(act.title)

            elif step.domain == "browser" and step.browser_action:
                act = step.browser_action
                if act.action_type == "open" and act.url:
                    await self.browser.open_url(act.url)
                elif act.action_type == "navigate" and act.url:
                    await self.browser.navigate(act.url)
                elif act.action_type == "refresh":
                    await self.browser.refresh()
                elif act.action_type == "back":
                    await self.browser.back()
                elif act.action_type == "forward":
                    await self.browser.forward()
                elif act.action_type == "click" and act.selector:
                    await self.browser.click_element(act.selector)
                elif act.action_type == "fill" and act.selector and act.value:
                    await self.browser.fill_input(act.selector, act.value)
                elif act.action_type == "screenshot" and act.value:
                    await self.browser.screenshot(act.value)
                    result.screenshot_path = act.value
                elif act.action_type == "dom":
                    result.stdout = await self.browser.extract_dom()

            elif step.domain == "explorer" and step.explorer_action:
                act = step.explorer_action
                if act.action_type == "open_dir":
                    self.explorer.open_directory(act.path)
                elif act.action_type == "open_file":
                    self.explorer.open_file(act.path)
                elif act.action_type == "create_folder":
                    self.explorer.create_folder(act.path)
                elif act.action_type == "rename" and act.new_name:
                    self.explorer.rename(act.path, act.new_name)
                elif act.action_type == "move" and act.destination:
                    self.explorer.move(act.path, act.destination)
                elif act.action_type == "copy" and act.destination:
                    self.explorer.copy(act.path, act.destination)
                elif act.action_type == "delete":
                    self.explorer.delete(act.path)
                elif act.action_type == "search" and act.destination:
                    result.stdout = "\n".join(self.explorer.search(act.path, act.destination))

            elif step.domain == "terminal" and step.terminal_action:
                act = step.terminal_action
                if act.action_type == "launch":
                    self.terminal.launch_terminal()
                elif act.action_type == "execute" and act.command:
                    result.stdout = self.terminal.execute_command(act.command, act.cwd, act.env)
                elif act.action_type == "capture":
                    result.stdout = self.terminal.capture_output()
                elif act.action_type == "clear":
                    self.terminal.clear_terminal()
                elif act.action_type == "cd" and act.cwd:
                    self.terminal.change_directory(act.cwd)
                elif act.action_type == "env" and act.cwd:
                    self.terminal.activate_environment(act.cwd)

            elif step.domain == "process" and step.process_action:
                act = step.process_action
                if act.action_type == "list":
                    result.stdout = json.dumps(self.process.list_processes())
                elif act.action_type == "find" and act.process_name:
                    result.stdout = json.dumps(self.process.find_process(act.process_name))
                elif act.action_type == "terminate" and act.pid:
                    self.process.terminate_process(act.pid)
                    context.active_pid = None
                elif act.action_type == "restart" and act.pid:
                    self.process.restart_process(act.pid)
                elif act.action_type == "monitor" and act.pid:
                    result.stdout = json.dumps(self.process.monitor_process(act.pid))
                elif act.action_type == "resource_usage" and act.pid:
                    result.stdout = json.dumps(self.process.resource_usage(act.pid))

        except Exception as err:
            logger.error("Step execution failed", step_id=step.step_id, error=str(err))
            result.status = "failed"
            result.error_message = str(err)

        return result
