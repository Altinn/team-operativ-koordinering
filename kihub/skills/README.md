# skills/

Innkapslet framgangsmåte som modellen henter inn når oppgaven passer. Hver skill
er en mappe med `SKILL.md` (frontmatter + instruksjoner) og ev. medfølgende
skript/maler.

## Første kandidat: `endre-rolle`

Veileder en ikke-teknisk eier gjennom å endre hvem som holder en rolle:
- redigerer **kilden** (`roles/registry.yaml` / `people/directory.yaml`),
  aldri en generert fil;
- kjører `python scripts/resolve.py validate` før commit;
- åpner en PR med en tydelig beskrivelse (PR-en er revisjonssporet).

Dette er adopsjonsnøkkelen: gjør den trygge endringen lettere enn å åpne Word.
