# MissionForge

**Agent-Company-Spawner & Orchestrierungs-Engine für Claude**

MissionForge verwandelt beliebige Aufgabenbeschreibungen in vollständige Agent-Companies mit Orchestrator-Hierarchie, Sub-Orchestratoren, Skill-Zuordnung und lückenloser Aufgabenverfolgung. Exportiert bewährte Companies als wiederverwendbare Packages.

---

## Was MissionForge macht

Komplexe Aufgaben scheitern nicht an fehlender Intelligenz, sondern an fehlender Struktur. MissionForge liefert die Organisationsebene:

- **Company Spawning** — Aus einer Aufgabenbeschreibung entsteht eine vollständige Organisation mit Teams, Agenten, Rollen und Governance
- **Zero-Drop-Garantie** — Jede Anforderung wird erfasst, zugewiesen, eingeplant, ausgeführt und verifiziert. Nichts fällt durchs Raster
- **Wellenbasierte Ausführung** — Arbeitspakete werden nach Abhängigkeiten in parallele Wellen gruppiert, bis zu 3 Agenten gleichzeitig
- **Skill-Orchestrierung** — Vorhandene Skills werden automatisch erkannt und zugeordnet, fehlende on-the-fly generiert
- **Export als .skill** — Bewährte Companies werden als autarke, parametrisierbare Dateien exportiert
- **5-Ebenen-Verifikation** — Von der Einzelprüfung bis zum Qualitäts-Audit

---

## Installation

```bash
# Repository klonen
git clone https://github.com/GodModeAI2025/MissionForge.git

# Skill in dein Projekt kopieren
cp -r MissionForge/ .claude/skills/mission-forge/
```

Alternativ direkt in dein Home-Verzeichnis für globale Verfügbarkeit:

```bash
cp -r MissionForge/ ~/.claude/skills/mission-forge/
```

---

## Quickstart

### Company spawnen

Starte Claude und sage:

```
"Spawne eine Company für die Entwicklung einer REST-API mit Authentifizierung"
```

MissionForge durchläuft automatisch 9 Phasen:

1. **Aufgabenanalyse** — Primärziel, Erfolgskriterien und Arbeitspakete ableiten
2. **Company Spawnen** — Verzeichnisstruktur und Manifeste generieren
3. **Orchestrator-Hierarchie** — Mission-Orchestrator + Sub-Orchestratoren einsetzen
4. **Skill-Zuordnung** — Verfügbare Skills erkennen und Agenten zuordnen
5. **Wellenplanung** — Abhängigkeitsgraph erstellen, parallele Wellen planen
6. **Ausführung** — Welle für Welle mit frischem Kontext pro Agent
7. **Verifikation** — 5-Ebenen-Prüfung gegen Akzeptanzkriterien
8. **Abschluss** — Bericht und Dokumentation
9. **Export** — Optional als wiederverwendbare .skill-Datei

### .skill-Datei ausführen

```
"Führe api-development.skill aus für einen E-Commerce-Checkout-Service"
```

### Company exportieren

```
"Exportiere diese Company als .skill"
```

---

## Architektur

### 6 Manifest-Typen

| Manifest     | Zweck                                      | Datei        |
|--------------|--------------------------------------------|--------------|
| **COMPANY**  | Wurzel der Organisation, Ziele, Governance | `COMPANY.md` |
| **TEAM**     | Wiederverwendbarer Organisationsbaum       | `TEAM.md`    |
| **AGENT**    | Einzelne Rolle mit Anweisungen und Skills  | `AGENTS.md`  |
| **PROJECT**  | Geplante Arbeitsgruppierung                | `PROJECT.md` |
| **TASK**     | Atomare ausführbare Arbeitseinheit         | `TASK.md`    |
| **SKILL**    | Wiederverwendbare Fähigkeit                | `SKILL.md`   |

### Status-Werte

`OPEN` → `IN_PROGRESS` → `DONE` → `VERIFIED`

Bei Problemen: `FAILED` → `ESCALATED` → `SKIPPED` oder `ABORTED`

### Generierte Projektstruktur

```
.mission-forge/
  COMPANY.md              # Wurzel-Manifest
  STATE.md                # Live-Status aller Komponenten
  VERIFICATION.md         # Zero-Drop-Audit
  MISSION-REPORT.md       # Abschlussbericht
  teams/
    planung/              TEAM.md
    ausfuehrung/          TEAM.md
    verifikation/         TEAM.md
  agents/
    [agent-slug]/         AGENTS.md
  tasks/
    [wp-id]/              TASK.md
  skills/                 # Auto-generierte Skills
  results/
    wave-N-wp-XXX/        SUMMARY.md
```

---

## Skalierung

| Arbeitspakete | Struktur                                                   |
|---------------|-------------------------------------------------------------|
| 1–2           | Vereinfacht: Direkte Ausführung ohne Sub-Orchestrator       |
| 3–15          | Standard: 3 Teams (Planung, Ausführung, Verifikation)      |
| 16–25         | Erweitert: Mehrere Sub-Orchestratoren, ggf. 4 Teams        |
| 25+           | Aufteilen in mehrere Missionen mit eigener Company          |

---

## Projektstruktur des Skills

```
MissionForge/
  SKILL.md                             # Haupt-Skill-Datei (9 Phasen)
  index.html                           # Landing Page
  references/
    manifest-reference.md              # Vollständige Feld-Referenz
    communication-protocol.md          # Kommunikation zwischen Agenten
    error-handling.md                  # Fehlerbehandlung & Eskalation
    troubleshooting.md                 # Fehlerbehebung
    checklists.md                      # Checklisten für alle Phasen
  scripts/
    validate-mission.sh                # Validierungs-Script
  templates/
    company-template.md                # COMPANY.md Template
    team-template.md                   # TEAM.md Template
    agent-template.md                  # AGENTS.md Template
    project-template.md                # PROJECT.md Template
    task-template.md                   # TASK.md Template
    state-template.md                  # STATE.md Template
    verification-template.md           # VERIFICATION.md Template
    mission-report-template.md         # MISSION-REPORT.md Template
    exported-skill-template.md         # .skill Export Template
```

---

## Voraussetzungen

- **Claude Code** oder kompatible Agent-Runtime
- Tools: Bash, Read, Write, Edit, Agent
- Optional: Git (Versionierung), WebFetch (externe Skill-Discovery)

---

## Lizenz

MIT — siehe [LICENSE](LICENSE)

---

## Links

- **Landing Page**: [godmodeai2025.github.io/MissionForge](https://godmodeai2025.github.io/MissionForge/)
- **Repository**: [github.com/GodModeAI2025/MissionForge](https://github.com/GodModeAI2025/MissionForge)
- **Impressum**: [godmodeai2025.github.io/MarkZimmermann](https://godmodeai2025.github.io/MarkZimmermann/)
