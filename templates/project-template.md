---
schema: missionforge/v1
kind: project
slug: {{PROJECT_SLUG}}
name: "{{PROJECT_NAME}}"
description: >
  {{Projektziel und Kontext. Wann wird dieses Projekt aktiviert?
  Welchen Teil der Mission deckt es ab?}}
status: PLANNED
tags:
  - {{project-tag}}
metadata:
  created: {{ISO_DATE}}
  estimated-complexity: "{{S | M | L | XL}}"
---

# Projekt: {{PROJECT_NAME}}

## Ziel

{{Was soll mit diesem Projekt erreicht werden? Messbar formuliert.}}

## Scope

- **Enthalten**: {{Was gehoert in den Scope}}
- **Ausgeschlossen**: {{Was gehoert explizit NICHT dazu}}

## Arbeitspakete

| WP-ID   | Titel              | Anforderungen | Status  |
|---------|--------------------|--------------|---------|
| WP-001  | {{Titel}}          | REQ-001      | OPEN    |
| WP-002  | {{Titel}}          | REQ-002, 003 | OPEN    |

## Timeline

| Welle | Arbeitspakete    | Vorbedingung           |
|-------|------------------|------------------------|
| 1     | WP-001           | keine                  |
| 2     | WP-002           | Welle 1 abgeschlossen  |

## Abhaengigkeiten

- {{Abhaengigkeit zu anderen Projekten oder externen Faktoren}}

## Erfolgskriterien

- [ ] {{Pruefbares Kriterium 1}}
- [ ] {{Pruefbares Kriterium 2}}
