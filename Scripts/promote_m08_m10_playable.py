"""Fail-closed, dry-run-by-default promotion for M08-M10 playable maps."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME_REL = Path("Config/DefaultGame.ini")
MATRIX_REL = Path("Docs/AAA_Review/PHASE8_MISSION_SOAK_MATRIX.json")
COOK_VERIFIER_REL = Path("Scripts/verify_skyguard_phase8_cook_contract.py")
MAP_LINE_RE = re.compile(
    r'^\+MapsToCook=\(FilePath="(?P<map>/Game/[^"]+)"\)\r?$', re.MULTILINE
)
MISSION_ORDER = [f"M{index:02d}" for index in range(1, 11)]
PROMOTIONS = {
    "M08": {
        "expected": "/Game/Skyguard/Maps/Campaign_v1/Lvl_M08_RescueCover_Playable_v1",
        "assembly": "/Game/Skyguard/Maps/Campaign_v1/Lvl_M08_RescueCover_Assembly_v1",
    },
    "M09": {
        "expected": "/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Playable_v1",
        "assembly": "/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Assembly_v1",
    },
    "M10": {
        "expected": "/Game/Skyguard/Maps/Campaign_v1/Lvl_M10_EvacuationFinale_Playable_v1",
        "assembly": "/Game/Skyguard/Maps/Campaign_v1/Lvl_M10_EvacuationFinale_Assembly_v1",
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text_preserve_newlines(path: Path) -> str:
    payload = path.read_bytes()
    if payload.startswith(b"\xef\xbb\xbf"):
        payload = payload[3:]
    return payload.decode("utf-8")


def package_to_umap(root: Path, package: str) -> Path:
    if not package.startswith("/Game/"):
        raise ValueError(f"Invalid package: {package}")
    return root / "Content" / f"{package.removeprefix('/Game/')}.umap"


def mission_id_from_map(package: str) -> str | None:
    match = re.search(r"Lvl_(M(?:0[1-9]|10))_", package)
    return match.group(1) if match else None


def parse_timestamp_from_attempt(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    match = re.search(r"attempt_(\d{8}T\d{9}Z)$", value.replace("\\", "/"))
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y%m%dT%H%M%S%fZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None


def unified_diff(path: str, before: str, after: str) -> list[str]:
    return list(difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        fromfile=path + ".before",
        tofile=path + ".after",
        lineterm="",
    ))


def inspect_receipt(
    root: Path,
    mission_id: str,
    expected_map: str,
    now: datetime,
    max_age_hours: float,
) -> dict:
    receipt_path = root / "Saved/Reports" / f"{mission_id}_PLAYABLE_INTEGRATION_GATE_LATEST.json"
    build_path = root / "Saved/Reports" / f"{mission_id}_PLAYABLE_INTEGRATION_BUILD.json"
    umap = package_to_umap(root, expected_map)
    errors: list[str] = []
    receipt, build = None, None
    for label, path in (("receipt", receipt_path), ("build report", build_path)):
        if not path.is_file():
            errors.append(f"missing {label}: {path}")
    if receipt_path.is_file():
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid receipt JSON: {exc}")
    if build_path.is_file():
        try:
            build = json.loads(build_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid build report JSON: {exc}")
    if not umap.is_file():
        errors.append(f"missing playable umap: {umap}")

    if isinstance(receipt, dict):
        if receipt.get("gate") != "PASS":
            errors.append(f"receipt gate is {receipt.get('gate')!r}, expected PASS")
        audit = receipt.get("persistence_audit")
        if not isinstance(audit, dict) or audit.get("gate") != "PASS":
            errors.append("persistence audit is missing or not PASS")
        automation = receipt.get("automation")
        if (
            not isinstance(automation, dict)
            or automation.get("failure") != 0
            or automation.get("missing") not in ([], None)
            or not isinstance(automation.get("success"), int)
            or automation.get("success") <= 0
        ):
            errors.append("automation evidence is incomplete or failing")
        attempt_time = parse_timestamp_from_attempt(receipt.get("attempt"))
        if not attempt_time:
            errors.append("receipt attempt timestamp is missing or invalid")
        else:
            age_hours = (now - attempt_time).total_seconds() / 3600.0
            if age_hours < -0.25:
                errors.append("receipt timestamp is in the future")
            elif age_hours > max_age_hours:
                errors.append(
                    f"receipt is stale: {age_hours:.2f}h > {max_age_hours:.2f}h"
                )
        attempt = receipt.get("attempt")
        if not isinstance(attempt, str) or not Path(attempt).is_dir():
            errors.append("receipt attempt directory is missing")

    if isinstance(build, dict):
        if build.get("gate") != "PASS":
            errors.append(f"build gate is {build.get('gate')!r}, expected PASS")
        if build.get("target_map") != expected_map:
            errors.append(
                f"build target_map is {build.get('target_map')!r}, expected {expected_map}"
            )
        if build.get("source_preserved") is False:
            errors.append("build report says source assembly was not preserved")
        reported_hash = build.get("package_sha256")
        if not isinstance(reported_hash, str) or not re.fullmatch(
            r"[0-9a-f]{64}", reported_hash
        ):
            errors.append("build report package_sha256 is missing or invalid")
        elif umap.is_file() and sha256_file(umap) != reported_hash:
            errors.append("playable umap hash differs from build report")

    if receipt_path.is_file() and umap.is_file():
        if receipt_path.stat().st_mtime_ns < umap.stat().st_mtime_ns:
            errors.append("receipt predates the current playable umap")
    if receipt_path.is_file() and build_path.is_file():
        if receipt_path.stat().st_mtime_ns < build_path.stat().st_mtime_ns:
            errors.append("receipt predates the current build report")

    return {
        "mission_id": mission_id,
        "expected_map": expected_map,
        "receipt": str(receipt_path),
        "build_report": str(build_path),
        "umap": str(umap),
        "umap_exists": umap.is_file(),
        "umap_sha256": sha256_file(umap) if umap.is_file() else None,
        "valid": not errors,
        "errors": errors,
    }


def build_proposed_config(before: str, errors: list[str]) -> tuple[str, list[dict]]:
    maps = [match.group("map") for match in MAP_LINE_RE.finditer(before)]
    ids = [mission_id_from_map(package) for package in maps]
    if len(maps) != 10:
        errors.append(f"DefaultGame.ini has {len(maps)} MapsToCook entries, expected 10")
    if ids != MISSION_ORDER:
        errors.append(f"DefaultGame.ini mission order is {ids!r}, expected {MISSION_ORDER!r}")
    after = before
    substitutions: list[dict] = []
    for mission_id, spec in PROMOTIONS.items():
        old_line = f'+MapsToCook=(FilePath="{spec["assembly"]}")'
        new_line = f'+MapsToCook=(FilePath="{spec["expected"]}")'
        if old_line not in after:
            errors.append(f"DefaultGame.ini missing exact assembly line for {mission_id}")
        else:
            after = after.replace(old_line, new_line, 1)
        substitutions.append({
            "mission_id": mission_id,
            "before": old_line,
            "after": new_line,
        })
    proposed_maps = [match.group("map") for match in MAP_LINE_RE.finditer(after)]
    if [mission_id_from_map(package) for package in proposed_maps] != MISSION_ORDER:
        errors.append("proposed DefaultGame.ini does not preserve exact M01-M10 ordering")
    if len(proposed_maps) != 10 or len(set(proposed_maps)) != 10:
        errors.append("proposed DefaultGame.ini must contain ten unique maps")
    return after, substitutions


def build_proposed_matrix(before: str, errors: list[str]) -> tuple[str, list[dict]]:
    try:
        payload = json.loads(before)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid soak matrix JSON: {exc}")
        return before, []
    missions = payload.get("missions")
    if not isinstance(missions, list):
        errors.append("soak matrix missions must be an array")
        return before, []
    ids = [mission.get("id") for mission in missions if isinstance(mission, dict)]
    if payload.get("required_mission_count") != 10 or len(missions) != 10:
        errors.append("soak matrix must require and contain exactly ten missions")
    if ids != MISSION_ORDER:
        errors.append(f"soak matrix order is {ids!r}, expected {MISSION_ORDER!r}")
    substitutions: list[dict] = []
    by_id = {
        mission.get("id"): mission
        for mission in missions
        if isinstance(mission, dict)
    }
    for mission_id, spec in PROMOTIONS.items():
        mission = by_id.get(mission_id)
        if not mission:
            errors.append(f"soak matrix missing {mission_id}")
            continue
        before_map = mission.get("map")
        before_status = mission.get("status")
        if before_map != spec["assembly"]:
            errors.append(
                f"soak matrix {mission_id} map is {before_map!r}, expected assembly"
            )
        if before_status != "PROXY_ASSEMBLY_CANDIDATE":
            errors.append(
                f"soak matrix {mission_id} status is {before_status!r}, expected proxy"
            )
        mission["map"] = spec["expected"]
        mission["status"] = "PLAYABLE_INTEGRATION_CANDIDATE"
        substitutions.append({
            "mission_id": mission_id,
            "before": {
                "map": before_map,
                "status": before_status,
            },
            "after": {
                "map": spec["expected"],
                "status": "PLAYABLE_INTEGRATION_CANDIDATE",
            },
        })
    proposed_ids = [mission.get("id") for mission in missions]
    if proposed_ids != MISSION_ORDER:
        errors.append("proposed soak matrix does not preserve exact M01-M10 order")
    return json.dumps(payload, indent=2) + "\n", substitutions


def plan_promotion(
    root: Path = ROOT,
    *,
    now: datetime | None = None,
    max_receipt_age_hours: float = 72.0,
) -> tuple[dict, str, str]:
    now = now or datetime.now(timezone.utc)
    config_path = root / DEFAULT_GAME_REL
    matrix_path = root / MATRIX_REL
    errors: list[str] = []
    if not config_path.is_file():
        errors.append(f"missing {config_path}")
    if not matrix_path.is_file():
        errors.append(f"missing {matrix_path}")
    config_before = read_text_preserve_newlines(config_path) if config_path.is_file() else ""
    matrix_before = read_text_preserve_newlines(matrix_path) if matrix_path.is_file() else ""
    config_after, config_substitutions = build_proposed_config(config_before, errors)
    matrix_after, matrix_substitutions = build_proposed_matrix(matrix_before, errors)
    receipt_checks = [
        inspect_receipt(
            root, mission_id, spec["expected"], now, max_receipt_age_hours
        )
        for mission_id, spec in PROMOTIONS.items()
    ]
    for check in receipt_checks:
        errors.extend(f'{check["mission_id"]}: {error}' for error in check["errors"])
    all_proposed_maps = [
        match.group("map") for match in MAP_LINE_RE.finditer(config_after)
    ]
    missing_proposed_umaps = [
        str(package_to_umap(root, package))
        for package in all_proposed_maps
        if not package_to_umap(root, package).is_file()
    ]
    if missing_proposed_umaps:
        errors.append(
            "proposed ten-map source set is incomplete: "
            + ", ".join(missing_proposed_umaps)
        )
    report = {
        "schema": "skyguard.m08-m10-playable-promotion-plan.v1",
        "mode": "DRY_RUN",
        "gate": "PASS" if not errors else "FAIL_CLOSED",
        "generated_at_utc": now.isoformat(),
        "max_receipt_age_hours": max_receipt_age_hours,
        "receipt_checks": receipt_checks,
        "config": {
            "path": str(config_path),
            "sha256_before": sha256_file(config_path) if config_path.is_file() else None,
            "substitutions": config_substitutions,
            "unified_diff": unified_diff(str(config_path), config_before, config_after),
        },
        "soak_matrix": {
            "path": str(matrix_path),
            "sha256_before": sha256_file(matrix_path) if matrix_path.is_file() else None,
            "substitutions": matrix_substitutions,
            "unified_diff": unified_diff(str(matrix_path), matrix_before, matrix_after),
        },
        "proposed_map_order": all_proposed_maps,
        "missing_proposed_umaps": missing_proposed_umaps,
        "errors": errors,
        "mutation_performed": False,
    }
    return report, config_after, matrix_after


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def atomic_write(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def default_verifier_runner(
    root: Path,
    config: Path,
    matrix: Path,
    output: Path,
) -> dict:
    command = [
        sys.executable,
        str(root / COOK_VERIFIER_REL),
        "--project-root", str(root),
        "--default-game", str(config),
        "--mission-matrix", str(matrix),
        "--output", str(output),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0 or not output.is_file():
        raise RuntimeError(
            "Phase 8 cook-contract verifier failed: "
            + completed.stdout + completed.stderr
        )
    report = json.loads(output.read_text(encoding="utf-8"))
    if report.get("gate") != "PASS":
        raise RuntimeError("Phase 8 cook-contract report is not PASS")
    return report


def apply_promotion(
    root: Path,
    report: dict,
    config_after: str,
    matrix_after: str,
    *,
    verifier_runner: Callable[[Path, Path, Path, Path], dict] = default_verifier_runner,
    now: datetime | None = None,
) -> dict:
    if report.get("gate") != "PASS":
        raise RuntimeError("Refusing apply because dry-run gate is not PASS")
    now = now or datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%S%fZ")
    config_path = root / DEFAULT_GAME_REL
    matrix_path = root / MATRIX_REL
    backup_dir = root / "Saved/Backups/M08_M10_Playable_Promotion" / stamp
    backup_dir.mkdir(parents=True, exist_ok=False)
    config_backup = backup_dir / "DefaultGame.ini"
    matrix_backup = backup_dir / "PHASE8_MISSION_SOAK_MATRIX.json"
    shutil.copy2(config_path, config_backup)
    shutil.copy2(matrix_path, matrix_backup)
    manifest = {
        "schema": "skyguard.m08-m10-playable-promotion-backup.v1",
        "created_at_utc": now.isoformat(),
        "files": [
            {
                "source": str(config_path),
                "backup": str(config_backup),
                "sha256": sha256_file(config_backup),
            },
            {
                "source": str(matrix_path),
                "backup": str(matrix_backup),
                "sha256": sha256_file(matrix_backup),
            },
        ],
    }
    atomic_write(backup_dir / "manifest.json", json.dumps(manifest, indent=2) + "\n")
    verifier_output = (
        root / "Saved/Reports" / f"M08_M10_PLAYABLE_PROMOTION_COOK_CONTRACT_{stamp}.json"
    )
    try:
        atomic_write(config_path, config_after)
        atomic_write(matrix_path, matrix_after)
        cook_report = verifier_runner(
            root, config_path, matrix_path, verifier_output
        )
    except Exception:
        atomic_write_bytes(config_path, config_backup.read_bytes())
        atomic_write_bytes(matrix_path, matrix_backup.read_bytes())
        raise
    return {
        **report,
        "mode": "APPLY",
        "mutation_performed": True,
        "backup_directory": str(backup_dir),
        "cook_contract_report": cook_report,
        "sha256_after": {
            "default_game": sha256_file(config_path),
            "soak_matrix": sha256_file(matrix_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--max-receipt-age-hours", type=float, default=72.0)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.max_receipt_age_hours <= 0:
        parser.error("--max-receipt-age-hours must be positive")
    report, config_after, matrix_after = plan_promotion(
        args.project_root,
        max_receipt_age_hours=args.max_receipt_age_hours,
    )
    if args.apply:
        if report["gate"] != "PASS":
            print(json.dumps(report, indent=2))
            return 3
        report = apply_promotion(
            args.project_root, report, config_after, matrix_after
        )
    print(json.dumps(report, indent=2))
    return 0 if report["gate"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
