"""Fail-closed verifier for the M01 Landscape visible/GPU comparison gate."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import re
import statistics
import struct
import sys
import zlib
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_contract import load_effective_contract


HUMAN_REVIEW_PATH = (
    ROOT
    / "Saved/Reports/PHASE4_M01_LANDSCAPE_VISIBLE_HUMAN_REVIEW_ATTEMPT04.json"
)

CSV_FIELD_SIZE_LIMIT = 64 * 1024 * 1024

CRITICAL_PATTERNS = {
    "fatal": re.compile(r"Fatal error|LowLevelFatalError", re.IGNORECASE),
    "assert": re.compile(r"Assertion failed", re.IGNORECASE),
    "ensure": re.compile(r"Ensure condition failed", re.IGNORECASE),
    "gpu_crash": re.compile(
        r"GPU Crash|DXGI_ERROR_DEVICE_(?:REMOVED|HUNG|RESET)", re.IGNORECASE
    ),
    "out_of_memory": re.compile(
        r"Out of video memory|Ran out of memory|OOM detected", re.IGNORECASE
    ),
    "python_error": re.compile(
        r"LogPython: Error|Python exception|Traceback \(most recent call last\)",
        re.IGNORECASE,
    ),
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_png_rgb8(path: Path) -> tuple[int, int, bytes]:
    """Decode governed non-interlaced 8-bit RGB/RGBA PNGs with stdlib only."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    offset = 8
    width = height = bit_depth = color_type = interlace = None
    compressed = bytearray()
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = (
                struct.unpack(">IIBBBBB", payload)
            )
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    if (
        not width
        or not height
        or bit_depth != 8
        or color_type not in (0, 2, 6)
        or interlace != 0
    ):
        raise ValueError("unsupported governed PNG format")
    channels = {0: 1, 2: 3, 6: 4}[color_type]
    stride = width * channels
    raw = zlib.decompress(bytes(compressed))
    if len(raw) != (stride + 1) * height:
        raise ValueError("unexpected PNG scanline length")
    previous = bytearray(stride)
    rgb = bytearray(width * height * 3)
    raw_offset = 0
    rgb_offset = 0
    for _ in range(height):
        filter_type = raw[raw_offset]
        raw_offset += 1
        source = raw[raw_offset : raw_offset + stride]
        raw_offset += stride
        row = bytearray(stride)
        for index, value in enumerate(source):
            left = row[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = (
                previous[index - channels] if index >= channels else 0
            )
            if filter_type == 0:
                reconstructed = value
            elif filter_type == 1:
                reconstructed = value + left
            elif filter_type == 2:
                reconstructed = value + above
            elif filter_type == 3:
                reconstructed = value + ((left + above) // 2)
            elif filter_type == 4:
                estimate = left + above - upper_left
                left_distance = abs(estimate - left)
                above_distance = abs(estimate - above)
                upper_left_distance = abs(estimate - upper_left)
                predictor = (
                    left
                    if left_distance <= above_distance
                    and left_distance <= upper_left_distance
                    else (
                        above
                        if above_distance <= upper_left_distance
                        else upper_left
                    )
                )
                reconstructed = value + predictor
            else:
                raise ValueError("unsupported PNG filter")
            row[index] = reconstructed & 0xFF
        for pixel in range(width):
            source_index = pixel * channels
            if channels == 1:
                value = row[source_index]
                rgb[rgb_offset : rgb_offset + 3] = bytes(
                    (value, value, value)
                )
            else:
                rgb[rgb_offset : rgb_offset + 3] = row[
                    source_index : source_index + 3
                ]
            rgb_offset += 3
        previous = row
    return width, height, bytes(rgb)


def largest_connected_run_fraction(
    mask: bytearray, width: int, height: int
) -> float:
    """Return largest 4-connected region fraction using row runs."""
    parents: list[int] = []
    sizes: list[int] = []

    def create(size: int) -> int:
        index = len(parents)
        parents.append(index)
        sizes.append(size)
        return index

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        if sizes[left_root] < sizes[right_root]:
            left_root, right_root = right_root, left_root
        parents[right_root] = left_root
        sizes[left_root] += sizes[right_root]

    previous: list[tuple[int, int, int]] = []
    total = 0
    for y in range(height):
        current: list[tuple[int, int, int]] = []
        x = 0
        row_start = y * width
        while x < width:
            if not mask[row_start + x]:
                x += 1
                continue
            start = x
            while x + 1 < width and mask[row_start + x + 1]:
                x += 1
            end = x
            run_size = end - start + 1
            total += run_size
            run_id = create(run_size)
            current.append((start, end, run_id))
            x += 1
        previous_index = 0
        for start, end, run_id in current:
            while (
                previous_index < len(previous)
                and previous[previous_index][1] < start
            ):
                previous_index += 1
            overlap_index = previous_index
            while (
                overlap_index < len(previous)
                and previous[overlap_index][0] <= end
            ):
                union(run_id, previous[overlap_index][2])
                overlap_index += 1
        previous = current
    if total == 0:
        return 0.0
    largest = max(
        (sizes[index] for index in range(len(sizes)) if find(index) == index),
        default=0,
    )
    return largest / total


def normalized_repaired_capture_thresholds(contract: dict) -> dict:
    """Normalize Attempt05 and Attempt06 visual thresholds fail-closed.

    Attempt05 stores the per-camera coverage minimums in one mapping.
    Attempt06 makes each camera the sole authority for its own minimum.  The
    Attempt06 loader replaces ``repair`` wholesale, so blindly using the
    Attempt05 mapping raises before any evidence can be analyzed.
    """
    revision = contract["repair"]["capture_revision"]
    camera_thresholds = revision.get(
        "minimum_landscape_pixel_fraction_by_camera"
    )
    if camera_thresholds is None:
        cameras = revision.get("cameras")
        if not isinstance(cameras, list) or not cameras:
            raise KeyError(
                "capture_revision requires cameras or "
                "minimum_landscape_pixel_fraction_by_camera"
            )
        camera_thresholds = {}
        for camera in cameras:
            camera_id = camera.get("id")
            minimum = camera.get("minimum_landscape_pixel_fraction")
            if (
                not isinstance(camera_id, str)
                or not camera_id
                or camera_id in camera_thresholds
                or not isinstance(minimum, (int, float))
                or isinstance(minimum, bool)
                or minimum < 0.0
                or minimum > 1.0
            ):
                raise ValueError(
                    "invalid Attempt06 per-camera coverage threshold"
                )
            camera_thresholds[camera_id] = float(minimum)
    readability = revision.get("readability_inside_coverage_mask")
    if not isinstance(readability, dict):
        raise KeyError(
            "capture_revision requires readability_inside_coverage_mask"
        )
    return {
        "minimum_landscape_pixel_fraction_by_camera": camera_thresholds,
        "readability_inside_coverage_mask": readability,
    }


def analyze_attempt05_visuals(
    contract: dict, candidate_root: Path
) -> dict[str, Any]:
    thresholds = normalized_repaired_capture_thresholds(contract)
    camera_results = {}
    all_pass = True
    for camera_id, minimum_fraction in thresholds[
        "minimum_landscape_pixel_fraction_by_camera"
    ].items():
        mask_path = (
            candidate_root
            / f"candidate_diagnostic_landscape_coverage_{camera_id}.png"
        )
        lit_path = candidate_root / f"candidate_lit_{camera_id}.png"
        result = {"mask": str(mask_path), "lit": str(lit_path), "pass": False}
        if not mask_path.is_file() or not lit_path.is_file():
            camera_results[camera_id] = result
            all_pass = False
            continue
        mask_width, mask_height, mask_rgb = decode_png_rgb8(mask_path)
        lit_width, lit_height, lit_rgb = decode_png_rgb8(lit_path)
        if (mask_width, mask_height) != (lit_width, lit_height):
            camera_results[camera_id] = result
            all_pass = False
            continue
        mask = bytearray(mask_width * mask_height)
        luminance = []
        for pixel in range(mask_width * mask_height):
            index = pixel * 3
            mask_value = (
                mask_rgb[index]
                + mask_rgb[index + 1]
                + mask_rgb[index + 2]
            ) / (3.0 * 255.0)
            if mask_value < 0.5:
                continue
            mask[pixel] = 1
            luminance.append(
                (
                    0.2126 * lit_rgb[index]
                    + 0.7152 * lit_rgb[index + 1]
                    + 0.0722 * lit_rgb[index + 2]
                )
                / 255.0
            )
        coverage = sum(mask) / len(mask)
        median = statistics.median(luminance) if luminance else 0.0
        p10 = percentile(luminance, 0.10) or 0.0
        p90 = percentile(luminance, 0.90) or 0.0
        connected = largest_connected_run_fraction(
            mask, mask_width, mask_height
        )
        readability = thresholds["readability_inside_coverage_mask"]
        result.update(
            {
                "coverage_fraction": coverage,
                "minimum_coverage_fraction": minimum_fraction,
                "median_luminance": median,
                "p90_minus_p10_luminance": p90 - p10,
                "largest_connected_region_fraction_of_mask": connected,
                "pass": (
                    coverage >= minimum_fraction
                    and median
                    >= readability["minimum_median_luminance"]
                    and p90 - p10
                    >= readability[
                        "minimum_p90_minus_p10_luminance"
                    ]
                    and connected
                    >= readability[
                        "minimum_largest_connected_region_fraction_of_mask"
                    ]
                ),
            }
        )
        camera_results[camera_id] = result
        all_pass &= result["pass"]

    component_path = (
        candidate_root / "candidate_diagnostic_component_boundary_C05.png"
    )
    component_bucket_count = 0
    if component_path.is_file():
        _, _, component_rgb = decode_png_rgb8(component_path)
        buckets = set()
        for index in range(0, len(component_rgb), 3):
            red, green, blue = component_rgb[index : index + 3]
            if red + green + blue < 48:
                continue
            buckets.add((red // 16, green // 16, blue // 16))
        component_bucket_count = len(buckets)
    complexity_path = (
        candidate_root / "candidate_diagnostic_shader_complexity_C04.png"
    )
    complexity_lit = candidate_root / "candidate_lit_C04_INLAND_CLOSE.png"
    component_lit = candidate_root / "candidate_lit_C05_COVERAGE_HIGH.png"
    diagnostic_hashes_distinct = bool(
        complexity_path.is_file()
        and complexity_lit.is_file()
        and component_path.is_file()
        and component_lit.is_file()
        and sha256_file(complexity_path) != sha256_file(complexity_lit)
        and sha256_file(component_path) != sha256_file(component_lit)
    )
    return {
        "camera_results": camera_results,
        "all_camera_coverage_and_readability_pass": all_pass,
        "component_color_bucket_count": component_bucket_count,
        "all_16_component_ids_visible": component_bucket_count >= 16,
        "diagnostic_hashes_distinct_from_lit": diagnostic_hashes_distinct,
    }


def srgb8_to_linear(value: int) -> float:
    normalized = value / 255.0
    if normalized <= 0.04045:
        return normalized / 12.92
    return ((normalized + 0.055) / 1.055) ** 2.4


def analyze_attempt06_visuals(
    contract: dict, candidate_root: Path
) -> dict[str, Any]:
    """Use exact expected component IDs; generic color buckets are forbidden."""
    result = analyze_attempt05_visuals(contract, candidate_root)
    component_gate = contract["repair"]["capture_revision"][
        "component_id_gate"
    ]
    component_path = (
        candidate_root / "candidate_diagnostic_component_boundary_C05.png"
    )
    expected = []
    for y_index in range(2):
        for x_index in range(8):
            component_id = x_index + 8 * y_index
            expected.append(
                (
                    component_id,
                    (x_index + 1) / 9.0,
                    (y_index + 1) / 3.0,
                    0.25
                    + 0.75
                    * (
                        component_id * 0.61803398875
                        - math.floor(component_id * 0.61803398875)
                    ),
                )
            )
    counts = {str(item[0]): 0 for item in expected}
    if component_path.is_file():
        _, _, component_rgb = decode_png_rgb8(component_path)
        tolerance = (
            component_gate["rgb8_tolerance_per_channel"] / 255.0
        )
        for index in range(0, len(component_rgb), 3):
            pixel = tuple(
                srgb8_to_linear(channel)
                for channel in component_rgb[index : index + 3]
            )
            best_id = None
            best_distance = float("inf")
            for component_id, red, green, blue in expected:
                differences = (
                    abs(pixel[0] - red),
                    abs(pixel[1] - green),
                    abs(pixel[2] - blue),
                )
                maximum = max(differences)
                if maximum <= tolerance and maximum < best_distance:
                    best_id = component_id
                    best_distance = maximum
            if best_id is not None:
                counts[str(best_id)] += 1
    minimum_pixels = component_gate["minimum_pixels_per_expected_id"]
    result.pop("component_color_bucket_count", None)
    result["component_expected_palette_linear"] = [
        {
            "component_id": component_id,
            "linear_rgb": [red, green, blue],
        }
        for component_id, red, green, blue in expected
    ]
    result["component_expected_id_pixel_counts"] = counts
    result["minimum_pixels_per_expected_id"] = minimum_pixels
    result["component_palette_match_method"] = (
        "decode RGB8 as sRGB, compare in linear space to the exact material "
        "formula, per-channel tolerance only"
    )
    result["generic_color_bucket_count_used"] = False
    result["all_16_component_ids_visible"] = (
        len(counts) == 16
        and all(count >= minimum_pixels for count in counts.values())
    )
    return result


def percentile(values: list[float], value: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = (len(ordered) - 1) * value
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return ordered[low]
    return ordered[low] * (high - rank) + ordered[high] * (rank - low)


def open_csv(path: Path):
    if path.suffix.lower() == ".gz":
        return gzip.open(
            path, "rt", encoding="utf-8-sig", errors="replace", newline=""
        )
    return path.open("r", encoding="utf-8-sig", errors="replace", newline="")


def number(value: str) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def find_column(header: list[str], patterns: list[re.Pattern]) -> int | None:
    # Pattern order is semantic priority. UE 5.8 can place per-pass
    # DrawCall/SlateUI before the aggregate RHI/DrawCalls column.
    for pattern in patterns:
        for index, value in enumerate(header):
            if pattern.search(value.strip()):
                return index
    return None


def analyze_csv(path: Path) -> dict[str, Any]:
    result = {
        "path": str(path),
        "exists": path.is_file(),
        "parseable": False,
        "frame_count": 0,
        "columns": {},
        "memory_column": None,
        "metrics": {},
    }
    if not path.is_file() or path.stat().st_size == 0:
        return result
    try:
        csv.field_size_limit(CSV_FIELD_SIZE_LIMIT)
        with open_csv(path) as stream:
            rows = list(csv.reader(stream))
    except (OSError, csv.Error):
        return result
    header_index = next(
        (
            index
            for index, row in enumerate(rows)
            if any("frametime" in cell.lower().replace(" ", "") for cell in row)
        ),
        None,
    )
    if header_index is None:
        return result
    header = [cell.strip() for cell in rows[header_index]]
    patterns = {
        "frame": [re.compile(r"^frame\s*time(?:\s*\(ms\))?$", re.I), re.compile(r"frametime", re.I)],
        "gpu": [re.compile(r"gpu.*(?:frame)?time", re.I), re.compile(r"^gpu$", re.I)],
        "draw_calls": [
            re.compile(r"^RHI/DrawCalls$", re.I),
            re.compile(r"^DrawCalls?$", re.I),
            re.compile(r"draw.*calls?", re.I),
        ],
        "physical_used_mib": [
            re.compile(r"^PhysicalUsedMB$", re.I),
        ],
    }
    columns = {name: find_column(header, regexes) for name, regexes in patterns.items()}
    if columns["frame"] is None:
        return result
    values = {name: [] for name in columns}
    for row in rows[header_index + 1 :]:
        for name, index in columns.items():
            if index is None or index >= len(row):
                continue
            parsed = number(row[index])
            if parsed is not None and parsed >= 0:
                values[name].append(parsed)
    frames = [value for value in values["frame"] if value > 0]
    if not frames:
        return result
    gpu = values["gpu"]
    draws = values["draw_calls"]
    physical_used = values["physical_used_mib"]
    result["parseable"] = True
    result["frame_count"] = len(frames)
    result["columns"] = {
        name: header[index] if index is not None else None
        for name, index in columns.items()
        if name != "physical_used_mib"
    }
    memory_index = columns["physical_used_mib"]
    result["memory_column"] = (
        header[memory_index] if memory_index is not None else None
    )
    result["metrics"] = {
        "mean_frame_time_ms": statistics.fmean(frames),
        "p95_frame_time_ms": percentile(frames, 0.95),
        "frames_over_50_ms": sum(value > 50.0 for value in frames),
        "mean_gpu_time_ms": statistics.fmean(gpu) if gpu else None,
        "p95_gpu_time_ms": percentile(gpu, 0.95) if gpu else None,
        "p95_draw_calls": percentile(draws, 0.95) if draws else None,
        "peak_physical_used_mib": (
            max(physical_used) if physical_used else None
        ),
    }
    return result


def png_dimensions(path: Path) -> tuple[int, int] | None:
    if not path.is_file() or path.stat().st_size < 24:
        return None
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def scan_logs(paths: list[Path]) -> dict[str, Any]:
    lines: dict[str, list[str]] = {name: [] for name in CRITICAL_PATTERNS}
    texture_budget = []
    shader_compile = []
    shader_autogen = []
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            for name, pattern in CRITICAL_PATTERNS.items():
                if pattern.search(line):
                    lines[name].append(line.strip())
            if re.search(r"texture.*pool.*over budget", line, re.I):
                texture_budget.append(line.strip())
            if re.search(r"Compiling shader autogen file", line, re.I):
                shader_autogen.append(line.strip())
            elif re.search(
                r"shader compile job|Shaders left to compile|"
                r"Compiling\s+\d+\s+shader",
                line,
                re.I,
            ):
                shader_compile.append(line.strip())
    return {
        "critical_count": sum(len(items) for items in lines.values()),
        "critical_samples": {name: items[:20] for name, items in lines.items()},
        "texture_pool_over_budget_frames": len(texture_budget),
        "shader_compile_hits": len(shader_compile),
        "shader_autogen_header_hits": len(shader_autogen),
        "texture_budget_samples": texture_budget[:20],
        "shader_compile_samples": shader_compile[:20],
        "shader_autogen_header_samples": shader_autogen[:20],
    }


def process_stage_pass(stage: dict | None) -> bool:
    if not stage:
        return False
    return bool(
        stage.get("process_exit_observed")
        and not stage.get("timed_out")
        and stage.get("exit_code") in (None, 0)
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--latest-output", type=Path, required=True)
    args = parser.parse_args()

    contract = load_effective_contract()
    manifest = read_json(args.manifest)
    stages = {item["name"]: item for item in manifest.get("stages", [])}
    thresholds = contract["acceptance"]["cost"]
    baseline_file = ROOT / contract["baseline"]["file"]
    baseline_csv = Path(manifest["artifacts"].get("baseline_csv", ""))
    candidate_csv = Path(manifest["artifacts"].get("candidate_csv", ""))
    baseline_metrics = analyze_csv(baseline_csv)
    candidate_metrics = analyze_csv(candidate_csv)

    expected_captures = []
    for mode in ("baseline", "candidate"):
        root = Path(manifest["artifacts"][f"{mode}_capture_root"])
        expected_captures.extend(
            root / f"{mode}_lit_{camera['id']}.png"
            for camera in contract["capture"]["cameras"]
        )
    candidate_capture_root = Path(manifest["artifacts"]["candidate_capture_root"])
    is_attempt05 = (
        contract["contract_id"] == "P4.5-M01-LANDSCAPE-VISIBLE-005"
    )
    is_attempt06 = (
        contract["contract_id"] == "P4.5-M01-LANDSCAPE-VISIBLE-006"
    )
    is_repaired_attempt = is_attempt05 or is_attempt06
    if is_repaired_attempt:
        expected_captures.extend(
            candidate_capture_root
            / f"candidate_diagnostic_landscape_coverage_{camera['id']}.png"
            for camera in contract["capture"]["cameras"]
        )
        expected_captures.extend(
            [
                candidate_capture_root
                / "candidate_diagnostic_shader_complexity_C04.png",
                candidate_capture_root
                / "candidate_diagnostic_component_boundary_C05.png",
            ]
        )
    else:
        expected_captures.extend(
            [
                candidate_capture_root
                / "candidate_diagnostic_landscape_lod_C05.png",
                candidate_capture_root
                / "candidate_diagnostic_shader_complexity_C04.png",
                candidate_capture_root
                / "candidate_diagnostic_component_boundary_C05.png",
            ]
        )
    capture_records = [
        {
            "path": str(path),
            "exists": path.is_file(),
            "bytes": path.stat().st_size if path.is_file() else 0,
            "sha256": sha256_file(path) if path.is_file() else None,
            "dimensions": list(png_dimensions(path))
            if png_dimensions(path) is not None
            else None,
        }
        for path in expected_captures
    ]

    measured_logs = [
        Path(stages[name][key])
        for name in ("baseline_profile_measured", "candidate_profile_measured")
        if name in stages
        for key in ("stdout", "stderr", "engine_log")
        if stages[name].get(key)
    ]
    all_logs = [
        Path(stage[key])
        for stage in stages.values()
        for key in ("stdout", "stderr", "engine_log")
        if stage.get(key)
    ]
    measured_scan = scan_logs(measured_logs)
    all_scan = scan_logs(all_logs)

    base = baseline_metrics.get("metrics", {})
    cand = candidate_metrics.get("metrics", {})
    required_metric_names = (
        "mean_frame_time_ms",
        "p95_frame_time_ms",
        "mean_gpu_time_ms",
        "p95_gpu_time_ms",
        "p95_draw_calls",
    )
    metrics_complete = bool(
        baseline_metrics["parseable"]
        and candidate_metrics["parseable"]
        and all(base.get(name) is not None for name in required_metric_names)
        and all(cand.get(name) is not None for name in required_metric_names)
    )
    deltas = {
        name: (cand[name] - base[name]) if metrics_complete else None
        for name in (
            "mean_frame_time_ms",
            "p95_frame_time_ms",
            "p95_gpu_time_ms",
            "p95_draw_calls",
        )
    }
    baseline_stage_peak = stages.get("baseline_profile_measured", {}).get(
        "peak_working_set_mib"
    )
    candidate_stage_peak = stages.get("candidate_profile_measured", {}).get(
        "peak_working_set_mib"
    )
    baseline_csv_peak = base.get("peak_physical_used_mib")
    candidate_csv_peak = cand.get("peak_physical_used_mib")
    if baseline_stage_peak is not None and candidate_stage_peak is not None:
        baseline_peak = baseline_stage_peak
        candidate_peak = candidate_stage_peak
        working_set_source = "supervisor_stage_peak_working_set_mib"
    elif baseline_csv_peak is not None and candidate_csv_peak is not None:
        # Attempt06 Recovery01's supervisor omitted the process peak from its
        # stage schema. PhysicalUsedMB is sampled during the governed measured
        # interval in the immutable UE CSV and is therefore an evidence-backed
        # fallback, not a fabricated estimate.
        baseline_peak = baseline_csv_peak
        candidate_peak = candidate_csv_peak
        working_set_source = "immutable_csv_PhysicalUsedMB"
    else:
        baseline_peak = None
        candidate_peak = None
        working_set_source = None
    working_set_delta = (
        candidate_peak - baseline_peak
        if baseline_peak is not None and candidate_peak is not None
        else None
    )

    editor_acceptance_path = Path(
        manifest["artifacts"].get("editor_acceptance", "")
    )
    editor_acceptance = (
        read_json(editor_acceptance_path)
        if editor_acceptance_path.is_file()
        else {}
    )
    human_review_path = (
        ROOT
        / "Saved/Reports"
        / (
            "PHASE4_M01_LANDSCAPE_VISIBLE_HUMAN_REVIEW_ATTEMPT06.json"
            if is_attempt06
            else "PHASE4_M01_LANDSCAPE_VISIBLE_HUMAN_REVIEW_ATTEMPT05.json"
        )
        if is_repaired_attempt
        else HUMAN_REVIEW_PATH
    )
    human_review = (
        read_json(human_review_path) if human_review_path.is_file() else {}
    )
    required_human = (
        "all_components_visible_in_C05",
        "no_vertical_edge_cliff_inside_route_view",
        "no_floating_landscape_pixels",
        "no_flat_infinite_slab_read",
        "no_visible_component_cracks",
        "no_visible_black_seam_lines",
        "no_z_fighting_after_warmup",
        "no_C03_district_gap_pixels",
        "shoreline_transition_continuous",
        "water_below_landscape_and_beach",
        "shoreline_world_fixed",
    )
    human_complete = bool(
        human_review.get("contract_id") == contract["contract_id"]
        and all(human_review.get("checks", {}).get(name) is True for name in required_human)
    )

    repaired_visual = (
        analyze_attempt06_visuals(contract, candidate_capture_root)
        if is_attempt06
        else (
            analyze_attempt05_visuals(contract, candidate_capture_root)
            if is_attempt05
            else {}
        )
    )
    profile_receipts = []
    if is_repaired_attempt:
        for key in ("baseline_profile_receipt", "candidate_profile_receipt"):
            path = Path(manifest["artifacts"].get(key, ""))
            profile_receipts.append(read_json(path) if path.is_file() else {})
    checks = {
        "contract_id_exact": manifest.get("contract_id") == contract["contract_id"],
        "baseline_hash_unchanged": (
            baseline_file.is_file()
            and sha256_file(baseline_file) == contract["baseline"]["sha256"]
            and manifest.get("baseline_sha256_before") == contract["baseline"]["sha256"]
            and manifest.get("baseline_sha256_after") == contract["baseline"]["sha256"]
        ),
        "candidate_hashes_unchanged": bool(
            manifest.get("candidate_sha256_before")
            and manifest.get("candidate_material_sha256_before")
            and manifest.get("candidate_sha256_before")
            == manifest.get("candidate_sha256_after")
            and manifest.get("candidate_material_sha256_before")
            == manifest.get("candidate_material_sha256_after")
        ),
        "candidate_editor_acceptance": editor_acceptance.get("gate") == "PASS",
        "all_stages_bounded_and_clean": all(
            process_stage_pass(stage) for stage in stages.values()
        ),
        "exact_capture_count": len(capture_records) == (
            17 if is_repaired_attempt else 13
        ),
        "all_captures_present": all(item["exists"] and item["bytes"] > 0 for item in capture_records),
        "all_captures_exact_1920x1080": all(
            item["dimensions"] == [1920, 1080] for item in capture_records
        ),
        "profile_metrics_complete": metrics_complete,
        "candidate_mean_frame_within_budget": bool(
            metrics_complete
            and cand["mean_frame_time_ms"] <= thresholds["mean_frame_time_ms_max"]
        ),
        "candidate_p95_frame_within_budget": bool(
            metrics_complete
            and cand["p95_frame_time_ms"] <= thresholds["p95_frame_time_ms_max"]
        ),
        "candidate_mean_gpu_within_budget": bool(
            metrics_complete
            and cand["mean_gpu_time_ms"] <= thresholds["mean_gpu_time_ms_max"]
        ),
        "candidate_p95_gpu_within_budget": bool(
            metrics_complete
            and cand["p95_gpu_time_ms"] <= thresholds["p95_gpu_time_ms_max"]
        ),
        "mean_frame_delta_within_budget": bool(
            metrics_complete
            and deltas["mean_frame_time_ms"]
            <= thresholds["candidate_minus_baseline_mean_frame_time_ms_max"]
        ),
        "p95_frame_delta_within_budget": bool(
            metrics_complete
            and deltas["p95_frame_time_ms"]
            <= thresholds["candidate_minus_baseline_p95_frame_time_ms_max"]
        ),
        "p95_gpu_delta_within_budget": bool(
            metrics_complete
            and deltas["p95_gpu_time_ms"]
            <= thresholds["candidate_minus_baseline_p95_gpu_time_ms_max"]
        ),
        "draw_call_delta_within_budget": bool(
            metrics_complete
            and deltas["p95_draw_calls"]
            <= thresholds["candidate_minus_baseline_draw_calls_max"]
        ),
        "working_set_delta_available": working_set_delta is not None,
        "working_set_delta_within_budget": bool(
            working_set_delta is not None
            and working_set_delta
            <= thresholds["candidate_minus_baseline_peak_working_set_mib_max"]
        ),
        "no_frames_over_50ms": bool(
            metrics_complete
            and cand["frames_over_50_ms"]
            == thresholds["frames_over_50_ms_after_warmup"]
        ),
        "no_texture_pool_over_budget": (
            measured_scan["texture_pool_over_budget_frames"]
            == thresholds["texture_pool_over_budget_frames"]
        ),
        "no_shader_compiles_measured": (
            measured_scan["shader_compile_hits"]
            == thresholds["shader_compiles_during_measured_interval"]
        ),
        "no_critical_logs": (
            all_scan["critical_count"] == thresholds["critical_log_hits"]
        ),
    }
    if is_repaired_attempt:
        checks.update(
            {
                "all_five_landscape_coverage_and_readability_gates": bool(
                    repaired_visual.get(
                        "all_camera_coverage_and_readability_pass"
                    )
                ),
                "all_16_component_ids_visible": bool(
                    repaired_visual.get("all_16_component_ids_visible")
                ),
                "diagnostic_hashes_distinct_from_lit": bool(
                    repaired_visual.get(
                        "diagnostic_hashes_distinct_from_lit"
                    )
                ),
                "same_process_profile_receipts_exact": bool(
                    len(profile_receipts) == 2
                    and all(
                        receipt.get("gate") == "PASS"
                        and receipt.get("contract_id")
                        == contract["contract_id"]
                        and receipt.get(
                            "same_process_warmup_and_measurement"
                        )
                        is True
                        and receipt.get("startup_frames_excluded") is True
                        and receipt.get("warmup_seconds") == 30
                        and receipt.get("measured_seconds") == 60
                        and receipt.get("rhi", "").find("D3D12") >= 0
                        and receipt.get("feature_level") == "SM6"
                        for receipt in profile_receipts
                    )
                ),
                "profile_commandline_has_no_boot_capture": all(
                    "-csvCaptureFrames"
                    not in str(
                        stage.get("command_line")
                        or " ".join(
                            str(item) for item in stage.get("command", [])
                        )
                    )
                    for name, stage in stages.items()
                    if name in {
                        "baseline_profile_measured",
                        "candidate_profile_measured",
                    }
                ),
            }
        )
    if is_attempt06:
        required_manifest_fields = {
            "camera_id",
            "exact_location_cm",
            "exact_rotation_degrees",
            "camera_transform_authority",
            "forward_ray_intersects_bounds",
            "projected_top_surface_fraction",
            "show_only_component_count",
            "generated_material_instance_count",
            "material_parent_match_count",
            "render_thread_synchronization_complete",
        }
        candidate_manifest_path = (
            candidate_capture_root / "capture_manifest.json"
        )
        candidate_manifest = (
            read_json(candidate_manifest_path)
            if candidate_manifest_path.is_file()
            else {}
        )
        candidate_files = candidate_manifest.get("files", [])
        diagnostic_files = [
            record
            for record in candidate_files
            if "diagnostic_landscape_coverage_" in record.get("path", "")
            or "diagnostic_component_boundary_" in record.get("path", "")
        ]
        checks.update(
            {
                "attempt06_contract_only_camera_transforms": bool(
                    candidate_manifest.get("camera_transform_authority")
                    == "contract_only"
                    and candidate_manifest.get(
                        "serialized_camera_actor_fallback_used"
                    )
                    is False
                    and len(candidate_files) == 12
                    and all(
                        required_manifest_fields.issubset(record)
                        and record.get("camera_transform_authority")
                        == "contract_only"
                        for record in candidate_files
                    )
                ),
                "attempt06_diagnostics_explicit_16_and_synchronized": bool(
                    len(diagnostic_files) == 6
                    and all(
                        record.get("show_only_component_count") == 16
                        and record.get(
                            "generated_material_instance_count"
                        )
                        == 16
                        and record.get("material_parent_match_count") == 16
                        and record.get(
                            "render_thread_synchronization_complete"
                        )
                        is True
                        for record in diagnostic_files
                    )
                ),
                "attempt06_exact_component_palette_gate": bool(
                    repaired_visual.get(
                        "generic_color_bucket_count_used"
                    )
                    is False
                    and repaired_visual.get(
                        "all_16_component_ids_visible"
                    )
                    is True
                ),
            }
        )
    technical_gate = "PASS" if all(checks.values()) else "FAIL"
    gate = (
        "PASS"
        if technical_gate == "PASS" and human_complete
        else ("INCOMPLETE_HUMAN_REVIEW" if technical_gate == "PASS" else "FAIL")
    )
    report = {
        "schema": "skyguard.phase4.m01-landscape-visible-gpu-gate.v1",
        "contract_id": contract["contract_id"],
        "gate": gate,
        "technical_gate": technical_gate,
        "human_review_complete": human_complete,
        "human_review_path": str(human_review_path),
        "checks": checks,
        "baseline_profile": baseline_metrics,
        "candidate_profile": candidate_metrics,
        "candidate_minus_baseline": {
            **deltas,
            "peak_working_set_mib": working_set_delta,
            "peak_working_set_source": working_set_source,
        },
        "capture_records": capture_records,
        "repaired_attempt_automatic_visual_analysis": repaired_visual,
        "profile_receipts": profile_receipts,
        "measured_log_scan": measured_scan,
        "all_stage_log_scan": all_scan,
        "injected_module_candidates": sorted(
            {
                path
                for stage in stages.values()
                for path in stage.get("injected_module_candidates", [])
            }
        ),
        "promotion": {
            "landscape_material_visible_acceptance": gate == "PASS",
            "shoreline_relationship_acceptance": gate == "PASS",
            "landscape_cost_acceptance": gate == "PASS",
            "production_vegetation_complete": False,
            "mission01_aaa_complete": False,
        },
        "limitations": (
            []
            if human_complete
            else [
                "Technical evidence cannot replace the required human visual rubric."
            ]
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    args.latest_output.parent.mkdir(parents=True, exist_ok=True)
    args.latest_output.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if gate == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
