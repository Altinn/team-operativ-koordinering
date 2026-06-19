# Beredskap som kode – designdokument

**Status:** utkast til review · **Forfatter:** (deg) · **Dato:** 2026-06-18
**Mål:** flytte kontinuitetsplaner fra arkivskuffen til Git som strukturerte
`.md`- og `.yaml`-filer, med Slack-varsling, veiviser og logg som kjører på
knapp eller hendelse.

---

## 1. Problemet

En kontinuitetsplan i Word har tre svakheter som slår inn akkurat når planen
trengs:

1. **Den er statisk.** Navn og telefonnumre forvitrer. Når noen slutter 30.06,
   er planen feil 01.07 – og ingen oppdager det før det står på.
2. **Den er passiv.** Den beskriver hva som *bør* skje, men gjør ingenting.
   Aktivering, varsling og logging blir manuelt arbeid lagt oppå en krise.
3. **Den lar seg ikke etterprøve.** Det finnes ingen tidsstemplet, attribuert
   logg over hva som faktisk ble gjort – noe både ISO 22301 og evalueringen i
   kapittel 8 forutsetter.

## 2. Kjerneinnsikt: plan som data vs. plan som kjøretid

Word-dokumentet blander sammen to ting som bør holdes adskilt:

- **Plan som data** – roller, terskler, RTO/RPO, avhengigheter,
  eskaleringsnivåer. Dette er YAML, og det er dette maskinen leser.
- **Plan som kjøretid** – hvem som varsles, hvilke veiviser-steg som utløses,
  hva som logges. Dette er en GitHub Action pluss Slack.

## 3. Nøkkelbeslutning: rolleindireksjon

Dette er den viktigste enkeltbeslutningen. Planen navngir **aldri** en person –
den navngir en *rolle* (`beredskapsleder`). Roller løses gjennom to filer:

```
roles/registry.yaml    rolle  -> innehaver + stedfortreder   (endres når folk bytter jobb)
people/directory.yaml  person -> navn/e-post/telefon/slack   (kontaktoppslag)
```

N�r noen slutter: endre **én linje** i `registry.yaml`. Alle planer som peker på
rollen, blir umiddelbart riktige. PR-en er revisjonssporet. CI hindrer at en
plan kan peke på en person som ikke finnes.

Hvorfor to filer? Roller endres sjelden og må reviewes nøye – det handler om
hvem som har myndighet. Kontaktdetaljer endres ofte og har lavere risiko. Ulik
endringstakt gir ulike filer.

> **Gjenbruk:** dette rolleregisteret er ikke beredskapsspesifikt. Det løser
> «hvem eier dette»-problemet.

## 4. Arkitektur

```
┌─ Kilde (Git) ─────────────────────────────┐
│  roles/registry.yaml   ← endres ved jobbytte
│  people/directory.yaml                     │
│  plans/*/plan.yaml + plan.md               │
│  plans/*/steps/*.yaml  (veivisere)         │
└──────────────┬─────────────────────────────┘
               │ workflow_dispatch (knapp) / repository_dispatch (hendelse)
        ┌──────▼───────┐
        │ GitHub Action│  validér → render → opprett sak → post til Slack
        └──────┬───────┘
       ┌───────┼───────────────┐
   ┌───▼──┐  ┌─▼────┐   ┌──────▼─────┐
   │Slack │  │ Sak  │   │ incidents/ │
   │varsel│  │veivis│   │   *.md     │
   │+tråd │  │+logg │   │ (arkiv)    │
   └──────┘  └──────┘   └────────────┘
```

### Komponenter

| Fil | Rolle |
|---|---|
| `scripts/resolve.py` | Ren oppslagslogikk og validator. Ingen sideeffekter, så den kan kjøres i CI. |
| `scripts/activate.py` | Rendrer sakstekst og Slack-blokker. Tar ingen beslutninger og sender ingenting. Kan kjøres som dry-run. |
| `scripts/notify_slack.py` | Sender til Slack (kanal pluss DM-varsler). Kun standardbibliotek. |
| `.github/workflows/activate.yml` | To triggere (knapp og hendelse) til én jobb. |
| `.github/workflows/validate.yml` | Referanseintegritet på hver PR. |

## 5. Veiviseren

En statisk markdown-sjekkliste er skjør under press. I stedet oppretter hver
aktivering en **GitHub-sak fra veiviseren**, der hvert steg er et avhukingspunkt
med rolleløst ansvarlig, og en Slack-tråd speiler det. Saken *er*
hendelsesloggen.

Hvert steg har en **gate**:

| Gate | Betydning | Går videre automatisk? |
|---|---|---|
| `info` | Informasjonssteg | Ja |
| `ack` | Ansvarlig må bekrefte | Nei |
| `action` | Utfør, så huk av | Nei |
| `decision` | Navngitt person registrerer ja/nei og begrunnelse | **Aldri** |

`decision`-gatene er der mennesket i løkka hører hjemme. Klokker, utsending og
bokføring er maskinens jobb; det å erklære rødt og å normalisere er menneskets.

## 6. Aktiveringsveier

- **Knapp:** `workflow_dispatch` med nedtrekksmeny (`level`, `plan`, `category`,
  `affected`). Ett klikk fra Actions-fanen, eller via en tynn proxy for en
  Slack slash-kommando som kaller GitHub-API-et.
- **Hendelse:** `repository_dispatch` – overvåking (Statuspage, Azure Monitor)
  sender en POST til dispatches-endepunktet og utløser aktivering automatisk når
  en A-terskel passeres.

## 7. Avgrensning: hva som *ikke* automatiseres

Beredskap har reelle konsekvenser og krav til revisjon og etterlevelse (ISO
22301). Derfor begrenses automatikken til **varsling, koordinering og logging**,
og omfatter *ikke* beslutninger som å erklære rødt eller normalisere. Planen
reserverer med rette disse for avdelingsdirektør og beredskapsleder. Mennesket
beholder tilstandsovergangene; maskinen håndterer utsending og bokføring.
Grensen er gjort eksplisitt slik at de som reviewer, kan stole på systemet.

## 8. Sikkerhet og personvern

- `people/directory.yaml` er klassifisert `Internt` (telefonnumre er
  personopplysninger). Den skal ikke speiles til offentlige flater, logger eller
  URL-parametre.
- Slack-token og kanal-ID er repo-secrets (`SLACK_BOT_TOKEN`,
  `SLACK_INCIDENT_CHANNEL`), aldri i kode.
- Repoet bør være privat. Vurder CODEOWNERS på `roles/`, slik at endringer i
  hvem som har myndighet, krever review fra rett personell.
- Telefoneskalering (SMS/tale) er bevisst *ikke* automatisert i v1 – varslene
  inneholder nummeret slik at et menneske kan ringe bevisst.

## 9. Veikart

| Fase | Innhold |
|---|---|
| **v1 (her)** | Skjelett: register, plan, veivisere, aktivator, CI, Slack-sender. Verifisert med dry-run. |
| v1.1 | Fyll inn ekte Slack-ID-er; opprett Slack-app med `chat:write` og `im:write`; sett secrets. |
| v1.2 | Toveis synk: huk av i Slack → oppdater avkrysning i saken (Slack Events API og en liten webhook-mottaker). |
| v2 | Proxy for slash-kommando; `repository_dispatch` fra Statuspage/Azure; CODEOWNERS. |
| v2.1 | Autoevaluering: regn ut RTO/RPO-etterlevelse fra tidsstemplene i saken; generer rapport til kapittel 8. |

## 10. Åpne spørsmål til review

1. Skal arkivet `incidents/*.md` genereres når saken lukkes, eller holder saken
   alene som logg? (v1 forutsetter at saken er loggen, og at arkiv-md-en er
   valgfri.)
2. Bør gult kunne aktiveres fra Slack av vakthavende uten GitHub-tilgang? (Det
   krever slash-proxyen i v2, ikke v1.1.)
3. Hvor mange planer? Hvis flere BOD-planer deler roller, er et delt register
   åpenbart riktig – bekreft at det ikke allerede finnes konkurrerende registre.
