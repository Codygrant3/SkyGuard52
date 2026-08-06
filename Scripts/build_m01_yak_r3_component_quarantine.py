"""Import only R3 donor components into an isolated Unreal quarantine folder.

This script never opens, creates, saves, or replaces a map. It never promotes
the imported assets. Run only through run_m01_yak_r3_component_quarantine_gate.ps1.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import unreal


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Scripts"))
from audit_m01_yak_r3_component_import_source import audit_source, load_json  # noqa: E402


CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_YAK_R3_COMPONENT_IMPORT_CONTRACT.json"
DESTINATION = "/Game/Skyguard/Quarantine/M01/YakR3ComponentEval"
BUILD_REPORT = ROOT / "Saved/Reports/M01_YAK_R3_COMPONENT_QUARANTINE_BUILD.json"
def fail(message: str) -> None:
    raise RuntimeError("[M01YakR3Quarantine] " + message)


def asset_class(asset) -> str:
    return asset.get_class().get_name() if asset else "Missing"


def set_tags(asset, tags: dict[str, str]) -> None:
    for key, value in tags.items():
        unreal.EditorAssetLibrary.set_metadata_tag(asset, key, str(value))


def metadata(asset, key: str) -> str:
    return str(unreal.EditorAssetLibrary.get_metadata_tag(asset, key))


def validate_resume_assets(contract: dict, existing: list[str]) -> tuple[
    dict[str, str], list[str]
]:
    """Accept only the exact persisted output of the known failed-closed attempt."""
    expected_targets = {
        target: source for source, target in contract["component_meshes"].items()
    }
    allowed_support = set(contract["support_materials"]) | set(
        contract["support_textures"]
    )
    found: dict[str, str] = {}
    support: list[str] = []
    errors: list[str] = []
    for path in existing:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        kind = asset_class(asset)
        name = asset.get_name() if asset else ""
        if isinstance(asset, unreal.StaticMesh) and name in expected_targets:
            identity = expected_targets[name]
            required_tags = {
                "Skyguard.BuildId": contract["build_id"],
                "Skyguard.R3LedgerIdentity": identity,
                "Skyguard.SourceSha256": contract["source"]["sha256"],
                "Skyguard.Quarantine": "true",
                "Skyguard.EvaluationOnly": "true",
                "Skyguard.PromotionAllowed": "false",
            }
            for key, expected in required_tags.items():
                if metadata(asset, key).lower() != expected.lower():
                    errors.append(f"{name}: metadata mismatch for {key}")
            found[identity] = path
        elif name in allowed_support and kind in {
            "Material", "MaterialInstanceConstant", "Texture2D"
        }:
            support.append(path)
        else:
            errors.append(f"unexpected persisted asset {path}:{kind}")
    missing_meshes = sorted(set(contract["component_meshes"]) - set(found))
    support_names = {
        unreal.EditorAssetLibrary.load_asset(path).get_name() for path in support
    }
    missing_support = sorted(allowed_support - support_names)
    if missing_meshes:
        errors.append("missing persisted donor meshes: " + ", ".join(missing_meshes))
    if missing_support:
        errors.append("missing persisted support assets: " + ", ".join(missing_support))
    if errors:
        fail(
            "non-empty quarantine is not the exact recoverable failed attempt: "
            + "; ".join(errors)
        )
    return found, support


def main() -> None:
    contract = load_json(CONTRACT_PATH)
    if contract["unreal"]["destination"] != DESTINATION:
        fail("destination differs from source-audited contract")
    source_audit = audit_source()
    if source_audit["gate"] != "PASS_COMPONENT_IMPORT_SOURCE_AUDIT":
        fail("offline source audit failed")
    if not unreal.EditorAssetLibrary.does_directory_exist(DESTINATION):
        unreal.EditorAssetLibrary.make_directory(DESTINATION)

    expected_by_source = contract["component_meshes"]
    allowed_support_names = set(contract["support_materials"]) | set(
        contract["support_textures"]
    )
    found: dict[str, str] = {}
    support_assets: list[str] = []
    removed_assets: list[str] = []
    violations: list[str] = []
    existing = list(unreal.EditorAssetLibrary.list_assets(DESTINATION, True, False))
    resumed_failed_attempt = bool(existing)
    if resumed_failed_attempt:
        found, support_assets = validate_resume_assets(contract, existing)
    else:
        source = str(ROOT / contract["source"]["path"])
        task = unreal.AssetImportTask()
        task.filename = source
        task.destination_path = DESTINATION
        task.automated = True
        task.replace_existing = False
        task.save = False
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        if not task.imported_object_paths:
            fail("GLB import returned no object paths")
        all_assets = list(unreal.EditorAssetLibrary.list_assets(DESTINATION, True, False))
        for path in all_assets:
            asset = unreal.EditorAssetLibrary.load_asset(path)
            kind = asset_class(asset)
            name = asset.get_name() if asset else path.rsplit("/", 1)[-1].split(".")[0]
            if isinstance(asset, unreal.StaticMesh) and name in expected_by_source:
                found[name] = path
            elif name in allowed_support_names and kind in {
                "Material", "MaterialInstanceConstant", "Texture2D"
            }:
                support_assets.append(path)
            else:
                if kind in contract["forbidden_import_classes"]:
                    violations.append(f"{path}:{kind}")
                if not unreal.EditorAssetLibrary.delete_asset(path):
                    fail("could not remove non-whitelisted import " + path)
                removed_assets.append(path)

        missing = sorted(set(expected_by_source) - set(found))
        if missing:
            fail("missing donor meshes after import: " + ", ".join(missing))
        imported_support_names = {
            unreal.EditorAssetLibrary.load_asset(path).get_name()
            for path in support_assets
        }
        missing_support = sorted(allowed_support_names - imported_support_names)
        if missing_support:
            fail("missing contracted support assets: " + ", ".join(missing_support))
        if violations:
            fail(
                "forbidden imported asset classes were observed: "
                + ", ".join(violations)
            )

    pivot_payload = {
        "build_id": contract["build_id"],
        "reference_datums": contract["reference_datums"],
        "promotion_allowed": False,
    }
    safety_payload = {
        "build_id": contract["build_id"],
        "camera_reference": contract["camera_reference"],
        "safety_volumes": contract["safety_volumes"],
        "retained_l88_bundles": contract["retained_l88_bundles"],
        "promotion_allowed": False,
    }
    pivot_json = json.dumps(pivot_payload, sort_keys=True)
    safety_json = json.dumps(safety_payload, sort_keys=True)
    retained: list[dict[str, str]] = []
    for source_name, target_name in expected_by_source.items():
        source_path = found[source_name]
        target_path = DESTINATION + "/" + target_name
        if not resumed_failed_attempt:
            if not unreal.EditorAssetLibrary.rename_asset(source_path, target_path):
                fail(f"could not rename {source_path} to {target_path}")
        asset = unreal.EditorAssetLibrary.load_asset(target_path)
        if not isinstance(asset, unreal.StaticMesh):
            fail("renamed donor did not persist as StaticMesh: " + target_path)
        set_tags(
            asset,
            {
                "Skyguard.BuildId": contract["build_id"],
                "Skyguard.R3LedgerIdentity": source_name,
                "Skyguard.SourceSha256": contract["source"]["sha256"],
                "Skyguard.Quarantine": "true",
                "Skyguard.EvaluationOnly": "true",
                "Skyguard.PromotionAllowed": "false",
                "Skyguard.RequiresPivotEvidence": "true",
                "Skyguard.RequiresMaterialEvidence": "true",
                "Skyguard.RequiresCollisionEvidence": "true",
                "Skyguard.RequiresCameraEvidence": "true",
                "Skyguard.RequiresSafetyEvidence": "true",
                "Skyguard.PivotReferenceJson": pivot_json,
                "Skyguard.SafetyCameraReferenceJson": safety_json,
            },
        )
        retained.append({"ledger_identity": source_name, "asset": target_path})

    if not unreal.EditorAssetLibrary.save_directory(
        DESTINATION, only_if_is_dirty=False, recursive=True
    ):
        fail("failed to save quarantine directory")

    BUILD_REPORT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "skyguard.m01.yak-r3-component-quarantine-build.v1",
        "gate": "PASS_QUARANTINE_IMPORT_REQUIRES_FRESH_PROCESS_AUDIT",
        "build_id": contract["build_id"],
        "source_sha256": contract["source"]["sha256"],
        "destination": DESTINATION,
        "retained_components": retained,
        "reference_storage": "metadata_on_each_component",
        "reference_asset_count": 0,
        "support_assets": sorted(support_assets),
        "removed_non_whitelisted_assets": sorted(removed_assets),
        "resumed_exact_failed_attempt": resumed_failed_attempt,
        "runtime_map_changed": False,
        "config_changed": False,
        "promotion_allowed": False,
    }
    BUILD_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("[M01YakR3Quarantine] " + report["gate"])


if __name__ == "__main__":
    main()
