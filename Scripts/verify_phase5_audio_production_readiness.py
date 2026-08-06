"""Offline, fail-closed audit for the Phase 5 authentic-audio production lane.

This script never opens Unreal, imports media, downloads sources, or upgrades
an acquisition state. It checks that the planning, rights, naming, routing and
source-bank contracts agree before external audio acquisition begins.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOCS = ROOT / "Docs/AAA_Review"
REPORT = ROOT / "Saved/Reports/PHASE5_AUDIO_PRODUCTION_READINESS_AUDIT.json"
SESSION_SCHEMA = DOCS / "PHASE5_AUDIO_RECORDING_SESSION_SCHEMA.json"
SESSION_MANIFEST = DOCS / "PHASE5_AUDIO_RECORDING_SESSION_MANIFEST.json"
IMPORT_CONTRACT = (
    DOCS / "PHASE5_AUDIO_UNREAL_IMPORT_NAMING_LOUDNESS_CONTRACT.json"
)
BRIEFS = DOCS / "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
PROVENANCE = DOCS / "PHASE5_AUDIO_PRODUCTION_PROVENANCE_TEMPLATE.json"
AUTHENTIC_SCHEMA = DOCS / "PHASE5_AUTHENTIC_AUDIO_ACQUISITION_SCHEMA.json"
AUTHENTIC_MANIFEST = DOCS / "PHASE5_AUTHENTIC_AUDIO_ACQUISITION_MANIFEST.json"
AUTHENTIC_VERIFIER = ROOT / "Scripts/verify_phase5_authentic_audio_acquisition.py"
CPP_BANK = ROOT / "Source/Skyguard52/SkyguardAudioProductionBank.h"
LEGACY_SOURCE = ROOT / "Content/Skyguard/Audio/Source"
SOURCE_ROOT = ROOT / "Source/Skyguard52"

SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHOT_ID = re.compile(r"^P5-[A-Z0-9-]+$")
SW_NAME = re.compile(r"^SW_[A-Za-z0-9_]+$")
IDENTITY_BINDINGS = {
    "EngineIdle",
    "EngineCruise",
    "EnginePower",
    "Propeller",
    "OpenCockpitWind",
}
RIGHTS_KEYS = {
    "aircraft_operator_release",
    "location_release",
    "recordist_assignment",
    "performer_releases",
    "insurance_and_operational_approval",
}
EXPECTED_SHOTS = {
    "P5-IDLE-RC",
    "P5-IDLE-EXT",
    "P5-TAXI-RC",
    "P5-CRUISE-RC",
    "P5-CRUISE-EXT",
    "P5-POWER-RC",
    "P5-POWER-EXT",
    "P5-TRANSITION-RC",
    "P5-WIND-OPEN-LOW",
    "P5-WIND-OPEN-HIGH",
    "P5-ROOMTONE-RC",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def has_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_sha(value) -> bool:
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def find_current_metasound_topology_receipt() -> dict:
    candidates = list(
        (
            ROOT / "Saved/Reports/Phase5MetaSoundTopology"
        ).glob("attempt_*/fresh_topology_audit.json")
    )
    canonical = (
        ROOT / "Saved/Reports/PHASE5_METASOUND_TOPOLOGY_FRESH_AUDIT.json"
    )
    if canonical.exists():
        candidates.append(canonical)
    for path in sorted(
        candidates, key=lambda item: item.stat().st_mtime, reverse=True
    ):
        try:
            data = load_json(path)
        except (OSError, ValueError):
            continue
        accepted = bool(
            data.get("status")
            == "PASS_FRESH_GOVERNED_METASOUND_TOPOLOGY_SOURCES_MISSING"
            and data.get("graph_count") == 6
            and data.get("primitive_count") == 29
            and data.get("governed_asset_count") == 35
            and data.get("fresh_for_current_contract") is True
            and data.get("authentic_source_count") == 0
            and data.get("production_ready") is False
            and data.get("shipping_allowed") is False
            and data.get("production_bank", {}).get(
                "explicit_missing_source_count"
            )
            == 25
            and data.get("production_bank", {}).get(
                "bound_production_source_count"
            )
            == 0
            and not data.get("errors")
        )
        return {
            "present": True,
            "accepted": accepted,
            "path": str(path),
            "contract_bundle_sha256": data.get(
                "contract_bundle", {}
            ).get("bundle_sha256"),
        }
    return {
        "present": False,
        "accepted": False,
        "path": None,
        "contract_bundle_sha256": None,
    }


def validate_session(schema: dict, manifest: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("recording schema is not draft 2020-12")
    if manifest.get("schema") != "skyguard.phase5.audio-recording-session.v1":
        errors.append("recording manifest schema mismatch")
    if not str(manifest.get("session_id", "")).startswith("P5REC-"):
        errors.append("recording session id is not governed")

    safety = manifest.get("safety_policy", {})
    for key in (
        "flight_operations_controlled_by_qualified_operator",
        "recordist_does_not_direct_unsafe_maneuvers",
        "no_live_weapon_or_missile_capture",
        "hearing_and_equipment_restraint_plan_required",
        "abort_authority_documented",
    ):
        if safety.get(key) is not True:
            errors.append("unsafe recording policy: " + key)

    rights = manifest.get("rights_packet", {})
    if set(rights) != RIGHTS_KEYS:
        errors.append("recording rights packet is not exact")
    approved_rights = 0
    for key in sorted(RIGHTS_KEYS):
        evidence = rights.get(key, {})
        state = evidence.get("state")
        if state not in {"MISSING", "PENDING_REVIEW", "APPROVED"}:
            errors.append(key + ": invalid evidence state")
        if state == "APPROVED":
            approved_rights += 1
            for field in ("path", "reviewer", "reviewed_at_utc"):
                if not has_text(evidence.get(field)):
                    errors.append(key + ": approved evidence missing " + field)
            if not valid_sha(evidence.get("sha256")):
                errors.append(key + ": approved evidence hash invalid")
        elif state == "PENDING_REVIEW":
            if not has_text(evidence.get("path")) or not valid_sha(
                evidence.get("sha256")
            ):
                errors.append(key + ": pending evidence lacks path or hash")
            if evidence.get("reviewer") is not None or evidence.get(
                "reviewed_at_utc"
            ) is not None:
                errors.append(key + ": pending evidence carries approval data")
        elif any(
            evidence.get(field) is not None
            for field in ("path", "sha256", "reviewer", "reviewed_at_utc")
        ):
            errors.append(key + ": missing evidence carries review data")

    setup = manifest.get("technical_setup", {})
    if setup.get("target_sample_rate_hz") not in (48000, 96000, 192000):
        errors.append("recording sample rate is unsupported")
    if setup.get("target_bit_depth") != 24:
        errors.append("recording bit depth must be 24")
    for key in ("lossless_capture", "automatic_gain_control_disabled", "limiter_disabled"):
        if setup.get(key) is not True:
            errors.append("recording setup is unsafe: " + key)

    shots = manifest.get("shots", [])
    ids = [shot.get("shot_id") for shot in shots]
    if set(ids) != EXPECTED_SHOTS or len(ids) != len(set(ids)):
        errors.append("recording shot list is not exact and unique")
    covered_bindings: set[str] = set()
    captured_file_count = 0
    for shot in shots:
        shot_id = str(shot.get("shot_id", "UNKNOWN"))
        if not SHOT_ID.fullmatch(shot_id):
            errors.append(shot_id + ": invalid shot id")
        if shot.get("subject") != "Yak-52":
            errors.append(shot_id + ": subject is not Yak-52")
        bindings = shot.get("bank_bindings", [])
        if not bindings or not set(bindings).issubset(IDENTITY_BINDINGS):
            errors.append(shot_id + ": invalid identity-bank bindings")
        covered_bindings.update(bindings)
        if len(shot.get("required_metadata", [])) < 4:
            errors.append(shot_id + ": metadata plan is incomplete")
        if shot.get("canopy_state") == "RearOpen":
            metadata = set(shot.get("required_metadata", []))
            if not {"airspeed", "canopy_open_fraction", "restraint_configuration"}.issubset(
                metadata
            ):
                errors.append(shot_id + ": open-canopy proof fields missing")
        capture_state = shot.get("capture_state")
        files = shot.get("captured_files", [])
        if capture_state == "PLANNED" and files:
            errors.append(shot_id + ": planned shot already claims captured files")
        if capture_state in {"CAPTURED_QUARANTINED", "METADATA_VERIFIED"}:
            if len(files) < int(shot.get("minimum_takes", 0)):
                errors.append(shot_id + ": captured take count is below plan")
        for source in files:
            captured_file_count += 1
            if not has_text(source.get("filename")):
                errors.append(shot_id + ": captured filename missing")
            if not valid_sha(source.get("sha256")):
                errors.append(shot_id + ": captured source hash invalid")
            if not isinstance(source.get("byte_size"), int) or source["byte_size"] < 1:
                errors.append(shot_id + ": captured byte size invalid")
            if source.get("sample_rate_hz") not in (48000, 96000, 192000):
                errors.append(shot_id + ": captured sample rate unsupported")
            if source.get("bit_depth") != 24:
                errors.append(shot_id + ": captured bit depth is not 24")
            if not isinstance(source.get("channels"), int) or not (
                1 <= source["channels"] <= 8
            ):
                errors.append(shot_id + ": captured channel count invalid")
            if not has_text(source.get("take_notes")):
                errors.append(shot_id + ": captured take notes missing")
    if covered_bindings != IDENTITY_BINDINGS:
        errors.append("recording shots do not cover all five identity bindings")

    state = manifest.get("session_state")
    if state not in {
        "PLANNING",
        "SCHEDULED_BLOCKED_EVIDENCE",
        "CLEARED_TO_RECORD",
        "CAPTURE_COMPLETE_QUARANTINED",
        "CANCELLED",
    }:
        errors.append("recording session state invalid")
    if state == "PLANNING":
        if captured_file_count:
            errors.append("planning session cannot carry captured files")
    if state in {"CLEARED_TO_RECORD", "CAPTURE_COMPLETE_QUARANTINED"}:
        if approved_rights != len(RIGHTS_KEYS):
            errors.append("recording session claims clearance without all rights")
        for field in ("aircraft_identity", "session_utc", "location"):
            if not manifest.get(field):
                errors.append("cleared recording session missing " + field)
        for field in ("timecode_or_slate_plan", "microphone_plan", "recorder_plan"):
            if not setup.get(field):
                errors.append("cleared recording session missing setup " + field)
    if state == "CAPTURE_COMPLETE_QUARANTINED":
        incomplete = [
            shot.get("shot_id")
            for shot in shots
            if shot.get("capture_state") not in {
                "CAPTURED_QUARANTINED",
                "METADATA_VERIFIED",
            }
        ]
        if incomplete:
            errors.append("capture-complete session has incomplete shots")

    return errors, {
        "session_state": state,
        "approved_rights_count": approved_rights,
        "required_rights_count": len(RIGHTS_KEYS),
        "shot_count": len(shots),
        "captured_file_count": captured_file_count,
        "identity_bindings_covered": sorted(covered_bindings),
    }


def parse_cpp_categories(source: str) -> set[str]:
    match = re.search(
        r"enum class ESkyguardProductionAudioCategory\s*:\s*uint8\s*\{(?P<body>.*?)\};",
        source,
        re.DOTALL,
    )
    if not match:
        return set()
    return {
        token.strip().split("=")[0].strip()
        for token in match.group("body").split(",")
        if token.strip()
    }


def validate_import_contract(
    contract: dict, briefs: dict, provenance: dict, cpp_source: str
) -> tuple[list[str], dict]:
    errors: list[str] = []
    required = contract.get("required_bank_categories", [])
    required_set = set(required)
    if len(required) != 25 or len(required_set) != 25:
        errors.append("import contract must declare 25 unique bank categories")
    if contract.get("governed_root") != "/Game/Skyguard/Audio/Production/":
        errors.append("import contract governed root mismatch")
    delivery = contract.get("source_delivery", {})
    if (
        delivery.get("container") != "WAV"
        or delivery.get("codec") != "PCM_INTEGER"
        or delivery.get("sample_rate_hz") != 48000
        or delivery.get("bit_depth") != 24
        or delivery.get("lossy_source_forbidden") is not True
        or delivery.get("immutable_original_import_forbidden") is not True
    ):
        errors.append("import delivery is not governed 48 kHz/24-bit PCM WAV")
    prefixes = contract.get("asset_prefixes", {})
    expected_prefixes = {
        "SoundWave": "SW_",
        "MetaSoundSource": "MS_",
        "SoundCue": "SC_",
        "SoundAttenuation": "ATT_",
        "SoundConcurrency": "CON_",
        "SoundSubmix": "SMX_",
        "SoundMix": "MIX_",
    }
    if prefixes != expected_prefixes:
        errors.append("Unreal audio prefixes are incomplete or inconsistent")
    qa = contract.get("derivative_qa", {})
    if qa.get("max_true_peak_dbtp") != -3.0 or qa.get("clipped_sample_count") != 0:
        errors.append("offline derivative peak/clipping contract mismatch")
    runtime = contract.get("runtime_mix_acceptance", {})
    if (
        runtime.get("master_true_peak_ceiling_dbtp") != -1.0
        or int(runtime.get("minimum_measured_samples", 0)) < 600
        or int(runtime.get("minimum_combat_soak_seconds", 0)) < 180
    ):
        errors.append("runtime audible acceptance contract is too weak")

    profiles = contract.get("profiles", {})
    category_profiles = contract.get("category_profiles", {})
    if set(category_profiles) != required_set:
        errors.append("category-profile mapping is not exact")
    for category, profile_name in category_profiles.items():
        profile = profiles.get(profile_name)
        if not profile:
            errors.append(category + ": missing category profile")
            continue
        if int(profile.get("minimum_variants", 0)) < 1:
            errors.append(category + ": invalid minimum variation count")
        if profile.get("concurrency_required") is not True:
            errors.append(category + ": concurrency is not required")

    brief_entries = briefs.get("categories", [])
    brief_categories = [entry.get("category") for entry in brief_entries]
    if len(brief_categories) != 25 or set(brief_categories) != required_set:
        errors.append("category briefs disagree with import contract")
    destinations: list[str] = []
    for entry in brief_entries:
        category = str(entry.get("category", "UNKNOWN"))
        destination = str(entry.get("unreal_destination", ""))
        destinations.append(destination)
        basename = destination.rsplit("/", 1)[-1]
        if not destination.startswith(contract.get("governed_root", "")):
            errors.append(category + ": destination outside governed root")
        if not SW_NAME.fullmatch(basename):
            errors.append(category + ": SoundWave destination lacks SW_ naming")
        try:
            destination.encode("ascii")
        except UnicodeEncodeError:
            errors.append(category + ": destination is not ASCII")
        if " " in destination:
            errors.append(category + ": destination contains spaces")
    if len(destinations) != len(set(destinations)):
        errors.append("category briefs contain duplicate Unreal destinations")

    provenance_categories = [
        entry.get("category") for entry in provenance.get("entries", [])
    ]
    if len(provenance_categories) != 25 or set(provenance_categories) != required_set:
        errors.append("provenance template disagrees with import contract")
    cpp_categories = parse_cpp_categories(cpp_source)
    if cpp_categories != required_set:
        errors.append("C++ production bank enum disagrees with import contract")

    routing = contract.get("routing_assets", {})
    expected_routing_names = {
        "MasterSubmix": "SMX_",
        "CockpitSubmix": "SMX_",
        "ExteriorSubmix": "SMX_",
        "WeaponsSubmix": "SMX_",
        "ExplosionsSubmix": "SMX_",
        "RadioSubmix": "SMX_",
        "CockpitSoundMix": "MIX_",
    }
    if set(routing) != set(expected_routing_names):
        errors.append("routing asset contract is not exact")
    for key, prefix in expected_routing_names.items():
        if not str(routing.get(key, "")).rsplit("/", 1)[-1].startswith(prefix):
            errors.append(key + ": routing asset prefix mismatch")

    provenance_routing_key_map = {
        "MasterSubmix": "master_submix",
        "CockpitSubmix": "cockpit_submix",
        "ExteriorSubmix": "exterior_submix",
        "WeaponsSubmix": "weapons_submix",
        "ExplosionsSubmix": "explosions_submix",
        "RadioSubmix": "radio_submix",
        "CockpitSoundMix": "cockpit_sound_mix",
    }
    provenance_routing = provenance.get("routing_assets", {})
    local_routing_present = 0
    for contract_key, provenance_key in provenance_routing_key_map.items():
        contract_path = routing.get(contract_key)
        if provenance_routing.get(provenance_key) != contract_path:
            errors.append(contract_key + ": provenance routing path disagrees")
            continue
        local_file = ROOT / "Content" / (
            str(contract_path).removeprefix("/Game/") + ".uasset"
        )
        if local_file.is_file() and local_file.stat().st_size > 0:
            local_routing_present += 1
        else:
            errors.append(contract_key + ": declared local routing binary missing")
    bank_path = str(provenance.get("bank_asset", ""))
    bank_file = ROOT / "Content" / (
        bank_path.removeprefix("/Game/") + ".uasset"
    )
    bank_local_present = bank_file.is_file() and bank_file.stat().st_size > 0
    if not bank_local_present:
        errors.append("declared local production-bank binary missing")
    if provenance.get("routing_validation_state") != (
        "LOCAL_BINARIES_PRESENT_FRESH_UNREAL_AUDIT_MISSING"
    ):
        errors.append("routing validation state is not honest")
    if provenance.get("bank_asset_validation_state") != (
        "LOCAL_BINARY_PRESENT_FRESH_UNREAL_AUDIT_MISSING"
    ):
        errors.append("bank validation state is not honest")

    topology_receipt = find_current_metasound_topology_receipt()
    return errors, {
        "bank_category_count": len(required),
        "brief_category_count": len(brief_entries),
        "provenance_category_count": len(provenance_categories),
        "cpp_category_count": len(cpp_categories),
        "routing_asset_count": len(routing),
        "local_routing_binary_count": local_routing_present,
        "local_bank_binary_present": bank_local_present,
        "fresh_unreal_routing_audit_present": topology_receipt["accepted"],
        "fresh_unreal_routing_audit": topology_receipt,
    }


def load_authentic_verifier():
    spec = importlib.util.spec_from_file_location(
        "phase5_authentic_verifier", AUTHENTIC_VERIFIER
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def validate_all(
    session_schema: dict,
    session_manifest: dict,
    import_contract: dict,
    briefs: dict,
    provenance: dict,
    authentic_schema: dict,
    authentic_manifest: dict,
    cpp_source: str,
) -> tuple[list[str], dict]:
    errors: list[str] = []
    session_errors, session_summary = validate_session(
        session_schema, session_manifest
    )
    import_errors, import_summary = validate_import_contract(
        import_contract, briefs, provenance, cpp_source
    )
    authentic = load_authentic_verifier()
    acquisition_errors, importable_count = authentic.validate(
        authentic_schema, authentic_manifest
    )
    errors.extend("session:" + error for error in session_errors)
    errors.extend("import:" + error for error in import_errors)
    errors.extend("acquisition:" + error for error in acquisition_errors)

    governed = set(import_contract.get("required_bank_categories", []))
    flattened_bindings = [
        binding
        for entry in authentic_manifest.get("entries", [])
        for binding in entry.get("bank_bindings", [])
    ]
    if len(flattened_bindings) != len(set(flattened_bindings)):
        errors.append("acquisition:bank bindings are duplicated across source bundles")
    if set(flattened_bindings) != governed:
        errors.append("acquisition:source bundles do not cover all 25 bank categories")

    legacy_files = (
        sorted(path.name for path in LEGACY_SOURCE.glob("*") if path.is_file())
        if LEGACY_SOURCE.exists()
        else []
    )
    legacy_runtime_references: list[str] = []
    imported_reference = re.compile(r"/Game/Skyguard/Audio/Imported/[^\"\s)]+")
    for source_file in sorted(SOURCE_ROOT.glob("*.cpp")):
        source_text = source_file.read_text(encoding="utf-8")
        for line_number, line in enumerate(source_text.splitlines(), start=1):
            for reference in imported_reference.findall(line):
                legacy_runtime_references.append(
                    f"{source_file.name}:{line_number}:{reference}"
                )
    source_state_counts: dict[str, int] = {}
    for entry in authentic_manifest.get("entries", []):
        state = str(entry.get("acquisition_state"))
        source_state_counts[state] = source_state_counts.get(state, 0) + 1
    production_ready = (
        not errors
        and importable_count == len(authentic_manifest.get("entries", []))
        and session_manifest.get("session_state") == "CAPTURE_COMPLETE_QUARANTINED"
        and not legacy_runtime_references
        and import_summary["fresh_unreal_routing_audit_present"]
    )
    external_blockers = [
        "Five approved and hashed Yak-52 recording-session rights and operations records",
        "Exact aircraft, operator, location, schedule, restraint, microphone and recorder plans",
        "Eleven completed and metadata-verified Yak-52 identity recording shots",
        "Licensed matching rifle muzzle, mechanics, casing and airborne reflection variations",
        "Licensed system-appropriate Igla search, lock, launch, fly-by and impact layers",
        "Licensed light/heavy piston-UAV motor loops and fly-bys",
        "Licensed small/heavy crack, body, debris and environment-tail explosion layers",
        "Released Ukrainian and English mission-radio performances",
        "Immutable originals, rights evidence, source and derivative hashes, edit logs and metering",
        "Packaged audible combat-soak and calibrated mix acceptance",
    ]
    if not import_summary["fresh_unreal_routing_audit_present"]:
        external_blockers.append(
            "Fresh serialized Unreal routing/import persistence audit"
        )
    if legacy_runtime_references:
        external_blockers.append(
            "Replacement or explicit non-shipping quarantine of legacy Imported audio runtime references"
        )
    summary = {
        "session": session_summary,
        "import_contract": import_summary,
        "authentic_source_bundle_count": len(
            authentic_manifest.get("entries", [])
        ),
        "authentic_source_state_counts": source_state_counts,
        "approved_for_governed_import_count": importable_count,
        "legacy_nonproduction_source_files": legacy_files,
        "legacy_nonproduction_source_file_count": len(legacy_files),
        "legacy_imported_runtime_references": legacy_runtime_references,
        "legacy_imported_runtime_reference_count": len(legacy_runtime_references),
        "external_blockers": external_blockers,
        "production_ready": production_ready,
    }
    return errors, summary


def main() -> int:
    inputs = {
        "session_schema": load_json(SESSION_SCHEMA),
        "session_manifest": load_json(SESSION_MANIFEST),
        "import_contract": load_json(IMPORT_CONTRACT),
        "briefs": load_json(BRIEFS),
        "provenance": load_json(PROVENANCE),
        "authentic_schema": load_json(AUTHENTIC_SCHEMA),
        "authentic_manifest": load_json(AUTHENTIC_MANIFEST),
        "cpp_source": CPP_BANK.read_text(encoding="utf-8"),
    }
    errors, summary = validate_all(**inputs)
    structural_valid = not errors
    status = (
        "PRODUCTION_READY"
        if summary["production_ready"]
        else "CONTRACT_VALID_EXTERNAL_ACQUISITION_REQUIRED"
        if structural_valid
        else "CONTRACT_INVALID"
    )
    report = {
        "schema": "skyguard.phase5.audio-production-readiness-audit.v1",
        "status": status,
        "structural_valid": structural_valid,
        "production_ready": summary["production_ready"],
        "summary": summary,
        "errors": errors,
        "execution": "OFFLINE_CONTRACT_VALIDATION_ONLY",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if structural_valid else 2


if __name__ == "__main__":
    sys.exit(main())
