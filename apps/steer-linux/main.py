"""steer-linux — Linux GUI automation CLI for AI agents."""

import sys

import click

from backends.detect import detect_backend
from commands.apps import apps
from commands.click_cmd import click_cmd
from commands.clipboard import clipboard
from commands.drag import drag
from commands.find_cmd import find_cmd
from commands.focus import focus
from commands.hotkey import hotkey
from commands.ocr_cmd import ocr_cmd
from commands.scroll import scroll
from commands.screens import screens
from commands.see import see
from commands.type_cmd import type_cmd
from commands.wait import wait
from commands.window import window
from modules.errors import SteerError


@click.group()
@click.version_option("0.1.0", prog_name="steer-linux")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Linux GUI automation CLI for AI agents. Eyes and hands on your desktop."""
    ctx.ensure_object(dict)
    try:
        ctx.obj = detect_backend()
    except SteerError:
        # Allow --help to work without a compositor
        if "--help" in sys.argv or "-h" in sys.argv:
            ctx.obj = None
        else:
            raise


cli.add_command(see)
cli.add_command(click_cmd)
cli.add_command(type_cmd)
cli.add_command(hotkey)
cli.add_command(scroll)
cli.add_command(drag)
cli.add_command(apps)
cli.add_command(screens)
cli.add_command(window)
cli.add_command(ocr_cmd)
cli.add_command(focus)
cli.add_command(find_cmd)
cli.add_command(clipboard)
cli.add_command(wait)


if __name__ == "__main__":
    cli()
