"""Capture the deterministic one-process Attempt03 exposure sweep.

The script requires a separately authorized full UnrealEditor D3D12/SM6 run.
It loads the isolated Attempt03 review map and exports all 63 combinations of
seven manual exposure biases and nine contracted views. No package is saved.
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
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
EXPECTED_RHI = "D3D12|SM6"
TRANSIENT_PREFIX = "M01C008A03_Transient_"


def fail(message: str) -> None:
    raise RuntimeError("[M01Grouped008Attempt03Capture] " + message)


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
        fail("missing required -" + name + " switch")
    return match.group(1) or match.group(2)


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))


def hash_tree(root: Path) -> dict[str, str]:
    records = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".uasset", ".umap"}:
            records[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    return records


def require_d3d12_sm6() -> str:
    validation = (
        unreal.SkyguardMission01EnvironmentAuthoringLibrary
        .get_active_rhi_and_feature_level()
        .strip()
        .upper()
    )
    if validation != EXPECTED_RHI:
        fail(f"required D3D12|SM6, got {validation!r}")
    unreal.log("[M01Grouped008Attempt03Capture][RHI_VALIDATED] " + validation)
    return validation


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        fail("invalid PNG: " + str(path))
    return struct.unpack(">II", header[16:24])


def find_actors(contract: dict) -> dict[str, list]:
    expected = {
        "M01C008A03_" + record["key"].replace("/", "_"): record
        for record in contract["assembly"]["actors"]
    }
    actual = {}
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        label = actor.get_actor_label()
        if label.startswith("M01C008A03_") and not label.startswith(TRANSIENT_PREFIX):
            actual[label] = actor
    if set(actual) != set(expected):
        fail("Attempt03 review actor labels differ from exact contract")
    tolerance = float(contract["assembly"]["location_tolerance_cm"])
    grouped = {family: [] for family in contract["exposure_sweep"]["families"]}
    for label, actor in actual.items():
        record = expected[label]
        location = actor.get_actor_location()
        current = [float(location.x), float(location.y), float(location.z)]
        if any(
            abs(current[index] - float(record["actor_location_cm"][index])) > tolerance
            for index in range(3)
        ):
            fail("Attempt03 actor transform differs from contract: " + record["key"])
        family = record["key"].split("/", 1)[0]
        grouped[family].append(actor)
    if any(len(grouped[family]) != 4 for family in grouped):
        fail("Attempt03 family actor count mismatch")
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


def get_light_component(actor, *names):
    for name in names:
        cls = getattr(unreal, name, None)
        if cls:
            component = actor.get_component_by_class(cls)
            if component:
                return component
    return None


def set_light(component, intensity: float) -> None:
    if not component:
        fail("transient light component unavailable")
    try:
        component.set_intensity(intensity)
    except Exception:
        component.set_editor_property("intensity", intensity)
    try:
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
    except Exception:
        pass


def spawn_lighting(contract: dict) -> list:
    lighting = contract["exposure_sweep"]["lighting"]
    transient = []
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
        unreal.SkyLight, unreal.Vector(3000.0, 0.0, 3000.0), unreal.Rotator()
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
        if not actor:
            fail("could not spawn transient " + suffix)
        actor.set_actor_label(TRANSIENT_PREFIX + suffix)
        transient.append(actor)
    set_light(
        get_light_component(sun, "DirectionalLightComponent", "LightComponent"),
        float(lighting["key_directional_lux"]),
    )
    set_light(
        get_light_component(fill, "DirectionalLightComponent", "LightComponent"),
        float(lighting["fill_directional_lux"]),
    )
    set_light(
        get_light_component(sky, "SkyLightComponent", "LightComponent"),
        float(lighting["skylight_intensity"]),
    )
    try:
        get_light_component(
            sun, "DirectionalLightComponent", "LightComponent"
        ).set_editor_property("atmosphere_sun_light", True)
    except Exception:
        pass
    return transient


def make_capture_component(resolution: list[int]):
    world = unreal.EditorLevelLibrary.get_editor_world()
    target = unreal.RenderingLibrary.create_render_target2d(
        world,
        int(resolution[0]),
        int(resolution[1]),
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
    )
    capture = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
    )
    if not target or not capture:
        fail("could not create transient capture resources")
    capture.set_actor_label(TRANSIENT_PREFIX + "SceneCapture")
    component = capture.capture_component2d
    component.set_editor_property("texture_target", target)
    component.set_editor_property(
        "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
    )
    component.set_editor_property("capture_every_frame", False)
    component.set_editor_property("capture_on_movement", False)
    component.set_editor_property("fov_angle", 45.0)
    component.set_editor_property("post_process_blend_weight", 1.0)
    return capture, component, target


def set_manual_exposure(component, bias_ev: float) -> None:
    settings = component.get_editor_property("post_process_settings")
    settings.set_editor_property("override_auto_exposure_method", True)
    settings.set_editor_property(
        "auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL
    )
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", float(bias_ev))
    component.set_editor_property("post_process_settings", settings)


def camera_location(origin: unreal.Vector, extent: unreal.Vector, view: str) -> unreal.Vector:
    radius = max(extent.x, extent.y, extent.z, 100.0)
    distance = radius * 2.7
    if view == "three_quarter":
        return origin + unreal.Vector(-distance * 0.72, -distance * 0.72, distance * 0.32)
    if view == "grazing_port":
        return origin + unreal.Vector(0.0, -distance, distance * 0.10)
    if view == "grazing_starboard":
        return origin + unreal.Vector(0.0, distance, distance * 0.10)
    fail("unknown view " + view)
    return origin


def ev_token(value: int) -> str:
    return ("m" + str(abs(value))) if value < 0 else ("p" + str(value))


def main() -> None:
    contract = load_contract()
    output = Path(parse_switch("SkyguardAttempt03SweepOutput"))
    requested_map = parse_switch("SkyguardAttempt03ReviewMap")
    expected_map = contract["candidate"]["attempt03_review_map"]
    if requested_map != expected_map:
        fail("review map switch differs from contract")
    if output.exists():
        fail("immutable sweep output already exists")
    output.mkdir(parents=True, exist_ok=False)
    original_root = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
    attempt03_root = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
    original_before = hash_tree(original_root)
    attempt03_before = hash_tree(attempt03_root)
    rhi = require_d3d12_sm6()
    if not unreal.EditorLevelLibrary.load_level(expected_map):
        fail("could not load Attempt03 review map")
    grouped = find_actors(contract)
    bounds = {family: combined_bounds(actors) for family, actors in grouped.items()}
    transient = spawn_lighting(contract)
    capture, component, target = make_capture_component(
        contract["exposure_sweep"]["capture_resolution"]
    )
    transient.append(capture)
    all_candidate = [actor for actors in grouped.values() for actor in actors]
    records = []
    try:
        for bias in contract["exposure_sweep"]["manual_exposure_bias_candidates_ev"]:
            set_manual_exposure(component, float(bias))
            for family in contract["exposure_sweep"]["families"]:
                for actor in all_candidate:
                    actor.set_actor_hidden_in_game(actor not in grouped[family])
                origin, extent = bounds[family]
                for view in contract["exposure_sweep"]["views_per_family"]:
                    location = camera_location(origin, extent, view)
                    rotation = unreal.MathLibrary.find_look_at_rotation(location, origin)
                    capture.set_actor_location(location, False, False)
                    capture.set_actor_rotation(rotation, False)
                    for _ in range(3):
                        component.capture_scene()
                    filename = (
                        f"Pilot_EV_{ev_token(int(bias))}_{family}_{view}_008.png"
                    )
                    unreal.RenderingLibrary.export_render_target(
                        unreal.EditorLevelLibrary.get_editor_world(),
                        target,
                        str(output),
                        filename,
                    )
                    path = output / filename
                    if not path.is_file() or path.stat().st_size < 25000:
                        fail("pilot capture missing or implausibly small: " + str(path))
                    dimensions = png_dimensions(path)
                    if list(dimensions) != contract["exposure_sweep"]["capture_resolution"]:
                        fail("pilot capture dimensions differ from contract")
                    records.append(
                        {
                            "exposure_bias_ev": bias,
                            "family": family,
                            "view": view,
                            "path": str(path),
                            "bytes": path.stat().st_size,
                            "sha256": sha256_file(path),
                            "dimensions": list(dimensions),
                        }
                    )
    finally:
        for actor in all_candidate:
            actor.set_actor_hidden_in_game(False)
        for actor in reversed(transient):
            try:
                unreal.EditorLevelLibrary.destroy_actor(actor)
            except Exception:
                pass
    if len(records) != contract["exposure_sweep"]["pilot_capture_count"]:
        fail("pilot capture count differs from contract")
    original_after = hash_tree(original_root)
    attempt03_after = hash_tree(attempt03_root)
    if original_before != original_after or attempt03_before != attempt03_after:
        fail("candidate package hashes changed during read-only sweep")
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-sweep.v1",
        "gate": "PASS_ATTEMPT03_SWEEP_AWAITING_OFFLINE_GLOBAL_EV_SELECTION",
        "build_id": contract["build_id"],
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "review_map": expected_map,
        "rhi_validation": rhi,
        "capture_resolution": contract["exposure_sweep"]["capture_resolution"],
        "capture_count": len(records),
        "captures": records,
        "original_candidate_packages_unchanged": True,
        "attempt03_packages_unchanged": True,
        "world_saved": False,
        "package_save_invoked": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    manifest = output / "capture_manifest.json"
    manifest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("[M01Grouped008Attempt03Capture] " + report["gate"])


if __name__ == "__main__":
    main()
