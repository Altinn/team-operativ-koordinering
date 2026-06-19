#!/usr/bin/env python3
"""
scripts/activate.py
-------------------
The activator. Given a plan, a level, and an incident context, it:
  1. resolves the notify list and the playbook owners,
  2. renders the incident Issue body (the wizard + hendelseslogg), and
  3. renders Slack message blocks (paging DMs + the mirrored thread).

It does NOT decide anything and it does NOT send anything itself — it emits
artifacts that the GitHub Action posts. Keeping send-effects out of here makes
it dry-runnable: `python scripts/activate.py red --dry-run` prints everything.

This is deliberately dependency-light (pyyaml only) so it runs in Actions
without a build step.
"""
from __future__ import annotations
import sys
import json
import argparse
import datetime as dt
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from resolve import resolve_role, notify_list, _load_plan, expand_targets  # noqa: E402


def load_playbook(plan_id: str, level: str) -> dict:
    plan = _load_plan(plan_id)
    rel = plan["escalation"][level].get("playbook")
    if not rel:
        return {"playbook": level, "title": level, "steps": []}
    return yaml.safe_load((ROOT / "plans" / plan_id / rel).read_text())


def render_issue_body(plan_id: str, level: str, ctx: dict) -> str:
    plan = _load_plan(plan_id)
    esc = plan["escalation"][level]
    pb = load_playbook(plan_id, level)
    now = ctx["activated_at"]

    lines = []
    lines.append(f"## {esc['label']} — {plan['meta']['title']}")
    lines.append("")
    lines.append(f"- **Aktivert:** {now}")
    lines.append(f"- **Aktivert av:** {ctx.get('activated_by','—')}")
    lines.append(f"- **Kategori:** {ctx.get('category','(settes i steg 1)')}")
    lines.append(f"- **Berørte funksjoner:** {ctx.get('affected','(settes i steg 1)')}")
    lines.append(f"- **Plan-versjon:** {plan['meta']['version']}")
    lines.append("")

    # RTO/RPO clocks for affected (or all critical) functions
    lines.append("### ⏱️ RTO/RPO — frister")
    lines.append("| Funksjon | Prioritet | RTO | RPO | Frist (RTO) |")
    lines.append("|---|---|---|---|---|")
    t0 = dt.datetime.fromisoformat(now)
    for f in plan["functions"]:
        rto = f.get("rto_hours")
        rpo = ("0" if f.get("rpo") == "zero"
               else f"<{f['rpo_minutes']}min" if f.get("rpo_minutes")
               else f"<{f['rpo_hours']}t" if f.get("rpo_hours") else "—")
        deadline = (t0 + dt.timedelta(hours=rto)).strftime("%H:%M") if rto is not None else "—"
        lines.append(f"| {f['label']} | {f['priority']} | {rto}t | {rpo} | {deadline} |")
    lines.append("")

    # The wizard
    lines.append("### ✅ Tiltaksveiviser")
    lines.append("_Hak av når steget er utført. `decision`-steg krever navngitt person + begrunnelse i tråden._")
    lines.append("")
    for s in pb["steps"]:
        owner = resolve_role(s["owner_role"])
        badge = {"decision": "🟥 BESLUTNING", "action": "🔧 handling",
                 "ack": "👍 bekreft", "info": "ℹ️ info"}.get(s["gate"], s["gate"])
        when = f" _(kun hvis: {s['when']})_" if s.get("when") else ""
        dep = f" ⟂ etter `{', '.join(s['blocks_on'])}`" if s.get("blocks_on") else ""
        lines.append(f"- [ ] **[{badge}]** ({owner['label']} → {owner['holder']['name']}) "
                     f"{s['text'].strip()}{when}{dep}")
    lines.append("")

    # SPOFs surfaced
    spofs = [d for d in plan.get("dependencies", []) if d.get("spof")]
    if spofs:
        lines.append("### ⚠️ Kjente enkeltpunkt for feil (SPOF)")
        for d in spofs:
            lines.append(f"- **{d['function']}** — {d['depends_on']} · _avbøtende:_ {d['mitigation']}")
        lines.append("")

    lines.append("### 🧾 Hendelseslogg")
    lines.append("_Alle kommentarer under er tidsstemplet og utgjør den formelle loggen "
                 "(jf. kap. 7 normalisering, kap. 9 endringslogg)._")
    return "\n".join(lines)


def render_slack_blocks(plan_id: str, level: str, ctx: dict, issue_url: str = "") -> dict:
    plan = _load_plan(plan_id)
    esc = plan["escalation"][level]
    targets = notify_list(level, plan_id)
    mentions = " ".join(
        f"<@{resolve_role.__globals__['PEOPLE'][t['holder']['id']].get('slack','')}>"
        for t in targets
    )
    header = f"{esc['label']} aktivert — {plan['meta']['title']}"
    body = (f"*Aktivert:* {ctx['activated_at']}  |  *av:* {ctx.get('activated_by','—')}\n"
            f"*Veiviser/logg:* {issue_url or '(issue opprettes)'}\n"
            f"Paged: {mentions}")
    return {
        "channel_message": {
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": header}},
                {"type": "section", "text": {"type": "mrkdwn", "text": body}},
            ]
        },
        "direct_pages": [
            {"slack_id": resolve_role.__globals__["PEOPLE"][t["holder"]["id"]].get("slack", ""),
             "name": t["holder"]["name"],
             "phone": t["holder"].get("phone", ""),
             "text": f"{esc['label']} aktivert. Du er varslet som {t['label']}. Se {issue_url}"}
            for t in targets
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("level", choices=["yellow", "red"])
    ap.add_argument("--plan", default="bod-altinn3")
    ap.add_argument("--by", default="(workflow_dispatch)")
    ap.add_argument("--category", default="")
    ap.add_argument("--affected", default="")
    ap.add_argument("--issue-url", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    ctx = {
        "activated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "activated_by": a.by,
        "category": a.category,
        "affected": a.affected,
    }
    issue_body = render_issue_body(a.plan, a.level, ctx)
    slack = render_slack_blocks(a.plan, a.level, ctx, a.issue_url)

    if a.dry_run:
        print("=" * 70 + "\nISSUE BODY\n" + "=" * 70)
        print(issue_body)
        print("\n" + "=" * 70 + "\nSLACK\n" + "=" * 70)
        print(json.dumps(slack, indent=2, ensure_ascii=False))
    else:
        out = ROOT / "build"
        out.mkdir(exist_ok=True)
        (out / "issue_body.md").write_text(issue_body)
        (out / "slack.json").write_text(json.dumps(slack, ensure_ascii=False))
        print(str(out / "issue_body.md"))
        print(str(out / "slack.json"))


if __name__ == "__main__":
    main()
