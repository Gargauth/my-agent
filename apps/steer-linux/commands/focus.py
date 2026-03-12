"""Show focused UI element."""

import click

from backends.base import CompositorBackend
from modules import accessibility
from modules.output import emit


@click.command()
@click.option("--app", "app_name", help="Target app name (default: frontmost)")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
@click.pass_obj
def focus(backend: CompositorBackend, app_name: str | None, use_json: bool) -> None:
    """Show the currently focused UI element."""
    if app_name:
        windows = backend.list_windows(app_name)
        if not windows:
            from modules.errors import AppNotFound

            raise AppNotFound(app_name)
        pid = windows[0].pid
        target_name = app_name
    else:
        active = backend.active_window()
        if not active or not active.pid:
            if use_json:
                emit({"app": "(none)", "focused": None}, json=True, human_lines="")
            else:
                click.echo("app: (none)")
                click.echo("focused: (none)")
            return
        pid = active.pid
        target_name = active.title or active.app

    el = accessibility.focused_element(pid)

    if el is None:
        if use_json:
            emit({"app": target_name, "focused": None}, json=True, human_lines="")
        else:
            click.echo(f"app: {target_name}")
            click.echo("focused: (none)")
        return

    if use_json:
        emit(
            {"app": target_name, "focused": el.to_dict()},
            json=True,
            human_lines="",
        )
    else:
        lbl = el.label if el.label else (el.value or "(no label)")
        lines = [
            f"app: {target_name}",
            f'focused: {el.role} "{lbl}"  ({el.x},{el.y} {el.width}x{el.height})',
        ]
        if el.value and el.label:
            lines.append(f'  value: "{el.value[:80]}"')
        emit({}, json=False, human_lines=lines)
