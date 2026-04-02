#!/usr/bin/env python3
"""
MissionForge Schema Validator — Strukturelle Manifest-Pruefung
===============================================================
Validiert YAML-Frontmatter aller Manifest-Dateien gegen definierte Schemas.
Prueft Feldwerte, Typen, Cross-Referenzen und semantische Konsistenz.

Inspiriert von claude-codes Zod-Schema-Validierung: Fehler VOR Ausfuehrung fangen.

Usage:
    python scripts/validate-schema.py [path-to-.mission-forge]
    python scripts/validate-schema.py .mission-forge --strict     # Warnings = Errors
    python scripts/validate-schema.py .mission-forge --json        # JSON-Output
    python scripts/validate-schema.py --test                       # Selbsttest

Exit codes: 0 = OK, 1 = Validierungsfehler, 2 = Systemfehler
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional


# ── YAML-Frontmatter Parser ────────────────────────────────

def parse_frontmatter(filepath: Path) -> dict:
    """Extrahiert YAML-Frontmatter zwischen --- Markern."""
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
    # Track nested keys (metadata.X)
    parent_key = None
    indent_level = 0

    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Aktuelle Einrückung messen
        current_indent = len(line) - len(line.lstrip())

        # Listen-Eintrag
        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
                if parent_key:
                    if parent_key not in result or not isinstance(result[parent_key], dict):
                        result[parent_key] = {}
                    result[parent_key][current_key] = current_list
                else:
                    result[current_key] = current_list
            current_list.append(stripped[2:].strip().strip('"').strip("'"))
            continue

        # Key: Value
        match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_.-]*)\s*:\s*(.*)', line)
        if match:
            key = match.group(1)
            value = match.group(2).strip().strip('"').strip("'")
            current_list = None

            if current_indent == 0:
                parent_key = None
                current_key = key

                if value == "" or value == ">":
                    result[current_key] = ""
                elif value.startswith("[") and value.endswith("]"):
                    items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
                    result[current_key] = [i for i in items if i]
                    current_list = result[current_key]
                else:
                    result[current_key] = value

                # Prüfe ob dies ein Parent-Key wird (z.B. metadata:)
                if value == "" or value == ">":
                    parent_key = key
            elif current_indent > 0 and parent_key:
                current_key = key
                if parent_key not in result:
                    result[parent_key] = {}
                if isinstance(result[parent_key], str):
                    result[parent_key] = {}

                if value == "" or value == ">":
                    result[parent_key][current_key] = ""
                elif value.startswith("[") and value.endswith("]"):
                    items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
                    result[parent_key][current_key] = [i for i in items if i]
                    current_list = result[parent_key][current_key]
                else:
                    result[parent_key][current_key] = value

    return result


# ── Schema-Definitionen ────────────────────────────────────

VALID_STATUSES = {"OPEN", "IN_PROGRESS", "DONE", "VERIFIED", "FAILED", "ESCALATED", "SKIPPED", "ABORTED"}
VALID_PRIORITIES = {"critical", "high", "medium", "low"}
VALID_KINDS = {"company", "team", "agent", "project", "task", "skill"}
VALID_MODEL_PREFS = {"opus", "sonnet", "haiku"}
VALID_COMPLEXITY = {"S", "M", "L", "XL"}

SCHEMAS = {
    "COMPANY.md": {
        "required": ["schema", "kind", "slug", "name", "description"],
        "recommended": ["version", "tags"],
        "kind_value": "company",
        "field_validators": {
            "schema": lambda v: v.startswith("missionforge/") or v.startswith("agentcompanies/"),
            "kind": lambda v: v == "company",
            "slug": lambda v: bool(re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', v)) or len(v) <= 2,
        },
    },
    "TEAM.md": {
        "required": ["schema", "kind", "slug", "name", "description", "manager"],
        "recommended": ["includes", "tags"],
        "kind_value": "team",
        "field_validators": {
            "kind": lambda v: v == "team",
            "manager": lambda v: v.startswith("agents/") or v.startswith("../agents/"),
        },
    },
    "AGENTS.md": {
        "required": ["schema", "kind", "slug", "name", "description", "reports-to"],
        "recommended": ["skills", "metadata"],
        "kind_value": "agent",
        "field_validators": {
            "kind": lambda v: v == "agent",
        },
        "metadata_validators": {
            "model-preference": lambda v: v in VALID_MODEL_PREFS,
            "read-only": lambda v: v in ("true", "false"),
        },
    },
    "PROJECT.md": {
        "required": ["schema", "kind", "slug", "name", "description"],
        "recommended": ["status", "tags"],
        "kind_value": "project",
        "field_validators": {
            "kind": lambda v: v == "project",
            "status": lambda v: v in {"PLANNED", "IN_PROGRESS", "DONE"},
        },
    },
    "TASK.md": {
        "required": ["schema", "kind", "slug", "name", "description", "assigned-to", "status", "wave", "requirements"],
        "recommended": ["priority", "depends-on"],
        "kind_value": "task",
        "field_validators": {
            "kind": lambda v: v == "task",
            "status": lambda v: v in VALID_STATUSES,
            "priority": lambda v: v in VALID_PRIORITIES,
            "wave": lambda v: v.isdigit() or v == "0",
            "assigned-to": lambda v: v.startswith("agents/"),
        },
        "metadata_validators": {
            "estimated-complexity": lambda v: v in VALID_COMPLEXITY,
        },
    },
    "SKILL.md": {
        "required": ["name", "description"],
        "recommended": ["license", "compatibility"],
        "kind_value": "skill",
        "field_validators": {
            "name": lambda v: bool(re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', v)) or len(v) <= 2,
        },
    },
}


# ── Validator ───────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.ok_count: int = 0
        self.files_checked: int = 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def ok(self):
        self.ok_count += 1

    def to_json(self) -> str:
        return json.dumps({
            "valid": not self.has_errors,
            "files_checked": self.files_checked,
            "errors": self.errors,
            "warnings": self.warnings,
            "ok_count": self.ok_count,
        }, indent=2, ensure_ascii=False)


class SchemaValidator:
    """Validiert MissionForge-Manifeste gegen definierte Schemas."""

    def __init__(self, mission_dir: str):
        self.mission_dir = Path(mission_dir)
        self.result = ValidationResult()
        # Gesammelte Daten für Cross-Referenz-Prüfung
        self.known_agents: set[str] = set()
        self.known_tasks: set[str] = set()
        self.known_teams: set[str] = set()
        self.task_deps: dict[str, list[str]] = {}
        self.task_waves: dict[str, int] = {}
        self.req_ids_in_tasks: set[str] = set()
        self.req_ids_in_state: set[str] = set()

    def validate_all(self) -> ValidationResult:
        """Validiert alle Manifeste in der Mission-Struktur."""

        if not self.mission_dir.exists():
            self.result.error(f"Verzeichnis existiert nicht: {self.mission_dir}")
            return self.result

        # Phase 1: Alle Manifeste sammeln und einzeln validieren
        for md_file in sorted(self.mission_dir.rglob("*.md")):
            rel = md_file.relative_to(self.mission_dir)
            # Nur bekannte Manifest-Typen validieren
            if md_file.name in SCHEMAS:
                self._validate_file(md_file)

        # Phase 2: Cross-Referenzen prüfen
        self._validate_cross_refs()

        # Phase 3: Semantische Konsistenz
        self._validate_semantics()

        return self.result

    def _validate_file(self, filepath: Path):
        """Validiert eine einzelne Manifest-Datei."""
        self.result.files_checked += 1
        rel_path = filepath.relative_to(self.mission_dir)
        schema_name = filepath.name
        schema = SCHEMAS.get(schema_name)

        if not schema:
            return

        # Frontmatter extrahieren
        fm = parse_frontmatter(filepath)
        if not fm:
            self.result.error(f"{rel_path}: Kein YAML-Frontmatter gefunden")
            return

        # Pflichtfelder prüfen
        for field in schema["required"]:
            if field not in fm or (isinstance(fm[field], str) and not fm[field]):
                self.result.error(f"{rel_path}: Pflichtfeld '{field}' fehlt oder ist leer")
            else:
                self.result.ok()

        # Empfohlene Felder prüfen
        for field in schema.get("recommended", []):
            if field not in fm:
                self.result.warn(f"{rel_path}: Empfohlenes Feld '{field}' fehlt")

        # Feldwert-Validierung
        validators = schema.get("field_validators", {})
        for field, validator in validators.items():
            value = fm.get(field)
            if value and isinstance(value, str):
                if not validator(value):
                    self.result.error(
                        f"{rel_path}: Feld '{field}' hat ungueltigen Wert: '{value}'"
                    )

        # Metadata-Validierung
        meta_validators = schema.get("metadata_validators", {})
        metadata = fm.get("metadata", {})
        if isinstance(metadata, dict):
            for field, validator in meta_validators.items():
                value = metadata.get(field)
                if value and not validator(value):
                    self.result.error(
                        f"{rel_path}: metadata.{field} hat ungueltigen Wert: '{value}'"
                    )

        # Daten für Cross-Referenzen sammeln
        slug = fm.get("slug", "")
        kind = fm.get("kind", "")

        if kind == "agent" or schema_name == "AGENTS.md":
            # Agent-Pfad registrieren
            parent_dir = filepath.parent.name
            self.known_agents.add(f"agents/{parent_dir}")

        elif kind == "task" or schema_name == "TASK.md":
            self.known_tasks.add(slug)
            deps = fm.get("depends-on", [])
            if isinstance(deps, str):
                deps = [d.strip() for d in deps.split(",") if d.strip()]
            self.task_deps[slug] = deps
            wave = fm.get("wave", "0")
            try:
                self.task_waves[slug] = int(wave)
            except (ValueError, TypeError):
                pass

            # REQ-IDs sammeln
            reqs = fm.get("requirements", [])
            if isinstance(reqs, str):
                reqs = [reqs]
            for req in reqs:
                if req:
                    self.req_ids_in_tasks.add(req)

        elif kind == "team" or schema_name == "TEAM.md":
            self.known_teams.add(slug)

    def _validate_cross_refs(self):
        """Prüft Cross-Referenzen zwischen Manifesten."""

        # Task depends-on muss auf existierende Tasks zeigen
        for slug, deps in self.task_deps.items():
            for dep in deps:
                if dep and dep not in self.known_tasks:
                    self.result.error(
                        f"Task '{slug}': depends-on '{dep}' referenziert nicht-existierenden Task"
                    )

        # Task assigned-to muss auf existierende Agents zeigen
        for task_file in sorted(self.mission_dir.rglob("TASK.md")):
            fm = parse_frontmatter(task_file)
            assigned = fm.get("assigned-to", "")
            if assigned and self.known_agents and assigned not in self.known_agents:
                rel_path = task_file.relative_to(self.mission_dir)
                self.result.warn(
                    f"{rel_path}: assigned-to '{assigned}' — Agent nicht gefunden"
                )

    def _validate_semantics(self):
        """Prüft semantische Konsistenz."""

        # Wave-Konsistenz: Abhängigkeiten müssen in früheren Waves sein
        for slug, deps in self.task_deps.items():
            my_wave = self.task_waves.get(slug, 0)
            for dep in deps:
                dep_wave = self.task_waves.get(dep, 0)
                if dep_wave >= my_wave and my_wave > 0 and dep_wave > 0:
                    self.result.error(
                        f"Task '{slug}' (Wave {my_wave}) haengt von '{dep}' (Wave {dep_wave}) ab "
                        f"— Abhaengigkeit muss in frueherer Wave sein"
                    )

        # STATE.md REQ-Coverage prüfen
        state_file = self.mission_dir / "STATE.md"
        if state_file.exists():
            state_text = state_file.read_text(encoding="utf-8")
            state_reqs = set(re.findall(r'REQ-\d+', state_text))
            if state_reqs and self.req_ids_in_tasks:
                uncovered = state_reqs - self.req_ids_in_tasks
                for req in sorted(uncovered):
                    self.result.warn(
                        f"STATE.md: {req} ist in der Traceability-Matrix "
                        f"aber in keiner TASK.md referenziert (Zero-Drop-Verletzung)"
                    )


# ── Terminal-Ausgabe ────────────────────────────────────────

def print_result(result: ValidationResult, is_tty: bool = True):
    """Formatierte Terminal-Ausgabe."""
    if is_tty:
        RED = '\033[0;31m'
        YELLOW = '\033[1;33m'
        GREEN = '\033[0;32m'
        NC = '\033[0m'
    else:
        RED = YELLOW = GREEN = NC = ''

    print("=" * 56)
    print("  MissionForge Schema Validator")
    print("=" * 56)

    if result.errors:
        print(f"\n{RED}── Fehler ({len(result.errors)}) ──{NC}\n")
        for err in result.errors:
            print(f"  {RED}✗{NC} {err}")

    if result.warnings:
        print(f"\n{YELLOW}── Warnungen ({len(result.warnings)}) ──{NC}\n")
        for warn in result.warnings:
            print(f"  {YELLOW}⚠{NC} {warn}")

    print(f"\n{'─' * 56}")
    print(f"  Dateien geprueft: {result.files_checked}")
    print(f"  Felder OK:        {GREEN}{result.ok_count}{NC}")
    print(f"  Warnungen:        {YELLOW}{len(result.warnings)}{NC}")
    print(f"  Fehler:           {RED}{len(result.errors)}{NC}")
    print()

    if not result.has_errors:
        print(f"  {GREEN}✅ Schema-Validierung bestanden{NC}")
    else:
        print(f"  {RED}❌ {len(result.errors)} Fehler gefunden. Bitte beheben.{NC}")


# ── Selbsttest ──────────────────────────────────────────────

def self_test():
    """Integrierter Selbsttest."""
    import tempfile
    import shutil

    print("🧪 Schema Validator — Selbsttest\n")
    tmpdir = Path(tempfile.mkdtemp())
    mission = tmpdir / ".mission-forge"

    try:
        # Gültige COMPANY.md
        mission.mkdir(parents=True)
        (mission / "COMPANY.md").write_text(
            '---\nschema: missionforge/v1\nkind: company\nslug: test-co\n'
            'name: "Test Company"\ndescription: "Eine Testfirma"\n---\n# Test\n'
        )

        # Gültiger Agent
        (mission / "agents" / "dev").mkdir(parents=True)
        (mission / "agents" / "dev" / "AGENTS.md").write_text(
            '---\nschema: missionforge/v1\nkind: agent\nslug: dev\n'
            'name: "Developer"\ndescription: "Entwickler"\nreports-to: mission-orchestrator\n---\n'
        )

        # Gültiger Task
        (mission / "tasks" / "wp-001").mkdir(parents=True)
        (mission / "tasks" / "wp-001" / "TASK.md").write_text(
            '---\nschema: missionforge/v1\nkind: task\nslug: wp-001\n'
            'name: "Setup"\ndescription: "Initiales Setup"\nassigned-to: agents/dev\n'
            'status: OPEN\npriority: high\nwave: 1\nrequirements:\n  - REQ-001\n---\n'
        )

        # Ungültiger Task (falscher Status)
        (mission / "tasks" / "wp-bad").mkdir(parents=True)
        (mission / "tasks" / "wp-bad" / "TASK.md").write_text(
            '---\nschema: missionforge/v1\nkind: task\nslug: wp-bad\n'
            'name: "Bad Task"\ndescription: "Ungueltig"\nassigned-to: agents/dev\n'
            'status: UNKNOWN\npriority: ultra\nwave: 1\nrequirements:\n  - REQ-002\n---\n'
        )

        validator = SchemaValidator(str(mission))
        result = validator.validate_all()

        # Prüfe dass Fehler für ungültige Werte erkannt wurden
        status_errors = [e for e in result.errors if "status" in e and "UNKNOWN" in e]
        assert len(status_errors) > 0, "Ungueltiger Status sollte Fehler erzeugen"
        print("  ✅ Ungueltiger Status erkannt")

        priority_errors = [e for e in result.errors if "priority" in e and "ultra" in e]
        assert len(priority_errors) > 0, "Ungueltige Prioritaet sollte Fehler erzeugen"
        print("  ✅ Ungueltige Prioritaet erkannt")

        # Gültige Dateien sollten keine Fehler haben
        company_errors = [e for e in result.errors if "COMPANY.md" in e]
        assert len(company_errors) == 0, f"COMPANY.md sollte valide sein: {company_errors}"
        print("  ✅ Gueltige COMPANY.md akzeptiert")

        agent_errors = [e for e in result.errors if "AGENTS.md" in e]
        assert len(agent_errors) == 0, f"AGENTS.md sollte valide sein: {agent_errors}"
        print("  ✅ Gueltiger Agent akzeptiert")

        print(f"\n  Gesamt: {result.files_checked} Dateien, {len(result.errors)} Fehler, {len(result.warnings)} Warnungen")
        print(f"\n✅ Alle Tests bestanden!")
        return 0

    finally:
        shutil.rmtree(tmpdir)


# ── CLI ──────────────────────────────────────────────────────

def main():
    if "--test" in sys.argv:
        sys.exit(self_test())

    mission_dir = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else ".mission-forge"
    strict_mode = "--strict" in sys.argv
    json_mode = "--json" in sys.argv

    validator = SchemaValidator(mission_dir)
    result = validator.validate_all()

    if strict_mode:
        # Warnings werden zu Errors
        result.errors.extend(result.warnings)
        result.warnings = []

    if json_mode:
        print(result.to_json())
    else:
        print_result(result, is_tty=sys.stdout.isatty())

    sys.exit(1 if result.has_errors else 0)


if __name__ == "__main__":
    main()
