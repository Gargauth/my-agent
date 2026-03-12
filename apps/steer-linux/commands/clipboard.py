"""Clipboard read/write."""

import click

from modules import clipboard_ctl
from modules.output import emit


@click.command()
@click.argument("action")
@click.argument("text", required=False)
@click.option("--type", "content_type", default="text", help="Content type: text | image")
@click.option("--file", "file_path", help="File path for image read/write")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
def clipboard(
    action: str,
    text: str | None,
    content_type: str,
    file_path: str | None,
    use_json: bool,
) -> None:
    """Read or write the system clipboard."""
    action = action.lower()
    content_type = content_type.lower()

    if action == "read":
        if content_type == "text":
            content = clipboard_ctl.read_text()
            if use_json:
                emit(
                    {"action": "read", "type": "text", "content": content or "", "ok": True},
                    json=True,
                    human_lines="",
                )
            else:
                click.echo(content or "(clipboard empty)")
        elif content_type == "image":
            path = clipboard_ctl.read_image(save_to=file_path)
            emit(
                {"action": "read", "type": "image", "file": path, "ok": True},
                json=use_json,
                human_lines=f"Saved clipboard image to {path}",
            )
        else:
            raise click.UsageError("Type must be: text, image")

    elif action == "write":
        if content_type == "text":
            if not text:
                raise click.UsageError("Provide text to write")
            clipboard_ctl.write_text(text)
            preview = text[:80] + ("..." if len(text) > 80 else "")
            emit(
                {"action": "write", "type": "text", "content": text, "ok": True},
                json=use_json,
                human_lines=f'Copied to clipboard: "{preview}"',
            )
        elif content_type == "image":
            if not file_path:
                raise click.UsageError("Provide --file path for image write")
            clipboard_ctl.write_image(file_path)
            emit(
                {"action": "write", "type": "image", "file": file_path, "ok": True},
                json=use_json,
                human_lines=f"Copied image to clipboard from {file_path}",
            )
        else:
            raise click.UsageError("Type must be: text, image")

    else:
        raise click.UsageError("Action must be: read, write")
