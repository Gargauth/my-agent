"""Type text into focused element."""

import time

import click

from modules import element_store, input as inp
from modules.output import emit


@click.command("type")
@click.argument("text")
@click.option("--into", help="Target element ID or label — clicks to focus first")
@click.option("--snapshot", help="Snapshot ID")
@click.option("--clear", is_flag=True, help="Clear field first (Ctrl+A, Delete)")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
def type_cmd(
    text: str,
    into: str | None,
    snapshot: str | None,
    clear: bool,
    use_json: bool,
) -> None:
    """Type text into the focused element, or click a target first."""
    if into:
        el = element_store.resolve(into, snap=snapshot)
        inp.mouse_click(el.center_x, el.center_y)
        time.sleep(0.1)
    if clear:
        inp.hotkey("ctrl+a")
        time.sleep(0.05)
        inp.hotkey("delete")
        time.sleep(0.05)
    inp.type_text(text)

    emit(
        {"action": "type", "text": text, "ok": True},
        json=use_json,
        human_lines=f'Typed "{text}"' + (f" into {into}" if into else ""),
    )
