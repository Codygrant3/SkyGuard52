"""Deterministic offline camera-to-Landscape proof for immutable Attempt06.

The proof intentionally uses only the governed heightmap, serialized actor
transform, contract camera transforms, and a 90-degree horizontal field of
view.  It does not launch Unreal or inspect mutable editor state.
"""

from __future__ import annotations

import math
import struct
from pathlib import Path
from typing import Iterable


ROOT = Path(r"D:\Skyguard52")
HEIGHTMAP = (
    ROOT
    / "Content/Skyguard/Environment/Source/Mission01/"
    "HM_M01_CoastalProduction_505x127.r16"
)
WIDTH = 505
HEIGHT = 127
ACTOR_LOCATION_CM = (0.0, 7000.0, -120.0)
ACTOR_SCALE = (100.0, 100.0, 100.0)
COMPONENT_QUADS = 63
COMPONENTS_X = 8
COMPONENTS_Y = 2
HORIZONTAL_FOV_DEGREES = 90.0
ASPECT_RATIO = 16.0 / 9.0
CAPTURE_WIDTH = 1920
CAPTURE_HEIGHT = 1080


ATTEMPT06_CAMERAS = (
    {
        "id": "C01_ESTABLISHING_HIGH",
        "location_cm": (25200.0, -8000.0, 10000.0),
        "rotation_degrees": {
            "pitch": -25.226895,
            "yaw": 90.0,
            "roll": 0.0,
        },
        "purpose": "high coastal establishing view with route context",
        "minimum_landscape_pixel_fraction": 0.08,
    },
    {
        "id": "C02_SHORELINE_GRAZE",
        "location_cm": (25200.0, 4000.0, 1200.0),
        "rotation_degrees": {
            "pitch": -8.530766,
            "yaw": 90.0,
            "roll": 0.0,
        },
        "purpose": "low ocean-beach-landscape continuity view",
        "minimum_landscape_pixel_fraction": 0.10,
    },
    {
        "id": "C03_ROUTE_LOW",
        "location_cm": (-5000.0, 13300.0, 1500.0),
        "rotation_degrees": {
            "pitch": -3.433630,
            "yaw": 0.0,
            "roll": 0.0,
        },
        "purpose": "longitudinal low route and component seam view",
        "minimum_landscape_pixel_fraction": 0.05,
    },
    {
        "id": "C04_INLAND_CLOSE",
        "location_cm": (25200.0, 5000.0, 3000.0),
        "rotation_degrees": {
            "pitch": -19.872176,
            "yaw": 90.0,
            "roll": 0.0,
        },
        "purpose": "close material readability and shoreline transition",
        "minimum_landscape_pixel_fraction": 0.30,
    },
    {
        "id": "C05_COVERAGE_HIGH",
        "location_cm": (25200.0, 13300.0, 30000.0),
        "rotation_degrees": {
            "pitch": -90.0,
            "yaw": 90.0,
            "roll": 0.0,
        },
        "purpose": "orthographic-like perspective proof of all 16 components",
        "minimum_landscape_pixel_fraction": 0.20,
    },
)

ATTEMPT05_ACTUAL_CAMERAS = (
    {
        "id": "C01_ROUTE_WIDE",
        "location_cm": (22500.0, -9000.0, 8500.0),
        "rotation_degrees": {"pitch": -28.0, "yaw": 90.0, "roll": 0.0},
        "minimum_landscape_pixel_fraction": 0.08,
    },
    {
        "id": "C02_SHORE_APPROACH",
        "location_cm": (22500.0, 3000.0, 900.0),
        "rotation_degrees": {"pitch": -6.0, "yaw": 90.0, "roll": 0.0},
        "minimum_landscape_pixel_fraction": 0.10,
    },
    {
        "id": "C03_SHORE_GRAZE",
        "location_cm": (6000.0, 6600.0, 220.0),
        "rotation_degrees": {"pitch": -2.0, "yaw": 0.0, "roll": 0.0},
        "minimum_landscape_pixel_fraction": 0.05,
    },
    {
        "id": "C04_INLAND_CLOSE",
        "location_cm": (22500.0, 9600.0, 800.0),
        "rotation_degrees": {"pitch": -12.0, "yaw": 25.0, "roll": 0.0},
        "minimum_landscape_pixel_fraction": 0.30,
    },
    {
        "id": "C05_COVERAGE_HIGH",
        "location_cm": (22500.0, 3000.0, 12000.0),
        "rotation_degrees": {"pitch": -42.0, "yaw": 90.0, "roll": 0.0},
        "minimum_landscape_pixel_fraction": 0.20,
    },
)


def landscape_bounds() -> dict:
    raw = HEIGHTMAP.read_bytes()
    expected_bytes = WIDTH * HEIGHT * 2
    if len(raw) != expected_bytes:
        raise ValueError(
            f"heightmap bytes {len(raw)} != governed {expected_bytes}"
        )
    values = struct.unpack(f"<{WIDTH * HEIGHT}H", raw)
    minimum_height = min(values)
    maximum_height = max(values)
    z_scale_cm_per_sample = ACTOR_SCALE[2] / 128.0
    return {
        "heightmap": str(HEIGHTMAP),
        "heightmap_dimensions": [WIDTH, HEIGHT],
        "height_sample_min": minimum_height,
        "height_sample_max": maximum_height,
        "minimum_cm": [
            ACTOR_LOCATION_CM[0],
            ACTOR_LOCATION_CM[1],
            ACTOR_LOCATION_CM[2]
            + (minimum_height - 32768) * z_scale_cm_per_sample,
        ],
        "maximum_cm": [
            ACTOR_LOCATION_CM[0] + (WIDTH - 1) * ACTOR_SCALE[0],
            ACTOR_LOCATION_CM[1] + (HEIGHT - 1) * ACTOR_SCALE[1],
            ACTOR_LOCATION_CM[2]
            + (maximum_height - 32768) * z_scale_cm_per_sample,
        ],
        "component_count": COMPONENTS_X * COMPONENTS_Y,
        "component_grid": [COMPONENTS_X, COMPONENTS_Y],
        "component_size_cm": COMPONENT_QUADS * ACTOR_SCALE[0],
    }


def _dot(left: Iterable[float], right: Iterable[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def _subtract(left: Iterable[float], right: Iterable[float]) -> tuple:
    return tuple(a - b for a, b in zip(left, right))


def camera_basis(rotation: dict) -> tuple[tuple, tuple, tuple]:
    pitch = math.radians(rotation["pitch"])
    yaw = math.radians(rotation["yaw"])
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    forward = (cp * cy, cp * sy, sp)
    right = (-sy, cy, 0.0)
    up = (-sp * cy, -sp * sy, cp)
    return forward, right, up


def project_point(camera: dict, point: Iterable[float]) -> tuple | None:
    forward, right, up = camera_basis(camera["rotation_degrees"])
    relative = _subtract(point, camera["location_cm"])
    depth = _dot(relative, forward)
    if depth <= 1.0:
        return None
    tangent_horizontal = math.tan(
        math.radians(HORIZONTAL_FOV_DEGREES * 0.5)
    )
    tangent_vertical = tangent_horizontal / ASPECT_RATIO
    return (
        _dot(relative, right) / (depth * tangent_horizontal),
        _dot(relative, up) / (depth * tangent_vertical),
        depth,
    )


def _clip_polygon_axis(
    polygon: list[tuple[float, float]],
    axis: int,
    boundary: float,
    keep_less: bool,
) -> list[tuple[float, float]]:
    if not polygon:
        return []

    def inside(point: tuple[float, float]) -> bool:
        return (
            point[axis] <= boundary
            if keep_less
            else point[axis] >= boundary
        )

    def intersection(start, end):
        delta = end[axis] - start[axis]
        if abs(delta) < 1e-12:
            return start
        factor = (boundary - start[axis]) / delta
        return (
            start[0] + factor * (end[0] - start[0]),
            start[1] + factor * (end[1] - start[1]),
        )

    result = []
    previous = polygon[-1]
    previous_inside = inside(previous)
    for current in polygon:
        current_inside = inside(current)
        if current_inside:
            if not previous_inside:
                result.append(intersection(previous, current))
            result.append(current)
        elif previous_inside:
            result.append(intersection(previous, current))
        previous = current
        previous_inside = current_inside
    return result


def clip_to_viewport(
    polygon: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    result = polygon
    for axis, boundary, keep_less in (
        (0, -1.0, False),
        (0, 1.0, True),
        (1, -1.0, False),
        (1, 1.0, True),
    ):
        result = _clip_polygon_axis(result, axis, boundary, keep_less)
    return result


def polygon_area(polygon: list[tuple[float, float]]) -> float:
    if len(polygon) < 3:
        return 0.0
    doubled = 0.0
    for index, current in enumerate(polygon):
        following = polygon[(index + 1) % len(polygon)]
        doubled += current[0] * following[1] - following[0] * current[1]
    return abs(doubled) * 0.5


def projected_surface_fraction(camera: dict, bounds: dict) -> float:
    minimum = bounds["minimum_cm"]
    maximum = bounds["maximum_cm"]
    z = maximum[2]
    corners = (
        (minimum[0], minimum[1], z),
        (maximum[0], minimum[1], z),
        (maximum[0], maximum[1], z),
        (minimum[0], maximum[1], z),
    )
    projected = [project_point(camera, corner) for corner in corners]
    if any(point is None for point in projected):
        return 0.0
    polygon = [(point[0], point[1]) for point in projected]
    # NDC viewport area is four; convert clipped NDC area to pixel fraction.
    return polygon_area(clip_to_viewport(polygon)) / 4.0


def ray_intersects_bounds(camera: dict, bounds: dict) -> bool:
    origin = camera["location_cm"]
    direction = camera_basis(camera["rotation_degrees"])[0]
    minimum = bounds["minimum_cm"]
    maximum = bounds["maximum_cm"]
    near = 0.0
    far = float("inf")
    for axis in range(3):
        if abs(direction[axis]) < 1e-12:
            if origin[axis] < minimum[axis] or origin[axis] > maximum[axis]:
                return False
            continue
        first = (minimum[axis] - origin[axis]) / direction[axis]
        second = (maximum[axis] - origin[axis]) / direction[axis]
        if first > second:
            first, second = second, first
        near = max(near, first)
        far = min(far, second)
        if near > far:
            return False
    return far >= max(near, 0.0)


def c05_component_coverage_proof(camera: dict, bounds: dict) -> dict:
    if camera["id"] != "C05_COVERAGE_HIGH":
        raise ValueError("all-component proof is defined for C05 only")
    component_size = bounds["component_size_cm"]
    minimum = bounds["minimum_cm"]
    z_values = (bounds["minimum_cm"][2], bounds["maximum_cm"][2])
    components = []
    all_corners_inside = True
    for y_index in range(COMPONENTS_Y):
        for x_index in range(COMPONENTS_X):
            x0 = minimum[0] + x_index * component_size
            x1 = x0 + component_size
            y0 = minimum[1] + y_index * component_size
            y1 = y0 + component_size
            projections = [
                project_point(camera, (x, y, z))
                for x in (x0, x1)
                for y in (y0, y1)
                for z in z_values
            ]
            if any(point is None for point in projections):
                inside = False
                min_pixel_area = 0.0
                ndc_bounds = None
            else:
                xs = [point[0] for point in projections]
                ys = [point[1] for point in projections]
                inside = (
                    min(xs) >= -1.0
                    and max(xs) <= 1.0
                    and min(ys) >= -1.0
                    and max(ys) <= 1.0
                )
                # The farthest plane gives the conservative perspective area.
                far_z = bounds["minimum_cm"][2]
                far_points = [
                    project_point(camera, (x, y, far_z))
                    for x in (x0, x1)
                    for y in (y0, y1)
                ]
                far_xs = [point[0] for point in far_points]
                far_ys = [point[1] for point in far_points]
                width_pixels = (
                    (max(far_xs) - min(far_xs)) * 0.5 * CAPTURE_WIDTH
                )
                height_pixels = (
                    (max(far_ys) - min(far_ys)) * 0.5 * CAPTURE_HEIGHT
                )
                min_pixel_area = width_pixels * height_pixels
                ndc_bounds = [min(xs), min(ys), max(xs), max(ys)]
            all_corners_inside &= inside
            components.append(
                {
                    "component_id": y_index * COMPONENTS_X + x_index,
                    "grid": [x_index, y_index],
                    "all_8_bounds_corners_inside_viewport": inside,
                    "ndc_bounds": ndc_bounds,
                    "conservative_projected_pixel_area": min_pixel_area,
                }
            )
    return {
        "all_16_component_bounds_inside_viewport": all_corners_inside,
        "component_count": len(components),
        "minimum_conservative_component_pixel_area": min(
            item["conservative_projected_pixel_area"] for item in components
        ),
        "components": components,
    }


def build_proof() -> dict:
    bounds = landscape_bounds()
    attempt05_camera_results = []
    for camera in ATTEMPT05_ACTUAL_CAMERAS:
        fraction = projected_surface_fraction(camera, bounds)
        ray_hit = ray_intersects_bounds(camera, bounds)
        attempt05_camera_results.append(
            {
                **camera,
                "location_cm": list(camera["location_cm"]),
                "forward_ray_intersects_landscape_bounds": ray_hit,
                "projected_top_surface_fraction": fraction,
                "offline_framing_pass": (
                    ray_hit
                    and fraction
                    >= camera["minimum_landscape_pixel_fraction"]
                ),
            }
        )
    camera_results = []
    for camera in ATTEMPT06_CAMERAS:
        fraction = projected_surface_fraction(camera, bounds)
        camera_results.append(
            {
                **camera,
                "location_cm": list(camera["location_cm"]),
                "forward_ray_intersects_landscape_bounds": (
                    ray_intersects_bounds(camera, bounds)
                ),
                "projected_top_surface_fraction": fraction,
                "threshold_margin": (
                    fraction - camera["minimum_landscape_pixel_fraction"]
                ),
                "offline_framing_pass": (
                    ray_intersects_bounds(camera, bounds)
                    and fraction
                    >= camera["minimum_landscape_pixel_fraction"]
                ),
            }
        )
    c05 = next(
        camera for camera in ATTEMPT06_CAMERAS
        if camera["id"] == "C05_COVERAGE_HIGH"
    )
    all_components = c05_component_coverage_proof(c05, bounds)
    return {
        "schema": "skyguard.phase4.m01-attempt06-camera-proof.v1",
        "method": (
            "90-degree horizontal perspective projection of the governed "
            "Landscape bounds, clipped to a 16:9 viewport"
        ),
        "landscape_bounds": bounds,
        "attempt05_actual_camera_results": attempt05_camera_results,
        "attempt05_all_five_camera_framing_proofs_pass": all(
            result["offline_framing_pass"]
            for result in attempt05_camera_results
        ),
        "camera_results": camera_results,
        "all_five_camera_framing_proofs_pass": all(
            result["offline_framing_pass"] for result in camera_results
        ),
        "c05_all_component_proof": all_components,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build_proof(), indent=2))
