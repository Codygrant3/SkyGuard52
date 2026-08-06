"""Independent offline audit for persistent-capture Recovery03."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY03_CONTRACT.json"
ORIGINAL = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
ATTEMPT03 = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
RUNTIME = ROOT / "Content/Skyguard/Maps"
CONFIG = ROOT / "Config"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_tree(root: Path, suffixes: set[str] | None = None) -> dict[str, str]:
    records = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and (not suffixes or path.suffix.lower() in suffixes):
            records[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    return records


def load(path: Path) -> dict:
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
        raise RuntimeError("immutable Recovery03 audit output exists")
    contract = load(CONTRACT_PATH)
    preflight = load(Path(args.preflight))
    sweep = load(Path(args.sweep_manifest))
    selection = load(Path(args.selection_receipt))
    pilot_path = Path(sweep["pilot_receipt"])
    pilot = load(pilot_path)
    checks: list[dict] = []

    bound_ok = all(
        (ROOT / record["path"]).is_file()
        and (ROOT / record["path"]).stat().st_size == record["bytes"]
        and sha256_file(ROOT / record["path"]) == record["sha256"]
        for record in contract["bound_evidence"].values()
    )
    add(checks, "recovery02_evidence_and_review_map_bound", bound_ok, "all hashes exact")
    current = {
        "original_candidate_packages": hash_tree(ORIGINAL, {".uasset", ".umap"}),
        "attempt03_packages": hash_tree(ATTEMPT03, {".uasset", ".umap"}),
        "runtime_map_packages": hash_tree(RUNTIME, {".uasset", ".umap"}),
        "config_files": hash_tree(CONFIG),
    }
    for key, label in (
        ("original_candidate_packages", "original_candidate_hash_invariance"),
        ("attempt03_packages", "attempt03_review_map_hash_invariance"),
        ("runtime_map_packages", "runtime_map_hash_invariance"),
        ("config_files", "config_hash_invariance"),
    ):
        add(
            checks,
            label,
            current[key] == preflight[key]
            and (key != "attempt03_packages" or len(current[key]) == 1),
            f"count={len(current[key])}",
        )

    bounds = contract["pilot"]["hard_liveness_bounds"]
    pilot_records = pilot.get("captures", [])
    pilot_ok = (
        pilot.get("gate")
        == "PASS_RECOVERY03_PERSISTENT_PILOT_LIVE_FULL_SWEEP_ALLOWED"
        and pilot.get("persistent_scene_capture_actor_count") == 1
        and pilot.get("persistent_render_target_count") == 1
        and len(pilot_records) == 3
        and len({record["sha256"] for record in pilot_records}) == 3
        and all(
            Path(record["path"]).is_file()
            and sha256_file(Path(record["path"])) == record["sha256"]
            and record["metrics"]["active_pixel_fraction"]
            >= bounds["minimum_active_pixel_fraction_luma_gt_8"]
            and record["metrics"]["maximum_channel_value"]
            >= bounds["minimum_max_channel_value"]
            and record["metrics"]["unique_color_count_capped_at_4096"]
            >= bounds["minimum_unique_color_count"]
            and record["metrics"]["sentinel_magenta_fraction"]
            <= bounds["maximum_sentinel_magenta_fraction"]
            for record in pilot_records
        )
    )
    add(
        checks,
        "persistent_pilot_proved_live_rendering",
        pilot_ok and sha256_file(pilot_path) == sweep["pilot_receipt_sha256"],
        f"gate={pilot.get('gate')}",
    )
    captures = sweep.get("captures", [])
    hashes = [record.get("sha256") for record in captures]
    sweep_ok = (
        sweep.get("gate")
        == "PASS_RECOVERY03_PERSISTENT_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION"
        and sweep.get("rhi_validation") == "D3D12|SM6"
        and len(captures) == 72
        and len(set(hashes)) == 72
        and sweep.get("persistent_scene_capture_actor_count") == 1
        and sweep.get("persistent_render_target_count") == 1
        and sweep.get("world_saved") is False
        and sweep.get("package_save_invoked") is False
        and all(
            Path(record["path"]).is_file()
            and sha256_file(Path(record["path"])) == record["sha256"]
            and record["dimensions"] == [2048, 2048]
            for record in captures
        )
    )
    add(
        checks,
        "d3d12_sm6_exact_72_unique_persistent_sweep",
        sweep_ok,
        f"count={len(captures)},unique={len(set(hashes))}",
    )
    canonical = selection.get("canonical_captures", [])
    selection_ok = (
        selection.get("gate")
        == "PASS_RECOVERY03_GLOBAL_RIG_SELECTED_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
        and selection.get("canonical_capture_count") == 9
        and selection.get("files_are_byte_for_byte_selected_rig_copies") is True
        and len(canonical) == 9
        and all(
            Path(record["path"]).is_file()
            and sha256_file(Path(record["path"])) == record["sha256"]
            for record in canonical
        )
    )
    add(
        checks,
        "one_global_rig_nine_canonical_captures",
        selection_ok,
        f"gate={selection.get('gate')}",
    )
    add(
        checks,
        "promotion_and_p3_4_false",
        all(
            record.get("promotion_allowed") is False
            and record.get("p3_4_closed") is False
            for record in (pilot, sweep, selection, contract)
        ),
        "review-only",
    )
    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery03-execution-audit.v1",
        "gate": (
            "PASS_RECOVERY03_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
            if not failures
            else "FAIL_CLOSED_RECOVERY03_EXECUTION_AUDIT"
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
