"""Synchronized pilot-gated Recovery02 capture in one Unreal process."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
BASE_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY02_CONTRACT.json"
BASE_CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
ORIGINAL_CANDIDATE = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
ATTEMPT03_CONTENT = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
RUNTIME_MAPS = ROOT / "Content/Skyguard/Maps"
CONFIG = ROOT / "Config"
TRANSIENT_PREFIX = "M01C008A03R02_Transient_"


def fail(message: str) -> None:
    raise RuntimeError("[M01Grouped008Attempt03Recovery02Capture] " + message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail("could not load base capture helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("skyguard_attempt03_capture_helpers_r02", BASE_CAPTURE_PATH)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_tree(root: Path, suffixes: set[str] | None = None) -> dict[str, str]:
    records: dict[str, str] = {}
    if not root.exists():
        return records
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if suffixes and path.suffix.lower() not in suffixes:
            continue
        records[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    return records


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def mark_render_state_dirty(component) -> None:
    try:
        component.mark_render_state_dirty()
    except Exception:
        pass


def spawn_rig(rig: dict, label: str) -> tuple[list, tuple]:
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
            fail("could not spawn synchronized rig actor " + suffix)
        actor.set_actor_label(TRANSIENT_PREFIX + label + "_" + suffix)
        transient.append(actor)
    components = (
        BASE.get_light_component(
            sun, "DirectionalLightComponent", "LightComponent"
        ),
        BASE.get_light_component(
            fill, "DirectionalLightComponent", "LightComponent"
        ),
        BASE.get_light_component(sky, "SkyLightComponent", "LightComponent"),
    )
    BASE.set_light(components[0], float(rig["key_lux"]))
    BASE.set_light(components[1], float(rig["fill_lux"]))
    BASE.set_light(components[2], float(rig["skylight"]))
    for component in components:
        mark_render_state_dirty(component)
    try:
        components[0].set_editor_property("atmosphere_sun_light", True)
    except Exception:
        pass
    try:
        components[2].recapture_sky()
    except Exception:
        pass
    return transient, components


def destroy_actors(actors: list) -> None:
    for actor in reversed(actors):
        try:
            unreal.EditorLevelLibrary.destroy_actor(actor)
        except Exception:
            pass


def configure_capture(component, target, exposure_bias: float) -> None:
    component.set_editor_property("texture_target", target)
    component.set_editor_property(
        "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
    )
    component.set_editor_property("capture_every_frame", False)
    component.set_editor_property("capture_on_movement", False)
    component.set_editor_property("fov_angle", 45.0)
    component.set_editor_property("post_process_blend_weight", 1.0)
    try:
        component.set_editor_property("always_persist_rendering_state", False)
    except Exception:
        pass
    BASE.set_manual_exposure(component, exposure_bias)
    mark_render_state_dirty(component)


def capture_fresh_frame(
    world,
    output: Path,
    filename: str,
    location,
    rotation,
    resolution: list[int],
    exposure_bias: float,
    capture_calls: int,
    sentinel: list[float],
) -> Path:
    target = unreal.RenderingLibrary.create_render_target2d(
        world,
        int(resolution[0]),
        int(resolution[1]),
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
    )
    if not target:
        fail("could not create fresh render target")
    unreal.RenderingLibrary.clear_render_target2d(
        world,
        target,
        unreal.LinearColor(*[float(value) for value in sentinel]),
    )
    capture = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SceneCapture2D, location, rotation
    )
    if not capture:
        fail("could not create fresh SceneCapture2D")
    capture.set_actor_label(TRANSIENT_PREFIX + "Frame_" + filename[:-4])
    component = capture.capture_component2d
    configure_capture(component, target, exposure_bias)
    capture.set_actor_location(location, False, False)
    capture.set_actor_rotation(rotation, False)
    mark_render_state_dirty(component)
    for _ in range(capture_calls):
        component.capture_scene()
    unreal.RenderingLibrary.export_render_target(
        world, target, str(output), filename
    )
    path = output / filename
    try:
        unreal.EditorLevelLibrary.destroy_actor(capture)
    except Exception:
        pass
    if not path.is_file() or path.stat().st_size < 25000:
        fail("fresh synchronized capture missing or implausibly small: " + str(path))
    if list(BASE.png_dimensions(path)) != resolution:
        fail("fresh synchronized capture dimensions differ from contract")
    return path


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png_rgb(path: Path) -> tuple[int, int, list[tuple[int, int, int]]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("pilot is not a PNG")
    position = 8
    width = height = bit_depth = color_type = None
    compressed = bytearray()
    while position < len(data):
        length = struct.unpack(">I", data[position : position + 4])[0]
        kind = data[position + 4 : position + 8]
        payload = data[position + 8 : position + 8 + length]
        position += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(
                ">IIBB", payload[:10]
            )
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    if bit_depth != 8 or color_type not in (2, 6):
        fail(f"unsupported pilot PNG format depth={bit_depth} type={color_type}")
    channels = 3 if color_type == 2 else 4
    raw = zlib.decompress(bytes(compressed))
    stride = int(width) * channels
    previous = bytearray(stride)
    pixels: list[tuple[int, int, int]] = []
    offset = 0
    for _ in range(int(height)):
        filter_type = raw[offset]
        offset += 1
        source = raw[offset : offset + stride]
        offset += stride
        current = bytearray(stride)
        for index, value in enumerate(source):
            left = current[index - channels] if index >= channels else 0
            up = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                decoded = value
            elif filter_type == 1:
                decoded = value + left
            elif filter_type == 2:
                decoded = value + up
            elif filter_type == 3:
                decoded = value + ((left + up) // 2)
            elif filter_type == 4:
                decoded = value + paeth(left, up, upper_left)
            else:
                fail("unsupported PNG filter in pilot")
            current[index] = decoded & 0xFF
        for index in range(0, stride, channels):
            pixels.append((current[index], current[index + 1], current[index + 2]))
        previous = current
    return int(width), int(height), pixels


def pilot_metrics(path: Path, threshold: int) -> dict:
    width, height, pixels = decode_png_rgb(path)
    active = 0
    sentinel = 0
    maximum = 0
    colors: set[tuple[int, int, int]] = set()
    for red, green, blue in pixels:
        luma = (54 * red + 183 * green + 19 * blue) // 256
        if luma > threshold:
            active += 1
        if red >= 250 and green <= 5 and blue >= 250:
            sentinel += 1
        maximum = max(maximum, red, green, blue)
        if len(colors) < 4096:
            colors.add((red, green, blue))
    total = width * height
    return {
        "dimensions": [width, height],
        "active_pixel_fraction": round(active / total, 8),
        "maximum_channel_value": maximum,
        "unique_color_count_capped_at_4096": len(colors),
        "sentinel_magenta_fraction": round(sentinel / total, 8),
    }


def main() -> None:
    base_contract = load_json(BASE_CONTRACT_PATH)
    contract = load_json(CONTRACT_PATH)
    output = Path(BASE.parse_switch("SkyguardAttempt03Recovery02Output"))
    requested_map = BASE.parse_switch("SkyguardAttempt03Recovery02ReviewMap")
    if requested_map != contract["review_map"]:
        fail("review map switch differs from Recovery02 contract")
    if output.exists():
        fail("immutable Recovery02 output already exists")
    output.mkdir(parents=True, exist_ok=False)
    pilot_output = output / "pilot"
    sweep_output = output / "sweep"
    pilot_output.mkdir()

    before = {
        "original": hash_tree(ORIGINAL_CANDIDATE, {".uasset", ".umap"}),
        "attempt03": hash_tree(ATTEMPT03_CONTENT, {".uasset", ".umap"}),
        "runtime": hash_tree(RUNTIME_MAPS, {".uasset", ".umap"}),
        "config": hash_tree(CONFIG),
    }
    rhi = BASE.require_d3d12_sm6()
    if not unreal.EditorLevelLibrary.load_level(contract["review_map"]):
        fail("could not load immutable Attempt03 review map")
    grouped = BASE.find_actors(base_contract)
    bounds = {
        family: BASE.combined_bounds(actors) for family, actors in grouped.items()
    }
    all_candidate = [actor for actors in grouped.values() for actor in actors]
    world = unreal.EditorLevelLibrary.get_editor_world()
    pilot_records = []
    pilot_rig = contract["pilot"]["rig"]
    pilot_actors, _ = spawn_rig(pilot_rig, "Pilot")
    try:
        for pair in contract["pilot"]["family_view_pairs"]:
            family = pair["family"]
            view = pair["view"]
            for actor in all_candidate:
                actor.set_actor_hidden_in_game(actor not in grouped[family])
            origin, extent = bounds[family]
            location = BASE.camera_location(origin, extent, view)
            rotation = unreal.MathLibrary.find_look_at_rotation(location, origin)
            filename = f"Pilot_{family}_{view}_Recovery02.png"
            path = capture_fresh_frame(
                world,
                pilot_output,
                filename,
                location,
                rotation,
                contract["capture"]["resolution"],
                float(pilot_rig["manual_exposure_bias_ev"]),
                int(contract["capture"]["immediate_capture_scene_calls_per_frame"]),
                contract["pilot"]["sentinel_clear_rgba"],
            )
            pilot_records.append(
                {
                    "family": family,
                    "view": view,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "metrics": pilot_metrics(
                        path,
                        int(contract["selector"]["active_pixel_threshold_luma"]),
                    ),
                }
            )
    finally:
        destroy_actors(pilot_actors)
        for actor in all_candidate:
            actor.set_actor_hidden_in_game(False)
    bounds_policy = contract["pilot"]["hard_liveness_bounds"]
    pilot_pass = (
        len(pilot_records) == contract["pilot"]["capture_count"]
        and len({record["sha256"] for record in pilot_records})
        == bounds_policy["unique_png_hash_count"]
        and all(
            record["metrics"]["active_pixel_fraction"]
            >= bounds_policy["minimum_active_pixel_fraction_luma_gt_8"]
            and record["metrics"]["maximum_channel_value"]
            >= bounds_policy["minimum_max_channel_value"]
            and record["metrics"]["unique_color_count_capped_at_4096"]
            >= bounds_policy["minimum_unique_color_count"]
            and record["metrics"]["sentinel_magenta_fraction"]
            <= bounds_policy["maximum_sentinel_magenta_fraction"]
            for record in pilot_records
        )
    )
    pilot_receipt = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery02-pilot.v1",
        "gate": (
            "PASS_RECOVERY02_PILOT_LIVE_FULL_SWEEP_ALLOWED"
            if pilot_pass
            else "FAIL_CLOSED_RECOVERY02_PILOT_BLANK_STALE_OR_SENTINEL"
        ),
        "rhi_validation": rhi,
        "captures": pilot_records,
        "capture_count": len(pilot_records),
        "unique_png_hash_count": len(
            {record["sha256"] for record in pilot_records}
        ),
        "full_sweep_allowed": pilot_pass,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    pilot_receipt_path = output / "pilot_receipt.json"
    pilot_receipt_path.write_text(
        json.dumps(pilot_receipt, indent=2) + "\n", encoding="utf-8"
    )
    if not pilot_pass:
        fail("pilot liveness proof failed; full sweep was not started")

    sweep_output.mkdir()
    records = []
    for rig in contract["capture"]["rig_candidates"]:
        rig_actors, components = spawn_rig(rig, rig["rig_id"])
        try:
            for component in components:
                mark_render_state_dirty(component)
            for family in contract["capture"]["families"]:
                for actor in all_candidate:
                    actor.set_actor_hidden_in_game(actor not in grouped[family])
                origin, extent = bounds[family]
                for view in contract["capture"]["views_per_family"]:
                    location = BASE.camera_location(origin, extent, view)
                    rotation = unreal.MathLibrary.find_look_at_rotation(
                        location, origin
                    )
                    filename = (
                        f"Rig_{rig['rig_id']}_{family}_{view}_008_"
                        "Attempt03_Recovery02.png"
                    )
                    path = capture_fresh_frame(
                        world,
                        sweep_output,
                        filename,
                        location,
                        rotation,
                        contract["capture"]["resolution"],
                        float(contract["capture"]["fixed_manual_exposure_bias_ev"]),
                        int(
                            contract["capture"][
                                "immediate_capture_scene_calls_per_frame"
                            ]
                        ),
                        contract["pilot"]["sentinel_clear_rgba"],
                    )
                    records.append(
                        {
                            "rig_id": rig["rig_id"],
                            "rig_index": rig["rig_index"],
                            "key_lux": rig["key_lux"],
                            "fill_lux": rig["fill_lux"],
                            "skylight": rig["skylight"],
                            "fixed_manual_exposure_bias_ev": contract["capture"][
                                "fixed_manual_exposure_bias_ev"
                            ],
                            "family": family,
                            "view": view,
                            "path": str(path),
                            "bytes": path.stat().st_size,
                            "sha256": sha256_file(path),
                            "dimensions": list(BASE.png_dimensions(path)),
                        }
                    )
        finally:
            destroy_actors(rig_actors)
            for actor in all_candidate:
                actor.set_actor_hidden_in_game(False)
    if len(records) != contract["capture"]["full_sweep_capture_count"]:
        fail("Recovery02 full sweep count differs from contract")
    after = {
        "original": hash_tree(ORIGINAL_CANDIDATE, {".uasset", ".umap"}),
        "attempt03": hash_tree(ATTEMPT03_CONTENT, {".uasset", ".umap"}),
        "runtime": hash_tree(RUNTIME_MAPS, {".uasset", ".umap"}),
        "config": hash_tree(CONFIG),
    }
    if before != after:
        fail("Recovery02 changed a package, runtime map, or Config file")
    manifest = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery02-sweep.v1",
        "gate": "PASS_RECOVERY02_SYNCHRONIZED_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION",
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "review_map": contract["review_map"],
        "rhi_validation": rhi,
        "pilot_receipt": str(pilot_receipt_path),
        "pilot_receipt_sha256": sha256_file(pilot_receipt_path),
        "pilot_gate": pilot_receipt["gate"],
        "capture_resolution": contract["capture"]["resolution"],
        "capture_count": len(records),
        "captures": records,
        "fresh_scene_capture_actor_per_frame": True,
        "fresh_render_target_per_frame": True,
        "sentinel_clear_before_capture": True,
        "original_candidate_packages_unchanged": True,
        "attempt03_packages_unchanged": True,
        "runtime_maps_unchanged": True,
        "config_unchanged": True,
        "world_saved": False,
        "package_save_invoked": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    manifest_path = output / "capture_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log(
        "[M01Grouped008Attempt03Recovery02Capture] "
        "PASS_RECOVERY02_SYNCHRONIZED_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION"
    )


if __name__ == "__main__":
    main()
