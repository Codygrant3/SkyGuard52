"""Independent offline execution audit for synchronized Recovery02."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY02_CONTRACT.json"
ORIGINAL_CANDIDATE = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
ATTEMPT03_CONTENT = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
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
        raise RuntimeError("immutable Recovery02 audit output already exists")
    contract = load_json(CONTRACT_PATH)
    preflight = load_json(Path(args.preflight))
    sweep = load_json(Path(args.sweep_manifest))
    selection = load_json(Path(args.selection_receipt))
    pilot_path = Path(sweep["pilot_receipt"])
    pilot = load_json(pilot_path)
    checks: list[dict] = []

    bound_ok = True
    for record in contract["bound_evidence"].values():
        path = ROOT / record["path"]
        bound_ok = (
            bound_ok
            and path.is_file()
            and path.stat().st_size == record["bytes"]
            and sha256_file(path) == record["sha256"]
        )
    add(checks, "recovery01_evidence_and_review_map_still_bound", bound_ok, "all bound hashes exact")

    current_original = hash_tree(ORIGINAL_CANDIDATE, {".uasset", ".umap"})
    current_attempt03 = hash_tree(ATTEMPT03_CONTENT, {".uasset", ".umap"})
    current_runtime = hash_tree(RUNTIME_MAPS, {".uasset", ".umap"})
    current_config = hash_tree(CONFIG)
    add(
        checks,
        "original_candidate_hash_invariance",
        current_original == preflight["original_candidate_packages"],
        f"packages={len(current_original)}",
    )
    add(
        checks,
        "attempt03_review_map_hash_invariance",
        current_attempt03 == preflight["attempt03_packages"]
        and len(current_attempt03) == 1,
        json.dumps(current_attempt03, sort_keys=True),
    )
    add(
        checks,
        "runtime_map_hash_invariance",
        current_runtime == preflight["runtime_map_packages"],
        f"packages={len(current_runtime)}",
    )
    add(
        checks,
        "config_hash_invariance",
        current_config == preflight["config_files"],
        f"files={len(current_config)}",
    )

    pilot_records = pilot.get("captures", [])
    pilot_bounds = contract["pilot"]["hard_liveness_bounds"]
    pilot_ok = (
        pilot.get("gate") == "PASS_RECOVERY02_PILOT_LIVE_FULL_SWEEP_ALLOWED"
        and pilot.get("full_sweep_allowed") is True
        and len(pilot_records) == 3
        and len({record["sha256"] for record in pilot_records})
        == pilot_bounds["unique_png_hash_count"]
        and all(
            Path(record["path"]).is_file()
            and sha256_file(Path(record["path"])) == record["sha256"]
            and record["metrics"]["active_pixel_fraction"]
            >= pilot_bounds["minimum_active_pixel_fraction_luma_gt_8"]
            and record["metrics"]["maximum_channel_value"]
            >= pilot_bounds["minimum_max_channel_value"]
            and record["metrics"]["unique_color_count_capped_at_4096"]
            >= pilot_bounds["minimum_unique_color_count"]
            and record["metrics"]["sentinel_magenta_fraction"]
            <= pilot_bounds["maximum_sentinel_magenta_fraction"]
            for record in pilot_records
        )
    )
    add(
        checks,
        "pilot_proved_live_synchronized_rendering",
        pilot_ok and sha256_file(pilot_path) == sweep["pilot_receipt_sha256"],
        f"gate={pilot.get('gate')},count={len(pilot_records)}",
    )

    captures = sweep.get("captures", [])
    capture_hashes = [record.get("sha256") for record in captures]
    captures_ok = (
        len(captures) == 72
        and len(set(capture_hashes)) == 72
        and all(
            Path(record["path"]).is_file()
            and sha256_file(Path(record["path"])) == record["sha256"]
            and record.get("dimensions") == [2048, 2048]
            for record in captures
        )
    )
    add(
        checks,
        "d3d12_sm6_exact_72_unique_synchronized_sweep",
        sweep.get("gate")
        == "PASS_RECOVERY02_SYNCHRONIZED_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION"
        and sweep.get("rhi_validation") == "D3D12|SM6"
        and sweep.get("capture_count") == 72
        and captures_ok
        and sweep.get("fresh_scene_capture_actor_per_frame") is True
        and sweep.get("fresh_render_target_per_frame") is True
        and sweep.get("sentinel_clear_before_capture") is True
        and sweep.get("world_saved") is False
        and sweep.get("package_save_invoked") is False,
        f"gate={sweep.get('gate')},count={len(captures)},unique={len(set(capture_hashes))}",
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
        "one_global_rig_and_nine_canonical_captures",
        selection.get("gate")
        == "PASS_RECOVERY02_GLOBAL_RIG_SELECTED_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
        and isinstance(selection.get("selected_rig_id"), str)
        and selection.get("canonical_capture_count") == 9
        and selection.get("files_are_byte_for_byte_selected_rig_copies") is True
        and canonical_ok,
        f"gate={selection.get('gate')},rig={selection.get('selected_rig_id')}",
    )
    add(
        checks,
        "promotion_and_p3_4_remain_false",
        all(
            record.get("promotion_allowed") is False
            and record.get("p3_4_closed") is False
            for record in (pilot, sweep, selection, contract)
        ),
        "Recovery02 remains review-only",
    )
    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery02-execution-audit.v1",
        "gate": (
            "PASS_RECOVERY02_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
            if not failures
            else "FAIL_CLOSED_RECOVERY02_EXECUTION_AUDIT"
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
