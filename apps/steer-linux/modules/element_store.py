"""Snapshot save/load/resolve — port of ElementStore.swift."""

import json
import os
from pathlib import Path

from modules.errors import ElementNotFound, NoSnapshot
from modules.models import UIElement

STORE_DIR = Path("/tmp/steer")

_cache: dict[str, list[UIElement]] = {}


def _ensure_dir() -> None:
    STORE_DIR.mkdir(parents=True, exist_ok=True)


def _serialize(elements: list[UIElement]) -> str:
    return json.dumps([e.to_dict() for e in elements], indent=2)


def _deserialize(data: str) -> list[UIElement]:
    raw = json.loads(data)
    return [
        UIElement(
            id=e["id"],
            role=e["role"],
            label=e["label"],
            x=e["x"],
            y=e["y"],
            width=e["width"],
            height=e["height"],
            is_enabled=e.get("isEnabled", True),
            depth=e.get("depth", 0),
            value=e.get("value"),
        )
        for e in raw
    ]


def save(snap_id: str, elements: list[UIElement]) -> None:
    """Save elements to cache and disk."""
    _cache[snap_id] = elements
    _ensure_dir()
    path = STORE_DIR / f"{snap_id}.json"
    path.write_text(_serialize(elements))


def load(snap_id: str) -> list[UIElement] | None:
    """Load elements from cache or disk."""
    if snap_id in _cache:
        return _cache[snap_id]
    path = STORE_DIR / f"{snap_id}.json"
    if not path.exists():
        return None
    elements = _deserialize(path.read_text())
    _cache[snap_id] = elements
    return elements


def latest() -> tuple[str, list[UIElement]] | None:
    """Get the most recently modified snapshot."""
    # Check cache first
    if _cache:
        last_key = max(_cache.keys())
        return (last_key, _cache[last_key])
    # Fall back to disk
    if not STORE_DIR.exists():
        return None
    files = sorted(
        STORE_DIR.glob("*.json"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    if not files:
        return None
    newest = files[0]
    snap_id = newest.stem
    elements = _deserialize(newest.read_text())
    _cache[snap_id] = elements
    return (snap_id, elements)


def resolve(query: str, snap: str | None = None) -> UIElement:
    """Resolve an element by ID, exact label, or partial label match."""
    if snap:
        els = load(snap)
    else:
        pair = latest()
        els = pair[1] if pair else None
    if els is None:
        raise NoSnapshot()

    lq = query.lower()
    # Exact ID match: B1, T2, S3
    for e in els:
        if e.id.lower() == lq:
            return e
    # Exact label match
    for e in els:
        if e.label.lower() == lq:
            return e
    # Partial label match
    for e in els:
        if lq in e.label.lower():
            return e

    raise ElementNotFound(query)
