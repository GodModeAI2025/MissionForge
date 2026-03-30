---
name: {{COMPANY_SLUG}}
description: >
  {{COMPANY_DESCRIPTION}}
  Autarke Company-Skill-Datei: Spawnt eine vollstaendige Agenten-Organisation
  zur Abarbeitung von {{AUFGABEN_TYP}} Aufgaben. Enthaelt alle Agenten, Teams,
  Skills und Orchestrierungslogik. Trigger: {{TRIGGER_WOERTER}}.
license: MIT
compatibility: >
  Designed for Claude Code and compatible agent runtimes.
  Requires Bash, Read, Write, Edit, Agent tools.
metadata:
  author: mission-forge-export
  version: "1.0.0"
  exported-from: "{{SOURCE_MISSION_SLUG}}"
  exported-date: "{{ISO_DATE}}"
  parameters:
    AUFGABE: {required: true, description: "Konkrete Aufgabenbeschreibung"}
    ZIEL: {required: true, description: "Primaerziel dieser Mission"}
    MAX_AGENTS: {required: false, default: "3", description: "Max parallele Agenten"}
    MODEL_PROFILE: {required: false, default: "balanced", description: "quality | balanced | budget"}
    MONTE_CARLO: {required: false, default: "false", description: "Monte-Carlo fuer critical Tasks"}
allowed-tools: Bash Read Write Edit Agent Glob Grep TaskCreate TaskUpdate TaskGet TaskList
---

# {{COMPANY_NAME}} — Autarke Company-Skill-Datei

> Exportiert aus Mission: {{SOURCE_MISSION_SLUG}} am {{ISO_DATE}}.
> Diese Datei ist vollstaendig autark und enthaelt alles fuer die Ausfuehrung.

---

## Konfiguration

```yaml
max_concurrent_agents: {{MAX_AGENTS}}
model_profile: {{MODEL_PROFILE}}
wave_gate: strict
repair_attempts: 2
auditchain:
  enabled: true
  auto_log: true
execution:
  monte_carlo: {{MONTE_CARLO_ENABLED}}
  mc_variants: {{MC_VARIANTS}}
  mc_selection: {{MC_SELECTION}}
```

---

## 1. Company-Definition

**Mission**: {{COMPANY_DESCRIPTION}}

**Ziele**:
1. {{ZIEL}}
2. {{WEITERE_ZIELE}}

**Governance**:
- Eskalationspfad: Agent -> Sub-Orchestrator -> Mission-Orchestrator -> User
- Agenten entscheiden innerhalb ihres WP-Scopes autonom
- Jede Welle wird verifiziert bevor die naechste startet

---

## 2. Team-Definitionen

### Team: Planung
- **Manager**: Sub-Orchestrator Planung
- **Agenten**: {{PLANUNGS_AGENTEN}}
- **Aufgabe**: Anforderungsanalyse, Architektur-Design, Risikobewertung
- **Eskalation**: Bei unklaren Anforderungen oder widersprüchlichen Constraints -> Mission-Orchestrator

### Team: Ausfuehrung
- **Manager**: Sub-Orchestrator Ausfuehrung
- **Agenten**: {{AUSFUEHRUNGS_AGENTEN}}
- **Aufgabe**: Implementierung der Arbeitspakete, Integration
- **Eskalation**: Nach 2 fehlgeschlagenen Reparatur-Versuchen -> Mission-Orchestrator

### Team: Verifikation
- **Manager**: Sub-Orchestrator Verifikation
- **Agenten**: {{VERIFIKATIONS_AGENTEN}}
- **Aufgabe**: Pruefung gegen Akzeptanzkriterien, Zero-Drop-Audit
- **Eskalation**: Bei nicht-behebbaren Qualitaetsmaengeln -> Mission-Orchestrator

---

## 3. Agenten-Definitionen

{{FUER_JEDEN_AGENTEN_AUS_DER_MISSION:}}

### Agent: {{AGENT_NAME}}
- **Rolle**: {{AGENT_BESCHREIBUNG}}
- **Team**: {{TEAM_NAME}}
- **Skills**: {{AGENT_SKILLS}}
- **Model**: {{MODEL_PREFERENCE}}
- **Tools**: {{ERLAUBTE_TOOLS}}
- **Read-Only**: {{JA_NEIN}}

**Anweisungen**:
1. {{KONKRETE_ANWEISUNG_1}}
2. {{KONKRETE_ANWEISUNG_2}}
3. {{KONKRETE_ANWEISUNG_3}}

**Input**: {{ERWARTETE_EINGABEN}}
**Output**: {{ERWARTETE_AUSGABEN}}
**Nicht-Ziele**: {{EXPLIZITE_AUSSCHLUESSE}}

---

## 4. Eingebettete Skills

{{FUER_JEDEN_VERWENDETEN_SKILL:}}

### Skill: {{SKILL_NAME}}

**Beschreibung**: {{SKILL_BESCHREIBUNG}}

**Anweisungen**:
{{VOLLSTAENDIGE_SKILL_ANWEISUNGEN_HIER_EINGEBETTET}}

**Validierung**:
{{WIE_PRUEFT_MAN_KORREKTHEIT}}

---

## 5. Orchestrierungs-Ablauf

Wenn diese .skill Datei aktiviert wird, fuehre folgende Schritte aus:

### Schritt 1: Parameter einsetzen
- Lies die Parameter aus dem User-Aufruf: AUFGABE, ZIEL
- Ersetze alle {{AUFGABE}} und {{ZIEL}} Platzhalter in diesem Dokument

### Schritt 2: Aufgabe in Arbeitspakete zerlegen
- Analysiere die AUFGABE und leite Anforderungen (REQ-IDs) ab
- Schneide atomare Arbeitspakete (WP-IDs) mit Akzeptanzkriterien
- Validiere: Jede REQ hat mindestens ein WP

### Schritt 3: Wellenplanung
- Analysiere WP-Abhaengigkeiten als DAG
- Gruppiere unabhaengige WPs in parallele Wellen
- Weise Agenten aus Abschnitt 3 den WPs zu
- Pruefe: Kein Zyklus, alle WPs zugeordnet, alle REQs abgedeckt

### Schritt 4: User-Freigabe
- Praesentiere den Wellenplan mit Traceability-Matrix
- Warte auf explizite Freigabe

### Schritt 5: Wellenausfuehrung
Fuer jede Welle:
1. Erstelle STATE.md mit aktuellem Stand
2. Spawne Agenten parallel (max {{MAX_AGENTS}} concurrent)
3. Jeder Agent erhaelt: seine Definition (aus Abschnitt 3), sein WP, seine Skills (aus Abschnitt 4)
4. Jeder Agent arbeitet in frischem Kontext
5. Sammle Ergebnisse in `.mission-forge/results/wave-N-wp-XXX/SUMMARY.md`
6. Verifiziere gegen Akzeptanzkriterien
7. Bei Fehler: Reparatur (max 2 Versuche), dann Eskalation

### Schritt 6: Verifikation
- Zero-Drop-Audit: Jede REQ zugeordnet, ausgefuehrt, geprueft, dokumentiert?
- Luecken-Suche: REQs ohne WP? WPs ohne Ergebnis? Agenten ohne Report?
- Erstelle VERIFICATION.md

### Schritt 7: Abschluss
- Erstelle MISSION-REPORT.md
- Aktualisiere STATE.md auf finalen Stand

---

## 6. Verifikationsregeln

### Akzeptanzkriterien pro WP
Jedes WP muss gegen seine definierten Akzeptanzkriterien geprueft werden.
Ein WP gilt als VERIFIED wenn ALLE Kriterien bestanden sind.

### Zero-Drop-Audit
Fuer JEDE REQ-ID pruefe:
- [ ] Mindestens ein WP zugeordnet
- [ ] WP ausgefuehrt (Status != OPEN)
- [ ] Akzeptanzkriterium geprueft
- [ ] Ergebnis dokumentiert

### Luecken-Erkennung
- REQs ohne WP-Zuordnung
- WPs ohne Agent-Zuordnung
- WPs ohne Ergebnis-Datei
- Agenten die gespawnt aber nie reported haben

---

## 7. Fehlerbehandlung

Agent-Fehler -> Reparatur 1 -> Reparatur 2 -> Eskalation Sub-Orchestrator -> Eskalation Mission-Orchestrator -> Eskalation User.

User-Optionen bei Eskalation:
- **Ueberspringen**: WP Status SKIPPED mit Begruendung
- **Manuell loesen**: User gibt Input, dann weiter
- **Abbrechen**: Mission Status ABORTED, partieller Report

---

## 8. Lessons Learned aus Ursprungs-Mission

{{LESSONS_LEARNED_AUS_MISSION_REPORT}}

### Was gut funktioniert hat
- {{BEOBACHTUNG_1}}
- {{BEOBACHTUNG_2}}

### Empfehlungen
- {{EMPFEHLUNG_1}}
- {{EMPFEHLUNG_2}}
