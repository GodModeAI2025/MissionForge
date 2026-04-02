#!/usr/bin/env python3
"""
AuditChain — Kryptographische Beweiskette für MissionForge
===========================================================
Append-only Hash-Chain: Jeder Eintrag referenziert den Hash des
vorherigen. Manipulation eines Eintrags bricht die Kette.

Skills und Artefakte werden mitgehasht — nachweisbar, nach welchen
Anweisungen ein Agent gearbeitet hat und ob sich Ergebnisse verändert haben.

Verwendung:
    from chain import AuditChain

    ac = AuditChain(".mission-forge/audit")
    ac.genesis("MISSION-042", goals=["API bauen"], actors=["agent-01"],
               skill_files={"main": "SKILL.md", "testing": "skills/test/SKILL.md"})
    ac.log("TASK_STATUS_CHANGE", ref="WP-003", data={
        "from": "IN_PROGRESS", "to": "DONE",
        "artifact_hash": AuditChain.hash_file("output.py"),
    })
    ac.log_skill_change(ref="EXP-005", skill_name="humanizer",
                        skill_path="skills/humanizer/SKILL.md",
                        reason="Mutation: Personality-Schritt ergänzt")

CLI:
    python chain.py log        <audit_dir> <event> <ref> [key=value ...]
    python chain.py genesis    <audit_dir> <mission_id> [--skill name=path ...]
    python chain.py verify     <audit_dir>
    python chain.py show       <audit_dir> [--last N]
    python chain.py summary    <audit_dir>
    python chain.py hash-file  <audit_dir> <filepath>
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


CHAIN_FILE = "CHAIN.jsonl"
GENESIS_EVENT = "GENESIS"


class ChainIntegrityError(Exception):
    """Wird geworfen wenn die Hash-Kette gebrochen ist."""
    pass


class AuditChain:
    """Append-only Hash-Chain mit SHA-256-Verkettung."""

    def __init__(self, audit_dir: str):
        self.audit_dir = Path(audit_dir)
        self.chain_file = self.audit_dir / CHAIN_FILE
        self.audit_dir.mkdir(parents=True, exist_ok=True)

    # ── Kern-Operationen ─────────────────────────────────────

    def log(
        self,
        event: str,
        ref: str = "",
        data: Optional[dict[str, Any]] = None,
        agent: str = "",
    ) -> dict:
        """Neuen Eintrag an die Chain anhängen. Gibt den Eintrag zurück."""
        prev_hash = self._get_last_hash()
        seq = self._get_next_seq()

        entry = {
            "seq": seq,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "event": event,
            "ref": ref,
            "agent": agent,
            "data": data or {},
            "prev_hash": prev_hash,
        }

        # entry_hash wird über den gesamten Eintrag OHNE entry_hash berechnet
        entry["entry_hash"] = self._compute_hash(entry)

        with open(self.chain_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

        return entry

    def genesis(self, mission_id: str, goals: list[str], actors: list[str],
                skill_files: Optional[dict[str, str]] = None) -> dict:
        """Genesis-Block: Erster Eintrag der Kette.
        
        skill_files: Dict von {name: dateipfad} — jeder Skill wird gehasht
                     und im Genesis-Block versiegelt. Damit ist nachweisbar,
                     nach welchen Anweisungen die Agenten gearbeitet haben.
        """
        if self.chain_file.exists() and self.chain_file.stat().st_size > 0:
            raise ValueError("Chain existiert bereits. Genesis nur einmal erlaubt.")

        data = {
            "mission_id": mission_id,
            "goals": goals,
            "actors": actors,
            "chain_version": "1.1.0",
            "algorithm": "sha256",
        }

        if skill_files:
            data["skill_hashes"] = {
                name: self.hash_file(path) for name, path in skill_files.items()
            }

        return self.log(
            event=GENESIS_EVENT,
            ref=mission_id,
            data=data,
        )

    def log_skill_change(self, ref: str, skill_name: str, skill_path: str,
                         agent: str = "", reason: str = "") -> dict:
        """Protokolliert eine Skill-Änderung mit dem Hash der neuen Version."""
        return self.log(
            event="SKILL_CHANGED",
            ref=ref,
            agent=agent,
            data={
                "skill_name": skill_name,
                "skill_hash": self.hash_file(skill_path),
                "reason": reason,
            },
        )

    # ── Phase-D Erweiterungen ────────────────────────────────

    def log_cost(self, ref: str, agent: str, input_tokens: int,
                 output_tokens: int, cost_usd: float, model: str = "") -> dict:
        """Protokolliert Token-Verbrauch und Kosten eines Agenten."""
        return self.log(
            event="COST_TRACKED",
            ref=ref,
            agent=agent,
            data={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": round(cost_usd, 4),
                "model": model,
            },
        )

    def log_context_budget(self, ref: str, agent: str,
                           estimated_tokens: int, budget_tokens: int,
                           utilization_pct: float) -> dict:
        """Protokolliert Context-Budget vor Agent-Spawn."""
        return self.log(
            event="CONTEXT_BUDGET",
            ref=ref,
            agent=agent,
            data={
                "estimated_tokens": estimated_tokens,
                "budget_tokens": budget_tokens,
                "utilization_pct": round(utilization_pct, 1),
                "within_budget": estimated_tokens <= budget_tokens,
            },
        )

    def log_error(self, ref: str, agent: str, category: str,
                  description: str, attempt: int = 1,
                  recommendation: str = "") -> dict:
        """Protokolliert einen kategorisierten Fehler (E1-E5)."""
        return self.log(
            event="ERROR_CATEGORIZED",
            ref=ref,
            agent=agent,
            data={
                "category": category,
                "description": description,
                "attempt": attempt,
                "recommendation": recommendation,
            },
        )

    def log_mcp_call(self, ref: str, agent: str, server: str,
                     tool: str, input_hash: str = "",
                     output_hash: str = "") -> dict:
        """Protokolliert einen MCP-Tool-Aufruf."""
        return self.log(
            event="MCP_TOOL_CALL",
            ref=ref,
            agent=agent,
            data={
                "server": server,
                "tool": tool,
                "input_hash": input_hash,
                "output_hash": output_hash,
            },
        )

    def log_mode_set(self, ref: str, mode: str) -> dict:
        """Protokolliert den gewählten Operational Mode."""
        return self.log(
            event="MODE_SET",
            ref=ref,
            data={"mode": mode},
        )

    # ── Execution Gateway ────────────────────────────────────

    def gate_check(
        self,
        action: str,
        agent: str,
        ref: str = "",
        policies: Optional[list[dict[str, Any]]] = None,
    ) -> tuple[bool, dict]:
        """
        Pre-Flight-Prüfung: Darf der Agent diese Aktion ausführen?

        policies: Liste von Policy-Dicts mit:
            - "name": Name der Policy
            - "allowed_actions": Liste erlaubter Actions (Wildcards mit *)
            - "blocked_actions": Liste blockierter Actions
            - "max_priority": Höchste erlaubte Priorität ("low"|"medium"|"high"|"critical")
            - "require_approval": Wenn True, wird die Aktion als PENDING geloggt
            - "allowed_agents": Liste erlaubter Agenten (leer = alle)

        Gibt (allowed: bool, entry: dict) zurück.
        Die Entscheidung wird in jedem Fall in der Chain protokolliert.
        """
        if not policies:
            # Ohne Policies ist alles erlaubt, aber protokolliert
            entry = self.log(
                event="GATE_PASSED",
                ref=ref,
                agent=agent,
                data={"action": action, "reason": "no_policies_defined"},
            )
            return True, entry

        violations = []
        for policy in policies:
            pname = policy.get("name", "unnamed")

            # Blocked Actions prüfen
            blocked = policy.get("blocked_actions", [])
            for pattern in blocked:
                if self._action_matches(action, pattern):
                    violations.append(f"{pname}: action '{action}' is blocked by '{pattern}'")

            # Allowed Actions prüfen (wenn definiert, muss mindestens eine matchen)
            allowed = policy.get("allowed_actions", [])
            if allowed:
                if not any(self._action_matches(action, p) for p in allowed):
                    violations.append(f"{pname}: action '{action}' not in allowed list")

            # Agent-Berechtigung prüfen
            allowed_agents = policy.get("allowed_agents", [])
            if allowed_agents and agent not in allowed_agents:
                violations.append(f"{pname}: agent '{agent}' not authorized")

        if violations:
            entry = self.log(
                event="GATE_BLOCKED",
                ref=ref,
                agent=agent,
                data={
                    "action": action,
                    "violations": violations,
                    "policy_count": len(policies),
                },
            )
            return False, entry

        # Approval-Check
        needs_approval = any(p.get("require_approval") for p in policies)
        if needs_approval:
            entry = self.log(
                event="GATE_PENDING_APPROVAL",
                ref=ref,
                agent=agent,
                data={
                    "action": action,
                    "reason": "policy requires approval",
                },
            )
            return False, entry

        entry = self.log(
            event="GATE_PASSED",
            ref=ref,
            agent=agent,
            data={
                "action": action,
                "policies_checked": len(policies),
            },
        )
        return True, entry

    @staticmethod
    def _action_matches(action: str, pattern: str) -> bool:
        """Einfaches Pattern-Matching: 'file.*' matcht 'file.write', 'file.read' etc."""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return action.startswith(pattern[:-1])
        return action == pattern

    def seal(self, mission_id: str) -> dict:
        """Versiegelt die Chain mit einem finalen SEAL-Eintrag."""
        stats = self.stats()
        return self.log(
            event="CHAIN_SEALED",
            ref=mission_id,
            data={
                "total_entries": stats["total"],
                "genesis_hash": stats["genesis_hash"],
                "chain_intact": stats["intact"],
            },
        )

    # ── Verifikation ─────────────────────────────────────────

    def verify(self) -> tuple[bool, list[str]]:
        """
        Prüft die gesamte Kette auf Integrität.
        Gibt (intact: bool, errors: list[str]) zurück.
        """
        entries = self._read_all()
        errors = []

        if not entries:
            return True, ["Chain ist leer."]

        # Genesis prüfen
        if entries[0]["event"] != GENESIS_EVENT:
            errors.append(f"Seq 0: Erster Eintrag ist kein GENESIS (ist: {entries[0]['event']})")

        if entries[0]["prev_hash"] != "0" * 64:
            errors.append(f"Seq 0: Genesis prev_hash ist nicht null-hash")

        for i, entry in enumerate(entries):
            # Hash-Konsistenz prüfen
            stored_hash = entry.get("entry_hash", "")
            check_entry = {k: v for k, v in entry.items() if k != "entry_hash"}
            computed_hash = self._compute_hash(check_entry)

            if stored_hash != computed_hash:
                errors.append(
                    f"Seq {entry['seq']}: Hash-Mismatch! "
                    f"Gespeichert={stored_hash[:16]}... "
                    f"Berechnet={computed_hash[:16]}..."
                )

            # Verkettung prüfen (ab Eintrag 2)
            if i > 0:
                expected_prev = entries[i - 1]["entry_hash"]
                actual_prev = entry["prev_hash"]
                if actual_prev != expected_prev:
                    errors.append(
                        f"Seq {entry['seq']}: Ketten-Bruch! "
                        f"prev_hash={actual_prev[:16]}... "
                        f"erwartet={expected_prev[:16]}..."
                    )

            # Sequenz-Kontinuität
            if entry["seq"] != i:
                errors.append(f"Seq {entry['seq']}: Sequenz-Lücke (erwartet: {i})")

        intact = len(errors) == 0
        return intact, errors if errors else ["Kette intakt. Alle Hashes verifiziert."]

    def stats(self) -> dict:
        """Statistiken über die Chain."""
        entries = self._read_all()
        if not entries:
            return {"total": 0, "intact": True, "genesis_hash": None, "final_hash": None}

        intact, _ = self.verify()
        event_counts: dict[str, int] = {}
        agents: set[str] = set()

        for e in entries:
            ev = e["event"]
            event_counts[ev] = event_counts.get(ev, 0) + 1
            if e.get("agent"):
                agents.add(e["agent"])

        return {
            "total": len(entries),
            "intact": intact,
            "genesis_hash": entries[0]["entry_hash"],
            "final_hash": entries[-1]["entry_hash"],
            "first_timestamp": entries[0]["timestamp"],
            "last_timestamp": entries[-1]["timestamp"],
            "event_counts": event_counts,
            "unique_agents": sorted(agents),
        }

    # ── Abfragen ─────────────────────────────────────────────

    def get_entries(self, last_n: Optional[int] = None) -> list[dict]:
        """Gibt alle oder die letzten N Einträge zurück."""
        entries = self._read_all()
        if last_n:
            return entries[-last_n:]
        return entries

    def get_by_ref(self, ref: str) -> list[dict]:
        """Alle Einträge zu einer bestimmten Referenz (z.B. WP-003)."""
        return [e for e in self._read_all() if e.get("ref") == ref]

    def get_by_event(self, event: str) -> list[dict]:
        """Alle Einträge eines bestimmten Event-Typs."""
        return [e for e in self._read_all() if e.get("event") == event]

    # ── Report-Generierung ───────────────────────────────────

    def generate_integrity_report(self) -> str:
        """Generiert einen Markdown-Integritätsbericht."""
        s = self.stats()
        intact, messages = self.verify()

        report = f"""## Kryptographische Integrität (AuditChain)

| Eigenschaft | Wert |
|---|---|
| Chain-Länge | {s['total']} Einträge |
| Genesis-Hash | `{s.get('genesis_hash', 'N/A')[:24]}...` |
| Finaler Hash | `{s.get('final_hash', 'N/A')[:24]}...` |
| Zeitraum | {s.get('first_timestamp', 'N/A')} → {s.get('last_timestamp', 'N/A')} |
| Kette intakt | {'✅ Ja' if intact else '❌ NEIN — MANIPULATION ERKANNT'} |
| Beteiligte Agenten | {', '.join(s.get('unique_agents', [])) or 'keine'} |

### Event-Verteilung

| Event | Anzahl |
|---|---|
"""
        for event, count in sorted(s.get("event_counts", {}).items()):
            report += f"| {event} | {count} |\n"

        if not intact:
            report += "\n### ⚠️ Integritätsfehler\n\n"
            for msg in messages:
                report += f"- {msg}\n"
        else:
            report += f"\n> Alle {s['total']} Einträge verifiziert. Keine Manipulation erkannt.\n"

        return report

    # ── Hilfsfunktionen ──────────────────────────────────────

    @staticmethod
    def _compute_hash(entry: dict) -> str:
        """SHA-256 über den kanonisch serialisierten Eintrag."""
        canonical = json.dumps(entry, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def hash_file(path: str) -> str:
        """SHA-256 einer Datei. Für Skill-Hashes und Artefakt-Hashes."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return "sha256:" + h.hexdigest()

    def _get_last_hash(self) -> str:
        """Hash des letzten Eintrags oder Null-Hash bei leerer Chain."""
        if not self.chain_file.exists() or self.chain_file.stat().st_size == 0:
            return "0" * 64

        # Letzten Eintrag lesen (effizient von hinten)
        with open(self.chain_file, "rb") as f:
            f.seek(0, 2)
            pos = f.tell() - 1
            while pos > 0 and f.read(1) != b"\n":
                pos -= 1
                f.seek(pos)
            if pos > 0:
                f.seek(pos + 1)
            else:
                f.seek(0)
            last_line = f.readline().decode("utf-8").strip()

        if not last_line:
            return "0" * 64

        return json.loads(last_line).get("entry_hash", "0" * 64)

    def _get_next_seq(self) -> int:
        """Nächste Sequenznummer."""
        if not self.chain_file.exists() or self.chain_file.stat().st_size == 0:
            return 0
        with open(self.chain_file, "r", encoding="utf-8") as f:
            count = sum(1 for line in f if line.strip())
        return count

    def _read_all(self) -> list[dict]:
        """Alle Einträge lesen."""
        if not self.chain_file.exists():
            return []
        entries = []
        with open(self.chain_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries


# ── CLI ──────────────────────────────────────────────────────

def _cli():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    audit_dir = sys.argv[2]
    ac = AuditChain(audit_dir)

    if cmd == "log":
        if len(sys.argv) < 5:
            print("Usage: chain.py log <audit_dir> <event> <ref> [key=value ...]")
            sys.exit(1)
        event = sys.argv[3]
        ref = sys.argv[4]
        data = {}
        for arg in sys.argv[5:]:
            if "=" in arg:
                k, v = arg.split("=", 1)
                data[k] = v
        entry = ac.log(event, ref=ref, data=data)
        print(f"✅ Logged: seq={entry['seq']} event={event} ref={ref}")
        print(f"   Hash: {entry['entry_hash']}")

    elif cmd == "genesis":
        if len(sys.argv) < 4:
            print("Usage: chain.py genesis <audit_dir> <mission_id> [--skill name=path ...]")
            sys.exit(1)
        mission_id = sys.argv[3]
        skill_files = {}
        for arg in sys.argv[4:]:
            if arg.startswith("--skill") and "=" in arg:
                # --skill=name=path
                _, rest = arg.split("=", 1)
                name, path = rest.split("=", 1)
                skill_files[name] = path
            elif "=" in arg and not arg.startswith("-"):
                name, path = arg.split("=", 1)
                skill_files[name] = path
        entry = ac.genesis(
            mission_id,
            goals=["(set via API)"],
            actors=["(set via API)"],
            skill_files=skill_files if skill_files else None,
        )
        print(f"✅ Genesis-Block erstellt: {entry['entry_hash']}")
        if skill_files:
            for name in skill_files:
                print(f"   Skill versiegelt: {name}")

    elif cmd == "hash-file":
        if len(sys.argv) < 4:
            print("Usage: chain.py hash-file <audit_dir> <filepath>")
            sys.exit(1)
        filepath = sys.argv[3]
        h = AuditChain.hash_file(filepath)
        print(f"{h}  {filepath}")

    elif cmd == "verify":
        intact, messages = ac.verify()
        status = "✅ INTAKT" if intact else "❌ GEBROCHEN"
        print(f"\nChain-Status: {status}\n")
        for msg in messages:
            print(f"  {msg}")
        sys.exit(0 if intact else 1)

    elif cmd == "show":
        last_n = None
        if len(sys.argv) > 3 and sys.argv[3] == "--last":
            last_n = int(sys.argv[4])
        entries = ac.get_entries(last_n=last_n)
        for e in entries:
            print(json.dumps(e, indent=2, ensure_ascii=False))

    elif cmd == "summary":
        print(ac.generate_integrity_report())

    elif cmd == "seal":
        if len(sys.argv) < 4:
            print("Usage: chain.py seal <audit_dir> <mission_id>")
            sys.exit(1)
        entry = ac.seal(sys.argv[3])
        print(f"✅ Chain versiegelt: {entry['entry_hash']}")

    else:
        print(f"Unbekannter Befehl: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    _cli()
