"""Search elements in snapshot."""

import click

from modules import element_store
from modules.output import emit


@click.command("find")
@click.argument("query")
@click.option("--snapshot", help="Snapshot ID to search in")
@click.option("--exact", is_flag=True, help="Exact match only")
@click.option("--json", "use_json", is_flag=True, help="Output JSON")
def find_cmd(query: str, snapshot: str | None, exact: bool, use_json: bool) -> None:
    """Search elements by text in the latest snapshot."""
    if snapshot:
        els = element_store.load(snapshot)
        snap_id = snapshot
    else:
        pair = element_store.latest()
        if pair is None:
            from modules.errors import NoSnapshot

            raise NoSnapshot()
        snap_id, els = pair

    if els is None:
        from modules.errors import NoSnapshot

        raise NoSnapshot()

    lq = query.lower()
    if exact:
        matches = [
            e
            for e in els
            if e.label.lower() == lq or (e.value and e.value.lower() == lq)
        ]
    else:
        matches = [
            e
            for e in els
            if lq in e.label.lower() or (e.value and lq in e.value.lower())
        ]

    if use_json:
        emit(
            {
                "snapshot": snap_id,
                "query": query,
                "count": len(matches),
                "matches": [e.to_dict() for e in matches],
            },
            json=True,
            human_lines="",
        )
    else:
        lines = [
            f"snapshot: {snap_id}",
            f'query: "{query}"',
            f"matches: {len(matches)}",
            "",
        ]
        if not matches:
            lines.append("  (no matches)")
        else:
            for el in matches:
                lbl = el.label if el.label else (el.value or "")
                t = lbl[:50]
                lines.append(
                    f"  {el.id:<6} {el.role:<14} "
                    f'"{t}"  ({el.x},{el.y} {el.width}x{el.height})'
                )
        emit({}, json=False, human_lines=lines)
