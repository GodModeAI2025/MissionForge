---
schema: missionforge/v1
kind: task
slug: {{wp-id}}
name: "{{TASK_TITEL}}"
description: >
  {{Was muss konkret getan werden? Welches Ergebnis wird erwartet?}}
assigned-to: agents/{{AGENT_SLUG}}
status: OPEN
priority: {{critical | high | medium | low}}
wave: {{WELLEN_NUMMER}}
depends-on:
  - {{wp-id-der-abhaengigkeit}}
requirements:
  - {{REQ-ID-1}}
  - {{REQ-ID-2}}
tags:
  - {{tag}}
metadata:
  estimated-complexity: "{{S | M | L | XL}}"
---

# Task: {{TASK_TITEL}}

## Ziel

{{Was ist das konkrete, pruefbare Ergebnis dieses Arbeitspakets?}}

## Akzeptanzkriterien

- [ ] {{Pruefbares Kriterium 1 — z.B. "Datei X existiert und enthaelt Y"}}
- [ ] {{Pruefbares Kriterium 2 — z.B. "Test Z laeuft erfolgreich"}}
- [ ] {{Pruefbares Kriterium 3 — z.B. "Kein Fehler bei `command`"}}

## Zu lesende Dateien (read_first)

Lies diese Dateien BEVOR du mit der Arbeit beginnst:

1. `{{pfad/zur/datei-1}}` — {{Warum relevant}}
2. `{{pfad/zur/datei-2}}` — {{Warum relevant}}

## Anweisungen

### Schritt 1: {{Ueberschrift}}
{{Konkrete Anweisung — kein "implementiere geeignetes Error-Handling"}}

### Schritt 2: {{Ueberschrift}}
{{Konkrete Anweisung}}

### Schritt 3: {{Ueberschrift}}
{{Konkrete Anweisung}}

## Ergebnis-Format

- **Speicherort**: `.mission-forge/results/wave-{{N}}-{{wp-id}}/SUMMARY.md`
- **Format**: Markdown mit folgender Struktur:

```markdown
# Ergebnis: {{TASK_TITEL}}

## Zusammenfassung
[Was wurde getan — 2-3 Saetze]

## Geaenderte Dateien
- [Pfad] — [Was geaendert]

## Tests
- [Welche Tests ausgefuehrt, Ergebnis]

## Akzeptanzkriterien
- [x] Kriterium 1: PASSED
- [x] Kriterium 2: PASSED

## Offene Punkte
[Falls vorhanden — sonst "Keine"]
```

## Nicht-Ziele

- {{Was explizit NICHT Teil dieses WPs ist}}
- {{Auch wenn es verlockend waere — hier nicht machen}}
