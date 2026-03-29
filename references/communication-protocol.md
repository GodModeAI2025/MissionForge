# Kommunikationsprotokoll — Mission Forge

## Prinzip

Agenten kommunizieren **ausschliesslich ueber Dateien** im `.mission-forge/` Verzeichnis.
Kein Agent kommuniziert direkt mit einem anderen Agent.

## Datenfluss

```
┌─────────────────────────────────────────────────────┐
│                MISSION-ORCHESTRATOR                  │
│  STATE.md: Single Source of Truth                    │
├──────────┬──────────────────┬───────────────────────┤
│          │                  │                        │
▼          ▼                  ▼                        │
PLANUNG    AUSFUEHRUNG       VERIFIKATION             │
│          │                  │                        │
│ Schreibt │ Schreibt        │ Schreibt               │
│ PLAN.md  │ SUMMARY.md      │ VERIFICATION.md        │
│          │ pro WP          │                        │
└──────────┴──────────────────┴───────────────────────┘
```

## Regeln

1. **STATE.md** ist die einzige Datei die der Mission-Orchestrator schreibt
2. **Agenten** schreiben nur in ihren zugewiesenen `results/wave-N-wp-XXX/` Ordner
3. **Sub-Orchestratoren** lesen Ergebnisse und melden Status an den Mission-Orchestrator
4. **Keine Seiteneffekte**: Ein Agent darf keine Dateien aendern die einem anderen Agent zugewiesen sind
5. **Read-Only fuer Pruefer**: Checker-Agenten haben kein Write/Edit-Recht

## Uebergabe-Format

| Von                  | An                    | Datei                               | Inhalt                  |
|----------------------|-----------------------|--------------------------------------|-------------------------|
| Mission-Orchestrator | Sub-Orchestrator      | TASK.md pro WP                       | Arbeitsauftrag          |
| Agent                | Sub-Orchestrator      | results/wave-N-wp-XXX/SUMMARY.md    | Ergebnis + Evidenz      |
| Sub-Orchestrator     | Mission-Orchestrator  | STATE.md Update (via Orchestrator)   | Status + Maengelliste   |
| Verifikation         | Mission-Orchestrator  | VERIFICATION.md                      | Pruefbericht            |
