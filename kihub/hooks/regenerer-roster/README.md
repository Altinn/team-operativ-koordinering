# hook: regenerer-roster

Holder `people/ROSTER.generated.md` i synk med kilden automatisk.

- **Hendelse:** `PostToolUse` på `Edit|Write|MultiEdit`.
- **Gjør:** hvis en YAML-fil under `roles/` eller `people/` ble endret, kjør
  `scripts/generate_roster.py`. Ellers ingenting.
- **Hvorfor:** den genererte oversikten kan da aldri drive fra dataene — du
  redigerer kilden, dokumentet følger etter av seg selv.

## Installering

Slå sammen `hooks.json` inn i prosjektets `.claude/settings.json` (eller
installer via KI Hub). Hooken bruker `$CLAUDE_PROJECT_DIR` og trenger ingen
konfig utover det.
