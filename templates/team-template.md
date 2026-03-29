---
schema: missionforge/v1
kind: team
slug: {{TEAM_SLUG}}
name: "Team {{TEAM_NAME}}"
description: >
  {{Wann wird dieses Team aktiviert? Welche Entscheidungen unterstuetzt es?
  Welchen Teil der Mission deckt es ab?}}
manager: agents/{{SUB_ORCHESTRATOR_SLUG}}
includes:
  agents:
    - agents/{{agent-slug-1}}
    - agents/{{agent-slug-2}}
  skills:
    - {{skill-shortname-1}}
    - {{skill-shortname-2}}
tags:
  - {{team-capability-tag}}
metadata:
  phase: "{{planung | ausfuehrung | verifikation}}"
---

# Team {{TEAM_NAME}}

## Verantwortungsbereich

{{Klare Abgrenzung: Was gehoert in den Scope dieses Teams?}}

- **Zustaendig fuer**: {{Aufzaehlung}}
- **Nicht zustaendig fuer**: {{Explizite Ausschluesse}}

## Arbeitsweise

1. **Sub-Orchestrator** empfaengt Auftrag vom Mission-Orchestrator
2. **Sub-Orchestrator** verteilt Arbeitspakete an Team-Agenten
3. **Agenten** arbeiten parallel (wo moeglich) in frischen Kontexten
4. **Agenten** schreiben Ergebnisse in `.mission-forge/results/`
5. **Sub-Orchestrator** sammelt und validiert Ergebnisse
6. **Sub-Orchestrator** meldet Abschluss an Mission-Orchestrator

## Uebergaben

| Von                  | An                    | Was wird uebergeben            |
|----------------------|-----------------------|-------------------------------|
| Mission-Orchestrator | Sub-Orchestrator      | WP-Liste fuer aktuelle Welle  |
| Sub-Orchestrator     | Agent                 | TASK.md + aktivierte Skills    |
| Agent                | Sub-Orchestrator      | SUMMARY.md im results/ Ordner |
| Sub-Orchestrator     | Mission-Orchestrator  | Wellen-Status + Maengelliste  |

## Eskalationsregeln

Der Sub-Orchestrator eskaliert an den Mission-Orchestrator wenn:

- Ein Agent nach 2 Reparatur-Versuchen weiterhin fehlschlaegt
- Eine Abhaengigkeit nicht erfuellt ist die ausserhalb des Team-Scopes liegt
- Der Team-Scope nicht ausreicht um ein WP zu erledigen
- Ein Blocker entdeckt wird der andere Teams betrifft
