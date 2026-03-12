"""Abstract compositor backend protocol."""

from abc import ABC, abstractmethod

from modules.models import AppInfo, ScreenInfo, WindowInfo


class CompositorBackend(ABC):
    """Protocol for compositor-specific operations."""

    # --- Screenshots ---

    @abstractmethod
    def capture_screen(self, index: int, output_path: str) -> str:
        """Capture a monitor by index. Returns path to saved PNG."""

    @abstractmethod
    def capture_window(self, address: str, output_path: str) -> str:
        """Capture a specific window by address/geometry. Returns path to saved PNG."""

    # --- Windows ---

    @abstractmethod
    def list_windows(self, app_filter: str | None = None) -> list[WindowInfo]:
        """List windows, optionally filtered by app class/title."""

    @abstractmethod
    def active_window(self) -> WindowInfo | None:
        """Get the currently focused window."""

    @abstractmethod
    def focus_window(self, address: str) -> None:
        """Focus/activate a window by address."""

    @abstractmethod
    def move_window(self, address: str, x: int, y: int) -> None:
        """Move window to absolute position."""

    @abstractmethod
    def resize_window(self, address: str, width: int, height: int) -> None:
        """Resize window to exact dimensions."""

    @abstractmethod
    def close_window(self, address: str) -> None:
        """Close a window."""

    @abstractmethod
    def fullscreen_window(self, address: str) -> None:
        """Toggle fullscreen for a window."""

    # --- Monitors ---

    @abstractmethod
    def list_screens(self) -> list[ScreenInfo]:
        """List connected monitors."""

    # --- Apps ---

    @abstractmethod
    def list_apps(self) -> list[AppInfo]:
        """List running GUI applications (unique by class)."""

    @abstractmethod
    def frontmost_app(self) -> AppInfo | None:
        """Get the frontmost/focused application."""

    @abstractmethod
    def activate_app(self, name: str) -> None:
        """Focus/activate an app by name or class."""

    @abstractmethod
    def launch_app(self, name: str) -> None:
        """Launch an application by name."""
