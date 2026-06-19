#!/usr/bin/env python3
"""
scripts/notify_slack.py
-----------------------
Thin Slack sender. Reads build/slack.json (produced by activate.py) and:
  - posts the coordination message to the incident channel
  - opens a DM with each paged person and sends their page

Stdlib-only (urllib) so it needs no extra install in Actions. Reads:
  SLACK_BOT_TOKEN     — xoxb-... bot token with chat:write, im:write
  SLACK_INCIDENT_CHANNEL — channel ID (Cxxxx) for the coordination thread

Phone fallback is intentionally NOT automated here: paging a phone is a
side-effectful action with cost/escalation semantics. The page DM includes the
phone number so a human can escalate to a call deliberately. Wire an SMS/voice
provider later behind an explicit `--phone-escalation` flag if desired.
"""
import sys, json, os, urllib.request, urllib.error

API = "https://slack.com/api/"
TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
CHANNEL = os.environ.get("SLACK_INCIDENT_CHANNEL", "")


def call(method: str, payload: dict) -> dict:
    req = urllib.request.Request(
        API + method,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"http {e.code}"}
    if not out.get("ok"):
        print(f"  ! {method} failed: {out.get('error')}", file=sys.stderr)
    return out


def main(path: str):
    data = json.loads(open(path).read())
    if not TOKEN:
        print("DRY: no SLACK_BOT_TOKEN — would post:", file=sys.stderr)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # 1) coordination message to the incident channel
    msg = data["channel_message"]
    res = call("chat.postMessage", {"channel": CHANNEL, **msg})
    thread_ts = res.get("ts")
    print(f"channel post: ok={res.get('ok')} ts={thread_ts}")

    # 2) direct pages
    for page in data["direct_pages"]:
        sid = page.get("slack_id", "")
        if not sid or sid.startswith("U_REPLACE"):
            print(f"  skip page for {page['name']} (no Slack ID)")
            continue
        opened = call("conversations.open", {"users": sid})
        dm = opened.get("channel", {}).get("id")
        if dm:
            call("chat.postMessage", {"channel": dm, "text": page["text"]})
            print(f"  paged {page['name']} (phone on file: {page.get('phone','—')})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "build/slack.json")
