"""Recovery04: exact known-nonblank lighting lifecycle plus a tiny EV pilot."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
BASE_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY04_CONTRACT.json"
BASE_CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
PNG_HELPER_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery02.py"
ORIGINAL_CANDIDATE = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
ATTEMPT03_CONTENT = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"
RUNTIME_MAPS = ROOT / "Content/Skyguard/Maps"
CONFIG = ROOT / "Config"


def fail(message: str) -> None:
    raise RuntimeError("[M01Grouped008Attempt03Recovery04Capture] " + message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail("could not load bound helper module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("skyguard_attempt03_known_nonblank_base_r04", BASE_CAPTURE_PATH)
PNG = load_module("skyguard_attempt03_png_helpers_r04", PNG_HELPER_PATH)


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
        if path.is_file() and (not suffixes or path.suffix.lower() in suffixes):
            records[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    return records


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def percentile_from_histogram(histogram: list[int], fraction: float) -> float:
    total = sum(histogram)
    if total == 0:
        return 0.0
    target = fraction * (total - 1)
    cumulative = 0
    for value, count in enumerate(histogram):
        if cumulative + count > target:
            return float(value)
        cumulative += count
    return 255.0


def exposure_metrics(path: Path, threshold: int) -> dict:
    width, height, pixels = PNG.decode_png_rgb(path)
    active_histogram = [0] * 256
    maximum = 0
    colors: set[tuple[int, int, int]] = set()
    for red, green, blue in pixels:
        luma = (54 * red + 183 * green + 19 * blue) // 256
        if luma > threshold:
            active_histogram[luma] += 1
        maximum = max(maximum, red, green, blue)
        if len(colors) < 4096:
            colors.add((red, green, blue))
    active = sum(active_histogram)
    total = width * height
    if active == 0:
        return {
            "dimensions": [width, height],
            "active_pixel_fraction": 0.0,
            "active_clipped_fraction": 1.0,
            "active_p05": 0.0,
            "active_p50": 0.0,
            "active_p95": 0.0,
            "active_dynamic_range": 0.0,
            "maximum_channel_value": maximum,
            "unique_color_count_capped_at_4096": len(colors),
        }
    p05 = percentile_from_histogram(active_histogram, 0.05)
    p50 = percentile_from_histogram(active_histogram, 0.50)
    p95 = percentile_from_histogram(active_histogram, 0.95)
    return {
        "dimensions": [width, height],
        "active_pixel_fraction": round(active / total, 8),
        "active_clipped_fraction": round(sum(active_histogram[250:]) / active, 8),
        "active_p05": p05,
        "active_p50": p50,
        "active_p95": p95,
        "active_dynamic_range": p95 - p05,
        "maximum_channel_value": maximum,
        "unique_color_count_capped_at_4096": len(colors),
    }


def metric_result(metrics: dict, policy: dict) -> tuple[bool, list[str], float]:
    failures = []
    liveness = policy["liveness_bounds"]
    if (
        metrics["active_pixel_fraction"]
        < liveness["minimum_active_pixel_fraction_luma_gt_8"]
    ):
        failures.append("active_pixel_fraction")
    if metrics["maximum_channel_value"] < liveness["minimum_max_channel_value"]:
        failures.append("maximum_channel_value")
    if (
        metrics["unique_color_count_capped_at_4096"]
        < liveness["minimum_unique_color_count"]
    ):
        failures.append("unique_color_count")
    exposure = policy["exposure_hard_bounds"]
    if (
        metrics["active_clipped_fraction"]
        > exposure["maximum_active_clipped_fraction_luma_ge_250"]
    ):
        failures.append("active_clipped_fraction")
    if not exposure["active_p50_range"][0] <= metrics["active_p50"] <= exposure["active_p50_range"][1]:
        failures.append("active_p50")
    if not exposure["active_p95_range"][0] <= metrics["active_p95"] <= exposure["active_p95_range"][1]:
        failures.append("active_p95")
    if (
        metrics["active_dynamic_range"]
        < exposure["minimum_active_dynamic_range_p95_minus_p05"]
    ):
        failures.append("active_dynamic_range")
    penalty = (
        metrics["active_clipped_fraction"]
        / exposure["maximum_active_clipped_fraction_luma_ge_250"]
        + abs(metrics["active_p50"] - 120.0) / 120.0
        + abs(metrics["active_p95"] - 220.0) / 220.0
        + max(0.0, 100.0 - metrics["active_dynamic_range"]) / 100.0
    )
    return not failures, failures, round(penalty, 8)


def ev_token(value: int) -> str:
    return f"neg{abs(value):02d}" if value < 0 else f"pos{value:02d}"


def require_exposure_readback(component, requested: float) -> float:
    settings = component.get_editor_property("post_process_settings")
    actual = float(settings.get_editor_property("auto_exposure_bias"))
    if not math.isclose(actual, requested, rel_tol=0.0, abs_tol=0.0001):
        fail(f"manual exposure readback {actual} differs from requested {requested}")
    return actual


def export_frame(world, capture, component, target, output: Path, filename: str, location, rotation, calls: int) -> Path:
    capture.set_actor_location(location, False, False)
    capture.set_actor_rotation(rotation, False)
    for _ in range(calls):
        component.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, target, str(output), filename)
    path = output / filename
    if not path.is_file() or path.stat().st_size < 25000:
        fail("capture missing or implausibly small: " + str(path))
    return path


def main() -> None:
    base_contract = load_json(BASE_CONTRACT_PATH)
    contract = load_json(CONTRACT_PATH)
    output = Path(BASE.parse_switch("SkyguardAttempt03Recovery04Output"))
    requested_map = BASE.parse_switch("SkyguardAttempt03Recovery04ReviewMap")
    if requested_map != contract["review_map"]:
        fail("review map switch differs from Recovery04 contract")
    if output.exists():
        fail("immutable Recovery04 output already exists")
    output.mkdir(parents=True, exist_ok=False)
    pilot_output = output / "pilot"
    pilot_output.mkdir()
    full_output = output / "full_views"

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
    bounds = {family: BASE.combined_bounds(actors) for family, actors in grouped.items()}
    all_candidate = [actor for actors in grouped.values() for actor in actors]
    world = unreal.EditorLevelLibrary.get_editor_world()

    transient = BASE.spawn_lighting(base_contract)
    capture, component, target = BASE.make_capture_component(contract["capture"]["resolution"])
    capture.set_actor_label("M01C008A03R04_Transient_BaseLifecycleSceneCapture")
    transient.append(capture)
    pilot_records = []
    try:
        family = contract["pilot"]["family"]
        view = contract["pilot"]["view"]
        for actor in all_candidate:
            actor.set_actor_hidden_in_game(actor not in grouped[family])
        origin, extent = bounds[family]
        location = BASE.camera_location(origin, extent, view)
        rotation = unreal.MathLibrary.find_look_at_rotation(location, origin)
        for bias in contract["pilot"]["exposure_candidates_ev"]:
            BASE.set_manual_exposure(component, float(bias))
            effective_bias = require_exposure_readback(component, float(bias))
            filename = f"Pilot_EV_{ev_token(int(bias))}_{family}_{view}_Recovery04.png"
            path = export_frame(
                world,
                capture,
                component,
                target,
                pilot_output,
                filename,
                location,
                rotation,
                int(contract["pilot"]["capture_scene_calls_per_export"]),
            )
            metrics = exposure_metrics(
                path,
                int(
                    contract["pilot"]["exposure_hard_bounds"][
                        "active_pixel_threshold_luma"
                    ]
                ),
            )
            passed, failures, penalty = metric_result(metrics, contract["pilot"])
            pilot_records.append(
                {
                    "exposure_bias_ev": bias,
                    "effective_exposure_bias_ev": effective_bias,
                    "family": family,
                    "view": view,
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "metrics": metrics,
                    "hard_bounds_passed": passed,
                    "hard_bound_failures": failures,
                    "penalty": penalty,
                }
            )
        eligible = [record for record in pilot_records if record["hard_bounds_passed"]]
        selected = (
            min(
                eligible,
                key=lambda record: (
                    record["penalty"],
                    abs(record["exposure_bias_ev"]),
                    record["exposure_bias_ev"],
                ),
            )
            if eligible
            else None
        )
        pilot_receipt = {
            "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery04-pilot.v1",
            "gate": (
                "PASS_RECOVERY04_BASE_LIGHTING_LIVE_EXPOSURE_SELECTED_FULL_VIEWS_ALLOWED"
                if selected
                else "FAIL_CLOSED_RECOVERY04_NO_LIVE_HARD_BOUND_EXPOSURE"
            ),
            "rhi_validation": rhi,
            "base_spawn_lighting_used_once": True,
            "light_proxy_changes_after_spawn": 0,
            "capture_count": len(pilot_records),
            "captures": pilot_records,
            "selected_exposure_bias_ev": (
                selected["exposure_bias_ev"] if selected else None
            ),
            "full_views_allowed": selected is not None,
            "promotion_allowed": False,
            "p3_4_closed": False,
        }
        pilot_receipt_path = output / "pilot_receipt.json"
        pilot_receipt_path.write_text(
            json.dumps(pilot_receipt, indent=2) + "\n", encoding="utf-8"
        )
        if selected is None:
            fail("base-lighting exposure pilot failed; full views were not started")

        selected_ev = int(selected["exposure_bias_ev"])
        BASE.set_manual_exposure(component, float(selected_ev))
        require_exposure_readback(component, float(selected_ev))
        full_output.mkdir()
        full_records = []
        for full_family in contract["full_views"]["families"]:
            for actor in all_candidate:
                actor.set_actor_hidden_in_game(actor not in grouped[full_family])
            full_origin, full_extent = bounds[full_family]
            for full_view in contract["full_views"]["views_per_family"]:
                full_location = BASE.camera_location(full_origin, full_extent, full_view)
                full_rotation = unreal.MathLibrary.find_look_at_rotation(
                    full_location, full_origin
                )
                filename = (
                    f"EV_{ev_token(selected_ev)}_{full_family}_{full_view}_"
                    "008_Attempt03_Recovery04.png"
                )
                path = export_frame(
                    world,
                    capture,
                    component,
                    target,
                    full_output,
                    filename,
                    full_location,
                    full_rotation,
                    int(contract["full_views"]["capture_scene_calls_per_export"]),
                )
                metrics = exposure_metrics(
                    path,
                    int(
                        contract["pilot"]["exposure_hard_bounds"][
                            "active_pixel_threshold_luma"
                        ]
                    ),
                )
                passed, failures, penalty = metric_result(metrics, contract["pilot"])
                full_records.append(
                    {
                        "selected_exposure_bias_ev": selected_ev,
                        "effective_exposure_bias_ev": float(selected_ev),
                        "family": full_family,
                        "view": full_view,
                        "path": str(path),
                        "bytes": path.stat().st_size,
                        "sha256": sha256_file(path),
                        "dimensions": metrics["dimensions"],
                        "metrics": metrics,
                        "hard_bounds_passed": passed,
                        "hard_bound_failures": failures,
                        "penalty": penalty,
                    }
                )
        full_pass = (
            len(full_records) == contract["full_views"]["capture_count"]
            and len({record["sha256"] for record in full_records}) == 9
            and all(record["hard_bounds_passed"] for record in full_records)
        )
        manifest = {
            "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery04-capture.v1",
            "gate": (
                "PASS_RECOVERY04_NINE_VIEWS_AWAITING_OFFLINE_AUDIT"
                if full_pass
                else "FAIL_CLOSED_RECOVERY04_NINE_VIEWS_DID_NOT_PASS_HARD_BOUNDS"
            ),
            "captured_utc": datetime.now(timezone.utc).isoformat(),
            "review_map": contract["review_map"],
            "rhi_validation": rhi,
            "pilot_receipt": str(pilot_receipt_path),
            "pilot_receipt_sha256": sha256_file(pilot_receipt_path),
            "selected_exposure_bias_ev": selected_ev,
            "capture_count": len(full_records),
            "captures": full_records,
            "base_spawn_lighting_used_once": True,
            "light_proxy_changes_after_spawn": 0,
            "world_saved": False,
            "package_save_invoked": False,
            "promotion_allowed": False,
            "p3_4_closed": False,
        }
        manifest_path = output / "capture_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not full_pass:
            fail("nine Recovery04 views did not all pass unchanged hard bounds")
    finally:
        for actor in all_candidate:
            actor.set_actor_hidden_in_game(False)
        for actor in reversed(transient):
            try:
                unreal.EditorLevelLibrary.destroy_actor(actor)
            except Exception:
                pass

    after = {
        "original": hash_tree(ORIGINAL_CANDIDATE, {".uasset", ".umap"}),
        "attempt03": hash_tree(ATTEMPT03_CONTENT, {".uasset", ".umap"}),
        "runtime": hash_tree(RUNTIME_MAPS, {".uasset", ".umap"}),
        "config": hash_tree(CONFIG),
    }
    if before != after:
        fail("Recovery04 changed a package, runtime map, or Config file")
    unreal.log(
        "[M01Grouped008Attempt03Recovery04Capture] "
        "PASS_RECOVERY04_NINE_VIEWS_AWAITING_OFFLINE_AUDIT"
    )


if __name__ == "__main__":
    main()
