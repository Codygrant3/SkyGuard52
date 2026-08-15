"""Freeze the rejected Mission 1 Realism Stack Visual Proof02 evidence.

This is an offline evidence-only helper.  It never launches Unreal or Blender
and never mutates an attempt artifact.  The generated reports make the direct
full-resolution visual decision explicit instead of relying on the automatic
pixel-luminance rejection alone.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02"
CAPTURES = ATTEMPT / r"attempt_01\proof\captures"
REPORTS = ROOT / "Saved" / "Reports"
DOCS = ROOT / "Docs" / "AAA_Review"


def digest(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": str(path),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    required = [
        DOCS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_OFFLINE_DESIGN_FREEZE.json",
        DOCS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_EXECUTION_PROMPT_BINDING_FREEZE.json",
        REPORTS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_EXECUTION_PREFLIGHT.json",
        REPORTS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_TERMINAL_SUPERVISOR.json",
        REPORTS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_POSTFLIGHT.json",
        ATTEMPT / r"attempt_01\proof\capture_receipt.json",
        ATTEMPT / r"attempt_01\proof\frame_samples.csv",
        ATTEMPT / r"attempt_01\proof\lifecycle_heartbeat.jsonl",
        ATTEMPT / r"attempt_01\proof\restoration_receipt.json",
        ATTEMPT / r"attempt_01\terminal_receipt.json",
        ATTEMPT / r"launcher_attempt_01\executor_startup_receipt.json",
        ATTEMPT / r"launcher_attempt_01\runtime_actor_inventory.json",
        ATTEMPT / r"launcher_attempt_01\process_tree_samples.jsonl",
        ATTEMPT / r"launcher_attempt_01\logs\m01_environment_realism_stack_visual_proof02.engine.log",
        ATTEMPT / r"launcher_attempt_01\logs\m01_environment_realism_stack_visual_proof02.postflight.log",
        ATTEMPT / r"launcher_attempt_01\logs\m01_environment_realism_stack_visual_proof02.stdout.log",
        ATTEMPT / r"launcher_attempt_01\logs\m01_environment_realism_stack_visual_proof02.stderr.log",
        Path(r"D:\SG52T08_ENV01\Saved\Profiling\CSV\M01EnvironmentRealismStackVisualProof02.csv"),
    ]
    required.extend(sorted(CAPTURES.glob("*.png")))
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing governed proof evidence: " + ", ".join(missing))

    captures = sorted(CAPTURES.glob("*.png"))
    if len(captures) != 8:
        raise AssertionError(f"Expected eight captures; found {len(captures)}")

    created = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    review = {
        "schema": "skyguard.m01-environment-realism-stack.visual-proof02.direct-visual-review.v1",
        "created_utc": created,
        "classification": "FAILED_WITH_EVIDENCE",
        "automatic_postflight": "FAILED_WITH_EVIDENCE_CRUSHED_SHADOWS_C01",
        "all_original_pngs_inspected_directly": True,
        "capture_count": 8,
        "resolution": [2560, 1440],
        "passes": [
            "The Stack03 landscape extension removed the city-over-void failure.",
            "Buildings, roads and vegetation are grounded on continuous terrain.",
            "The coastline route and ten governed shoreline contacts remain spatially coherent.",
            "Sun-facing surfaces are more readable than the rejected Visual Proof01 baseline.",
            "No camera clipping or camera-coupled world motion was observed in the eight captures.",
        ],
        "blocking_findings": [
            {
                "category": "lighting",
                "finding": "Shadowed building faces remain nearly black; the skylight is not supplying credible ambient fill.",
            },
            {
                "category": "architecture",
                "finding": "Apartment and midrise geometry remains flat, box-derived and visibly repetitive at rear-gunner review distance.",
            },
            {
                "category": "facades",
                "finding": "Windows, balconies, entrances and rooflines lack sufficient depth, variation and construction detail.",
            },
            {
                "category": "vegetation",
                "finding": "Trees read as faceted geometric placeholders rather than credible coastal vegetation.",
            },
            {
                "category": "shoreline",
                "finding": "Water is visually flat and the beach lacks surf, foam, wet-sand response and a natural shore transition.",
            },
            {
                "category": "surfaces",
                "finding": "Terrain, road, plaster and concrete lack calibrated macro/micro roughness, weathering, drainage, salt and grime layers.",
            },
            {
                "category": "landmarks",
                "finding": "The lighthouse and surrounding street furniture retain obvious primitive or blockout silhouettes.",
            },
        ],
        "decision": "REJECT_REPRESENTATIVE_VISUAL_ART_QUALITY",
        "promotion_authorized": False,
        "next_route": "FRESH_MODULAR_ENVIRONMENT_ART_AND_PBR_PRODUCTION_RESET_BEFORE_ANOTHER_MAPPED_PROOF",
        "capture_members": [digest(path) for path in captures],
    }
    review_path = REPORTS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_ATTEMPT01_DIRECT_VISUAL_REVIEW.json"
    write_json(review_path, review)

    analysis = {
        "schema": "skyguard.m01-environment-realism-stack.visual-proof02.failure-analysis.v1",
        "created_utc": created,
        "classification": "FAILED_WITH_EVIDENCE",
        "root_causes": [
            "Automatic rejection: crushed shadow luminance in C01.",
            "Art rejection: the visible city, vegetation, shoreline and landmark language remains production-placeholder quality.",
        ],
        "what_worked": [
            "Stack03 terrain continuity and actor grounding",
            "explicit sun rotation correction",
            "one-shot D3D12 SM6 evidence lifecycle",
            "eight fixed-camera captures and CSV profiling",
        ],
        "what_not_to_repeat": [
            "Do not spend another full mapped proof on exposure-only changes.",
            "Do not promote or integrate the rejected StageA Recovery10 environment kit.",
            "Do not reuse failed proof or Blender output namespaces.",
        ],
        "corrective_strategy": [
            "Author fresh modular buildings with deep openings, balcony variants, roof equipment and nonrepeating silhouettes.",
            "Use the governed local Poly Haven PBR library for plaster, concrete, brick, asphalt, roof, metal and sand response.",
            "Replace faceted trees with branch-and-leaf-card production vegetation or verified local production foliage.",
            "Create an explicit surf, foam, wet-sand and seawall-contact treatment in Unreal.",
            "Use a movable, real-time-capture skylight and validate ambient fill only after production geometry is present.",
        ],
        "next_gate": "M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET_CHECKPOINT01",
    }
    analysis_path = REPORTS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_ATTEMPT01_FAILURE_ANALYSIS.json"
    write_json(analysis_path, analysis)

    inventory_members = [digest(path) for path in required]
    inventory_members.extend([digest(review_path), digest(analysis_path)])
    inventory = {
        "schema": "skyguard.m01-environment-realism-stack.visual-proof02.attempt01-inventory.v1",
        "created_utc": created,
        "classification": "FAILED_WITH_EVIDENCE",
        "member_count": len(inventory_members),
        "members": inventory_members,
    }
    inventory_path = REPORTS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_ATTEMPT01_INVENTORY.json"
    write_json(inventory_path, inventory)

    review_md = DOCS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_ATTEMPT01_DIRECT_VISUAL_REVIEW.md"
    review_md.write_text(
        "# Mission 1 Environment Realism Stack Visual Proof02\n\n"
        "Classification: `FAILED_WITH_EVIDENCE`\n\n"
        "All eight original 2560x1440 captures were inspected directly at full resolution. "
        "The Stack03 terrain and grounding correction worked, but the representative scene still fails the production visual gate.\n\n"
        "## Accepted progress\n\n"
        "- Continuous terrain now supports the buildings, roads and vegetation.\n"
        "- Shoreline contacts and route composition remain coherent.\n"
        "- Sun-facing surfaces are more readable than Visual Proof01.\n\n"
        "## Blocking findings\n\n"
        "- Shadowed facades are nearly black and lack credible skylight fill.\n"
        "- Buildings remain box-derived, repetitive and shallow.\n"
        "- Trees, lighthouse, street furniture and shoreline remain obvious placeholder art.\n"
        "- Water, surf, wet sand, material weathering and terrain transitions are not production quality.\n\n"
        "The next gate is a fresh modular environment-art and PBR production reset. Exposure-only retries are prohibited.\n",
        encoding="utf-8",
    )

    freeze_members = [digest(review_path), digest(review_md), digest(analysis_path), digest(inventory_path)]
    freeze_members.extend(digest(path) for path in required[:5])
    freeze = {
        "schema": "skyguard.m01-environment-realism-stack.visual-proof02.attempt01-terminal-freeze.v1",
        "created_utc": created,
        "classification": "FAILED_WITH_EVIDENCE",
        "failure": "AUTOMATIC_CRUSHED_SHADOW_REJECTION_AND_DIRECT_VISUAL_ART_REJECTION",
        "unreal_launch_count": 1,
        "adjudicator_launch_count": 1,
        "automatic_retry_count": 0,
        "attempt_namespace": str(ATTEMPT),
        "attempt_preservation": "IMMUTABLE_NO_REUSE",
        "member_count": len(freeze_members),
        "members": freeze_members,
        "next_executable_gate": "M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET_CHECKPOINT01",
    }
    freeze_path = DOCS / "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF02_ATTEMPT01_TERMINAL_FREEZE.json"
    write_json(freeze_path, freeze)
    print(json.dumps({"classification": freeze["classification"], "freeze": digest(freeze_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
