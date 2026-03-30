# Checklisten — Mission Forge

## Pre-Flight (vor Ausfuehrungsbeginn)

- [ ] COMPANY.md erstellt und validiert
- [ ] Alle Teams mit TEAM.md definiert
- [ ] Alle Agenten mit AGENTS.md definiert
- [ ] Alle Anforderungen in REQs erfasst
- [ ] Alle REQs haben zugehoerige WPs
- [ ] Alle WPs sind Wellen zugeordnet
- [ ] Alle WPs haben zugewiesene Agenten
- [ ] Alle benoetigten Skills verfuegbar
- [ ] Abhaengigkeitsgraph ist azyklisch
- [ ] STATE.md initialisiert
- [ ] AuditChain Genesis-Block erstellt
- [ ] Traceability-Matrix vollstaendig
- [ ] User hat Plan freigegeben
- [ ] Wellenplan in AuditChain versiegelt (WAVE_PLAN_SEALED)

## Wave-Gate (nach jeder Welle)

- [ ] Alle Agenten der Welle haben Ergebnisse geliefert
- [ ] Ergebnisse gegen Akzeptanzkriterien geprueft
- [ ] STATE.md aktualisiert
- [ ] Alle Statuswechsel in AuditChain protokolliert
- [ ] Fehlgeschlagene WPs: Reparatur oder Eskalation dokumentiert
- [ ] Monte-Carlo Tasks: Alle Varianten in Chain, Auswahl dokumentiert

## Post-Flight (nach Missionsende)

- [ ] Zero-Drop-Audit bestanden
- [ ] AuditChain-Integritaetspruefung bestanden (Ebene 6)
- [ ] Verifikationsbericht erstellt (VERIFICATION.md) inkl. Chain-Bericht
- [ ] Abschlussbericht erstellt (MISSION-REPORT.md) inkl. Revisionssicherheit
- [ ] AuditChain versiegelt (CHAIN_SEALED)
- [ ] Alle Artefakte im results/ Verzeichnis
- [ ] Offene Punkte dokumentiert oder eskaliert

## Export-Check (vor Package-Export)

- [ ] Mission Status VERIFIED
- [ ] AuditChain intakt und versiegelt
- [ ] Alle aufgabenspezifischen Werte durch Platzhalter ersetzt
- [ ] AuditChain-Konfiguration in .skill eingebettet
- [ ] defaults.yaml mit allen Parametern erstellt
- [ ] README.md generiert
- [ ] Exportierte SKILL.md validiert (Name, Description, Frontmatter)
- [ ] Package in REGISTRY.md eingetragen
- [ ] Test: Re-Spawn mit anderem Aufgabentext funktioniert
