"""Independent offline audit for base-lighting Recovery04."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY04_CONTRACT.json"
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
    parser.add_argument("--capture-manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise RuntimeError("immutable Recovery04 audit output exists")
    contract = load(CONTRACT_PATH)
    preflight = load(Path(args.preflight))
    manifest = load(Path(args.capture_manifest))
    pilot_path = Path(manifest["pilot_receipt"])
    pilot = load(pilot_path)
    checks: list[dict] = []

    bound_ok = all(
        (ROOT / record["path"]).is_file()
        and (ROOT / record["path"]).stat().st_size == record["bytes"]
        and sha256_file(ROOT / record["path"]) == record["sha256"]
        for record in contract["bound_evidence"].values()
    )
    add(checks, "recovery03_failure_known_good_and_review_map_bound", bound_ok, "all hashes exact")

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

    pilot_records = pilot.get("captures", [])
    candidates = contract["pilot"]["exposure_candidates_ev"]
    selected_ev = pilot.get("selected_exposure_bias_ev")
    eligible = [record for record in pilot_records if record.get("hard_bounds_passed")]
    expected_selected = (
        min(
            eligible,
            key=lambda record: (
                record["penalty"],
                abs(record["exposure_bias_ev"]),
                record["exposure_bias_ev"],
            ),
        )["exposure_bias_ev"]
        if eligible
        else None
    )
    pilot_ok = (
        pilot.get("gate")
        == "PASS_RECOVERY04_BASE_LIGHTING_LIVE_EXPOSURE_SELECTED_FULL_VIEWS_ALLOWED"
        and pilot.get("rhi_validation") == "D3D12|SM6"
        and pilot.get("base_spawn_lighting_used_once") is True
        and pilot.get("light_proxy_changes_after_spawn") == 0
        and len(pilot_records) == 6
        and [record["exposure_bias_ev"] for record in pilot_records] == candidates
        and all(
            record.get("effective_exposure_bias_ev")
            == float(record["exposure_bias_ev"])
            for record in pilot_records
        )
        and selected_ev == expected_selected
        and all(
            Path(record["path"]).is_file()
            and sha256_file(Path(record["path"])) == record["sha256"]
            and record["metrics"]["dimensions"] == [2048, 2048]
            for record in pilot_records
        )
    )
    add(
        checks,
        "exact_base_lighting_live_exposure_pilot",
        pilot_ok and sha256_file(pilot_path) == manifest["pilot_receipt_sha256"],
        f"selected_ev={selected_ev},eligible={len(eligible)}",
    )

    captures = manifest.get("captures", [])
    hashes = [record.get("sha256") for record in captures]
    full_ok = (
        manifest.get("gate") == "PASS_RECOVERY04_NINE_VIEWS_AWAITING_OFFLINE_AUDIT"
        and manifest.get("rhi_validation") == "D3D12|SM6"
        and manifest.get("selected_exposure_bias_ev") == selected_ev
        and manifest.get("base_spawn_lighting_used_once") is True
        and manifest.get("light_proxy_changes_after_spawn") == 0
        and len(captures) == 9
        and len(set(hashes)) == 9
        and manifest.get("world_saved") is False
        and manifest.get("package_save_invoked") is False
        and all(
            record.get("selected_exposure_bias_ev") == selected_ev
            and record.get("effective_exposure_bias_ev") == float(selected_ev)
            and record.get("hard_bounds_passed") is True
            and record.get("dimensions") == [2048, 2048]
            and Path(record["path"]).is_file()
            and sha256_file(Path(record["path"])) == record["sha256"]
            for record in captures
        )
    )
    add(
        checks,
        "exact_nine_unique_hard_bound_passing_views",
        full_ok,
        f"count={len(captures)},unique={len(set(hashes))}",
    )
    add(
        checks,
        "promotion_and_p3_4_false",
        all(
            record.get("promotion_allowed") is False
            and record.get("p3_4_closed") is False
            for record in (pilot, manifest, contract)
        ),
        "review-only",
    )
    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery04-execution-audit.v1",
        "gate": (
            "PASS_RECOVERY04_EXECUTION_AWAITING_ORIGINAL_RESOLUTION_REVIEW"
            if not failures
            else "FAIL_CLOSED_RECOVERY04_EXECUTION_AUDIT"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "selected_exposure_bias_ev": selected_ev,
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
