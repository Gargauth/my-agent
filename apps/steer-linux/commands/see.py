"""Screenshot + accessibility tree."""

import uuid
from pathlib import Path

import click

from backends.base import CompositorBackend
from modules import accessibility, element_store, ocr_engine
from modules.output import emit


@click.command()
@click.option("--app", "app_name", help="Target app name (default: frontmost)")
@click.option("--screen", type=int, help="Screen index to capture")
@click.option("--ocr", "use_ocr", is_flag=True, help="Run OCR when accessibility tree is empty")
@click.option("--role", help="Filter elements by role")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
@click.pass_obj
def see(
    backend: CompositorBackend,
    app_name: str | None,
    screen: int | None,
    use_ocr: bool,
    role: str | None,
    use_json: bool,
) -> None:
    """Capture screenshot + accessibility tree. Returns element map."""
    snap_id = str(uuid.uuid4())[:8]
    store_dir = element_store.STORE_DIR
    store_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = str(store_dir / f"{snap_id}.png")
    elements = []
    target_name = ""

    if screen is not None and app_name is None:
        # Full screen capture
        backend.capture_screen(screen, screenshot_path)
        target_name = f"screen-{screen}"
    else:
        # App capture
        if app_name:
            windows = backend.list_windows(app_name)
            if not windows:
                from modules.errors import AppNotFound

                raise AppNotFound(app_name)
            win = windows[0]
            target_name = app_name
            backend.capture_window(win.address, screenshot_path)
            # Walk accessibility tree
            if win.pid:
                elements = accessibility.walk(win.pid)
        else:
            active = backend.active_window()
            if active:
                target_name = active.title or active.app
                backend.capture_window(active.address, screenshot_path)
                if active.pid:
                    elements = accessibility.walk(active.pid)
            else:
                # Fallback: capture first screen
                backend.capture_screen(0, screenshot_path)
                target_name = "desktop"

        if not elements and use_ocr:
            ocr_results = ocr_engine.recognize(screenshot_path)
            elements = ocr_engine.to_elements(ocr_results)

    if elements:
        element_store.save(snap_id, elements)

    displayed = elements
    if role:
        displayed = [e for e in elements if role.lower() in e.role.lower()]

    windows_data = []
    if app_name:
        wins = backend.list_windows(app_name)
        windows_data = [w.to_dict() for w in wins]

    if use_json:
        emit(
            {
                "snapshot": snap_id,
                "app": target_name,
                "screenshot": screenshot_path,
                "count": len(displayed),
                "windows": windows_data,
                "elements": [e.to_dict() for e in displayed],
            },
            json=True,
            human_lines="",
        )
    else:
        lines = [
            f"snapshot: {snap_id}",
            f"app: {target_name}",
            f"screenshot: {screenshot_path}",
            f"elements: {len(displayed)}"
            + (f" (filtered by {role})" if role else ""),
        ]
        if not displayed and screen is not None:
            lines.append("  (full screen capture -- no element tree)")
        elif not displayed:
            lines.append("  (no interactive elements found)")
        else:
            for el in displayed:
                lbl = el.label if el.label else (el.value or "")
                t = lbl[:40]
                lines.append(
                    f"  {el.id:<6} {el.role:<14} "
                    f'"{t}"  ({el.x},{el.y} {el.width}x{el.height})'
                )
        emit({}, json=False, human_lines=lines)
