"""Click by ID, label, or coordinates."""

import click

from modules import element_store, input as inp
from modules.output import emit


@click.command("click")
@click.option("--on", "on_target", help="Element ID (B1) or label text")
@click.option("-x", type=int, help="X coordinate")
@click.option("-y", type=int, help="Y coordinate")
@click.option("--snapshot", help="Snapshot ID to resolve element from")
@click.option("--double", is_flag=True, help="Double-click")
@click.option("--right", is_flag=True, help="Right-click")
@click.option("--middle", is_flag=True, help="Middle-click")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
def click_cmd(
    on_target: str | None,
    x: int | None,
    y: int | None,
    snapshot: str | None,
    double: bool,
    right: bool,
    middle: bool,
    use_json: bool,
) -> None:
    """Click an element by ID (B1), label, or x,y coordinates."""
    if right and middle:
        raise click.UsageError("Cannot combine --right and --middle")

    label = ""
    if on_target:
        el = element_store.resolve(on_target, snap=snapshot)
        px, py = el.center_x, el.center_y
        label = f'{el.id} "{el.label}"'
    elif x is not None and y is not None:
        px, py = x, y
    else:
        raise click.UsageError("Provide --on <element> or -x/-y coordinates")

    button = "right" if right else ("middle" if middle else "left")
    count = 2 if double else 1
    inp.mouse_click(px, py, button=button, count=count)

    verb = (
        "Double-clicked"
        if double
        else ("Right-clicked" if right else ("Middle-clicked" if middle else "Clicked"))
    )
    target = label if label else f"({px}, {py})"

    emit(
        {"action": "click", "x": px, "y": py, "label": label, "ok": True},
        json=use_json,
        human_lines=f"{verb} {target} at ({px}, {py})",
    )
