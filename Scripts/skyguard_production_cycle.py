from __future__ import annotations

"""Run one registered Blender worker and its mandatory automatic postflight.

This is the preferred production entry point.  It keeps human visual acceptance
separate, never retries, and fails the lane when automatic postflight rejects an
otherwise successful Blender process.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from . import adjudicate_ready_blender_asset_attempt_v2 as postflight_v2
    from . import skyguard_production as controller
except ImportError:  # Direct script execution from the project root.
    import adjudicate_ready_blender_asset_attempt_v2 as postflight_v2
    import skyguard_production as controller


ROOT = controller.ROOT
CYCLES_ROOT = controller.PRODUCTION / "Cycles"
STANDING_AUTH = controller.PRODUCTION / "standing_heavy_process_authorization.json"


class CycleError(RuntimeError):
    pass


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def verify_standing_authorization() -> dict[str, Any]:
    payload = controller.load_json(STANDING_AUTH)
    if payload.get("status") != "ACTIVE":
        raise CycleError("Standing heavy-process authorization is not active.")
    policy = payload.get("execution_policy", {})
    required = {
        "per_run_user_authorization_required": False,
        "one_heavy_process_at_a_time": True,
        "automatic_retry_count": 0,
        "failed_namespace_reuse": False,
        "immutable_attempt_evidence_required": True,
    }
    for key, expected in required.items():
        if policy.get(key) != expected:
            raise CycleError(f"Standing-authorization policy mismatch: {key}.")
    return payload


def format_postflight(asset: dict[str, Any], attempt: Path) -> tuple[list[str], Path]:
    binding = asset.get("worker", {}).get("postflight")
    if not isinstance(binding, dict):
        raise CycleError(f"{asset['id']} has no registered postflight.")
    if binding.get("mandatory_after_automatic_controller_pass") is not True:
        raise CycleError(f"{asset['id']} postflight is not mandatory.")
    if binding.get("visual_review_still_required") is not True:
        raise CycleError(f"{asset['id']} incorrectly bypasses visual review.")
    script = ROOT / str(binding.get("script", ""))
    if not script.is_file():
        raise CycleError(f"Postflight script is missing: {script}")
    attempt_id = attempt.name
    values = {
        "attempt_dir": str(attempt),
        "attempt_id": attempt_id,
        "output_dir": str(attempt / "output"),
    }
    arguments = [str(value).format(**values) for value in binding.get("arguments", [])]
    command = [sys.executable, str(script), *arguments]
    try:
        report_index = command.index("--report") + 1
        report = Path(command[report_index])
    except (ValueError, IndexError) as exc:
        raise CycleError("Postflight binding has no --report path.") from exc
    if not report.is_absolute():
        report = ROOT / report
    return command, report.resolve()


def update_after_postflight(
    asset_id: str, report_path: Path, passed: bool, reason: str
) -> None:
    manifest = controller.load_manifest()
    asset = controller.asset_index(manifest)[asset_id]
    asset["latest_postflight_report"] = str(report_path.relative_to(ROOT))
    asset["automatic_postflight_classification"] = (
        "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW"
        if passed
        else "FAILED_WITH_EVIDENCE"
    )
    if passed:
        if asset.get("status") != "awaiting_review":
            raise CycleError(
                f"Postflight passed but {asset_id} is {asset.get('status')}, not awaiting_review."
            )
        asset["state_reason"] = reason
        asset["state_changed_at_utc"] = controller.now_utc()
    else:
        if asset.get("status") == "awaiting_review":
            controller.transition(asset, "failed", reason)
        elif asset.get("status") != "failed":
            raise CycleError(
                f"Cannot fail postflight from asset state {asset.get('status')}."
            )
    controller.save_manifest(manifest)
    controller.append_event(
        {
            "event": "mandatory_postflight",
            "asset_id": asset_id,
            "passed": passed,
            "report": str(report_path.relative_to(ROOT)),
            "reason": reason,
        }
    )


def audit_asset(asset_id: str) -> dict[str, Any]:
    verify_standing_authorization()
    manifest = controller.load_manifest()
    errors = controller.validate_manifest(manifest)
    if errors:
        raise CycleError("; ".join(errors))
    asset = controller.asset_index(manifest).get(asset_id)
    if asset is None:
        raise CycleError(f"Unknown asset: {asset_id}")
    if asset.get("status") != "ready":
        raise CycleError(f"{asset_id} is {asset.get('status')}, not ready.")
    _, static = postflight_v2.validate_target_contract(asset_id)
    resource = controller.preflight(manifest)
    if not resource["pass"]:
        raise CycleError("Preflight failed: " + "; ".join(resource["errors"]))
    return {
        "schema": "skyguard.production-cycle-audit.v1",
        "asset_id": asset_id,
        "pass": True,
        "target_lane_postflight": static,
        "resource_preflight": resource,
        "standing_authorization": True,
        "human_visual_review_still_required": True,
    }


def run_cycle(asset_id: str) -> int:
    audit = audit_asset(asset_id)
    cycle_dir = CYCLES_ROOT / asset_id / f"cycle_{now_stamp()}"
    if cycle_dir.exists():
        raise CycleError(f"Cycle namespace already exists: {cycle_dir}")
    cycle_dir.mkdir(parents=True)
    controller.atomic_write_json(cycle_dir / "preflight.json", audit)

    terminal: dict[str, Any] = {
        "schema": "skyguard.production-cycle.v1",
        "asset_id": asset_id,
        "cycle_dir": str(cycle_dir),
        "controller_launch_count": 0,
        "postflight_launch_count": 0,
        "retry_count": 0,
        "classification": "FAILED_WITH_EVIDENCE",
        "started_at_utc": controller.now_utc(),
    }
    try:
        command = [
            sys.executable,
            str(ROOT / "Scripts" / "skyguard_production.py"),
            "run",
            asset_id,
        ]
        terminal["controller_command"] = command
        with (cycle_dir / "controller.stdout.log").open("w", encoding="utf-8") as stdout, (
            cycle_dir / "controller.stderr.log"
        ).open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, check=False)
        terminal["controller_launch_count"] = 1
        terminal["controller_exit_code"] = int(completed.returncode)
        terminal["controller_exit_code_type"] = type(completed.returncode).__name__
        if completed.returncode != 0:
            raise CycleError(f"Production controller failed with exit code {completed.returncode}.")

        manifest = controller.load_manifest()
        asset = controller.asset_index(manifest)[asset_id]
        if asset.get("status") != "awaiting_review":
            raise CycleError(
                f"Controller returned zero but {asset_id} is {asset.get('status')}."
            )
        attempt = ROOT / str(asset.get("latest_attempt", ""))
        if not attempt.is_dir():
            raise CycleError(f"Controller did not record a valid attempt: {attempt}")
        terminal["attempt_dir"] = str(attempt)

        postflight_command, report_path = format_postflight(asset, attempt)
        terminal["postflight_command"] = postflight_command
        terminal["postflight_report"] = str(report_path)
        with (cycle_dir / "postflight.stdout.log").open("w", encoding="utf-8") as stdout, (
            cycle_dir / "postflight.stderr.log"
        ).open("w", encoding="utf-8") as stderr:
            completed = subprocess.run(
                postflight_command, cwd=ROOT, stdout=stdout, stderr=stderr, check=False
            )
        terminal["postflight_launch_count"] = 1
        terminal["postflight_exit_code"] = int(completed.returncode)
        terminal["postflight_exit_code_type"] = type(completed.returncode).__name__
        if not report_path.is_file():
            raise CycleError("Mandatory postflight did not write its report.")
        report = controller.load_json(report_path)
        terminal["postflight_report_sha256"] = controller.sha256(report_path)
        classification = str(report.get("classification", ""))
        passed = (
            completed.returncode == 0
            and classification
            == "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW"
        )
        if not passed:
            reason = (
                f"Mandatory automatic postflight rejected the attempt: {classification or 'missing classification'}; "
                f"exit code {completed.returncode}."
            )
            update_after_postflight(asset_id, report_path, False, reason)
            raise CycleError(reason)

        reason = (
            "Blender output and mandatory automatic postflight passed; direct full-resolution "
            "visual review remains required before Unreal import or acceptance."
        )
        update_after_postflight(asset_id, report_path, True, reason)
        terminal["classification"] = (
            "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW"
        )
        return_code = 0
    except Exception as exc:
        terminal["error"] = f"{type(exc).__name__}: {exc}"
        return_code = 2
    finally:
        terminal["ended_at_utc"] = controller.now_utc()
        terminal["cycle_inventory"] = controller.inventory_files(cycle_dir)
        controller.atomic_write_json(cycle_dir / "terminal.json", terminal)

    print(json.dumps(terminal, indent=2))
    return return_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Skyguard one-attempt production cycle.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit = subparsers.add_parser("audit")
    audit.add_argument("asset")
    run = subparsers.add_parser("run")
    run.add_argument("asset")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "audit":
            print(json.dumps(audit_asset(args.asset), indent=2))
            return 0
        return run_cycle(args.asset)
    except Exception as exc:
        print(
            json.dumps({"classification": "FAILED_WITH_EVIDENCE", "error": f"{type(exc).__name__}: {exc}"}, indent=2),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
