"""List connected displays."""

import click

from backends.base import CompositorBackend
from modules.output import emit


@click.command()
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
@click.pass_obj
def screens(backend: CompositorBackend, use_json: bool) -> None:
    """List connected displays with index, resolution, and position."""
    monitors = backend.list_screens()
    if use_json:
        emit(
            {"screens": [s.to_dict() for s in monitors], "count": len(monitors)},
            json=True,
            human_lines="",
        )
    else:
        for s in monitors:
            focused = " (focused)" if s.is_focused else ""
            click.echo(
                f"  {s.index}  {s.name:<30} {s.width}x{s.height}  "
                f"at ({s.x},{s.y})  scale:{s.scale}{focused}"
            )
