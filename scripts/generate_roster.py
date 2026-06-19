#!/usr/bin/env python3
"""
scripts/generate_roster.py
--------------------------
Generates people/ROSTER.generated.md from roles/registry.yaml +
people/directory.yaml — a *projection* of the source data, never edited by hand.

This is the concrete proof of the "one source of truth, doc is generated"
principle: edit the YAML, re-run this (a hook does it automatically), and the
human-readable roster can never drift from the data.

    python scripts/generate_roster.py           # (re)write the roster
    python scripts/generate_roster.py --check    # CI: fail if it's stale
"""
from __future__ import annotations
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from resolve import ROLES, resolve_role  # noqa: E402

OUT = ROOT / "people" / "ROSTER.generated.md"


def render() -> str:
    lines = [
        "<!-- GENERERT FIL — IKKE REDIGER FOR HÅND. -->",
        "<!-- Kilde: roles/registry.yaml + people/directory.yaml -->",
        "<!-- Regenerer: python scripts/generate_roster.py -->",
        "",
        "# Rolleoversikt (generert)",
        "",
        "Hvem som holder hvilken rolle akkurat nå. Endre **kilden**, ikke denne",
        "fila — den blir overskrevet ved neste regenerering.",
        "",
        "| Rolle | Innehaver | Stedfortreder |",
        "|---|---|---|",
    ]
    for rid in ROLES["roles"]:
        r = resolve_role(rid)
        deputy = r["deputy"]["name"] if r["deputy"] else "—"
        lines.append(f"| {r['label']} | {r['holder']['name']} | {deputy} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    content = render()
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != content:
            print(f"STALE: {OUT.name} differs from source — "
                  f"run: python scripts/generate_roster.py", file=sys.stderr)
            return 1
        print(f"{OUT.name} up to date")
        return 0
    OUT.write_text(content, encoding="utf-8")
    print(str(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
