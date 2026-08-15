import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


EXPECTED = [
    "01_daylight_front_intact.png",
    "02_daylight_rear_intact.png",
    "03_overcast_top_weakpoints.png",
    "04_wet_storm_underside_engine.png",
    "05_night_operational_intact.png",
    "06_close_antenna_camera.png",
    "07_close_engine_linkage.png",
    "08_damaged_gameplay_flyby.png",
]


def metrics(path: Path):
    image = Image.open(path).convert("RGB")
    array = np.asarray(image, dtype=np.float32) / 255.0
    maximum = array.max(axis=2)
    minimum = array.min(axis=2)
    luminance = 0.2126 * array[:, :, 0] + 0.7152 * array[:, :, 1] + 0.0722 * array[:, :, 2]
    saturation = maximum - minimum
    gradient_x = np.abs(np.diff(luminance, axis=1))
    gradient_y = np.abs(np.diff(luminance, axis=0))
    edge_density = float(((gradient_x > 0.035).mean() + (gradient_y > 0.035).mean()) / 2.0)
    return {
        "resolution": [image.width, image.height],
        "mean_luminance": float(luminance.mean()),
        "p05_luminance": float(np.quantile(luminance, 0.05)),
        "p95_luminance": float(np.quantile(luminance, 0.95)),
        "dynamic_range_p95_p05": float(np.quantile(luminance, 0.95) - np.quantile(luminance, 0.05)),
        "mean_saturation": float(saturation.mean()),
        "clipped_white_fraction": float((luminance > 0.985).mean()),
        "crushed_black_fraction": float((luminance < 0.015).mean()),
        "edge_density": edge_density,
    }


def validate(name, values):
    failures = []
    if values["resolution"] != [1920, 1080]:
        failures.append("resolution")
    is_night = name.startswith("05_")
    if is_night:
        if not 0.035 <= values["mean_luminance"] <= 0.55:
            failures.append("night_mean_luminance")
        if values["crushed_black_fraction"] > 0.42:
            failures.append("night_crushed_black")
        if values["mean_saturation"] < 0.018:
            failures.append("night_material_color_readability")
    else:
        if not 0.12 <= values["mean_luminance"] <= 0.82:
            failures.append("mean_luminance")
        if values["crushed_black_fraction"] > 0.16:
            failures.append("crushed_black")
        if values["mean_saturation"] < 0.035:
            failures.append("material_color_readability")
    if values["clipped_white_fraction"] > 0.01:
        failures.append("clipped_white")
    if values["dynamic_range_p95_p05"] < 0.18:
        failures.append("insufficient_dynamic_range")
    if values["edge_density"] < 0.018:
        failures.append("insufficient_detail_edges")
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--renders", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    render_dir = Path(args.renders)
    output = Path(args.output)
    actual = sorted(path.name for path in render_dir.glob("*.png")) if render_dir.is_dir() else []
    report = {
        "schema": "skyguard.m01-pathfinder.render-suite-automatic-review.v1",
        "classification": "FAIL",
        "expected": EXPECTED,
        "actual": actual,
        "images": [],
        "failures": [],
    }
    if actual != EXPECTED:
        report["failures"].append({"render_set": "exact_names_or_count_mismatch"})
    for name in EXPECTED:
        path = render_dir / name
        if not path.is_file():
            continue
        values = metrics(path)
        failures = validate(name, values)
        report["images"].append({"file": str(path), "metrics": values, "failures": failures})
        if failures:
            report["failures"].append({"file": name, "reasons": failures})
    if not report["failures"] and len(report["images"]) == len(EXPECTED):
        report["classification"] = "PASS_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report["classification"])
    raise SystemExit(0 if report["classification"].startswith("PASS") else 1)


if __name__ == "__main__":
    main()

