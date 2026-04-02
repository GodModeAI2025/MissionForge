# Layered Configuration — Mission Forge

Inspiriert von claude-codes geschichtetem Settings-System
(User → Managed → Policy) mit klarer Ueberschreibsemantik.

---

## Konfigurationshierarchie

Settings werden in folgender Reihenfolge geladen. Spaetere Ebenen
ueberschreiben fruehere:

```
1. Defaults (im Skill eingebaut)
    ↓
2. User-Config:     ~/.mission-forge/config.yaml
    ↓
3. Projekt-Config:  .mission-forge/config.yaml
    ↓
4. Company-Config:  .mission-forge/COMPANY.md (execution: Block)
    ↓
5. Agent-Config:    .mission-forge/agents/*/AGENTS.md (metadata:)
```

## Config-Datei Schema

```yaml
# ~/.mission-forge/config.yaml  ODER  .mission-forge/config.yaml
# ================================================================

# Ausfuehrungsmodus
mode: standard                    # lite | standard | enterprise

# Default-Einstellungen fuer Agenten
defaults:
  model-preference: sonnet        # opus | sonnet | haiku
  max-context-usage: "60%"        # Maximale Context-Nutzung
  permission-profile: executor    # executor | reviewer | planner | orchestrator
  max-cost: "5.00"                # Budget-Limit pro Agent (USD)

# Validierung
validation:
  schema-check: true              # validate-schema.py bei Pre-Flight
  dag-check: true                 # build-dag.py bei Pre-Flight
  strict-mode: false              # Warnings als Errors behandeln

# Parallelitaet
execution:
  max-parallel-agents: 3          # Maximale gleichzeitige Agenten
  max-repair-attempts: 2          # Reparatur-Versuche pro Fehler-Kategorie
  wave-gate: strict               # strict | relaxed (alle WPs oder Mehrheit)

# AuditChain
auditchain:
  enabled: true                   # Hash-Chain aktivieren
  verify-on-complete: true        # Automatische Verifikation am Ende

# Monte-Carlo
monte_carlo:
  enabled: false                  # Nur fuer critical Tasks
  variants: 3                     # Anzahl Varianten
  selection: best_score           # best_score | consensus | user_choice

# Skill-Discovery
skills:
  search-paths:                   # Zusaetzliche Skill-Suchpfade
    - ~/.claude/skills
    - ./.claude/skills
  auto-generate: true             # Fehlende Skills automatisch generieren
  lock-on-genesis: true           # skills.lock beim Genesis erstellen

# Cost-Tracking
cost:
  budget: "10.00"                 # Gesamt-Budget (USD)
  warn-threshold: 80              # Warnung bei X% verbraucht
  abort-threshold: 100            # Eskalation bei X% verbraucht
  track-per-wave: true            # Pro-Welle Tracking

# Internationalisierung (Vorbereitung fuer Phase D)
locale: de                        # de | en
```

## Defaults (Ebene 1 — im Skill eingebaut)

Wenn keine Config-Datei existiert, gelten diese Werte:

| Setting                    | Default     |
|----------------------------|-------------|
| mode                       | standard    |
| defaults.model-preference  | sonnet      |
| defaults.max-context-usage | 60%         |
| defaults.permission-profile| executor    |
| execution.max-parallel-agents | 3        |
| execution.max-repair-attempts | 2        |
| execution.wave-gate        | strict      |
| auditchain.enabled         | true        |
| monte_carlo.enabled        | false       |
| cost.budget                | 10.00       |
| cost.warn-threshold        | 80          |
| locale                     | de          |

## Resolved Configuration anzeigen

```bash
python scripts/validate-schema.py .mission-forge --show-config
```

Zeigt die aufgeloeste Konfiguration nach Merge aller Ebenen.

## Policy Overrides (Organisationsebene)

Fuer Enterprise-Umgebungen koennen Policies definiert werden die NICHT
ueberschrieben werden koennen:

```yaml
# ~/.mission-forge/policy.yaml (von Admin verwaltet)
policy:
  enforce:
    auditchain.enabled: true         # AuditChain kann nicht deaktiviert werden
    validation.schema-check: true    # Schema-Check ist Pflicht
    cost.budget: "50.00"             # Maximales Budget
  deny:
    mode: lite                       # Lite-Modus nicht erlaubt
```

Policy-Felder haben hoechste Prioritaet und koennen nicht durch
User- oder Projekt-Config ueberschrieben werden.
