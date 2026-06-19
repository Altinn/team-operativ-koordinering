#!/usr/bin/env python3
"""
PostToolUse hook — regenerate the generated roster when source data changes.

Fires after any Edit/Write/MultiEdit. If the touched file is YAML under roles/
or people/, it re-runs scripts/generate_roster.py so people/ROSTER.generated.md
stays in lockstep with the source. Stays silent (exit 0) otherwise.
"""
import json
import sys
import subprocess
import pathlib

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

path = (data.get("tool_input") or {}).get("file_path", "") or ""
touched_source = (
    ("/roles/" in path or "/people/" in path or path.startswith(("roles/", "people/")))
    and path.endswith((".yaml", ".yml"))
)
if not touched_source:
    sys.exit(0)

root = pathlib.Path(__file__).resolve().parents[3]
subprocess.run([sys.executable, str(root / "scripts" / "generate_roster.py")], check=False)
sys.exit(0)
