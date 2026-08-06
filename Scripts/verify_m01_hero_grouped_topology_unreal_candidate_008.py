"""Fresh-process persistence verifier for the isolated Build 008 candidate."""

from __future__ import annotations

import json
from pathlib import Path

import unreal


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_ACCEPTANCE_008_CONTRACT.json"
BUILD_REPORT = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_CANDIDATE_008_BUILD.json"
VERIFY_REPORT = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_CANDIDATE_008_PERSISTENCE.json"
CANDIDATE_ROOT = "/Game/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def material_path(mesh, index: int) -> str | None:
    material = mesh.get_material(index)
    return material.get_path_name() if material else None


def package_path(path: str | None) -> str | None:
    """Normalize `/Package/Asset.Asset` object paths to `/Package/Asset`."""
    return path.rsplit(".", 1)[0] if path and "." in path.rsplit("/", 1)[-1] else path


def main() -> None:
    contract = load(CONTRACT_PATH)
    if contract["unreal"]["candidate_root"] != CANDIDATE_ROOT:
        raise RuntimeError("candidate root differs from source-audited verifier")
    build = load(BUILD_REPORT)
    failures = []
    mesh_results = []
    tolerance = contract["mesh_policy"]["scale"]["maximum_dimension_relative_error"]

    for record in build["meshes"]:
        key = record["key"]
        mesh = unreal.EditorAssetLibrary.load_asset(record["asset"])
        if not isinstance(mesh, unreal.StaticMesh):
            failures.append(key + ": missing StaticMesh")
            continue
        actual = mesh.get_bounds().box_extent
        actual_dims = [abs(float(actual.x)) * 2.0, abs(float(actual.y)) * 2.0, abs(float(actual.z)) * 2.0]
        expected_dims = record["expected_dimensions_cm"]
        dimension_error = max(
            abs(a - e) / max(e, 0.001)
            for a, e in zip(sorted(actual_dims), sorted(expected_dims))
        )
        settings = mesh.get_editor_property("nanite_settings")
        expected_nanite = key in contract["mesh_policy"]["nanite"]["enabled_groups"]
        body_setup = mesh.get_editor_property("body_setup")
        aggregate = body_setup.get_editor_property("agg_geom")
        primitive_count = 0
        for field in (
            "box_elems",
            "sphere_elems",
            "sphyl_elems",
            "convex_elems",
            "tapered_capsule_elems",
        ):
            try:
                primitive_count += len(aggregate.get_editor_property(field))
            except Exception:
                pass
        collision_mode = contract["mesh_policy"]["collision"][key]
        slots = len(mesh.get_editor_property("static_materials"))
        bindings = [
            package_path(material_path(mesh, index)) for index in range(slots)
        ]
        expected_material = package_path(record["material"])
        metadata_ok = (
            unreal.EditorAssetLibrary.get_metadata_tag(mesh, "Skyguard.BuildId") == contract["build_id"]
            and unreal.EditorAssetLibrary.get_metadata_tag(mesh, "Skyguard.SourceSha256")
            == contract["bound_sources"]["low_glb"]["sha256"]
            and unreal.EditorAssetLibrary.get_metadata_tag(mesh, "Skyguard.SemanticGroup") == key
            and unreal.EditorAssetLibrary.get_metadata_tag(mesh, "Skyguard.PromotionAllowed").lower() == "false"
        )
        passed = (
            dimension_error <= tolerance
            and bool(settings.enabled) == expected_nanite
            and ((collision_mode == "NONE" and primitive_count == 0) or (collision_mode != "NONE" and primitive_count > 0))
            and slots > 0
            and all(path == expected_material for path in bindings)
            and metadata_ok
        )
        if not passed:
            failures.append(key + ": mesh acceptance mismatch")
        mesh_results.append({
            "key": key,
            "asset": record["asset"],
            "dimensions_cm": actual_dims,
            "maximum_dimension_relative_error": dimension_error,
            "nanite_expected": expected_nanite,
            "nanite_actual": bool(settings.enabled),
            "collision_mode": collision_mode,
            "collision_primitive_count": primitive_count,
            "material_bindings": bindings,
            "metadata_ok": metadata_ok,
            "passed": passed,
        })

    texture_results = []
    for record in build["textures"]:
        texture = unreal.EditorAssetLibrary.load_asset(record["asset"])
        role = record["key"].rsplit("/", 1)[-1]
        passed = isinstance(texture, unreal.Texture2D)
        actual = {}
        if passed:
            actual = {
                "srgb": bool(texture.get_editor_property("srgb")),
                "virtual_texture_streaming": bool(texture.get_editor_property("virtual_texture_streaming")),
                "compression_settings": str(texture.get_editor_property("compression_settings")),
                "flip_green_channel": bool(texture.get_editor_property("flip_green_channel")),
            }
            passed = (
                not actual["srgb"]
                and not actual["virtual_texture_streaming"]
                and (
                    role == "Normal"
                    and texture.get_editor_property("compression_settings")
                    == unreal.TextureCompressionSettings.TC_NORMALMAP
                    and actual["flip_green_channel"]
                    or role == "AO"
                    and texture.get_editor_property("compression_settings")
                    == unreal.TextureCompressionSettings.TC_MASKS
                )
            )
        if not passed:
            failures.append(record["key"] + ": texture setting mismatch")
        texture_results.append({"key": record["key"], "asset": record["asset"], "actual": actual, "passed": passed})

    loaded_map = unreal.EditorLevelLibrary.load_level(contract["unreal"]["review_map"])
    candidate_assets = list(
        unreal.EditorAssetLibrary.list_assets(contract["unreal"]["candidate_root"], True, False)
    )
    checks = {
        "exact_12_meshes_persisted": len(mesh_results) == 12 and all(item["passed"] for item in mesh_results),
        "exact_24_textures_persisted": len(texture_results) == 24 and all(item["passed"] for item in texture_results),
        "exact_12_materials_persisted": len(build["materials"]) == 12 and all(
            unreal.EditorAssetLibrary.does_asset_exist(path)
            for path in build["materials"].values()
        ),
        "candidate_review_map_persisted": bool(loaded_map)
        and unreal.EditorAssetLibrary.does_asset_exist(contract["unreal"]["review_map"]),
        "candidate_namespace_only": all(
            path.startswith(contract["unreal"]["candidate_root"] + "/")
            for path in candidate_assets
        ),
        "maximum_dimension_relative_error": all(
            item["maximum_dimension_relative_error"] <= tolerance for item in mesh_results
        ),
        "promotion_allowed": False,
    }
    passed = all(value is True or key == "promotion_allowed" and value is False for key, value in checks.items())
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-candidate-persistence.v1",
        "gate": (
            "PASS_CANDIDATE_PERSISTED_AWAITING_MAPPED_VIEW_REVIEW"
            if passed and not failures
            else "FAIL_CANDIDATE_PERSISTENCE"
        ),
        "build_id": contract["build_id"],
        "candidate_root": contract["unreal"]["candidate_root"],
        "candidate_asset_count": len(candidate_assets),
        "mesh_results": mesh_results,
        "texture_results": texture_results,
        "checks": checks,
        "failures": failures,
        "runtime_map_changed": False,
        "config_changed": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    VERIFY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    VERIFY_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("[M01Grouped008] " + report["gate"])
    if not report["gate"].startswith("PASS_"):
        raise RuntimeError("Build 008 candidate persistence failed")


if __name__ == "__main__":
    main()
