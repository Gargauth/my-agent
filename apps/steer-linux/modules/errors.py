"""Error hierarchy for steer-linux CLI."""

import click


class SteerError(click.ClickException):
    """Base error for all steer operations."""

    code: str = "error"

    def __init__(self, message: str):
        super().__init__(message)

    def to_dict(self) -> dict:
        return {"ok": False, "error": self.code, "message": self.message}


class CaptureFailure(SteerError):
    code = "capture_failure"

    def __init__(self, msg: str):
        super().__init__(f"Capture failed: {msg}")


class AppNotFound(SteerError):
    code = "app_not_found"

    def __init__(self, name: str):
        super().__init__(f"App not found: {name}")


class ElementNotFound(SteerError):
    code = "element_not_found"

    def __init__(self, query: str):
        super().__init__(f"Element not found: {query}")


class NoSnapshot(SteerError):
    code = "no_snapshot"

    def __init__(self):
        super().__init__("No snapshot. Run 'steer see' first.")


class ScreenNotFound(SteerError):
    code = "screen_not_found"

    def __init__(self, index: int, available: int):
        super().__init__(
            f"Screen {index} not found. {available} screen(s) available (use 0-{available - 1}). "
            "Run 'steer screens' to list."
        )


class WindowNotFound(SteerError):
    code = "window_not_found"

    def __init__(self, name: str):
        super().__init__(f"No window found for app: {name}")


class WindowActionFailed(SteerError):
    code = "window_action_failed"

    def __init__(self, action: str, name: str):
        super().__init__(f"Window {action} failed for: {name}")


class ClipboardEmpty(SteerError):
    code = "clipboard_empty"

    def __init__(self, content_type: str):
        super().__init__(f"Clipboard has no {content_type} content")


class WaitTimeout(SteerError):
    code = "wait_timeout"

    def __init__(self, condition: str, seconds: float):
        super().__init__(f"Timeout after {int(seconds)}s waiting for {condition}")


class OcrFailed(SteerError):
    code = "ocr_failed"

    def __init__(self, msg: str):
        super().__init__(f"OCR failed: {msg}")


class CompositorNotFound(SteerError):
    code = "compositor_not_found"

    def __init__(self):
        super().__init__(
            "No supported compositor detected. Currently supported: Hyprland. "
            "Set $HYPRLAND_INSTANCE_SIGNATURE or run under Hyprland."
        )


class ToolNotFound(SteerError):
    code = "tool_not_found"

    def __init__(self, tool: str, install_hint: str):
        super().__init__(f"{tool} not found. Install with: {install_hint}")
