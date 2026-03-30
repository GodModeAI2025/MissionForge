#!/usr/bin/env python3
"""
AuditChain — Demo & Selbsttest
================================
Simuliert einen kompletten MissionForge-Durchlauf mit AuditChain.
"""

import json
import os
import shutil
import sys
from pathlib import Path

# Import aus gleichem Verzeichnis
sys.path.insert(0, str(Path(__file__).parent))
from chain import AuditChain


def run_demo():
    demo_dir = "/tmp/auditchain-demo/audit"
    
    # Clean start
    if Path(demo_dir).exists():
        shutil.rmtree(Path(demo_dir).parent)
    
    ac = AuditChain(demo_dir)
    print("=" * 60)
    print("  AuditChain Demo — MissionForge Integration")
    print("=" * 60)

    # Phase 2: Genesis
    print("\n📌 Phase 2 — Company spawnen (Genesis-Block)")
    genesis = ac.genesis(
        mission_id="MISSION-2026-042",
        goals=["REST-API mit Auth implementieren", "Tests schreiben", "Deployment"],
        actors=["orchestrator", "implementierer-alpha", "implementierer-beta", "tester-01"],
    )
    print(f"   ✅ Genesis: {genesis['entry_hash'][:40]}...")

    # Phase 5: Wellenplan versiegeln
    print("\n📌 Phase 5 — Wellenplan versiegeln")
    ac.log("WAVE_PLAN_SEALED", ref="PLAN-v1", data={
        "waves": 3,
        "total_wps": 5,
        "plan_hash": "sha256:planinhalt_gehasht...",
    })
    print("   ✅ Wellenplan versiegelt")

    # Phase 6: Ausführung
    print("\n📌 Phase 6 — Ausführung (Task-Statuswechsel)")
    
    tasks = [
        ("WP-001", "implementierer-alpha", "OPEN", "IN_PROGRESS"),
        ("WP-002", "implementierer-beta", "OPEN", "IN_PROGRESS"),
        ("WP-001", "implementierer-alpha", "IN_PROGRESS", "DONE"),
        ("WP-002", "implementierer-beta", "IN_PROGRESS", "DONE"),
        ("WP-003", "implementierer-alpha", "OPEN", "IN_PROGRESS"),
        ("WP-003", "implementierer-alpha", "IN_PROGRESS", "DONE"),
    ]

    for ref, agent, from_status, to_status in tasks:
        entry = ac.log(
            event="TASK_STATUS_CHANGE",
            ref=ref,
            agent=agent,
            data={"from": from_status, "to": to_status},
        )
        print(f"   📝 {ref}: {from_status} → {to_status} (by {agent})")

    # Monte-Carlo Simulation
    print("\n📌 Phase 6 — Monte-Carlo für kritischen Task")
    for variant in range(1, 4):
        ac.log(
            event="MONTE_CARLO_VARIANT",
            ref="WP-004",
            agent="implementierer-alpha",
            data={
                "variant": variant,
                "prompt_variation": f"temperature=0.{variant}",
                "score": [0.82, 0.91, 0.87][variant - 1],
            },
        )
        print(f"   🎲 Variante {variant}: Score {[0.82, 0.91, 0.87][variant - 1]}")

    ac.log(
        event="MONTE_CARLO_SELECTED",
        ref="WP-004",
        data={"selected_variant": 2, "reason": "Höchster Score (0.91)"},
    )
    print("   ✅ Variante 2 ausgewählt (Score 0.91)")

    # Phase 7: Verifikation
    print("\n📌 Phase 7 — Verifikation")
    for wp in ["WP-001", "WP-002", "WP-003", "WP-004"]:
        ac.log(
            event="VERIFICATION_PASSED",
            ref=wp,
            agent="tester-01",
            data={"level": "acceptance_criteria", "result": "PASS"},
        )
    print("   ✅ Alle WPs verifiziert")

    # Phase 8: Versiegeln
    print("\n📌 Phase 8 — Chain versiegeln")
    seal = ac.seal("MISSION-2026-042")
    print(f"   🔒 Versiegelt: {seal['entry_hash'][:40]}...")

    # Verifikation
    print("\n" + "=" * 60)
    print("  Integritätsprüfung")
    print("=" * 60)
    
    intact, messages = ac.verify()
    print(f"\n   Status: {'✅ INTAKT' if intact else '❌ GEBROCHEN'}")
    for msg in messages:
        print(f"   {msg}")

    # Report
    print("\n" + "=" * 60)
    print("  Integritätsbericht")
    print("=" * 60)
    print(ac.generate_integrity_report())

    # Manipulationstest
    print("=" * 60)
    print("  Manipulationstest")
    print("=" * 60)
    
    chain_file = Path(demo_dir) / "CHAIN.jsonl"
    lines = chain_file.read_text().splitlines()
    
    # Manipuliere einen Eintrag
    tampered = json.loads(lines[3])
    tampered["data"]["to"] = "SKIPPED"  # Fälschen!
    lines[3] = json.dumps(tampered, ensure_ascii=False, separators=(",", ":"))
    chain_file.write_text("\n".join(lines) + "\n")
    
    print("\n   ⚡ Eintrag Seq 3 manipuliert (DONE → SKIPPED)")
    
    intact2, errors2 = ac.verify()
    print(f"   Status: {'✅ INTAKT' if intact2 else '❌ MANIPULATION ERKANNT'}")
    for err in errors2:
        print(f"   {err}")

    print(f"\n{'=' * 60}")
    print("  Demo abgeschlossen")
    print(f"{'=' * 60}")
    print(f"\n   Chain-Datei: {demo_dir}/CHAIN.jsonl")
    print(f"   Einträge: {len(lines)}")
    print()


if __name__ == "__main__":
    run_demo()
