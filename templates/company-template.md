---
schema: missionforge/v1
kind: company
slug: {{MISSION_SLUG}}
name: "{{MISSION_NAME}} Task Force"
description: >
  {{DESCRIPTION — Erklaere wann diese Company aktiviert werden soll und
  welche Art von Entscheidungen sie unterstuetzt.}}
version: "1.0.0"
license: MIT
authors:
  - {{AUTHOR}}
tags:
  - {{DOMAIN_TAG}}
  - {{CAPABILITY_TAG}}
metadata:
  created: {{ISO_DATE}}
  source-task: "{{ORIGINAL_TASK_SUMMARY}}"
  priority: {{critical | high | medium | low}}
  estimated-complexity: {{S | M | L | XL}}
---

# {{MISSION_NAME}} Task Force

## Mission Statement

{{1-3 Saetze: Was soll erreicht werden und warum ist diese Mission wichtig?}}

## Ziele

1. {{Ziel 1 — messbar formuliert, z.B. "Alle API-Endpunkte implementiert und getestet"}}
2. {{Ziel 2}}
3. {{Ziel 3}}

## Erfolgskriterien

- [ ] {{Kriterium 1 — pruefbar}}
- [ ] {{Kriterium 2}}
- [ ] {{Kriterium 3}}

## Governance

- **Eskalationspfad**: Agent -> Sub-Orchestrator -> Mission-Orchestrator -> User
- **Quality Gates**: {{Verifikation pro Welle | pro Phase | am Ende}}
- **Kommunikation**: Nur ueber Dateien in `.mission-forge/`

## Randbedingungen

- **Technisch**: {{Stack, Plattform, Versionen}}
- **Zeitlich**: {{Deadline falls vorhanden}}
- **Qualitativ**: {{Standards, Compliance-Anforderungen}}
- **Ressourcen**: {{Max parallele Agenten, Model-Budget}}

## Ausfuehrungskonfiguration

```yaml
# Operational Mode (siehe references/configuration.md)
mode: {{lite | standard | enterprise}}
#   lite:       Kein Sub-Orchestrator, keine formale Verifikation, kein Export
#   standard:   Voller 9-Phasen-Workflow (Default)
#   enterprise: Standard + AuditChain + Monte-Carlo + Policy-Enforcement

auditchain:
  enabled: true              # Kryptographische Hash-Chain (empfohlen: immer true)

execution:
  monte_carlo: false         # true fuer Monte-Carlo bei critical Tasks
  mc_variants: 3             # Anzahl Varianten (nur wenn monte_carlo: true)
  mc_selection: best_score   # best_score | consensus | user_choice
  max-parallel-agents: 3     # Maximale gleichzeitige Agenten

cost:
  budget: "{{10.00}}"        # Gesamt-Budget in USD
  warn-threshold: 80         # Warnung bei X% verbraucht
```

## Includes

- teams/{{TEAM_1}}/TEAM.md
- teams/{{TEAM_2}}/TEAM.md
- teams/{{TEAM_3}}/TEAM.md
