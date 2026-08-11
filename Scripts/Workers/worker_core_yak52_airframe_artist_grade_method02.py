from __future__ import annotations

"""Yak-52 artist-grade Method02: reference station cage + separate systems.

This lane does not cosmetically repair the rejected Recovery01 GLB and must not
reuse Production/Attempts/core-yak52-airframe* namespaces. Dimensional and
socket authority may be loaded from the governed source blend path when Blender
is available; production surfaces are built fresh from the station cage.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "core-yak52-airframe-artist-grade-method02"
SOURCE_BLEND = (
    PROJECT_ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "Mission01"
    / "Yak52_Uplift_003_R3"
    / "BLD_M01_YAK_UPLIFT_003_R3_MASTER.blend"
)
CONTRACT = (
    PROJECT_ROOT
    / "Docs"
    / "AAA_Review"
    / "PHASE2_YAK52_AIRFRAME_ARTIST_GRADE_METHOD02_CONTRACT.json"
)
SYSTEMS = (
    PROJECT_ROOT
    / "Docs"
    / "AAA_Review"
    / "PHASE2_YAK52_AIRFRAME_ARTIST_GRADE_METHOD02_SYSTEMS.json"
)
STATION_CAGE = (
    PROJECT_ROOT
    / "Docs"
    / "AAA_Review"
    / "PHASE2_YAK52_AIRFRAME_ARTIST_GRADE_METHOD02_SILHOUETTE_STATION_CAGE.json"
)
CAMERAS = (
    PROJECT_ROOT
    / "Docs"
    / "AAA_Review"
    / "PHASE2_YAK52_AIRFRAME_ARTIST_GRADE_METHOD02_CAMERAS.json"
)
RUBRIC = (
    PROJECT_ROOT
    / "Docs"
    / "AAA_Review"
    / "PHASE2_YAK52_AIRFRAME_ARTIST_GRADE_METHOD02_VISUAL_RUBRIC.json"
)
FAILED_ATTEMPT_ROOTS = (
    PROJECT_ROOT / "Production" / "Attempts" / "core-yak52-airframe",
    PROJECT_ROOT / "Production" / "Attempts" / "core-yak52-airframe-recovery01",
)

AUTHORITATIVE = {
    "overall_length_m": 7.745,
    "overall_height_m": 2.7,
    "wingspan_m": 9.3,
    "horizontal_tail_span_m": 3.16,
    "propeller_diameter_m": 2.4,
    "gear_track_m": 2.715,
    "wheelbase_m": 1.285,
}

REQUIRED_SOCKETS = {
    "SOCKET_Origin": (0.0, 0.0, 0.0),
    "SOCKET_Propeller": (3.82, 0.0, 1.22),
    "SOCKET_MainGear_L": (0.42, -1.3575, 0.44),
    "SOCKET_MainGear_R": (0.42, 1.3575, 0.44),
    "SOCKET_NoseGear": (1.705, 0.0, 0.38),
    "SOCKET_CanopyRearClosed": (-0.62, 0.0, 1.56),
    "SOCKET_CanopyRearOpen": (-1.32, 0.0, 1.56),
    "SOCKET_RearGunnerCamera": (-0.78, -0.36, 1.55),
    "SOCKET_RifleClearance": (-0.35, -0.72, 1.58),
    "SOCKET_IglaBackblast": (-1.42, 0.70, 1.58),
}

SYSTEM_OBJECT_NAMES = (
    "SYS_Cowling",
    "SYS_Fuselage",
    "SYS_Wing",
    "SYS_Empennage",
    "SYS_Canopy",
    "SYS_LandingGear",
    "SYS_Propeller",
    "SYS_ControlSurfaces",
)


class Method02Error(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    source = list(sys.argv)
    if "--" in source:
        source = source[source.index("--") + 1 :]
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    args = parser.parse_args(source)
    if args.asset_id != ASSET_ID:
        raise Method02Error(f"Unexpected asset id: {args.asset_id}")
    return args


def assert_fresh_namespace(output: Path) -> None:
    resolved = output.resolve()
    for forbidden in FAILED_ATTEMPT_ROOTS:
        try:
            resolved.relative_to(forbidden.resolve())
            raise Method02Error(
                f"Method02 must not write into failed namespace: {forbidden}"
            )
        except ValueError:
            continue
    if "core-yak52-airframe-artist-grade-method02" not in str(resolved):
        raise Method02Error(
            "Output must remain under the Method02 fresh attempt namespace."
        )


def load_station_profiles(path: Path | None = None) -> list[dict[str, float | str]]:
    payload = json.loads((path or STATION_CAGE).read_text(encoding="utf-8"))
    stations = payload.get("stations")
    if not isinstance(stations, list) or len(stations) < 5:
        raise Method02Error("Station cage authority is incomplete.")
    profiles: list[dict[str, float | str]] = []
    for station in stations:
        profiles.append(
            {
                "id": str(station["id"]),
                "x_m": float(station["x_m"]),
                "half_width_m": float(station["half_width_m"]),
                "half_height_m": float(station["half_height_m"]),
                "role": str(station.get("role", "")),
            }
        )
    return profiles


def fuselage_width_variation(profiles: list[dict[str, float | str]]) -> float:
    widths = [float(profile["half_width_m"]) for profile in profiles]
    mean = sum(widths) / len(widths)
    if mean <= 1e-9:
        raise Method02Error("Station cage mean width is zero.")
    variance = sum((width - mean) ** 2 for width in widths) / len(widths)
    return math.sqrt(variance) / mean


def ellipse_points(
    half_width: float, half_height: float, segments: int = 16
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for index in range(segments):
        angle = (2.0 * math.pi * index) / segments
        points.append((half_width * math.cos(angle), half_height * math.sin(angle)))
    return points


def project_point_perspective(
    point: tuple[float, float, float],
    camera: tuple[float, float, float],
    target: tuple[float, float, float],
    lens_mm: float,
    sensor_width_mm: float = 36.0,
) -> tuple[float, float] | None:
    """Project a world point into approximate NDC for framing gates (offline-safe)."""
    forward = (
        target[0] - camera[0],
        target[1] - camera[1],
        target[2] - camera[2],
    )
    forward_length = math.sqrt(sum(axis * axis for axis in forward))
    if forward_length <= 1e-9:
        return None
    forward = tuple(axis / forward_length for axis in forward)
    world_up = (0.0, 0.0, 1.0)
    right = (
        forward[1] * world_up[2] - forward[2] * world_up[1],
        forward[2] * world_up[0] - forward[0] * world_up[2],
        forward[0] * world_up[1] - forward[1] * world_up[0],
    )
    right_length = math.sqrt(sum(axis * axis for axis in right))
    if right_length <= 1e-9:
        return None
    right = tuple(axis / right_length for axis in right)
    up = (
        right[1] * forward[2] - right[2] * forward[1],
        right[2] * forward[0] - right[0] * forward[2],
        right[0] * forward[1] - right[1] * forward[0],
    )
    delta = (point[0] - camera[0], point[1] - camera[1], point[2] - camera[2])
    depth = delta[0] * forward[0] + delta[1] * forward[1] + delta[2] * forward[2]
    if depth <= 1e-6:
        return None
    x = delta[0] * right[0] + delta[1] * right[1] + delta[2] * right[2]
    y = delta[0] * up[0] + delta[1] * up[1] + delta[2] * up[2]
    half_width = depth * math.tan(0.5 * math.atan(sensor_width_mm / max(lens_mm, 1e-6)))
    aspect = 16.0 / 9.0
    half_height = half_width / aspect
    if half_width <= 1e-9 or half_height <= 1e-9:
        return None
    return x / half_width, y / half_height


def framing_coverage(
    bounds_min: tuple[float, float, float],
    bounds_max: tuple[float, float, float],
    camera: tuple[float, float, float],
    target: tuple[float, float, float],
    lens_mm: float,
) -> float:
    corners = [
        (x, y, z)
        for x in (bounds_min[0], bounds_max[0])
        for y in (bounds_min[1], bounds_max[1])
        for z in (bounds_min[2], bounds_max[2])
    ]
    projected = [
        project_point_perspective(corner, camera, target, lens_mm) for corner in corners
    ]
    valid = [point for point in projected if point is not None]
    if len(valid) < 2:
        return 0.0
    xs = [point[0] for point in valid]
    ys = [point[1] for point in valid]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    # Coverage against a full NDC square of width/height 2.
    return max(0.0, min(1.0, (width * height) / 4.0))


def evaluate_framing_gates(
    views: list[dict[str, Any]],
    subject_bounds: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]],
    minimum_coverage: float,
    maximum_coverage: float,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for view in views:
        subject = str(view.get("subject", "ALL_SYSTEMS"))
        if subject == "ALL_SYSTEMS":
            mins = [bounds[0] for bounds in subject_bounds.values()]
            maxs = [bounds[1] for bounds in subject_bounds.values()]
            bounds_min = (
                min(point[0] for point in mins),
                min(point[1] for point in mins),
                min(point[2] for point in mins),
            )
            bounds_max = (
                max(point[0] for point in maxs),
                max(point[1] for point in maxs),
                max(point[2] for point in maxs),
            )
        else:
            names = [name.strip() for name in subject.split(",") if name.strip()]
            missing = [name for name in names if name not in subject_bounds]
            if missing:
                raise Method02Error(f"Framing subject missing bounds: {missing}")
            mins = [subject_bounds[name][0] for name in names]
            maxs = [subject_bounds[name][1] for name in names]
            bounds_min = (
                min(point[0] for point in mins),
                min(point[1] for point in mins),
                min(point[2] for point in mins),
            )
            bounds_max = (
                max(point[0] for point in maxs),
                max(point[1] for point in maxs),
                max(point[2] for point in maxs),
            )
        if view["mode"] == "ORTHO":
            # Ortho coverage uses normalized extent against ortho_scale.
            ortho = float(view["ortho_scale"])
            extent = (
                bounds_max[0] - bounds_min[0],
                bounds_max[1] - bounds_min[1],
                bounds_max[2] - bounds_min[2],
            )
            coverage = min(1.25, max(extent) / max(ortho, 1e-6))
        else:
            coverage = framing_coverage(
                bounds_min,
                bounds_max,
                tuple(view["camera"]),
                tuple(view["target"]),
                float(view["lens_mm"]),
            )
        passed = minimum_coverage <= coverage <= maximum_coverage
        results.append(
            {
                "name": view["name"],
                "subject": subject,
                "coverage": round(coverage, 6),
                "pass": passed,
            }
        )
    return results


def verify_authorities() -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for path in (CONTRACT, SYSTEMS, STATION_CAGE, CAMERAS, RUBRIC):
        if not path.is_file():
            raise Method02Error(f"Missing Method02 authority: {path}")
        inventory.append(
            {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
        )
    if not SOURCE_BLEND.is_file():
        raise Method02Error(f"Missing dimensional authority blend: {SOURCE_BLEND}")
    source_bytes = SOURCE_BLEND.stat().st_size
    source_hash = sha256(SOURCE_BLEND)
    if source_bytes != 1526526 or source_hash != (
        "512f13fde09edaeb77d75f0c27372a340dc0b2b123e7d0b813c89df3acdf22e6"
    ):
        raise Method02Error(f"Dimensional authority blend identity mismatch: {SOURCE_BLEND}")
    inventory.append(
        {
            "path": str(SOURCE_BLEND),
            "bytes": source_bytes,
            "sha256": source_hash,
            "role": "dimensional_socket_authority_only",
        }
    )
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("asset_id") != ASSET_ID:
        raise Method02Error("Contract asset_id mismatch.")
    if "cosmetic repair" not in " ".join(contract.get("prohibited", [])).lower() and not any(
        "cosmetic" in str(item).lower() for item in contract.get("prohibited", [])
    ):
        raise Method02Error("Contract must prohibit cosmetic repair of rejected GLB.")
    return inventory


def load_dimensional_authority_record() -> dict[str, Any]:
    """Record immutable source-blend identity; do not import donor meshes."""
    before = sha256(SOURCE_BLEND)
    if SOURCE_BLEND.stat().st_size <= 0:
        raise Method02Error("Dimensional authority blend is empty.")
    after = sha256(SOURCE_BLEND)
    if before != after:
        raise Method02Error("Dimensional authority blend mutated during probe.")
    return {
        "source_blend": str(SOURCE_BLEND),
        "bytes": SOURCE_BLEND.stat().st_size,
        "sha256": after,
        "authoritative_dimensions": AUTHORITATIVE,
        "authoritative_sockets": REQUIRED_SOCKETS,
        "donor_meshes_used_as_production_surface": False,
        "unchanged": True,
    }


def clear_default_scene() -> None:
    import bpy

    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)


def new_object(name: str, mesh: Any, collection: Any) -> Any:
    import bpy

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj["SKG_AssetID"] = ASSET_ID
    obj["SKG_GeometryAuthority"] = "PROJECT_DERIVED_NONAUTHORITATIVE"
    obj["SKG_Method"] = "artist_grade_method02_station_cage"
    return obj


def mesh_from_loft(
    name: str,
    profiles: list[dict[str, float | str]],
    collection: Any,
    segments: int = 16,
) -> Any:
    import bpy
    from mathutils import Vector

    rings = []
    for profile in profiles:
        x = float(profile["x_m"])
        z_center = 1.12
        ring = []
        for y, z in ellipse_points(
            float(profile["half_width_m"]), float(profile["half_height_m"]), segments
        ):
            ring.append(Vector((x, y, z_center + z)))
        rings.append(ring)
    vertices: list[Any] = []
    faces: list[tuple[int, int, int, int]] = []
    for ring in rings:
        base = len(vertices)
        vertices.extend(ring)
        if base == 0:
            continue
        previous = base - segments
        for index in range(segments):
            a = previous + index
            b = previous + ((index + 1) % segments)
            c = base + ((index + 1) % segments)
            d = base + index
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata([(v.x, v.y, v.z) for v in vertices], [], faces)
    mesh.update()
    obj = new_object(name, mesh, collection)
    return obj


def add_box(
    name: str,
    location: tuple[float, float, float],
    size: tuple[float, float, float],
    collection: Any,
) -> Any:
    import bpy

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj["SKG_AssetID"] = ASSET_ID
    obj["SKG_GeometryAuthority"] = "PROJECT_DERIVED_NONAUTHORITATIVE"
    obj["SKG_Method"] = "artist_grade_method02_station_cage"
    return obj


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    collection: Any,
    vertices: int = 24,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Any:
    import bpy

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj["SKG_AssetID"] = ASSET_ID
    obj["SKG_GeometryAuthority"] = "PROJECT_DERIVED_NONAUTHORITATIVE"
    return obj


def ensure_uv(obj: Any) -> None:
    if obj.data.uv_layers:
        return
    uv_layer = obj.data.uv_layers.new(name="UVMap")
    mesh = obj.data
    for polygon in mesh.polygons:
        normal = polygon.normal
        axis = max(range(3), key=lambda index: abs(normal[index]))
        for loop_index in polygon.loop_indices:
            coordinate = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if axis == 0:
                uv = (coordinate.y, coordinate.z)
            elif axis == 1:
                uv = (coordinate.x, coordinate.z)
            else:
                uv = (coordinate.x, coordinate.y)
            uv_layer.data[loop_index].uv = (float(uv[0]), float(uv[1]))


def configure_material(name: str, role: str, base: tuple[float, float, float, float], metallic: float, roughness: float) -> Any:
    import bpy

    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = base
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = roughness
        if role == "canopy_glass":
            for candidate in ("Transmission Weight", "Transmission"):
                if candidate in principled.inputs:
                    principled.inputs[candidate].default_value = 0.86
            principled.inputs["IOR"].default_value = 1.45
            if hasattr(material, "surface_render_method"):
                material.surface_render_method = "DITHERED"
    material["SKG_MaterialRole"] = role
    material["SKG_Status"] = "PROVISIONAL_PBR_REQUIRES_UNREAL_CALIBRATION"
    return material


def assign_material(obj: Any, material: Any) -> None:
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def join_objects(name: str, objects: list[Any], collection: Any) -> Any:
    import bpy

    if not objects:
        raise Method02Error(f"Cannot join empty system: {name}")
    if len(objects) == 1:
        objects[0].name = name
        return objects[0]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    joined.name = name
    for owner in list(joined.users_collection):
        if owner != collection:
            owner.objects.unlink(joined)
    if joined.name not in collection.objects:
        collection.objects.link(joined)
    return joined


def object_bounds(obj: Any) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    from mathutils import Vector

    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = tuple(min(point[index] for point in corners) for index in range(3))
    maximum = tuple(max(point[index] for point in corners) for index in range(3))
    return minimum, maximum  # type: ignore[return-value]


def build_systems(collection: Any, profiles: list[dict[str, float | str]]) -> dict[str, Any]:
    paint = configure_material("MAT_Yak52_Paint", "painted_aluminum", (0.20, 0.23, 0.26, 1.0), 0.05, 0.40)
    yellow = configure_material("MAT_Yak52_Accent", "paint_yellow", (0.72, 0.46, 0.03, 1.0), 0.0, 0.42)
    metal = configure_material("MAT_Yak52_Metal", "bare_aluminum", (0.42, 0.46, 0.49, 1.0), 0.82, 0.30)
    glass = configure_material("MAT_Yak52_Glass", "canopy_glass", (0.10, 0.20, 0.24, 0.22), 0.0, 0.12)
    rubber = configure_material("MAT_Yak52_Rubber", "rubber", (0.018, 0.022, 0.025, 1.0), 0.0, 0.78)

    cowling_profiles = [profile for profile in profiles if "cowling" in str(profile["role"]) or str(profile["role"]) == "spinner"]
    fuselage_profiles = [
        profile
        for profile in profiles
        if str(profile["role"])
        in {
            "cowling_fuselage_join",
            "fuselage",
            "wing_carry_through",
            "canopy_front",
            "canopy_rear_open",
            "aft_taper",
            "tailcone",
            "empennage_root",
        }
    ]
    if len(cowling_profiles) < 2:
        cowling_profiles = profiles[1:4]
    if len(fuselage_profiles) < 3:
        fuselage_profiles = profiles[3:]

    cowling = mesh_from_loft("SYS_Cowling", cowling_profiles, collection, segments=20)
    assign_material(cowling, metal)
    fuselage = mesh_from_loft("SYS_Fuselage", fuselage_profiles, collection, segments=20)
    assign_material(fuselage, paint)

    # Tapered wing: root thicker/longer chord than tip.
    wing_parts = []
    for sign, suffix in ((-1.0, "L"), (1.0, "R")):
        root = add_box(
            f"TMP_WingRoot_{suffix}",
            (0.45, sign * 1.35, 1.10),
            (1.85, 2.40, 0.22),
            collection,
        )
        tip = add_box(
            f"TMP_WingTip_{suffix}",
            (0.20, sign * 3.85, 1.18),
            (1.05, 2.20, 0.10),
            collection,
        )
        wing_parts.extend([root, tip])
    wing = join_objects("SYS_Wing", wing_parts, collection)
    assign_material(wing, yellow)

    ht = add_box("TMP_HT", (-3.05, 0.0, 1.35), (0.95, AUTHORITATIVE["horizontal_tail_span_m"], 0.08), collection)
    vt = add_box("TMP_VT", (-3.25, 0.0, 1.85), (0.85, 0.10, 1.05), collection)
    empennage = join_objects("SYS_Empennage", [ht, vt], collection)
    assign_material(empennage, paint)

    canopy_front = add_box("TMP_CanopyFront", (-0.15, 0.0, 1.78), (1.05, 0.78, 0.55), collection)
    canopy_rear = add_box("TMP_CanopyRear", (-1.05, 0.0, 1.76), (0.95, 0.74, 0.52), collection)
    bow = add_box("TMP_CanopyBow", (-0.60, 0.0, 1.95), (0.08, 0.80, 0.42), collection)
    canopy = join_objects("SYS_Canopy", [canopy_front, canopy_rear, bow], collection)
    assign_material(canopy, glass)

    gear_parts = []
    for name, location in (
        ("TMP_NoseStrut", (1.705, 0.0, 0.55)),
        ("TMP_MainStrut_L", (0.42, -1.3575, 0.60)),
        ("TMP_MainStrut_R", (0.42, 1.3575, 0.60)),
    ):
        gear_parts.append(add_cylinder(name, location, 0.035, 0.55, collection, rotation=(0.0, math.radians(90.0), 0.0)))
    for name, location in (
        ("TMP_NoseWheel", (1.705, 0.0, 0.22)),
        ("TMP_MainWheel_L", (0.42, -1.3575, 0.22)),
        ("TMP_MainWheel_R", (0.42, 1.3575, 0.22)),
    ):
        wheel = add_cylinder(name, location, 0.22, 0.10, collection, rotation=(math.radians(90.0), 0.0, 0.0))
        assign_material(wheel, rubber)
        gear_parts.append(wheel)
    gear = join_objects("SYS_LandingGear", gear_parts, collection)

    spinner = add_cylinder("TMP_Spinner", (3.70, 0.0, 1.22), 0.22, 0.45, collection, rotation=(0.0, math.radians(90.0), 0.0))
    assign_material(spinner, metal)
    blades = []
    radius = AUTHORITATIVE["propeller_diameter_m"] * 0.5
    for index in range(2):
        angle = index * math.pi
        blade = add_box(
            f"TMP_Blade_{index}",
            (
                3.82,
                math.sin(angle) * radius * 0.45,
                1.22 + math.cos(angle) * radius * 0.45,
            ),
            (0.08, 0.16, radius * 0.95),
            collection,
        )
        blade.rotation_euler = (angle, 0.0, 0.0)
        blades.append(blade)
    propeller = join_objects("SYS_Propeller", [spinner, *blades], collection)
    assign_material(propeller, metal)

    aileron_l = add_box("TMP_Aileron_L", (0.05, -3.55, 1.12), (0.45, 1.4, 0.05), collection)
    aileron_r = add_box("TMP_Aileron_R", (0.05, 3.55, 1.12), (0.45, 1.4, 0.05), collection)
    elevator = add_box("TMP_Elevator", (-3.35, 0.0, 1.35), (0.35, 2.6, 0.05), collection)
    rudder = add_box("TMP_Rudder", (-3.55, 0.0, 1.90), (0.30, 0.06, 0.85), collection)
    controls = join_objects(
        "SYS_ControlSurfaces", [aileron_l, aileron_r, elevator, rudder], collection
    )
    assign_material(controls, paint)

    systems = {
        "SYS_Cowling": cowling,
        "SYS_Fuselage": fuselage,
        "SYS_Wing": wing,
        "SYS_Empennage": empennage,
        "SYS_Canopy": canopy,
        "SYS_LandingGear": gear,
        "SYS_Propeller": propeller,
        "SYS_ControlSurfaces": controls,
    }
    for obj in systems.values():
        ensure_uv(obj)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return systems


def new_empty(name: str, location: tuple[float, float, float], collection: Any, role: str) -> Any:
    import bpy

    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.09
    obj.location = location
    obj["SKG_AssetID"] = ASSET_ID
    obj["SKG_Role"] = role
    obj["SKG_GeometryAuthority"] = "PROJECT_DERIVED_NONAUTHORITATIVE"
    collection.objects.link(obj)
    return obj


def add_datums(collection: Any, profiles: list[dict[str, float | str]]) -> list[str]:
    names: list[str] = []
    for name, location in REQUIRED_SOCKETS.items():
        new_empty(name, location, collection, "unreal_socket")
        names.append(name)
    for index, profile in enumerate(profiles):
        name = f"DATUM_STATION_{index:02d}_{profile['id']}"
        datum = new_empty(
            name,
            (float(profile["x_m"]), 0.0, 1.12),
            collection,
            "reference_station",
        )
        datum["SKG_StationRole"] = str(profile["role"])
        names.append(name)
    return names


def add_collisions(collection: Any) -> list[str]:
    specifications = [
        ("UCX_Yak52_Fuselage", (0.0, 0.0, 1.06), (6.65, 1.18, 1.32)),
        ("UCX_Yak52_Wing_L", (0.35, -2.55, 1.08), (2.05, 3.95, 0.18)),
        ("UCX_Yak52_Wing_R", (0.35, 2.55, 1.08), (2.05, 3.95, 0.18)),
        ("UCX_Yak52_Tail", (-2.82, 0.0, 1.28), (1.55, 3.16, 0.34)),
    ]
    names: list[str] = []
    for name, location, size in specifications:
        obj = add_box(name, location, size, collection)
        obj.display_type = "WIRE"
        obj.hide_render = True
        obj["SKG_Role"] = "unreal_collision"
        ensure_uv(obj)
        names.append(name)
    return names


def set_lighting(profile: str, key: Any, fill: Any, rim: Any, world: Any) -> None:
    settings = {
        "daylight": (4.0, 1750.0, 720.0, 850.0, (0.055, 0.075, 0.11)),
        "overcast": (2.0, 1050.0, 900.0, 500.0, (0.09, 0.10, 0.12)),
        "night": (0.7, 640.0, 280.0, 1050.0, (0.006, 0.012, 0.028)),
        "wet": (2.4, 1350.0, 620.0, 1100.0, (0.025, 0.04, 0.065)),
        "cockpit": (1.3, 800.0, 360.0, 700.0, (0.012, 0.022, 0.034)),
    }
    exposure, key_energy, fill_energy, rim_energy, color = settings[profile]
    key.data.energy = key_energy
    fill.data.energy = fill_energy
    rim.data.energy = rim_energy
    world.color = color
    key.data.color = (1.0, 0.82, 0.66) if profile in {"night", "cockpit"} else (1.0, 0.94, 0.84)
    rim.data.color = (0.20, 0.42, 1.0) if profile in {"night", "wet"} else (0.68, 0.80, 1.0)
    key["SKG_ExposureHint"] = exposure


def render_view_set(
    views: list[dict[str, Any]],
    output_dir: Path,
    resolution: tuple[int, int],
    review: Any,
    camera: Any,
    lights: tuple[Any, Any, Any],
    world: Any,
) -> list[Path]:
    import bpy
    from mathutils import Vector

    scene = bpy.context.scene
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    key, fill, rim = lights
    paths: list[Path] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for specification in views:
        camera.location = specification["camera"]
        target = Vector(specification["target"])
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        if specification["mode"] == "ORTHO":
            camera.data.type = "ORTHO"
            camera.data.ortho_scale = specification["ortho_scale"]
        else:
            camera.data.type = "PERSP"
            camera.data.lens = specification["lens_mm"]
        set_lighting(specification["lighting"], key, fill, rim, world)
        path = output_dir / f"{specification['name']}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def render_views(output: Path) -> tuple[list[Path], list[Path]]:
    import bpy
    from mathutils import Vector

    camera_contract = json.loads(CAMERAS.read_text(encoding="utf-8"))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("WORLD_Yak52Method02")

    review = bpy.data.collections.new("REVIEW_ONLY")
    scene.collection.children.link(review)
    bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0.0, 0.0, -0.015))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for owner in list(ground.users_collection):
        owner.objects.unlink(ground)
    review.objects.link(ground)
    ground_material = bpy.data.materials.new("MAT_REVIEW_Ground")
    ground_material.diffuse_color = (0.055, 0.065, 0.075, 1.0)
    ground.data.materials.append(ground_material)

    camera_data = bpy.data.cameras.new("CAM_REVIEW")
    camera = bpy.data.objects.new("CAM_REVIEW", camera_data)
    review.objects.link(camera)
    scene.camera = camera

    lights = []
    for name, location, size in (
        ("REVIEW_Key", (6.0, -7.0, 8.5), 6.0),
        ("REVIEW_Fill", (-4.0, 5.0, 5.0), 7.0),
        ("REVIEW_Rim", (-5.0, -4.0, 6.0), 5.0),
    ):
        data = bpy.data.lights.new(name + "_Data", "AREA")
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        light.location = location
        light.rotation_euler = (Vector((0.0, 0.0, 1.0)) - light.location).to_track_quat("-Z", "Y").to_euler()
        review.objects.link(light)
        lights.append(light)

    checkpoints = render_view_set(
        camera_contract["checkpoint_views"],
        output / "checkpoints",
        tuple(camera_contract["checkpoint_resolution"]),
        review,
        camera,
        (lights[0], lights[1], lights[2]),
        scene.world,
    )
    finals = render_view_set(
        camera_contract["final_views"],
        output / "renders",
        tuple(camera_contract["final_resolution"]),
        review,
        camera,
        (lights[0], lights[1], lights[2]),
        scene.world,
    )
    return checkpoints, finals


def export_outputs(asset_collection: Any, output: Path) -> tuple[Path, Path]:
    import bpy

    blend_path = output / "SKG_Yak52_Airframe_ArtistGrade_Method02.blend"
    glb_path = output / "SKG_Yak52_Airframe_ArtistGrade_Method02.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    selected = []
    for obj in asset_collection.all_objects:
        if obj.type in {"MESH", "EMPTY"}:
            obj.hide_set(False)
            obj.select_set(True)
            selected.append(obj)
    bpy.context.view_layer.objects.active = next(
        (obj for obj in selected if obj.type == "MESH"), None
    )
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )
    return blend_path, glb_path


def dimensions_from_systems(systems: dict[str, Any]) -> dict[str, float]:
    mins = []
    maxs = []
    for obj in systems.values():
        minimum, maximum = object_bounds(obj)
        mins.append(minimum)
        maxs.append(maximum)
    minimum = tuple(min(point[index] for point in mins) for index in range(3))
    maximum = tuple(max(point[index] for point in maxs) for index in range(3))
    return {
        "overall_length_m": float(maximum[0] - minimum[0]),
        "wingspan_m": float(maximum[1] - minimum[1]),
        "overall_height_m": float(maximum[2] - minimum[2]),
        "minimum_x_m": float(minimum[0]),
        "maximum_x_m": float(maximum[0]),
        "minimum_y_m": float(minimum[1]),
        "maximum_y_m": float(maximum[1]),
        "minimum_z_m": float(minimum[2]),
        "maximum_z_m": float(maximum[2]),
    }


def main() -> int:
    import bpy

    args = parse_args()
    output = Path(args.output)
    assert_fresh_namespace(output)
    if output.exists() and any(output.iterdir()):
        raise Method02Error(f"Output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    authorities = verify_authorities()
    profiles = load_station_profiles()
    variation = fuselage_width_variation(profiles)
    if variation < 0.18:
        raise Method02Error(
            f"Station cage width variation {variation:.3f} is below the Method02 gate."
        )

    donor = load_dimensional_authority_record()
    clear_default_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"

    asset_collection = bpy.data.collections.new("ASSET")
    scene.collection.children.link(asset_collection)
    systems = build_systems(asset_collection, profiles)
    missing = [name for name in SYSTEM_OBJECT_NAMES if name not in systems]
    if missing:
        raise Method02Error(f"Missing required systems: {missing}")

    subject_bounds = {name: object_bounds(obj) for name, obj in systems.items()}
    camera_contract = json.loads(CAMERAS.read_text(encoding="utf-8"))
    framing = evaluate_framing_gates(
        camera_contract["checkpoint_views"] + camera_contract["final_views"],
        subject_bounds,
        float(camera_contract["framing_gate"]["minimum_subject_coverage"]),
        float(camera_contract["framing_gate"]["maximum_subject_coverage"]),
    )
    if any(not item["pass"] for item in framing):
        raise Method02Error(f"Camera framing gate failed: {framing}")

    datum_names = add_datums(asset_collection, profiles)
    collision_names = add_collisions(asset_collection)
    checkpoints, finals = render_views(output)
    blend_path, glb_path = export_outputs(asset_collection, output)
    final_dimensions = dimensions_from_systems(systems)

    write_json(
        output / "dimension_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-artist-grade-method02.dimension-receipt.v1",
            "authoritative_targets": AUTHORITATIVE,
            "reconciled_dimensions_m": final_dimensions,
            "station_width_coefficient_of_variation": variation,
            "global_envelope_pass": all(
                abs(final_dimensions[key] - AUTHORITATIVE[key]) / AUTHORITATIVE[key] <= 0.12
                for key in ("overall_length_m", "overall_height_m", "wingspan_m")
            ),
            "derived_geometry_label": "PROJECT_DERIVED_NONAUTHORITATIVE",
            "rejected_glb_reused": False,
        },
    )
    write_json(
        output / "source_parity_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-artist-grade-method02.source-parity.v1",
            "authorities": authorities,
            "dimensional_authority_probe": donor,
            "failed_namespaces_not_used": [str(path) for path in FAILED_ATTEMPT_ROOTS],
            "unchanged": bool(donor.get("unchanged")),
        },
    )
    write_json(
        output / "silhouette_station_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-artist-grade-method02.silhouette-station.v1",
            "station_count": len(profiles),
            "stations": profiles,
            "width_coefficient_of_variation": variation,
            "checkpoint_count": len(checkpoints),
            "checkpoint_names": [path.name for path in checkpoints],
        },
    )
    write_json(
        output / "systems_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-artist-grade-method02.systems.v1",
            "systems": sorted(systems.keys()),
            "system_count": len(systems),
            "separate_systems": True,
        },
    )
    write_json(
        output / "camera_framing_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-artist-grade-method02.camera-framing.v1",
            "results": framing,
            "all_passed": all(item["pass"] for item in framing),
        },
    )
    write_json(
        output / "topology_material_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-artist-grade-method02.topology-material.v1",
            "system_meshes": sorted(systems.keys()),
            "sockets": datum_names,
            "collision": collision_names,
            "derived_geometry_label": "PROJECT_DERIVED_NONAUTHORITATIVE",
            "visual_acceptance_claimed": False,
        },
    )
    artifacts = [blend_path, glb_path, *checkpoints, *finals]
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.phase2.yak52-airframe-artist-grade-method02.artifact-receipt.v1",
            "asset_id": ASSET_ID,
            "blender_version": bpy.app.version_string,
            "classification": "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW",
            "artifacts": [
                {
                    "path": str(path.relative_to(output)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
                for path in artifacts
            ],
            "checkpoint_count": len(checkpoints),
            "render_count": len(finals),
            "checkpoint_dimensions": list(camera_contract["checkpoint_resolution"]),
            "render_dimensions": list(camera_contract["final_resolution"]),
            "unreal_import_authorized": False,
            "aaa_claimed": False,
        },
    )
    print(
        json.dumps(
            {
                "asset_id": ASSET_ID,
                "status": "awaiting_review",
                "checkpoint_count": len(checkpoints),
                "render_count": len(finals),
            }
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Method02Error as exc:
        print(f"Method02Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except Exception as exc:  # noqa: BLE001 - Blender must not exit zero on worker failure
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
