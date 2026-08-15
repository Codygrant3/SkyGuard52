#!/usr/bin/env python3
"""Freeze the verified Mission 2-10 offline package and queue addendum."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "Docs" / "AAA_Review"
REPORTS = ROOT / "Saved" / "Reports"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def item(path: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.write_text(payload.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    created_utc = datetime.now(timezone.utc).isoformat()
    members = [
        ROOT / "Scripts" / "build_campaign_m02_m10_final_art_production_offline.py",
        ROOT / "Scripts" / "finalize_campaign_m02_m10_final_art_production_offline.py",
        ROOT / "Scripts" / "verify_campaign_m02_m10_final_art_production_offline.py",
        ROOT / "Scripts" / "tests" / "test_campaign_m02_m10_final_art_production_offline.py",
        DOCS / "CAMPAIGN_M02_M10_FINAL_ART_PRODUCTION_CONTRACT.json",
        DOCS / "CAMPAIGN_M02_M10_MISSION_BOSS_PRODUCTION_MATRIX.json",
        DOCS / "CAMPAIGN_M02_M10_VISUAL_PERFORMANCE_ACCEPTANCE_RUBRIC.json",
        REPORTS / "CAMPAIGN_M02_M10_FINAL_ART_SOURCE_INVENTORY.json",
        REPORTS / "CAMPAIGN_M02_M10_FINAL_ART_READINESS.json",
        REPORTS / "CAMPAIGN_M02_M10_FINAL_ART_OFFLINE_VERIFICATION.json",
        DOCS / "NEXT_PROMPT_CAMPAIGN_M02_M03_FINAL_ART_PRODUCTION_WAVE01_OFFLINE_ORCHESTRATION.md",
        DOCS / "PHASE1_8_COMPLETION_AUDIT_ADDENDUM_CAMPAIGN_M02_M10_FINAL_ART_OFFLINE_DESIGN_2026-08-09.md",
        DOCS / "SKYGUARD52_CAMPAIGN_ACCEPTANCE_MATRIX_ADDENDUM_M02_M10_FINAL_ART_OFFLINE_DESIGN_2026-08-09.md",
    ]
    missing = [str(path) for path in members if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing freeze members:\n" + "\n".join(missing))

    package_freeze = DOCS / "SKYGUARD52_CAMPAIGN_M02_M10_FINAL_ART_OFFLINE_DESIGN_FREEZE.json"
    write_json(
        package_freeze,
        {
            "schema": "skyguard.campaign-m02-m10-final-art-offline-design-freeze.v1",
            "created_utc": created_utc,
            "classification": "PASSED_OFFLINE_DESIGN_AWAITING_M01_VISUAL_LANGUAGE_ACCEPTANCE",
            "member_count": len(members),
            "members": [item(path) for path in members],
            "mission_contracts": "9_OF_9",
            "production_mission_acceptance": "0_OF_10",
            "heavy_execution_authorized": False,
            "first_heavy_gate_unchanged": "Recovery07 Mapped Visual Proof01 Recovery04",
            "next_campaign_gate": "OFFLINE_M02_M03_WAVE01_ORCHESTRATION_AFTER_M01_VISUAL_AND_COMBAT_ACCEPTANCE",
        },
    )

    revision04_json = DOCS / "SKYGUARD52_CANONICAL_NEXT_GATE_QUEUE_REVISION04_2026-08-09.json"
    revision04_freeze = DOCS / "SKYGUARD52_CANONICAL_NEXT_GATE_QUEUE_REVISION04_FREEZE_2026-08-09.json"
    recovery04_readiness = DOCS / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY04_TERMINAL_READINESS_FREEZE.json"
    for authority in (revision04_json, revision04_freeze, recovery04_readiness):
        if not authority.is_file():
            raise FileNotFoundError(authority)
    revision04 = json.loads(revision04_json.read_text(encoding="utf-8"))
    if revision04.get("inherited_heavy_queue", {}).get("ordered_gate_count") != 7:
        raise RuntimeError("Revision04 no longer carries seven heavy gates")

    revision05_json = DOCS / "SKYGUARD52_CANONICAL_NEXT_GATE_QUEUE_REVISION05_2026-08-09.json"
    revision05_md = DOCS / "SKYGUARD52_CANONICAL_NEXT_GATE_QUEUE_REVISION05_2026-08-09.md"
    write_json(
        revision05_json,
        {
            "schema": "skyguard.production.next-gate-queue.v5",
            "created_utc": created_utc,
            "classification": "PASS_SEVEN_HEAVY_GATES_UNCHANGED_CAMPAIGN_FINAL_ART_CONTRACT_FROZEN",
            "inherited_queue": {
                **item(revision04_json),
                "freeze": item(revision04_freeze),
                "ordered_gate_count": 7,
                "order_changed": False,
            },
            "first_heavy_gate": {
                "lane": "mission01_environment_visual_acceptance",
                "name": "Recovery07 Mapped Visual Proof01 Recovery04",
                "process": "UnrealEditor",
                "separate_explicit_authorization_required": True,
                "readiness": item(recovery04_readiness),
            },
            "campaign_offline_authority": {
                **item(package_freeze),
                "mission_contracts": "9_OF_9",
                "production_acceptance": "0_OF_10",
                "wave01_executable_now": False,
                "wave01_prerequisite": "accepted Mission 1 mapped visual and combat vertical slice",
            },
            "one_heavy_process_only": True,
            "automatic_retries": 0,
            "failed_namespace_reuse": False,
        },
    )
    write_text(
        revision05_md,
        """# Skyguard 52 — Canonical Next-Gate Queue, Revision 05

The seven heavy gates and their order remain unchanged. Recovery07 Mapped Visual Proof01 Recovery04 remains first and requires separate explicit authorization.

## Campaign final-art correction

The current campaign baseline contains ten governed mission definitions, distinct routes, maps, integration directors and boss gameplay classes. Production acceptance remains **0 of 10**.

A single offline production contract now governs Missions 2-10:

- nine distinct environment and boss identities;
- three to ten exclusive hero assets per mission;
- 65-70% shared modular geometry without duplicated layouts;
- three propagation waves: M02-M03, M04-M07 and M08-M10;
- fixed mapped-visual, input-combat, performance, stability and packaged-mission gates;
- preauthored, pooled boss destruction instead of live complex fracture.

No campaign heavy execution is authorized until Mission 1 establishes accepted visual and combat language.
""",
    )
    queue_freeze = DOCS / "SKYGUARD52_CANONICAL_NEXT_GATE_QUEUE_REVISION05_FREEZE_2026-08-09.json"
    queue_members = [revision05_json, revision05_md, revision04_freeze, package_freeze, recovery04_readiness]
    write_json(
        queue_freeze,
        {
            "schema": "skyguard.production.next-gate-queue-revision05-freeze.v1",
            "created_utc": created_utc,
            "classification": "PASS_SEVEN_HEAVY_GATES_UNCHANGED_CAMPAIGN_FINAL_ART_CONTRACT_FROZEN",
            "member_count": len(queue_members),
            "members": [item(path) for path in queue_members],
            "heavy_gate_count": 7,
            "heavy_gate_order_changed": False,
            "first_heavy_gate": "Recovery07 Mapped Visual Proof01 Recovery04",
            "campaign_production_acceptance": "0_OF_10",
            "heavy_execution_authorized": False,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
