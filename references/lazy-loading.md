# Lazy Loading & Startup-Optimierung — Mission Forge

Inspiriert von claude-codes Parallel-Prefetching, Profiling-Checkpoints
und Lazy-Module-Loading.

---

## Prinzip

MissionForge erstellt in Phase 2 alle Manifeste auf einmal. Bei grossen
Missions (15+ WPs) verbraucht das unnoetig Tokens und Zeit. Lazy Loading
verschiebt die Erstellung auf den Zeitpunkt des tatsaechlichen Bedarfs.

## Eager vs. Lazy Erstellung

| Komponente        | Bisher (Eager)          | Neu (Lazy)                       |
|-------------------|-------------------------|----------------------------------|
| COMPANY.md        | Phase 2                 | Phase 2 (unveraendert)           |
| STATE.md          | Phase 2                 | Phase 2 (unveraendert)           |
| TEAM.md           | Phase 2 (alle)          | Phase 3 (bei Bedarf)             |
| AGENTS.md         | Phase 2 (alle)          | Phase 5 (wenn Welle geplant)     |
| TASK.md           | Phase 2 (alle)          | Phase 2 (nur Frontmatter-Stub)   |
| Skill-Loading     | Phase 4 (alle lesen)    | Phase 6 (vor Agent-Spawn)        |
| Context-Manifest  | —                       | Phase 6 (vor Agent-Spawn)        |

## Stub-Manifeste

In Phase 2 werden nur minimale Stubs erstellt (Katalog-Stufe):

```yaml
# Stub TASK.md (~50 Tokens statt ~500-2000)
---
schema: missionforge/v1
kind: task
slug: wp-007
name: "API-Tests schreiben"
status: OPEN
wave: 3
depends-on:
  - wp-004
requirements:
  - REQ-007
assigned-to: agents/tester
_stub: true                    # Markiert als nicht vollstaendig
---
```

Der vollstaendige Body wird erst in Phase 5/6 generiert wenn das WP
tatsaechlich geplant wird.

## Parallel-Prefetching

Waehrend der Orchestrator Wave N ausfuehrt, kann er parallel:

1. **Wave N+1 Stubs aufloesen**: Vollstaendige TASK.md generieren
2. **Skills vorladen**: Katalog-Stufe der benoetigten Skills
3. **Context-Manifeste erstellen**: Budget-Berechnung fuer naechste Wave

```
Wave N laeuft          Parallel: Wave N+1 vorbereiten
┌─────────────┐        ┌──────────────────────────┐
│ Agent A: WP3│        │ Stub WP-005 aufloesen    │
│ Agent B: WP4│        │ Skill "testing" vorladen │
│             │        │ Context-Manifest WP-005  │
└─────────────┘        └──────────────────────────┘
```

## Manifest-Cache

Einmal geladene und geparste Frontmatter werden im STATE.md
zwischengespeichert (um Mehrfach-Parsing zu vermeiden):

```markdown
## Manifest-Cache (automatisch generiert)

| Slug    | Kind  | Status      | Wave | Agent       | Tokens (est.) |
|---------|-------|-------------|------|-------------|---------------|
| wp-001  | task  | VERIFIED    | 1    | agents/dev  | 800           |
| wp-002  | task  | DONE        | 1    | agents/dev  | 650           |
| wp-003  | task  | IN_PROGRESS | 2    | agents/qa   | 1200          |
```

## Profiling-Checkpoints

Fuer Optimierung koennen Zeitstempel gesetzt werden:

```markdown
## Timing (Debug)

| Checkpoint           | Zeitstempel              | Dauer  |
|----------------------|--------------------------|--------|
| Phase 1 Start        | 2026-04-02T10:00:00Z     | —      |
| Phase 2 Complete     | 2026-04-02T10:00:12Z     | 12s    |
| Phase 5 Complete     | 2026-04-02T10:01:05Z     | 53s    |
| Wave 1 Start         | 2026-04-02T10:01:10Z     | —      |
| Wave 1 Complete      | 2026-04-02T10:03:45Z     | 155s   |
```

## Wann Eager, wann Lazy?

| WP-Anzahl | Empfehlung | Begruendung                          |
|-----------|------------|--------------------------------------|
| 1-5       | Eager      | Overhead von Lazy ueberwiegt Nutzen  |
| 6-15      | Hybrid     | Stubs fuer Tasks, Rest eager         |
| 16+       | Full Lazy  | Signifikante Token-Einsparung        |

Im `lite`-Modus: Immer eager (zu wenig WPs fuer Lazy).
Im `enterprise`-Modus: Lazy empfohlen, aber vollstaendige Stubs erforderlich.
