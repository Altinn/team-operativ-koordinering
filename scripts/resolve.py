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
import json
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


def _step_vocab() -> tuple[set, set, set]:
    """Controlled vocabularies live in schema/step.schema.json (single source of
    truth). Read them here so the data and the validator can never disagree."""
    schema = json.loads((ROOT / "schema" / "step.schema.json").read_text())
    d = schema["$defs"]
    return (set(d["gate"]["enum"]), set(d["risk"]["enum"]), set(d["automation"]["enum"]))


def validate_steps(errors: list[str]) -> None:
    """Each wizard step uses allowed gate/risk/automation values and obeys the
    governance rules: high-risk may never be 'auto'; a decision-gated step must
    be 'narrate' (the call is the human's, the machine only narrates + records)."""
    gates, risks, autos = _step_vocab()
    for plan_dir in sorted((ROOT / "plans").iterdir()):
        steps_dir = plan_dir / "steps"
        if not steps_dir.is_dir():
            continue
        for sf in sorted(steps_dir.glob("*.yaml")):
            pb = yaml.safe_load(sf.read_text()) or {}
            rel = f"{plan_dir.name}/steps/{sf.name}"
            for s in pb.get("steps", []):
                sid = s.get("id", "?")
                for field, vocab in (("gate", gates), ("risk", risks), ("automation", autos)):
                    val = s.get(field)
                    if val is None:
                        errors.append(f"step '{rel}:{sid}' missing '{field}'")
                    elif val not in vocab:
                        errors.append(f"step '{rel}:{sid}' {field}='{val}' not in {sorted(vocab)}")
                if s.get("risk") == "high" and s.get("automation") == "auto":
                    errors.append(f"step '{rel}:{sid}' is high-risk and cannot be automation='auto'")
                if s.get("gate") == "decision" and s.get("automation") not in (None, "narrate"):
                    errors.append(f"step '{rel}:{sid}' is decision-gated and must be automation='narrate'")
                owner = s.get("owner_role")
                if owner and owner not in ROLES["roles"]:
                    errors.append(f"step '{rel}:{sid}' owner_role -> unknown role '{owner}'")


def validate() -> int:
    """Referential integrity: every holder/deputy exists; every group member is a
    role; every wizard step is well-formed and obeys the governance rules."""
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
    validate_steps(errors)
    fatal = [e for e in errors if "(warn)" not in e]
    for e in errors:
        print(("FATAL " if "(warn)" not in e else "warn  ") + e, file=sys.stderr)
    return 1 if fatal else 0


def _load_plan(plan_id: str = "bod-altinn3") -> dict:
    return yaml.safe_load((ROOT / "plans" / plan_id / "plan.yaml").read_text())


def notify_list(level: str, plan_id: str = "bod-altinn3",
                category: str | None = None) -> list[dict]:
    """Roles paged at a tier. A category (e.g. 'sikkerhet') folds in its
    `notify_always` roles, so a *yellow* security incident still pages security."""
    plan = _load_plan(plan_id)
    targets = list(plan["escalation"][level].get("notifies", []))
    if category:
        cat = plan.get("incident_categories", {}).get(category, {})
        targets += cat.get("notify_always", [])
    return [resolve_role(r) for r in expand_targets(targets)]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "validate":
        sys.exit(validate())
    elif cmd == "whois":
        print(json.dumps(resolve_role(sys.argv[2]), indent=2, ensure_ascii=False))
    elif cmd == "notify-list":
        category = sys.argv[3] if len(sys.argv) > 3 else None
        for p in notify_list(sys.argv[2], category=category):
            d = p["deputy"]["name"] if p["deputy"] else "—"
            print(f"{p['label']:40} {p['holder']['name']:24} (dep: {d})")
    else:
        print(__doc__)
        sys.exit(2)
