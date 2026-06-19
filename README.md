# beredskap-ops

Kontinuitetsplaner som kjørbar kode. Planer bor i Git som `.yaml` (maskin) og
`.md` (menneske); aktivering skjer på knapp eller hendelse og gir Slack-
varsling, en veiviser og en tidsstemplet logg – uten å automatisere
beslutninger som hører mennesket til.

> Les [`docs/DESIGN.md`](./docs/DESIGN.md) først. Den forklarer hvorfor det er
> bygget slik.

## Repokart

```
roles/registry.yaml          rolle  -> innehaver/stedfortreder   ← keystone, endres ved jobbytte
people/directory.yaml        person -> kontaktinfo (Internt)
plans/bod-altinn3/
  plan.yaml                  maskinlesbar plan (eskalering, BIA, avhengigheter)
  plan.md                    menneskelesbar prosa
  steps/red.yaml             veiviser, A-hendelse
  steps/yellow.yaml          veiviser, B-hendelse
scripts/
  resolve.py                 oppslag og validator (ingen sideeffekter)
  activate.py                rendrer sak og Slack (kan kjøres som dry-run)
  notify_slack.py            sender til Slack
.github/workflows/
  activate.yml               knapp og hendelse -> sak og Slack
  validate.yml               referanseintegritet på hver PR
incidents/                   (valgfritt) arkiverte logger
```

## Kom i gang

```bash
pip install pyyaml

# Sjekk at registeret henger sammen (gjøres også i CI)
python scripts/resolve.py validate

# Hvem varsles ved rødt?
python scripts/resolve.py notify-list red

# Se hele aktiveringen uten å sende noe
python scripts/activate.py red --category drift --affected autorisasjon --dry-run
```

## Sette i drift (v1.1)

1. Opprett en Slack-app med scopene `chat:write` og `im:write`; installer den i
   workspacet; hent bot-token (`xoxb-…`).
2. Finn medlems-ID-er (profil → ··· → Kopier medlems-ID) og fyll inn `slack:` i
   `people/directory.yaml` (erstatt `U_REPLACE_ME`).
3. Sett repo-secrets: `SLACK_BOT_TOKEN` og `SLACK_INCIDENT_CHANNEL` (kanal-ID).
4. Gjør repoet privat. Vurder `CODEOWNERS` på `roles/`.
5. Test: Actions-fanen → **Aktiver kontinuitetsplan** → `level: yellow` → Run.
   Bekreft at saken opprettes og at Slack-meldingen kommer.

## Designprinsipper (kort)

- **Rolleindireksjon:** planer navngir roller, aldri personer.
- **Mennesket i løkka:** `decision`-steg går aldri videre automatisk.
- **Saken er loggen:** veiviseren er hendelsesloggen, tidsstemplet og attribuert.
- **Alt kan dry-runnes:** ingen sideeffekt skjer uten at den kan forhåndsvises.
