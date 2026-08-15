from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
R09_WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery09\build_m01_visible_environment_kit_refinement01_stagea_recovery09_checkpoint01.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=os.environ.get("SKYGUARD_PROBE_OUTPUT"))
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(arguments)


def load_generated_source() -> str:
    spec = importlib.util.spec_from_file_location("skyguard_r09_storm_probe_source", R09_WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the frozen Recovery09 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source, _ = module.load_recovery09_source()
    return source


def main() -> int:
    args = parse_args()
    if not args.output:
        raise RuntimeError("Probe output is required by --output or SKYGUARD_PROBE_OUTPUT")
    output = Path(args.output).resolve()
    if output.exists():
        raise RuntimeError(f"Probe output already exists: {output}")
    output.mkdir(parents=True)
    source = load_generated_source()
    namespace: dict[str, object] = {
        "__name__": "skyguard_recovery10_storm_light_probe_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(source, str(Path(__file__).resolve()), "exec"), namespace)

    bpy = namespace["bpy"]
    Vector = namespace["Vector"]
    scene = namespace["reset_scene"]()
    root = namespace["collection"]("NONGOVERNED_RECOVERY10_STORM_LIGHT_PROBE")
    district = namespace["collection"]("ASSET_CoastalDistrict", root)
    collision = namespace["collection"]("COLLISION_CoastalDistrict", root)
    sockets = namespace["collection"]("SOCKETS_CoastalDistrict", root)
    materials = namespace["build_materials"]()
    namespace["build_shore_and_street"](materials, district, collision, sockets)
    specs = ((10.0, 5, "A"), (30.0, 7, "B"), (50.0, 4, "C"), (70.0, 6, "D"), (90.0, 5, "E"))
    for index, (center_x, floors, style) in enumerate(specs, 1):
        namespace["build_midrise"](
            f"SM_M01_STAGEA_R05_Midrise_{style}_{index:02d}",
            center_x,
            floors,
            style,
            materials,
            district,
            collision,
            sockets,
        )
    rig = namespace["add_review_rig"](scene)
    namespace["configure_condition"](scene, rig, "storm", materials)
    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100

    cameras = {
        "coastal_route": ((50.0, -54.0, 22.0), (50.0, 54.0, 7.0), 52.0),
        "street_close": ((24.0, 39.0, 9.5), (31.0, 72.0, 8.0), 58.0),
        "district_aerial": ((50.0, -42.0, 44.0), (50.0, 52.0, 7.0), 50.0),
    }
    candidates = (
        {"id": "A", "fill_energy": 1800.0, "moon_energy": 1800.0, "sun_energy": 0.80, "exposure": 0.80},
        {"id": "B", "fill_energy": 2800.0, "moon_energy": 2400.0, "sun_energy": 1.10, "exposure": 1.00},
        {"id": "C", "fill_energy": 4000.0, "moon_energy": 3200.0, "sun_energy": 1.35, "exposure": 1.20},
    )

    def apply_candidate(candidate: dict[str, float | str], camera_location, target) -> None:
        target_vector = Vector(target)
        view_direction = (Vector(camera_location) - target_vector).normalized()
        rig["sun"].data.energy = float(candidate["sun_energy"])
        rig["sun"].data.color = (0.42, 0.52, 0.64)
        rig["fill"].location = target_vector + view_direction * 20.0 + Vector((0.0, 0.0, 14.0))
        rig["fill"].rotation_euler = (target_vector - rig["fill"].location).to_track_quat("-Z", "Y").to_euler()
        rig["fill"].data.energy = float(candidate["fill_energy"])
        rig["fill"].data.color = (0.42, 0.50, 0.58)
        rig["moon"].location = target_vector + view_direction * 30.0 + Vector((14.0, 0.0, 30.0))
        rig["moon"].rotation_euler = (target_vector - rig["moon"].location).to_track_quat("-Z", "Y").to_euler()
        rig["moon"].data.energy = float(candidate["moon_energy"])
        rig["moon"].data.color = (0.30, 0.38, 0.48)
        scene.view_settings.exposure = float(candidate["exposure"])

    results: list[dict[str, object]] = []
    selected = None
    for candidate in candidates:
        candidate_passed = True
        for camera_id, (location, target, lens) in cameras.items():
            namespace["point_camera"](rig["camera"], location, target, lens)
            apply_candidate(candidate, location, target)
            path = output / f"candidate_{candidate['id']}_{camera_id}.png"
            metrics = namespace["render_and_measure"](scene, path)
            passed = metrics["mean_luma_linear"] >= 0.018 and metrics["black_fraction_linear_0_01"] <= 0.58
            candidate_passed = candidate_passed and passed
            result = {
                "candidate": candidate,
                "camera": camera_id,
                "metrics": metrics,
                "passed": passed,
                "path": str(path),
            }
            results.append(result)
            print(json.dumps(result, sort_keys=True), flush=True)
        if candidate_passed and selected is None:
            selected = candidate
    if selected is None:
        raise RuntimeError("No targeted-storm-light candidate passed all three camera bounds")

    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery10.storm-review-light-probe.v1",
        "classification": "PASS",
        "selected_candidate": selected,
        "results": results,
        "render_resolution": [640, 360],
        "production_namespace_created": False,
    }
    (output / "probe_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"classification": "PASS", "selected_candidate": selected}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
