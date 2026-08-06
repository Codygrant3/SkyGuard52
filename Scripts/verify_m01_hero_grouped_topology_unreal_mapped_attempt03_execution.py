"""Independent offline verification for the authorized Attempt03 execution."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
FAILED_REVIEW = (
    ROOT
    / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_UNREAL_008"
    / "attempt_20260802T173639559Z"
    / "unreal_mapped_view_original_resolution_review_receipt.json"
)
BUILD_REPORT = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_BUILD.json"
ORIGINAL_CANDIDATE = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
ATTEMPT03_CONTENT = (
    ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
)
RUNTIME_MAPS = ROOT / "Content/Skyguard/Maps"
CONFIG = ROOT / "Config"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_tree(root: Path, suffixes: set[str] | None = None) -> dict[str, str]:
    records: dict[str, str] = {}
    if not root.exists():
        return records
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if suffixes and path.suffix.lower() not in suffixes:
            continue
        records[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    return records


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def add(checks: list[dict], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", required=True)
    parser.add_argument("--sweep-manifest", required=True)
    parser.add_argument("--selection-receipt", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    if output.exists():
        raise RuntimeError("immutable Attempt03 execution audit output already exists")
    preflight_path = Path(args.preflight)
    sweep_path = Path(args.sweep_manifest)
    selection_path = Path(args.selection_receipt)
    contract = load_json(CONTRACT)
    failed_review = load_json(FAILED_REVIEW)
    preflight = load_json(preflight_path)
    build = load_json(BUILD_REPORT)
    sweep = load_json(sweep_path)
    selection = load_json(selection_path)
    checks: list[dict] = []

    expected_original = failed_review["persistence"]["current_package_hashes"]
    current_original = hash_tree(ORIGINAL_CANDIDATE, {".uasset", ".umap"})
    current_attempt03 = hash_tree(ATTEMPT03_CONTENT, {".uasset", ".umap"})
    current_runtime = hash_tree(RUNTIME_MAPS, {".uasset", ".umap"})
    current_config = hash_tree(CONFIG)

    add(
        checks,
        "original_candidate_hash_invariance",
        current_original == expected_original
        and current_original == preflight["original_candidate_packages"],
        f"expected={len(expected_original)},current={len(current_original)}",
    )
    add(
        checks,
        "runtime_map_hash_invariance",
        current_runtime == preflight["runtime_map_packages"],
        f"before={len(preflight['runtime_map_packages'])},after={len(current_runtime)}",
    )
    add(
        checks,
        "config_hash_invariance",
        current_config == preflight["config_files"],
        f"before={len(preflight['config_files'])},after={len(current_config)}",
    )
    add(
        checks,
        "one_new_attempt03_map_only",
        len(current_attempt03) == 1
        and current_attempt03 == build.get("attempt03_packages", {}),
        json.dumps(current_attempt03, sort_keys=True),
    )
    add(
        checks,
        "build_gate_and_transforms",
        build.get("gate")
        == "PASS_ATTEMPT03_MAP_BUILD_REQUIRES_FRESH_TRANSFORM_AUDIT"
        and len(build.get("actors", [])) == 12
        and build.get("existing_candidate_packages_unchanged") is True
        and build.get("runtime_maps_unchanged") is True
        and build.get("config_unchanged") is True,
        str(build.get("gate")),
    )
    captures = sweep.get("captures", [])
    capture_hashes_ok = (
        len(captures) == 63
        and all(
            Path(record["path"]).is_file()
            and sha256_file(Path(record["path"])) == record["sha256"]
            and record.get("dimensions") == [2048, 2048]
            for record in captures
        )
    )
    add(
        checks,
        "d3d12_sm6_exact_63_sweep",
        sweep.get("gate")
        == "PASS_ATTEMPT03_SWEEP_AWAITING_OFFLINE_GLOBAL_EV_SELECTION"
        and sweep.get("rhi_validation") == "D3D12|SM6"
        and sweep.get("capture_count") == 63
        and capture_hashes_ok
        and sweep.get("original_candidate_packages_unchanged") is True
        and sweep.get("attempt03_packages_unchanged") is True
        and sweep.get("world_saved") is False
        and sweep.get("package_save_invoked") is False,
        f"gate={sweep.get('gate')},count={len(captures)},rhi={sweep.get('rhi_validation')}",
    )
    canonical = selection.get("canonical_captures", [])
    canonical_ok = (
        len(canonical) == 9
        and all(
            Path(record["path"]).is_file()
            and sha256_file(Path(record["path"])) == record["sha256"]
            and record.get("dimensions") == [2048, 2048]
            for record in canonical
        )
    )
    add(
        checks,
        "offline_global_ev_selection",
        selection.get("gate")
        == "PASS_ATTEMPT03_EXPOSURE_SELECTED_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
        and selection.get("canonical_capture_count") == 9
        and selection.get("files_are_byte_for_byte_selected_pilot_copies") is True
        and canonical_ok,
        f"gate={selection.get('gate')},count={len(canonical)}",
    )
    add(
        checks,
        "bound_contract_and_preflight",
        preflight.get("contract_sha256") == sha256_file(CONTRACT)
        and preflight.get("failed_review_sha256") == sha256_file(FAILED_REVIEW)
        and preflight.get("attempt03_content_absent") is True,
        str(preflight.get("contract_sha256")),
    )
    non_promotable = all(
        record.get("promotion_allowed") is False
        and record.get("p3_4_closed") is False
        for record in (build, sweep, selection)
    )
    add(
        checks,
        "promotion_and_p3_4_remain_false",
        non_promotable
        and contract.get("promotion_allowed") is False
        and contract.get("p3_4_closed") is False,
        "Attempt03 remains review-only",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-execution-audit.v1",
        "gate": (
            "PASS_ATTEMPT03_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
            if not failures
            else "FAIL_CLOSED_ATTEMPT03_EXECUTION_AUDIT"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
