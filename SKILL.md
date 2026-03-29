---
name: mission-forge
description: >
  Spawnt vollstaendige Agent-Companies aus beliebigen Aufgabenbeschreibungen mit
  Orchestrator-Hierarchie, Sub-Orchestratoren, Skill-Zuordnung und lueckenloser
  Aufgabenverfolgung. Exportiert abgeschlossene Companies als wiederverwendbare
  Packages. Trigger: "company spawnen", "organisation erstellen", "aufgabe
  orchestrieren", "ablauforganisation", "mission starten", "nichts vergessen",
  "skill-organisation", "multi-agent", "task-force", "projekt-orchestrierung",
  "company exportieren", "package erstellen", "company wiederverwenden".
license: MIT
compatibility: >
  Designed for Claude Code and compatible agent runtimes.
  Requires Bash, Read, Write, Edit, Agent tools.
  Optional: Git for versioning, WebFetch for external skill discovery.
metadata:
  author: skillorga
  version: "3.0.0"
  schema: missionforge/v1
  kind: skill
  tags: orchestration, company-spawning, multi-agent, task-management, workflow, export
allowed-tools: Bash Read Write Edit Agent Glob Grep TaskCreate TaskUpdate TaskGet TaskList
---

# Mission Forge — Agent-Company-Spawner & Orchestrierungs-Engine

> Verwandelt jede Aufgabe in eine lebende Organisation aus spezialisierten Agenten
> mit garantierter Vollstaendigkeit, Nachverfolgbarkeit und Qualitaetssicherung.
> Exportiert bewährte Companies als wiederverwendbare Packages.

---

## Inhaltsverzeichnis

1. [Wann verwenden](#1-wann-verwenden)
2. [Kernkonzepte](#2-kernkonzepte)
3. [Phase 1 — Aufgabenanalyse & Zerlegung](#3-phase-1--aufgabenanalyse--zerlegung)
4. [Phase 2 — Company spawnen](#4-phase-2--company-spawnen)
5. [Phase 3 — Orchestrator-Hierarchie](#5-phase-3--orchestrator-hierarchie)
6. [Phase 4 — Skill-Zuordnung](#6-phase-4--skill-zuordnung)
7. [Phase 5 — Wellenplanung](#7-phase-5--wellenplanung)
8. [Phase 6 — Ausfuehrung](#8-phase-6--ausfuehrung)
9. [Phase 7 — Verifikation](#9-phase-7--verifikation)
10. [Phase 8 — Abschluss](#10-phase-8--abschluss)
11. [Phase 9 — Export & Wiederverwendung](#11-phase-9--export--wiederverwendung)
12. [Referenzen](#12-referenzen)

---

## 1. Wann verwenden

Aktiviere Mission Forge wenn:

- Eine **komplexe Aufgabe** mehrere Arbeitsschritte, Skills oder Perspektiven erfordert
- **Mehrere Skills** orchestriert werden muessen ohne dass etwas vergessen wird
- Eine **Ablauforganisation** mit klaren Verantwortlichkeiten gebraucht wird
- Eine **wiederverwendbare Organisationsstruktur** fuer wiederkehrende Aufgabentypen entstehen soll

**Nicht verwenden** fuer triviale Einzel-Tasks die in unter 2 Minuten erledigt sind.

---

## 2. Kernkonzepte

### 2.1 Die 6 Manifest-Typen (Agent Companies Standard)

| Manifest     | Zweck                                      | Datei        |
|--------------|--------------------------------------------|--------------|
| **COMPANY**  | Wurzel der Organisation, Ziele, Governance | `COMPANY.md` |
| **TEAM**     | Wiederverwendbarer Organisationsbaum       | `TEAM.md`    |
| **AGENT**    | Einzelne Rolle mit Anweisungen und Skills  | `AGENTS.md`  |
| **PROJECT**  | Geplante Arbeitsgruppierung                | `PROJECT.md` |
| **TASK**     | Atomare ausfuehrbare Arbeitseinheit        | `TASK.md`    |
| **SKILL**    | Wiederverwendbare Faehigkeit               | `SKILL.md`   |

Vollstaendige Feld-Referenz: [references/manifest-reference.md](references/manifest-reference.md)

### 2.2 Progressive Disclosure (3 Stufen)

1. **Katalog** — Nur Name + Beschreibung laden (~100 Token pro Einheit)
2. **Aktivierung** — Vollstaendige Manifeste bei Bedarf laden
3. **Ressourcen** — Scripts, Referenzen, Assets nur bei Ausfuehrung

### 2.3 Status-Werte (einheitlich in allen Dateien)

| Status        | Bedeutung                                          |
|---------------|-----------------------------------------------------|
| `OPEN`        | Noch nicht begonnen                                 |
| `IN_PROGRESS` | Agent arbeitet daran                                |
| `DONE`        | Agent hat Ergebnis geliefert                        |
| `VERIFIED`    | Ergebnis gegen Akzeptanzkriterien geprueft, bestanden|
| `FAILED`      | Reparatur-Versuche erschoepft                       |
| `ESCALATED`   | An hoehere Ebene eskaliert                          |
| `SKIPPED`     | Bewusst ausgelassen (mit Begruendung)               |
| `ABORTED`     | Mission vorzeitig beendet                           |

### 2.4 Prioritaeten (einheitlich)

| Prioritaet | Verwendung                          |
|------------|--------------------------------------|
| `critical` | Blocker, ohne dies geht nichts weiter|
| `high`     | Kernfunktionalitaet                  |
| `medium`   | Wichtig aber nicht blockierend       |
| `low`      | Nice-to-have                         |

### 2.5 Vollstaendigkeitsgarantie (Zero-Drop-Prinzip)

Jede Anforderung muss:
1. In mindestens einer TASK.md erfasst sein (Traceability)
2. Einem Agenten zugewiesen sein (Ownership)
3. In einer Welle eingeplant sein (Scheduling)
4. Nach Ausfuehrung verifiziert sein (Verification)
5. Im Abschlussbericht dokumentiert sein (Documentation)

Fehlt ein Schritt, blockiert die Pipeline.

---

## 3. Phase 1 — Aufgabenanalyse & Zerlegung

### Schritt 1.1: Aufgabe verstehen

Lies die Aufgabenbeschreibung und extrahiere:

- **Primaerziel**: Was ist das uebergeordnete Ziel?
- **Erfolgskriterien**: Pruefbare Bedingungen fuer "fertig"
- **Lieferobjekte**: Konkret benennbare Ergebnisse
- **Randbedingungen**: Zeitlich, technisch, qualitativ
- **Offene Fragen**: Was muss geklaert werden bevor die Arbeit beginnt?

### Schritt 1.2: Anforderungen ableiten

Fuer jedes Erfolgskriterium erstelle eine Anforderung:

```
REQ-001: [Kurztitel]
  Beschreibung: [Was genau muss erreicht werden]
  Akzeptanzkriterium: [Pruefbar formuliert]
  Prioritaet: critical | high | medium | low
  Abhaengigkeiten: [REQ-IDs oder "keine"]
```

### Schritt 1.3: Arbeitspakete schneiden

Zerlege Anforderungen in atomare Arbeitspakete:

| WP-ID  | Titel   | Anforderungen | Komplexitaet | Abhaengigkeiten |
|--------|---------|---------------|--------------|-----------------|
| WP-001 | [Titel] | REQ-001       | S/M/L/XL     | keine           |
| WP-002 | [Titel] | REQ-002, 003  | M            | WP-001          |

**Validierung**: Jede REQ-ID muss in mindestens einem WP erscheinen.

---

## 4. Phase 2 — Company spawnen

Erstelle die `.mission-forge/` Verzeichnisstruktur. Verwende die Templates aus `templates/` als Basis:

### 4.1 Company-Manifest

Erstelle `.mission-forge/COMPANY.md` basierend auf [templates/company-template.md](templates/company-template.md).

### 4.2 Team-Manifeste

Fuer jedes Team erstelle `.mission-forge/teams/[team-name]/TEAM.md` basierend auf [templates/team-template.md](templates/team-template.md).

Standard-Teams:
- **Planung** — Anforderungsanalyse, Architektur, Risikobewertung
- **Ausfuehrung** — Implementierung, Integration
- **Verifikation** — Pruefung, Abnahme, Dokumentation

### 4.3 Agenten-Manifeste

Fuer jeden Agenten erstelle `.mission-forge/agents/[agent-slug]/AGENTS.md` basierend auf [templates/agent-template.md](templates/agent-template.md).

### 4.4 Task-Manifeste

Fuer jedes WP erstelle `.mission-forge/tasks/[wp-id]/TASK.md` basierend auf [templates/task-template.md](templates/task-template.md).

---

## 5. Phase 3 — Orchestrator-Hierarchie

### 5.1 Mission-Orchestrator (Root)

Der einzige Agent der die gesamte Mission ueberblickt.

**Ablauf:**
1. Lade COMPANY.md und alle Team-Manifeste (Katalog-Stufe)
2. Erstelle STATE.md basierend auf [templates/state-template.md](templates/state-template.md)
3. Validiere: Alle REQs haben zugehoerige WPs
4. Delegiere an Sub-Orchestratoren in Reihenfolge: Planung -> Ausfuehrung -> Verifikation
5. Pruefe nach jeder Welle die Vollstaendigkeit
6. Eskaliere Blocker an den User

### 5.2 Sub-Orchestratoren

Jeder erhaelt einen **frischen Kontext** mit nur den fuer seine Phase relevanten Informationen.

| Sub-Orchestrator | Input                                | Output                              |
|------------------|--------------------------------------|--------------------------------------|
| **Planung**      | COMPANY.md, REQs, WPs               | Ausfuehrungsplan mit Wellenplanung   |
| **Ausfuehrung**  | Plan, zugewiesene WPs pro Welle      | Erledigte WPs mit Artefakten         |
| **Verifikation** | Erledigte WPs, Akzeptanzkriterien    | Verifikationsbericht, offene Maengel |

### 5.3 Kommunikation

**Ausschliesslich ueber Dateien** im `.mission-forge/` Verzeichnis. Kein Agent kommuniziert direkt mit einem anderen. Der Orchestrator liest Ergebnisdateien und leitet relevante Teile weiter. Siehe [references/communication-protocol.md](references/communication-protocol.md).

---

## 6. Phase 4 — Skill-Zuordnung

### 6.1 Skill-Discovery

Durchsuche vorhandene Skills in dieser Reihenfolge (erster Treffer gewinnt):

1. **Projekt-Skills**: `./.claude/skills/`, `./.agents/skills/`
2. **User-Skills**: `~/.claude/skills/`, `~/.agents/skills/`
3. **Company-eigene Skills**: `.mission-forge/skills/`
4. **Externe Skills**: Via `metadata.sources` in Manifesten

Lade nur Name + Beschreibung (Katalog-Stufe). Bei Kollisionen: Warnung loggen.

### 6.2 Skill-Matching

Fuer jeden Agenten:
1. Extrahiere benoetigte Faehigkeiten aus AGENTS.md
2. Matche gegen verfuegbare Skills (Beschreibung, Tags, Trigger-Woerter)
3. Weise per Shortname zu: `skills: [code-review, testing]`
4. Falls kein Skill existiert: Erstelle unter `.mission-forge/skills/[name]/SKILL.md`

### 6.3 Trust fuer externe Skills

- **Projekt-Skills** aus trusted Repos: ohne Pruefung nutzbar
- **Externe Skills**: Provenienz pruefen (metadata.sources mit SHA), Lizenz, ausfuehrbare Scripts -> Warnung
- Im Zweifel: nur mit expliziter User-Freigabe aktivieren

---

## 7. Phase 5 — Wellenplanung

### 7.1 Abhaengigkeitsgraph

Analysiere WP-Abhaengigkeiten als DAG. Pruefe auf Zyklen.

### 7.2 Wellen zuordnen

Gruppiere unabhaengige WPs in parallele Wellen:

| Welle | Arbeitspakete        | Parallelitaet | Vorbedingung          |
|-------|----------------------|---------------|-----------------------|
| 1     | WP-001, WP-002, 003 | 3 parallel    | keine                 |
| 2     | WP-004               | 1 sequenziell | Welle 1 abgeschlossen |

### 7.3 Agenten zuordnen

| Welle | WP     | Agent                | Skills               | Model  |
|-------|--------|----------------------|----------------------|--------|
| 1     | WP-001 | implementierer-alpha | code-review, testing | sonnet |

### 7.4 Pre-Flight-Check

- [ ] Jedes WP genau einer Welle zugeordnet
- [ ] Keine Welle referenziert ein WP aus einer spaeteren Welle
- [ ] Jedes WP hat zugewiesenen Agenten
- [ ] Alle Skills verfuegbar
- [ ] Abhaengigkeitsgraph azyklisch
- [ ] Jede REQ durch mindestens ein WP abgedeckt

**Zeige dem User den vollstaendigen Plan mit Traceability-Matrix. Keine Ausfuehrung ohne Freigabe.**

---

## 8. Phase 6 — Ausfuehrung

### 8.1 Wellenausfuehrung

Fuer jede Welle:

1. **Vorbereitung**: Manifeste laden, Vorbedingungen pruefen, STATE.md aktualisieren
2. **Parallele Ausfuehrung**: Agenten spawnen (max 3 concurrent), jeder in frischem Kontext
3. **Ergebnis-Sammlung**: Jeder Agent schreibt `.mission-forge/results/wave-N-wp-XXX/SUMMARY.md`
4. **Wellen-Verifikation**: Gegen Akzeptanzkriterien pruefen, bei Fehler Reparatur (max 2 Versuche)
5. **Gate-Check**: Alle DONE? -> Naechste Welle. FAILED? -> Eskalation

### 8.2 Frischer Kontext pro Agent

Jeder Agent erhaelt NUR: sein AGENTS.md, seine TASK.md, aktivierte Skills, STATE.md (read-only), Dateien aus `read_first`. NICHT den gesamten Company-Kontext.

Einmal aktivierte Manifeste und Skills duerfen waehrend der Task-Ausfuehrung nicht aus dem Kontext entfernt werden.

### 8.3 Fehlerbehandlung

Agent Fehler -> Reparatur-Versuch 1 -> Reparatur-Versuch 2 -> Eskalation Sub-Orchestrator -> Eskalation Mission-Orchestrator -> Eskalation User (entscheidet: Ueberspringen / Manuell / Abbrechen).

Siehe [references/error-handling.md](references/error-handling.md) fuer Details.

### 8.4 Skalierung

| WP-Anzahl | Struktur                                                          |
|-----------|-------------------------------------------------------------------|
| 1-2       | Vereinfacht: Kein Sub-Orchestrator, direkte Ausfuehrung          |
| 3-15      | Standard: 3 Teams (Planung, Ausfuehrung, Verifikation)           |
| 16-25     | Erweitert: Mehrere Sub-Orchestratoren, ggf. 4 Teams              |
| 25+       | Aufteilen in mehrere Missionen mit eigener Company pro Teilbereich|

---

## 9. Phase 7 — Verifikation

### 9.1 Fuenf-Ebenen-Verifikation

| Ebene | Prueft                               | Agent                    |
|-------|--------------------------------------|--------------------------|
| 1     | Einzelnes WP: Akzeptanzkriterien     | Abnahme-Tester           |
| 2     | Welle: Integration der WP-Ergebnisse | Integrations-Pruefer     |
| 3     | Phase: Alle Wellen kohaerent         | Sub-Orch. Verifikation   |
| 4     | Mission: Alle REQs erfuellt          | Vollstaendigkeits-Pruefer|
| 5     | Qualitaet: Nicht-funktionale Kriterien| Qualitaets-Sicherer     |

### 9.2 Zero-Drop-Audit

Pruefe fuer JEDE REQ-ID: WP zugeordnet? Ausgefuehrt? Akzeptanzkriterium geprueft? Dokumentiert?

Suche nach Luecken: REQs ohne WP, WPs ohne Agent, WPs ohne Ergebnis, Agenten ohne Report, Skills ohne Aktivierung.

Erstelle `.mission-forge/VERIFICATION.md` basierend auf [templates/verification-template.md](templates/verification-template.md).

---

## 10. Phase 8 — Abschluss

### 10.1 Abschlussbericht

Erstelle `.mission-forge/MISSION-REPORT.md` basierend auf [templates/mission-report-template.md](templates/mission-report-template.md).

### 10.2 Missions-Abbruch

Falls vorzeitig beendet: Status `ABORTED` in STATE.md, Grund im Entscheidungslog, partieller Report. Bereits abgeschlossene Ergebnisse bleiben erhalten.

---

## 11. Phase 9 — Export als autarke .skill Datei

### 11.1 Wann exportieren

Exportiere eine Company wenn:
- Die Mission erfolgreich abgeschlossen wurde (VERIFIED)
- Die Aufgabe wiederkehrend ist und kuenftig reproduzierbar abgearbeitet werden soll
- Die Organisationsstruktur, Agenten und Skills als Blaupause dienen sollen

### 11.2 Was ist eine .skill Datei?

Eine `.skill` Datei ist eine **vollstaendig autarke, selbstausfuehrende Datei** die alles enthaelt:

- Komplette Orchestrierungslogik (Mission-Orchestrator + Sub-Orchestratoren)
- Alle Agenten-Definitionen mit Rollen und Anweisungen
- Alle Team-Strukturen mit Eskalationsregeln
- Alle Skills die die Agenten benoetigen
- Wellenplanung und Abhaengigkeitslogik
- Verifikations- und Qualitaetssicherungsregeln
- Konfigurierbare Parameter fuer neue Aufgaben

**Eine .skill Datei reicht aus um die gesamte Company zu spawnen und die Aufgabe abzuarbeiten.**

### 11.3 Export-Prozess

**Schritt 1: Analysiere die abgeschlossene Mission**

Lies COMPANY.md, alle TEAM.md, AGENTS.md, TASK.md, verwendete Skills, STATE.md und MISSION-REPORT.md. Extrahiere:

- Welche Team-Struktur hat funktioniert?
- Welche Agenten-Rollen waren noetig?
- Welche Skills wurden aktiviert?
- Welche Wellenplanung war effektiv?
- Was waren Lessons Learned?

**Schritt 2: Generiere die .skill Datei**

Verwende [templates/exported-skill-template.md](templates/exported-skill-template.md) als Basis.

Die generierte `.skill` Datei wird gespeichert unter:
```
packages/[company-slug].skill
```

**Schritt 3: Bake alles ein**

Die `.skill` Datei muss ALLES enthalten — keine externen Abhaengigkeiten:

```
┌─────────────────────────────────────────────────┐
│  [company-name].skill                           │
│                                                  │
│  FRONTMATTER (Name, Description, Trigger)        │
│  ├── Konfiguration & Parameter                   │
│  ├── Company-Definition (Mission, Ziele, Gov.)   │
│  ├── Team-Definitionen (komplett eingebettet)    │
│  ├── Agenten-Definitionen (komplett eingebettet) │
│  ├── Eingebettete Skills (Inline-Anweisungen)    │
│  ├── Orchestrierungs-Ablauf (Schritt fuer Schritt)│
│  ├── Wellenplanungs-Logik                        │
│  ├── Verifikations-Regeln                        │
│  └── Fehlerbehandlung & Eskalation               │
└─────────────────────────────────────────────────┘
```

**Schritt 4: Parametrisieren**

Ersetze aufgabenspezifische Werte durch Platzhalter. Definiere im Frontmatter welche Parameter beim Aufruf gesetzt werden muessen:

```yaml
metadata:
  parameters:
    AUFGABE: {required: true, description: "Neue Aufgabenbeschreibung"}
    ZIEL: {required: true, description: "Primaerziel der Mission"}
    MAX_AGENTS: {required: false, default: "3", description: "Max parallele Agenten"}
```

**Schritt 5: Validieren**

Pruefe die exportierte `.skill` Datei:
- [ ] Frontmatter valide (name, description vorhanden)
- [ ] Alle Agenten-Definitionen vollstaendig eingebettet
- [ ] Alle Skills inline enthalten (keine externen Referenzen)
- [ ] Orchestrierungs-Ablauf lueckenlos
- [ ] Verifikationsregeln enthalten
- [ ] Test-Aufruf mit Beispiel-Aufgabe funktioniert

### 11.4 Aufruf einer .skill Datei

Wenn der User sagt: **"Fuehre [company-name].skill aus fuer [Aufgabe]"**:

1. **Laden**: Lies die `.skill` Datei aus `packages/`, `.claude/skills/`, `~/.agents/skills/`
2. **Parameter einsetzen**: Ersetze `{{AUFGABE}}`, `{{ZIEL}}` etc. mit den User-Angaben
3. **Direkt ausfuehren**: Die Datei enthaelt den kompletten Ablauf — folge den Anweisungen Schritt fuer Schritt
4. **Keine Phase 1-4 noetig**: Company-Struktur, Agenten und Skills sind bereits definiert
5. **Starte bei Wellenplanung**: Erstelle aufgabenspezifische Tasks und plane Wellen

### 11.5 Skill-Extraktion (einzelne Skills)

Einzelne Skills aus einer Mission koennen separat exportiert werden:

1. Kopiere `.mission-forge/skills/[name]/` nach `.claude/skills/[name]/`
2. Entferne `auto-generated: true` aus metadata
3. Pruefe dass der Skill ohne Missions-Kontext funktioniert
4. Global verfuegbar fuer alle zukuenftigen Projekte

### 11.6 Package-Registry

Exportierte `.skill` Dateien werden registriert in `packages/REGISTRY.md`:

```markdown
# .skill Registry

| Datei                      | Beschreibung                  | Exportiert | Version |
|----------------------------|-------------------------------|------------|---------|
| api-development.skill      | REST-API mit Auth & DB        | 2026-03-29 | 1.0.0   |
| frontend-app.skill         | Frontend mit React/Next.js    | 2026-03-30 | 1.0.0   |
| data-pipeline.skill        | ETL-Pipeline mit Validierung  | 2026-04-01 | 1.1.0   |
```

---

## 12. Referenzen

- **Manifest-Felder**: [references/manifest-reference.md](references/manifest-reference.md)
- **Kommunikationsprotokoll**: [references/communication-protocol.md](references/communication-protocol.md)
- **Fehlerbehandlung**: [references/error-handling.md](references/error-handling.md)
- **Fehlerbehebung**: [references/troubleshooting.md](references/troubleshooting.md)
- **Checklisten**: [references/checklists.md](references/checklists.md)
- **Templates**: `templates/` Verzeichnis

---

## Schnellstart

**"Spawne eine Company fuer [Aufgabe]":**
1. Aufgabe analysieren (Phase 1)
2. Bei Unklarheiten nachfragen (max 3 Fragen)
3. Company-Struktur erstellen (Phase 2-4)
4. Wellenplan praesentieren (Phase 5) — **User-Freigabe abwarten**
5. Ausfuehren (Phase 6), Verifizieren (Phase 7), Dokumentieren (Phase 8)
6. Optional: Exportieren (Phase 9)

**"Fuehre [name].skill aus fuer [Aufgabe]":**
1. `.skill` Datei aus `packages/` laden
2. Parameter einsetzen (AUFGABE, ZIEL)
3. Aufgabenspezifische Tasks erstellen
4. Direkt ausfuehren — Company-Struktur ist bereits eingebettet

**"Exportiere diese Company als .skill":**
1. Abgeschlossene Mission analysieren
2. Alles in eine autarke `.skill` Datei baken (Teams, Agenten, Skills, Orchestrierung)
3. In `packages/` speichern und Registry aktualisieren
