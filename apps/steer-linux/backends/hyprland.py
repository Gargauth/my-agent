"""Hyprland compositor backend using hyprctl IPC."""

import json
import subprocess

from backends.base import CompositorBackend
from modules.errors import (
    AppNotFound,
    CaptureFailure,
    ScreenNotFound,
    ToolNotFound,
    WindowActionFailed,
    WindowNotFound,
)
from modules.models import AppInfo, ScreenInfo, WindowInfo


def _hyprctl(*args: str) -> str:
    """Run hyprctl and return stdout."""
    try:
        r = subprocess.run(
            ["hyprctl", "-j", *args],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except FileNotFoundError:
        raise ToolNotFound("hyprctl", "Install Hyprland")
    if r.returncode != 0:
        raise RuntimeError(f"hyprctl {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def _hyprctl_dispatch(*args: str) -> None:
    """Run hyprctl dispatch command (no JSON needed)."""
    try:
        r = subprocess.run(
            ["hyprctl", "dispatch", *args],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except FileNotFoundError:
        raise ToolNotFound("hyprctl", "Install Hyprland")
    if r.returncode != 0:
        raise RuntimeError(f"hyprctl dispatch {' '.join(args)}: {r.stderr.strip()}")


def _grim(*args: str) -> None:
    """Run grim screenshot tool."""
    try:
        r = subprocess.run(
            ["grim", *args],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        raise ToolNotFound("grim", "sudo pacman -S grim")
    if r.returncode != 0:
        raise CaptureFailure(f"grim failed: {r.stderr.strip()}")


class HyprlandBackend(CompositorBackend):
    """Hyprland compositor backend."""

    def _monitors(self) -> list[dict]:
        return json.loads(_hyprctl("monitors"))

    def _clients(self) -> list[dict]:
        return json.loads(_hyprctl("clients"))

    # --- Screenshots ---

    def capture_screen(self, index: int, output_path: str) -> str:
        monitors = self._monitors()
        if index < 0 or index >= len(monitors):
            raise ScreenNotFound(index, len(monitors))
        name = monitors[index]["name"]
        _grim("-o", name, output_path)
        return output_path

    def capture_window(self, address: str, output_path: str) -> str:
        clients = self._clients()
        client = next(
            (c for c in clients if c.get("address") == address),
            None,
        )
        if client is None:
            raise WindowNotFound(address)
        at = client.get("at", [0, 0])
        size = client.get("size", [0, 0])
        region = f"{at[0]},{at[1]} {size[0]}x{size[1]}"
        _grim("-g", region, output_path)
        return output_path

    # --- Windows ---

    def list_windows(self, app_filter: str | None = None) -> list[WindowInfo]:
        clients = self._clients()
        if app_filter:
            f = app_filter.lower()
            clients = [
                c
                for c in clients
                if f in c.get("class", "").lower()
                or f in c.get("title", "").lower()
            ]
        return [self._client_to_window(c) for c in clients]

    def active_window(self) -> WindowInfo | None:
        try:
            data = json.loads(_hyprctl("activewindow"))
        except Exception:
            return None
        if not data or not data.get("address"):
            return None
        return self._client_to_window(data)

    def focus_window(self, address: str) -> None:
        _hyprctl_dispatch("focuswindow", f"address:{address}")

    def move_window(self, address: str, x: int, y: int) -> None:
        try:
            _hyprctl_dispatch(
                "movewindowpixel", f"exact {x} {y},address:{address}"
            )
        except RuntimeError as e:
            raise WindowActionFailed("move", address) from e

    def resize_window(self, address: str, width: int, height: int) -> None:
        try:
            _hyprctl_dispatch(
                "resizewindowpixel", f"exact {width} {height},address:{address}"
            )
        except RuntimeError as e:
            raise WindowActionFailed("resize", address) from e

    def close_window(self, address: str) -> None:
        _hyprctl_dispatch("closewindow", f"address:{address}")

    def fullscreen_window(self, address: str) -> None:
        # Focus the window first, then toggle fullscreen
        _hyprctl_dispatch("focuswindow", f"address:{address}")
        _hyprctl_dispatch("fullscreen", "1")

    # --- Monitors ---

    def list_screens(self) -> list[ScreenInfo]:
        monitors = self._monitors()
        return [
            ScreenInfo(
                index=i,
                name=m["name"],
                width=m.get("width", 0),
                height=m.get("height", 0),
                x=m.get("x", 0),
                y=m.get("y", 0),
                scale=m.get("scale", 1.0),
                transform=m.get("transform", 0),
                is_focused=m.get("focused", False),
            )
            for i, m in enumerate(monitors)
        ]

    # --- Apps ---

    def list_apps(self) -> list[AppInfo]:
        clients = self._clients()
        active = self.active_window()
        active_addr = active.address if active else ""
        seen: dict[str, AppInfo] = {}
        for c in clients:
            cls = c.get("class", "") or c.get("title", "unknown")
            if cls not in seen:
                seen[cls] = AppInfo(
                    name=c.get("title", cls),
                    pid=c.get("pid", 0),
                    window_class=cls,
                    is_active=c.get("address", "") == active_addr,
                )
        return list(seen.values())

    def frontmost_app(self) -> AppInfo | None:
        win = self.active_window()
        if not win:
            return None
        return AppInfo(
            name=win.title or win.app,
            pid=win.pid,
            window_class=win.app,
            is_active=True,
        )

    def activate_app(self, name: str) -> None:
        clients = self._clients()
        n = name.lower()
        client = next(
            (
                c
                for c in clients
                if n in c.get("class", "").lower()
                or n in c.get("title", "").lower()
            ),
            None,
        )
        if client is None:
            raise AppNotFound(name)
        _hyprctl_dispatch("focuswindow", f"address:{client['address']}")

    def launch_app(self, name: str) -> None:
        try:
            subprocess.Popen(
                [name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except FileNotFoundError:
            raise AppNotFound(name)

    # --- Helpers ---

    @staticmethod
    def _client_to_window(c: dict) -> WindowInfo:
        at = c.get("at", [0, 0])
        size = c.get("size", [0, 0])
        return WindowInfo(
            app=c.get("class", ""),
            title=c.get("title", ""),
            x=at[0] if isinstance(at, list) else 0,
            y=at[1] if isinstance(at, list) else 0,
            width=size[0] if isinstance(size, list) else 0,
            height=size[1] if isinstance(size, list) else 0,
            address=c.get("address", ""),
            workspace=c.get("workspace", {}).get("id", -1)
            if isinstance(c.get("workspace"), dict)
            else c.get("workspace", -1),
            is_fullscreen=bool(c.get("fullscreen")),
            is_floating=bool(c.get("floating")),
            pid=c.get("pid", 0),
        )
