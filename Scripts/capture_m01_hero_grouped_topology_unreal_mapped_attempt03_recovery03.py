"""Known-good persistent SceneCapture lifecycle with a hard pilot gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
BASE_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY03_CONTRACT.json"
RECOVERY02_CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery02.py"
ORIGINAL_CANDIDATE = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
ATTEMPT03_CONTENT = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
RUNTIME_MAPS = ROOT / "Content/Skyguard/Maps"
CONFIG = ROOT / "Config"


def fail(message: str) -> None:
    raise RuntimeError("[M01Grouped008Attempt03Recovery03Capture] " + message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail("could not load bound Recovery02 helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R02 = load_module("skyguard_attempt03_recovery02_helpers_r03", RECOVERY02_CAPTURE_PATH)
BASE = R02.BASE


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


def set_rig(components: tuple, rig: dict) -> None:
    BASE.set_light(components[0], float(rig["key_lux"]))
    BASE.set_light(components[1], float(rig["fill_lux"]))
    BASE.set_light(components[2], float(rig["skylight"]))
    for component in components:
        R02.mark_render_state_dirty(component)
    try:
        components[2].recapture_sky()
    except Exception:
        pass


def export_persistent_frame(
    world,
    capture,
    component,
    target,
    output: Path,
    filename: str,
    location,
    rotation,
    contract: dict,
) -> Path:
    unreal.RenderingLibrary.clear_render_target2d(
        world,
        target,
        unreal.LinearColor(
            *[float(value) for value in contract["pilot"]["sentinel_clear_rgba"]]
        ),
    )
    capture.set_actor_location(location, False, False)
    capture.set_actor_rotation(rotation, False)
    R02.mark_render_state_dirty(component)
    for _ in range(
        int(contract["capture"]["immediate_capture_scene_calls_per_export"])
    ):
        component.capture_scene()
    unreal.RenderingLibrary.export_render_target(
        world, target, str(output), filename
    )
    path = output / filename
    if not path.is_file() or path.stat().st_size < 25000:
        fail("persistent capture missing or implausibly small: " + str(path))
    if list(BASE.png_dimensions(path)) != contract["capture"]["resolution"]:
        fail("persistent capture dimensions differ from contract")
    return path


def main() -> None:
    base_contract = load_json(BASE_CONTRACT_PATH)
    contract = load_json(CONTRACT_PATH)
    output = Path(BASE.parse_switch("SkyguardAttempt03Recovery03Output"))
    requested_map = BASE.parse_switch("SkyguardAttempt03Recovery03ReviewMap")
    if requested_map != contract["review_map"]:
        fail("review map switch differs from Recovery03 contract")
    if output.exists():
        fail("immutable Recovery03 output already exists")
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

    lighting_actors, lighting_components = R02.spawn_rig(
        contract["pilot"]["rig"], "Persistent"
    )
    capture, component, target = BASE.make_capture_component(
        contract["capture"]["resolution"]
    )
    capture.set_actor_label("M01C008A03R03_Transient_PersistentSceneCapture")
    BASE.set_manual_exposure(
        component,
        float(contract["capture"]["fixed_manual_exposure_bias_ev"]),
    )
    try:
        component.set_editor_property("always_persist_rendering_state", True)
    except Exception:
        pass
    pilot_records = []
    try:
        for pair in contract["pilot"]["family_view_pairs"]:
            family = pair["family"]
            view = pair["view"]
            for actor in all_candidate:
                actor.set_actor_hidden_in_game(actor not in grouped[family])
            origin, extent = bounds[family]
            location = BASE.camera_location(origin, extent, view)
            rotation = unreal.MathLibrary.find_look_at_rotation(location, origin)
            filename = f"Pilot_{family}_{view}_Recovery03.png"
            path = export_persistent_frame(
                world,
                capture,
                component,
                target,
                pilot_output,
                filename,
                location,
                rotation,
                contract,
            )
            pilot_records.append(
                {
                    "family": family,
                    "view": view,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "metrics": R02.pilot_metrics(
                        path,
                        int(contract["selector"]["active_pixel_threshold_luma"]),
                    ),
                }
            )
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
            "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery03-pilot.v1",
            "gate": (
                "PASS_RECOVERY03_PERSISTENT_PILOT_LIVE_FULL_SWEEP_ALLOWED"
                if pilot_pass
                else "FAIL_CLOSED_RECOVERY03_PERSISTENT_PILOT_NOT_LIVE"
            ),
            "rhi_validation": rhi,
            "persistent_scene_capture_actor_count": 1,
            "persistent_render_target_count": 1,
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
            fail("persistent pilot failed; full sweep was not started")

        sweep_output.mkdir()
        records = []
        for rig in contract["capture"]["rig_candidates"]:
            set_rig(lighting_components, rig)
            first_family = contract["capture"]["families"][0]
            origin, extent = bounds[first_family]
            warm_location = BASE.camera_location(origin, extent, "three_quarter")
            warm_rotation = unreal.MathLibrary.find_look_at_rotation(
                warm_location, origin
            )
            capture.set_actor_location(warm_location, False, False)
            capture.set_actor_rotation(warm_rotation, False)
            for _ in range(
                int(
                    contract["capture"][
                        "unexported_warmup_captures_after_rig_change"
                    ]
                )
            ):
                component.capture_scene()
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
                        "Attempt03_Recovery03.png"
                    )
                    path = export_persistent_frame(
                        world,
                        capture,
                        component,
                        target,
                        sweep_output,
                        filename,
                        location,
                        rotation,
                        contract,
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
        if len(records) != contract["capture"]["full_sweep_capture_count"]:
            fail("Recovery03 full sweep count differs from contract")
    finally:
        for actor in all_candidate:
            actor.set_actor_hidden_in_game(False)
        try:
            unreal.EditorLevelLibrary.destroy_actor(capture)
        except Exception:
            pass
        R02.destroy_actors(lighting_actors)

    after = {
        "original": hash_tree(ORIGINAL_CANDIDATE, {".uasset", ".umap"}),
        "attempt03": hash_tree(ATTEMPT03_CONTENT, {".uasset", ".umap"}),
        "runtime": hash_tree(RUNTIME_MAPS, {".uasset", ".umap"}),
        "config": hash_tree(CONFIG),
    }
    if before != after:
        fail("Recovery03 changed a package, runtime map, or Config file")
    manifest = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery03-sweep.v1",
        "gate": "PASS_RECOVERY03_PERSISTENT_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION",
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "review_map": contract["review_map"],
        "rhi_validation": rhi,
        "pilot_receipt": str(pilot_receipt_path),
        "pilot_receipt_sha256": sha256_file(pilot_receipt_path),
        "pilot_gate": pilot_receipt["gate"],
        "capture_resolution": contract["capture"]["resolution"],
        "capture_count": len(records),
        "captures": records,
        "persistent_scene_capture_actor_count": 1,
        "persistent_render_target_count": 1,
        "sentinel_clear_before_every_export": True,
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
        "[M01Grouped008Attempt03Recovery03Capture] "
        "PASS_RECOVERY03_PERSISTENT_SWEEP_AWAITING_OFFLINE_GLOBAL_RIG_SELECTION"
    )


if __name__ == "__main__":
    main()
