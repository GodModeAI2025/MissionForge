# Context Management — Mission Forge

Inspiriert von claude-codes 13-Dateien-System fuer Session Compaction.
Verhindert den haeufigsten Agent-Fehler: "Context-Limit erreicht".

---

## Problem

MissionForge-Agenten arbeiten mit frischem Kontext. Aber wenn ein Agent:
- TASK.md + alle read_first-Dateien + aktivierte Skills + SUMMARY.md der
  Vorgaenger-WPs laden muss, kann der Kontext gesprengt werden.

## Context-Budget-Modell

### Token-Schaetzung pro Komponente

| Komponente              | Geschaetzte Tokens | Quelle              |
|-------------------------|-------------------:|----------------------|
| TASK.md (Body)          | 200 – 2.000       | Manifest             |
| read_first Datei        | 500 – 10.000      | Pro Datei            |
| Aktivierter Skill       | 500 – 5.000       | SKILL.md Body        |
| SUMMARY.md (Vorgaenger) | 200 – 1.000       | Pro WP               |
| STATE.md (read-only)    | 300 – 1.500       | Immer geladen        |
| Agent-Instruktionen     | 200 – 800         | AGENTS.md Body       |

### Budgetberechnung vor Agent-Spawn

Bevor ein Agent gespawnt wird, berechnet der Orchestrator:

```
Context-Budget = Σ(read_first Tokens) + TASK.md + SKILL.md + STATE.md + AGENTS.md + Reserve

Verfuegbar = Max-Context × max-context-usage
                              (z.B. 200K × 60% = 120K Tokens)

Wenn Context-Budget > Verfuegbar:
  → Warnung loggen
  → Kompaktierungs-Strategien anwenden
```

### Kompaktierungs-Strategien (in Prioritaetsreihenfolge)

1. **read_first reduzieren**: Nur die wirklich benoetigten Abschnitte laden,
   nicht ganze Dateien. Orchestrator erstellt Zusammenfassung der relevanten Teile.

2. **Vorgaenger-Zusammenfassung**: Statt rohe SUMMARY.md der Vorgaenger-WPs
   laden, erstellt der Orchestrator eine kompakte Handoff-Zusammenfassung
   (max 500 Tokens pro Vorgaenger).

3. **Skill-Kompaktierung**: Nur den `## Anweisungen`-Teil des Skills laden,
   nicht die vollstaendige SKILL.md mit allen Referenzen.

4. **WP splitten**: Wenn nach Kompaktierung immer noch zu gross:
   Das WP in 2 Sub-WPs aufteilen mit klar getrenntem Scope.

## Handoff-Dokumente

Zwischen Wellen erstellt der Orchestrator kompakte Handoff-Dokumente
statt rohe SUMMARY.md-Dateien weiterzugeben:

```markdown
# Handoff: Welle 1 → Welle 2

## Erledigte WPs
- WP-001: Setup abgeschlossen. Konfigdatei unter /config/app.yaml
- WP-002: API-Endpunkte implementiert. 5 Routen in /src/api/

## Fuer Welle 2 relevant
- Datei /config/app.yaml enthaelt DB-Credentials (fuer WP-003)
- API-Schema in /docs/api.json (fuer WP-004)

## Bekannte Einschraenkungen
- Rate-Limit auf 100 req/s (relevant fuer WP-005)
```

**Regel**: Ein Handoff-Dokument darf maximal 1.000 Tokens haben.

## Context-Manifest

Jeder Agent bekommt ein Context-Manifest das exakt auflistet was geladen wird:

```yaml
# .mission-forge/context/wp-003-context.yaml
agent: implementierer-01
task: tasks/wp-003/TASK.md
context-items:
  - type: task
    path: tasks/wp-003/TASK.md
    estimated-tokens: 800
  - type: read_first
    path: src/api/routes.py
    estimated-tokens: 2400
  - type: skill
    name: code-review
    path: skills/code-review/SKILL.md
    estimated-tokens: 1200
    mode: compact     # nur Anweisungen, keine Referenzen
  - type: handoff
    path: context/handoff-wave-1.md
    estimated-tokens: 600
  - type: state
    path: STATE.md
    estimated-tokens: 800
    mode: summary     # nur Metriken + aktuelle Welle
total-estimated: 5800
budget: 120000
utilization: "4.8%"
```

## max-context-usage Enforcement

Das `metadata.max-context-usage` Feld in AGENTS.md wird jetzt tatsaechlich enforced:

1. **Pre-Spawn-Check**: Orchestrator berechnet Context-Budget
2. **Warnung bei >80%**: Logge Warnung im Entscheidungslog
3. **Blockierung bei >100%**: Spawne Agent NICHT, wende Kompaktierung an
4. **Logging**: Geschaetztes Budget wird in AuditChain protokolliert

## Best Practices

- **read_first sparsam verwenden**: Maximal 3 Dateien pro Task
- **Dateien nicht vollstaendig laden**: Spezifische Zeilen/Abschnitte angeben
- **Ergebnisse kompakt halten**: SUMMARY.md unter 1.000 Tokens
- **Skills modular halten**: Ein Skill unter 3.000 Tokens
- **Context-Manifest erstellen**: Fuer komplexe Tasks immer ein Manifest anlegen
