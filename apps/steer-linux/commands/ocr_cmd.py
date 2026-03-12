"""OCR command — extract text from screenshots."""

import uuid

import click

from backends.base import CompositorBackend
from modules import element_store, ocr_engine
from modules.errors import CaptureFailure
from modules.output import emit


@click.command("ocr")
@click.option("--image", help="Path to a screenshot PNG (default: captures fresh)")
@click.option("--app", "app_name", help="Target app name (default: frontmost)")
@click.option("--screen", type=int, help="Screen index to capture")
@click.option("--confidence", type=float, default=0.5, help="Minimum confidence 0.0-1.0")
@click.option("--store", "do_store", is_flag=True, help="Save results as snapshot for click --on")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
@click.pass_obj
def ocr_cmd(
    backend: CompositorBackend,
    image: str | None,
    app_name: str | None,
    screen: int | None,
    confidence: float,
    do_store: bool,
    use_json: bool,
) -> None:
    """Extract text from a screenshot via OCR."""
    target_name = ""
    image_path = image

    if image_path:
        from pathlib import Path

        target_name = Path(image_path).stem
    elif screen is not None and app_name is None:
        snap_id = str(uuid.uuid4())[:8]
        store_dir = element_store.STORE_DIR
        store_dir.mkdir(parents=True, exist_ok=True)
        image_path = str(store_dir / f"{snap_id}.png")
        backend.capture_screen(screen, image_path)
        target_name = f"screen-{screen}"
    else:
        if app_name:
            windows = backend.list_windows(app_name)
            if not windows:
                from modules.errors import AppNotFound

                raise AppNotFound(app_name)
            win = windows[0]
            target_name = app_name
        else:
            active = backend.active_window()
            if not active:
                raise CaptureFailure("No active window")
            win = active  # type: ignore[assignment]
            target_name = win.title or win.app  # type: ignore[union-attr]

        snap_id = str(uuid.uuid4())[:8]
        store_dir = element_store.STORE_DIR
        store_dir.mkdir(parents=True, exist_ok=True)
        image_path = str(store_dir / f"{snap_id}.png")
        backend.capture_window(win.address, image_path)  # type: ignore[union-attr]

    results = ocr_engine.recognize(image_path, min_confidence=confidence)

    saved_snap = None
    if do_store:
        saved_snap = str(uuid.uuid4())[:8]
        store_dir = element_store.STORE_DIR
        store_dir.mkdir(parents=True, exist_ok=True)
        element_store.save(saved_snap, ocr_engine.to_elements(results))

    if use_json:
        data: dict = {
            "app": target_name,
            "count": len(results),
            "results": [r.to_dict() for r in results],
        }
        if saved_snap:
            data["snapshot"] = saved_snap
        emit(data, json=True, human_lines="")
    else:
        lines = [
            f"app: {target_name}",
            f"text regions: {len(results)}",
        ]
        if saved_snap:
            lines.append(f"snapshot: {saved_snap}")
        lines.append("")
        for r in results:
            t = r.text[:60]
            lines.append(
                f'  "{t}"  ({r.x},{r.y} {r.width}x{r.height})  conf:{r.confidence:.2f}'
            )
        emit({}, json=False, human_lines=lines)
