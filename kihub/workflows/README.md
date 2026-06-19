# workflows/

Reproduserbar fler-stegs orkestrering der *flyten* er deterministisk (løkker,
fan-out, betingelser), og agenter er de smarte delene inni. Hver workflow er en
`<navn>.md` med naturlig-språk-instruksjoner + hendelseskonfig.

## Første kandidat: `aktivering`

En revisjonsvennlig variant av aktiveringsløpet: validér → resolve → render sak
→ post til Slack → opprett klokker. Spinnen MÅ være deterministisk (beredskap
krever etterprøvbarhet); GitHub Action-en i `.github/workflows/activate.yml`
dekker v1, denne er stedet hvis/ når løpet trenger flere koordinerte AI-steg.
