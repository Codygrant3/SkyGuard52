import json
import os
from datetime import datetime, timezone

import unreal


PROJECT_ROOT = r"D:\Skyguard52"
REPORT_PATH = os.path.join(
    PROJECT_ROOT,
    "Saved",
    "Reports",
    "M01_RUNTIME_MATERIAL_COMPATIBILITY_VERIFICATION.json",
)

MESH_ROOTS = [
    "/Game/Skyguard/Meshes/L88/yak52_l88_silhouette_blockout",
    "/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement",
]

INSTANCED_MATERIALS = [
    "/Game/Skyguard/Materials/Generated/M_AsphaltRoad",
    "/Game/Skyguard/Materials/Generated/M_L23_Ocean",
    "/Game/Skyguard/Materials/Generated/M_L23_Beach",
]


def main():
    mesh_results = []
    failures = []
    discovered = set()
    for root in MESH_ROOTS:
        for path in unreal.EditorAssetLibrary.list_assets(
            root, recursive=True, include_folder=False
        ):
            asset = unreal.EditorAssetLibrary.load_asset(path)
            if not isinstance(asset, unreal.StaticMesh):
                continue
            canonical = asset.get_path_name().split(".", 1)[0]
            if canonical in discovered:
                continue
            discovered.add(canonical)
            enabled = bool(
                asset.get_editor_property("nanite_settings").enabled
            )
            mesh_results.append(
                {"asset": canonical, "nanite_enabled": enabled}
            )
            if enabled:
                failures.append(
                    f"Provisional Interchange mesh still has Nanite: {canonical}"
                )

    material_results = []
    for path in INSTANCED_MATERIALS:
        interface = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(interface, unreal.MaterialInterface):
            failures.append(f"Missing material interface: {path}")
            continue
        material = interface.get_base_material()
        if not material:
            failures.append(f"Missing base material: {path}")
            continue
        base_path = material.get_path_name().split(".", 1)[0]
        enabled = bool(
            material.get_editor_property(
                "used_with_instanced_static_meshes"
            )
        )
        material_results.append(
            {
                "material_interface": path,
                "base_material": base_path,
                "used_with_instanced_static_meshes": enabled,
            }
        )
        if not base_path.startswith("/Game/Skyguard/"):
            failures.append(
                f"Instanced material does not use a project base: "
                f"{path} -> {base_path}"
            )
        if not enabled:
            failures.append(
                f"Instanced usage flag is false: {path} -> {base_path}"
            )

    if not mesh_results:
        failures.append("No provisional Interchange static meshes discovered.")

    report = {
        "schema": "skyguard.m01.runtime-material-compatibility-verification.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": "PASS" if not failures else "FAIL",
        "mesh_count": len(mesh_results),
        "material_count": len(material_results),
        "mesh_results": mesh_results,
        "material_results": material_results,
        "failures": failures,
    }
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    if failures:
        raise RuntimeError("; ".join(failures))
    unreal.log(
        "M01_RUNTIME_MATERIAL_COMPATIBILITY_VERIFICATION=PASS "
        f"meshes={len(mesh_results)} materials={len(material_results)} "
        f"report={REPORT_PATH}"
    )


if __name__ == "__main__":
    main()
