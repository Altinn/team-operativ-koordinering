# hooks/

Deterministisk automatikk som kjøres på livssyklus-hendelser — garantert, ikke
opp til modellen. Hver hook er en mappe med `hooks.json` + ev. skript.

## Første kandidater

- **regenerer-doc** — etter endring i `plans/*/plan.yaml`: regenerer `plan.md`
  fra YAML, så de to aldri går ut av synk (én kilde, doc er generert).
- **blokker-generert** — avvis redigering av filer merket som genererte, så
  ingen ved et uhell endrer `plan.md` i stedet for kilden.
- **valider-før-commit** — kjør `scripts/resolve.py validate` lokalt, samme gate
  som CI, før endringen rekker å bli en feilende PR.

Hooks håndhever det skills bare *anbefaler*: belte og bukseseler.
