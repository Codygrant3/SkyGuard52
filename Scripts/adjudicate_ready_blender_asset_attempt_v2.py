from __future__ import annotations

"""Postflight for production-controller Blender attempts.

The original adjudicator correctly validates immutable output contracts, but its
offline lane audit requires every future attempt namespace to be absent and
every lane to remain ``ready``.  Those conditions cannot be true after the
controller has completed the very attempt being adjudicated.  This version
keeps the same artifact validation and narrows the static audit to the target
lane, accepting the target's governed ``awaiting_review`` state.
"""

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from . import adjudicate_ready_blender_asset_attempt as base
    from . import blender_hero_quality_gate
except ImportError:  # Direct script execution from the project root.
    import adjudicate_ready_blender_asset_attempt as base
    import blender_hero_quality_gate


SCHEMA = "skyguard.ready-blender-attempt-postflight.v2"
SCRIPT_RELATIVE = r"Scripts\adjudicate_ready_blender_asset_attempt_v2.py"


class PostflightError(RuntimeError):
    pass


def _has_governed_mode_separation(source: str) -> bool:
    """Accept legacy per-run authorization or the standing-authority guard.

    Both forms must retain an explicit offline mode.  The standing-authority
    form additionally has to prove that the mechanical execution switch is
    bound to the centralized policy instead of silently removing the guard.
    """
    if "OfflineContractTest" not in source:
        return False
    legacy = "AuthorizeSingleBlender" in source
    standing = all(
        token in source
        for token in (
            "ExecuteOnce",
            "StandingAuthority",
            "per_run_user_authorization_required",
            "one_heavy_process_at_a_time",
            "automatic_retry_count",
            "failed_namespace_reuse",
        )
    )
    return legacy or standing


def _manifest_assets() -> dict[str, dict[str, Any]]:
    manifest = base.load_json(base.MANIFEST_PATH)
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise PostflightError("Production manifest has no asset list.")
    return {str(asset["id"]): asset for asset in assets}


def validate_target_contract(asset_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = base.load_json(base.CONTRACT_PATH)
    if payload.get("schema") != "skyguard.ready-blender-output-contracts.v1":
        raise PostflightError("Unexpected ready Blender output-contract schema.")
    contracts = payload.get("contracts")
    if not isinstance(contracts, dict) or asset_id not in contracts:
        raise PostflightError(f"No registered output contract for {asset_id}.")

    assets = _manifest_assets()
    asset = assets.get(asset_id)
    if asset is None:
        raise PostflightError(f"Production manifest is missing {asset_id}.")
    if asset.get("status") not in {"ready", "awaiting_review"}:
        raise PostflightError(
            f"{asset_id} must be ready or awaiting_review, not {asset.get('status')}."
        )

    contract = contracts[asset_id]
    worker = asset.get("worker", {})
    if worker.get("script") != contract.get("worker_script"):
        raise PostflightError(f"Worker binding mismatch for {asset_id}.")
    expected_renders = sum(int(group["count"]) for group in contract["render_groups"])
    if int(worker.get("minimum_renders", -1)) != expected_renders:
        raise PostflightError(f"Render-count contract mismatch for {asset_id}.")
    postflight = worker.get("postflight", {})
    if postflight.get("script") != SCRIPT_RELATIVE:
        raise PostflightError(f"Postflight v2 is not bound for {asset_id}.")
    if postflight.get("mandatory_after_automatic_controller_pass") is not True:
        raise PostflightError(f"Mandatory postflight flag is not true for {asset_id}.")
    if postflight.get("visual_review_still_required") is not True:
        raise PostflightError(f"Visual-review requirement is not true for {asset_id}.")

    authorities = [base.verify_authority(record) for record in contract["authorities"]]
    worker_sources = [
        base.PROJECT_ROOT / str(record["path"])
        for record in contract["authorities"]
        if str(record["path"]).startswith("Scripts\\Workers\\")
        and str(record["path"]).endswith(".py")
    ]
    merged_source = "\n".join(path.read_text(encoding="utf-8") for path in worker_sources)
    hazards = sorted(
        {
            description
            for pattern, description in base.FORBIDDEN_WORKER_PATTERNS.items()
            if pattern in merged_source
        }
    )
    if hazards:
        raise PostflightError(f"Known Blender hazard in {asset_id}: {hazards}")
    if 'bpy.ops.render.render(write_still=True)' not in merged_source:
        raise PostflightError(f"{asset_id} has no governed write-still render path.")

    supervisor = base.PROJECT_ROOT / str(contract["supervisor_script"])
    source = supervisor.read_text(encoding="utf-8")
    launch_paths = source.count("$ControllerPath run $AssetId") + source.count(
        "$CyclePath run $AssetId"
    )
    if launch_paths != 1:
        raise PostflightError(f"{asset_id} supervisor must expose one governed run path.")
    if "Start-Process" in source or "blender.exe" in source.lower():
        raise PostflightError(f"{asset_id} supervisor has an alternate Blender path.")
    if not _has_governed_mode_separation(source):
        raise PostflightError(f"{asset_id} supervisor lacks mode separation.")

    attempt_parent = base.ATTEMPTS_ROOT / asset_id
    prior_attempts = []
    if attempt_parent.is_dir():
        for attempt in sorted(path for path in attempt_parent.iterdir() if path.is_dir()):
            terminal = attempt / "terminal.json"
            if not terminal.is_file():
                raise PostflightError(f"Prior attempt has no terminal receipt: {attempt}")
            payload = base.load_json(terminal)
            if payload.get("status") not in {"failed", "awaiting_review"}:
                raise PostflightError(
                    f"Prior attempt has unsupported terminal status: {attempt}: {payload.get('status')}"
                )
            prior_attempts.append(
                {
                    "attempt": attempt.name,
                    "status": payload.get("status"),
                    "terminal_sha256": base.sha256(terminal),
                }
            )
    if asset.get("status") == "ready" and any(
        record["status"] != "failed" for record in prior_attempts
    ):
        raise PostflightError(
            f"Ready recovery lane has a nonterminal prior attempt: {attempt_parent}"
        )
    if asset.get("status") == "awaiting_review" and not attempt_parent.is_dir():
        raise PostflightError(f"Awaiting-review lane has no attempt namespace: {attempt_parent}")

    static = {
        "asset_id": asset_id,
        "asset_status": asset.get("status"),
        "authority_count": len(authorities),
        "known_hazard_count": 0,
        "governed_run_paths": 1,
        "direct_blender_launch_paths": 0,
        "expected_render_count": expected_renders,
        "attempt_parent_exists": attempt_parent.exists(),
        "prior_attempts": prior_attempts,
        "mandatory_postflight": True,
        "visual_review_still_required": True,
    }
    return contract, static


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--attempt-dir")
    parser.add_argument("--report")
    parser.add_argument("--offline-authority-audit", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": "FAILED_WITH_EVIDENCE",
        "asset_id": args.asset_id,
        "automatic_visual_acceptance": False,
        "unreal_import_authorized": False,
        "errors": [],
    }
    try:
        contract, static = validate_target_contract(args.asset_id)
        report["contract_sha256"] = base.sha256(base.CONTRACT_PATH)
        report["target_lane_audit"] = static
        report["heavy_processes"] = base.heavy_processes()
        if report["heavy_processes"]:
            raise PostflightError(
                f"Heavy process active during postflight: {report['heavy_processes']}"
            )
        if args.offline_authority_audit:
            if args.attempt_dir or args.report:
                raise PostflightError(
                    "Offline authority audit cannot target an attempt or write a governed report."
                )
            report["classification"] = "PASSED_TARGET_LANE_POSTFLIGHT_V2_OFFLINE_AUDIT"
        else:
            if not args.attempt_dir or not args.report:
                raise PostflightError("Postflight requires --attempt-dir and --report.")
            attempt = Path(args.attempt_dir).resolve()
            report_path = Path(args.report).resolve()
            if report_path == attempt or attempt in report_path.parents:
                raise PostflightError(
                    "Postflight report must remain outside the immutable attempt directory."
                )
            try:
                report["attempt_validation"] = base.validate_attempt(
                    args.asset_id, attempt, contract
                )
            except Exception as exc:
                report["errors"].append(f"{type(exc).__name__}: {exc}")
            try:
                report["hero_quality_gate"] = blender_hero_quality_gate.evaluate(
                    attempt, contract
                )
                report["errors"].extend(report["hero_quality_gate"]["errors"])
            except Exception as exc:
                report["errors"].append(f"{type(exc).__name__}: {exc}")
            if not report["errors"]:
                report["classification"] = (
                    "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW"
                )
    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")

    if args.report:
        base.atomic_json(Path(args.report).resolve(), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["classification"].startswith("PASSED_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
