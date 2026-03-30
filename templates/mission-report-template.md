---
mission: {{MISSION_SLUG}}
company: "{{COMPANY_NAME}}"
completed: {{ISO_DATE}}
duration: "{{DAUER}}"
result: {{PASSED | PARTIAL | FAILED}}
---

# Mission Report: {{MISSION_NAME}}

## Executive Summary

{{2-3 Saetze: Was war die Mission, was wurde erreicht, was ist das Endergebnis?}}

## Ergebnisse

| #  | Lieferobjekt               | Status       | Speicherort / Beschreibung      |
|----|----------------------------|--------------|---------------------------------|
| 1  | {{Deliverable 1}}          | Geliefert    | {{Pfad oder Beschreibung}}      |
| 2  | {{Deliverable 2}}          | Geliefert    | {{Pfad}}                        |
| 3  | {{Deliverable 3}}          | {{Status}}   | {{Pfad}}                        |

## Anforderungs-Erfuellung

| REQ-ID  | Beschreibung          | Status       | Abgedeckt durch  |
|---------|-----------------------|--------------|------------------|
| REQ-001 | {{Kurztitel}}         | FULFILLED    | WP-001           |
| REQ-002 | {{Kurztitel}}         | FULFILLED    | WP-002, WP-003   |

**Abdeckungsquote**: {{X}}/{{N}} ({{%}})

## Organisationsstruktur (wie ausgefuehrt)

```
{{MISSION_NAME}} Task Force
├── Mission-Orchestrator
├── Team Planung
│   ├── Sub-Orchestrator: Planung
│   ├── {{Agent 1}}
│   └── {{Agent 2}}
├── Team Ausfuehrung
│   ├── Sub-Orchestrator: Ausfuehrung
│   ├── {{Agent 3}}
│   ├── {{Agent 4}}
│   └── {{Agent 5}}
└── Team Verifikation
    ├── Sub-Orchestrator: Verifikation
    ├── {{Agent 6}}
    └── {{Agent 7}}
```

## Ausfuehrungs-Metriken

| Metrik                          | Wert     |
|---------------------------------|----------|
| Wellen ausgefuehrt              | {{N}}    |
| Agenten gespawnt                | {{N}}    |
| Arbeitspakete erledigt          | {{N}}/{{N}} |
| Reparatur-Zyklen                | {{N}}    |
| Eskalationen an User            | {{N}}    |
| Skills aktiviert                | {{N}}    |
| Context-Resets                  | {{N}}    |

## Wellen-Verlauf

| Welle | WPs               | Dauer      | Ergebnis          |
|-------|--------------------|------------|--------------------|
| 1     | WP-001, WP-002     | {{Dauer}}  | Alle bestanden     |
| 2     | WP-003             | {{Dauer}}  | Bestanden          |
| 3     | WP-004, WP-005     | {{Dauer}}  | 1 Reparatur noetig |

## Lessons Learned

### Was gut funktioniert hat
- {{Beobachtung 1}}
- {{Beobachtung 2}}

### Was verbessert werden sollte
- {{Verbesserung 1}}
- {{Verbesserung 2}}

### Empfehlungen fuer aehnliche Missionen
- {{Empfehlung 1}}
- {{Empfehlung 2}}

## Revisionssicherheit (AuditChain)

| Eigenschaft | Wert |
|---|---|
| AuditChain | `.mission-forge/audit/CHAIN.jsonl` |
| Eintraege | {{CHAIN_LENGTH}} |
| Genesis-Hash | `{{GENESIS_HASH}}` |
| Finaler Hash | `{{FINAL_HASH}}` |
| Kette intakt | {{INTACT_STATUS}} |
| Versiegelt | {{SEALED_STATUS}} |
| Monte-Carlo Tasks | {{MC_TASK_COUNT}} ({{MC_VARIANT_COUNT}} Varianten) |

Pruefbar mit:
```bash
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --report
```

{{Falls Monte-Carlo verwendet: Auflistung der MC-Tasks mit gewaehlter Variante und Score}}

## Wiederverwendbarkeit

### Wiederverwendbare Company-Teile

| Komponente            | Wiederverwendbar | Anpassung noetig      |
|-----------------------|------------------|-----------------------|
| Team Planung          | JA               | Minimal               |
| Team Verifikation     | JA               | Keine                 |
| Skill: {{name}}       | JA               | {{Beschreibung}}      |
| Agent: {{name}}       | PARTIAL          | {{Was anpassen}}      |

### Export-Empfehlung

{{Welche Teile sollten als eigenstaendige Packages extrahiert und
in die globale Skill-/Company-Bibliothek aufgenommen werden?}}
