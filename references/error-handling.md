# Fehlerbehandlung — Mission Forge

## Eskalationskette

```
AGENT MELDET FEHLER
     │
     ▼
REPARATUR-VERSUCH 1 (gleicher Agent, neuer Anlauf)
     │
     ├── Erfolg ──> Weiter
     │
     ▼
REPARATUR-VERSUCH 2 (gleicher Agent, anderer Ansatz)
     │
     ├── Erfolg ──> Weiter
     │
     ▼
ESKALATION AN SUB-ORCHESTRATOR
     │ Kann er das Problem mit einem anderen Agent loesen?
     ├── Ja ──> Neuer Agent, gleiches WP
     │
     ▼
ESKALATION AN MISSION-ORCHESTRATOR
     │ Kann er umplanen? WP aufteilen? Abhaengigkeit aendern?
     ├── Ja ──> Neuer Plan, neue Welle
     │
     ▼
ESKALATION AN USER
     │
     └── User entscheidet:
         ├── Ueberspringen (Status: SKIPPED mit Begruendung)
         ├── Manuell loesen (Status: DONE nach User-Input)
         └── Mission abbrechen (Status: ABORTED)
```

## Reparatur-Strategie

| Versuch | Strategie                                              |
|---------|--------------------------------------------------------|
| 1       | Gleicher Ansatz mit mehr Kontext oder korrigierten Inputs |
| 2       | Alternativer Ansatz: anderes Tool, andere Zerlegung     |
| Danach  | Eskalation — kein dritter Versuch auf gleicher Ebene    |

## Missions-Abbruch

Wenn eine Mission vorzeitig beendet werden muss:

1. Setze `status: ABORTED` in STATE.md
2. Alle laufenden WPs erhalten Status `ABORTED`
3. Dokumentiere im Entscheidungslog den Grund des Abbruchs
4. Erstelle einen partiellen MISSION-REPORT.md mit dem erreichten Stand
5. Alle bereits abgeschlossenen WP-Ergebnisse bleiben erhalten

## Haeufige Fehlerursachen

| Fehler                         | Ursache                          | Praevention                        |
|--------------------------------|----------------------------------|------------------------------------|
| Agent liefert kein Ergebnis    | Context-Limit erreicht           | WP weiter zerlegen                 |
| Falsches Ergebnis-Format       | Unklare Anweisungen in TASK.md   | Konkrete Beispiele in TASK.md      |
| Agent arbeitet an falschem WP  | Unklare Scope-Abgrenzung         | Explizite Nicht-Ziele in TASK.md   |
| Deadlock zwischen Wellen       | Fehlende Abhaengigkeit im Graph  | Pre-Flight DAG-Validierung         |
