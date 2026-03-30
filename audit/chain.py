#!/usr/bin/env python3
"""
AuditChain — Kryptographische Beweiskette für MissionForge
===========================================================
Append-only Hash-Chain: Jeder Eintrag referenziert den Hash des
vorherigen. Manipulation eines Eintrags bricht die Kette.

Verwendung:
    from chain import AuditChain

    ac = AuditChain(".mission-forge/audit")
    ac.log("TASK_STATUS_CHANGE", ref="WP-003", data={
        "from": "IN_PROGRESS", "to": "DONE",
        "agent": "implementierer-01",
        "artifact_hash": "sha256:..."
    })

CLI:
    python chain.py log   <audit_dir> <event> <ref> [key=value ...]
    python chain.py verify <audit_dir>
    python chain.py show   <audit_dir> [--last N]
    python chain.py summary <audit_dir>
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

    def genesis(self, mission_id: str, goals: list[str], actors: list[str]) -> dict:
        """Genesis-Block: Erster Eintrag der Kette."""
        if self.chain_file.exists() and self.chain_file.stat().st_size > 0:
            raise ValueError("Chain existiert bereits. Genesis nur einmal erlaubt.")

        return self.log(
            event=GENESIS_EVENT,
            ref=mission_id,
            data={
                "mission_id": mission_id,
                "goals": goals,
                "actors": actors,
                "chain_version": "1.0.0",
                "algorithm": "sha256",
            },
        )

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
            print("Usage: chain.py genesis <audit_dir> <mission_id>")
            sys.exit(1)
        mission_id = sys.argv[3]
        entry = ac.genesis(mission_id, goals=["(set via API)"], actors=["(set via API)"])
        print(f"✅ Genesis-Block erstellt: {entry['entry_hash']}")

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
