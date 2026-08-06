"""Offline validator for the P5-A source-independent routing scaffold."""

import argparse
import ast
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DEFAULT_CONTRACT = (
    ROOT / "Docs/AAA_Review/PHASE5_P5A_IDENTITY_BED_ROUTING_CONTRACT.json"
)
DEFAULT_BUILDER = ROOT / "Scripts/build_skyguard_phase5_p5a_audio_routing.py"
DEFAULT_BUILD_RECEIPT = ROOT / "Saved/Reports/PHASE5_P5A_ROUTING_BUILD.json"
DEFAULT_AUDIT = ROOT / "Saved/Reports/PHASE5_P5A_ROUTING_CONTRACT_AUDIT.json"

EXPECTED_ROUTING = {
    "MasterSubmix": "SoundSubmix",
    "CockpitSubmix": "SoundSubmix",
    "ExteriorSubmix": "SoundSubmix",
    "WeaponsSubmix": "SoundSubmix",
    "ExplosionsSubmix": "SoundSubmix",
    "RadioSubmix": "SoundSubmix",
    "CockpitSoundMix": "SoundMix",
}
EXPECTED_IDENTITY = {
    "EngineIdle",
    "EngineCruise",
    "EnginePower",
    "Propeller",
    "OpenCockpitWind",
}
PROHIBITED_IMPORTS = {
    "requests",
    "urllib",
    "http",
    "ftplib",
    "socket",
    "subprocess",
}
PROHIBITED_CALL_NAMES = {
    "AssetImportTask",
    "import_asset_tasks",
    "import_assets_automated",
}


def dotted_name(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def validate_builder(path):
    errors = []
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    imports = set()
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            calls.add(dotted_name(node.func).rsplit(".", 1)[-1])
    prohibited_imports = sorted(imports & PROHIBITED_IMPORTS)
    prohibited_calls = sorted(calls & PROHIBITED_CALL_NAMES)
    if prohibited_imports:
        errors.append("builder has network/process imports: " + ",".join(prohibited_imports))
    if prohibited_calls:
        errors.append("builder has asset-import calls: " + ",".join(prohibited_calls))
    required_fragments = (
        "load_asset",
        "create_asset",
        "initialize_required_entries",
        "preserve",
        "MISSING_SOURCE",
        "production_ready",
    )
    for fragment in required_fragments:
        if fragment not in source:
            errors.append("builder missing safeguard fragment: " + fragment)
    return errors


def validate_contract(data):
    errors = []
    if data.get("schema") != "skyguard.phase5.p5a-identity-bed-routing.v1":
        errors.append("unexpected contract schema")
    bank = data.get("production_bank", {})
    if bank.get("required_full_bank_category_count") != 25:
        errors.append("production bank must retain all 25 categories")
    if bank.get("initialize_only_when_created") is not True:
        errors.append("bank initialization must be create-only")
    if bank.get("preserve_existing_entries_on_rerun") is not True:
        errors.append("reruns must preserve existing bank entries")

    routing = data.get("routing_assets", [])
    names = [item.get("contract_name") for item in routing]
    paths = [item.get("asset_path") for item in routing]
    if len(routing) != 7 or set(names) != set(EXPECTED_ROUTING):
        errors.append("routing contract must contain the exact seven assets")
    if len(names) != len(set(names)) or len(paths) != len(set(paths)):
        errors.append("routing names and paths must be unique")
    for item in routing:
        name = item.get("contract_name")
        if EXPECTED_ROUTING.get(name) != item.get("asset_class"):
            errors.append("wrong routing class for " + str(name))
        if not str(item.get("asset_path", "")).startswith("/Game/Skyguard/Audio/"):
            errors.append("routing asset outside governed audio root: " + str(name))
        expected_parent = None if name in ("MasterSubmix", "CockpitSoundMix") else "MasterSubmix"
        if item.get("parent") != expected_parent:
            errors.append("wrong routing parent for " + str(name))

    placeholders = data.get("identity_bed_placeholders", [])
    categories = [item.get("category") for item in placeholders]
    if len(placeholders) != 5 or set(categories) != EXPECTED_IDENTITY:
        errors.append("identity bed must contain the exact five P5-A categories")
    if len(categories) != len(set(categories)):
        errors.append("identity placeholder categories must be unique")
    for item in placeholders:
        category = str(item.get("category"))
        if item.get("source_status") != "MISSING_SOURCE":
            errors.append(category + " is not explicitly MISSING_SOURCE")
        for field in ("sound", "provenance_id", "source_sha256"):
            if item.get(field) is not None:
                errors.append(category + " has forbidden unsourced proof field: " + field)
        if not str(item.get("future_sound_destination", "")).startswith(
            "/Game/Skyguard/Audio/Production/"
        ):
            errors.append(category + " has invalid future destination")

    defaults = data.get("routing_defaults", {})
    if defaults.get("cockpit_exterior_attenuation") != 0.72:
        errors.append("cockpit exterior attenuation drift")
    if defaults.get("cockpit_low_pass_hz") != 7200.0:
        errors.append("cockpit low-pass drift")

    performance = data.get("performance_contract", {})
    expected_performance = {
        "director_hard_voice_limit": 24,
        "packaged_acceptance_voice_limit": 48,
        "p5a_isolated_identity_voice_limit": 8,
        "maximum_audio_thread_ms": 2.0,
        "maximum_true_peak_dbtp": -1.0,
        "maximum_underruns": 0,
        "minimum_metered_samples": 600,
        "prime_during_briefing": True,
        "synchronous_gameplay_loads_allowed": False,
        "procedural_qa_sources_allowed_in_shipping": False,
    }
    for key, expected in expected_performance.items():
        if performance.get(key) != expected:
            errors.append("performance contract drift: " + key)

    state = data.get("current_state", {})
    if state.get("identity_sources_bound") != 0:
        errors.append("offline scaffold cannot claim bound identity sources")
    if state.get("production_ready") is not False:
        errors.append("offline scaffold cannot claim production readiness")
    policy = data.get("acceptance_policy", {})
    if policy.get("full_phase5_requires_bound_categories") != 25:
        errors.append("full Phase 5 cannot require fewer than 25 bound categories")
    if policy.get("forbidden_claim") != "PHASE5_PRODUCTION_READY":
        errors.append("missing forbidden readiness claim")
    return errors


def validate_build_receipt(path):
    if not path.exists():
        return False, ["Unreal build receipt not present (expected before builder execution)"], None
    receipt = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if receipt.get("schema") != "skyguard.phase5.p5a-routing-build-receipt.v1":
        errors.append("unexpected build receipt schema")
    if receipt.get("routing_asset_count") != 7:
        errors.append("build receipt does not prove seven routing assets")
    if receipt.get("identity_placeholder_count") != 5:
        errors.append("build receipt does not prove five identity placeholders")
    if receipt.get("required_category_count") != 25:
        errors.append("build receipt lost the full 25-category bank")
    if receipt.get("missing_routing_assets") != []:
        errors.append("build receipt reports missing routing assets")
    # Routing-only construction must not itself make an unsourced bank ready.
    if (
        receipt.get("bound_production_source_count") == 0
        and receipt.get("production_ready") is not False
    ):
        errors.append("unsourced routing receipt falsely claims production ready")
    return not errors, errors, receipt


def run(contract_path=DEFAULT_CONTRACT, builder_path=DEFAULT_BUILDER,
        receipt_path=DEFAULT_BUILD_RECEIPT):
    data = json.loads(contract_path.read_text(encoding="utf-8"))
    contract_errors = validate_contract(data)
    builder_errors = validate_builder(builder_path)
    built, receipt_errors, receipt = validate_build_receipt(receipt_path)
    offline_valid = not contract_errors and not builder_errors
    production_ready = bool(
        built and receipt and receipt.get("production_ready") is True
    )
    return {
        "schema": "skyguard.phase5.p5a-routing-contract-audit.v1",
        "contract_path": str(contract_path),
        "builder_path": str(builder_path),
        "routing_contract_count": len(data.get("routing_assets", [])),
        "identity_placeholder_count": len(data.get("identity_bed_placeholders", [])),
        "contract_errors": contract_errors,
        "builder_errors": builder_errors,
        "build_receipt_errors": receipt_errors,
        "offline_contract_valid": offline_valid,
        "routing_scaffold_built": built,
        "production_ready": production_ready,
        "status": (
            "INVALID_CONTRACT"
            if not offline_valid
            else "P5A_ROUTING_SCAFFOLD_BUILT"
            if built
            else "CONTRACT_VALID_NOT_BUILT_MISSING_SOURCE"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--builder", type=Path, default=DEFAULT_BUILDER)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_BUILD_RECEIPT)
    parser.add_argument("--require-built", action="store_true")
    parser.add_argument("--require-production-ready", action="store_true")
    args = parser.parse_args()
    audit = run(args.contract, args.builder, args.receipt)
    DEFAULT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))
    if not audit["offline_contract_valid"]:
        return 2
    if args.require_built and not audit["routing_scaffold_built"]:
        return 3
    if args.require_production_ready and not audit["production_ready"]:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
