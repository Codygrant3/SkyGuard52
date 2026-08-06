"""Offline fail-closed validator for authentic Phase 5 audio acquisition."""

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCHEMA_PATH = (
    ROOT / "Docs/AAA_Review/PHASE5_AUTHENTIC_AUDIO_ACQUISITION_SCHEMA.json"
)
MANIFEST_PATH = (
    ROOT / "Docs/AAA_Review/PHASE5_AUTHENTIC_AUDIO_ACQUISITION_MANIFEST.json"
)
AUDIT_PATH = (
    ROOT / "Saved/Reports/PHASE5_AUTHENTIC_AUDIO_ACQUISITION_AUDIT.json"
)
EXPECTED = {
    "EngineIdle",
    "EngineCruise",
    "EnginePower",
    "Propeller",
    "OpenCockpitWind",
    "RifleShot",
    "IglaLaunch",
    "MissileFlight",
    "DronePropulsion",
    "DroneImpactExplosion",
}
EXPECTED_BINDINGS = {
    "EngineIdle": {"EngineIdle"},
    "EngineCruise": {"EngineCruise"},
    "EnginePower": {"EnginePower"},
    "Propeller": {"Propeller"},
    "OpenCockpitWind": {"OpenCockpitWind"},
    "RifleShot": {
        "RifleMuzzle",
        "RifleMechanical",
        "RifleCasing",
        "RifleReflection",
    },
    "IglaLaunch": {"IglaSearch", "IglaLock", "IglaLaunch"},
    "MissileFlight": {"IglaFlyby"},
    "DronePropulsion": {"DroneLightMotor", "DroneHeavyMotor", "DroneFlyby"},
    "DroneImpactExplosion": {
        "IglaImpact",
        "ExplosionSmallCrack",
        "ExplosionSmallBody",
        "ExplosionSmallDebris",
        "ExplosionSmallTail",
        "ExplosionHeavyCrack",
        "ExplosionHeavyBody",
        "ExplosionHeavyDebris",
        "ExplosionHeavyTail",
    },
}
ALLOWED_STATES = {
    "MISSING_LICENSE_AND_SOURCE",
    "LICENSE_REVIEW_PENDING",
    "SOURCE_ACQUIRED_QUARANTINED",
    "EVIDENCE_REVIEW_PENDING",
    "APPROVED_FOR_GOVERNED_IMPORT",
    "REJECTED",
}
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
ASSET_NAME = re.compile(r"^SW_[A-Za-z0-9_]+$")
IMPORTABLE = "APPROVED_FOR_GOVERNED_IMPORT"


def valid_sha(value):
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def require_nonempty(mapping, fields, errors, prefix):
    for field in fields:
        if mapping.get(field) in (None, "", [], {}):
            errors.append(prefix + " missing " + field)


def validate_importable(entry, errors):
    category = entry["category_id"]
    prefix = category + ":"
    vendor = entry.get("vendor", {})
    license_data = entry.get("license", {})
    source = entry.get("source", {})
    semantic = entry.get("semantic", {})
    derivative = entry.get("derivative", {})
    risk = entry.get("distribution_risk", {})
    unreal_import = entry.get("unreal_import", {})

    require_nonempty(
        vendor,
        ("legal_name", "product_id", "source_page_url"),
        errors,
        prefix + " vendor",
    )
    require_nonempty(
        license_data,
        (
            "license_name",
            "agreement_url",
            "agreement_version_or_date",
            "purchase_or_grant_evidence_path",
            "license_evidence_sha256",
            "licensed_identity",
            "seat_scope",
            "territory",
            "term",
            "rights_reviewer",
            "rights_approved_at_utc",
        ),
        errors,
        prefix + " license",
    )
    for field in (
        "commercial_game_use_allowed",
        "modification_allowed",
        "cooked_distribution_allowed",
        "promotional_sync_allowed",
    ):
        if license_data.get(field) is not True:
            errors.append(prefix + " license does not affirm " + field)
    if not valid_sha(license_data.get("license_evidence_sha256")):
        errors.append(prefix + " license evidence SHA-256 invalid")

    require_nonempty(
        source,
        (
            "original_filename",
            "original_sha256",
            "archive_path",
            "byte_size",
            "sample_rate_hz",
            "bit_depth",
            "channels",
            "duration_seconds",
            "acquired_at_utc",
        ),
        errors,
        prefix + " source",
    )
    if not valid_sha(source.get("original_sha256")):
        errors.append(prefix + " source SHA-256 invalid")
    for field in ("byte_size", "sample_rate_hz", "bit_depth", "channels", "duration_seconds"):
        if not isinstance(source.get(field), (int, float)) or source[field] <= 0:
            errors.append(prefix + " source " + field + " must be positive")
    if source.get("archive_path") and str(source["archive_path"]).startswith(
        "/Game/"
    ):
        errors.append(prefix + " raw source archive is inside Unreal content")

    require_nonempty(
        semantic,
        (
            "recorded_subject",
            "state_or_event",
            "listener_perspective",
            "recorder_metadata_evidence_path",
            "recorder_metadata_evidence_sha256",
            "metadata_verified_by",
            "metadata_verified_at_utc",
        ),
        errors,
        prefix + " semantic",
    )
    if semantic.get("metadata_verified") is not True:
        errors.append(prefix + " recorder metadata is not verified")
    if not valid_sha(semantic.get("recorder_metadata_evidence_sha256")):
        errors.append(prefix + " recorder metadata SHA-256 invalid")

    if category == "OpenCockpitWind":
        if semantic.get("open_canopy_claim") is not True:
            errors.append(prefix + " open-canopy claim not proven")
        canopy = semantic.get("canopy_open_fraction")
        if not isinstance(canopy, (int, float)) or not 0.0 < canopy <= 1.0:
            errors.append(prefix + " canopy opening fraction invalid")
        if not isinstance(semantic.get("documented_airspeed"), (int, float)):
            errors.append(prefix + " documented airspeed missing")
        if semantic.get("listener_perspective") != "RearCockpit":
            errors.append(prefix + " perspective is not RearCockpit")
        if semantic.get("recorded_subject") != "Yak-52":
            errors.append(prefix + " source is not verified Yak-52 airflow")

    require_nonempty(
        derivative,
        (
            "filename",
            "sha256",
            "edit_log_path",
            "edit_log_sha256",
            "sample_rate_hz",
            "bit_depth",
            "channels",
            "audio_qa_reviewer",
            "audio_qa_at_utc",
        ),
        errors,
        prefix + " derivative",
    )
    if not valid_sha(derivative.get("sha256")):
        errors.append(prefix + " derivative SHA-256 invalid")
    if not valid_sha(derivative.get("edit_log_sha256")):
        errors.append(prefix + " edit-log SHA-256 invalid")
    if not str(derivative.get("filename", "")).lower().endswith(".wav"):
        errors.append(prefix + " derivative must be a WAV file")
    if derivative.get("sample_rate_hz") != 48000:
        errors.append(prefix + " derivative sample rate must be 48000 Hz")
    if derivative.get("bit_depth") != 24:
        errors.append(prefix + " derivative bit depth must be 24")
    if derivative.get("channels") not in (1, 2):
        errors.append(prefix + " derivative channels must be mono or stereo")
    require_nonempty(
        derivative,
        (
            "integrated_lufs",
            "max_short_term_lufs",
            "true_peak_dbtp",
            "dc_offset_dbfs",
            "clipped_sample_count",
        ),
        errors,
        prefix + " derivative metering",
    )
    if isinstance(derivative.get("true_peak_dbtp"), (int, float)) and derivative[
        "true_peak_dbtp"
    ] > -3.0:
        errors.append(prefix + " derivative true peak exceeds -3 dBTP")
    if derivative.get("clipped_sample_count") not in (None, 0):
        errors.append(prefix + " derivative contains clipped samples")

    if risk.get("raw_files_excluded_from_build") is not True:
        errors.append(prefix + " raw-file build exclusion not proven")
    if risk.get("standalone_redistribution_allowed") is not False:
        errors.append(prefix + " raw standalone redistribution risk unresolved")
    if risk.get("cooked_asset_extraction_review") != "APPROVED":
        errors.append(prefix + " cooked extraction-risk review missing")
    require_nonempty(
        risk,
        ("reviewer", "reviewed_at_utc", "packaging_test_receipt_path"),
        errors,
        prefix + " distribution risk",
    )

    require_nonempty(
        unreal_import,
        (
            "destination",
            "asset_name",
            "output_submix",
            "attenuation_asset",
            "concurrency_asset",
        ),
        errors,
        prefix + " Unreal import",
    )
    if not str(unreal_import.get("destination", "")).startswith(
        "/Game/Skyguard/Audio/Production/"
    ):
        errors.append(prefix + " Unreal destination outside governed root")
    if not ASSET_NAME.fullmatch(str(unreal_import.get("asset_name", ""))):
        errors.append(prefix + " Unreal SoundWave name must use SW_ prefix")


def validate(schema, manifest):
    errors = []
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("schema is not draft 2020-12")
    if manifest.get("schema") != "skyguard.phase5.authentic-audio-acquisition.v1":
        errors.append("manifest schema mismatch")
    policy = manifest.get("policy", {})
    for field in (
        "raw_files_excluded_from_build",
        "import_requires_complete_evidence",
        "audition_does_not_equal_import_approval",
    ):
        if policy.get(field) is not True:
            errors.append("unsafe manifest policy: " + field)
    if policy.get("source_hash_algorithm") != "SHA-256":
        errors.append("source hash algorithm must be SHA-256")

    entries = manifest.get("entries", [])
    categories = [entry.get("category_id") for entry in entries]
    if len(entries) != 10 or set(categories) != EXPECTED:
        errors.append("manifest must contain exact ten governed source bundles")
    if len(categories) != len(set(categories)):
        errors.append("manifest categories are duplicated")
    for entry in entries:
        category = entry.get("category_id", "UNKNOWN")
        state = entry.get("acquisition_state")
        if state not in ALLOWED_STATES:
            errors.append(category + ": invalid acquisition state")
        bindings = entry.get("bank_bindings", [])
        if (
            category in EXPECTED_BINDINGS
            and (
                len(bindings) != len(set(bindings))
                or set(bindings) != EXPECTED_BINDINGS[category]
            )
        ):
            errors.append(category + ": bank bindings are not exact")
        if entry.get("acquisition_state") == IMPORTABLE:
            validate_importable(entry, errors)
        elif entry.get("acquisition_state") == "MISSING_LICENSE_AND_SOURCE":
            for section in ("vendor", "license", "source", "derivative", "distribution_risk"):
                if entry.get(section):
                    errors.append(category + ": empty-state " + section + " is not empty")
            if category == "OpenCockpitWind" and entry.get("semantic", {}).get(
                "open_canopy_claim"
            ) is not False:
                errors.append(category + ": unsupported open-canopy claim")

    importable_count = sum(
        entry.get("acquisition_state") == IMPORTABLE for entry in entries
    )
    if manifest.get("overall_state") == "READY_FOR_GOVERNED_IMPORT":
        if importable_count != len(entries):
            errors.append("overall ready state lacks ten importable source bundles")
    elif importable_count == len(entries) and entries:
        errors.append("all entries importable but overall state is not ready")
    return errors, importable_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-any-importable", action="store_true")
    parser.add_argument("--require-all-importable", action="store_true")
    args = parser.parse_args()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    errors, importable = validate(schema, manifest)
    result = {
        "schema": "skyguard.phase5.authentic-audio-acquisition-audit.v1",
        "entry_count": len(manifest.get("entries", [])),
        "missing_license_and_source_count": sum(
            entry.get("acquisition_state") == "MISSING_LICENSE_AND_SOURCE"
            for entry in manifest.get("entries", [])
        ),
        "importable_count": importable,
        "contract_valid": not errors,
        "production_ready": False,
        "errors": errors,
        "status": (
            "INVALID_ACQUISITION_MANIFEST"
            if errors
            else "VALID_EMPTY_MANIFEST_NOT_IMPORTABLE"
            if importable == 0
            else "PARTIAL_EVIDENCE_NOT_PRODUCTION_READY"
        ),
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if errors:
        return 2
    if args.require_any_importable and importable == 0:
        return 3
    if args.require_all_importable and importable != 10:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
