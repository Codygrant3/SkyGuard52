"""Fail-closed Shipping boundary for Phase 5 production audio.

Default invocation is a release gate and exits nonzero while any unverified
legacy audio or incomplete production evidence remains. ``--audit-only`` emits
the same evidence but returns success when the policy itself is structurally
valid, allowing routine development audits to remain green-but-blocked.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOCS = ROOT / "Docs/AAA_Review"
POLICY_PATH = DOCS / "PHASE5_AUDIO_SHIPPING_BOUNDARY_POLICY.json"
READINESS_PATH = ROOT / "Saved/Reports/PHASE5_AUDIO_PRODUCTION_READINESS_AUDIT.json"
ACQUISITION_PATH = DOCS / "PHASE5_AUTHENTIC_AUDIO_ACQUISITION_MANIFEST.json"
REPORT_PATH = ROOT / "Saved/Reports/PHASE5_AUDIO_SHIPPING_BOUNDARY_AUDIT.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def collect_scan_files(globs: list[str]) -> dict[str, str]:
    files: dict[str, str] = {}
    for pattern in globs:
        for path in sorted(ROOT.glob(pattern)):
            if path.is_file():
                files[normalize_relative(path)] = path.read_text(
                    encoding="utf-8", errors="replace"
                )
    return files


def collect_directory_files(directories: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for relative in directories:
        path = ROOT / relative
        result[relative] = (
            sorted(
                normalize_relative(candidate)
                for candidate in path.rglob("*")
                if candidate.is_file()
            )
            if path.exists()
            else []
        )
    return result


def find_references(
    texts: dict[str, str], forbidden_roots: list[str]
) -> list[dict]:
    findings: list[dict] = []
    for relative_path, text in sorted(texts.items()):
        for line_number, line in enumerate(text.splitlines(), start=1):
            for root in forbidden_roots:
                if root in line:
                    findings.append(
                        {
                            "path": relative_path,
                            "line": line_number,
                            "forbidden_root": root,
                            "excerpt": line.strip()[:300],
                        }
                    )
    return findings


def validate_policy(policy: dict) -> list[str]:
    errors: list[str] = []
    if policy.get("schema") != (
        "skyguard.phase5.audio-shipping-boundary-policy.v1"
    ):
        errors.append("policy schema mismatch")
    if policy.get("shipping_audio_root") != (
        "/Game/Skyguard/Audio/Production/"
    ):
        errors.append("Shipping audio root must be governed Production")
    for key in (
        "forbidden_runtime_object_roots",
        "forbidden_cook_roots",
        "forbidden_content_directories",
        "forbidden_loose_media_directories",
        "forbidden_loose_media_extensions",
        "runtime_scan_globs",
        "config_scan_globs",
    ):
        value = policy.get(key)
        if not isinstance(value, list) or not value:
            errors.append(key + " must be a nonempty list")
    if policy.get("required_acquisition_state") != (
        "APPROVED_FOR_GOVERNED_IMPORT"
    ):
        errors.append("required acquisition state is unsafe")
    if policy.get("required_source_bundle_count") != 10:
        errors.append("required source bundle count must be 10")
    if policy.get("required_bank_category_count") != 25:
        errors.append("required bank category count must be 25")
    for key in (
        "require_readiness_production_ready",
        "require_fresh_unreal_routing_audit",
        "require_packaged_audible_acceptance",
    ):
        if policy.get(key) is not True:
            errors.append(key + " must remain true")
    if policy.get("shipping_gate_exit_code_when_blocked") in (None, 0):
        errors.append("blocked Shipping exit code must be nonzero")
    return errors


def evaluate(
    policy: dict,
    readiness: dict,
    acquisition: dict,
    runtime_texts: dict[str, str],
    config_texts: dict[str, str],
    forbidden_content_files: dict[str, list[str]],
    loose_media_files: dict[str, list[str]],
) -> dict:
    policy_errors = validate_policy(policy)
    runtime_references = find_references(
        runtime_texts, policy.get("forbidden_runtime_object_roots", [])
    )
    forbidden_cook_references = find_references(
        config_texts, policy.get("forbidden_cook_roots", [])
    )

    forbidden_extensions = {
        str(item).lower()
        for item in policy.get("forbidden_loose_media_extensions", [])
    }
    loose_media = sorted(
        path
        for files in loose_media_files.values()
        for path in files
        if Path(path).suffix.lower() in forbidden_extensions
    )
    forbidden_assets = sorted(
        path
        for files in forbidden_content_files.values()
        for path in files
    )

    entries = acquisition.get("entries", [])
    required_state = policy.get("required_acquisition_state")
    unapproved_bundles = [
        str(entry.get("category_id", "UNKNOWN"))
        for entry in entries
        if entry.get("acquisition_state") != required_state
    ]
    flattened_bindings = [
        binding
        for entry in entries
        for binding in entry.get("bank_bindings", [])
    ]
    source_bundle_contract_complete = (
        len(entries) == policy.get("required_source_bundle_count")
        and len(flattened_bindings) == policy.get("required_bank_category_count")
        and len(flattened_bindings) == len(set(flattened_bindings))
    )

    readiness_summary = readiness.get("summary", {})
    import_summary = readiness_summary.get("import_contract", {})
    production_ready = readiness.get("production_ready") is True
    fresh_routing = import_summary.get("fresh_unreal_routing_audit_present") is True
    packaged_audible = (
        readiness_summary.get("packaged_audible_acceptance_passed") is True
    )

    blockers: list[str] = []
    if runtime_references:
        blockers.append("FORBIDDEN_LEGACY_RUNTIME_REFERENCES")
    if forbidden_cook_references:
        blockers.append("FORBIDDEN_LEGACY_ALWAYS_COOK_DIRECTIVE")
    if forbidden_assets:
        blockers.append("FORBIDDEN_LEGACY_IMPORTED_ASSETS_PRESENT")
    if loose_media:
        blockers.append("FORBIDDEN_LOOSE_SOURCE_MEDIA_IN_CONTENT")
    if not source_bundle_contract_complete:
        blockers.append("SOURCE_BUNDLE_OR_BANK_BINDING_CONTRACT_INCOMPLETE")
    if unapproved_bundles:
        blockers.append("AUTHENTIC_SOURCE_BUNDLES_NOT_APPROVED")
    if not production_ready:
        blockers.append("PRODUCTION_READINESS_NOT_ACCEPTED")
    if not fresh_routing:
        blockers.append("FRESH_UNREAL_ROUTING_AUDIT_MISSING")
    if not packaged_audible:
        blockers.append("PACKAGED_AUDIBLE_ACCEPTANCE_MISSING")

    shipping_allowed = not policy_errors and not blockers
    return {
        "policy_errors": policy_errors,
        "runtime_references": runtime_references,
        "forbidden_cook_references": forbidden_cook_references,
        "forbidden_imported_assets": forbidden_assets,
        "forbidden_loose_media": loose_media,
        "source_bundle_count": len(entries),
        "bank_binding_count": len(flattened_bindings),
        "source_bundle_contract_complete": source_bundle_contract_complete,
        "unapproved_source_bundles": unapproved_bundles,
        "production_readiness_accepted": production_ready,
        "fresh_unreal_routing_audit_present": fresh_routing,
        "packaged_audible_acceptance_passed": packaged_audible,
        "blockers": blockers,
        "shipping_allowed": shipping_allowed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="Return success for a valid policy even when Shipping is blocked.",
    )
    args = parser.parse_args()

    policy = load_json(POLICY_PATH)
    readiness = load_json(READINESS_PATH)
    acquisition = load_json(ACQUISITION_PATH)
    runtime_texts = collect_scan_files(policy.get("runtime_scan_globs", []))
    config_texts = collect_scan_files(policy.get("config_scan_globs", []))
    forbidden_content = collect_directory_files(
        policy.get("forbidden_content_directories", [])
    )
    loose_media = collect_directory_files(
        policy.get("forbidden_loose_media_directories", [])
    )
    result = evaluate(
        policy,
        readiness,
        acquisition,
        runtime_texts,
        config_texts,
        forbidden_content,
        loose_media,
    )
    status = (
        "INVALID_SHIPPING_POLICY"
        if result["policy_errors"]
        else "PASS_SHIPPING_AUDIO_BOUNDARY"
        if result["shipping_allowed"]
        else "BLOCK_SHIPPING_UNVERIFIED_AUDIO"
    )
    report = {
        "schema": "skyguard.phase5.audio-shipping-boundary-audit.v1",
        "status": status,
        "shipping_allowed": result["shipping_allowed"],
        "audit_only": args.audit_only,
        "policy_path": str(POLICY_PATH),
        "readiness_path": str(READINESS_PATH),
        "acquisition_path": str(ACQUISITION_PATH),
        "result": result,
        "execution": "OFFLINE_READ_ONLY_SCAN_NO_MEDIA_PROMOTION",
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if result["policy_errors"]:
        return int(policy.get("invalid_policy_exit_code", 2))
    if result["shipping_allowed"] or args.audit_only:
        return 0
    return int(policy.get("shipping_gate_exit_code_when_blocked", 3))


if __name__ == "__main__":
    sys.exit(main())
