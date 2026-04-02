# Checklisten — Mission Forge

## Pre-Flight (vor Ausfuehrungsbeginn)

### Basis-Checks (alle Modi)
- [ ] COMPANY.md erstellt und validiert
- [ ] Operational Mode bestimmt (lite/standard/enterprise)
- [ ] Alle Teams mit TEAM.md definiert (nicht im lite-Modus)
- [ ] Alle Agenten mit AGENTS.md definiert
- [ ] Alle Anforderungen in REQs erfasst
- [ ] Alle REQs haben zugehoerige WPs
- [ ] Alle WPs sind Wellen zugeordnet
- [ ] Alle WPs haben zugewiesene Agenten
- [ ] Alle benoetigten Skills verfuegbar
- [ ] STATE.md initialisiert
- [ ] Traceability-Matrix vollstaendig
- [ ] User hat Plan freigegeben

### Schema & DAG Validierung (standard + enterprise)
- [ ] `python scripts/validate-schema.py` bestanden
- [ ] `python scripts/build-dag.py` — Abhaengigkeitsgraph azyklisch
- [ ] Context-Budget pro Agent berechnet und unter Limit

### Enterprise-Checks (nur enterprise-Modus)
- [ ] AuditChain Genesis-Block erstellt
- [ ] Alle Agenten haben permission-profile gesetzt
- [ ] Budget in COMPANY.md definiert (metadata.max-cost)
- [ ] skills.lock erstellt und im Genesis-Block gehasht
- [ ] Wellenplan in AuditChain versiegelt (WAVE_PLAN_SEALED)
- [ ] Policy-Compliance geprueft (falls policy.yaml existiert)

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
