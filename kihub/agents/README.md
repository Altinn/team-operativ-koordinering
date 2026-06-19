# agents/

Egne personaer/kontekster med eget systemprompt og verktøy, for avgrensede
fler-trinns oppgaver. Hver agent er en `<navn>.agent.md` med frontmatter
(description, model, tools, name).

## Første kandidat: `veiviser-assistent`

Chat-assistenten som følger en innsatsperson gjennom et aktivert playbook-steg:
- kjenner planen, rollene og hvem som er på vakt akkurat nå;
- svarer på «hvordan gjør jeg dette steget konkret»;
- respekterer automatiseringsgrensen — den **forteller og registrerer** på
  `decision`-steg, men tar dem aldri.
