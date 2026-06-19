---
name: endre-rolle
description: Veileder en bruker gjennom å endre hvem som holder en rolle i beredskap-ops (innehaver/stedfortreder), eller å legge til/fjerne en person. Bruk når noen begynner, slutter eller bytter rolle, eller når brukeren sier ting som "X er ny beredskapsleder", "Y har sluttet", "bytt stedfortreder for incident manager".
---

# Endre en rolle trygt

Målet: gjøre den riktige endringen i **kilden** så validering passerer og
dokumentene regenereres — uten at brukeren trenger å kunne YAML eller Git.

## Før du gjør noe

- Endre KUN kildefilene: `roles/registry.yaml` (hvem holder hva) og
  `people/directory.yaml` (kontaktinfo). Rør aldri `*.generated.md`.
- Person-ID-er (`person.a`, `incident_manager` …) er nøkler som må stemme på
  tvers av de to filene. Bruk samme ID begge steder.

## Framgangsmåte

1. **Avklar hva som skal skje.** Hvem, hvilken rolle, og er det innehaver
   (`holder`) eller stedfortreder (`deputy`)? Ny person, eller en som finnes?

2. **Hvis personen er ny:** legg til en blokk i `people/directory.yaml` med en ny
   ID, navn, e-post, telefon og Slack-ID (`U…`). Mangler du Slack-ID, sett
   `U_REPLACE_ME` og si fra at den må fylles inn (valideringen advarer om den).

3. **Oppdater rollen** i `roles/registry.yaml`: sett `holder` eller `deputy` til
   person-ID-en. Hver rolle bør ha en stedfortreder.

4. **Hvis personen har sluttet:** erstatt alle forekomster av deres ID i
   `roles/registry.yaml` med etterfølgeren. Fjern personen fra
   `people/directory.yaml` først når ingen rolle peker på dem lenger.

5. **Valider:** `python scripts/resolve.py validate`. Det skal ikke være noen
   `FATAL`-linjer. `(warn)` om placeholder-Slack-ID er greit å la stå hvis ekte
   ID ikke finnes ennå.

6. **Regenerer dokumentene:** `python scripts/generate_roster.py`.

7. **Åpne en PR** med en kort beskrivelse av endringen ("Ny beredskapsleder:
   <navn>, gjeldende fra <dato>"). PR-en er revisjonssporet — den viser hvem som
   endret hvem-har-myndighet, og når.

## Vanlige feil å unngå

- Å redigere `ROSTER.generated.md` eller `plan.md`-tabeller direkte — de blir
  overskrevet. Endre kilden.
- Å bytte navn på en person uten å oppdatere ID-en begge steder — gir `FATAL`.
- Å fjerne en stedfortreder uten erstatter — gir advarsel; nøkkelroller skal ha
  en vara.
