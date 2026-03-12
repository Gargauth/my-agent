"""Scroll in a direction."""

import click

from modules import input as inp
from modules.output import emit


@click.command()
@click.argument("direction")
@click.argument("lines", default=3, type=int)
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
def scroll(direction: str, lines: int, use_json: bool) -> None:
    """Scroll in a direction (up/down/left/right) by N lines."""
    d = direction.lower()
    dx, dy = 0, 0
    if d == "up":
        dy = lines
    elif d == "down":
        dy = -lines
    elif d == "left":
        dx = lines
    elif d == "right":
        dx = -lines
    else:
        raise click.UsageError("Direction must be: up, down, left, right")

    inp.mouse_scroll(dx=dx, dy=dy)
    emit(
        {"action": "scroll", "direction": direction, "lines": lines, "ok": True},
        json=use_json,
        human_lines=f"Scrolled {direction} {lines} lines",
    )
