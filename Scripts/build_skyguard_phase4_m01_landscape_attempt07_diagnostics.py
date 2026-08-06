"""Author only the two immutable Attempt07 Landscape diagnostic materials."""

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
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_CONTRACT.json"
)


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
    if contract["contract_id"] != "P4.5-M01-LANDSCAPE-VISIBLE-007":
        raise RuntimeError("Attempt07 contract ID mismatch")
    receipt = Path(parse_switch("SkyguardAttempt07AuthorReceipt"))
    if receipt.exists():
        raise RuntimeError("Attempt07 author receipt already exists")
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
                "Attempt07 immutable diagnostic already exists: "
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
    usage = {}
    for name, material in authored.items():
        if not isinstance(material, unreal.Material):
            raise RuntimeError("Attempt07 output is not a Material: " + name)
        usage[name] = {
            "used_with_landscape": bool(
                material.get_editor_property("used_with_landscape")
            ),
            "shading_model": str(
                material.get_editor_property("shading_model")
            ),
        }
        if not usage[name]["used_with_landscape"]:
            raise RuntimeError(name + " lacks Landscape usage")
        output_path = ROOT / outputs[name]["file"]
        if not output_path.is_file():
            raise RuntimeError("Attempt07 output file missing: " + str(output_path))
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
            "attempt07-author-receipt.v1"
        ),
        "contract_id": contract["contract_id"],
        "gate": "PASS",
        "output_hashes": output_hashes,
        "material_usage": usage,
        "locked_packages_before": locked_before,
        "locked_packages_after": locked_after,
        "locked_packages_unchanged": True,
        "world_saved": False,
        "only_new_diagnostic_packages_saved": True,
        "pcg_generation_invoked": False,
        "promotion_allowed": False,
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("[SkyguardAttempt07Author] " + json.dumps(report))


if __name__ == "__main__":
    main()
