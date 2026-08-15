from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(r"D:\Skyguard52")
SCRIPTS_ROOT = PROJECT_ROOT / "Scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import adjudicate_ready_blender_asset_attempt as base


ASSET_ID = "core-yak52-airframe-recovery01"
BASE_CONTRACT_ASSET_ID = "core-yak52-airframe"
RECOVERY_FREEZE = (
    PROJECT_ROOT
    / "Docs"
    / "AAA_Review"
    / "PHASE2_YAK52_AIRFRAME_REFINEMENT01_RECOVERY01_OFFLINE_DESIGN_FREEZE.json"
)
RECOVERY_FREEZE_BYTES = 2759
RECOVERY_FREEZE_SHA256 = "1feb7abd7fabd5d005be6b3e9007d419639443af6cb5bf35b1b6945f20b5573f"
BASE_CONTRACT_BYTES = 14718
BASE_CONTRACT_SHA256 = "624b597f0b3efe1ef9c79d90ab8864d54057f8e339df1cb9a6effa900aa9e9d8"
BASE_ADJUDICATOR_BYTES = 18323
BASE_ADJUDICATOR_SHA256 = "aa358f1509817105b07a63124edeab69b0da29b81a61b6a47abc069855ece12d"


class RecoveryPostflightError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, expected_bytes: int, expected_sha256: str) -> dict[str, Any]:
    if not path.is_file():
        raise RecoveryPostflightError(f"Missing frozen authority: {path}")
    actual = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }
    if actual["bytes"] != expected_bytes or actual["sha256"] != expected_sha256:
        raise RecoveryPostflightError(f"Frozen authority mismatch: {path}")
    return actual


def verify_recovery_authorities() -> list[dict[str, Any]]:
    records = [
        verify_file(RECOVERY_FREEZE, RECOVERY_FREEZE_BYTES, RECOVERY_FREEZE_SHA256),
        verify_file(base.CONTRACT_PATH, BASE_CONTRACT_BYTES, BASE_CONTRACT_SHA256),
        verify_file(Path(base.__file__).resolve(), BASE_ADJUDICATOR_BYTES, BASE_ADJUDICATOR_SHA256),
    ]
    freeze = base.load_json(RECOVERY_FREEZE)
    if freeze.get("classification") != (
        "PASSED_READY_FOR_AUTONOMOUS_SINGLE_YAK52_AIRFRAME_RECOVERY01_BLENDER_EXECUTION"
    ):
        raise RecoveryPostflightError("Unexpected Recovery01 offline-freeze classification.")
    if freeze.get("asset_id") != ASSET_ID:
        raise RecoveryPostflightError("Recovery01 offline freeze targets the wrong asset.")
    members = freeze.get("members")
    if not isinstance(members, list) or len(members) != 9:
        raise RecoveryPostflightError("Recovery01 offline freeze must contain exactly nine members.")
    for member in members:
        records.append(
            verify_file(
                Path(str(member["path"])),
                int(member["bytes"]),
                str(member["sha256"]),
            )
        )
    return records


def load_base_contract() -> dict[str, Any]:
    payload = base.load_json(base.CONTRACT_PATH)
    if payload.get("schema") != "skyguard.ready-blender-output-contracts.v1":
        raise RecoveryPostflightError("Unexpected base output-contract schema.")
    contracts = payload.get("contracts")
    if not isinstance(contracts, dict) or BASE_CONTRACT_ASSET_ID not in contracts:
        raise RecoveryPostflightError("Frozen Yak-52 base contract is unavailable.")
    return contracts[BASE_CONTRACT_ASSET_ID]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-id", choices=[ASSET_ID])
    parser.add_argument("--attempt-dir")
    parser.add_argument("--report")
    parser.add_argument("--offline-contract-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report: dict[str, Any] = {
        "schema": "skyguard.phase2.yak52-airframe-refinement01-recovery01.postflight.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "asset_id": ASSET_ID,
        "automatic_visual_acceptance": False,
        "unreal_import_authorized": False,
        "errors": [],
    }
    try:
        report["authority_records"] = verify_recovery_authorities()
        contract = load_base_contract()
        report["base_contract_asset_id"] = BASE_CONTRACT_ASSET_ID
        report["base_contract_sha256"] = sha256(base.CONTRACT_PATH)
        if args.offline_contract_test:
            if args.asset_id or args.attempt_dir or args.report:
                raise RecoveryPostflightError(
                    "Offline contract test cannot target an attempt or write a governed report."
                )
            report["classification"] = "PASSED_RECOVERY01_POSTFLIGHT_OFFLINE_CONTRACT"
        else:
            if args.asset_id != ASSET_ID or not args.attempt_dir or not args.report:
                raise RecoveryPostflightError(
                    f"Postflight requires --asset-id {ASSET_ID}, --attempt-dir, and --report."
                )
            heavy = base.heavy_processes()
            report["heavy_processes"] = heavy
            if heavy:
                raise RecoveryPostflightError(
                    f"Heavy process active during postflight: {heavy}"
                )
            attempt = Path(args.attempt_dir).resolve()
            report_path = Path(args.report).resolve()
            if report_path == attempt or attempt in report_path.parents:
                raise RecoveryPostflightError(
                    "Postflight report must remain outside the immutable attempt directory."
                )
            report["attempt_validation"] = base.validate_attempt(ASSET_ID, attempt, contract)
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
