"""Fresh-editor persistence verification for Mission 1 refined materials."""

import json
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
SOURCE_AUDIT_PATH = ROOT / "Saved/Reports/M01_REFINEMENT_MATERIAL_UNREAL_AUDIT.json"
VERIFY_PATH = ROOT / "Saved/Reports/M01_REFINEMENT_MATERIAL_PERSISTENCE_AUDIT.json"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Material_Validation"


def expected_texture_settings(role):
    return {
        "srgb": role == "BaseColor",
        "normal_compression": role == "Normal",
        "mask_compression": role in {"Roughness", "ORM", "MaterialID"},
        "flip_green": role == "Normal",
    }


def main():
    with open(SOURCE_AUDIT_PATH, "r", encoding="utf-8") as stream:
        source = json.load(stream)
    loaded = unreal.EditorLevelLibrary.load_level(MAP_PATH)
    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())

    observed = {}
    for actor in actors:
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.get_editor_property("static_mesh")
            if mesh is None:
                continue
            key = "%s|%s|%s" % (
                actor.get_actor_label(),
                component.get_name(),
                mesh.get_name(),
            )
            overrides = component.get_editor_property("override_materials")
            observed[key] = [
                material.get_path_name() if material else None for material in overrides
            ]

    binding_failures = []
    for entry in source["bindings"]:
        key = "%s|%s|%s" % (
            entry["actor"],
            entry["component"],
            entry["mesh"],
        )
        expected_path = entry["material"]
        actual = observed.get(key)
        if (
            actual is None
            or len(actual) < entry["slot_count"]
            or any(path != expected_path for path in actual[: entry["slot_count"]])
        ):
            binding_failures.append({
                "key": key,
                "expected": expected_path,
                "observed": actual,
            })

    texture_results = []
    for entry in source["provenance"]:
        texture = unreal.EditorAssetLibrary.load_asset(entry["unreal_asset"])
        expected = expected_texture_settings(entry["role"])
        actual = {
            "srgb": bool(texture.get_editor_property("srgb")) if texture else None,
            "normal_compression": (
                texture.get_editor_property("compression_settings")
                == unreal.TextureCompressionSettings.TC_NORMALMAP
                if texture else False
            ),
            "mask_compression": (
                texture.get_editor_property("compression_settings")
                == unreal.TextureCompressionSettings.TC_MASKS
                if texture else False
            ),
            "flip_green": (
                bool(texture.get_editor_property("flip_green_channel"))
                if texture else None
            ),
        }
        passed = (
            texture is not None
            and actual["srgb"] == expected["srgb"]
            and (not expected["normal_compression"] or actual["normal_compression"])
            and (not expected["mask_compression"] or actual["mask_compression"])
            and actual["flip_green"] == expected["flip_green"]
        )
        texture_results.append({
            "asset": entry["unreal_asset"],
            "role": entry["role"],
            "expected": expected,
            "actual": actual,
            "pass": passed,
        })

    material_paths = sorted({entry["material"] for entry in source["bindings"]})
    checks = {
        "map_loaded": bool(loaded),
        "all_component_bindings_persisted": not binding_failures,
        "all_texture_settings_persisted": all(
            entry["pass"] for entry in texture_results
        ),
        "all_material_assets_persisted": all(
            unreal.EditorAssetLibrary.does_asset_exist(path)
            for path in material_paths
        ),
        "material_family_count_persisted": len(material_paths) == 7,
    }
    report = {
        "schema": "skyguard.m01.refinement.material-persistence-audit.v1",
        "map": MAP_PATH,
        "actor_count": len(actors),
        "expected_binding_count": len(source["bindings"]),
        "binding_failure_count": len(binding_failures),
        "binding_failures": binding_failures,
        "texture_setting_count": len(texture_results),
        "texture_results": texture_results,
        "material_paths": material_paths,
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion": "material_candidate_requires_rendered_visual_and_gpu_profile_acceptance",
    }
    VERIFY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VERIFY_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    unreal.log("[SkyguardM01MaterialPersistence] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 1 material persistence gate failed")


if __name__ == "__main__":
    main()
