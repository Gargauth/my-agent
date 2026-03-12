"""Auto-detect the running compositor."""

import os

from backends.base import CompositorBackend
from modules.errors import CompositorNotFound


def detect_backend() -> CompositorBackend:
    """Detect the running compositor and return the appropriate backend."""
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        from backends.hyprland import HyprlandBackend

        return HyprlandBackend()

    # Future: KDE, GNOME, Sway, etc.
    # if os.environ.get("KDE_SESSION_VERSION"):
    #     from backends.kde import KDEBackend
    #     return KDEBackend()

    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "hyprland" in desktop:
        from backends.hyprland import HyprlandBackend

        return HyprlandBackend()

    raise CompositorNotFound()
