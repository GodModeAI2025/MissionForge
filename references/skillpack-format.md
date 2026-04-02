# .skillpack Paketformat — Mission Forge

Inspiriert von claude-codes Tool-Plugin-Directories und dem MCP-Registry-Konzept.
Evolution von der monolithischen .skill-Datei zum strukturierten Paketformat.

---

## Problem

Die aktuelle `.skill`-Exportdatei (exported-skill-template.md) bakt alles
in eine einzelne Datei. Bei grossen Companies (10+ Agenten, 5+ Skills)
wird diese Datei unuebersichtlich und schwer wartbar.

## Zwei Formate

| Format      | Wann verwenden                    | Struktur           |
|-------------|-----------------------------------|---------------------|
| `.skill`    | Einfache Companies (1-5 Agenten) | Einzelne Datei      |
| `.skillpack`| Komplexe Companies (5+ Agenten)  | Verzeichnis-Paket   |

## .skillpack Verzeichnisstruktur

```
packages/
└── my-company.skillpack/
    ├── manifest.yaml            # Paket-Metadaten und Parameter
    ├── SKILL.md                 # Orchestrierungs-Anweisungen
    ├── README.md                # Dokumentation fuer Nutzer
    ├── agents/                  # Agenten-Definitionen
    │   ├── planner.md
    │   ├── implementer.md
    │   └── tester.md
    ├── skills/                  # Eingebettete Skills
    │   ├── code-review.md
    │   └── testing.md
    ├── templates/               # Wiederverwendbare Templates
    │   └── task-template.md
    ├── config/                  # Default-Konfiguration
    │   └── defaults.yaml
    └── meta/                    # Paket-Metadaten
        ├── origin.yaml          # Ursprungs-Mission
        └── changelog.md         # Aenderungshistorie
```

## manifest.yaml

```yaml
# Paket-Metadaten
name: my-company
version: "1.0.0"
description: "Beschreibung der Company"
author: "Mark Zimmermann"
license: MIT
created: "2026-04-02"
exported-from: "MISSION-2026-042"

# MissionForge Kompatibilitaet
min-missionforge: "4.0.0"
schema: missionforge/v1

# Parameter (ersetzbar beim Spawn)
parameters:
  AUFGABE:
    required: true
    description: "Konkrete Aufgabenbeschreibung"
  ZIEL:
    required: true
    description: "Primaerziel dieser Mission"
  MAX_AGENTS:
    required: false
    default: "3"
    description: "Max parallele Agenten"
  MODE:
    required: false
    default: "standard"
    description: "lite | standard | enterprise"

# Inhalt
agents:
  - agents/planner.md
  - agents/implementer.md
  - agents/tester.md
skills:
  - skills/code-review.md
  - skills/testing.md
templates:
  - templates/task-template.md

# Trigger-Woerter
triggers:
  - "my-company aktivieren"
  - "keyword1"
  - "keyword2"

# Validierung
checksums:
  SKILL.md: "sha256:abc123..."
  agents/planner.md: "sha256:def456..."
  agents/implementer.md: "sha256:ghi789..."
```

## origin.yaml

Dokumentiert die Herkunft des Pakets:

```yaml
mission: "MISSION-2026-042"
exported: "2026-04-02T14:30:00Z"
mission-status: VERIFIED
chain-hash: "sha256:final_chain_hash..."
chain-intact: true
total-waves: 3
total-wps: 8
success-rate: "100%"
lessons-learned:
  - "Parallele API-Calls auf max 3 begrenzen"
  - "Testing-Agent braucht read-Zugriff auf config/"
```

## Pack & Unpack Befehle

### Pack (Export als .skillpack)

```bash
python scripts/pack-skillpack.py .mission-forge --output packages/my-company.skillpack
```

Schritte:
1. Validiere Mission-Status (muss VERIFIED sein)
2. Extrahiere Agenten-Definitionen (ohne mission-spezifische Daten)
3. Extrahiere verwendete Skills
4. Ersetze aufgabenspezifische Werte durch Parameter-Platzhalter
5. Generiere manifest.yaml mit Checksums
6. Kopiere origin.yaml aus Mission-Metadaten
7. Generiere README.md

### Unpack (Spawn aus .skillpack)

```bash
python scripts/unpack-skillpack.py packages/my-company.skillpack \
    --param AUFGABE="Neue API bauen" \
    --param ZIEL="REST-API mit 5 Endpunkten"
```

Schritte:
1. Validiere Checksums
2. Erstelle .mission-forge/ Verzeichnis
3. Ersetze Parameter-Platzhalter
4. Generiere COMPANY.md, STATE.md
5. Kopiere Agenten und Skills
6. Fuehre Pre-Flight-Check aus

## Versionierung

```yaml
# changelog.md
## 1.1.0 (2026-04-15)
- Neuer Agent: Security-Reviewer
- Testing-Skill: Abdeckung von 80% auf 90% erhoeht

## 1.0.0 (2026-04-02)
- Initiale Version aus MISSION-2026-042
```

## Registry-Integration

Exportierte .skillpack-Pakete koennen in einer zentralen Registry
registriert werden:

```json
{
  "packages": [
    {
      "name": "api-builder",
      "version": "1.2.0",
      "description": "Baut REST-APIs mit Tests und Dokumentation",
      "path": "packages/api-builder.skillpack",
      "hash": "sha256:...",
      "downloads": 12,
      "rating": 4.5
    }
  ]
}
```
