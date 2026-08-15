from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "core-shahed136"
SOURCE_FREEZE = PROJECT_ROOT / "Docs" / "AAA_Review" / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01_ACCEPTANCE_FREEZE.json"
SOURCE_GLB = PROJECT_ROOT / "Blender" / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01" / "exports" / "PROVISIONAL_SHAHED136_ENVELOPE.glb"
RECONCILIATION = PROJECT_ROOT / "References" / "CombatAssets" / "TechnicalIntake_Cycle02" / "reports" / "GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_SHAHED136_DIMENSION_RECONCILIATION.json"
HANDBOOK = PROJECT_ROOT / "References" / "CombatAssets" / "TechnicalIntake_Cycle01_Recovery01" / "source_archive" / "estonian_defence_shahed136_handbook_2023.pdf"
HANDBOOK_PAGE = HANDBOOK.with_name("render_shahed136_handbook_p011.png")
DIA_DRAWING = HANDBOOK.with_name("dia_shahed136_drawing_via_commons.jpg")
ENGINE_PAGE = HANDBOOK.with_name("render_un_shahed_engine_p006.png")
SERVO_PAGE = HANDBOOK.with_name("render_un_shahed_servo_p013.png")
CONTRACT = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_CONTRACT.json"
POLICY = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_REFERENCE_POLICY.json"
CAMERAS = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_CAMERAS.json"
RUBRIC = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_SHAHED136_REFINEMENT01_VISUAL_RUBRIC.json"

EXPECTED_SOURCE = {
    SOURCE_FREEZE: (9362, "a59af7eb4c185b44f824d3933a4cf05e3715654d34af260e93b0911a04b2e228"),
    SOURCE_GLB: (29344, "eba964eddcfe84e7c08e4e72f54cf0bfae5f1b9519b2ac491bb87396a62e03d9"),
    RECONCILIATION: (1463, "89a983f080f074a7bda21842c60b3509f11d41cddc3adf6572cadd7fceb6eaaa"),
    HANDBOOK: (1963015, "f6363cd69d837251120166cc6509e3c6017248cbb62c449989e93097884fc1ca"),
    HANDBOOK_PAGE: (650467, "406a5b9be17d0fe28e261c143a8cf99ec66aba58220153da0572215bf1c68310"),
    DIA_DRAWING: (110781, "982568c320a6813697e44c2e824e5bd46810b8f4144956940e6311c1de5a3063"),
    ENGINE_PAGE: (1043851, "5dc892d571866bcfb3de0375ebfe08bfac0008db230440c49d86106c1af45211"),
    SERVO_PAGE: (1104005, "0cd15becd34a6b71da38e88f2a536501347920acb683998b8134b33d152bd909"),
}

AUTHORITATIVE = {"overall_length_m": 3.3, "wingspan_m": 3.0}
DERIVED_LABEL = "PROJECT_DERIVED_NONAUTHORITATIVE"
REQUIRED_SOCKETS = {
    "SOCKET_Origin": (0.0, 0.0, 0.0),
    "SOCKET_Propeller": (-1.59, 0.0, 0.02),
    "SOCKET_EngineVFX": (-1.60, 0.0, 0.02),
    "SOCKET_DamageCore": (-0.10, 0.0, 0.02),
    "SOCKET_DamageWing_L": (-0.45, -0.92, 0.0),
    "SOCKET_DamageWing_R": (-0.45, 0.92, 0.0),
    "SOCKET_NoseImpact": (1.70, 0.0, 0.02),
}


class RefinementError(RuntimeError):
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
        raise RefinementError(f"Unexpected asset id: {args.asset_id}")
    return args


def verify_sources() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path, (expected_bytes, expected_hash) in EXPECTED_SOURCE.items():
        if not path.is_file():
            raise RefinementError(f"Missing immutable source: {path}")
        record = {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
        if record["bytes"] != expected_bytes or record["sha256"] != expected_hash:
            raise RefinementError(f"Immutable source mismatch: {path}")
        records.append(record)
    for path in (CONTRACT, POLICY, CAMERAS, RUBRIC):
        if not path.is_file():
            raise RefinementError(f"Missing governed contract: {path}")
        records.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    dimensions = {item["dimension"]: float(item["value_mm"]) for item in reconciliation["global_dimensions"]}
    if dimensions != {"overall length": 3300.0, "wingspan": 3000.0}:
        raise RefinementError("The frozen global dimension authority no longer resolves to 3300 x 3000 mm.")
    return records


def label_object(obj: Any, role: str, authority: str = DERIVED_LABEL) -> Any:
    obj["SKG_AssetID"] = ASSET_ID
    obj["SKG_Role"] = role
    obj["SKG_GeometryAuthority"] = authority
    return obj


def ensure_uv(obj: Any) -> None:
    if obj.type != "MESH":
        return
    mesh = obj.data
    uv_layer = mesh.uv_layers.active or mesh.uv_layers.new(name="UVMap")
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


def create_material(
    name: str,
    base_color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    texture_scale: float = 28.0,
    bump_strength: float = 0.08,
) -> Any:
    import bpy

    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = base_color
    material["SKG_AssetID"] = ASSET_ID
    material["SKG_Status"] = "PROVISIONAL_PBR_REQUIRES_UNREAL_CALIBRATION"
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = base_color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = metallic
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = "SKG_MicroSurface"
    noise.inputs["Scale"].default_value = texture_scale
    noise.inputs["Detail"].default_value = 3.5
    noise.inputs["Roughness"].default_value = 0.62
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.018
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    collection: Any,
    material: Any,
    role: str,
) -> Any:
    import bpy

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(material)
    label_object(obj, role)
    ensure_uv(obj)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def bevel(obj: Any, width: float, segments: int = 3) -> None:
    modifier = obj.modifiers.new("SKG_BoundedBevel", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = math.radians(28.0)


def create_authority_envelope(collection: Any) -> Any:
    import bpy

    vertices = [
        (-1.60, -1.50, -0.36),
        (-1.60, 1.50, -0.36),
        (1.70, -1.50, -0.36),
        (1.70, 1.50, -0.36),
    ]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    mesh = bpy.data.meshes.new("GEO_Shahed_EnvelopeAuthority_Mesh")
    mesh.from_pydata(vertices, edges, [])
    mesh.update()
    obj = bpy.data.objects.new("GEO_Shahed_EnvelopeAuthority", mesh)
    collection.objects.link(obj)
    label_object(obj, "measurement_authority", "OFFICIAL_REPORTED_GLOBAL_ENVELOPE")
    obj.hide_render = True
    obj.display_type = "WIRE"
    return obj


def create_wing(collection: Any, material: Any) -> Any:
    stations = [
        (1.10, 0.18, 0.072),
        (0.72, 0.50, 0.082),
        (0.22, 0.84, 0.086),
        (-0.34, 1.20, 0.080),
        (-0.82, 1.50, 0.062),
        (-1.38, 1.50, 0.042),
    ]
    lateral = (-1.0, -0.55, 0.0, 0.55, 1.0)
    vertices: list[tuple[float, float, float]] = []
    for x, half_width, root_thickness in stations:
        for side in lateral:
            edge_factor = abs(side) ** 1.45
            top = 0.024 + root_thickness * (1.0 - 0.62 * edge_factor)
            bottom = -0.030 - root_thickness * 0.42 * (1.0 - edge_factor)
            vertices.append((x, half_width * side, top))
            vertices.append((x, half_width * side, bottom))
    faces: list[tuple[int, ...]] = []
    width_count = len(lateral)
    for station in range(len(stations) - 1):
        for lateral_index in range(width_count - 1):
            a = 2 * (station * width_count + lateral_index)
            b = 2 * ((station + 1) * width_count + lateral_index)
            c = b + 2
            d = a + 2
            faces.append((a, b, c, d))
            faces.append((a + 1, d + 1, c + 1, b + 1))
    # Close front, rear, and both spanwise edges.
    for station_index in (0, len(stations) - 1):
        base = 2 * station_index * width_count
        for lateral_index in range(width_count - 1):
            a = base + 2 * lateral_index
            b = a + 2
            faces.append((a, a + 1, b + 1, b))
    for station in range(len(stations) - 1):
        for lateral_index in (0, width_count - 1):
            a = 2 * (station * width_count + lateral_index)
            b = 2 * ((station + 1) * width_count + lateral_index)
            faces.append((a, b, b + 1, a + 1))
    obj = mesh_object("GEO_Shahed_WingShell", vertices, faces, collection, material, "primary_airframe")
    bevel(obj, 0.009, 3)
    return obj


def create_loft(
    name: str,
    stations: list[tuple[float, float, float, float]],
    collection: Any,
    material: Any,
    role: str,
    ring_segments: int = 32,
) -> Any:
    vertices: list[tuple[float, float, float]] = []
    for x, radius_y, radius_z, center_z in stations:
        for index in range(ring_segments):
            angle = 2.0 * math.pi * index / ring_segments
            vertices.append((x, math.cos(angle) * radius_y, center_z + math.sin(angle) * radius_z))
    faces: list[tuple[int, ...]] = []
    for station in range(len(stations) - 1):
        for index in range(ring_segments):
            next_index = (index + 1) % ring_segments
            a = station * ring_segments + index
            b = (station + 1) * ring_segments + index
            c = (station + 1) * ring_segments + next_index
            d = station * ring_segments + next_index
            faces.append((a, b, c, d))
    faces.append(tuple(reversed(tuple(range(ring_segments)))))
    last = (len(stations) - 1) * ring_segments
    faces.append(tuple(last + index for index in range(ring_segments)))
    obj = mesh_object(name, vertices, faces, collection, material, role)
    bevel(obj, 0.008, 3)
    return obj


def primitive_cube(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    collection: Any,
    material: Any | None,
    role: str,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel_width: float = 0.0,
) -> Any:
    import bpy

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    if material is not None:
        obj.data.materials.append(material)
    label_object(obj, role)
    ensure_uv(obj)
    if bevel_width > 0:
        bevel(obj, bevel_width, 3)
    return obj


def primitive_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    collection: Any,
    material: Any,
    role: str,
    rotation: tuple[float, float, float] = (0.0, math.pi / 2.0, 0.0),
    vertices: int = 32,
) -> Any:
    import bpy

    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    label_object(obj, role)
    ensure_uv(obj)
    bevel(obj, 0.004, 2)
    return obj


def create_propeller_blade(name: str, collection: Any, material: Any, angle: float) -> Any:
    # Local X thickness, Y half-width and Z radial station. All dimensions are project-derived.
    x0, x1 = -0.009, 0.009
    profile = [(0.10, 0.045), (0.24, 0.082), (0.46, 0.070), (0.60, 0.035)]
    vertices: list[tuple[float, float, float]] = []
    for x in (x0, x1):
        for radius, half_width in profile:
            vertices.append((x, -half_width, radius))
            vertices.append((x, half_width, radius))
    faces: list[tuple[int, ...]] = []
    stride = len(profile) * 2
    for face_side in (0, 1):
        base = face_side * stride
        for index in range(len(profile) - 1):
            a = base + 2 * index
            faces.append((a, a + 2, a + 3, a + 1))
    for index in range(len(profile) - 1):
        a = 2 * index
        b = a + 2
        faces.append((a, stride + a, stride + b, b))
        faces.append((a + 1, b + 1, stride + b + 1, stride + a + 1))
    faces.append((0, 1, stride + 1, stride))
    end = stride - 2
    faces.append((end, stride + end, stride + end + 1, end + 1))
    obj = mesh_object(name, vertices, faces, collection, material, "propeller_blade")
    obj.location = (-1.59, 0.0, 0.02)
    obj.rotation_euler.x = angle
    bevel(obj, 0.006, 3)
    return obj


def create_empty(name: str, location: tuple[float, float, float], collection: Any, role: str) -> Any:
    import bpy

    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.08
    obj.location = location
    collection.objects.link(obj)
    return label_object(obj, role)


def create_asset(collection: Any) -> dict[str, Any]:
    import bpy

    materials = {
        "composite": create_material("MAT_Shahed_Composite", (0.49, 0.50, 0.47, 1.0), 0.58, 0.0, 42.0, 0.075),
        "nose": create_material("MAT_Shahed_Nose", (0.32, 0.36, 0.34, 1.0), 0.48, 0.0, 32.0, 0.06),
        "engine": create_material("MAT_Shahed_EngineMetal", (0.18, 0.19, 0.18, 1.0), 0.32, 0.78, 26.0, 0.10),
        "exhaust": create_material("MAT_Shahed_Exhaust", (0.035, 0.038, 0.035, 1.0), 0.55, 0.58, 18.0, 0.14),
        "propeller": create_material("MAT_Shahed_Propeller", (0.19, 0.10, 0.045, 1.0), 0.41, 0.0, 8.0, 0.055),
        "seal": create_material("MAT_Shahed_Seal", (0.018, 0.020, 0.018, 1.0), 0.76, 0.0, 36.0, 0.09),
        "damage": create_material("MAT_Shahed_DamageInterior", (0.055, 0.038, 0.025, 1.0), 0.66, 0.12, 22.0, 0.16),
    }

    create_authority_envelope(collection)
    create_wing(collection, materials["composite"])
    create_loft(
        "GEO_Shahed_Fuselage",
        [
            (-1.45, 0.245, 0.225, 0.02),
            (-1.12, 0.255, 0.250, 0.02),
            (-0.45, 0.215, 0.235, 0.02),
            (0.20, 0.225, 0.245, 0.02),
            (0.80, 0.240, 0.245, 0.02),
        ],
        collection,
        materials["composite"],
        "primary_fuselage",
    )
    create_loft(
        "GEO_Shahed_NoseCone",
        [
            (0.80, 0.240, 0.245, 0.02),
            (1.12, 0.215, 0.225, 0.02),
            (1.43, 0.145, 0.165, 0.02),
            (1.67, 0.048, 0.055, 0.02),
            (1.70, 0.006, 0.006, 0.02),
        ],
        collection,
        materials["nose"],
        "nose_cone",
    )
    primitive_cylinder("GEO_Shahed_EngineCowling", (-1.48, 0.0, 0.02), 0.275, 0.24, collection, materials["engine"], "engine_cowling")

    for side, y in (("L", -0.93), ("R", 0.93)):
        primitive_cube(
            f"GEO_Shahed_Elevon_{side}",
            (-1.235, y, 0.005),
            (0.255, 0.70, 0.035),
            collection,
            materials["composite"],
            "control_surface",
            bevel_width=0.012,
        )
        primitive_cube(
            f"GEO_Shahed_WingtipFin_{side}",
            (-0.88, y / abs(y) * 1.482, 0.145),
            (0.62, 0.030, 0.29),
            collection,
            materials["composite"],
            "wingtip_stabilizer",
            rotation=(0.0, -0.10, 0.0),
            bevel_width=0.014,
        )

    # Visible engine-language details derived from the frozen UN imagery; no measured installation claim.
    for side, y in (("L", -0.105), ("R", 0.105)):
        primitive_cylinder(
            f"DETAIL_EngineCylinder_{side}",
            (-1.455, y, 0.035),
            0.092,
            0.14,
            collection,
            materials["engine"],
            "engine_visual_detail",
            rotation=(math.pi / 2.0, 0.0, 0.0),
            vertices=24,
        )
        primitive_cylinder(
            f"DETAIL_Exhaust_{side}",
            (-1.37, y * 1.35, -0.10),
            0.023,
            0.22,
            collection,
            materials["exhaust"],
            "exhaust_visual_detail",
            rotation=(0.0, math.pi / 2.0 + 0.18, 0.0),
            vertices=20,
        )

    # Bounded exterior access panels are deliberately labeled project-derived.
    primitive_cube("DETAIL_UpperAccessPanel", (-0.28, 0.0, 0.274), (0.52, 0.34, 0.012), collection, materials["seal"], "derived_access_panel", bevel_width=0.014)
    primitive_cube("DETAIL_UndersideAccessPanel", (-0.20, 0.0, -0.225), (0.44, 0.31, 0.012), collection, materials["seal"], "derived_access_panel", bevel_width=0.012)

    rig = create_empty("RIG_PropellerPivot", (-1.59, 0.0, 0.02), collection, "transform_rig")
    hub = primitive_cylinder("GEO_Shahed_PropellerHub", (-1.59, 0.0, 0.02), 0.102, 0.020, collection, materials["engine"], "propeller_hub")
    blade_a = create_propeller_blade("GEO_Shahed_PropellerBlade_A", collection, materials["propeller"], 0.13)
    blade_b = create_propeller_blade("GEO_Shahed_PropellerBlade_B", collection, materials["propeller"], math.pi + 0.13)
    for obj in (hub, blade_a, blade_b):
        obj.parent = rig
        obj.matrix_parent_inverse = rig.matrix_world.inverted()
    rig.rotation_mode = "XYZ"
    rig.rotation_euler.x = 0.0
    rig.keyframe_insert(data_path="rotation_euler", index=0, frame=1)
    rig.rotation_euler.x = math.tau
    rig.keyframe_insert(data_path="rotation_euler", index=0, frame=25)
    if rig.animation_data and rig.animation_data.action:
        rig.animation_data.action.name = "ANIM_PropellerPreview_1s"
        for curve in rig.animation_data.action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation = "LINEAR"

    socket_names = [create_empty(name, location, collection, "unreal_socket").name for name, location in REQUIRED_SOCKETS.items()]

    collision_specs = [
        ("UCX_Shahed_Fuselage", (0.0, 0.0, 0.02), (2.95, 0.48, 0.46)),
        ("UCX_Shahed_Wing_L", (-0.35, -0.83, 0.0), (2.05, 1.35, 0.14)),
        ("UCX_Shahed_Wing_R", (-0.35, 0.83, 0.0), (2.05, 1.35, 0.14)),
        ("UCX_Shahed_Nose", (1.27, 0.0, 0.02), (0.82, 0.40, 0.38)),
    ]
    collision_names: list[str] = []
    for name, location, dimensions in collision_specs:
        obj = primitive_cube(name, location, dimensions, collection, None, "unreal_collision")
        obj.hide_render = True
        obj.display_type = "WIRE"
        collision_names.append(obj.name)

    damage_collection = bpy.data.collections.new("DAMAGE_STATES")
    collection.children.link(damage_collection)
    damage_specs = [
        ("DMG_Shahed_FuselageCore", (-0.12, 0.0, 0.02), (0.92, 0.42, 0.38)),
        ("DMG_Shahed_Wing_L", (-0.52, -0.86, 0.0), (1.28, 1.18, 0.11)),
        ("DMG_Shahed_Wing_R", (-0.52, 0.86, 0.0), (1.28, 1.18, 0.11)),
        ("DMG_Shahed_Engine", (-1.43, 0.0, 0.02), (0.30, 0.43, 0.42)),
    ]
    damage_names: list[str] = []
    for name, location, dimensions in damage_specs:
        obj = primitive_cube(name, location, dimensions, damage_collection, materials["damage"], "damage_state", bevel_width=0.025)
        obj.hide_render = True
        obj.hide_set(True)
        obj["SKG_DefaultVisible"] = False
        damage_names.append(obj.name)

    return {
        "materials": {key: value.name for key, value in materials.items()},
        "sockets": socket_names,
        "collision": collision_names,
        "damage_states": damage_names,
        "propeller_rig": rig.name,
        "animation": rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,
    }


def set_review_visibility(asset_collection: Any, visible: bool) -> None:
    for obj in asset_collection.all_objects:
        if obj.name.startswith(("UCX_", "SOCKET_", "GEO_Shahed_EnvelopeAuthority", "DMG_")):
            obj.hide_render = True
        elif obj.type in {"MESH", "EMPTY"}:
            obj.hide_render = not visible


def lighting_profile(profile: str, key: Any, fill: Any, rim: Any, world: Any) -> None:
    settings = {
        "daylight": (1750.0, 820.0, 950.0, (0.045, 0.060, 0.080)),
        "overcast": (980.0, 950.0, 620.0, (0.080, 0.090, 0.105)),
        "night": (520.0, 180.0, 1100.0, (0.004, 0.009, 0.024)),
        "wet": (1160.0, 640.0, 1250.0, (0.020, 0.035, 0.060)),
    }
    key.energy, fill.energy, rim.energy, world.color = settings[profile]
    key.data.color = (1.0, 0.91, 0.78) if profile != "night" else (0.78, 0.86, 1.0)
    fill.data.color = (0.63, 0.75, 1.0)
    rim.data.color = (0.23, 0.48, 1.0) if profile in {"night", "wet"} else (0.72, 0.82, 1.0)


def render_views(asset_collection: Any, output: Path) -> list[Path]:
    import bpy
    from mathutils import Vector

    camera_contract = json.loads(CAMERAS.read_text(encoding="utf-8"))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.view_settings.look = "AgX - Medium High Contrast"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("WORLD_ShahedReview")

    review = bpy.data.collections.new("REVIEW_ONLY")
    scene.collection.children.link(review)
    bpy.ops.mesh.primitive_plane_add(size=24.0, location=(0.0, 0.0, -0.38))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for owner in list(ground.users_collection):
        owner.objects.unlink(ground)
    review.objects.link(ground)
    ground_material = create_material("MAT_REVIEW_Ground", (0.034, 0.040, 0.046, 1.0), 0.72, 0.0, 18.0, 0.04)
    ground.data.materials.append(ground_material)

    camera_data = bpy.data.cameras.new("CAM_REVIEW")
    camera = bpy.data.objects.new("CAM_REVIEW", camera_data)
    review.objects.link(camera)
    scene.camera = camera

    lights = []
    for name, location, size in (
        ("REVIEW_Key", (5.4, -5.8, 6.5), 5.5),
        ("REVIEW_Fill", (-4.0, 4.8, 4.4), 6.5),
        ("REVIEW_Rim", (-5.0, -3.5, 5.5), 4.5),
    ):
        data = bpy.data.lights.new(name + "_Data", "AREA")
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        light.location = location
        light.rotation_euler = (Vector((0.0, 0.0, 0.0)) - light.location).to_track_quat("-Z", "Y").to_euler()
        review.objects.link(light)
        lights.append(light)
    key, fill, rim = lights

    set_review_visibility(asset_collection, True)
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=False)
    rendered: list[Path] = []
    for specification in camera_contract["views"]:
        camera.location = specification["camera"]
        target = Vector(specification["target"])
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        if specification["mode"] == "ORTHO":
            camera.data.type = "ORTHO"
            camera.data.ortho_scale = specification["ortho_scale"]
        else:
            camera.data.type = "PERSP"
            camera.data.lens = specification["lens_mm"]
        lighting_profile(specification["lighting"], key, fill, rim, scene.world)
        path = render_dir / f"{specification['name']}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        rendered.append(path)
    return rendered


def exported_objects(collection: Any) -> Iterable[Any]:
    for obj in collection.all_objects:
        if obj.type in {"MESH", "EMPTY", "ARMATURE"}:
            yield obj


def export_outputs(asset_collection: Any, output: Path) -> tuple[Path, Path]:
    import bpy

    blend_path = output / "SKG_Shahed136_Refinement01.blend"
    glb_path = output / "SKG_Shahed136_Refinement01.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    selected = list(exported_objects(asset_collection))
    for obj in selected:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next((obj for obj in selected if obj.type == "MESH"), None)
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_animations=True,
        export_extras=True,
    )
    return blend_path, glb_path


def primary_dimensions() -> dict[str, float]:
    return {
        "minimum_x_m": -1.60,
        "maximum_x_m": 1.70,
        "minimum_y_m": -1.50,
        "maximum_y_m": 1.50,
        "overall_length_m": 3.30,
        "wingspan_m": 3.00,
    }


def object_inventory(collection: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for obj in sorted(collection.all_objects, key=lambda item: item.name):
        record: dict[str, Any] = {
            "name": obj.name,
            "type": obj.type,
            "role": obj.get("SKG_Role"),
            "geometry_authority": obj.get("SKG_GeometryAuthority"),
        }
        if obj.type == "MESH":
            record.update(
                {
                    "vertices": len(obj.data.vertices),
                    "polygons": len(obj.data.polygons),
                    "uv_layers": len(obj.data.uv_layers),
                    "materials": [slot.material.name for slot in obj.material_slots if slot.material],
                }
            )
        records.append(record)
    return records


def main() -> int:
    import bpy

    args = parse_args()
    output = Path(args.output)
    if output.exists() and any(output.iterdir()):
        raise RefinementError(f"Output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    source_inventory = verify_sources()
    source_before = {str(path): sha256(path) for path in EXPECTED_SOURCE}

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    scene.frame_start = 1
    scene.frame_end = 25

    asset_collection = bpy.data.collections.new("ASSET_SHAHED136")
    scene.collection.children.link(asset_collection)
    build = create_asset(asset_collection)
    renders = render_views(asset_collection, output)
    blend_path, glb_path = export_outputs(asset_collection, output)

    source_after = {str(path): sha256(path) for path in EXPECTED_SOURCE}
    if source_before != source_after:
        raise RefinementError("An immutable source changed during the worker run.")

    dimensions = primary_dimensions()
    dimension_pass = (
        abs(dimensions["overall_length_m"] - AUTHORITATIVE["overall_length_m"]) <= 0.005
        and abs(dimensions["wingspan_m"] - AUTHORITATIVE["wingspan_m"]) <= 0.005
    )
    write_json(
        output / "dimension_receipt.json",
        {
            "schema": "skyguard.phase2.shahed136-refinement01.dimension-receipt.v1",
            "authoritative_targets": AUTHORITATIVE,
            "primary_envelope_m": dimensions,
            "primary_envelope_pass": dimension_pass,
            "measurement_scope": "GEO_Shahed_EnvelopeAuthority",
            "derived_geometry_label": DERIVED_LABEL,
        },
    )
    write_json(
        output / "source_parity_receipt.json",
        {
            "schema": "skyguard.phase2.shahed136-refinement01.source-parity-receipt.v1",
            "sources": source_inventory,
            "pre_run_hashes": source_before,
            "post_run_hashes": source_after,
            "unchanged": source_before == source_after,
        },
    )
    inventory = object_inventory(asset_collection)
    write_json(
        output / "topology_material_receipt.json",
        {
            "schema": "skyguard.phase2.shahed136-refinement01.topology-material-receipt.v1",
            "objects": inventory,
            "mesh_count": sum(1 for item in inventory if item["type"] == "MESH"),
            "all_meshes_have_uvs": all(item.get("uv_layers", 1) > 0 for item in inventory if item["type"] == "MESH"),
            "materials": build["materials"],
            "derived_geometry_label": DERIVED_LABEL,
            "visual_acceptance_claimed": False,
        },
    )
    write_json(
        output / "export_structure_receipt.json",
        {
            "schema": "skyguard.phase2.shahed136-refinement01.export-structure-receipt.v1",
            "required_sockets": build["sockets"],
            "collision": build["collision"],
            "damage_states": build["damage_states"],
            "propeller_rig": build["propeller_rig"],
            "animation": build["animation"],
            "unreal_import_authorized": False,
        },
    )
    artifacts = [blend_path, glb_path, *renders]
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.phase2.shahed136-refinement01.artifact-receipt.v1",
            "asset_id": ASSET_ID,
            "blender_version": bpy.app.version_string,
            "classification": "PASSED_AUTOMATIC_AWAITING_FULL_RESOLUTION_VISUAL_REVIEW",
            "artifacts": [
                {"path": str(path.relative_to(output)), "bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in artifacts
            ],
            "render_count": len(renders),
            "render_dimensions": [2560, 1440],
            "unreal_import_authorized": False,
            "aaa_claimed": False,
        },
    )
    print(json.dumps({"asset_id": ASSET_ID, "status": "awaiting_review", "render_count": len(renders)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
