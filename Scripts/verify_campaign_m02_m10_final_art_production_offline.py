#!/usr/bin/env python3
"""Verify the Mission 2-10 final-art offline production package."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_contract(contract: dict[str, Any], matrix: dict[str, Any], rubric: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missions = matrix.get("missions", [])
    orders = [mission.get("order") for mission in missions]
    bosses = [mission.get("boss") for mission in missions]
    routes = [json.dumps(mission.get("route_signature_cm"), sort_keys=True) for mission in missions]
    identities = [mission.get("environment_identity") for mission in missions]
    if orders != list(range(2, 11)):
        errors.append(f"mission orders are not 2-10: {orders}")
    if len(set(bosses)) != 9:
        errors.append("bosses are not unique")
    if len(set(routes)) != 9:
        errors.append("routes are not unique")
    if len(set(identities)) != 9:
        errors.append("environment identities are not unique")
    for mission in missions:
        hero_count = len(mission.get("exclusive_hero_assets", []))
        if not 3 <= hero_count <= 10:
            errors.append(f"{mission.get('mission_id')} hero count {hero_count} outside 3-10")
        if len(mission.get("canonical_weakpoints", [])) != 4:
            errors.append(f"{mission.get('mission_id')} does not have four weak points")
        if mission.get("production_acceptance") != "UNVERIFIED":
            errors.append(f"{mission.get('mission_id')} overclaims production acceptance")
        if len(mission.get("required_review_views", [])) != 8:
            errors.append(f"{mission.get('mission_id')} does not require eight review views")
    reuse = contract.get("reuse_contract", {})
    if reuse.get("shared_geometry_target_percent_min") != 65 or reuse.get("shared_geometry_target_percent_max") != 70:
        errors.append("shared geometry target is not 65-70 percent")
    if contract.get("heavy_execution_authorized") is not False:
        errors.append("offline contract improperly authorizes heavy execution")
    if contract.get("baseline_truth", {}).get("production_mission_acceptance") != "0_OF_10":
        errors.append("contract does not preserve zero-of-ten production truth")
    if rubric.get("visual_proof", {}).get("human_full_resolution_review_required") is not True:
        errors.append("rubric lacks human full-resolution review")
    if rubric.get("measurement", {}).get("minimum_frame_samples") != 900:
        errors.append("rubric does not preserve 900-sample minimum")
    return errors


def verify_inventory(inventory: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    records = inventory.get("records", [])
    if inventory.get("record_count") != len(records):
        errors.append("inventory record count mismatch")
    for item in records:
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"missing inventory member: {item['path']}")
            continue
        if path.stat().st_size != item["bytes"]:
            errors.append(f"byte mismatch: {item['path']}")
        if sha256_file(path) != item["sha256"]:
            errors.append(f"hash mismatch: {item['path']}")
    return errors


def validate_package() -> list[str]:
    paths = {
        "contract": DOCS / "CAMPAIGN_M02_M10_FINAL_ART_PRODUCTION_CONTRACT.json",
        "matrix": DOCS / "CAMPAIGN_M02_M10_MISSION_BOSS_PRODUCTION_MATRIX.json",
        "rubric": DOCS / "CAMPAIGN_M02_M10_VISUAL_PERFORMANCE_ACCEPTANCE_RUBRIC.json",
        "inventory": REPORTS / "CAMPAIGN_M02_M10_FINAL_ART_SOURCE_INVENTORY.json",
        "readiness": REPORTS / "CAMPAIGN_M02_M10_FINAL_ART_READINESS.json",
        "prompt": DOCS / "NEXT_PROMPT_CAMPAIGN_M02_M03_FINAL_ART_PRODUCTION_WAVE01_OFFLINE_ORCHESTRATION.md",
    }
    errors = [f"missing package artifact: {name}" for name, path in paths.items() if not path.is_file()]
    if errors:
        return errors
    contract = load_json(paths["contract"])
    matrix = load_json(paths["matrix"])
    rubric = load_json(paths["rubric"])
    inventory = load_json(paths["inventory"])
    readiness = load_json(paths["readiness"])
    errors.extend(validate_contract(contract, matrix, rubric))
    errors.extend(verify_inventory(inventory))
    if readiness.get("classification") != "PASSED_OFFLINE_DESIGN_AWAITING_M01_VISUAL_LANGUAGE_ACCEPTANCE":
        errors.append("readiness classification mismatch")
    if readiness.get("heavy_execution_authorized") is not False:
        errors.append("readiness improperly authorizes a heavy process")
    prompt = paths["prompt"].read_text(encoding="utf-8")
    for required in ["Do not launch Unreal, Blender", "Mission 1 mapped visual proof", "65-70%", "FAILED_WITH_EVIDENCE"]:
        if required not in prompt:
            errors.append(f"prompt missing required clause: {required}")
    return errors


def verify_freeze(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing freeze: {path.name}"]
    payload = load_json(path)
    members = payload.get("members", [])
    if payload.get("member_count") != len(members):
        errors.append(f"freeze member count mismatch: {path.name}")
    for member in members:
        member_path = ROOT / member["path"]
        if not member_path.is_file():
            errors.append(f"missing frozen member: {member['path']}")
            continue
        if member_path.stat().st_size != member["bytes"]:
            errors.append(f"frozen byte mismatch: {member['path']}")
        if sha256_file(member_path) != member["sha256"]:
            errors.append(f"frozen hash mismatch: {member['path']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    errors = validate_package()
    package_freeze = DOCS / "SKYGUARD52_CAMPAIGN_M02_M10_FINAL_ART_OFFLINE_DESIGN_FREEZE.json"
    queue_freeze = DOCS / "SKYGUARD52_CANONICAL_NEXT_GATE_QUEUE_REVISION05_FREEZE_2026-08-09.json"
    if package_freeze.exists():
        errors.extend(verify_freeze(package_freeze))
    if queue_freeze.exists():
        errors.extend(verify_freeze(queue_freeze))
    result = {
        "schema": "skyguard.campaign-m02-m10-final-art-offline-verification.v1",
        "classification": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
