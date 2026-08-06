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

    if manifest["policies"].get("automatic_retries") != 0:
        errors.append("Automatic retries must remain zero.")
    if not manifest["policies"].get("one_heavy_process"):
        errors.append("One-heavy-process policy is not enabled.")
    if not manifest["policies"].get("circular_hashes_forbidden"):
        errors.append("Circular-hash prohibition is not enabled.")

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
