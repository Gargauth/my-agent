"""Press key combinations."""

import click

from modules import input as inp
from modules.output import emit


@click.command()
@click.argument("combo")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
def hotkey(combo: str, use_json: bool) -> None:
    """Press a key combination: super+s, ctrl+c, return, escape, tab, etc."""
    inp.hotkey(combo)
    emit(
        {"action": "hotkey", "combo": combo, "ok": True},
        json=use_json,
        human_lines=f"Pressed {combo}",
    )
