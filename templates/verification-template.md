---
mission: {{MISSION_SLUG}}
verified-by: vollstaendigkeits-pruefer
date: {{ISO_DATE}}
result: {{PASSED | PARTIAL | FAILED}}
coverage-score: {{0-100}}%
---

# Verifikationsbericht: {{MISSION_NAME}}

## Executive Summary

| Metrik                    | Wert                          |
|---------------------------|-------------------------------|
| Anforderungen gesamt      | {{N}}                         |
| Erfuellt                  | {{X}} ({{%}})                 |
| Teilweise                 | {{Y}} ({{%}})                 |
| Offen                     | {{Z}} ({{%}})                 |
| Arbeitspakete gesamt      | {{N}}                         |
| Abgeschlossen             | {{X}}                         |
| Verifiziert               | {{X}}                         |
| Fehlgeschlagen            | {{Y}}                         |

## Zero-Drop-Audit

### Anforderungs-Abdeckung

| REQ-ID  | WP-IDs      | WP-Status      | Akzeptanz geprueft | Dokumentiert | Urteil    |
|---------|-------------|----------------|--------------------|--------------|-----------|
| REQ-001 | WP-001      | VERIFIED       | YES                | YES          | PASSED    |
| REQ-002 | WP-002, 003 | DONE           | YES                | YES          | PASSED    |

### Luecken-Analyse

- [ ] Keine REQ ohne WP-Zuordnung gefunden
- [ ] Keine WP ohne Agent-Zuordnung gefunden
- [ ] Keine WP ohne Ergebnis-Datei gefunden
- [ ] Kein Agent gespawnt der nie reported hat
- [ ] Kein zugewiesener Skill der nie aktiviert wurde

### Traceability-Validierung

- [ ] Jede Zeile in der Traceability-Matrix hat Status != OPEN
- [ ] Jede Zeile hat Verified = YES oder dokumentierte Ausnahme
- [ ] Kein REQ-ID existiert ausserhalb der Matrix

## Detail pro Anforderung

### REQ-001: {{Kurztitel}}

| Aspekt              | Ergebnis                                  |
|---------------------|-------------------------------------------|
| **Status**          | {{FULFILLED / PARTIAL / OPEN}}            |
| **Evidenz**         | {{Wo ist der Beweis? Datei, Test, Output}}|
| **Akzeptanztest**   | {{Beschreibung und Ergebnis}}             |
| **Anmerkungen**     | {{Falls relevant}}                        |

### REQ-002: {{Kurztitel}}
{{Gleiche Struktur}}

## Qualitaetspruefung (Nicht-Funktional)

| Dimension      | Geprueft | Ergebnis         | Anmerkung        |
|----------------|----------|------------------|------------------|
| Vollstaendigkeit| JA      | {{PASS/FAIL}}    |                  |
| Konsistenz     | JA       | {{PASS/FAIL}}    |                  |
| Korrektheit    | JA       | {{PASS/FAIL}}    |                  |
| Integration    | JA       | {{PASS/FAIL}}    |                  |
| Dokumentation  | JA       | {{PASS/FAIL}}    |                  |

## Kryptographische Integritaet (AuditChain)

| Eigenschaft | Wert |
|---|---|
| Chain-Laenge | {{CHAIN_LENGTH}} Eintraege |
| Genesis-Hash | `{{GENESIS_HASH}}` |
| Finaler Hash | `{{FINAL_HASH}}` |
| Zeitraum | {{FIRST_TIMESTAMP}} → {{LAST_TIMESTAMP}} |
| Kette intakt | {{INTACT_STATUS}} |
| Versiegelt | {{SEALED_STATUS}} |
| Beteiligte Agenten | {{AGENTS_LIST}} |

### Event-Verteilung

| Event | Anzahl |
|---|---|
| {{EVENT_NAME}} | {{COUNT}} |

### Integritaets-Urteil

{{INTEGRITY_RESULT — z.B.: "Alle N Eintraege verifiziert. Keine Manipulation erkannt." oder "INTEGRITAETSVERLETZUNG: [Details]"}}

Pruefbar mit:
```bash
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --verbose
```

## Offene Punkte

| # | Beschreibung                   | Schweregrad | Empfehlung              |
|---|--------------------------------|-------------|-------------------------|
| 1 | {{Falls vorhanden}}            | {{H/M/L}}  | {{Nacharbeit/Akzeptanz}}|

## Gesamtempfehlung

**{{APPROVED | REWORK_REQUIRED | ESCALATION}}**

{{Begruendung in 2-3 Saetzen}}
