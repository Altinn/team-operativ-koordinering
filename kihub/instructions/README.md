# instructions/

Alltid-lastet kontekst og regler for hvordan repoet skal endres. Filer på formen
`<navn>.instructions.md` med frontmatter.

## Første kandidat: `beredskap-ops.instructions.md`

Kjernereglene, alltid i kontekst:
- **Kilden til sannhet er YAML-dataene.** Rediger aldri en generert `.md` for
  hånd.
- **Pek på roller, aldri personer.**
- **Automatiseringsgrensen:** maskinen varsler, koordinerer og logger; den
  erklærer aldri rødt og normaliserer aldri. Høyrisiko-steg kan ikke være `auto`;
  `decision`-steg er `narrate`.
- **Kjør `scripts/resolve.py validate`** før enhver PR som rører
  roles/people/plans.
