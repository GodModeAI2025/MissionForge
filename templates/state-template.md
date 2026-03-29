---
mission: {{MISSION_SLUG}}
status: OPEN
started: {{ISO_TIMESTAMP}}
current-wave: 0
total-waves: {{N}}
total-requirements: {{N}}
total-work-packages: {{N}}
total-agents: {{N}}
---

# Mission State: {{MISSION_NAME}}

> Single Source of Truth — Wird ausschliesslich vom Mission-Orchestrator aktualisiert.

## Traceability Matrix

| REQ-ID  | Beschreibung          | WP-IDs       | Status      | Verified | Anmerkung |
|---------|-----------------------|--------------|-------------|----------|-----------|
| REQ-001 | {{Anforderung 1}}     | WP-001       | OPEN        | NO       |           |
| REQ-002 | {{Anforderung 2}}     | WP-002, 003  | OPEN        | NO       |           |

## Arbeitspaket-Status

| WP-ID   | Welle | Agent              | Status       | Artefakte              | Versuche |
|---------|-------|--------------------|--------------|------------------------|----------|
| WP-001  | 1     | {{agent-slug}}     | OPEN         | —                      | 0/2      |
| WP-002  | 1     | {{agent-slug}}     | OPEN         | —                      | 0/2      |

### Status-Werte

- `OPEN` — Noch nicht begonnen
- `IN_PROGRESS` — Agent arbeitet daran
- `DONE` — Agent hat Ergebnis geliefert
- `VERIFIED` — Ergebnis gegen Akzeptanzkriterien geprueft und bestanden
- `FAILED` — Reparatur-Versuche erschoepft
- `ESCALATED` — An hoehere Ebene eskaliert
- `SKIPPED` — Bewusst ausgelassen (mit Begruendung)
- `ABORTED` — Mission vorzeitig beendet

## Wellen-Fortschritt

| Welle | WPs              | Status       | Gestartet        | Abgeschlossen    |
|-------|------------------|--------------|------------------|------------------|
| 1     | WP-001, WP-002   | PENDING      | —                | —                |
| 2     | WP-003           | PENDING      | —                | —                |

## Entscheidungslog

| Zeitpunkt | Entscheider            | Entscheidung                    | Begruendung              |
|-----------|------------------------|---------------------------------|--------------------------|
| {{TS}}    | Mission-Orchestrator   | {{Was wurde entschieden}}       | {{Warum}}                |

## Blocker

| Zeitpunkt | WP-ID   | Beschreibung             | Zugewiesen an       | Status    |
|-----------|---------|--------------------------|---------------------|-----------|
|           |         |                          |                     |           |

## Metriken

| Metrik                    | Wert |
|---------------------------|------|
| Agenten gespawnt          | 0    |
| Reparatur-Zyklen          | 0    |
| Eskalationen an User      | 0    |
| Context-Resets             | 0    |
| Skills aktiviert          | 0    |
