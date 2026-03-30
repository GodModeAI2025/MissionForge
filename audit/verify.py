#!/usr/bin/env python3
"""
AuditChain Verifier — Standalone Integritätsprüfung
=====================================================
Unabhängiges Script zur Prüfung einer CHAIN.jsonl-Datei.
Kann von externen Auditoren ohne MissionForge verwendet werden.

Usage:
    python verify.py <path_to_CHAIN.jsonl>
    python verify.py .mission-forge/audit/CHAIN.jsonl --verbose
    python verify.py .mission-forge/audit/CHAIN.jsonl --report > audit_report.md
"""

import hashlib
import json
import sys
from pathlib import Path


def compute_hash(entry: dict) -> str:
    """SHA-256 über kanonisch serialisierten Eintrag (identisch zu chain.py)."""
    canonical = json.dumps(entry, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_chain(chain_file: str, verbose: bool = False) -> tuple[bool, list[str], dict]:
    """
    Prüft eine CHAIN.jsonl auf vollständige Integrität.
    
    Returns:
        (intact, errors, stats)
    """
    path = Path(chain_file)
    if not path.exists():
        return False, [f"Datei nicht gefunden: {chain_file}"], {}

    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                return False, [f"Zeile {i+1}: Ungültiges JSON — {e}"], {}

    if not entries:
        return True, ["Chain ist leer."], {"total": 0}

    errors = []
    warnings = []

    # 1. Genesis-Prüfung
    if entries[0]["event"] != "GENESIS":
        errors.append(f"[SEQ 0] Erster Eintrag ist kein GENESIS (ist: {entries[0]['event']})")

    if entries[0]["prev_hash"] != "0" * 64:
        errors.append(f"[SEQ 0] Genesis prev_hash ist nicht der Null-Hash")

    # 2. Jeden Eintrag prüfen
    for i, entry in enumerate(entries):
        # 2a. Hash-Konsistenz
        stored_hash = entry.get("entry_hash", "MISSING")
        check_entry = {k: v for k, v in entry.items() if k != "entry_hash"}
        computed_hash = compute_hash(check_entry)

        if stored_hash != computed_hash:
            errors.append(
                f"[SEQ {entry.get('seq', '?')}] HASH-MANIPULATION ERKANNT!\n"
                f"    Gespeichert: {stored_hash}\n"
                f"    Berechnet:   {computed_hash}"
            )
        elif verbose:
            print(f"  ✅ Seq {entry['seq']:>4}: {entry['event']:<30} Hash OK")

        # 2b. Verkettung (ab Eintrag 2)
        if i > 0:
            expected_prev = entries[i - 1]["entry_hash"]
            actual_prev = entry.get("prev_hash", "MISSING")
            if actual_prev != expected_prev:
                errors.append(
                    f"[SEQ {entry.get('seq', '?')}] KETTEN-BRUCH!\n"
                    f"    prev_hash:   {actual_prev}\n"
                    f"    Erwartet:    {expected_prev}"
                )

        # 2c. Sequenz-Kontinuität
        if entry.get("seq") != i:
            errors.append(f"[SEQ {entry.get('seq', '?')}] Sequenz-Lücke (erwartet: {i})")

        # 2d. Pflichtfelder
        for field in ["seq", "timestamp", "event", "prev_hash", "entry_hash"]:
            if field not in entry:
                errors.append(f"[SEQ {i}] Pflichtfeld fehlt: {field}")

    # 3. Statistiken
    event_counts: dict[str, int] = {}
    agents: set[str] = set()
    refs: set[str] = set()
    for e in entries:
        ev = e.get("event", "UNKNOWN")
        event_counts[ev] = event_counts.get(ev, 0) + 1
        if e.get("agent"):
            agents.add(e["agent"])
        if e.get("ref"):
            refs.add(e["ref"])

    stats = {
        "total": len(entries),
        "intact": len(errors) == 0,
        "genesis_hash": entries[0].get("entry_hash", "N/A"),
        "final_hash": entries[-1].get("entry_hash", "N/A"),
        "first_timestamp": entries[0].get("timestamp", "N/A"),
        "last_timestamp": entries[-1].get("timestamp", "N/A"),
        "event_counts": event_counts,
        "unique_agents": sorted(agents),
        "unique_refs": sorted(refs),
        "errors": errors,
        "sealed": entries[-1].get("event") == "CHAIN_SEALED",
    }

    return len(errors) == 0, errors, stats


def generate_report(chain_file: str) -> str:
    """Generiert einen vollständigen Audit-Report als Markdown."""
    intact, errors, stats = verify_chain(chain_file, verbose=False)

    report = f"""# AuditChain — Integritätsbericht

**Datei:** `{chain_file}`  
**Prüfzeitpunkt:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Ergebnis:** {'✅ INTAKT' if intact else '❌ INTEGRITÄTSVERLETZUNG ERKANNT'}

---

## Zusammenfassung

| Eigenschaft | Wert |
|---|---|
| Chain-Länge | {stats.get('total', 0)} Einträge |
| Genesis-Hash | `{stats.get('genesis_hash', 'N/A')}` |
| Finaler Hash | `{stats.get('final_hash', 'N/A')}` |
| Zeitraum | {stats.get('first_timestamp', 'N/A')} → {stats.get('last_timestamp', 'N/A')} |
| Versiegelt | {'✅ Ja' if stats.get('sealed') else '⚠️ Nein (Chain noch offen)'} |
| Beteiligte Agenten | {', '.join(stats.get('unique_agents', [])) or 'keine'} |
| Referenzierte Objekte | {', '.join(stats.get('unique_refs', [])) or 'keine'} |

## Event-Verteilung

| Event | Anzahl |
|---|---|
"""
    for event, count in sorted(stats.get("event_counts", {}).items()):
        report += f"| `{event}` | {count} |\n"

    if errors:
        report += "\n## ⚠️ Erkannte Fehler\n\n"
        for err in errors:
            report += f"```\n{err}\n```\n\n"
        report += (
            "> **WARNUNG:** Die Hash-Kette ist gebrochen. "
            "Einträge wurden möglicherweise nachträglich manipuliert. "
            "Dieses Audit-Log ist NICHT revisionssicher.\n"
        )
    else:
        report += (
            f"\n## Integritätsnachweis\n\n"
            f"> Alle {stats['total']} Einträge wurden einzeln verifiziert.\n"
            f"> Jeder `entry_hash` stimmt mit dem berechneten SHA-256 überein.\n"
            f"> Jeder `prev_hash` referenziert korrekt den vorherigen Eintrag.\n"
            f"> Die Sequenz ist lückenlos (0 bis {stats['total'] - 1}).\n"
            f"> **Keine Manipulation erkannt.**\n"
        )

    report += f"""
---

## Prüfverfahren

Diese Prüfung wurde mit `verify.py` durchgeführt.  
**Algorithmus:** Für jeden Eintrag wird der `entry_hash` aus allen Feldern  
(exklusive `entry_hash` selbst) per SHA-256 über kanonisches JSON berechnet  
und mit dem gespeicherten Wert verglichen. Zusätzlich wird die Verkettung  
über `prev_hash` geprüft.

Reproduzierbar mit:
```bash
python verify.py {chain_file} --verbose
```
"""
    return report


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    chain_file = sys.argv[1]
    verbose = "--verbose" in sys.argv
    report_mode = "--report" in sys.argv

    if report_mode:
        print(generate_report(chain_file))
        sys.exit(0)

    print(f"\n🔍 Prüfe: {chain_file}\n")
    intact, errors, stats = verify_chain(chain_file, verbose=verbose)

    if intact:
        print(f"\n✅ Chain INTAKT — {stats['total']} Einträge verifiziert")
        print(f"   Genesis: {stats['genesis_hash'][:32]}...")
        print(f"   Final:   {stats['final_hash'][:32]}...")
        if stats.get("sealed"):
            print(f"   🔒 Chain ist versiegelt")
    else:
        print(f"\n❌ INTEGRITÄTSVERLETZUNG — {len(errors)} Fehler gefunden:\n")
        for err in errors:
            print(f"   {err}")

    sys.exit(0 if intact else 1)


if __name__ == "__main__":
    main()
