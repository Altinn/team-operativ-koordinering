# kihub/ — AI-native artefakter for beredskap-ops

Denne mappa holder de gjenbrukbare AI-byggeklossene for dette repoet:
skills, agents, hooks, workflows, tools og instructions. De utvikles her, mot
vår egen kjøretid, og kan publiseres til **DigDir KI Hub**
(https://altinn.github.io/kihub/) når de er modne.

Skillet å huske: **dataene** (roller, planer, steg) bor i repoet ellers og er
kilden til sannhet. **Artefaktene her** er verktøyene som hjelper mennesker og
maskiner å lese, endre og kjøre de dataene trygt.

## Mappestruktur (følger KI Hubs egne kategorier)

| Mappe | Hva | Konvensjon |
|---|---|---|
| `skills/` | Innkapslet framgangsmåte modellen henter ved behov | `<navn>/SKILL.md` + ev. skript |
| `agents/` | Egne personaer/kontekster for avgrensede oppgaver | `<navn>.agent.md` |
| `hooks/` | Deterministisk automatikk på livssyklus-hendelser | `<navn>/hooks.json` + skript |
| `workflows/` | Reproduserbar fler-stegs orkestrering | `<navn>.md` |
| `tools/` | Integrasjoner (Slack, GitHub, overvåking) via MCP | per server |
| `instructions/` | Alltid-lastet kontekst/regler for repoet | `<navn>.instructions.md` |
| `plugins/` | Samlepakke av det over, klar for distribusjon | `<navn>/plugin.json` |

## Valg av byggekloss (kort)

- Skal noe **alltid** skje på en hendelse (regenerere doc, blokkere redigering av
  generert fil, kjøre `validate`)? → **hook** (garanti, ikke valgfritt).
- Skal modellen **veilede** noen gjennom en oppgave (endre en rolle trygt)? →
  **skill**.
- Trenger du en egen **kontekst** som løser en flertrinns-oppgave? → **agent**.
- Må flyten være **deterministisk og reproduserbar** med flere steg? → **workflow**.
- En **enkelt evne** mot en ekstern tjeneste? → **tool** (MCP).
- Skal flere av disse **distribueres samlet**? → **plugin**.

Se hver undermappe for første konkrete kandidat.
