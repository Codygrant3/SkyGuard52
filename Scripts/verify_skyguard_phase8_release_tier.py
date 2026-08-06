"""Offline Phase 8 release-tier preflight with authentic-audio enforcement."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/PHASE8_RELEASE_TIER_CONTRACT.json"
AUDIO_GATE_PATH = ROOT / "Scripts/verify_phase5_audio_shipping_boundary.py"
DEFAULT_OUTPUT = ROOT / "Saved/Reports/PHASE8_RELEASE_TIER_PREFLIGHT_LATEST.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_audio_gate():
    spec = importlib.util.spec_from_file_location("phase5_shipping", AUDIO_GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def validate_contract(contract: dict) -> list[str]:
    errors: list[str] = []
    if contract.get("schema") != "skyguard.phase8.release-tier-contract.v1":
        errors.append("release-tier contract schema mismatch")
    tiers = contract.get("tiers", {})
    if set(tiers) != {"Engineering", "AAA", "FriendFacing"}:
        errors.append("release-tier set is not exact")
    if contract.get("default_tier") != "Engineering":
        errors.append("backward-compatible default tier must be Engineering")
    for name, tier in tiers.items():
        if name == "Engineering":
            if tier.get("production_audio_required") is not False:
                errors.append("Engineering production-audio requirement drifted")
            if tier.get("blocked_audio_exception_allowed") is not True:
                errors.append("Engineering exception is not explicitly allowed")
            if tier.get("friend_distribution_allowed") is not False:
                errors.append("Engineering cannot be friend-facing")
            if tier.get("shipping_promotion_allowed") is not False:
                errors.append("Engineering cannot claim Shipping promotion")
        else:
            if tier.get("production_audio_required") is not True:
                errors.append(name + " must require production audio")
            if tier.get("blocked_audio_exception_allowed") is not False:
                errors.append(name + " cannot allow an audio exception")
            if tier.get("accepted_audio_states") != [
                "PASS_SHIPPING_AUDIO_BOUNDARY"
            ]:
                errors.append(name + " accepted audio state is unsafe")
    policy = contract.get("prepackage_policy", {})
    for key in (
        "tier_preflight_required_before_uat",
        "tier_preflight_required_before_build_cook_stage_package_archive",
        "audio_shipping_boundary_must_be_fresh",
        "audio_exception_never_upgrades_audio_state",
        "historical_missing_tier_receipts_are_engineering_only",
    ):
        if policy.get(key) is not True:
            errors.append("unsafe prepackage policy: " + key)
    return errors


def evaluate_tier(
    contract: dict,
    release_tier: str,
    allow_engineering_audio_exception: bool,
    audio_result: dict,
) -> dict:
    errors = validate_contract(contract)
    tiers = contract.get("tiers", {})
    tier = tiers.get(release_tier)
    if not tier:
        errors.append("unknown release tier: " + release_tier)
        tier = {}

    audio_shipping_allowed = audio_result.get("shipping_allowed") is True
    audio_blockers = list(audio_result.get("blockers", []))
    exception_applied = bool(
        release_tier == "Engineering"
        and not audio_shipping_allowed
        and allow_engineering_audio_exception
        and tier.get("blocked_audio_exception_allowed") is True
    )
    exception_forbidden = bool(
        release_tier != "Engineering" and allow_engineering_audio_exception
    )
    if exception_forbidden:
        errors.append(release_tier + " cannot request Engineering audio exception")

    if audio_shipping_allowed:
        effective_audio_state = "PASS_SHIPPING_AUDIO_BOUNDARY"
    elif exception_applied:
        effective_audio_state = (
            "BLOCK_SHIPPING_UNVERIFIED_AUDIO_WITH_ENGINEERING_EXCEPTION"
        )
    else:
        effective_audio_state = "BLOCK_SHIPPING_UNVERIFIED_AUDIO"

    accepted_states = tier.get("accepted_audio_states", [])
    packaging_allowed = (
        not errors and effective_audio_state in accepted_states
    )
    external_distribution_allowed = bool(
        packaging_allowed
        and audio_shipping_allowed
        and tier.get("friend_distribution_allowed") is True
    )
    shipping_promotion_allowed = bool(
        packaging_allowed
        and audio_shipping_allowed
        and tier.get("shipping_promotion_allowed") is True
    )
    return {
        "contract_errors": errors,
        "release_tier": release_tier,
        "audio_shipping_allowed": audio_shipping_allowed,
        "audio_blockers": audio_blockers,
        "engineering_audio_exception_requested": (
            allow_engineering_audio_exception
        ),
        "engineering_audio_exception_applied": exception_applied,
        "effective_audio_state": effective_audio_state,
        "packaging_allowed": packaging_allowed,
        "external_distribution_allowed": external_distribution_allowed,
        "shipping_promotion_allowed": shipping_promotion_allowed,
    }


def current_audio_evidence() -> tuple[dict, dict]:
    audio = load_audio_gate()
    policy = audio.load_json(audio.POLICY_PATH)
    readiness = audio.load_json(audio.READINESS_PATH)
    acquisition = audio.load_json(audio.ACQUISITION_PATH)
    result = audio.evaluate(
        policy,
        readiness,
        acquisition,
        audio.collect_scan_files(policy.get("runtime_scan_globs", [])),
        audio.collect_scan_files(policy.get("config_scan_globs", [])),
        audio.collect_directory_files(
            policy.get("forbidden_content_directories", [])
        ),
        audio.collect_directory_files(
            policy.get("forbidden_loose_media_directories", [])
        ),
    )
    return result, {
        "shipping_policy": str(audio.POLICY_PATH),
        "readiness": str(audio.READINESS_PATH),
        "acquisition": str(audio.ACQUISITION_PATH),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-tier",
        choices=("Engineering", "AAA", "FriendFacing"),
        default="Engineering",
    )
    parser.add_argument(
        "--allow-engineering-audio-exception",
        action="store_true",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    contract = load_json(CONTRACT_PATH)
    audio_result, audio_inputs = current_audio_evidence()
    result = evaluate_tier(
        contract,
        args.release_tier,
        args.allow_engineering_audio_exception,
        audio_result,
    )
    status = (
        "INVALID_RELEASE_TIER_CONTRACT"
        if result["contract_errors"]
        else "PASS_ENGINEERING_WITH_AUDIO_EXCEPTION"
        if result["engineering_audio_exception_applied"]
        else "PASS_RELEASE_TIER_PREFLIGHT"
        if result["packaging_allowed"]
        else "BLOCK_RELEASE_TIER_BEFORE_PACKAGING"
    )
    report = {
        "schema": "skyguard.phase8.release-tier-preflight.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "contract": str(CONTRACT_PATH),
        "audio_inputs": audio_inputs,
        "result": result,
        "execution": "OFFLINE_PREFLIGHT_NO_ENGINE_OR_PACKAGING",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if result["contract_errors"]:
        return 2
    return 0 if result["packaging_allowed"] else 3


if __name__ == "__main__":
    sys.exit(main())
