# Kontinuitetsplan – BOD (Altinn 3)

> **Dette er den menneskelesbare versjonen.** Maskinen leser [`plan.yaml`](./plan.yaml).
> De to skal holdes i synk gjennom review. En endring i den ene som ikke følges
> opp i den andre, fanges ikke automatisk. Det er et bevisst valg – prosa
> trenger nyanser YAML ikke har – men ha det i bakhodet ved revisjon.

- **Versjon:** 0.1 (utkast) · **Status:** draft
- **Plan-/innholdseier:** rollen `seksjonssjef_styring_stotte`
- **Godkjent av:** rollen `avdelingsdirektor`
- **Neste revisjon:** 2026-07-01 · **Klassifisering:** Internt
- **Referanse:** ISO 22301

## Slik kjøres planen

Planen er ikke et arkivdokument. Den aktiveres – med knapp eller hendelse – og
kjører som en veiviser der hvert steg har en ansvarlig **rolle**, ikke en
navngitt person. Rollen løses til riktig navn i det øyeblikket planen
aktiveres. Hele arkitekturen er beskrevet i [`../../docs/DESIGN.md`](../../docs/DESIGN.md).

## Aktivering og eskalering

| Nivå | Kriterium (kort) | Aktiveres av (rolle) | Veiviser |
|---|---|---|---|
| 🟢 Grønn | Normal drift | – | – |
| 🟡 Gul | B-hendelse: redusert eller ustabil tjeneste, eller bortfall med nødløsning | `incident_manager` | `steps/yellow.yaml` |
| 🔴 Rød | A-hendelse: bortfall av kritisk tjeneste uten nødløsning, sikkerhetsbrudd, omdømme | `avdelingsdirektor` | `steps/red.yaml` |

N�r rødt nivå aktiveres, utløses samtidig en *menneskelig* vurdering av om
Digdir kriseledelse skal etableres (jf. punkt 1.4 i originalplanen). Automatikken
tar ikke denne beslutningen – den løfter spørsmålet fram som et beslutningssteg
i veiviseren.

## Hendelseskategori (uavhengig akse fra alvorlighetsgrad)

Kategori (drift/sikkerhet) og alvorlighetsgrad (A/B/C) er to uavhengige akser.
Ved mistanke om et sikkerhetsaspekt klassifiseres hendelsen som
**sikkerhetshendelse** inntil det motsatte er avklart. Grunnen er at
sikkerhetsprosessen stiller krav til bevissikring som ikke lar seg gjenopprette
i etterkant. En sikkerhetshendelse varsler alltid `sikkerhetsansvarlig` og
starter en vurdering av 72-timersfristen til Datatilsynet ved brudd på
personopplysningssikkerheten.

## Kritiske funksjoner (BIA)

Den maskinlesbare utgaven ligger i `plan.yaml`. RTO/RPO brukes til å starte
nedtellingsklokker fra aktiveringstidspunktet, som vises i hendelsessaken.

| Funksjon | Prioritet | RTO | RPO |
|---|---|---|---|
| Plattform | Kritisk | 0,15 t | 0 |
| Autorisasjon | Kritisk | 0,5 t | 0 |
| Dialogporten | Kritisk | 4 t | < 15 min |
| Melding og Formidling | Kritisk | 4 t | < 15 min |
| Arbeidsflate / Altinn Studio | Høy | 8 t | < 1 t |
| Varsling / Servicedesk | Høy | 8 t | < 1 t |

## Roller

Ingen person er navngitt i planen. Roller løses via
[`../../roles/registry.yaml`](../../roles/registry.yaml). Når noen bytter jobb,
endres **én linje** der, og alle planer som peker på rollen blir umiddelbart
riktige. PR-en som gjør endringen, er sporet.

## Normalisering og logg

Hendelsessaken *er* hendelsesloggen: tidsstemplet, attribuert og uforanderlig
historikk. Tilbakeføring til normal drift er et beslutningssteg eid av
`beredskapsleder`, med forutsetningene fra kapittel 7 som konkrete
avhukingskrav.
