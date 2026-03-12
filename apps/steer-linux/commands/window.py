"""Window management commands."""

import click

from backends.base import CompositorBackend
from modules.errors import AppNotFound
from modules.output import emit


@click.command()
@click.argument("action")
@click.argument("app")
@click.option("-x", type=int, help="X position (for move)")
@click.option("-y", type=int, help="Y position (for move)")
@click.option("-w", "--width", type=int, help="Width (for resize)")
@click.option("-h", "--height", type=int, help="Height (for resize)")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
@click.pass_obj
def window(
    backend: CompositorBackend,
    action: str,
    app: str,
    x: int | None,
    y: int | None,
    width: int | None,
    height: int | None,
    use_json: bool,
) -> None:
    """Manage app windows: list, move, resize, minimize, fullscreen, close."""
    action = action.lower()
    windows = backend.list_windows(app)
    if not windows:
        raise AppNotFound(app)
    win = windows[0]

    if action == "list":
        if use_json:
            emit(
                {"windows": [w.to_dict() for w in windows], "count": len(windows)},
                json=True,
                human_lines="",
            )
        else:
            for i, w in enumerate(windows):
                title = w.title or "(untitled)"
                flags_parts = []
                if w.is_fullscreen:
                    flags_parts.append("fullscreen")
                if w.is_floating:
                    flags_parts.append("floating")
                flags = f"  [{', '.join(flags_parts)}]" if flags_parts else ""
                click.echo(
                    f'  {i}  "{title}"  ({w.x},{w.y} {w.width}x{w.height}){flags}'
                )

    elif action == "move":
        if x is None or y is None:
            raise click.UsageError("move requires -x and -y")
        backend.move_window(win.address, x, y)
        emit(
            {"action": "move", "app": app, "x": x, "y": y, "ok": True},
            json=use_json,
            human_lines=f"Moved {app} to ({x}, {y})",
        )

    elif action == "resize":
        if width is None or height is None:
            raise click.UsageError("resize requires --width and --height")
        backend.resize_window(win.address, width, height)
        emit(
            {"action": "resize", "app": app, "width": width, "height": height, "ok": True},
            json=use_json,
            human_lines=f"Resized {app} to {width}x{height}",
        )

    elif action == "fullscreen":
        backend.fullscreen_window(win.address)
        emit(
            {"action": "fullscreen", "app": app, "ok": True},
            json=use_json,
            human_lines=f"Toggled fullscreen for {app}",
        )

    elif action == "close":
        backend.close_window(win.address)
        emit(
            {"action": "close", "app": app, "ok": True},
            json=use_json,
            human_lines=f"Closed {app} window",
        )

    else:
        raise click.UsageError(
            "Action must be: list, move, resize, fullscreen, close"
        )
