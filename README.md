# MissionForge

**Agent-Company-Spawner & Orchestrierungs-Engine für Claude**

MissionForge verwandelt beliebige Aufgabenbeschreibungen in vollständige Agent-Companies mit Orchestrator-Hierarchie, Sub-Orchestratoren, Skill-Zuordnung und lückenloser Aufgabenverfolgung. Revisionssicher durch kryptographische Hash-Chain (AuditChain). Exportiert bewährte Companies als wiederverwendbare Packages.

---

## Was MissionForge macht

Komplexe Aufgaben scheitern nicht an fehlender Intelligenz, sondern an fehlender Struktur. MissionForge liefert die Organisationsebene:

- **Company Spawning** — Aus einer Aufgabenbeschreibung entsteht eine vollständige Organisation mit Teams, Agenten, Rollen und Governance
- **Zero-Drop-Garantie** — Jede Anforderung wird erfasst, zugewiesen, eingeplant, ausgeführt und verifiziert. Nichts fällt durchs Raster
- **Wellenbasierte Ausführung** — Arbeitspakete werden nach Abhängigkeiten in parallele Wellen gruppiert, bis zu 3 Agenten gleichzeitig
- **Skill-Orchestrierung** — Vorhandene Skills werden automatisch erkannt und zugeordnet, fehlende on-the-fly generiert
- **AuditChain** — Kryptographische SHA-256-Hash-Chain für revisionssichere Nachvollziehbarkeit jeder Agent-Entscheidung
- **Monte-Carlo-Modus** — Kritische Tasks mehrfach mit Variationen ausführen, statistisch bestes Ergebnis wählen
- **Export als .skill** — Bewährte Companies werden als autarke, parametrisierbare Dateien exportiert
- **6-Ebenen-Verifikation** — Von der Einzelprüfung bis zur kryptographischen Integritätsprüfung

---

## Was ist neu in v4.0.0

### AuditChain — Revisionssicherheit für Agent-Orchestrierung

Jeder Zustandswechsel in einer Mission wird als verketteter SHA-256-Hash-Eintrag protokolliert. Manipulation eines Eintrags bricht die Kette — sofort erkennbar, nicht rückgängig machbar.

```bash
# Chain prüfen
python audit/verify.py .mission-forge/audit/CHAIN.jsonl

# Vollständigen Audit-Report generieren
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --report
```

**Warum das wichtig ist:** Wenn KI-Agenten geschäftskritische Entscheidungen treffen, brauchen regulierte Branchen (Energie, Banken, Pharma) den Nachweis: Welcher Agent hat wann was entschieden, und wurde nachträglich nichts verändert.

### Monte-Carlo-Modus

Kritische Tasks werden N-mal mit variierten Parametern ausgeführt. Alle Varianten werden bewertet, das beste Ergebnis ausgewählt — und alle Varianten in der AuditChain dokumentiert.

```yaml
# In COMPANY.md aktivieren
execution:
  monte_carlo: true
  mc_variants: 3
  mc_selection: best_score
```

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
2. **Company Spawnen** — Verzeichnisstruktur, Manifeste und AuditChain Genesis-Block generieren
3. **Orchestrator-Hierarchie** — Mission-Orchestrator + Sub-Orchestratoren einsetzen
4. **Skill-Zuordnung** — Verfügbare Skills erkennen und Agenten zuordnen
5. **Wellenplanung** — Abhängigkeitsgraph erstellen, parallele Wellen planen und versiegeln
6. **Ausführung** — Welle für Welle mit frischem Kontext pro Agent, Auto-Logging in AuditChain
7. **Verifikation** — 6-Ebenen-Prüfung gegen Akzeptanzkriterien + Chain-Integritätsprüfung
8. **Abschluss** — Bericht, Dokumentation und Chain-Versiegelung
9. **Export** — Optional als wiederverwendbare .skill-Datei

### .skill-Datei ausführen

```
"Führe api-development.skill aus für einen E-Commerce-Checkout-Service"
```

### Company exportieren

```
"Exportiere diese Company als .skill"
```

### Revisionssicherheit prüfen

```bash
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --report
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

### AuditChain Events

| Event | Wann | Phase |
|---|---|---|
| `GENESIS` | Company wird gespawnt | 2 |
| `WAVE_PLAN_SEALED` | Wellenplan freigegeben | 5 |
| `TASK_STATUS_CHANGE` | Jeder Statuswechsel | 6 |
| `MONTE_CARLO_VARIANT` | MC-Variante ausgeführt | 6 |
| `MONTE_CARLO_SELECTED` | MC-Auswahl getroffen | 6 |
| `VERIFICATION_PASSED` | Verifikation bestanden | 7 |
| `VERIFICATION_FAILED` | Verifikation gescheitert | 7 |
| `CHAIN_SEALED` | Mission abgeschlossen | 8 |

### Generierte Projektstruktur

```
.mission-forge/
  COMPANY.md              # Wurzel-Manifest
  STATE.md                # Live-Status aller Komponenten
  VERIFICATION.md         # Zero-Drop-Audit + Chain-Integritätsbericht
  MISSION-REPORT.md       # Abschlussbericht mit Revisionssicherheit
  audit/                  # AuditChain (NEU in v4.0.0)
    CHAIN.jsonl           # Kryptographische Hash-Chain
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

## AuditChain API

### Python

```python
from audit.chain import AuditChain

ac = AuditChain(".mission-forge/audit")

# Genesis-Block (einmal pro Mission)
ac.genesis("MISSION-2026-042", goals=["API bauen"], actors=["agent-alpha"])

# Events loggen
ac.log("TASK_STATUS_CHANGE", ref="WP-001", agent="agent-alpha",
       data={"from": "OPEN", "to": "DONE"})

# Chain versiegeln
ac.seal("MISSION-2026-042")

# Integrität prüfen
intact, errors = ac.verify()

# Report generieren
report = ac.generate_integrity_report()
```

### CLI

```bash
python audit/chain.py genesis  .mission-forge/audit MISSION-ID
python audit/chain.py log      .mission-forge/audit TASK_STATUS_CHANGE WP-001 from=OPEN to=DONE
python audit/chain.py verify   .mission-forge/audit
python audit/chain.py summary  .mission-forge/audit
python audit/chain.py seal     .mission-forge/audit MISSION-ID
```

### Standalone Verifier (für Auditoren)

```bash
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --verbose
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --report > audit_report.md
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
  audit/                               # AuditChain (NEU in v4.0.0)
    chain.py                           # Hash-Chain-Engine
    verify.py                          # Standalone-Verifier für Auditoren
    test_demo.py                       # Demo & Selbsttest
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
- **Python 3.10+** für AuditChain (keine externen Dependencies)
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
