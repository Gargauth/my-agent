"""Data models for steer-linux."""

from dataclasses import dataclass, field


@dataclass
class UIElement:
    id: str
    role: str
    label: str
    x: int
    y: int
    width: int
    height: int
    is_enabled: bool = True
    depth: int = 0
    value: str | None = None

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def center_y(self) -> int:
        return self.y + self.height // 2

    def to_dict(self) -> dict:
        d: dict = {
            "id": self.id,
            "role": self.role,
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "isEnabled": self.is_enabled,
            "depth": self.depth,
        }
        if self.value is not None:
            d["value"] = self.value
        return d


@dataclass
class ScreenInfo:
    index: int
    name: str
    width: int
    height: int
    x: int
    y: int
    scale: float = 1.0
    transform: int = 0
    is_focused: bool = False

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "x": self.x,
            "y": self.y,
            "scale": self.scale,
            "transform": self.transform,
            "isFocused": self.is_focused,
        }


@dataclass
class WindowInfo:
    app: str
    title: str
    x: int
    y: int
    width: int
    height: int
    address: str = ""
    workspace: int = -1
    is_fullscreen: bool = False
    is_floating: bool = False
    pid: int = 0

    def to_dict(self) -> dict:
        return {
            "app": self.app,
            "title": self.title,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "address": self.address,
            "workspace": self.workspace,
            "isFullscreen": self.is_fullscreen,
            "isFloating": self.is_floating,
            "pid": self.pid,
        }


@dataclass
class AppInfo:
    name: str
    pid: int
    window_class: str
    is_active: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "pid": self.pid,
            "class": self.window_class,
            "isActive": self.is_active,
        }


@dataclass
class OCRResult:
    text: str
    confidence: float
    x: int
    y: int
    width: int
    height: int

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }
