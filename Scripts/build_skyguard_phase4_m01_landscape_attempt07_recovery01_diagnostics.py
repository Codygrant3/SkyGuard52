"""Author only the two immutable Attempt07 Recovery01 diagnostic materials."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from build_skyguard_phase4_m01_landscape_material_validation import (
    build_unlit_diagnostic_material,
)


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY01_CONTRACT.json"
)
CONTRACT_ID = "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-01"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def parse_switch(name: str) -> str:
    command_line = unreal.SystemLibrary.get_command_line()
    match = re.search(
        rf'(?:^|\s)-{re.escape(name)}=(?:"([^"]+)"|(\S+))',
        command_line,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Missing required -" + name + " switch")
    return match.group(1) or match.group(2)


def main() -> None:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Attempt07 Recovery01 contract ID mismatch")
    receipt = Path(
        parse_switch("SkyguardAttempt07Recovery01AuthorReceipt")
    )
    if receipt.exists():
        raise RuntimeError("Attempt07 Recovery01 author receipt already exists")

    failed = contract["immutable_failed_attempt07"]
    failed_root = ROOT / failed["root"]
    for name, item in failed["files"].items():
        path = failed_root / item["file"]
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise RuntimeError(
                "Failed Attempt07 evidence hash changed: " + name
            )

    outputs = contract["new_immutable_outputs"]
    for item in (
        outputs["coverage_material"],
        outputs["component_id_material"],
    ):
        if (
            unreal.EditorAssetLibrary.does_asset_exist(item["asset"])
            or (ROOT / item["file"]).exists()
        ):
            raise RuntimeError(
                "Attempt07 Recovery01 immutable diagnostic already exists: "
                + item["asset"]
            )

    locked_before = {}
    for name, item in contract["locked_production_packages"].items():
        path = ROOT / item["file"]
        digest = sha256_file(path)
        if digest != item["sha256"]:
            raise RuntimeError("Locked package hash failed: " + str(path))
        locked_before[name] = digest

    coverage = build_unlit_diagnostic_material(
        outputs["coverage_material"]["asset"], False
    )
    component = build_unlit_diagnostic_material(
        outputs["component_id_material"]["asset"], True
    )
    authored = {
        "coverage_material": coverage,
        "component_id_material": component,
    }
    output_hashes = {}
    material_metadata = {}
    for name, material in authored.items():
        if not isinstance(material, unreal.Material):
            raise RuntimeError(
                "Attempt07 Recovery01 output is not a Material: " + name
            )
        material_metadata[name] = {
            "shading_model": str(
                material.get_editor_property("shading_model")
            ),
            "graph_recompiled_before_save": True,
            "landscape_usage_flag_claimed": False,
        }
        output_path = ROOT / outputs[name]["file"]
        if not output_path.is_file():
            raise RuntimeError(
                "Attempt07 Recovery01 output file missing: "
                + str(output_path)
            )
        output_hashes[name] = sha256_file(output_path)

    locked_after = {
        name: sha256_file(ROOT / item["file"])
        for name, item in contract["locked_production_packages"].items()
    }
    if locked_after != locked_before:
        raise RuntimeError("Locked production package changed during authoring")

    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-recovery01-author-receipt.v1"
        ),
        "contract_id": contract["contract_id"],
        "gate": "PASS",
        "native_live_readiness_api": (
            "FMaterialResource::FinishCompilation plus valid "
            "game-thread shader-map audit"
        ),
        "output_hashes": output_hashes,
        "material_metadata": material_metadata,
        "locked_packages_before": locked_before,
        "locked_packages_after": locked_after,
        "locked_packages_unchanged": True,
        "failed_attempt07_evidence_unchanged": True,
        "world_saved": False,
        "only_new_recovery01_diagnostic_packages_saved": True,
        "pcg_generation_invoked": False,
        "promotion_allowed": False,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("[SkyguardAttempt07Recovery01Author] " + json.dumps(report))


if __name__ == "__main__":
    main()
