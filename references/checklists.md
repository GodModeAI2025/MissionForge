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
- [ ] Traceability-Matrix vollstaendig
- [ ] User hat Plan freigegeben

## Wave-Gate (nach jeder Welle)

- [ ] Alle Agenten der Welle haben Ergebnisse geliefert
- [ ] Ergebnisse gegen Akzeptanzkriterien geprueft
- [ ] STATE.md aktualisiert
- [ ] Fehlgeschlagene WPs: Reparatur oder Eskalation dokumentiert

## Post-Flight (nach Missionsende)

- [ ] Zero-Drop-Audit bestanden
- [ ] Verifikationsbericht erstellt (VERIFICATION.md)
- [ ] Abschlussbericht erstellt (MISSION-REPORT.md)
- [ ] Alle Artefakte im results/ Verzeichnis
- [ ] Offene Punkte dokumentiert oder eskaliert

## Export-Check (vor Package-Export)

- [ ] Mission Status VERIFIED
- [ ] Alle aufgabenspezifischen Werte durch Platzhalter ersetzt
- [ ] defaults.yaml mit allen Parametern erstellt
- [ ] README.md generiert
- [ ] Exportierte SKILL.md validiert (Name, Description, Frontmatter)
- [ ] Package in REGISTRY.md eingetragen
- [ ] Test: Re-Spawn mit anderem Aufgabentext funktioniert
