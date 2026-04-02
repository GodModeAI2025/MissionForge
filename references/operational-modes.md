# Operational Modes — Mission Forge

Inspiriert von claude-codes Feature-Gating mit Compile-Time Dead Code Elimination.
Drei Modi die den Workflow-Umfang an die Aufgabenkomplexitaet anpassen.

---

## Modi-Uebersicht

| Feature                     | `lite`  | `standard` | `enterprise` |
|-----------------------------|---------|------------|--------------|
| Phase 1: Aufgabenanalyse    | ✓       | ✓          | ✓            |
| Phase 2: Company spawnen    | Minimal | Voll       | Voll         |
| Phase 3: Orchestrator       | Kein SO | Voll       | Voll         |
| Phase 4: Skill-Zuordnung    | Auto    | Voll       | Voll + Lock  |
| Phase 5: Wellenplanung      | Auto    | Voll       | Voll + DAG   |
| Phase 6: Ausfuehrung        | Direkt  | Wellen     | Wellen + MC  |
| Phase 7: Verifikation       | Minimal | Voll       | Voll + Chain |
| Phase 8: Abschluss          | Report  | Voll       | Voll + Seal  |
| Phase 9: Export              | —       | Optional   | Voll         |
| AuditChain                  | —       | Optional   | Pflicht      |
| Monte-Carlo                 | —       | —          | Verfuegbar   |
| Permission-Profile          | —       | Empfohlen  | Pflicht      |
| Cost-Tracking               | —       | Optional   | Pflicht      |
| Schema-Validierung          | —       | Empfohlen  | Pflicht      |
| DAG-Validierung             | —       | Empfohlen  | Pflicht      |
| Context-Manifest            | —       | Optional   | Empfohlen    |
| skills.lock                 | —       | Optional   | Pflicht      |
| Policy-Enforcement          | —       | —          | Aktiv        |

---

## `lite` — Leichtgewichtiger Modus

**Fuer**: 1-3 Arbeitspakete, einfache Tasks ohne Compliance-Anforderungen.

**Was wird uebersprungen:**
- Keine Sub-Orchestratoren (Mission-Orchestrator arbeitet direkt)
- Keine formale Team-Struktur (kein teams/ Verzeichnis)
- Keine VERIFICATION.md (Orchestrator prueft selbst)
- Kein Export (Phase 9)
- Keine AuditChain
- Kein Monte-Carlo

**Verzeichnisstruktur:**
```
.mission-forge/
├── COMPANY.md          (vereinfacht)
├── STATE.md
├── agents/
│   └── worker/AGENTS.md
├── tasks/
│   └── wp-001/TASK.md
└── results/
    └── wave-1-wp-001/SUMMARY.md
```

**Wann verwenden:**
- Schnelle Prototypen
- Einzelne Features
- Bug-Fixes
- Tasks die "eigentlich zu klein fuer MissionForge" sind

---

## `standard` — Standard-Modus (Default)

**Fuer**: 3-15 Arbeitspakete, regulaere Projekte.

**Voller 9-Phasen-Workflow** wie in SKILL.md dokumentiert.

Alle Features verfuegbar, AuditChain und erweiterte Validierung empfohlen
aber nicht erzwungen.

---

## `enterprise` — Enterprise-Modus

**Fuer**: Regulierte Branchen, Compliance-kritische Projekte, 10+ WPs.

**Zusaetzliche Pflichten:**
1. AuditChain MUSS aktiviert sein
2. Permission-Profile MUESSEN fuer jeden Agenten gesetzt sein
3. Cost-Tracking MUSS aktiv sein mit definiertem Budget
4. Schema-Validierung MUSS bei Pre-Flight bestehen
5. DAG-Validierung MUSS bestehen
6. skills.lock MUSS erstellt werden
7. Alle Monte-Carlo-Varianten MUESSEN dokumentiert sein
8. Policy-Datei wird enforced (falls vorhanden)

**Zusaetzliche Pre-Flight-Checks:**
- [ ] AuditChain: enabled = true
- [ ] Alle Agenten haben permission-profile
- [ ] Budget in COMPANY.md definiert
- [ ] skills.lock erstellt und gehasht
- [ ] Policy-Compliance geprueft

---

## `--dry-run` Flag

Unabhaengig vom Modus: `--dry-run` fuehrt Phasen 1-5 aus und stoppt.
Erzeugt die gesamte Planung ohne auszufuehren.

**Nutzen:**
- Plan-Review vor Ausfuehrung
- Kostenschaetzung
- DAG-Visualisierung
- Skill-Verfuegbarkeitspruefung

---

## Modus-Auswahl

Der Modus wird bestimmt durch (Prioritaet):

1. Explizit in COMPANY.md: `mode: enterprise`
2. In Projekt-Config: `.mission-forge/config.yaml`
3. In User-Config: `~/.mission-forge/config.yaml`
4. Automatisch nach WP-Anzahl:
   - 1-2 WPs → `lite`
   - 3-15 WPs → `standard`
   - 16+ WPs → `standard` (enterprise muss explizit gewaehlt werden)
