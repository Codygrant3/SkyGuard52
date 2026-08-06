"""Offline fail-closed readiness audit for the Build 008 Unreal candidate lane."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_ACCEPTANCE_008_CONTRACT.json"
REPORT_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_ACCEPTANCE_008_OFFLINE_READINESS.json"
BUILDER_PATH = ROOT / "Scripts/build_m01_hero_grouped_topology_unreal_candidate_008.py"
VERIFIER_PATH = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_candidate_008.py"
RUNNER_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_acceptance_008.ps1"
RUNBOOK_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_ACCEPTANCE_008_RUNBOOK.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def add(checks: list[dict[str, Any]], name: str, passed: bool, detail: Any) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def audit_source(write_report: bool = True) -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    checks: list[dict[str, Any]] = []
    bound_paths: dict[str, Path] = {}
    for name, record in contract["bound_sources"].items():
        path = ROOT / record["path"]
        actual_bytes = path.stat().st_size if path.is_file() else None
        actual_hash = sha256(path) if path.is_file() else None
        add(
            checks,
            "bound_" + name,
            actual_bytes == record["bytes"] and actual_hash == record["sha256"],
            {
                "path": record["path"],
                "expected_bytes": record["bytes"],
                "actual_bytes": actual_bytes,
                "expected_sha256": record["sha256"],
                "actual_sha256": actual_hash,
            },
        )
        bound_paths[name] = path

    manifest = load_json(bound_paths["manifest"])
    map_records = [
        (asset["id"], group["id"], item)
        for asset in manifest["assets"]
        for group in asset["groups"]
        for item in group["maps"]
    ]
    map_provenance = []
    for asset_id, group_id, item in map_records:
        path = Path(item["path"])
        current_hash = sha256(path) if path.is_file() else None
        current_bytes = path.stat().st_size if path.is_file() else None
        map_provenance.append(
            {
                "key": f"{asset_id}/{group_id}/{item['type']}",
                "path": str(path),
                "bytes": item["bytes"],
                "sha256": item["sha256"],
                "current_bytes": current_bytes,
                "current_sha256": current_hash,
                "provenance": item["provenance"],
                "matches": current_bytes == item["bytes"] and current_hash == item["sha256"],
            }
        )
    add(checks, "exact_24_manifest_maps", len(map_records) == 24, len(map_records))
    add(
        checks,
        "all_manifest_maps_hash_match",
        all(item["matches"] for item in map_provenance),
        [item["key"] for item in map_provenance if not item["matches"]],
    )
    modes = [item["provenance"]["mode"] for item in map_provenance]
    add(
        checks,
        "six_rebaked_eighteen_reused",
        modes.count("corrective_rebake") == 6
        and modes.count("hash_verified_reuse") == 18,
        {
            "corrective_rebake": modes.count("corrective_rebake"),
            "hash_verified_reuse": modes.count("hash_verified_reuse"),
        },
    )

    groups = [
        (asset["id"], group["id"], group)
        for asset in manifest["assets"]
        for group in asset["groups"]
    ]
    expected_keys = {f"{asset}/{group}" for asset, group, _ in groups}
    add(checks, "exact_12_manifest_groups", len(groups) == 12, len(groups))
    add(
        checks,
        "mesh_target_keyset_exact",
        set(contract["mesh_targets"]) == expected_keys,
        sorted(set(contract["mesh_targets"]) ^ expected_keys),
    )
    nanite = contract["mesh_policy"]["nanite"]
    add(
        checks,
        "nanite_partition_exact",
        set(nanite["enabled_groups"]) | set(nanite["disabled_groups"]) == expected_keys
        and not (set(nanite["enabled_groups"]) & set(nanite["disabled_groups"])),
        nanite,
    )
    add(
        checks,
        "collision_keyset_exact",
        set(contract["mesh_policy"]["collision"]) == expected_keys,
        sorted(set(contract["mesh_policy"]["collision"]) ^ expected_keys),
    )

    artifact = load_json(bound_paths["artifact_verification"])
    direct = load_json(bound_paths["direct_map_review"])
    mapped = load_json(bound_paths["mapped_mesh_review"])
    summary = load_json(bound_paths["pre_unreal_summary"])
    add(checks, "artifact_gate_passed", artifact.get("gate") == "PASS", artifact.get("gate"))
    add(checks, "direct_map_gate_passed", direct.get("overall_gate") == "PASS", direct.get("overall_gate"))
    add(
        checks,
        "mapped_mesh_gate_passed",
        mapped.get("mapped_mesh_grazing_angle_gate") == "PASS",
        mapped.get("mapped_mesh_grazing_angle_gate"),
    )
    add(
        checks,
        "pre_unreal_summary_passed",
        summary.get("gate") == "PASS"
        and summary.get("gates", {}).get("unreal_acceptance") == "NOT_RUN",
        summary.get("gates"),
    )

    implementation = [BUILDER_PATH, VERIFIER_PATH, RUNNER_PATH, RUNBOOK_PATH]
    missing = [str(path.relative_to(ROOT)) for path in implementation if not path.is_file()]
    add(checks, "implementation_files_present", not missing, missing)
    if not missing:
        builder = BUILDER_PATH.read_text(encoding="utf-8-sig")
        verifier = VERIFIER_PATH.read_text(encoding="utf-8-sig")
        runner = RUNNER_PATH.read_text(encoding="utf-8-sig")
        ast.parse(builder, filename=str(BUILDER_PATH))
        ast.parse(verifier, filename=str(VERIFIER_PATH))
        forbidden = [
            "/Game/Skyguard/Maps",
            "/Game/Skyguard/Missions",
            "DefaultEngine.ini",
            "DefaultGame.ini",
            "replace_existing = True",
            "Build.bat",
            "-ExecCmds=Automation",
        ]
        combined = "\n".join((builder, verifier, runner))
        found = [token for token in forbidden if token in combined]
        add(checks, "no_runtime_or_build_mutation", not found, found)
        root = contract["unreal"]["candidate_root"]
        add(
            checks,
            "candidate_root_hard_bound",
            root in builder and root in verifier and root in runner,
            root,
        )
        required_tokens = [
            "TC_NORMALMAP",
            "TC_MASKS",
            "flip_green_channel",
            "MP_NORMAL",
            "MP_AMBIENT_OCCLUSION",
            "nanite_settings",
            "add_simple_collisions",
            "maximum_dimension_relative_error",
            "promotion_allowed",
        ]
        missing_tokens = [token for token in required_tokens if token not in combined]
        add(checks, "implementation_covers_acceptance_contract", not missing_tokens, missing_tokens)

    passed = all(item["passed"] for item in checks)
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-offline-readiness.v1",
        "gate": (
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_UNREAL_AUTHORIZATION"
            if passed
            else "FAIL_OFFLINE_NOT_READY"
        ),
        "build_id": contract["build_id"],
        "candidate_root": contract["unreal"]["candidate_root"],
        "bound_manifest_sha256": contract["bound_sources"]["manifest"]["sha256"],
        "bound_low_glb_sha256": contract["bound_sources"]["low_glb"]["sha256"],
        "map_provenance": map_provenance,
        "checks": checks,
        "unreal_launched": False,
        "blender_launched": False,
        "compiler_launched": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    if write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    report = audit_source(write_report=not args.no_write)
    print(json.dumps(report, indent=2))
    return 0 if report["gate"].startswith("PASS_") else 2


if __name__ == "__main__":
    sys.exit(main())
