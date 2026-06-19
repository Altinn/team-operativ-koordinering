# hook: valider-beredskap

Fanger inkonsistente endringer i det øyeblikket de skjer, ikke i en feilende PR.

- **Hendelse:** `PostToolUse` på `Edit|Write|MultiEdit`.
- **Gjør:** hvis en fil under `roles/`, `people/`, `plans/` eller `scripts/` ble
  endret, kjør `scripts/resolve.py validate`. Ved `FATAL` (ukjent person, brutt
  styringsregel for et steg, ukjent rolle): blokker (exit 2) med feilmeldingen.
- **Hvorfor:** samme gate som CI, men lokalt og umiddelbart. Advarsler
  (placeholder-Slack-ID) blokkerer ikke.

## Installering

Slå sammen `hooks.json` inn i prosjektets `.claude/settings.json` (eller
installer via KI Hub).
