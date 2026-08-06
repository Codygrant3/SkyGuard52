"""Capture the nine governed Unreal mapped-mesh review views for Build 008.

This script is read-only with respect to Unreal packages. It loads the isolated
candidate review map, creates transient lighting, floors, and SceneCapture2D
actors, exports nine 2048px PNGs, and proves every candidate package hash is
unchanged before exit.

Required command-line switches:
  -SkyguardMappedViewMap=/Game/...
  -SkyguardMappedViewOutput=D:/.../mapped_view_capture_01
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
from datetime import datetime, timezone
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_ACCEPTANCE_008_CONTRACT.json"
PERSISTENCE_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_CANDIDATE_008_PERSISTENCE.json"
CANDIDATE_FILES_ROOT = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
REFERENCE_ROOT = ROOT / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_008/attempt_20260802T161843676Z/mapped_mesh_review_attempt_02/previews"
EXPECTED_RHI = "D3D12|SM6"
EXPECTED_PERSISTENCE_SHA256 = "2bd9bbaf4750d57d3a3b9ca92dde14995a5b84d4332294a2ce61bfd690d8f185"
EXPECTED_BUILD_ID = "BLD_M01_HERO_GROUPED_TOPOLOGY_008"
RESOLUTION = (2048, 2048)
FAMILIES = ("Pathfinder", "Lighthouse", "RadarPost")
VIEWS = ("three_quarter", "grazing_port", "grazing_starboard")
TRANSIENT_PREFIX = "M01C008_TransientReview_"


def fail(message: str) -> None:
    raise RuntimeError("[M01Grouped008Capture] " + message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_switch(name: str) -> str:
    command_line = unreal.SystemLibrary.get_command_line()
    match = re.search(
        rf'(?:^|\s)-{re.escape(name)}=(?:"([^"]+)"|(\S+))',
        command_line,
        re.IGNORECASE,
    )
    if not match:
        fail("missing required -" + name + " command-line switch")
    return match.group(1) or match.group(2)


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        fail("capture is not a valid PNG: " + str(path))
    return struct.unpack(">II", header[16:24])


def hash_candidate_packages() -> dict[str, str]:
    if not CANDIDATE_FILES_ROOT.is_dir():
        fail("candidate package directory is missing")
    records = {}
    for path in sorted(CANDIDATE_FILES_ROOT.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".uasset", ".umap"}:
            records[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    if len(records) != 49:
        fail(f"expected 49 candidate packages, found {len(records)}")
    return records


def require_bound_state() -> tuple[dict, dict]:
    if sha256_file(PERSISTENCE_PATH) != EXPECTED_PERSISTENCE_SHA256:
        fail("persistence report hash does not match the accepted fresh verifier")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    persistence = json.loads(PERSISTENCE_PATH.read_text(encoding="utf-8-sig"))
    if contract.get("build_id") != EXPECTED_BUILD_ID:
        fail("contract build id mismatch")
    if persistence.get("build_id") != EXPECTED_BUILD_ID:
        fail("persistence build id mismatch")
    if persistence.get("gate") != "PASS_CANDIDATE_PERSISTED_AWAITING_MAPPED_VIEW_REVIEW":
        fail("fresh persistence gate is not the required PASS state")
    if persistence.get("promotion_allowed") is not False:
        fail("persistence report unexpectedly allows promotion")
    if persistence.get("p3_4_closed") is not False:
        fail("persistence report unexpectedly closes P3.4")
    if persistence.get("failures"):
        fail("persistence report contains failures")
    return contract, persistence


def require_d3d12_sm6() -> str:
    validation = (
        unreal.SkyguardMission01EnvironmentAuthoringLibrary
        .get_active_rhi_and_feature_level()
        .strip()
        .upper()
    )
    if validation != EXPECTED_RHI:
        fail(f"governed capture requires D3D12|SM6, got {validation!r}")
    unreal.log("[M01Grouped008Capture][RHI_VALIDATED] " + validation)
    return validation


def actor_family(actor) -> str | None:
    label = actor.get_actor_label()
    for family in FAMILIES:
        if label.startswith("M01C008_" + family + "_"):
            return family
    return None


def find_candidate_actors() -> dict[str, list]:
    grouped = {family: [] for family in FAMILIES}
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        family = actor_family(actor)
        if family:
            grouped[family].append(actor)
    counts = {family: len(actors) for family, actors in grouped.items()}
    expected = {"Pathfinder": 4, "Lighthouse": 4, "RadarPost": 4}
    if counts != expected:
        fail(f"review map actor set mismatch: {counts!r}")
    return grouped


def combined_bounds(actors: list) -> tuple[unreal.Vector, unreal.Vector]:
    minimum = unreal.Vector(float("inf"), float("inf"), float("inf"))
    maximum = unreal.Vector(float("-inf"), float("-inf"), float("-inf"))
    for actor in actors:
        origin, extent = actor.get_actor_bounds(False, True)
        minimum.x = min(minimum.x, origin.x - extent.x)
        minimum.y = min(minimum.y, origin.y - extent.y)
        minimum.z = min(minimum.z, origin.z - extent.z)
        maximum.x = max(maximum.x, origin.x + extent.x)
        maximum.y = max(maximum.y, origin.y + extent.y)
        maximum.z = max(maximum.z, origin.z + extent.z)
    return (minimum + maximum) * 0.5, (maximum - minimum) * 0.5


def get_component(actor, *class_names):
    for class_name in class_names:
        cls = getattr(unreal, class_name, None)
        if cls:
            component = actor.get_component_by_class(cls)
            if component:
                return component
    for property_name in (
        "light_component",
        "directional_light_component",
        "sky_light_component",
    ):
        try:
            component = actor.get_editor_property(property_name)
            if component:
                return component
        except Exception:
            pass
    return None


def configure_light(component, intensity: float) -> None:
    if not component:
        fail("transient light component is unavailable")
    try:
        component.set_intensity(intensity)
    except Exception:
        component.set_editor_property("intensity", intensity)
    try:
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
    except Exception:
        pass


def spawn_transient_environment(grouped: dict[str, list]) -> tuple[list, dict, dict]:
    transient = []
    origins = {}
    extents = {}
    for family, actors in grouped.items():
        origins[family], extents[family] = combined_bounds(actors)

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(3000.0, -2500.0, 7000.0),
        unreal.Rotator(-38.0, 42.0, 0.0),
    )
    fill = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(3000.0, 2500.0, 5000.0),
        unreal.Rotator(-18.0, -142.0, 0.0),
    )
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyLight,
        unreal.Vector(3000.0, 0.0, 3000.0),
        unreal.Rotator(),
    )
    atmosphere = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SkyAtmosphere, unreal.Vector(), unreal.Rotator()
    )
    for actor, suffix in (
        (sun, "KeySun"),
        (fill, "FillSun"),
        (sky, "SkyLight"),
        (atmosphere, "SkyAtmosphere"),
    ):
        if actor:
            actor.set_actor_label(TRANSIENT_PREFIX + suffix)
            transient.append(actor)
    if not sun or not fill or not sky:
        fail("could not spawn the required transient lighting")
    configure_light(
        get_component(sun, "DirectionalLightComponent", "LightComponent"),
        100000.0,
    )
    configure_light(
        get_component(fill, "DirectionalLightComponent", "LightComponent"),
        12000.0,
    )
    configure_light(get_component(sky, "SkyLightComponent", "LightComponent"), 2.25)
    try:
        get_component(sun, "DirectionalLightComponent", "LightComponent").set_editor_property(
            "atmosphere_sun_light", True
        )
    except Exception:
        pass
    try:
        sky_component = get_component(sky, "SkyLightComponent", "LightComponent")
        sky_component.set_editor_property("real_time_capture", True)
    except Exception:
        pass

    post_process = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PostProcessVolume,
        unreal.Vector(3000.0, 0.0, 1000.0),
        unreal.Rotator(),
    )
    if not post_process:
        fail("could not spawn transient review post-process volume")
    post_process.set_actor_label(TRANSIENT_PREFIX + "PostProcess")
    post_process.set_editor_property("unbound", True)
    settings = post_process.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_method", True)
    settings.set_editor_property(
        "auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL
    )
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 1.0)
    transient.append(post_process)

    cube = unreal.load_asset("/Engine/BasicShapes/Cube")
    if not cube:
        fail("Engine cube mesh is unavailable for transient review floors")
    for family in FAMILIES:
        origin = origins[family]
        extent = extents[family]
        floor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(origin.x, origin.y, origin.z - extent.z - 12.0),
            unreal.Rotator(),
        )
        if not floor:
            fail("could not spawn transient review floor for " + family)
        floor.set_actor_label(TRANSIENT_PREFIX + family + "_Floor")
        floor.static_mesh_component.set_static_mesh(cube)
        floor.set_actor_scale3d(
            unreal.Vector(
                max(extent.x * 3.5 / 100.0, 8.0),
                max(extent.y * 3.5 / 100.0, 8.0),
                0.12,
            )
        )
        transient.append(floor)
    return transient, origins, extents


def make_render_target():
    world = unreal.EditorLevelLibrary.get_editor_world()
    target = unreal.RenderingLibrary.create_render_target2d(
        world,
        RESOLUTION[0],
        RESOLUTION[1],
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
    )
    if target is None:
        fail("could not create transient review render target")
    target.set_editor_property("clear_color", unreal.LinearColor(0.04, 0.05, 0.07, 1.0))
    return target


def camera_location(origin: unreal.Vector, extent: unreal.Vector, view: str) -> unreal.Vector:
    radius = max(extent.x, extent.y, extent.z, 100.0)
    distance = radius * 3.4
    if view == "three_quarter":
        return origin + unreal.Vector(-distance * 0.72, -distance * 0.72, distance * 0.38)
    if view == "grazing_port":
        return origin + unreal.Vector(0.0, -distance, distance * 0.12)
    if view == "grazing_starboard":
        return origin + unreal.Vector(0.0, distance, distance * 0.12)
    fail("unknown view " + view)
    return origin


def reference_path(family: str, view: str) -> Path:
    path = REFERENCE_ROOT / f"{family}_{view}_008.png"
    if not path.is_file():
        fail("bound Blender reference is missing: " + str(path))
    return path


def capture_views(output_dir: Path, grouped: dict, transient: list, origins: dict, extents: dict) -> list[dict]:
    world = unreal.EditorLevelLibrary.get_editor_world()
    target = make_render_target()
    capture = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
    )
    if not capture:
        fail("could not spawn transient SceneCapture2D")
    capture.set_actor_label(TRANSIENT_PREFIX + "SceneCapture")
    transient.append(capture)
    component = capture.capture_component2d
    component.set_editor_property("texture_target", target)
    component.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    component.set_editor_property("capture_every_frame", False)
    component.set_editor_property("capture_on_movement", False)
    component.set_editor_property("fov_angle", 45.0)

    records = []
    all_candidate_actors = [actor for actors in grouped.values() for actor in actors]
    for family in FAMILIES:
        for actor in all_candidate_actors:
            actor.set_actor_hidden_in_game(actor not in grouped[family])
        for actor in transient:
            label = actor.get_actor_label()
            if label.endswith("_Floor"):
                actor.set_actor_hidden_in_game(label != TRANSIENT_PREFIX + family + "_Floor")
        for view in VIEWS:
            location = camera_location(origins[family], extents[family], view)
            target_point = origins[family] + unreal.Vector(0.0, 0.0, extents[family].z * 0.04)
            rotation = unreal.MathLibrary.find_look_at_rotation(location, target_point)
            capture.set_actor_location(location, False, False)
            capture.set_actor_rotation(rotation, False)
            for _ in range(3):
                component.capture_scene()
            filename = f"Unreal_{family}_{view}_008.png"
            unreal.RenderingLibrary.export_render_target(world, target, str(output_dir), filename)
            output = output_dir / filename
            if not output.is_file() or output.stat().st_size < 25_000:
                fail("capture missing or implausibly small: " + str(output))
            dimensions = png_dimensions(output)
            if dimensions != RESOLUTION:
                fail(f"capture dimensions mismatch for {filename}: {dimensions!r}")
            reference = reference_path(family, view)
            records.append(
                {
                    "family": family,
                    "view": view,
                    "path": str(output),
                    "bytes": output.stat().st_size,
                    "sha256": sha256_file(output),
                    "dimensions": list(dimensions),
                    "blender_reference_path": str(reference),
                    "blender_reference_sha256": sha256_file(reference),
                }
            )
    for actor in all_candidate_actors:
        actor.set_actor_hidden_in_game(False)
    return records


def main() -> None:
    contract, _persistence = require_bound_state()
    requested_map = parse_switch("SkyguardMappedViewMap")
    output_dir = Path(parse_switch("SkyguardMappedViewOutput"))
    expected_map = contract["unreal"]["review_map"]
    if requested_map != expected_map:
        fail("requested review map does not match the bound contract")
    if output_dir.exists():
        fail("capture output already exists; attempt outputs are immutable")
    output_dir.mkdir(parents=True, exist_ok=False)
    packages_before = hash_candidate_packages()
    rhi_validation = require_d3d12_sm6()
    if not unreal.EditorAssetLibrary.does_asset_exist(expected_map):
        fail("persisted review map asset is missing")
    if not unreal.EditorLevelLibrary.load_level(expected_map):
        fail("could not load persisted isolated review map")

    transient = []
    records = []
    try:
        grouped = find_candidate_actors()
        transient, origins, extents = spawn_transient_environment(grouped)
        records = capture_views(output_dir, grouped, transient, origins, extents)
    finally:
        for actor in reversed(transient):
            try:
                unreal.EditorLevelLibrary.destroy_actor(actor)
            except Exception:
                pass

    packages_after = hash_candidate_packages()
    if packages_before != packages_after:
        fail("candidate package hashes changed during read-only capture")
    if len(records) != 9:
        fail(f"expected nine governed captures, produced {len(records)}")

    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-capture.v1",
        "gate": "PASS_UNREAL_MAPPED_VIEW_CAPTURE_AWAITING_ORIGINAL_RESOLUTION_REVIEW",
        "build_id": EXPECTED_BUILD_ID,
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "review_map": expected_map,
        "resolution": list(RESOLUTION),
        "rhi_validation": rhi_validation,
        "candidate_package_count": len(packages_before),
        "candidate_packages_unchanged": True,
        "candidate_package_hashes_before": packages_before,
        "candidate_package_hashes_after": packages_after,
        "capture_count": len(records),
        "captures": records,
        "world_saved": False,
        "package_save_invoked": False,
        "runtime_map_changed": False,
        "config_changed": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    manifest = output_dir / "capture_manifest.json"
    manifest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("[M01Grouped008Capture] " + report["gate"])
    unreal.log("[M01Grouped008Capture] manifest_sha256=" + sha256_file(manifest))


if __name__ == "__main__":
    main()
