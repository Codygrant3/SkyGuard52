"""Build immutable M01 ProductionEnvironment_v5 with Landscape + PCG graph.

The native authoring bridge imports the governed height source and creates the
serialized graph. Licensed mesh slots remain empty and this script never calls
PCG generation.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
TARGET_MAP = (
    "/Game/Skyguard/Maps/"
    "Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03"
)
GRAPH_PATH = (
    "/Game/Skyguard/Environment/Mission01/PCG/"
    "PCG_M01_InlandVegetation"
)
HEIGHTMAP_PATH = (
    ROOT
    / "Content/Skyguard/Environment/Source/Mission01"
    / "HM_M01_CoastalProduction_505x127.r16"
)
HEIGHTMAP_MANIFEST = (
    ROOT / "Saved/Reports/PHASE4_M01_LANDSCAPE_SOURCE_MANIFEST.json"
)
ASSET_MANIFEST = (
    ROOT / "Saved/Reports/M01_WAVE1_AAA_REFINEMENT_MANIFEST.json"
)
REPORT_PATH = (
    ROOT / "Saved/Reports/PHASE4_M01_PCG_LANDSCAPE_BUILD.json"
)
PREFIX = "M01_P4_"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    for asset_path in (TARGET_MAP, GRAPH_PATH):
        if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            raise RuntimeError(
                "Immutable target already exists; verify it rather than overwrite: "
                + asset_path
            )
    if not HEIGHTMAP_PATH.is_file() or not HEIGHTMAP_MANIFEST.is_file():
        raise RuntimeError("Governed Landscape source or manifest is missing")
    source_manifest = json.loads(
        HEIGHTMAP_MANIFEST.read_text(encoding="utf-8-sig")
    )
    if (
        HEIGHTMAP_PATH.stat().st_size != 505 * 127 * 2
        or sha256_file(HEIGHTMAP_PATH) != source_manifest.get("sha256")
    ):
        raise RuntimeError("Governed Landscape source integrity failed")

    scripts_path = str(ROOT / "Scripts")
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    import build_skyguard_m01_wave1_refinement_validation as geometry
    import build_skyguard_phase4_m01_production_environment as base

    with ASSET_MANIFEST.open("r", encoding="utf-8") as stream:
        asset_manifest = json.load(stream)
    meshes, _ = geometry.collect_meshes()
    expected = {entry["name"] for entry in asset_manifest["assets"]}
    if set(meshes) != expected:
        raise RuntimeError("Imported refined mesh set differs from governed manifest")
    if not unreal.EditorLevelLibrary.new_level(TARGET_MAP):
        raise RuntimeError("Could not create immutable v5 map")

    placed = []
    for index, spec in enumerate(asset_manifest["placements"]):
        if str(spec["mission_role"]).startswith("boss_"):
            continue
        geometry.spawn_static(
            meshes[spec["asset"]],
            "%sRefined_%03d_%s" % (PREFIX, index, spec["asset"][:42]),
            spec["location_m"],
            spec["rotation_deg"],
            spec["scale"],
        )
        placed.append(spec["asset"])

    boss, bindings, required = geometry.spawn_and_bind_pathfinder(meshes)
    if boss is None or bindings != required:
        raise RuntimeError("Governed Pathfinder could not be bound")
    boss.set_actor_label(PREFIX + "Boss_Pathfinder")

    director_class = getattr(
        unreal, "SkyguardMission01EnvironmentDirector", None
    )
    if director_class is None:
        raise RuntimeError("Native Mission 1 environment director unavailable")
    director = unreal.EditorLevelLibrary.spawn_actor_from_class(
        director_class, unreal.Vector(), unreal.Rotator()
    )
    if director is None:
        raise RuntimeError("Native Mission 1 environment director did not spawn")
    director.set_actor_label(PREFIX + "ProductionEnvironmentDirector")
    director.rebuild_production_layout()

    authoring = getattr(
        unreal, "SkyguardMission01EnvironmentAuthoringLibrary", None
    )
    if authoring is None:
        raise RuntimeError("Native Phase 4 editor authoring bridge unavailable")
    authored = authoring.author_governed_landscape_and_graph(
        director,
        str(HEIGHTMAP_PATH),
        GRAPH_PATH,
    )
    if not bool(authored.success):
        raise RuntimeError(
            "Native Landscape/PCG authoring failed: " + str(authored.error)
        )

    atmosphere = base.spawn_actor(
        "/Script/Engine.SkyAtmosphere", PREFIX + "SkyAtmosphere"
    )
    cloud = base.spawn_actor(
        "/Script/Engine.VolumetricCloud", PREFIX + "VolumetricCloud"
    )
    fog = base.spawn_actor(
        "/Script/Engine.ExponentialHeightFog", PREFIX + "HeightFog"
    )
    wind = base.spawn_actor(
        "/Script/Engine.WindDirectionalSource",
        PREFIX + "WorldWind",
        rotation=(0.0, 35.0, 0.0),
    )
    sun = base.spawn_actor(
        "/Script/Engine.DirectionalLight",
        PREFIX + "Sun",
        location=(-4200.0, -5000.0, 7500.0),
        rotation=(-38.0, -32.0, 0.0),
    )
    skylight = base.spawn_actor(
        "/Script/Engine.SkyLight",
        PREFIX + "SkyFill",
        location=(0.0, 0.0, 3500.0),
    )
    for actor, tag in (
        (atmosphere, "Skyguard.Environment.Atmosphere"),
        (cloud, "Skyguard.Environment.Cloud"),
        (fog, "Skyguard.Environment.Fog"),
        (wind, "Skyguard.Environment.Wind"),
    ):
        if actor:
            base.add_tag(actor, tag)

    if fog:
        component = fog.get_component_by_class(
            unreal.ExponentialHeightFogComponent
        )
        if component:
            component.set_editor_property("fog_density", 0.012)
            component.set_editor_property("fog_height_falloff", 0.17)
    if sun:
        component = sun.get_component_by_class(
            unreal.DirectionalLightComponent
        )
        if component:
            component.set_editor_property("intensity", 4.5)
            component.set_editor_property("atmosphere_sun_light", True)
    if skylight:
        component = skylight.get_component_by_class(
            unreal.SkyLightComponent
        )
        if component:
            component.set_editor_property("intensity", 1.2)

    camera = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.CameraActor,
        unreal.Vector(-8200.0, -9800.0, 5200.0),
        unreal.Rotator(-17.0, 40.0, 0.0),
    )
    if camera:
        camera.set_actor_label(PREFIX + "ReviewCamera_Coast")

    # Persist graph first, then the referencing map. No generation is invoked.
    if not unreal.EditorAssetLibrary.save_asset(GRAPH_PATH, False):
        raise RuntimeError("Could not save governed PCG graph")
    unreal.EditorLevelLibrary.save_current_level()
    if not unreal.EditorAssetLibrary.save_asset(TARGET_MAP, False):
        raise RuntimeError("Could not save immutable v5 map")

    readiness = director.get_readiness()
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    revision = [
        actor
        for actor in actors
        if (actor.get_actor_label() or "").startswith(PREFIX)
    ]
    landscape = authored.landscape
    location = landscape.get_actor_location()
    scale = landscape.get_actor_scale3d()
    landscape_tags = [
        str(tag) for tag in list(landscape.get_editor_property("tags") or [])
    ]
    checks = {
        "immutable_v5_map_saved": unreal.EditorAssetLibrary.does_asset_exist(
            TARGET_MAP
        ),
        "governed_pcg_graph_saved": unreal.EditorAssetLibrary.does_asset_exist(
            GRAPH_PATH
        ),
        "governed_refined_assets_reused": len(placed) > 0,
        "pathfinder_bindings_complete": bindings == required,
        "landscape_components_8_by_2": int(
            authored.landscape_component_count
        )
        == 16,
        "landscape_transform_exact": (
            abs(location.x - 0.0) <= 0.01
            and abs(location.y - 7000.0) <= 0.01
            and abs(location.z - (-120.0)) <= 0.01
            and abs(scale.x - 100.0) <= 0.01
            and abs(scale.y - 100.0) <= 0.01
            and abs(scale.z - 100.0) <= 0.01
        ),
        "landscape_label_exact": (
            landscape.get_actor_label() == "M01_P4_Landscape_Production"
        ),
        "landscape_tag_exact": (
            "Skyguard.Environment.Mission01.Landscape" in landscape_tags
        ),
        "graph_topology_8_nodes_8_edges": (
            int(authored.graph_node_count) == 8
            and int(authored.graph_edge_count) == 8
        ),
        "director_structural_handoff_ready": bool(
            readiness.authored_pcg_structure_ready
        ),
        "licensed_mesh_slots_empty": bool(
            authored.licensed_mesh_slots_empty
        ),
        "generation_locked": bool(authored.generation_locked),
        "generation_not_authorized": not bool(
            readiness.ready_for_authored_pcg_generation
        ),
        "stable_atmosphere_stack": all(
            actor is not None
            for actor in (atmosphere, cloud, fog, wind, sun, skylight)
        ),
    }
    report = {
        "schema": "skyguard.phase4.m01-pcg-landscape-build.v1",
        "target_map": TARGET_MAP,
        "pcg_graph": GRAPH_PATH,
        "heightmap": {
            "path": str(HEIGHTMAP_PATH),
            "bytes": HEIGHTMAP_PATH.stat().st_size,
            "sha256": sha256_file(HEIGHTMAP_PATH),
            "width": 505,
            "height": 127,
        },
        "revision_actor_count": len(revision),
        "revision_actor_labels": sorted(
            actor.get_actor_label() for actor in revision
        ),
        "pcg_generation_invoked": False,
        "licensed_vegetation_slots": [],
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "promotion": {
            "serialized_p4_4_handoff_complete": all(checks.values()),
            "production_vegetation_complete": False,
            "visible_gpu_accepted": False,
            "aaa_accepted": False,
        },
        "limitations": [
            "Licensed vegetation slots are intentionally empty and generation remains locked.",
            "NullRHI cannot judge Landscape materials, silhouette, seams, vegetation, lighting, water, or GPU cost.",
            "No PCG generation or bake occurred in this authoring pass.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log("[SkyguardPhase4PCGLandscapeBuild] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Phase 4 M01 v5 authoring gate failed")


if __name__ == "__main__":
    main()
