---
name: mission-forge
description: >
  Spawnt vollstaendige Agent-Companies aus beliebigen Aufgabenbeschreibungen mit
  Orchestrator-Hierarchie, Sub-Orchestratoren, Skill-Zuordnung und lueckenloser
  Aufgabenverfolgung. Revisionssicher durch kryptographische Hash-Chain (AuditChain).
  Optionaler Monte-Carlo-Modus fuer kritische Tasks.
  Exportiert abgeschlossene Companies als wiederverwendbare Packages.
  Trigger: "company spawnen", "organisation erstellen", "aufgabe
  orchestrieren", "ablauforganisation", "mission starten", "nichts vergessen",
  "skill-organisation", "multi-agent", "task-force", "projekt-orchestrierung",
  "company exportieren", "package erstellen", "company wiederverwenden",
  "revisionssicher", "audit-trail", "monte-carlo".
license: MIT
compatibility: >
  Designed for Claude Code and compatible agent runtimes.
  Requires Bash, Read, Write, Edit, Agent tools.
  Requires Python 3.10+ for AuditChain (audit/chain.py).
  Optional: Git for versioning, WebFetch for external skill discovery.
metadata:
  author: skillorga
  version: "4.0.0"
  schema: agentcompanies/v1
  kind: skill
  tags: orchestration, company-spawning, multi-agent, task-management, workflow, export, audit-trail, revisionssicher, monte-carlo
allowed-tools: Bash Read Write Edit Agent Glob Grep TaskCreate TaskUpdate TaskGet TaskList
---

# Mission Forge — Agent-Company-Spawner & Orchestrierungs-Engine

> Verwandelt jede Aufgabe in eine lebende Organisation aus spezialisierten Agenten
> mit garantierter Vollstaendigkeit, Nachverfolgbarkeit und Qualitaetssicherung.
> Revisionssicher durch kryptographische Hash-Chain. Exportiert bewährte Companies
> als wiederverwendbare Packages.

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
- **Revisionssicherheit** gefordert ist (regulierte Branchen, Audits, Compliance)

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
6. In der AuditChain protokolliert sein (Revisionssicherheit)

Fehlt ein Schritt, blockiert die Pipeline.

### 2.6 AuditChain (Kryptographische Beweiskette)

Jede Zustandsaenderung in einer Mission wird als Hash-Chain-Eintrag protokolliert. Jeder Eintrag referenziert den SHA-256-Hash des vorherigen — Manipulation eines Eintrags bricht die Kette und wird bei der Verifikation sofort erkannt.

**Chain-Datei:** `.mission-forge/audit/CHAIN.jsonl`  
**Engine:** `audit/chain.py` (Python 3.10+, keine externen Dependencies)  
**Verifier:** `audit/verify.py` (Standalone, fuer externe Auditoren)

**Pflicht-Events:**

| Event                  | Wann                              | Phase |
|------------------------|-----------------------------------|-------|
| `GENESIS`              | Company wird gespawnt (inkl. Skill-Hashes) | 2     |
| `SKILL_CHANGED`        | Skill wurde mutiert/aktualisiert   | 6     |
| `GATE_PASSED`          | Aktion durch Gateway freigegeben   | 6     |
| `GATE_BLOCKED`         | Aktion durch Gateway blockiert     | 6     |
| `WAVE_PLAN_SEALED`     | Wellenplan freigegeben             | 5     |
| `TASK_STATUS_CHANGE`   | Jeder Statuswechsel eines WP      | 6     |
| `MONTE_CARLO_VARIANT`  | Jede MC-Variante (wenn aktiviert)  | 6     |
| `MONTE_CARLO_SELECTED` | MC-Auswahl mit Begruendung        | 6     |
| `VERIFICATION_PASSED`  | WP-Verifikation bestanden          | 7     |
| `VERIFICATION_FAILED`  | WP-Verifikation gescheitert        | 7     |
| `CHAIN_SEALED`         | Mission abgeschlossen              | 8     |

**Eintrag-Format (CHAIN.jsonl, eine Zeile pro Eintrag):**

```json
{
  "seq": 0,
  "timestamp": "2026-03-30T14:22:01.123456Z",
  "event": "TASK_STATUS_CHANGE",
  "ref": "WP-003",
  "agent": "implementierer-01",
  "data": {"from": "IN_PROGRESS", "to": "DONE", "artifact_hash": "sha256:..."},
  "prev_hash": "sha256:vorheriger_hash...",
  "entry_hash": "sha256:dieses_eintrags_hash..."
}
```

**Integritaetsregel:** `entry_hash` = SHA-256 ueber alle Felder OHNE entry_hash selbst, kanonisch serialisiert (sorted keys, keine Whitespaces). Verkettung ueber `prev_hash`. Genesis-Block hat prev_hash = 64 Nullen.

### 2.7 Monte-Carlo-Modus (Optional)

Fuer Tasks mit Prioritaet `critical` kann der Monte-Carlo-Modus aktiviert werden. Dabei wird ein Task N-mal mit variierten Parametern (Temperatur, Prompt-Reihenfolge, Formulierung) ausgefuehrt. Ergebnisse werden bewertet und das beste ausgewaehlt. Alle Varianten werden in der AuditChain dokumentiert — nachvollziehbar, warum welche Variante gewaehlt wurde.

Konfiguration in COMPANY.md:

```yaml
execution:
  monte_carlo: true          # Aktiviert MC fuer critical Tasks
  mc_variants: 3             # Anzahl Varianten (default: 3)
  mc_selection: best_score   # best_score | consensus | user_choice
```

**Nur fuer critical Tasks.** Fuer medium/low Tasks waere der Overhead unverhaeltnismaessig.

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

### 4.5 AuditChain initialisieren (Genesis-Block)

Erstelle `.mission-forge/audit/` und schreibe den Genesis-Block. Dies ist der erste Eintrag der kryptographischen Beweiskette und versiegelt: Mission-ID, Ziele, beteiligte Akteure, Chain-Version.

```bash
python audit/chain.py genesis .mission-forge/audit "MISSION-ID"
```

Oder programmatisch:

```python
from audit.chain import AuditChain
ac = AuditChain(".mission-forge/audit")
ac.genesis(
    mission_id="MISSION-2026-042",
    goals=["Ziel 1", "Ziel 2"],
    actors=["orchestrator", "agent-alpha", "tester-01"],
    skill_files={
        "main": "SKILL.md",
        "testing": ".mission-forge/skills/testing/SKILL.md",
    },
)
```

**Pflicht:** Ohne Genesis-Block ist die Mission NICHT revisionssicher. Der Genesis-Block MUSS vor der ersten Ausfuehrung existieren. Alle verwendeten Skills werden im Genesis-Block gehasht — damit ist nachweisbar, nach welchen Anweisungen die Agenten gearbeitet haben.

**Verzeichnisstruktur nach Phase 2:**

```
.mission-forge/
├── COMPANY.md
├── STATE.md
├── audit/                    ← NEU
│   └── CHAIN.jsonl           ← Genesis-Block als erster Eintrag
├── teams/
│   ├── planung/TEAM.md
│   ├── ausfuehrung/TEAM.md
│   └── verifikation/TEAM.md
├── agents/
│   └── [agent-slug]/AGENTS.md
└── tasks/
    └── [wp-id]/TASK.md
```

---

## 5. Phase 3 — Orchestrator-Hierarchie

### 5.1 Mission-Orchestrator (Root)

Der einzige Agent der die gesamte Mission ueberblickt.

**Ablauf:**
1. Lade COMPANY.md und alle Team-Manifeste (Katalog-Stufe)
2. Erstelle STATE.md basierend auf [templates/state-template.md](templates/state-template.md)
3. Validiere: Alle REQs haben zugehoerige WPs
4. Validiere: AuditChain Genesis-Block existiert
5. Delegiere an Sub-Orchestratoren in Reihenfolge: Planung -> Ausfuehrung -> Verifikation
6. Pruefe nach jeder Welle die Vollstaendigkeit
7. Eskaliere Blocker an den User

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

| Welle | WP     | Agent                | Skills               | Model  | Monte-Carlo |
|-------|--------|----------------------|----------------------|--------|-------------|
| 1     | WP-001 | implementierer-alpha | code-review, testing | sonnet | nein        |
| 2     | WP-004 | implementierer-alpha | api-design           | sonnet | ja (critical)|

### 7.4 Pre-Flight-Check

- [ ] Jedes WP genau einer Welle zugeordnet
- [ ] Keine Welle referenziert ein WP aus einer spaeteren Welle
- [ ] Jedes WP hat zugewiesenen Agenten
- [ ] Alle Skills verfuegbar
- [ ] Abhaengigkeitsgraph azyklisch
- [ ] Jede REQ durch mindestens ein WP abgedeckt
- [ ] AuditChain Genesis-Block existiert

**Zeige dem User den vollstaendigen Plan mit Traceability-Matrix. Keine Ausfuehrung ohne Freigabe.**

### 7.5 Wellenplan versiegeln (AuditChain)

Nach User-Freigabe des Plans wird der Wellenplan in der AuditChain versiegelt:

```python
ac.log("WAVE_PLAN_SEALED", ref="PLAN-v1", data={
    "waves": anzahl_wellen,
    "total_wps": anzahl_wps,
    "plan_hash": sha256_des_wellenplans,
    "monte_carlo_tasks": liste_der_mc_wps,
})
```

Ab diesem Punkt ist der Plan in der Chain fixiert. Aenderungen am Plan nach Freigabe erzeugen einen `WAVE_PLAN_AMENDED` Eintrag mit Begruendung:

```python
ac.log("WAVE_PLAN_AMENDED", ref="PLAN-v2", data={
    "reason": "WP-005 hinzugefuegt nach Scope-Erweiterung",
    "changes": ["added WP-005 to wave 3"],
    "approved_by": "user",
})
```

---

## 8. Phase 6 — Ausfuehrung

### 8.1 Wellenausfuehrung

Fuer jede Welle:

1. **Vorbereitung**: Manifeste laden, Vorbedingungen pruefen, STATE.md aktualisieren
2. **AuditChain-Logging**: Jeder Statuswechsel wird automatisch in der Chain protokolliert (siehe 8.5)
3. **Parallele Ausfuehrung**: Agenten spawnen (max 3 concurrent), jeder in frischem Kontext
4. **Ergebnis-Sammlung**: Jeder Agent schreibt `.mission-forge/results/wave-N-wp-XXX/SUMMARY.md`
5. **Wellen-Verifikation**: Gegen Akzeptanzkriterien pruefen, bei Fehler Reparatur (max 2 Versuche)
6. **Gate-Check**: Alle DONE? -> Naechste Welle. FAILED? -> Eskalation

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

### 8.5 AuditChain Auto-Logging

**Jeder Statuswechsel** eines WP wird automatisch in der AuditChain protokolliert. Dies ist keine optionale Ergaenzung — es ist Pflicht fuer revisionssichere Missionen.

```python
ac.log("TASK_STATUS_CHANGE", ref=wp_id, agent=agent_name, data={
    "from": alter_status,
    "to": neuer_status,
    "artifact_hash": sha256_des_ergebnisses,  # wenn Artefakt vorhanden
    "wave": aktuelle_welle,
})
```

**Weitere Events die automatisch geloggt werden:**

| Situation | Event | Daten |
|---|---|---|
| Agent gestartet | `AGENT_SPAWNED` | agent, wp_id, wave |
| Agent fertig | `AGENT_COMPLETED` | agent, wp_id, duration_seconds |
| Reparatur-Versuch | `REPAIR_ATTEMPT` | agent, wp_id, attempt_number, reason |
| Eskalation | `ESCALATION` | from_agent, to_level, reason |
| Plan-Aenderung | `WAVE_PLAN_AMENDED` | reason, changes, approved_by |
| Skill aktiviert | `SKILL_ACTIVATED` | skill_name, agent, trust_level |
| Skill mutiert | `SKILL_CHANGED` | skill_name, skill_hash, reason |
| Gateway-Freigabe | `GATE_PASSED` | action, agent, policies_checked |
| Gateway-Blockade | `GATE_BLOCKED` | action, agent, violations |

### 8.6 Monte-Carlo-Ausfuehrung

Wenn `monte_carlo: true` in COMPANY.md und ein Task die Prioritaet `critical` hat:

**Ablauf:**

1. Task wird `mc_variants`-mal ausgefuehrt (default: 3)
2. Jede Variante nutzt leicht veraenderte Parameter:
   - Variante 1: Original-Prompt, Temperatur 0.3
   - Variante 2: Umformulierter Prompt, Temperatur 0.5
   - Variante 3: Umgekehrte Reihenfolge der Anforderungen, Temperatur 0.7
3. Jede Variante wird einzeln gegen Akzeptanzkriterien bewertet (Score 0.0–1.0)
4. Auswahl nach `mc_selection`:
   - `best_score`: Hoechster Score gewinnt
   - `consensus`: Ergebnis das in >50% der Varianten vorkommt
   - `user_choice`: Alle Varianten werden dem User praesentiert

**AuditChain-Logging fuer Monte-Carlo:**

```python
# Jede Variante
ac.log("MONTE_CARLO_VARIANT", ref=wp_id, agent=agent_name, data={
    "variant": varianten_nummer,
    "prompt_variation": beschreibung_der_variation,
    "score": bewertungs_score,
    "artifact_hash": sha256_des_varianten_ergebnisses,
})

# Auswahl
ac.log("MONTE_CARLO_SELECTED", ref=wp_id, data={
    "selected_variant": gewaehlte_nummer,
    "reason": "Hoechster Score (0.91)",
    "all_scores": [0.82, 0.91, 0.87],
    "selection_method": "best_score",
})
```

**Alle Varianten bleiben in der Chain** — nachvollziehbar, warum welche gewaehlt wurde. Nicht-gewaehlte Varianten werden NICHT geloescht.

### 8.7 Execution Gateway (Pre-Flight-Pruefung)

Skills definieren, WAS ein Agent tun kann. Das Execution Gateway definiert, was er tun DARF. Bevor ein Agent eine Aktion ausfuehrt, prueft das Gateway die Aktion gegen definierte Policies. Wird die Aktion blockiert, landet ein `GATE_BLOCKED` Eintrag in der Chain. Wird sie freigegeben, ein `GATE_PASSED`.

**Policy-Definition in COMPANY.md:**

```yaml
policies:
  - name: prod-safety
    blocked_actions: ["file.delete_prod", "db.drop_*", "deploy.production"]
    allowed_agents: ["implementierer-alpha", "implementierer-beta"]
  - name: scope-control
    allowed_actions: ["file.write", "file.read", "test.run", "api.call"]
```

**Ablauf:**

1. Agent will Aktion ausfuehren (z.B. `deploy.production`)
2. Gateway prueft gegen alle definierten Policies
3. Ergebnis wird in der Chain protokolliert:
   - `GATE_PASSED`: Aktion erlaubt, Agent darf ausfuehren
   - `GATE_BLOCKED`: Aktion blockiert, mit Grund und verletzter Policy
   - `GATE_PENDING_APPROVAL`: Aktion erfordert manuelle Freigabe

```python
allowed, entry = ac.gate_check(
    action="deploy.production",
    agent="implementierer-alpha",
    ref="WP-005",
    policies=policies,
)
if not allowed:
    # Aktion wird nicht ausgefuehrt, Blockierung ist in der Chain dokumentiert
    escalate_to_orchestrator(entry)
```

**Unterschied zu Skills:** Ein Skill beschreibt Faehigkeiten und Instruktionen. Eine Policy beschreibt Grenzen und Berechtigungen. Beides wird in der Chain verankert: der Skill-Hash im Genesis-Block (nach WELCHEN Regeln gearbeitet wird) und die Gateway-Entscheidung bei jeder Aktion (OB gearbeitet werden darf).

---

## 9. Phase 7 — Verifikation

### 9.1 Sechs-Ebenen-Verifikation

| Ebene | Prueft                               | Agent                    |
|-------|--------------------------------------|--------------------------|
| 1     | Einzelnes WP: Akzeptanzkriterien     | Abnahme-Tester           |
| 2     | Welle: Integration der WP-Ergebnisse | Integrations-Pruefer     |
| 3     | Phase: Alle Wellen kohaerent         | Sub-Orch. Verifikation   |
| 4     | Mission: Alle REQs erfuellt          | Vollstaendigkeits-Pruefer|
| 5     | Qualitaet: Nicht-funktionale Kriterien| Qualitaets-Sicherer     |
| 6     | Integritaet: Kryptographische Chain  | AuditChain Verifier      |

### 9.2 Zero-Drop-Audit

Pruefe fuer JEDE REQ-ID: WP zugeordnet? Ausgefuehrt? Akzeptanzkriterium geprueft? Dokumentiert? In AuditChain protokolliert?

Suche nach Luecken: REQs ohne WP, WPs ohne Agent, WPs ohne Ergebnis, Agenten ohne Report, Skills ohne Aktivierung, Statuswechsel ohne Chain-Eintrag.

Erstelle `.mission-forge/VERIFICATION.md` basierend auf [templates/verification-template.md](templates/verification-template.md).

### 9.3 AuditChain-Integritaetspruefung (Ebene 6)

Nach dem Zero-Drop-Audit wird die kryptographische Integritaet der Chain geprueft:

```bash
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --verbose
```

Oder programmatisch:

```python
ac = AuditChain(".mission-forge/audit")
intact, errors = ac.verify()
```

**Ergebnis wird als neuer Abschnitt in VERIFICATION.md eingefuegt:**

```markdown
## Kryptographische Integritaet (AuditChain)

| Eigenschaft | Wert |
|---|---|
| Chain-Laenge | 47 Eintraege |
| Genesis-Hash | `sha256:abc123...` |
| Finaler Hash | `sha256:xyz789...` |
| Zeitraum | 2026-03-30T08:00:00Z → 2026-03-30T16:45:00Z |
| Kette intakt | ✅ Ja |
| Beteiligte Agenten | orchestrator, implementierer-alpha, tester-01 |

> Alle 47 Eintraege verifiziert. Keine Manipulation erkannt.
```

**Bei Integritaetsverletzung:** Sofortige Eskalation an User. Mission wird NICHT als VERIFIED markiert. Status wechselt zu ESCALATED mit Grund "AuditChain integrity violation".

### 9.4 Verifikations-Logging in AuditChain

Jedes Verifikationsergebnis wird in der Chain protokolliert:

```python
# Bestandene Verifikation
ac.log("VERIFICATION_PASSED", ref=wp_id, agent="tester-01", data={
    "level": "acceptance_criteria",
    "result": "PASS",
    "details": "Alle 5 Akzeptanzkriterien erfuellt",
})

# Gescheiterte Verifikation
ac.log("VERIFICATION_FAILED", ref=wp_id, agent="tester-01", data={
    "level": "acceptance_criteria",
    "result": "FAIL",
    "failed_criteria": ["Performance unter Threshold"],
    "action": "REPAIR",
})
```

---

## 10. Phase 8 — Abschluss

### 10.1 Abschlussbericht

Erstelle `.mission-forge/MISSION-REPORT.md` basierend auf [templates/mission-report-template.md](templates/mission-report-template.md).

### 10.2 Missions-Abbruch

Falls vorzeitig beendet: Status `ABORTED` in STATE.md, Grund im Entscheidungslog, partieller Report. Bereits abgeschlossene Ergebnisse bleiben erhalten. AuditChain wird trotzdem versiegelt (mit ABORTED-Event).

### 10.3 AuditChain versiegeln

Am Ende jeder Mission (erfolgreich oder abgebrochen) wird die Chain versiegelt:

```python
ac.seal("MISSION-ID")
```

Der SEAL-Eintrag enthaelt: Gesamtanzahl Eintraege, Genesis-Hash, Integritaetsstatus. Nach der Versiegelung duerfen keine weiteren Eintraege hinzugefuegt werden.

**Revisionssicherheits-Abschnitt im MISSION-REPORT.md:**

```markdown
## Revisionssicherheit

| Eigenschaft | Wert |
|---|---|
| AuditChain | `.mission-forge/audit/CHAIN.jsonl` |
| Eintraege | 47 |
| Genesis-Hash | `sha256:abc123...` |
| Finaler Hash | `sha256:xyz789...` |
| Kette intakt | ✅ |
| Versiegelt | ✅ |

Pruefbar mit:
```bash
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --report
```
```

**Integritaetsbericht generieren (optional):**

```bash
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --report > .mission-forge/AUDIT-REPORT.md
```

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
- AuditChain-Konfiguration (auto-log, Monte-Carlo-Einstellungen)
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
- Welche Monte-Carlo-Konfiguration hat die besten Ergebnisse geliefert?

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
│  ├── AuditChain-Konfiguration                    │
│  ├── Monte-Carlo-Einstellungen (wenn verwendet)  │
│  └── Fehlerbehandlung & Eskalation               │
└─────────────────────────────────────────────────┘
```

**Schritt 3b: AuditChain-Konfiguration einbetten**

Die `.skill` Datei enthaelt die AuditChain-Konfiguration als eingebetteten Abschnitt. Beim Aufruf wird automatisch eine NEUE Chain mit Genesis-Block erstellt. Die Chain der Original-Mission wird NICHT uebernommen — jede Ausfuehrung bekommt ihre eigene, unabhaengige Chain.

```yaml
auditchain:
  enabled: true
  auto_log: true
  monte_carlo: false  # oder true mit mc_variants, mc_selection
```

**Schritt 4: Parametrisieren**

Ersetze aufgabenspezifische Werte durch Platzhalter. Definiere im Frontmatter welche Parameter beim Aufruf gesetzt werden muessen:

```yaml
metadata:
  parameters:
    AUFGABE: {required: true, description: "Neue Aufgabenbeschreibung"}
    ZIEL: {required: true, description: "Primaerziel der Mission"}
    MAX_AGENTS: {required: false, default: "3", description: "Max parallele Agenten"}
    MONTE_CARLO: {required: false, default: "false", description: "MC fuer critical Tasks"}
```

**Schritt 5: Validieren**

Pruefe die exportierte `.skill` Datei:
- [ ] Frontmatter valide (name, description vorhanden)
- [ ] Alle Agenten-Definitionen vollstaendig eingebettet
- [ ] Alle Skills inline enthalten (keine externen Referenzen)
- [ ] Orchestrierungs-Ablauf lueckenlos
- [ ] Verifikationsregeln enthalten
- [ ] AuditChain-Konfiguration eingebettet
- [ ] Test-Aufruf mit Beispiel-Aufgabe funktioniert

### 11.4 Aufruf einer .skill Datei

Wenn der User sagt: **"Fuehre [company-name].skill aus fuer [Aufgabe]"**:

1. **Laden**: Lies die `.skill` Datei aus `packages/`, `.claude/skills/`, `~/.agents/skills/`
2. **Parameter einsetzen**: Ersetze `{{AUFGABE}}`, `{{ZIEL}}` etc. mit den User-Angaben
3. **AuditChain initialisieren**: Genesis-Block mit neuer Mission-ID erstellen
4. **Direkt ausfuehren**: Die Datei enthaelt den kompletten Ablauf — folge den Anweisungen Schritt fuer Schritt
5. **Keine Phase 1-4 noetig**: Company-Struktur, Agenten und Skills sind bereits definiert
6. **Starte bei Wellenplanung**: Erstelle aufgabenspezifische Tasks und plane Wellen

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

| Datei                      | Beschreibung                  | Exportiert | Version | AuditChain | Monte-Carlo |
|----------------------------|-------------------------------|------------|---------|------------|-------------|
| api-development.skill      | REST-API mit Auth & DB        | 2026-03-29 | 1.0.0   | ✅          | nein        |
| frontend-app.skill         | Frontend mit React/Next.js    | 2026-03-30 | 1.0.0   | ✅          | nein        |
| data-pipeline.skill        | ETL-Pipeline mit Validierung  | 2026-04-01 | 1.1.0   | ✅          | ja (3 var.) |
```

---

## 12. Referenzen

- **Manifest-Felder**: [references/manifest-reference.md](references/manifest-reference.md)
- **Kommunikationsprotokoll**: [references/communication-protocol.md](references/communication-protocol.md)
- **Fehlerbehandlung**: [references/error-handling.md](references/error-handling.md)
- **Fehlerbehebung**: [references/troubleshooting.md](references/troubleshooting.md)
- **Checklisten**: [references/checklists.md](references/checklists.md)
- **AuditChain-Engine**: [audit/chain.py](audit/chain.py)
- **AuditChain-Verifier**: [audit/verify.py](audit/verify.py)
- **Templates**: `templates/` Verzeichnis

---

## Schnellstart

**"Spawne eine Company fuer [Aufgabe]":**
1. Aufgabe analysieren (Phase 1)
2. Bei Unklarheiten nachfragen (max 3 Fragen)
3. Company-Struktur erstellen inkl. AuditChain Genesis-Block (Phase 2-4)
4. Wellenplan praesentieren und versiegeln (Phase 5) — **User-Freigabe abwarten**
5. Ausfuehren mit Auto-Logging (Phase 6), Verifizieren inkl. Chain-Pruefung (Phase 7), Dokumentieren und versiegeln (Phase 8)
6. Optional: Exportieren (Phase 9)

**"Fuehre [name].skill aus fuer [Aufgabe]":**
1. `.skill` Datei aus `packages/` laden
2. Parameter einsetzen (AUFGABE, ZIEL)
3. AuditChain Genesis-Block erstellen
4. Aufgabenspezifische Tasks erstellen
5. Direkt ausfuehren — Company-Struktur ist bereits eingebettet

**"Exportiere diese Company als .skill":**
1. Abgeschlossene Mission analysieren
2. Alles in eine autarke `.skill` Datei baken (Teams, Agenten, Skills, Orchestrierung, AuditChain-Config)
3. In `packages/` speichern und Registry aktualisieren

**"Pruefe die Revisionssicherheit":**
```bash
python audit/verify.py .mission-forge/audit/CHAIN.jsonl --report
```
