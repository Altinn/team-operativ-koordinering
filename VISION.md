# Visjon: prosess som kjørbar kode

**Kort sagt:** flytt rutiner, planer og prinsipper fra passive Word-/Excel-
dokumenter til systemer som gjør jobben og holder seg selv oppdatert. Beredskap
er det første beviset; mønsteret er ikke beredskapsspesifikt.

## Problemet

Et dokument *beskriver* hva som skal skje. Det legger hele byrden på et menneske
i det verste øyeblikket: huske at dokumentet finnes, finne mappa, lese, tolke,
finne ut *hvordan* – og så handle. Når noen bytter rolle, er dokumentet feil
dagen etter, og ingen oppdager det før det smeller. Det skalerer feil vei: ett
dokument blir til ti tusen, alle utdaterte samtidig.

## Skiftet: beskrivende → kjørbart

Et kjørbart system bærer *hvordan*-en og lar mennesket gjøre kun de vurderingene
som faktisk krever et menneske. Tre prinsipper:

1. **Én kilde til sannhet.** Roller, terskler og steg ligger som maskinlesbare
   data, ett sted, i Git. Det menneskelesbare dokumentet er *generert* fra
   dataene – aldri redigert for hånd. Da kan de to ikke gå ut av synk.
2. **Pek på roller, ikke personer.** Når noen slutter eller bytter jobb, endrer
   du én linje. Alle planer som peker på rollen blir riktige i samme øyeblikk.
   PR-en er revisjonssporet.
3. **Mennesket beholder beslutningene.** Automatikken håndterer varsling,
   koordinering og logging. Den erklærer aldri rød og normaliserer aldri – det
   er menneskets.

## Automatiseringsstige (per steg, risikostyrt)

Hvert steg velger hvor langt opp stigen det får gå, ut fra risiko:

```
narrate  →  assist  →  suggest  →  veto  →  auto
(fortell) (gi knapp) (foreslå)  (gjør,   (gjør
                                stopp-   selv)
                                bart)
```

Lavrisiko-steg kan gå helt til *auto*. Høyrisiko-steg stopper lavt. Regelen
håndheves i koden, ikke i en kommentar: et høyrisiko-steg *kan ikke* settes til
auto, og et beslutningssteg *kan ikke* gjøres av maskinen. CI avviser det.

## Manuell utløser er permanent

Ikke alt lar seg integrere. Innbrudd, ulykker, dødsfall – hendelser ingen API
varsler om. Knappen er hoveddøra for alt programvaren ikke kan se selv, ikke en
midlertidig krykke.

## Hvorfor beredskap først

Det er en konkret, avgrenset plan vi uansett må ha, der grensen mellom maskin og
menneske er knivskarp – perfekt som første bevis. Det samme mønsteret gjenbrukes
på onboarding, tilgangsstyring og andre rutiner. Rolleregisteret er delt
infrastruktur på tvers av alle.

## Hva det krever

- Ett **privat** ops-repo (det holder hvem-har-hvilken-rolle, som kan misbrukes).
- En **AI-plugin/skill** som veileder ikke-tekniske eiere gjennom endringer – de
  redigerer kilden, aldri det genererte dokumentet. En hook hindrer feilen.
- **CI** som håndhever integritet og styringsreglene over.
- **AI som forsterker oppå et solid fundament** – ikke noe systemet er avhengig
  av for å virke. Det holder tilliten (og revisjonssporet) uavhengig av en modell.
