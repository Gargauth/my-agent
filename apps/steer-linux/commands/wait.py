"""Wait for conditions."""

import time

import click

from backends.base import CompositorBackend
from modules import accessibility
from modules.errors import WaitTimeout
from modules.output import emit


@click.command()
@click.option("--for", "for_query", help="Element label or ID to wait for")
@click.option("--app", "app_name", help="App name (required for element wait, or alone to wait for app)")
@click.option("--timeout", default=10.0, help="Max seconds to wait (default: 10)")
@click.option("--interval", default=0.5, help="Poll interval in seconds (default: 0.5)")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
@click.pass_obj
def wait(
    backend: CompositorBackend,
    for_query: str | None,
    app_name: str | None,
    timeout: float,
    interval: float,
    use_json: bool,
) -> None:
    """Wait for an app to launch or a UI element to appear."""
    if not app_name and not for_query:
        raise click.UsageError("Provide --app, --for, or both")

    deadline = time.time() + timeout

    if app_name and not for_query:
        # Wait for app
        while time.time() < deadline:
            windows = backend.list_windows(app_name)
            if windows:
                emit(
                    {"action": "wait", "condition": "app", "app": app_name, "ok": True},
                    json=use_json,
                    human_lines=f"Found {app_name}",
                )
                return
            time.sleep(interval)
        if use_json:
            emit(
                {"action": "wait", "condition": "app", "app": app_name, "ok": False, "error": "timeout"},
                json=True,
                human_lines="",
            )
        raise WaitTimeout(f"app {app_name}", timeout)

    elif for_query:
        # Wait for element
        lq = for_query.lower()
        while time.time() < deadline:
            pid = None
            ctx_name = app_name or "frontmost"

            if app_name:
                windows = backend.list_windows(app_name)
                if windows:
                    pid = windows[0].pid
            else:
                active = backend.active_window()
                if active:
                    pid = active.pid
                    ctx_name = active.title or active.app

            if pid:
                elements = accessibility.walk(pid)
                match = (
                    next((e for e in elements if e.id.lower() == lq), None)
                    or next((e for e in elements if e.label.lower() == lq), None)
                    or next((e for e in elements if lq in e.label.lower()), None)
                )
                if match:
                    emit(
                        {
                            "action": "wait",
                            "condition": "element",
                            "id": match.id,
                            "label": match.label,
                            "app": ctx_name,
                            "ok": True,
                        },
                        json=use_json,
                        human_lines=f'Found {match.id} "{match.label}" in {ctx_name}',
                    )
                    return

            time.sleep(interval)

        if use_json:
            emit(
                {
                    "action": "wait",
                    "condition": "element",
                    "for": for_query,
                    "app": app_name or "frontmost",
                    "ok": False,
                    "error": "timeout",
                },
                json=True,
                human_lines="",
            )
        raise WaitTimeout(f'element "{for_query}" in {app_name or "frontmost"}', timeout)
