# Handoff til Claude Code

Dette repoet er et v1-scaffold for "beredskap som kode" – kontinuitetsplaner i
Git som aktiveres på knapp eller hendelse, varsler via Slack, kjører en veiviser
og logger alt i en GitHub-sak. Les `docs/DESIGN.md` for hele arkitekturen og
begrunnelsene. Dette dokumentet sier bare hvor v1 stoppet og hva som gjenstår.

## Status: hva er gjort og verifisert

- Rolleindireksjon: `roles/registry.yaml` + `people/directory.yaml`. Planer
  navngir roller, aldri personer.
- Plan `plans/bod-altinn3/` i både maskinform (`plan.yaml`) og prosa (`plan.md`).
- Veivisere `steps/red.yaml` og `steps/yellow.yaml` med gatede steg
  (info/ack/action/decision). `decision` går aldri videre automatisk.
- Skript (kun pyyaml): `resolve.py` (oppslag+validator), `activate.py`
  (rendrer sak+Slack, dry-run-bar), `notify_slack.py` (sender).
- Actions: `activate.yml` (knapp+hendelse) og `validate.yml` (PR-integritet).
- `python scripts/resolve.py validate` passerer. Begge veivisere rendrer.
  Slack-sending er dry-run-testet uten token.

## Oppgaver, i rekkefølge

### 1. Sett i drift (v1.1) – gjør dette først
> Alle navn, e-poster, telefonnumre og person-ID-er er placeholdere
> (`person.a`…`person.f`, `duty.desk`). Erstatt med ekte verdier. Person-ID-ene
> må holdes i synk mellom `people/directory.yaml` og `roles/registry.yaml`
> (holder/deputy må matche nøklene), ellers feiler valideringen.
- [ ] Erstatt placeholder-person-ID-er, navn, e-poster og telefonnumre i
      `people/directory.yaml` med ekte verdier, og oppdater de samme ID-ene i
      `roles/registry.yaml`.
- [ ] Finn ekte Slack medlems-ID-er, erstatt alle `U_REPLACE_ME` i
      `people/directory.yaml`. Kjør `python scripts/resolve.py validate` –
      placeholder-advarslene skal forsvinne.
- [ ] Opprett Slack-app, scopes `chat:write` + `im:write`, installer, hent
      `xoxb-`-token.
- [ ] Sett repo-secrets `SLACK_BOT_TOKEN` og `SLACK_INCIDENT_CHANNEL`.
- [ ] Erstatt `@digdir/bod-beredskap` i `.github/CODEOWNERS` med ekte team.
- [ ] Røyktest: Actions → "Aktiver kontinuitetsplan" → level: yellow → Run.
      Bekreft at sak opprettes med korrekt veiviser og at Slack-melding kommer.

### 2. Toveis synk (v1.2) – den høyest verdsatte neste biten
Akkurat nå rendres veiviseren til både sak og Slack, men avhukinger lever bare
i saken. Under reelt press vil folk huke av fra Slack. Bygg en liten mottaker
for Slack Events API som speiler reaksjoner/knappetrykk tilbake til
sakens checkboxer. Vurder en `block_actions`-payload med Slack-knapper per steg
framfor fritekst-reaksjoner. Dette er forskjellen på "fint scaffold" og "brukes
faktisk under en hendelse".

### 3. Gjenstående fra veikartet (se DESIGN.md §9)
- [ ] v2: slash-kommando-proxy så vakthavende kan aktivere uten GitHub-tilgang.
- [ ] v2: `repository_dispatch` fra Statuspage/Azure Monitor for auto-aktivering.
- [ ] v2.1: autoevaluering – regn RTO/RPO-etterlevelse fra sakens tidsstempler.

## To avstemminger før dette hardner (DESIGN.md §10)
1. Bekreft at det ikke finnes et konkurrerende rolleregister i bruk allerede.
2. Avklar de tre åpne spørsmålene i DESIGN.md §10.

## Vær varsom her
Dette er beredskap. Hold automatikken til varsling, koordinering og logging.
IKKE automatiser tilstandsoverganger (erklære rødt, normalisere) – de er
bevisst `decision`-gatet og reservert for avdelingsdirektør/beredskapsleder.
