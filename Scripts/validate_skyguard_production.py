from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "Scripts" / "skyguard_production.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("skyguard_production", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {CONTROLLER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    controller = load_controller()
    manifest = controller.load_manifest()
    errors = controller.validate_manifest(manifest)

    required_assets = {
        "core-apache-cockpit",
        "core-apache-30mm",
        "core-apache-hydra",
        "core-apache-hellfire",
        "core-apache-airframe",
        "core-yak52-airframe",
        "core-yak52-cockpit",
        "core-pilot",
        "core-rear-gunner",
        "core-hand-forearm",
        "core-rifle",
        "core-igla-launcher",
        "core-igla-missile",
        "core-shahed136",
        "m01-pathfinder-boss",
        "m02-breakwater-boss",
        "m03-road-hunter-boss",
        "m04-black-kite-boss",
        "m05-tempest-boss",
        "m06-runway-breaker-boss",
        "m07-radar-ghost-boss",
        "m08-lifeline-hunter-boss",
        "m09-iron-rain-boss",
        "m10-last-flight-boss",
        "release-clean-machine",
    }
    actual = {asset["id"] for asset in manifest["assets"]}
    missing = sorted(required_assets - actual)
    if missing:
        errors.append(f"Required production assets are missing: {missing}")

    execution_order = manifest.get("execution_order") or []
    if not execution_order or execution_order[0] != "P0-apache-cpg-hero-slice":
        errors.append("execution_order must start with P0-apache-cpg-hero-slice.")

    by_id = {asset["id"]: asset for asset in manifest["assets"]}
    apache_ids = [
        "core-apache-cockpit",
        "core-apache-30mm",
        "core-apache-hydra",
        "core-apache-hellfire",
        "core-apache-airframe",
    ]
    for asset_id in apache_ids:
        asset = by_id.get(asset_id)
        if asset is None:
            continue
        if asset.get("lane") != "P0-apache-cpg-hero-slice":
            errors.append(f"{asset_id} must live in P0-apache-cpg-hero-slice.")
        if asset.get("status") not in {"queued", "source_candidate"}:
            errors.append(f"{asset_id} must remain queued or source_candidate until a real worker exists.")
        if asset.get("worker"):
            errors.append(f"{asset_id} must not register a phantom worker.")

    deferred_archive = [
        "core-yak52-airframe",
        "core-yak52-cockpit",
        "core-pilot",
        "core-rear-gunner",
        "core-hand-forearm",
        "core-rifle",
        "core-igla-launcher",
        "core-igla-missile",
        "core-shahed136",
    ]
    for asset_id in deferred_archive:
        asset = by_id.get(asset_id)
        if asset is None:
            continue
        if asset.get("status") != "deferred":
            errors.append(f"{asset_id} must remain deferred in the archived Yak/Igla P0 lane.")

    if manifest["policies"].get("automatic_retries") != 0:
        errors.append("Automatic retries must remain zero.")
    if not manifest["policies"].get("one_heavy_process"):
        errors.append("One-heavy-process policy is not enabled.")
    if not manifest["policies"].get("circular_hashes_forbidden"):
        errors.append("Circular-hash prohibition is not enabled.")
    if not manifest["policies"].get("visual_review_required"):
        errors.append("Visual review must remain required.")
    if not manifest["policies"].get("unreal_import_requires_acceptance"):
        errors.append("Unreal import must still require acceptance.")

    accepted = [asset["id"] for asset in manifest["assets"] if asset["status"] == "accepted"]
    payload = {
        "schema": "skyguard.production-validation.v1",
        "pass": not errors,
        "errors": errors,
        "asset_count": len(manifest["assets"]),
        "required_asset_count": len(required_assets),
        "accepted_asset_count": len(accepted),
        "accepted_assets": accepted,
        "executable_worker_assets": [
            asset["id"] for asset in manifest["assets"] if asset.get("worker")
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
