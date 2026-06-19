#!/usr/bin/env python3
"""
scripts/resolve.py
-------------------
Pure resolution layer. Turns role IDs into people and contact channels by
walking roles/registry.yaml -> people/directory.yaml. No side effects, no
network — so it's trivially testable and runs in CI as a validator.

Usage:
    python scripts/resolve.py validate              # check referential integrity
    python scripts/resolve.py notify-list red       # who gets paged at a tier
    python scripts/resolve.py whois beredskapsleder  # resolve one role
"""
from __future__ import annotations
import sys
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROLES = yaml.safe_load((ROOT / "roles" / "registry.yaml").read_text())
PEOPLE = yaml.safe_load((ROOT / "people" / "directory.yaml").read_text())["people"]


def resolve_role(role_id: str) -> dict:
    """Return {role, label, holder: person, deputy: person|None}."""
    role = ROLES["roles"].get(role_id)
    if role is None:
        raise KeyError(f"unknown role: {role_id}")
    holder = PEOPLE.get(role["holder"])
    if holder is None:
        raise KeyError(f"role '{role_id}' holder '{role['holder']}' not in directory")
    deputy = PEOPLE.get(role["deputy"]) if role.get("deputy") else None
    return {
        "role": role_id,
        "label": role.get("label", role_id),
        "holder": {"id": role["holder"], **holder},
        "deputy": ({"id": role["deputy"], **deputy} if deputy else None),
    }


def expand_targets(targets: list[str]) -> list[str]:
    """Expand a notifies[] list (roles + groups) into a flat list of role IDs."""
    out: list[str] = []
    for t in targets:
        if t in ROLES.get("groups", {}):
            out.extend(ROLES["groups"][t].get("members", []))
        else:
            out.append(t)
    # de-dupe, preserve order
    seen, flat = set(), []
    for r in out:
        if r not in seen:
            seen.add(r)
            flat.append(r)
    return flat


def validate() -> int:
    """Referential integrity: every holder/deputy exists; every group member is a role."""
    errors = []
    for rid, role in ROLES["roles"].items():
        for slot in ("holder", "deputy"):
            who = role.get(slot)
            if who and who not in PEOPLE:
                errors.append(f"role '{rid}'.{slot} -> unknown person '{who}'")
        if not role.get("deputy"):
            errors.append(f"role '{rid}' has no deputy (warn)")
    for gid, group in ROLES.get("groups", {}).items():
        for m in group.get("members", []):
            if m not in ROLES["roles"]:
                errors.append(f"group '{gid}' member -> unknown role '{m}'")
    for pid, p in PEOPLE.items():
        if p.get("slack", "").startswith("U_REPLACE"):
            errors.append(f"person '{pid}' has placeholder Slack ID (warn)")
    fatal = [e for e in errors if "(warn)" not in e]
    for e in errors:
        print(("FATAL " if "(warn)" not in e else "warn  ") + e, file=sys.stderr)
    return 1 if fatal else 0


def _load_plan(plan_id: str = "bod-altinn3") -> dict:
    return yaml.safe_load((ROOT / "plans" / plan_id / "plan.yaml").read_text())


def notify_list(level: str, plan_id: str = "bod-altinn3") -> list[dict]:
    plan = _load_plan(plan_id)
    targets = plan["escalation"][level].get("notifies", [])
    return [resolve_role(r) for r in expand_targets(targets)]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "validate":
        sys.exit(validate())
    elif cmd == "whois":
        import json
        print(json.dumps(resolve_role(sys.argv[2]), indent=2, ensure_ascii=False))
    elif cmd == "notify-list":
        for p in notify_list(sys.argv[2]):
            d = p["deputy"]["name"] if p["deputy"] else "—"
            print(f"{p['label']:40} {p['holder']['name']:24} (dep: {d})")
    else:
        print(__doc__)
        sys.exit(2)
