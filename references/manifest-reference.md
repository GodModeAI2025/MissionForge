# Manifest-Referenz — Mission Forge

Vollstaendige Frontmatter-Referenz fuer alle 6 Manifest-Typen des Agent Companies Standards,
angepasst fuer Mission Forge.

---

## 1. COMPANY.md — Frontmatter

| Feld                    | Status     | Typ      | Beschreibung                                              |
|-------------------------|------------|----------|-----------------------------------------------------------|
| `schema`                | Required   | string   | `missionforge/v1`                                       |
| `kind`                  | Required   | string   | `company`                                                 |
| `slug`                  | Required   | string   | URL-sicherer Identifier, stabil ueber Versionen           |
| `name`                  | Required   | string   | Menschenlesbarer Name der Mission/Company                 |
| `description`           | Required   | string   | Wann aktivieren? Was entscheidet diese Company?            |
| `version`               | Recommended| string   | SemVer, z.B. `"1.0.0"`                                   |
| `license`               | Optional   | string   | Lizenz oder Verweis auf LICENSE.txt                        |
| `authors`               | Optional   | list     | Ersteller der Company                                     |
| `tags`                  | Recommended| list     | Klassifikation: Domain, Capability, Kontext               |
| `metadata`              | Optional   | map      | Beliebige Schluessel-Wert-Paare                           |
| `metadata.created`      | Recommended| string   | ISO-8601 Erstellungsdatum                                 |
| `metadata.source-task`  | Recommended| string   | Gekuerzte Ursprungsaufgabe                                |
| `metadata.priority`     | Optional   | string   | `critical`, `high`, `medium`, `low`                       |
| `metadata.sources`      | Optional   | list     | Externe Referenzen mit Provenienz (repo, sha, hash)       |

### Body-Struktur

```markdown
# [Company-Name]

## Mission Statement
[1-3 Saetze]

## Ziele
1. [Messbar]
2. ...

## Governance
- Eskalationspfad
- Entscheidungsautoritaet
- Quality Gates

## Includes
- teams/[name]/TEAM.md
- ...
```

---

## 2. TEAM.md — Frontmatter

| Feld          | Status     | Typ    | Beschreibung                                    |
|---------------|------------|--------|-------------------------------------------------|
| `schema`      | Required   | string | `missionforge/v1`                             |
| `kind`        | Required   | string | `team`                                          |
| `slug`        | Required   | string | Stabiler Identifier                             |
| `name`        | Required   | string | Team-Name                                       |
| `description` | Required   | string | Wann aktivieren? Welche Entscheidungen?          |
| `manager`     | Required   | string | Pfad zum Sub-Orchestrator AGENTS.md             |
| `includes`    | Required   | map    | `agents:` und `skills:` Listen                  |
| `tags`        | Optional   | list   | Klassifikation                                  |
| `metadata`    | Optional   | map    | Beliebige Schluessel-Wert-Paare                 |

### Body-Struktur

```markdown
# Team [Name]

## Verantwortungsbereich
[Klare Abgrenzung]

## Arbeitsweise
[Interne Koordination]

## Eskalationsregeln
[Wann eskaliert der Manager?]
```

---

## 3. AGENTS.md — Frontmatter

| Feld                        | Status     | Typ    | Beschreibung                               |
|-----------------------------|------------|--------|--------------------------------------------|
| `schema`                    | Required   | string | `missionforge/v1`                        |
| `kind`                      | Required   | string | `agent`                                    |
| `slug`                      | Required   | string | Stabiler Identifier                        |
| `name`                      | Required   | string | Rollenname                                 |
| `description`               | Required   | string | Wann aktivieren? Was tut dieser Agent?      |
| `reports-to`                | Required   | string | Pfad zum uebergeordneten Agent/Orchestrator|
| `skills`                    | Recommended| list   | Shortnames zugewiesener Skills             |
| `tags`                      | Optional   | list   | Capability-Tags                            |
| `metadata`                  | Optional   | map    | Beliebige Schluessel-Wert-Paare            |
| `metadata.model-preference` | Recommended| string | `opus`, `sonnet`, `haiku`                  |
| `metadata.max-context-usage`| Optional   | string | Maximale Context-Nutzung, z.B. `"60%"`     |
| `metadata.tools-allowed`    | Recommended| string | Erlaubte Tools (Least Privilege)           |
| `metadata.read-only`        | Optional   | bool   | `true` fuer Checker/Pruefer-Rollen         |

### Body-Struktur

```markdown
# [Rollenname]

## Kernauftrag
[1-2 Saetze]

## Anweisungen
1. [Konkret]
2. [Pruefbar]

## Input
- [Erwartete Eingaben]

## Output
- [Erwartete Ergebnisse mit Format und Speicherort]

## Abgrenzung
- Tut NICHT: [Explizite Ausschluesse]
- Bei Unklarheit: Eskaliere an [reports-to]

## Qualitaetskriterien
- [ ] [Pruefbar]
```

---

## 4. PROJECT.md — Frontmatter

| Feld          | Status     | Typ    | Beschreibung                                    |
|---------------|------------|--------|-------------------------------------------------|
| `schema`      | Required   | string | `missionforge/v1`                             |
| `kind`        | Required   | string | `project`                                       |
| `slug`        | Required   | string | Stabiler Identifier                             |
| `name`        | Required   | string | Projektname                                     |
| `description` | Required   | string | Projektziel und Kontext                          |
| `status`      | Recommended| string | `PLANNED`, `IN_PROGRESS`, `DONE`                 |
| `tags`        | Optional   | list   | Klassifikation                                  |
| `metadata`    | Optional   | map    | Beliebige Schluessel-Wert-Paare                 |

### Body-Struktur

```markdown
# Projekt: [Name]

## Ziel
[Was soll erreicht werden?]

## Scope
[Was gehoert dazu, was nicht]

## Arbeitspakete
- WP-001: [Titel]
- WP-002: [Titel]

## Timeline
[Wellen-Zuordnung oder Meilensteine]
```

---

## 5. TASK.md — Frontmatter

| Feld                  | Status     | Typ    | Beschreibung                                 |
|-----------------------|------------|--------|----------------------------------------------|
| `schema`              | Required   | string | `missionforge/v1`                          |
| `kind`                | Required   | string | `task`                                       |
| `slug`                | Required   | string | Stabiler Identifier, z.B. `wp-001`           |
| `name`                | Required   | string | Aufgabentitel                                |
| `description`         | Required   | string | Was muss getan werden?                        |
| `assigned-to`         | Required   | string | Pfad zum zugewiesenen Agent                  |
| `status`              | Required   | string | `OPEN`, `IN_PROGRESS`, `DONE`, `FAILED`, `VERIFIED` |
| `priority`            | Recommended| string | `critical`, `high`, `medium`, `low`          |
| `wave`                | Required   | int    | Wellen-Nummer fuer Scheduling                |
| `depends-on`          | Optional   | list   | Liste von TASK-Slugs                         |
| `requirements`        | Required   | list   | Liste von REQ-IDs die abgedeckt werden       |
| `tags`                | Optional   | list   | Klassifikation                               |
| `metadata`            | Optional   | map    | Beliebige Schluessel-Wert-Paare              |
| `metadata.estimated`  | Optional   | string | Geschaetzte Komplexitaet: S/M/L/XL           |

### Body-Struktur

```markdown
# Task: [Titel]

## Ziel
[Was ist das konkrete Ergebnis?]

## Akzeptanzkriterien
- [ ] [Pruefbar 1]
- [ ] [Pruefbar 2]

## Zu lesende Dateien (read_first)
- [Pfad 1]
- [Pfad 2]

## Anweisungen
1. [Schritt 1]
2. [Schritt 2]

## Ergebnis-Format
- Datei: [Pfad wohin das Ergebnis geschrieben wird]
- Format: [Markdown / JSON / Code / etc.]
```

---

## 6. SKILL.md — Frontmatter (Agent Skills Standard)

| Feld            | Status   | Typ    | Beschreibung                                       |
|-----------------|----------|--------|----------------------------------------------------|
| `name`          | Required | string | 1-64 Zeichen, lowercase, a-z und Bindestriche      |
| `description`   | Required | string | 1-1024 Zeichen. Was tut der Skill? Wann aktivieren? |
| `license`       | Optional | string | Lizenzname oder Verweis                            |
| `compatibility` | Optional | string | 1-500 Zeichen. Umgebungsanforderungen               |
| `metadata`      | Optional | map    | Beliebige Schluessel-Wert-Paare                    |
| `allowed-tools` | Optional | string | Space-delimited Tool-Liste (experimentell)          |

### Validierungsregeln fuer `name`

- Nur lowercase a-z, Ziffern, Bindestriche
- Kein Start/Ende mit Bindestrich
- Keine doppelten Bindestriche
- Muss mit Verzeichnisname uebereinstimmen
- Max 64 Zeichen

### Body-Struktur

```markdown
# [Skill-Name]

## Wann verwenden
[Trigger-Beschreibung]

## Anweisungen
[Schritt-fuer-Schritt]

## Validierung
[Wie prueft man korrektes Ergebnis?]
```

---

## Verzeichniskonventionen

```
.mission-forge/
├── COMPANY.md
├── STATE.md
├── VERIFICATION.md
├── MISSION-REPORT.md
├── teams/
│   └── [team-slug]/
│       └── TEAM.md
├── agents/
│   └── [agent-slug]/
│       └── AGENTS.md
├── projects/
│   └── [project-slug]/
│       └── PROJECT.md
├── tasks/
│   └── [task-slug]/
│       └── TASK.md
├── skills/
│   └── [skill-name]/
│       ├── SKILL.md
│       ├── scripts/
│       ├── references/
│       └── assets/
├── results/
│   └── wave-[N]-[wp-id]/
│       └── SUMMARY.md
└── references/
    └── [zusaetzliche-docs].md
```

---

## Progressive Disclosure — Token-Budget

| Stufe       | Was geladen wird                    | Token-Kosten pro Einheit |
|-------------|-------------------------------------|--------------------------|
| Katalog     | kind + name + slug + description    | ~50-100                  |
| Aktivierung | Vollstaendiger Manifest-Body        | ~500-5000                |
| Ressourcen  | Scripts, References, Assets         | Variabel                 |

**Regel**: Katalog-Stufe immer zuerst. Aktivierung nur bei Bedarf. Ressourcen nur bei Ausfuehrung.
