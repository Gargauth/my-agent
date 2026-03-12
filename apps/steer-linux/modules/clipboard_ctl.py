"""Clipboard control via wl-clipboard — port of ClipboardControl.swift."""

import subprocess
from pathlib import Path

from modules.errors import ClipboardEmpty, ToolNotFound


def _run_clip(cmd: list[str], tool: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=5
        )
    except FileNotFoundError:
        raise ToolNotFound(tool, "sudo pacman -S wl-clipboard")


def read_text() -> str | None:
    """Read text from clipboard."""
    r = _run_clip(["wl-paste", "--no-newline"], "wl-paste")
    if r.returncode != 0:
        return None
    return r.stdout


def write_text(text: str) -> None:
    """Write text to clipboard."""
    try:
        p = subprocess.Popen(
            ["wl-copy"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        p.communicate(input=text.encode(), timeout=5)
    except FileNotFoundError:
        raise ToolNotFound("wl-copy", "sudo pacman -S wl-clipboard")


def available_type() -> str:
    """Detect clipboard content type: text, image, or empty."""
    r = _run_clip(["wl-paste", "--list-types"], "wl-paste")
    if r.returncode != 0:
        return "empty"
    types = r.stdout.strip()
    if not types:
        return "empty"
    if "image/" in types:
        return "image"
    if "text/" in types or "STRING" in types or "UTF8_STRING" in types:
        return "text"
    return "empty"


def read_image(save_to: str | None = None) -> str:
    """Read image from clipboard and save as PNG."""
    output_path = save_to or str(
        Path("/tmp/steer") / f"clipboard-{_short_uuid()}.png"
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    r = _run_clip(
        ["wl-paste", "--type", "image/png"],
        "wl-paste",
    )
    if r.returncode != 0:
        # Try without type specification
        try:
            r2 = subprocess.run(
                ["wl-paste"],
                capture_output=True,
                timeout=5,
            )
            if r2.returncode != 0 or not r2.stdout:
                raise ClipboardEmpty("image")
            Path(output_path).write_bytes(r2.stdout)
            return output_path
        except FileNotFoundError:
            raise ToolNotFound("wl-paste", "sudo pacman -S wl-clipboard")

    # wl-paste with text=True won't work for binary, re-run for binary
    try:
        r2 = subprocess.run(
            ["wl-paste", "--type", "image/png"],
            capture_output=True,
            timeout=5,
        )
        if not r2.stdout:
            raise ClipboardEmpty("image")
        Path(output_path).write_bytes(r2.stdout)
    except FileNotFoundError:
        raise ToolNotFound("wl-paste", "sudo pacman -S wl-clipboard")

    return output_path


def write_image(from_path: str) -> None:
    """Copy image to clipboard from a file."""
    path = Path(from_path)
    if not path.exists():
        raise ClipboardEmpty(f"image at {from_path}")

    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    try:
        p = subprocess.Popen(
            ["wl-copy", "--type", mime],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        p.communicate(input=path.read_bytes(), timeout=5)
    except FileNotFoundError:
        raise ToolNotFound("wl-copy", "sudo pacman -S wl-clipboard")


def _short_uuid() -> str:
    import uuid

    return str(uuid.uuid4())[:8]
