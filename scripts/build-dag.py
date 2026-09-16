#!/usr/bin/env python3
"""
MissionForge DAG Builder — Automatische Wellenplanung
======================================================
Liest alle TASK.md-Dateien einer Mission, extrahiert depends-on-Felder,
baut einen gerichteten Abhängigkeitsgraphen, erkennt Zyklen und berechnet
Waves automatisch per topologischer Sortierung. Prueft ausserdem, ob parallel
laufende Tasks derselben Welle ueberlappende Schreibbereiche (writes) haben.

Usage:
    python scripts/build-dag.py [path-to-.mission-forge]
    python scripts/build-dag.py .mission-forge --apply        # Schreibt wave-Felder in TASK.md
    python scripts/build-dag.py .mission-forge --json          # JSON-Output
    python scripts/build-dag.py .mission-forge --critical-path # Zeigt kritischen Pfad
    python scripts/build-dag.py .mission-forge --test          # Selbsttest

Exit codes: 0 = OK, 1 = Zyklen erkannt, 2 = Fehler, 3 = Schreibkonflikt in einer Welle
"""

import fnmatch
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional


# ── YAML-Frontmatter Parser (kein externes Paket noetig) ────

def parse_frontmatter(filepath: Path) -> dict:
    """Extrahiert YAML-Frontmatter zwischen --- Markern als Dict.
    Minimaler Parser ohne externe Abhängigkeiten."""
    text = filepath.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    end = text.find("\n---", 3)
    if end == -1:
        return {}

    fm_text = text[4:end]
    result = {}
    current_key = None
    current_list: Optional[list] = None

    for line in fm_text.split("\n"):
        stripped = line.strip()

        # Leerzeilen und Kommentare ignorieren
        if not stripped or stripped.startswith("#"):
            continue

        # Listen-Eintrag (  - value)
        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
                result[current_key] = current_list
            current_list.append(stripped[2:].strip().strip('"').strip("'"))
            continue

        # Multi-line String (  continuation)
        if line.startswith("  ") and current_key and not stripped.startswith("- "):
            if isinstance(result.get(current_key), str):
                result[current_key] += " " + stripped
                continue

        # Key: Value
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_.-]*)\s*:\s*(.*)', line)
        if match:
            current_key = match.group(1)
            value = match.group(2).strip().strip('"').strip("'")
            current_list = None

            if value == "" or value == ">":
                result[current_key] = ""
            elif value.startswith("[") and value.endswith("]"):
                # Inline-Liste: [a, b, c]
                items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
                result[current_key] = [i for i in items if i]
                current_list = result[current_key]
            else:
                result[current_key] = value

    return result


# ── Schreibbereiche ─────────────────────────────────────────

def _normalize_scope(scope: str) -> str:
    scope = scope.strip()
    while scope.startswith("./"):
        scope = scope[2:]
    return scope


def _scope_base(scope: str) -> str:
    """Fester Verzeichnis-Anteil vor dem ersten Wildcard-Segment."""
    parts = []
    for part in scope.split("/"):
        if any(ch in part for ch in "*?["):
            break
        parts.append(part)
    return "/".join(parts).rstrip("/")


def _is_glob(scope: str) -> bool:
    return any(ch in scope for ch in "*?[")


def _paths_related(x: str, y: str) -> bool:
    """Gleicher Pfad oder einer liegt unterhalb des anderen ("" = Projektwurzel)."""
    return (x == "" or y == "" or x == y
            or y.startswith(x + "/") or x.startswith(y + "/"))


def _literal_suffix(scope: str) -> str:
    """Fester Rest des letzten Segments nach dem letzten Wildcard-Zeichen.

    `docs/*.md` -> `.md`, `src/**` -> ``, `src/*/config.json` -> `config.json`.
    """
    last = scope.rstrip("/").split("/")[-1]
    idx = max(last.rfind(ch) for ch in "*?]")
    return last[idx + 1:]


def scopes_overlap(a: str, b: str) -> bool:
    """True, wenn zwei Schreibbereiche dieselbe Datei treffen koennen.

    Pfade relativ zum Projekt, Globs erlaubt (`src/api/**`, `docs/*.md`),
    ein abschliessendes `/` meint den ganzen Ordner. Ein fester Pfad, unter
    dem ein anderer Bereich liegt, gilt ebenfalls als Ordner (`src` vs.
    `src/app.py`). Bei zwei Globs ist die Pruefung konservativ: Konflikt,
    sobald die festen Verzeichnis-Anteile zusammenhaengen und die festen
    Dateiendungen sich nicht ausschliessen (`docs/*.md` vs. `docs/*.png`
    ist kein Konflikt).
    """
    a, b = _normalize_scope(a), _normalize_scope(b)
    if not a or not b:
        return False
    if a == b:
        return True

    glob_a, glob_b = _is_glob(a), _is_glob(b)

    if not glob_a and not glob_b:
        ta, tb = a.rstrip("/"), b.rstrip("/")
        return ta == tb or tb.startswith(ta + "/") or ta.startswith(tb + "/")

    if glob_a and glob_b:
        if not _paths_related(_scope_base(a), _scope_base(b)):
            return False
        sa, sb = _literal_suffix(a), _literal_suffix(b)
        if sa and sb and not (sa.endswith(sb) or sb.endswith(sa)):
            return False
        return True

    literal, pattern = (b, a) if glob_a else (a, b)
    lit = literal.rstrip("/")
    if fnmatch.fnmatch(lit, pattern):
        return True
    base = _scope_base(pattern)
    # Der feste Pfad ist ein Ordner, unter dem der Glob liegt.
    if base == lit or base.startswith(lit + "/"):
        return True
    # Ausdruecklicher Ordner innerhalb des Glob-Bereichs: Dateien darin
    # koennen passen.
    if literal.endswith("/") and _paths_related(base, lit):
        return True
    return False


# ── DAG-Kernlogik ───────────────────────────────────────────

class DAGBuilder:
    """Baut einen DAG aus TASK.md-Dateien und berechnet Waves."""

    def __init__(self, mission_dir: str):
        self.mission_dir = Path(mission_dir)
        self.tasks: dict[str, dict] = {}      # slug -> {frontmatter, path}
        self.edges: dict[str, list[str]] = {}  # slug -> [dependency-slugs]

    def discover_tasks(self) -> int:
        """Findet alle TASK.md-Dateien und extrahiert Metadaten."""
        tasks_dir = self.mission_dir / "tasks"
        if not tasks_dir.exists():
            return 0

        for task_file in sorted(tasks_dir.rglob("TASK.md")):
            fm = parse_frontmatter(task_file)
            slug = fm.get("slug", "")
            if not slug:
                slug = task_file.parent.name

            deps = fm.get("depends-on", [])
            if isinstance(deps, str):
                deps = [d.strip() for d in deps.split(",") if d.strip()]

            writes = fm.get("writes", [])
            if isinstance(writes, str):
                writes = [w.strip() for w in writes.split(",") if w.strip()]

            self.tasks[slug] = {
                "frontmatter": fm,
                "writes": writes,
                "path": str(task_file),
                "name": fm.get("name", slug),
                "status": fm.get("status", "OPEN"),
                "priority": fm.get("priority", "medium"),
                "assigned-to": fm.get("assigned-to", ""),
                "current_wave": fm.get("wave", None),
            }
            self.edges[slug] = deps

        return len(self.tasks)

    def detect_cycles(self) -> list[list[str]]:
        """Erkennt Zyklen im Abhängigkeitsgraphen mittels DFS."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {slug: WHITE for slug in self.tasks}
        cycles = []
        path: list[str] = []

        def dfs(node: str):
            color[node] = GRAY
            path.append(node)

            for dep in self.edges.get(node, []):
                if dep not in color:
                    continue  # Referenz auf nicht-existierenden Task
                if color[dep] == GRAY:
                    # Zyklus gefunden
                    cycle_start = path.index(dep)
                    cycles.append(path[cycle_start:] + [dep])
                elif color[dep] == WHITE:
                    dfs(dep)

            path.pop()
            color[node] = BLACK

        for slug in self.tasks:
            if color[slug] == WHITE:
                dfs(slug)

        return cycles

    def compute_waves(self) -> dict[str, int]:
        """Berechnet Wave-Zuordnung per topologischer Sortierung.
        Tasks ohne Abhängigkeiten → Wave 1.
        Tasks abhängig von Wave-N-Tasks → Wave N+1."""
        waves: dict[str, int] = {}
        remaining = set(self.tasks.keys())

        wave_num = 1
        max_iterations = len(self.tasks) + 1  # Sicherheit gegen Endlosschleife

        while remaining and max_iterations > 0:
            max_iterations -= 1
            ready = []
            for slug in remaining:
                deps = self.edges.get(slug, [])
                # Alle echten Abhängigkeiten (nur solche die als Tasks existieren)
                real_deps = [d for d in deps if d in self.tasks]
                if all(d in waves for d in real_deps):
                    ready.append(slug)

            if not ready:
                # Verbleibende Tasks haben zirkuläre Abhängigkeiten
                break

            for slug in ready:
                waves[slug] = wave_num
                remaining.discard(slug)

            wave_num += 1

        # Nicht zuordenbare Tasks (Zyklen) auf Wave -1 setzen
        for slug in remaining:
            waves[slug] = -1

        return waves

    def critical_path(self) -> list[str]:
        """Berechnet den kritischen Pfad (längste Kette von Abhängigkeiten)."""
        waves = self.compute_waves()
        if not waves:
            return []

        # Rückwärtssuche: Finde den Task mit der höchsten Wave
        max_wave = max(waves.values())
        # Finde alle Tasks in der höchsten Wave
        end_tasks = [s for s, w in waves.items() if w == max_wave]

        # Rekonstruiere den längsten Pfad rückwärts
        longest = []
        for end_task in end_tasks:
            path = self._trace_back(end_task, waves)
            if len(path) > len(longest):
                longest = path

        return longest

    def _trace_back(self, slug: str, waves: dict[str, int]) -> list[str]:
        """Verfolgt den längsten Pfad rückwärts von einem Task."""
        path = [slug]
        current = slug
        while True:
            deps = [d for d in self.edges.get(current, []) if d in waves]
            if not deps:
                break
            # Wähle die Abhängigkeit mit der höchsten Wave (= längster Pfad)
            deps.sort(key=lambda d: waves.get(d, 0), reverse=True)
            current = deps[0]
            path.append(current)
        path.reverse()
        return path

    def check_write_conflicts(self, waves: dict[str, int]) -> list[dict]:
        """Findet Tasks derselben Welle mit ueberlappenden Schreibbereichen.

        Tasks einer Welle laufen parallel. Schreiben zwei davon in dieselbe
        Datei oder denselben Ordner, gewinnt der letzte Schreiber, und die
        Arbeit des anderen verschwindet ohne Fehlermeldung. Geprueft werden
        nur Tasks, die `writes` deklarieren; ohne Angabe ist keine Aussage
        moeglich. Die Pruefung ist bewusst konservativ: im Zweifel gilt eine
        Ueberlappung als Konflikt.
        """
        conflicts = []
        by_wave: dict[int, list[str]] = defaultdict(list)
        for slug, wave in waves.items():
            if wave > 0 and self.tasks[slug]["writes"]:
                by_wave[wave].append(slug)

        for wave, slugs in sorted(by_wave.items()):
            slugs = sorted(slugs)
            for i, a in enumerate(slugs):
                for b in slugs[i + 1:]:
                    for pa in self.tasks[a]["writes"]:
                        for pb in self.tasks[b]["writes"]:
                            if scopes_overlap(pa, pb):
                                conflicts.append({
                                    "wave": wave,
                                    "tasks": [a, b],
                                    "scopes": [pa, pb],
                                })
        return conflicts

    def check_dangling_refs(self) -> list[tuple[str, str]]:
        """Findet Abhängigkeiten die auf nicht-existierende Tasks zeigen."""
        dangling = []
        for slug, deps in self.edges.items():
            for dep in deps:
                if dep not in self.tasks:
                    dangling.append((slug, dep))
        return dangling

    def apply_waves(self, waves: dict[str, int]) -> int:
        """Schreibt berechnete Wave-Nummern in die TASK.md-Dateien."""
        updated = 0
        for slug, wave in waves.items():
            if wave < 0:
                continue
            task_info = self.tasks[slug]
            filepath = Path(task_info["path"])
            content = filepath.read_text(encoding="utf-8")

            # wave: N im Frontmatter ersetzen
            new_content = re.sub(
                r'^(wave:\s*)\S+',
                f'wave: {wave}',
                content,
                count=1,
                flags=re.MULTILINE,
            )

            if new_content != content:
                filepath.write_text(new_content, encoding="utf-8")
                updated += 1

        return updated

    def to_json(self, waves: dict[str, int]) -> str:
        """Exportiert den DAG als JSON."""
        total_waves = max(waves.values()) if waves else 0
        wave_groups: dict[int, list] = defaultdict(list)
        for slug, wave in waves.items():
            task = self.tasks[slug]
            wave_groups[wave].append({
                "slug": slug,
                "name": task["name"],
                "depends-on": self.edges.get(slug, []),
                "assigned-to": task["assigned-to"],
                "priority": task["priority"],
                "status": task["status"],
                "writes": task["writes"],
            })

        result = {
            "total_tasks": len(self.tasks),
            "total_waves": total_waves,
            "critical_path": self.critical_path(),
            "write_conflicts": self.check_write_conflicts(waves),
            "waves": {str(w): tasks for w, tasks in sorted(wave_groups.items())},
        }
        return json.dumps(result, indent=2, ensure_ascii=False)


# ── Terminal-Ausgabe ────────────────────────────────────────

def format_dag(dag: DAGBuilder, waves: dict[str, int], show_critical: bool = False) -> str:
    """Formatiert den DAG als Terminal-Ausgabe."""
    lines = []
    is_tty = sys.stdout.isatty()

    # Farben
    if is_tty:
        GREEN = '\033[0;32m'
        YELLOW = '\033[1;33m'
        RED = '\033[0;31m'
        CYAN = '\033[0;36m'
        BOLD = '\033[1m'
        NC = '\033[0m'
    else:
        GREEN = YELLOW = RED = CYAN = BOLD = NC = ''

    lines.append("=" * 56)
    lines.append(f"  MissionForge DAG Builder — Automatische Wellenplanung")
    lines.append(f"  Tasks: {len(dag.tasks)}  |  Waves: {max(waves.values()) if waves else 0}")
    lines.append("=" * 56)

    # Dangling References
    dangling = dag.check_dangling_refs()
    if dangling:
        lines.append(f"\n{YELLOW}⚠ Nicht aufgeloeste Abhaengigkeiten:{NC}")
        for src, target in dangling:
            lines.append(f"  {src} → {target} (existiert nicht)")

    # Waves
    total_waves = max(waves.values()) if waves else 0
    for w in range(1, total_waves + 1):
        tasks_in_wave = [(s, dag.tasks[s]) for s, wv in waves.items() if wv == w]
        lines.append(f"\n{BOLD}── Welle {w} ──{NC}  ({len(tasks_in_wave)} Tasks parallel)")

        for slug, info in sorted(tasks_in_wave, key=lambda x: x[0]):
            deps = dag.edges.get(slug, [])
            dep_str = f" ← {', '.join(deps)}" if deps else ""
            status_color = GREEN if info["status"] in ("DONE", "VERIFIED") else \
                          RED if info["status"] == "FAILED" else YELLOW
            priority = info["priority"]
            pri_marker = "!" if priority == "critical" else \
                        "▲" if priority == "high" else \
                        "─" if priority == "medium" else "▽"
            lines.append(
                f"  {pri_marker} {CYAN}{slug:<16}{NC} "
                f"{status_color}{info['status']:<12}{NC} "
                f"→ {info['assigned-to']}"
                f"{dep_str}"
            )

    # Zyklische Tasks
    cyclic = [s for s, w in waves.items() if w < 0]
    if cyclic:
        lines.append(f"\n{RED}✗ Zyklische Abhaengigkeiten (nicht planbar):{NC}")
        for slug in cyclic:
            deps = dag.edges.get(slug, [])
            lines.append(f"  {slug} ← {', '.join(deps)}")

    # Schreibkonflikte
    conflicts = dag.check_write_conflicts(waves)
    if conflicts:
        lines.append(f"\n{RED}✗ Schreibkonflikte (parallele Tasks derselben Welle):{NC}")
        for c in conflicts:
            lines.append(
                f"  Welle {c['wave']}: {c['tasks'][0]} ({c['scopes'][0]}) "
                f"↔ {c['tasks'][1]} ({c['scopes'][1]})"
            )
        lines.append("  → Schreibbereiche trennen oder einen Task per depends-on in eine spaetere Welle schieben.")

    # Critical Path
    if show_critical:
        cp = dag.critical_path()
        if cp:
            lines.append(f"\n{BOLD}── Kritischer Pfad ──{NC}  ({len(cp)} Tasks, {total_waves} Waves)")
            lines.append(f"  {' → '.join(cp)}")

    return "\n".join(lines)


# ── Selbsttest ──────────────────────────────────────────────

def self_test():
    """Integrierter Selbsttest mit temporärer Mission-Struktur."""
    import tempfile
    import shutil

    print("🧪 DAG Builder — Selbsttest\n")
    tmpdir = Path(tempfile.mkdtemp())
    mission = tmpdir / ".mission-forge"
    tasks = mission / "tasks"

    try:
        # Task A: keine Abhängigkeiten
        (tasks / "wp-001").mkdir(parents=True)
        (tasks / "wp-001" / "TASK.md").write_text(
            '---\nschema: missionforge/v1\nkind: task\nslug: wp-001\n'
            'name: "Setup"\nassigned-to: agents/dev\nstatus: OPEN\n'
            'priority: high\nwave: 0\ndepends-on: []\nrequirements:\n  - REQ-001\n---\n'
        )

        # Task B: hängt von A ab
        (tasks / "wp-002").mkdir(parents=True)
        (tasks / "wp-002" / "TASK.md").write_text(
            '---\nschema: missionforge/v1\nkind: task\nslug: wp-002\n'
            'name: "Build"\nassigned-to: agents/dev\nstatus: OPEN\n'
            'priority: medium\nwave: 0\ndepends-on:\n  - wp-001\nrequirements:\n  - REQ-002\n---\n'
        )

        # Task C: hängt von A ab (parallel zu B)
        (tasks / "wp-003").mkdir(parents=True)
        (tasks / "wp-003" / "TASK.md").write_text(
            '---\nschema: missionforge/v1\nkind: task\nslug: wp-003\n'
            'name: "Test"\nassigned-to: agents/qa\nstatus: OPEN\n'
            'priority: medium\nwave: 0\ndepends-on:\n  - wp-001\nrequirements:\n  - REQ-003\n---\n'
        )

        # Task D: hängt von B und C ab
        (tasks / "wp-004").mkdir(parents=True)
        (tasks / "wp-004" / "TASK.md").write_text(
            '---\nschema: missionforge/v1\nkind: task\nslug: wp-004\n'
            'name: "Deploy"\nassigned-to: agents/ops\nstatus: OPEN\n'
            'priority: critical\nwave: 0\ndepends-on:\n  - wp-002\n  - wp-003\nrequirements:\n  - REQ-004\n---\n'
        )

        dag = DAGBuilder(str(mission))
        count = dag.discover_tasks()
        assert count == 4, f"Erwartet 4 Tasks, gefunden: {count}"
        print(f"  ✅ {count} Tasks gefunden")

        cycles = dag.detect_cycles()
        assert len(cycles) == 0, f"Unerwartete Zyklen: {cycles}"
        print(f"  ✅ Keine Zyklen erkannt")

        waves = dag.compute_waves()
        assert waves["wp-001"] == 1, f"wp-001 sollte Wave 1 sein: {waves['wp-001']}"
        assert waves["wp-002"] == 2, f"wp-002 sollte Wave 2 sein: {waves['wp-002']}"
        assert waves["wp-003"] == 2, f"wp-003 sollte Wave 2 sein: {waves['wp-003']}"
        assert waves["wp-004"] == 3, f"wp-004 sollte Wave 3 sein: {waves['wp-004']}"
        print(f"  ✅ Wave-Berechnung korrekt: {waves}")

        cp = dag.critical_path()
        assert len(cp) == 3, f"Kritischer Pfad sollte 3 Tasks haben: {cp}"
        assert cp[0] == "wp-001", f"Kritischer Pfad startet falsch: {cp}"
        print(f"  ✅ Kritischer Pfad: {' → '.join(cp)}")

        dangling = dag.check_dangling_refs()
        assert len(dangling) == 0, f"Unerwartete Dangling-Refs: {dangling}"
        print(f"  ✅ Keine Dangling-Referenzen")

        # --apply testen
        updated = dag.apply_waves(waves)
        assert updated == 4, f"Erwartet 4 Updates: {updated}"
        # Nachlesen und prüfen
        content = (tasks / "wp-004" / "TASK.md").read_text()
        assert "wave: 3" in content, "wave: 3 nicht in wp-004 geschrieben"
        print(f"  ✅ --apply: {updated} Dateien aktualisiert")

        # Schreibkonflikte: wp-002 und wp-003 laufen parallel in Welle 2
        assert dag.check_write_conflicts(waves) == [], "Ohne writes kein Konflikt erwartet"
        dag.tasks["wp-002"]["writes"] = ["src/api/"]
        dag.tasks["wp-003"]["writes"] = ["tests/**", "src/api/handlers.py"]
        dag.tasks["wp-004"]["writes"] = ["src/api/"]  # andere Welle, kein Konflikt
        conflicts = dag.check_write_conflicts(waves)
        assert len(conflicts) == 1, f"Erwartet 1 Konflikt: {conflicts}"
        assert conflicts[0]["wave"] == 2 and conflicts[0]["tasks"] == ["wp-002", "wp-003"]
        dag.tasks["wp-003"]["writes"] = ["tests/**", "docs/*.md"]
        assert dag.check_write_conflicts(waves) == [], "Getrennte Bereiche melden Konflikt"
        print(f"  ✅ Schreibkonflikte in parallelen Wellen erkannt")

        for a, b, expected in [
            ("src/app.py", "src/app.py", True),
            ("./src/app.py", "src/app.py", True),
            ("src/**", "src/api/x.py", True),
            ("src/", "src/api/x.py", True),
            ("docs/*.md", "docs/intro.md", True),
            ("src/api/", "src/apiclient/x.py", False),
            ("docs/*.md", "src/app.py", False),
            ("**", "irgendwas.txt", True),
            ("src", "src/app.py", True),
            ("docs/", "docs/*.md", True),
            ("src/api/", "src/*.py", True),
            ("tests/**", "tests/*.py", True),
            # Fehlalarme vermeiden: fremde Endung, fremder Ordner
            ("docs/*.md", "docs/logo.png", False),
            ("*.md", "src/app.py", False),
            ("docs/*.md", "docs/*.png", False),
            ("**/*.test.ts", "src/app.py", False),
            ("src/*/config.json", "src/*/*.md", False),
            ("src/api/**", "docs/*.md", False),
        ]:
            assert scopes_overlap(a, b) is expected, f"scopes_overlap({a!r}, {b!r}) != {expected}"
            assert scopes_overlap(b, a) is expected, f"scopes_overlap({b!r}, {a!r}) != {expected}"
        print(f"  ✅ Ueberlappungsregeln fuer Pfade und Globs")

        print(f"\n✅ Alle Tests bestanden!")
        return 0

    finally:
        shutil.rmtree(tmpdir)


# ── CLI ──────────────────────────────────────────────────────

def main():
    if "--test" in sys.argv:
        sys.exit(self_test())

    mission_dir = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else ".mission-forge"
    apply_mode = "--apply" in sys.argv
    json_mode = "--json" in sys.argv
    critical_mode = "--critical-path" in sys.argv

    if not Path(mission_dir).exists():
        print(f"Fehler: Verzeichnis '{mission_dir}' existiert nicht.", file=sys.stderr)
        sys.exit(2)

    dag = DAGBuilder(mission_dir)
    count = dag.discover_tasks()

    if count == 0:
        print(f"Keine TASK.md-Dateien in {mission_dir}/tasks/ gefunden.", file=sys.stderr)
        sys.exit(2)

    # Zyklen prüfen
    cycles = dag.detect_cycles()
    if cycles:
        print(f"\n❌ ZYKLEN ERKANNT — Automatische Wellenplanung nicht moeglich!\n", file=sys.stderr)
        for cycle in cycles:
            print(f"  Zyklus: {' → '.join(cycle)}", file=sys.stderr)
        print(f"\nBitte depends-on-Felder in diesen Tasks korrigieren.", file=sys.stderr)
        sys.exit(1)

    waves = dag.compute_waves()

    if json_mode:
        print(dag.to_json(waves))
    else:
        print(format_dag(dag, waves, show_critical=critical_mode))

    if apply_mode:
        updated = dag.apply_waves(waves)
        print(f"\n✅ {updated} TASK.md-Dateien aktualisiert (wave-Feld geschrieben)")

    if dag.check_write_conflicts(waves):
        sys.exit(3)
    sys.exit(0)


if __name__ == "__main__":
    main()
