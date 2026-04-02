# Fehlerbehandlung — Mission Forge

## Fehler-Kategorien

Inspiriert von claude-codes strukturierter Fehler-Klassifizierung.
Unterschiedliche Fehlertypen erfordern unterschiedliche Strategien.

| Kategorie          | Code | Beschreibung                              | Retry-Strategie              | Max Retries |
|--------------------|------|-------------------------------------------|------------------------------|-------------|
| `TRANSIENT`        | E1   | Temporaerer API-Fehler, Rate-Limit        | Sofort retry (Backoff)       | 5           |
| `CONTEXT_OVERFLOW` | E2   | Context-Limit erreicht                    | WP splitten, dann retry      | 2           |
| `QUALITY_FAILURE`  | E3   | Ergebnis erfuellt Akzeptanzkriterien nicht | Retry mit mehr Kontext/Model | 2           |
| `BLOCKER`          | E4   | Fehlende Abhaengigkeit, Permission-Fehler | Sofort eskalieren            | 0           |
| `TIMEOUT`          | E5   | Agent antwortet nicht / haengt            | Retry mit Extended Limits    | 2           |

### Fehler-Erkennung

Der Sub-Orchestrator klassifiziert jeden Fehler automatisch:

```
AGENT MELDET FEHLER
     │
     ▼
FEHLER KLASSIFIZIEREN
     │
     ├── API-Error / Rate-Limit ──> TRANSIENT (E1)
     ├── "context length exceeded" ──> CONTEXT_OVERFLOW (E2)
     ├── Akzeptanzkriterien nicht erfuellt ──> QUALITY_FAILURE (E3)
     ├── Fehlende Datei / Permission denied ──> BLOCKER (E4)
     └── Keine Antwort / Abbruch ──> TIMEOUT (E5)
```

### Kategorie-spezifische Strategien

#### E1 — TRANSIENT
- Exponentielles Backoff: 2s, 4s, 8s, 16s, 32s
- Gleicher Agent, gleiche Eingabe
- Nach 5 Fehlschlaegen: Eskalation als BLOCKER

#### E2 — CONTEXT_OVERFLOW
- **Versuch 1**: WP in 2 kleinere Sub-WPs aufteilen
- **Versuch 2**: Nur essenzielle read_first-Dateien laden, Rest als Zusammenfassung
- Danach: Eskalation — WP ist zu komplex fuer einzelnen Agenten

#### E3 — QUALITY_FAILURE
- **Versuch 1**: Gleicher Agent mit spezifischem Feedback zu den gescheiterten Kriterien
- **Versuch 2**: Anderer Agent (hoehere Modell-Praeferenz) mit gleichem WP
- Danach: Eskalation an Mission-Orchestrator

#### E4 — BLOCKER
- Keine Retries — sofortige Eskalation
- Moegliche Ursachen und Loesungen:
  - Fehlende Abhaengigkeit → Welle umplanen
  - Permission denied → Permission-Profile pruefen
  - Fehlende Datei → Vorherige Welle pruefen
  - Budget erschoepft → User-Freigabe einholen

#### E5 — TIMEOUT
- **Versuch 1**: Agent erneut spawnen mit denselben Inputs
- **Versuch 2**: WP vereinfachen oder aufteilen
- Danach: Eskalation

### Fehler-Reporting in SUMMARY.md

Wenn ein Agent fehlschlaegt, muss die SUMMARY.md enthalten:

```markdown
## Fehler

| Feld          | Wert                                      |
|---------------|-------------------------------------------|
| Kategorie     | {{E1-E5}}                                 |
| Beschreibung  | {{Was genau ist schiefgelaufen}}           |
| Versuch       | {{1/2}}                                   |
| Kontext       | {{Welche Dateien geladen, welche Tools}}   |
| Empfehlung    | {{Was der Orchestrator tun sollte}}        |
```

---

## Eskalationskette

```
AGENT MELDET FEHLER
     │
     ▼
FEHLER KLASSIFIZIEREN (E1-E5)
     │
     ├── E1 (TRANSIENT) ──> Backoff + Retry (bis 5x)
     ├── E2 (CONTEXT_OVERFLOW) ──> WP splitten + Retry (bis 2x)
     ├── E3 (QUALITY_FAILURE) ──> Feedback + Retry (bis 2x)
     ├── E4 (BLOCKER) ──> Sofort eskalieren
     └── E5 (TIMEOUT) ──> Respawn + Retry (bis 2x)
     │
     ▼ (nach Retries erschoepft)
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

## Reparatur-Strategie (Legacy — wird durch Kategorie-System ersetzt)

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
4. Log `CHAIN_SEALED` mit `reason: ABORTED` in AuditChain
5. Erstelle einen partiellen MISSION-REPORT.md mit dem erreichten Stand
6. Alle bereits abgeschlossenen WP-Ergebnisse bleiben erhalten

## Haeufige Fehlerursachen

| Fehler                         | Kategorie | Ursache                          | Praevention                        |
|--------------------------------|-----------|----------------------------------|------------------------------------|
| Agent liefert kein Ergebnis    | E2 / E5   | Context-Limit oder Timeout       | WP weiter zerlegen                 |
| Falsches Ergebnis-Format       | E3        | Unklare Anweisungen in TASK.md   | Konkrete Beispiele in TASK.md      |
| Agent arbeitet an falschem WP  | E3        | Unklare Scope-Abgrenzung         | Explizite Nicht-Ziele in TASK.md   |
| Deadlock zwischen Wellen       | E4        | Fehlende Abhaengigkeit im Graph  | Pre-Flight DAG-Validierung         |
| API Rate-Limit                 | E1        | Zu viele parallele Requests      | Wave-Parallelitaet begrenzen       |
| Budget erschoepft              | E4        | Zu viele Repair-Zyklen           | Cost-Tracking + fruehe Warnung     |
| Permission denied              | E4        | Falsches Permission-Profile      | Profile vor Spawn validieren       |
