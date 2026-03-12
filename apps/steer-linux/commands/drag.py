"""Drag between elements or coordinates."""

import click

from modules import element_store, input as inp
from modules.output import emit


@click.command()
@click.option("--from", "from_target", help="Source element ID or label")
@click.option("--from-x", type=int, help="Source X coordinate")
@click.option("--from-y", type=int, help="Source Y coordinate")
@click.option("--to", "to_target", help="Destination element ID or label")
@click.option("--to-x", type=int, help="Destination X coordinate")
@click.option("--to-y", type=int, help="Destination Y coordinate")
@click.option("--snapshot", help="Snapshot ID")
@click.option("--steps", default=20, help="Intermediate drag points (default: 20)")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
def drag(
    from_target: str | None,
    from_x: int | None,
    from_y: int | None,
    to_target: str | None,
    to_x: int | None,
    to_y: int | None,
    snapshot: str | None,
    steps: int,
    use_json: bool,
) -> None:
    """Drag from one element/point to another."""
    from_label = ""
    to_label = ""

    if from_target:
        el = element_store.resolve(from_target, snap=snapshot)
        sx, sy = el.center_x, el.center_y
        from_label = f'{el.id} "{el.label}"'
    elif from_x is not None and from_y is not None:
        sx, sy = from_x, from_y
    else:
        raise click.UsageError("Provide --from <element> or --from-x/--from-y")

    if to_target:
        el = element_store.resolve(to_target, snap=snapshot)
        dx, dy = el.center_x, el.center_y
        to_label = f'{el.id} "{el.label}"'
    elif to_x is not None and to_y is not None:
        dx, dy = to_x, to_y
    else:
        raise click.UsageError("Provide --to <element> or --to-x/--to-y")

    inp.mouse_drag(sx, sy, dx, dy, steps=steps)

    src = from_label or f"({sx}, {sy})"
    dst = to_label or f"({dx}, {dy})"
    emit(
        {"action": "drag", "fromX": sx, "fromY": sy, "toX": dx, "toY": dy, "ok": True},
        json=use_json,
        human_lines=f"Dragged {src} -> {dst}",
    )
