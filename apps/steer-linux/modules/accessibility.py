"""AT-SPI2 accessibility tree walker — port of AccessibilityTree.swift.

Uses pyatspi2 to traverse the accessibility tree on Linux.
"""

from modules.models import UIElement

# AT-SPI2 role → prefix mapping (mirrors macOS AX roles)
_ROLE_PREFIX: dict[str, str] = {
    "push button": "B",
    "toggle button": "B",
    "text": "T",
    "password text": "T",
    "entry": "T",
    "paragraph": "T",
    "terminal": "T",
    "label": "S",
    "static": "S",
    "image": "I",
    "icon": "I",
    "check box": "C",
    "check menu item": "C",
    "radio button": "R",
    "radio menu item": "R",
    "combo box": "P",
    "slider": "SL",
    "spin button": "SL",
    "link": "L",
    "menu item": "M",
    "menu": "M",
    "page tab": "TB",
    "page tab list": "TB",
    "list item": "E",
    "table cell": "E",
    "tree item": "E",
}

_INTERACTIVE_ROLES: set[str] = {
    "push button",
    "toggle button",
    "text",
    "password text",
    "entry",
    "paragraph",
    "terminal",
    "check box",
    "check menu item",
    "radio button",
    "radio menu item",
    "combo box",
    "slider",
    "spin button",
    "link",
    "menu item",
    "menu",
    "page tab",
    "label",
    "static",
    "image",
    "icon",
    "list item",
    "table cell",
    "tree item",
    "tool bar",
}


def _get_prefix(role_name: str) -> str:
    return _ROLE_PREFIX.get(role_name, "E")


def _is_interactive(role_name: str) -> bool:
    return role_name in _INTERACTIVE_ROLES


def walk(pid: int, max_depth: int = 10) -> list[UIElement]:
    """Walk the accessibility tree for a process. Returns interactive elements."""
    try:
        import pyatspi  # type: ignore[import-untyped]
    except ImportError:
        return []

    desktop = pyatspi.Registry.getDesktop(0)

    # Find the app by PID
    target_app = None
    for i in range(desktop.childCount):
        try:
            app = desktop.getChildAtIndex(i)
            if app and app.get_process_id() == pid:
                target_app = app
                break
        except Exception:
            continue

    if target_app is None:
        return []

    raw: list[tuple[str, str, str | None, int, int, int, int, bool, int]] = []
    _walk_element(target_app, 0, max_depth, raw)

    # Filter to visible, interactive elements
    visible = [
        r
        for r in raw
        if r[4] > 1 and r[5] > 1 and _is_interactive(r[0])  # width  # height
    ]

    return _assign_ids(visible)


def _walk_element(
    el: object,
    depth: int,
    max_depth: int,
    out: list[tuple[str, str, str | None, int, int, int, int, bool, int]],
) -> None:
    if depth >= max_depth:
        return

    try:
        import pyatspi  # type: ignore[import-untyped]

        role = el.getRoleName()  # type: ignore[union-attr]
        name = el.name or ""  # type: ignore[union-attr]

        # Try to get value
        value = None
        try:
            text_iface = el.queryText()  # type: ignore[union-attr]
            if text_iface:
                value = text_iface.getText(0, text_iface.characterCount)
        except Exception:
            pass

        # Get position and size
        try:
            component = el.queryComponent()  # type: ignore[union-attr]
            if component:
                ext = component.getExtents(pyatspi.DESKTOP_COORDS)
                x, y, w, h = ext.x, ext.y, ext.width, ext.height
            else:
                x, y, w, h = 0, 0, 0, 0
        except Exception:
            x, y, w, h = 0, 0, 0, 0

        # Check enabled state
        try:
            states = el.getState()  # type: ignore[union-attr]
            enabled = states.contains(pyatspi.STATE_ENABLED)
        except Exception:
            enabled = True

        out.append((role, name, value, x, y, w, h, enabled, depth))

        # Walk children
        try:
            for i in range(el.childCount):  # type: ignore[union-attr]
                try:
                    child = el.getChildAtIndex(i)  # type: ignore[union-attr]
                    if child:
                        _walk_element(child, depth + 1, max_depth, out)
                except Exception:
                    continue
        except Exception:
            pass

    except Exception:
        pass


def _assign_ids(
    elements: list[tuple[str, str, str | None, int, int, int, int, bool, int]],
) -> list[UIElement]:
    counters: dict[str, int] = {}
    result: list[UIElement] = []
    for role, label, value, x, y, w, h, enabled, depth in elements:
        prefix = _get_prefix(role)
        counters[prefix] = counters.get(prefix, 0) + 1
        result.append(
            UIElement(
                id=f"{prefix}{counters[prefix]}",
                role=role,
                label=label,
                x=x,
                y=y,
                width=w,
                height=h,
                is_enabled=enabled,
                depth=depth,
                value=value,
            )
        )
    return result


def focused_element(pid: int) -> UIElement | None:
    """Get the currently focused element for a process."""
    try:
        import pyatspi  # type: ignore[import-untyped]
    except ImportError:
        return None

    desktop = pyatspi.Registry.getDesktop(0)

    target_app = None
    for i in range(desktop.childCount):
        try:
            app = desktop.getChildAtIndex(i)
            if app and app.get_process_id() == pid:
                target_app = app
                break
        except Exception:
            continue

    if target_app is None:
        return None

    try:
        # Get focused element through the app
        focused = None
        try:
            # Try to find focused element through state
            def find_focused(el: object) -> object | None:
                try:
                    states = el.getState()  # type: ignore[union-attr]
                    if states.contains(pyatspi.STATE_FOCUSED):
                        return el
                    for i in range(el.childCount):  # type: ignore[union-attr]
                        child = el.getChildAtIndex(i)  # type: ignore[union-attr]
                        if child:
                            result = find_focused(child)
                            if result:
                                return result
                except Exception:
                    pass
                return None

            focused = find_focused(target_app)
        except Exception:
            pass

        if focused is None:
            return None

        role = focused.getRoleName()  # type: ignore[union-attr]
        name = focused.name or ""  # type: ignore[union-attr]
        value = None
        try:
            text_iface = focused.queryText()  # type: ignore[union-attr]
            if text_iface:
                value = text_iface.getText(0, text_iface.characterCount)
        except Exception:
            pass

        try:
            component = focused.queryComponent()  # type: ignore[union-attr]
            ext = component.getExtents(pyatspi.DESKTOP_COORDS)
            x, y, w, h = ext.x, ext.y, ext.width, ext.height
        except Exception:
            x, y, w, h = 0, 0, 0, 0

        try:
            states = focused.getState()  # type: ignore[union-attr]
            enabled = states.contains(pyatspi.STATE_ENABLED)
        except Exception:
            enabled = True

        return UIElement(
            id="F0",
            role=role,
            label=name,
            x=x,
            y=y,
            width=w,
            height=h,
            is_enabled=enabled,
            depth=0,
            value=value,
        )

    except Exception:
        return None
