#!/usr/bin/env python3
"""
PostToolUse hook — validate the registry after a relevant edit.

Fires after Edit/Write/MultiEdit. If the touched file is under roles/, people/,
plans/ or scripts/, it runs `scripts/resolve.py validate`. On failure it exits 2
with the validator's errors on stderr, so the problem is surfaced immediately
(same gate as CI) rather than discovered in a failing PR. Warnings don't block.
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
relevant = any(
    seg in path or path.startswith(seg.strip("/") + "/")
    for seg in ("/roles/", "/people/", "/plans/", "/scripts/")
)
if not relevant:
    sys.exit(0)

root = pathlib.Path(__file__).resolve().parents[3]
res = subprocess.run(
    [sys.executable, str(root / "scripts" / "resolve.py"), "validate"],
    capture_output=True, text=True,
)
if res.returncode != 0:
    print("Beredskap-validering feilet — fiks før du går videre:\n"
          + (res.stderr or res.stdout), file=sys.stderr)
    sys.exit(2)
sys.exit(0)
