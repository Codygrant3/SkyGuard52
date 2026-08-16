from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "Scripts" / "skyguard_production.py"

APACHE_P0_IDS = (
    "core-apache-cockpit",
    "core-apache-cockpit-station-detail01",
    "core-apache-cockpit-station-model01",
    "core-apache-cockpit-station-model02",
    "core-apache-cockpit-station-model03",
    "core-apache-cockpit-station-model04",
    "core-apache-cockpit-station-model05",
    "core-apache-cockpit-station-model06",
    "core-apache-cockpit-station-model07",
    "core-apache-cockpit-station-model08",
    "core-apache-30mm",
    "core-apache-hydra",
    "core-apache-hellfire",
    "core-apache-airframe",
)
APACHE_P0_LANE = "P0-apache-cpg-hero-slice"
APACHE_P0_ALLOWED_STATES = {
    "queued",
    "source_candidate",
    "ready",
    "running",
    "awaiting_review",
    "accepted",
}
ARCHIVED_P0_IDS = (
    "core-yak52-airframe",
    "core-yak52-cockpit",
    "core-pilot",
    "core-rear-gunner",
    "core-hand-forearm",
    "core-rifle",
    "core-igla-launcher",
    "core-igla-missile",
    "core-shahed136",
)


def load_controller():
    spec = importlib.util.spec_from_file_location("skyguard_production", CONTROLLER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {CONTROLLER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def worker_script_value(asset: dict[str, Any]) -> str | None:
    """Return the registered worker script path, or None if worker is omitted."""
    worker = asset.get("worker")
    if worker in (None, "", False):
        return None
    if not isinstance(worker, dict):
        return ""
    script = worker.get("script")
    if isinstance(script, str) and script.strip():
        return script
    return ""


def apache_p0_contract_errors(
    manifest: dict[str, Any],
    root: Path | None = None,
) -> list[str]:
    """Lane, status, and worker-path checks for the live Apache CPG P0 slice.

    Omitted workers stay valid. A worker is allowed only when ``worker.script``
    is a real file under the project. Status may advance through the normal
    controller cycle; this does not authorize a ready→accepted skip.
    """
    project_root = root or ROOT
    errors: list[str] = []
    execution_order = manifest.get("execution_order") or []
    if not execution_order or execution_order[0] != APACHE_P0_LANE:
        errors.append("execution_order must start with P0-apache-cpg-hero-slice.")

    by_id = {asset["id"]: asset for asset in manifest.get("assets", [])}
    for asset_id in APACHE_P0_IDS:
        asset = by_id.get(asset_id)
        if asset is None:
            continue
        if asset.get("lane") != APACHE_P0_LANE:
            errors.append(f"{asset_id} must live in {APACHE_P0_LANE}.")
        status = asset.get("status")
        if status not in APACHE_P0_ALLOWED_STATES:
            allowed = ", ".join(sorted(APACHE_P0_ALLOWED_STATES))
            errors.append(
                f"{asset_id} has invalid Apache P0 status {status!r}; allowed: {allowed}."
            )
        script = worker_script_value(asset)
        if script is None:
            continue
        script_path = project_root / Path(script.replace("\\", "/"))
        if not script_path.is_file():
            errors.append(
                f"{asset_id} registered a phantom worker: {script} is not a file under the project."
            )

    for asset_id in ARCHIVED_P0_IDS:
        asset = by_id.get(asset_id)
        if asset is None:
            continue
        if asset.get("status") != "deferred":
            errors.append(
                f"{asset_id} must remain deferred in the archived Yak/Igla P0 lane."
            )
    return errors


def main() -> int:
    controller = load_controller()
    manifest = controller.load_manifest()
    errors = controller.validate_manifest(manifest)

    required_assets = {
        *APACHE_P0_IDS,
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

    errors.extend(apache_p0_contract_errors(manifest))

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
