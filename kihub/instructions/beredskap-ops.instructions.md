---
name: beredskap-ops
description: Kjernereglene for å endre beredskap-ops-repoet trygt. Alltid i kontekst.
---

# Slik endrer du beredskap-ops trygt

Dette repoet er prosess som kjørbar kode. Følg disse reglene uten unntak:

1. **Kilden til sannhet er YAML-dataene.** Roller, personer, planer og steg bor i
   `roles/`, `people/` og `plans/`. Rediger ALDRI en generert fil for hånd
   (filer merket `*.generated.md` eller med «GENERERT FIL»-header). Endre kilden
   og la regenereringen oppdatere dokumentet.

2. **Pek på roller, aldri personer.** Planer og steg navngir roller
   (`incident_manager`), aldri mennesker. Personer kobles til roller kun i
   `roles/registry.yaml`. Bytter noen jobb: endre én linje der.

3. **Hold person-ID-er i synk.** Hver `holder`/`deputy` i `roles/registry.yaml`
   må finnes som nøkkel i `people/directory.yaml`, ellers feiler valideringen.

4. **Automatiseringsgrensen er hellig.** Maskinen varsler, koordinerer og logger.
   Den erklærer aldri rødt og normaliserer aldri. I steg-data:
   - et `decision`-steg MÅ ha `automation: narrate`;
   - et `risk: high`-steg kan ALDRI ha `automation: auto`.
   Disse håndheves av `schema/step.schema.json` og validatoren.

5. **Valider før hver PR.** Kjør `python scripts/resolve.py validate` for alt som
   rører `roles/`, `people/`, `plans/` eller `scripts/`. CI kjører det samme.

6. **Personvern.** `people/directory.yaml` er `Internt` (telefonnumre er
   personopplysninger). Ikke speil den til offentlige flater, logger eller
   URL-parametre. Hold repoet privat.
