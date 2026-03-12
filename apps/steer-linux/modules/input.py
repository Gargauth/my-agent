"""Mouse (ydotool) + keyboard (wtype) input injection.

Port of MouseControl.swift + Keyboard.swift for Linux/Wayland.
"""

import subprocess
import time

from modules.errors import ToolNotFound


def _run(cmd: list[str], tool_name: str, install_hint: str) -> None:
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=True)
    except FileNotFoundError:
        raise ToolNotFound(tool_name, install_hint)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"{tool_name} failed: {e.stderr.strip()}")


# --- Mouse (ydotool) ---


def mouse_move(x: int, y: int) -> None:
    """Move mouse cursor to absolute position."""
    _run(
        ["ydotool", "mousemove", "--absolute", "-x", str(x), "-y", str(y)],
        "ydotool",
        "sudo pacman -S ydotool && systemctl --user enable --now ydotoold",
    )


def mouse_click(
    x: int,
    y: int,
    button: str = "left",
    count: int = 1,
) -> None:
    """Click at coordinates. button: left/right/middle."""
    mouse_move(x, y)
    time.sleep(0.02)

    btn_code = {"left": "0xC0", "right": "0xC1", "middle": "0xC2"}.get(button, "0xC0")

    for _ in range(count):
        _run(
            ["ydotool", "click", btn_code],
            "ydotool",
            "sudo pacman -S ydotool && systemctl --user enable --now ydotoold",
        )
        if count > 1:
            time.sleep(0.05)


def mouse_drag(
    from_x: int,
    from_y: int,
    to_x: int,
    to_y: int,
    steps: int = 20,
) -> None:
    """Drag from one point to another with interpolation."""
    mouse_move(from_x, from_y)
    time.sleep(0.05)

    # Mouse down
    _run(
        ["ydotool", "click", "--next-delay", "0", "0x40"],
        "ydotool",
        "sudo pacman -S ydotool",
    )
    time.sleep(0.1)

    # Interpolate movement
    for i in range(1, steps + 1):
        t = i / steps
        ix = int(from_x + (to_x - from_x) * t)
        iy = int(from_y + (to_y - from_y) * t)
        mouse_move(ix, iy)
        time.sleep(0.01)

    time.sleep(0.05)
    # Mouse up
    _run(
        ["ydotool", "click", "--next-delay", "0", "0x80"],
        "ydotool",
        "sudo pacman -S ydotool",
    )


def mouse_scroll(dx: int = 0, dy: int = 0) -> None:
    """Scroll by delta. Positive dy = up, negative = down."""
    # ydotool scroll: positive = up, which matches our convention
    # For horizontal: not directly supported by ydotool easily,
    # but we handle the common vertical case
    if dy != 0:
        # ydotool expects: positive = scroll up
        _run(
            ["ydotool", "mousemove", "--wheel", "--", "0", str(dy)],
            "ydotool",
            "sudo pacman -S ydotool",
        )
    if dx != 0:
        _run(
            ["ydotool", "mousemove", "--wheel", "--", str(dx), "0"],
            "ydotool",
            "sudo pacman -S ydotool",
        )


# --- Keyboard (wtype) ---

# Modifier mapping for wtype
_MODIFIERS = {
    "super": "super",
    "cmd": "super",
    "command": "super",
    "shift": "shift",
    "alt": "alt",
    "option": "alt",
    "opt": "alt",
    "ctrl": "ctrl",
    "control": "ctrl",
}

# Special key names for wtype -k
_SPECIAL_KEYS = {
    "return": "Return",
    "enter": "Return",
    "tab": "Tab",
    "space": "space",
    "delete": "BackSpace",
    "backspace": "BackSpace",
    "escape": "Escape",
    "esc": "Escape",
    "left": "Left",
    "right": "Right",
    "down": "Down",
    "up": "Up",
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",
    "home": "Home",
    "end": "End",
    "pageup": "Prior",
    "pagedown": "Next",
    "forwarddelete": "Delete",
}


def type_text(text: str) -> None:
    """Type a string of text."""
    _run(
        ["wtype", "--", text],
        "wtype",
        "sudo pacman -S wtype",
    )


def hotkey(combo: str) -> None:
    """Execute a key combination like 'super+s', 'ctrl+shift+n', 'return'."""
    parts = combo.lower().split("+")
    key_part = parts[-1]
    mod_parts = parts[:-1]

    # Build wtype command
    cmd: list[str] = ["wtype"]

    # Add modifiers
    for mod in mod_parts:
        wtype_mod = _MODIFIERS.get(mod)
        if wtype_mod:
            cmd.extend(["-M", wtype_mod])

    # Add key
    special = _SPECIAL_KEYS.get(key_part)
    if special:
        cmd.extend(["-k", special])
    elif len(key_part) == 1:
        cmd.extend(["-k", key_part])
    else:
        cmd.extend(["-k", key_part])

    # Release modifiers (in reverse)
    for mod in reversed(mod_parts):
        wtype_mod = _MODIFIERS.get(mod)
        if wtype_mod:
            cmd.extend(["-m", wtype_mod])

    _run(cmd, "wtype", "sudo pacman -S wtype")
