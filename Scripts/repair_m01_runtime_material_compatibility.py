import json
import os
from datetime import datetime, timezone

import unreal


PROJECT_ROOT = r"D:\Skyguard52"
REPORT_PATH = os.path.join(
    PROJECT_ROOT,
    "Saved",
    "Reports",
    "M01_RUNTIME_MATERIAL_COMPATIBILITY_REPAIR.json",
)

PROVISIONAL_INTERCHANGE_MESH_ROOTS = [
    "/Game/Skyguard/Meshes/L88/yak52_l88_silhouette_blockout",
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement",
]

INSTANCED_MATERIALS = [
    "/Game/Skyguard/Materials/Generated/M_AsphaltRoad",
    "/Game/Skyguard/Materials/Generated/M_L23_Ocean",
    "/Game/Skyguard/Materials/Generated/M_L23_Beach",
]

def load_required(path, expected_type):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not asset:
        raise RuntimeError(f"Required asset is missing: {path}")
    if not isinstance(asset, expected_type):
        raise RuntimeError(
            f"Required asset has wrong type: {path}; "
            f"expected={expected_type.__name__}; actual={type(asset).__name__}"
        )
    return asset


def set_material_usage(path, property_name):
    material_interface = load_required(path, unreal.MaterialInterface)
    material = material_interface.get_base_material()
    if not material:
        raise RuntimeError(f"Material interface has no base material: {path}")
    material_path = material.get_path_name().split(".", 1)[0]
    if not material_path.startswith("/Game/Skyguard/"):
        raise RuntimeError(
            f"Refusing to modify a non-project base material: "
            f"interface={path}; base={material_path}"
        )
    before = bool(material.get_editor_property(property_name))
    material.set_editor_property(property_name, True)
    if not unreal.EditorAssetLibrary.save_loaded_asset(material, False):
        raise RuntimeError(f"Failed to save material: {path}")
    after = bool(material.get_editor_property(property_name))
    if not after:
        raise RuntimeError(
            f"Material usage flag did not persist in memory: "
            f"{path}.{property_name}"
        )
    return {
        "material_interface": path,
        "base_material": material_path,
        "property": property_name,
        "before": before,
        "after": after,
    }


def disable_nanite(mesh):
    path = mesh.get_path_name().split(".", 1)[0]
    settings = mesh.get_editor_property("nanite_settings")
    before = bool(settings.enabled)
    settings.enabled = False
    mesh.set_editor_property("nanite_settings", settings)
    if not unreal.EditorAssetLibrary.save_loaded_asset(mesh, False):
        raise RuntimeError(f"Failed to save static mesh: {path}")
    persisted = mesh.get_editor_property("nanite_settings")
    after = bool(persisted.enabled)
    if after:
        raise RuntimeError(f"Nanite remained enabled on translucent mesh: {path}")
    return {
        "asset": path,
        "property": "nanite_settings.enabled",
        "before": before,
        "after": after,
    }


def disable_nanite_for_provisional_interchange_meshes():
    changes = []
    discovered = set()
    for root in PROVISIONAL_INTERCHANGE_MESH_ROOTS:
        for path in unreal.EditorAssetLibrary.list_assets(
            root, recursive=True, include_folder=False
        ):
            asset = unreal.EditorAssetLibrary.load_asset(path)
            if not isinstance(asset, unreal.StaticMesh):
                continue
            canonical_path = asset.get_path_name().split(".", 1)[0]
            if canonical_path in discovered:
                continue
            discovered.add(canonical_path)
            changes.append(disable_nanite(asset))
    if not changes:
        raise RuntimeError(
            "No provisional Interchange static meshes were discovered."
        )
    return changes


def main():
    changes = disable_nanite_for_provisional_interchange_meshes()
    for path in INSTANCED_MATERIALS:
        changes.append(
            set_material_usage(path, "used_with_instanced_static_meshes")
        )

    report = {
        "schema": "skyguard.m01.runtime-material-compatibility-repair.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": "PASS",
        "provisional_interchange_mesh_count": (
            len(changes) - len(INSTANCED_MATERIALS)
        ),
        "instanced_material_count": len(INSTANCED_MATERIALS),
        "changes": changes,
        "promotion_scope": (
            "Persisted compatibility settings only. Provisional Interchange "
            "meshes remain non-Nanite until they receive project-owned "
            "production materials. This report does not claim AAA visual "
            "acceptance or production material authorship."
        ),
    }
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    unreal.log(
        "M01_RUNTIME_MATERIAL_COMPATIBILITY_REPAIR=PASS "
        f"changes={len(changes)} report={REPORT_PATH}"
    )


if __name__ == "__main__":
    main()
