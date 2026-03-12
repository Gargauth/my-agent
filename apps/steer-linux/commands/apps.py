"""List, launch, or activate apps."""

import click

from backends.base import CompositorBackend
from modules.output import emit


@click.command()
@click.argument("action", default="list")
@click.argument("name", required=False)
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
@click.pass_obj
def apps(backend: CompositorBackend, action: str, name: str | None, use_json: bool) -> None:
    """List running apps, launch, or activate by name."""
    action = action.lower()

    if action == "list":
        app_list = backend.list_apps()
        if use_json:
            emit(
                {"apps": [a.to_dict() for a in app_list], "count": len(app_list)},
                json=True,
                human_lines="",
            )
        else:
            for a in app_list:
                star = " *" if a.is_active else ""
                click.echo(f"  {a.name:<25} pid:{a.pid}  class:{a.window_class}{star}")

    elif action == "launch":
        if not name:
            raise click.UsageError("Provide app name")
        backend.launch_app(name)
        emit(
            {"action": "launch", "app": name, "ok": True},
            json=use_json,
            human_lines=f"Launched {name}",
        )

    elif action in ("activate", "focus"):
        if not name:
            raise click.UsageError("Provide app name")
        backend.activate_app(name)
        emit(
            {"action": "activate", "app": name, "ok": True},
            json=use_json,
            human_lines=f"Activated {name}",
        )

    else:
        raise click.UsageError("Action must be: list, launch, activate")
