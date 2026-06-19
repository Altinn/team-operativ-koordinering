# tools/

Enkeltevner mot eksterne tjenester, eksponert via MCP-servere. Dette er
integrasjonslaget kjøretiden kaller.

## Første kandidater

- **slack** — post til hendelseskanal, åpne DM, speile avhukinger (jf. toveis-
  synk i DESIGN.md §9-veikartet).
- **github** — opprette/oppdatere hendelsessak, lese checkbox-status.
- **overvaking** — motta signal fra Statuspage / Azure Monitor som
  `repository_dispatch` (den maskin-detekterbare «when»-aksen).

Hold hemmeligheter som repo-secrets, aldri i kode (jf. DESIGN.md §8).
