# Skill-Plugin-Architektur — Mission Forge

Inspiriert von claude-codes 45 Tool-Directories mit standardisiertem Interface.
Skills werden von heuristischem Matching zu deterministischen Plugins mit
definierten Interfaces, Versionierung und Registry.

---

## Skill-Interface Standard

Jeder Skill MUSS in seiner SKILL.md folgende Felder im Frontmatter haben:

```yaml
---
name: skill-name                    # Pflicht: lowercase, a-z, Bindestriche
description: "Was tut der Skill"    # Pflicht: 1-1024 Zeichen
version: "1.0.0"                    # NEU — Pflicht: SemVer
input-schema:                       # NEU — Empfohlen: Was braucht der Skill?
  - name: input_text
    type: string
    required: true
    description: "Eingabetext"
  - name: options
    type: object
    required: false
output-schema:                      # NEU — Empfohlen: Was liefert der Skill?
  - name: result
    type: file
    format: markdown
    path: "results/"
trigger-patterns:                   # NEU — Empfohlen: Deterministische Trigger
  - "skill-name aktivieren"
  - "keyword1"
  - "keyword2"
compatibility: "Claude Code"        # Optional
allowed-tools: "Read Write Edit"    # Optional
metadata:
  author: "author-name"
  license: "MIT"
  category: "development"           # NEU — Kategorie fuer Registry
  min-missionforge: "4.0.0"         # NEU — Mindest-Version
---
```

## Skill-Verzeichnisstruktur

Jeder Skill ist ein eigenstaendiges Verzeichnis (wie claude-codes Tool-Directories):

```
skills/
└── skill-name/
    ├── SKILL.md              # Pflicht: Hauptdatei mit Interface
    ├── scripts/              # Optional: Ausfuehrbare Scripts
    ├── references/           # Optional: Referenzdokumentation
    ├── assets/               # Optional: Statische Dateien
    └── tests/                # NEU — Optional: Selbsttests
        └── test.sh           # Minimaler Smoke-Test
```

## Skill Registry

Die `skill-registry.json` indiziert alle verfuegbaren Skills fuer schnelles
Matching ohne jede SKILL.md einzeln zu laden (Progressive Disclosure).

```json
{
  "version": "1.0.0",
  "generated": "2026-04-02T10:00:00Z",
  "skills": [
    {
      "name": "code-review",
      "version": "1.2.0",
      "description": "Automatisches Code-Review mit Qualitaetsmetriken",
      "category": "development",
      "trigger-patterns": ["code review", "review code", "pruefe code"],
      "path": "skills/code-review/SKILL.md",
      "input-schema-summary": "source_files: list[string]",
      "output-schema-summary": "review_report: markdown"
    }
  ]
}
```

### Registry generieren

```bash
python scripts/build-registry.py [skills-dir]
```

Das Script durchsucht alle SKILL.md-Dateien und generiert die Registry.

## Skill-Locking (skills.lock)

Aehnlich wie `package-lock.json` — pinnt exakte Versionen pro Mission:

```json
{
  "mission": "MISSION-2026-042",
  "locked": "2026-04-02T10:00:00Z",
  "skills": {
    "code-review": {
      "version": "1.2.0",
      "path": "skills/code-review/SKILL.md",
      "hash": "sha256:abc123..."
    },
    "testing": {
      "version": "2.0.0",
      "path": ".claude/skills/testing/SKILL.md",
      "hash": "sha256:def456..."
    }
  }
}
```

**Regeln:**
- Die Lock-Datei wird beim Genesis-Block erstellt
- Waehrend der Mission wird nur die gelockte Version verwendet
- Wenn ein Skill aktualisiert wird, MUSS ein `SKILL_CHANGED` Event in der AuditChain protokolliert werden
- Die Lock-Datei liegt in `.mission-forge/skills.lock`

## Skill-Kompatibilitaetspruefung

Vor dem Spawnen eines Agenten prueft der Orchestrator:

1. Alle `skills` in AGENTS.md muessen in der Registry existieren
2. Die `allowed-tools` des Skills muessen Subset der Agent-`tools-allowed` sein
3. Die `min-missionforge` Version muss kompatibel sein
4. Input-Schema des Skills muss von der TASK.md bedient werden koennen

## Skill-Lifecycle

```
DISCOVERY ──> MATCHING ──> LOCKING ──> ACTIVATION ──> EXECUTION ──> AUDIT
     │            │           │            │              │           │
  Registry    Agent.skills  skills.lock  Vollstaendig   Agent     Chain-Log
  laden       abgleichen    erstellen    laden          arbeitet  (SKILL_CHANGED)
```
