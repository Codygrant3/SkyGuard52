"""Capture the immutable Attempt03 recovery_01 physical-light sweep."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
BASE_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
RECOVERY_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY01_CONTRACT.json"
BASE_CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
ORIGINAL_CANDIDATE = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
ATTEMPT03_CONTENT = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
RUNTIME_MAPS = ROOT / "Content/Skyguard/Maps"
CONFIG = ROOT / "Config"


def fail(message: str) -> None:
    raise RuntimeError("[M01Grouped008Attempt03Recovery01Capture] " + message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail("could not load base capture helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("skyguard_attempt03_capture_helpers", BASE_CAPTURE_PATH)


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


def spawn_rig() -> tuple[list, object, object, object]:
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
        actor.set_actor_label("M01C008A03R01_Transient_" + suffix)
        transient.append(actor)
    sun_component = BASE.get_light_component(
        sun, "DirectionalLightComponent", "LightComponent"
    )
    fill_component = BASE.get_light_component(
        fill, "DirectionalLightComponent", "LightComponent"
    )
    sky_component = BASE.get_light_component(
        sky, "SkyLightComponent", "LightComponent"
    )
    try:
        sun_component.set_editor_property("atmosphere_sun_light", True)
    except Exception:
        pass
    return transient, sun_component, fill_component, sky_component


def set_rig(components: tuple, rig: dict) -> None:
    sun_component, fill_component, sky_component = components
    BASE.set_light(sun_component, float(rig["key_lux"]))
    BASE.set_light(fill_component, float(rig["fill_lux"]))
    BASE.set_light(sky_component, float(rig["skylight"]))
    try:
        sky_component.recapture_sky()
    except Exception:
        pass


def main() -> None:
    base_contract = load_json(BASE_CONTRACT_PATH)
    recovery = load_json(RECOVERY_CONTRACT_PATH)
    output = Path(BASE.parse_switch("SkyguardAttempt03Recovery01Output"))
    requested_map = BASE.parse_switch("SkyguardAttempt03Recovery01ReviewMap")
    if requested_map != recovery["review_map"]:
        fail("review map switch differs from recovery contract")
    if output.exists():
        fail("immutable recovery_01 sweep output already exists")
    output.mkdir(parents=True, exist_ok=False)

    original_before = hash_tree(ORIGINAL_CANDIDATE, {".uasset", ".umap"})
    attempt03_before = hash_tree(ATTEMPT03_CONTENT, {".uasset", ".umap"})
    runtime_before = hash_tree(RUNTIME_MAPS, {".uasset", ".umap"})
    config_before = hash_tree(CONFIG)
    rhi = BASE.require_d3d12_sm6()
    if not unreal.EditorLevelLibrary.load_level(recovery["review_map"]):
        fail("could not load immutable Attempt03 review map")
    grouped = BASE.find_actors(base_contract)
    bounds = {
        family: BASE.combined_bounds(actors) for family, actors in grouped.items()
    }
    transient, sun_component, fill_component, sky_component = spawn_rig()
    capture, component, target = BASE.make_capture_component(
        recovery["capture"]["resolution"]
    )
    capture.set_actor_label("M01C008A03R01_Transient_SceneCapture")
    transient.append(capture)
    BASE.set_manual_exposure(
        component, float(recovery["capture"]["fixed_manual_exposure_bias_ev"])
    )
    all_candidate = [actor for actors in grouped.values() for actor in actors]
    records = []
    try:
        for rig in recovery["capture"]["rig_candidates"]:
            set_rig(
                (sun_component, fill_component, sky_component),
                rig,
            )
            for family in recovery["capture"]["families"]:
                for actor in all_candidate:
                    actor.set_actor_hidden_in_game(actor not in grouped[family])
                origin, extent = bounds[family]
                for view in recovery["capture"]["views_per_family"]:
                    location = BASE.camera_location(origin, extent, view)
                    rotation = unreal.MathLibrary.find_look_at_rotation(location, origin)
                    capture.set_actor_location(location, False, False)
                    capture.set_actor_rotation(rotation, False)
                    for _ in range(4):
                        component.capture_scene()
                    filename = (
                        f"Rig_{rig['rig_id']}_{family}_{view}_008_"
                        "Attempt03_Recovery01.png"
                    )
                    unreal.RenderingLibrary.export_render_target(
                        unreal.EditorLevelLibrary.get_editor_world(),
                        target,
                        str(output),
                        filename,
                    )
                    path = output / filename
                    if not path.is_file() or path.stat().st_size < 25000:
                        fail("recovery capture missing or implausibly small: " + str(path))
                    dimensions = BASE.png_dimensions(path)
                    if list(dimensions) != recovery["capture"]["resolution"]:
                        fail("recovery capture dimensions differ from contract")
                    records.append(
                        {
                            "rig_id": rig["rig_id"],
                            "rig_index": rig["rig_index"],
                            "key_lux": rig["key_lux"],
                            "fill_lux": rig["fill_lux"],
                            "skylight": rig["skylight"],
                            "fixed_manual_exposure_bias_ev": recovery["capture"][
                                "fixed_manual_exposure_bias_ev"
                            ],
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

    if len(records) != recovery["capture"]["capture_count"]:
        fail("recovery capture count differs from contract")
    original_after = hash_tree(ORIGINAL_CANDIDATE, {".uasset", ".umap"})
    attempt03_after = hash_tree(ATTEMPT03_CONTENT, {".uasset", ".umap"})
    runtime_after = hash_tree(RUNTIME_MAPS, {".uasset", ".umap"})
    config_after = hash_tree(CONFIG)
    if original_before != original_after:
        fail("original candidate package hashes changed")
    if attempt03_before != attempt03_after:
        fail("Attempt03 review-map package hashes changed")
    if runtime_before != runtime_after:
        fail("runtime map package hashes changed")
    if config_before != config_after:
        fail("Config hashes changed")
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery01-sweep.v1",
        "gate": "PASS_RECOVERY01_RIG_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION",
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "review_map": recovery["review_map"],
        "rhi_validation": rhi,
        "capture_resolution": recovery["capture"]["resolution"],
        "capture_count": len(records),
        "captures": records,
        "original_candidate_packages_unchanged": True,
        "attempt03_packages_unchanged": True,
        "runtime_maps_unchanged": True,
        "config_unchanged": True,
        "world_saved": False,
        "package_save_invoked": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    manifest = output / "capture_manifest.json"
    manifest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log(
        "[M01Grouped008Attempt03Recovery01Capture] "
        "PASS_RECOVERY01_RIG_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION"
    )


if __name__ == "__main__":
    main()
