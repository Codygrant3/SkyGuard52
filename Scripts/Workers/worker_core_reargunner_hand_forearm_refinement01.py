from __future__ import annotations

import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = PROJECT_ROOT / "Scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "Workers"))

import skyguard_blender_worker_sdk as sdk  # noqa: E402
from skyguard_worker_geometry import (  # noqa: E402
    add_socket,
    pbr_material,
    sha256,
    write_json,
    write_production_receipt,
)


ASSET_ID = "core-reargunner-hand-forearm-refinement01"
CONTRACT = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_CONTRACT.json"
POLICY = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_REFERENCE_POLICY.json"
CAMERAS = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_CAMERAS.json"
RUBRIC = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_VISUAL_RUBRIC.json"
BLOCKOUT_FREEZE = PROJECT_ROOT / "Docs" / "AAA_Review" / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01_ACCEPTANCE_FREEZE.json"
ANTHROPOMETRIC_CONTRACT = (
    PROJECT_ROOT
    / "References"
    / "CombatAssets"
    / "TechnicalIntake_Cycle02"
    / "reports"
    / "GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_CHARACTER_ANTHROPOMETRIC_CONTRACT.json"
)
BLOCKOUT_RECEIPT = (
    PROJECT_ROOT
    / "Blender"
    / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01"
    / "dimension_and_artifact_receipt.json"
)
BLOCKOUT_GLB = (
    PROJECT_ROOT
    / "Blender"
    / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01"
    / "exports"
    / "PROVISIONAL_REAR_GUNNER_HAND_FOREARM_MANNEQUIN.glb"
)

EXPECTED_AUTHORITIES: dict[Path, tuple[int, str]] = {
    BLOCKOUT_FREEZE: (9362, "a59af7eb4c185b44f824d3933a4cf05e3715654d34af260e93b0911a04b2e228"),
    ANTHROPOMETRIC_CONTRACT: (2195, "9702492331d8b2e73e45f4c42f2a9933081e48f1aac00aa2c3f02bb5591c0e09"),
    BLOCKOUT_RECEIPT: (5591, "7566ba0c4d485e3c1e84ea5e15be4a8b048d28a0900e46c3af9ad274a6f0607b"),
    BLOCKOUT_GLB: (416684, "c5761337f8fb8658375bc04625670ef22ab5a841a18fd379bd0d4074e6a4dad0"),
}

REQUIRED_SOCKETS = [
    "SOCKET_Origin",
    "SOCKET_Wrist_R",
    "SOCKET_Wrist_L",
    "SOCKET_Rifle_FiringHand",
    "SOCKET_Rifle_SupportHand",
    "SOCKET_Igla_FiringHand",
    "SOCKET_Igla_SupportHand",
    "SOCKET_ADS_HandAlignment",
]

REQUIRED_ACTIONS = [
    "ACT_Neutral",
    "ACT_RifleSupport",
    "ACT_RifleTriggerADS",
    "ACT_IglaSupport",
]

VISIBLE_TRIANGLE_BUDGET = 90000
MINIMUM_VISIBLE_VERTICES = 12000

FINGER_ORDER = ("Index", "Middle", "Ring", "Little")
FINGER_LENGTHS = {
    "Index": 0.078,
    "Middle": 0.086,
    "Ring": 0.080,
    "Little": 0.068,
}
FINGER_OFFSETS = {
    "Index": 0.027,
    "Middle": 0.009,
    "Ring": -0.010,
    "Little": -0.028,
}


class RefinementError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RefinementError(f"Expected a JSON object: {path}")
    return payload


def verify_authorities() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path, (expected_bytes, expected_hash) in EXPECTED_AUTHORITIES.items():
        if not path.is_file():
            raise RefinementError(f"Missing immutable authority: {path}")
        actual_bytes = path.stat().st_size
        actual_hash = sha256(path)
        if actual_bytes != expected_bytes or actual_hash != expected_hash:
            raise RefinementError(f"Immutable authority mismatch: {path}")
        records.append(
            {
                "path": str(path),
                "bytes": actual_bytes,
                "sha256": actual_hash,
                "use": "read-only dimensional/reference authority; geometry is never imported",
            }
        )
    for path in (CONTRACT, POLICY, CAMERAS, RUBRIC):
        if not path.is_file():
            raise RefinementError(f"Missing governed refinement contract: {path}")
        records.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    return records


def activate(obj: Any) -> None:
    import bpy

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def link_only(obj: Any, collection: Any) -> Any:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def smooth_mesh(obj: Any) -> None:
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def triangulated_count(obj: Any) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def smart_uv(obj: Any) -> None:
    import bpy

    activate(obj)
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UV0")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.012)
    bpy.ops.object.mode_set(mode="OBJECT")


def apply_modifier(obj: Any, name: str) -> None:
    import bpy

    activate(obj)
    bpy.ops.object.modifier_apply(modifier=name)


def ensure_surface_density(obj: Any, *, minimum_vertices: int, target_triangles: int) -> None:
    while len(obj.data.vertices) < minimum_vertices:
        modifier = obj.modifiers.new(name="SUBDIV_SurfaceDensity", type="SUBSURF")
        modifier.subdivision_type = "CATMULL_CLARK"
        modifier.levels = 1
        modifier.render_levels = 1
        apply_modifier(obj, modifier.name)
    triangles = triangulated_count(obj)
    if triangles > target_triangles:
        modifier = obj.modifiers.new(name="DECIMATE_GameBudget", type="DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = max(0.08, min(1.0, target_triangles / triangles))
        modifier.use_collapse_triangulate = True
        apply_modifier(obj, modifier.name)


def remap_xy_to_dimensions(obj: Any, *, x_min: float, x_extent: float, y_center: float, y_extent: float) -> None:
    xs = [vertex.co.x for vertex in obj.data.vertices]
    ys = [vertex.co.y for vertex in obj.data.vertices]
    if not xs or not ys:
        raise RefinementError(f"Cannot reconcile empty mesh: {obj.name}")
    source_x_min = min(xs)
    source_x_extent = max(xs) - source_x_min
    source_y_min = min(ys)
    source_y_extent = max(ys) - source_y_min
    if source_x_extent <= 1e-8 or source_y_extent <= 1e-8:
        raise RefinementError(f"Degenerate source bounds: {obj.name}")
    target_y_min = y_center - y_extent * 0.5
    for vertex in obj.data.vertices:
        vertex.co.x = x_min + ((vertex.co.x - source_x_min) / source_x_extent) * x_extent
        vertex.co.y = target_y_min + ((vertex.co.y - source_y_min) / source_y_extent) * y_extent
    obj.data.update()


def add_meta_ellipsoid(meta: Any, coordinate: tuple[float, float, float], sizes: tuple[float, float, float]) -> None:
    element = meta.elements.new()
    element.type = "ELLIPSOID"
    element.co = coordinate
    element.radius = 1.0
    element.size_x = sizes[0]
    element.size_y = sizes[1]
    element.size_z = sizes[2]
    element.stiffness = 2.4


def add_meta_ball(meta: Any, coordinate: tuple[float, float, float], radius: float) -> None:
    element = meta.elements.new()
    element.type = "BALL"
    element.co = coordinate
    element.radius = radius
    element.stiffness = 2.4


def build_fresh_high_glove(side: str, center_y: float, source_collection: Any) -> Any:
    import bpy

    sign = -1.0 if side == "R" else 1.0
    meta = bpy.data.metaballs.new(f"SRC_High_Glove_{side}_Meta")
    meta.resolution = 0.0021
    meta.render_resolution = 0.0017
    meta.threshold = 0.62
    obj = bpy.data.objects.new(f"SRC_High_Glove_{side}", meta)
    source_collection.objects.link(obj)

    # Palm volumes are deliberately overlapping, asymmetric ellipsoids. They are
    # converted into one continuous shell; no box/capsule donor survives.
    add_meta_ellipsoid(meta, (-0.018, center_y, 0.000), (0.040, 0.036, 0.027))
    add_meta_ellipsoid(meta, (0.030, center_y, 0.002), (0.058, 0.041, 0.027))
    add_meta_ellipsoid(meta, (0.071, center_y, 0.008), (0.046, 0.042, 0.028))
    add_meta_ellipsoid(meta, (0.028, center_y + sign * 0.030, -0.004), (0.043, 0.026, 0.026))
    add_meta_ellipsoid(meta, (0.012, center_y - sign * 0.026, -0.008), (0.046, 0.022, 0.022))

    for finger in FINGER_ORDER:
        offset = sign * FINGER_OFFSETS[finger]
        length = FINGER_LENGTHS[finger]
        base_x = 0.074
        tip_x = 0.083 + length
        radius = {"Index": 0.0125, "Middle": 0.0130, "Ring": 0.0122, "Little": 0.0108}[finger]
        points = (
            (base_x, center_y + offset, 0.010),
            (base_x + length * 0.28, center_y + offset, 0.009),
            (base_x + length * 0.55, center_y + offset + sign * 0.001, 0.006),
            (base_x + length * 0.79, center_y + offset + sign * 0.001, 0.001),
            (tip_x, center_y + offset, -0.004),
        )
        for index, point in enumerate(points):
            taper = 1.0 - index * 0.065
            add_meta_ellipsoid(meta, point, (radius * 1.34, radius * taper, radius * 0.92 * taper))

    thumb_points = (
        (0.006, center_y + sign * 0.037, -0.006),
        (0.034, center_y + sign * 0.052, -0.014),
        (0.061, center_y + sign * 0.066, -0.022),
        (0.088, center_y + sign * 0.061, -0.030),
    )
    for index, point in enumerate(thumb_points):
        add_meta_ball(meta, point, 0.020 - index * 0.0017)

    activate(obj)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = f"SRC_High_Glove_{side}"
    smooth_mesh(obj)
    obj["SKG_HighPolySource"] = True
    obj["SKG_GeometryOrigin"] = "fresh_metaball_anatomical_field_no_blockout_import"
    return obj


def duplicate_game_glove(high: Any, side: str, center_y: float, asset_collection: Any, leather: Any) -> Any:
    game = high.copy()
    game.data = high.data.copy()
    game.name = f"GEO_GloveShell_{side}"
    asset_collection.objects.link(game)
    remap_xy_to_dimensions(game, x_min=-0.020, x_extent=0.190, y_center=center_y, y_extent=0.085)
    ensure_surface_density(game, minimum_vertices=6200, target_triangles=27000)
    smart_uv(game)
    game.data.materials.append(leather)
    smooth_mesh(game)
    game["SKG_VisibleFinalShell"] = True
    game["SKG_DimensionsClaim"] = "PROJECT_PROVISIONAL_NOT_A_MEASURED_PERCENTILE"
    return game


def create_loft_mesh(
    name: str,
    sections: list[tuple[float, float, float, float]],
    center_y: float,
    collection: Any,
    material: Any,
    *,
    segments: int = 32,
    z_offset: float = 0.0,
    hide_render: bool = False,
) -> Any:
    import bpy

    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for x, radius_y, radius_z, wrinkle in sections:
        for index in range(segments):
            angle = math.tau * index / segments
            ripple = 1.0 + wrinkle * math.sin(angle * 3.0 + x * 61.0)
            vertices.append(
                (
                    x,
                    center_y + math.cos(angle) * radius_y * ripple,
                    z_offset + math.sin(angle) * radius_z * ripple,
                )
            )
    for section in range(len(sections) - 1):
        a = section * segments
        b = (section + 1) * segments
        for index in range(segments):
            nxt = (index + 1) % segments
            faces.append((a + index, a + nxt, b + nxt, b + index))
    faces.append(tuple(reversed(tuple(range(segments)))))
    last = (len(sections) - 1) * segments
    faces.append(tuple(last + index for index in range(segments)))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    smart_uv(obj)
    obj.data.materials.append(material)
    smooth_mesh(obj)
    obj.hide_render = hide_render
    return obj


def create_dorsal_patch(side: str, center_y: float, collection: Any, material: Any) -> Any:
    sections = [
        (-0.005, 0.026, 0.0040, 0.00),
        (0.020, 0.035, 0.0045, 0.00),
        (0.055, 0.036, 0.0045, 0.00),
        (0.084, 0.026, 0.0035, 0.00),
    ]
    obj = create_loft_mesh(
        f"GEO_Glove_DorsalReinforcement_{side}",
        sections,
        center_y,
        collection,
        material,
        segments=28,
        z_offset=0.029,
    )
    obj["SKG_SurfaceDetail"] = "dorsal_reinforcement"
    return obj


def create_curve_tube(
    name: str,
    points: Iterable[tuple[float, float, float]],
    radius: float,
    collection: Any,
    material: Any,
) -> Any:
    import bpy

    curve_data = bpy.data.curves.new(name=f"{name}_Curve", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 8
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 3
    curve_data.use_fill_caps = True
    spline = curve_data.splines.new("BEZIER")
    point_list = list(points)
    spline.bezier_points.add(len(point_list) - 1)
    for point, coordinate in zip(spline.bezier_points, point_list):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve_data)
    collection.objects.link(obj)
    curve_data.materials.append(material)
    activate(obj)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    smart_uv(obj)
    smooth_mesh(obj)
    return obj


def create_rig(collection: Any) -> Any:
    import bpy

    data = bpy.data.armatures.new("RIG_RearGunnerHands_R01_Data")
    rig = bpy.data.objects.new("RIG_RearGunnerHands_R01", data)
    collection.objects.link(rig)
    rig.show_in_front = True
    activate(rig)
    bpy.ops.object.mode_set(mode="EDIT")

    root = data.edit_bones.new("ROOT")
    root.head = (-0.30, 0.0, -0.10)
    root.tail = (-0.30, 0.0, -0.02)
    root.use_deform = False

    for side, center_y in (("R", -0.13), ("L", 0.13)):
        sign = -1.0 if side == "R" else 1.0
        specs: list[tuple[str, tuple[float, float, float], tuple[float, float, float], str]] = [
            (f"DEF_Forearm_{side}", (-0.29, center_y, 0.0), (-0.04, center_y, 0.0), "ROOT"),
            (f"DEF_Wrist_{side}", (-0.04, center_y, 0.0), (0.010, center_y, 0.0), f"DEF_Forearm_{side}"),
            (f"DEF_Palm_{side}", (0.010, center_y, 0.0), (0.082, center_y, 0.006), f"DEF_Wrist_{side}"),
        ]
        for finger in FINGER_ORDER:
            offset = sign * FINGER_OFFSETS[finger]
            length = FINGER_LENGTHS[finger]
            points = [
                (0.072, center_y + offset, 0.008),
                (0.072 + length * 0.36, center_y + offset, 0.007),
                (0.072 + length * 0.69, center_y + offset, 0.002),
                (0.083 + length, center_y + offset, -0.004),
            ]
            parent = f"DEF_Palm_{side}"
            for segment in range(3):
                name = f"DEF_{finger}_{segment + 1:02d}_{side}"
                specs.append((name, points[segment], points[segment + 1], parent))
                parent = name
        thumb_points = [
            (0.008, center_y + sign * 0.032, -0.003),
            (0.037, center_y + sign * 0.052, -0.014),
            (0.065, center_y + sign * 0.066, -0.023),
            (0.090, center_y + sign * 0.061, -0.030),
        ]
        parent = f"DEF_Palm_{side}"
        for segment in range(3):
            name = f"DEF_Thumb_{segment + 1:02d}_{side}"
            specs.append((name, thumb_points[segment], thumb_points[segment + 1], parent))
            parent = name
        for name, head, tail, parent_name in specs:
            bone = data.edit_bones.new(name)
            bone.head = head
            bone.tail = tail
            bone.parent = data.edit_bones[parent_name]
            bone.use_deform = True

    bpy.ops.object.mode_set(mode="OBJECT")
    rig["SKG_RigRole"] = "rear_gunner_first_person_hands_refinement01"
    rig["SKG_DimensionsAreProjectProvisional"] = True
    rig["SKG_MinimumDeformBonesPerSide"] = 18
    return rig


def add_armature_modifier(obj: Any, rig: Any) -> None:
    modifier = obj.modifiers.new(name="ARMATURE_Deform", type="ARMATURE")
    modifier.object = rig
    obj.parent = rig


def add_weight(obj: Any, group_name: str, vertex_index: int, weight: float) -> None:
    group = obj.vertex_groups.get(group_name) or obj.vertex_groups.new(name=group_name)
    group.add([vertex_index], max(0.0, min(1.0, weight)), "REPLACE")


def nearest_segment_parameter(point: Any, start: Any, end: Any) -> tuple[float, float]:
    direction = end - start
    length_squared = direction.length_squared
    if length_squared <= 1e-12:
        return 0.0, (point - start).length
    parameter = max(0.0, min(1.0, (point - start).dot(direction) / length_squared))
    closest = start + direction * parameter
    return parameter, (point - closest).length


def assign_glove_weights(obj: Any, rig: Any, side: str, center_y: float) -> None:
    from mathutils import Vector

    sign = -1.0 if side == "R" else 1.0
    thumb_path = [
        Vector((0.008, center_y + sign * 0.032, -0.003)),
        Vector((0.037, center_y + sign * 0.052, -0.014)),
        Vector((0.065, center_y + sign * 0.066, -0.023)),
        Vector((0.090, center_y + sign * 0.061, -0.030)),
    ]
    for vertex in obj.data.vertices:
        point = vertex.co.copy()
        thumb_candidates: list[tuple[float, int, float]] = []
        for segment in range(3):
            parameter, distance = nearest_segment_parameter(point, thumb_path[segment], thumb_path[segment + 1])
            thumb_candidates.append((distance, segment, parameter))
        thumb_distance, thumb_segment, _thumb_parameter = min(thumb_candidates)
        if thumb_distance < 0.029 and sign * (point.y - center_y) > 0.022:
            add_weight(obj, f"DEF_Thumb_{thumb_segment + 1:02d}_{side}", vertex.index, 1.0)
            continue
        if point.x > 0.066:
            finger = min(
                FINGER_ORDER,
                key=lambda name: abs(point.y - (center_y + sign * FINGER_OFFSETS[name])),
            )
            length = FINGER_LENGTHS[finger]
            normalized = (point.x - 0.068) / max(length, 1e-6)
            segment = 1 if normalized < 0.38 else 2 if normalized < 0.72 else 3
            add_weight(obj, f"DEF_{finger}_{segment:02d}_{side}", vertex.index, 1.0)
        elif point.x < -0.010:
            wrist_weight = max(0.0, min(1.0, (point.x + 0.035) / 0.035))
            add_weight(obj, f"DEF_Wrist_{side}", vertex.index, wrist_weight)
            add_weight(obj, f"DEF_Palm_{side}", vertex.index, 1.0 - wrist_weight)
        else:
            add_weight(obj, f"DEF_Palm_{side}", vertex.index, 1.0)
    add_armature_modifier(obj, rig)


def assign_axis_weights(obj: Any, rig: Any, primary: str, secondary: str | None = None, split_x: float = -0.04) -> None:
    for vertex in obj.data.vertices:
        if secondary is None:
            add_weight(obj, primary, vertex.index, 1.0)
            continue
        blend = max(0.0, min(1.0, (vertex.co.x - (split_x - 0.035)) / 0.07))
        add_weight(obj, primary, vertex.index, 1.0 - blend)
        add_weight(obj, secondary, vertex.index, blend)
    add_armature_modifier(obj, rig)


def pose_map(kind: str) -> dict[str, tuple[float, float, float]]:
    rotations: dict[str, tuple[float, float, float]] = {}
    for side in ("R", "L"):
        rotations[f"DEF_Wrist_{side}"] = (0.0, 0.0, 0.0)
        rotations[f"DEF_Palm_{side}"] = (0.0, 0.0, 0.0)
        for finger in FINGER_ORDER:
            for segment in range(1, 4):
                rotations[f"DEF_{finger}_{segment:02d}_{side}"] = (0.0, 0.0, 0.0)
        for segment in range(1, 4):
            rotations[f"DEF_Thumb_{segment:02d}_{side}"] = (0.0, 0.0, 0.0)

    if kind == "neutral":
        return rotations

    for side in ("R", "L"):
        sign = -1.0 if side == "R" else 1.0
        rotations[f"DEF_Wrist_{side}"] = (math.radians(sign * 4.0), math.radians(-7.0), math.radians(sign * 3.0))
        for finger in FINGER_ORDER:
            for segment, degrees in ((1, -28.0), (2, -46.0), (3, -34.0)):
                rotations[f"DEF_{finger}_{segment:02d}_{side}"] = (0.0, math.radians(degrees), 0.0)
        rotations[f"DEF_Thumb_01_{side}"] = (math.radians(sign * 18.0), math.radians(-20.0), math.radians(sign * 24.0))
        rotations[f"DEF_Thumb_02_{side}"] = (0.0, math.radians(-34.0), 0.0)
        rotations[f"DEF_Thumb_03_{side}"] = (0.0, math.radians(-18.0), 0.0)

    if kind == "rifle_support":
        rotations["DEF_Wrist_L"] = (math.radians(-8.0), math.radians(-13.0), math.radians(11.0))
        return rotations
    if kind == "rifle_ads":
        rotations["DEF_Wrist_R"] = (math.radians(-3.0), math.radians(-8.0), math.radians(-9.0))
        rotations["DEF_Index_01_R"] = (0.0, math.radians(-5.0), 0.0)
        rotations["DEF_Index_02_R"] = (0.0, math.radians(-8.0), 0.0)
        rotations["DEF_Index_03_R"] = (0.0, math.radians(-5.0), 0.0)
        return rotations
    if kind == "igla_support":
        rotations["DEF_Wrist_R"] = (math.radians(-10.0), math.radians(4.0), math.radians(-12.0))
        rotations["DEF_Wrist_L"] = (math.radians(10.0), math.radians(2.0), math.radians(12.0))
        rotations["DEF_Palm_R"] = (0.0, math.radians(-8.0), math.radians(-5.0))
        rotations["DEF_Palm_L"] = (0.0, math.radians(-8.0), math.radians(5.0))
        return rotations
    raise RefinementError(f"Unknown pose kind: {kind}")


def apply_pose(rig: Any, mapping: dict[str, tuple[float, float, float]]) -> None:
    for pose_bone in rig.pose.bones:
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler = mapping.get(pose_bone.name, (0.0, 0.0, 0.0))


def key_pose(rig: Any, action: Any, frame: int, kind: str) -> None:
    rig.animation_data.action = action
    apply_pose(rig, pose_map(kind))
    for pose_bone in rig.pose.bones:
        pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=pose_bone.name)


def create_actions(rig: Any) -> None:
    import bpy

    rig.animation_data_create()
    mapping = {
        "ACT_Neutral": "neutral",
        "ACT_RifleSupport": "rifle_support",
        "ACT_RifleTriggerADS": "rifle_ads",
        "ACT_IglaSupport": "igla_support",
    }
    for action_name, pose_name in mapping.items():
        action = bpy.data.actions.new(action_name)
        key_pose(rig, action, 1, pose_name)

    review = bpy.data.actions.new("ACT_PoseReview")
    for frame, pose_name in ((1, "neutral"), (20, "rifle_support"), (40, "rifle_ads"), (60, "igla_support")):
        key_pose(rig, review, frame, pose_name)
    rig.animation_data.action = review
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 60
    bpy.context.scene.frame_set(1)


def create_collision(side: str, center_y: float, collection: Any, collision_material: Any) -> Any:
    sections = [
        (-0.29, 0.050, 0.044, 0.0),
        (-0.09, 0.048, 0.040, 0.0),
        (0.06, 0.045, 0.034, 0.0),
        (0.17, 0.034, 0.025, 0.0),
    ]
    obj = create_loft_mesh(
        f"UCX_RearGunnerHandForearm_{side}",
        sections,
        center_y,
        collection,
        collision_material,
        segments=12,
        hide_render=True,
    )
    obj["SKG_Collision"] = True
    return obj


def create_materials() -> dict[str, Any]:
    leather = pbr_material(
        "MAT_Glove_BlackLeather_R01",
        (0.012, 0.014, 0.016, 1.0),
        0.0,
        0.38,
        micro_scale=160.0,
        micro_strength=0.16,
    )
    reinforcement = pbr_material(
        "MAT_Glove_Reinforcement_R01",
        (0.026, 0.029, 0.032, 1.0),
        0.0,
        0.52,
        micro_scale=110.0,
        micro_strength=0.12,
    )
    stitch = pbr_material("MAT_Glove_Stitch_R01", (0.15, 0.14, 0.12, 1.0), 0.0, 0.68)
    cloth = pbr_material(
        "MAT_FlightSuit_OliveCloth_R01",
        (0.075, 0.105, 0.080, 1.0),
        0.0,
        0.78,
        micro_scale=220.0,
        micro_strength=0.19,
    )
    collision = pbr_material("MAT_HandForearm_Collision_R01", (0.03, 0.05, 0.07, 1.0), 0.0, 0.95)
    return {
        "leather": leather,
        "reinforcement": reinforcement,
        "stitch": stitch,
        "cloth": cloth,
        "collision": collision,
    }


def build_asset(collection: Any) -> None:
    import bpy

    source_collection = bpy.data.collections.new("SOURCE_HIGH")
    bpy.context.scene.collection.children.link(source_collection)
    materials = create_materials()
    rig = create_rig(collection)

    for side, center_y in (("R", -0.13), ("L", 0.13)):
        high = build_fresh_high_glove(side, center_y, source_collection)
        high.hide_render = True
        high.hide_set(True)
        glove = duplicate_game_glove(high, side, center_y, collection, materials["leather"])
        sleeve = create_loft_mesh(
            f"GEO_FlightSuitSleeve_{side}",
            [
                (-0.29, 0.054, 0.048, 0.025),
                (-0.23, 0.052, 0.045, 0.035),
                (-0.17, 0.049, 0.042, 0.025),
                (-0.11, 0.046, 0.039, 0.045),
                (-0.055, 0.043, 0.035, 0.025),
                (-0.021, 0.041, 0.033, 0.015),
            ],
            center_y,
            collection,
            materials["cloth"],
            segments=40,
        )
        cuff = create_loft_mesh(
            f"GEO_Glove_Cuff_{side}",
            [
                (-0.052, 0.0435, 0.0345, 0.0),
                (-0.036, 0.0455, 0.0360, 0.0),
                (-0.017, 0.0440, 0.0345, 0.0),
            ],
            center_y,
            collection,
            materials["reinforcement"],
            segments=36,
        )
        patch = create_dorsal_patch(side, center_y, collection, materials["reinforcement"])
        sign = -1.0 if side == "R" else 1.0
        seam = create_curve_tube(
            f"GEO_Glove_PalmSeam_{side}",
            [
                (-0.008, center_y + sign * 0.041, -0.020),
                (0.035, center_y + sign * 0.043, -0.023),
                (0.075, center_y + sign * 0.036, -0.018),
            ],
            0.00115,
            collection,
            materials["stitch"],
        )
        collision = create_collision(side, center_y, collection, materials["collision"])

        assign_glove_weights(glove, rig, side, center_y)
        assign_axis_weights(sleeve, rig, f"DEF_Forearm_{side}", f"DEF_Wrist_{side}", split_x=-0.055)
        assign_axis_weights(cuff, rig, f"DEF_Wrist_{side}")
        assign_axis_weights(patch, rig, f"DEF_Palm_{side}")
        assign_axis_weights(seam, rig, f"DEF_Palm_{side}")
        assign_axis_weights(collision, rig, f"DEF_Forearm_{side}", f"DEF_Palm_{side}", split_x=-0.01)

    sockets = {
        "SOCKET_Origin": (0.0, 0.0, 0.0),
        "SOCKET_Wrist_R": (-0.020, -0.13, 0.0),
        "SOCKET_Wrist_L": (-0.020, 0.13, 0.0),
        "SOCKET_Rifle_FiringHand": (0.036, -0.13, -0.014),
        "SOCKET_Rifle_SupportHand": (0.036, 0.13, -0.014),
        "SOCKET_Igla_FiringHand": (0.030, -0.13, 0.020),
        "SOCKET_Igla_SupportHand": (0.030, 0.13, 0.020),
        "SOCKET_ADS_HandAlignment": (-0.012, 0.0, 0.095),
    }
    for name, location in sockets.items():
        socket = add_socket(name, location, collection)
        socket["SKG_SocketContract"] = "refinement01_provisional_weapon_contact"

    create_actions(rig)
    for obj in collection.all_objects:
        obj["SKG_AssetID"] = ASSET_ID
        obj["SKG_DimensionsClaim"] = "PROJECT_PROVISIONAL_NOT_A_MEASURED_PERCENTILE"


def set_lighting(mood: str, materials: dict[str, Any] | None = None) -> None:
    import bpy

    world = bpy.context.scene.world
    key = bpy.data.objects.get("REVIEW_Key")
    fill = bpy.data.objects.get("REVIEW_Fill")
    settings = {
        "daylight": ((0.060, 0.075, 0.095), 1600.0, 650.0, (1.0, 0.86, 0.70)),
        "overcast": ((0.045, 0.052, 0.060), 850.0, 700.0, (0.78, 0.86, 1.0)),
        "night": ((0.006, 0.010, 0.022), 280.0, 160.0, (0.44, 0.62, 1.0)),
        "wet": ((0.035, 0.045, 0.060), 1050.0, 520.0, (0.72, 0.82, 1.0)),
        "cockpit": ((0.010, 0.016, 0.020), 520.0, 240.0, (0.62, 1.0, 0.72)),
    }
    color, key_energy, fill_energy, key_color = settings[mood]
    world.color = color
    if key is not None:
        key.data.energy = key_energy
        key.data.color = key_color
    if fill is not None:
        fill.data.energy = fill_energy
        fill.data.color = (0.55, 0.70, 1.0) if mood in {"night", "wet"} else (0.82, 0.90, 1.0)
    leather = bpy.data.materials.get("MAT_Glove_BlackLeather_R01")
    if leather and leather.use_nodes:
        bsdf = leather.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Roughness"].default_value = 0.24 if mood == "wet" else 0.38


def render_hand_views(asset_collection: Any, output: Path) -> list[Path]:
    import bpy
    from mathutils import Vector

    _review, camera = sdk.add_review_stage(asset_collection)
    scene = bpy.context.scene
    scene.render.resolution_x = 2048
    scene.render.resolution_y = 2048
    scene.render.resolution_percentage = 100
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    views = load_json(CAMERAS)["views"]
    paths: list[Path] = []
    for view in views:
        scene.frame_set(int(view["frame"]))
        set_lighting(str(view["lighting"]))
        camera.location = Vector(view["camera"])
        target = Vector(view["target"])
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.lens = float(view["lens"])
        path = render_dir / f"{view['name']}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def export_rigged_asset(asset_id: str, collection: Any, output: Path) -> tuple[Path, Path]:
    import bpy

    blend_path = output / f"{asset_id}.blend"
    glb_path = output / f"{asset_id}.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in collection.all_objects:
        obj.hide_set(False)
        obj.select_set(True)
    rig = next((obj for obj in collection.all_objects if obj.type == "ARMATURE"), None)
    bpy.context.view_layer.objects.active = rig
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
        export_animation_mode="ACTIONS",
        export_force_sampling=True,
        export_frame_range=True,
        export_skins=True,
    )
    return blend_path, glb_path


def mesh_bounds_at_frame(objects: list[Any], frame: int) -> dict[str, float]:
    import bpy

    bpy.context.scene.frame_set(frame)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    if not points:
        raise RefinementError("No evaluated mesh points were available.")
    return {
        "x_min": min(point.x for point in points),
        "x_max": max(point.x for point in points),
        "y_min": min(point.y for point in points),
        "y_max": max(point.y for point in points),
        "z_min": min(point.z for point in points),
        "z_max": max(point.z for point in points),
    }


def manifold_report(obj: Any) -> dict[str, Any]:
    import bmesh

    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    try:
        nonmanifold = sum(1 for edge in mesh.edges if not edge.is_manifold)
    finally:
        mesh.free()
    return {"object": obj.name, "nonmanifold_edges": nonmanifold}


def create_geometry_rig_receipt(output: Path, collection: Any) -> dict[str, Any]:
    import bpy

    visible = [
        obj
        for obj in collection.all_objects
        if obj.type == "MESH" and not obj.hide_render and not obj.name.startswith("UCX_")
    ]
    vertices = sum(len(obj.data.vertices) for obj in visible)
    triangles = sum(triangulated_count(obj) for obj in visible)
    manifold = [manifold_report(obj) for obj in visible]
    if vertices < MINIMUM_VISIBLE_VERTICES:
        raise RefinementError(f"Visible vertex count {vertices} is below {MINIMUM_VISIBLE_VERTICES}.")
    if triangles > VISIBLE_TRIANGLE_BUDGET:
        raise RefinementError(f"Visible triangle count {triangles} exceeds {VISIBLE_TRIANGLE_BUDGET}.")
    if any(record["nonmanifold_edges"] for record in manifold):
        raise RefinementError(f"Visible mesh has nonmanifold edges: {manifold}")
    rig = next(obj for obj in collection.all_objects if obj.type == "ARMATURE")
    deform_counts = {
        side: sum(1 for bone in rig.data.bones if bone.use_deform and bone.name.endswith(f"_{side}"))
        for side in ("R", "L")
    }
    if any(value < 18 for value in deform_counts.values()):
        raise RefinementError(f"Rig does not meet the 18-deform-bone minimum: {deform_counts}")
    actions = sorted(action.name for action in bpy.data.actions)
    missing_actions = sorted(set(REQUIRED_ACTIONS) - set(actions))
    if missing_actions:
        raise RefinementError(f"Required actions are missing: {missing_actions}")
    neutral_shells = [obj for obj in visible if obj.name.startswith("GEO_GloveShell_")]
    neutral = mesh_bounds_at_frame(neutral_shells, 1)
    payload = {
        "schema": "skyguard.phase2.reargunner-hand-forearm-refinement01.geometry-rig-receipt.v1",
        "asset_id": ASSET_ID,
        "dimension_claim": "PROJECT_PROVISIONAL_NOT_A_MEASURED_PERCENTILE",
        "selected_dimensions_m": {"hand_length": 0.19, "hand_breadth": 0.085, "forearm_plus_hand": 0.46},
        "visible_vertices": vertices,
        "visible_triangles": triangles,
        "manifold": manifold,
        "deform_bones_per_side": deform_counts,
        "actions": actions,
        "neutral_combined_shell_bounds": neutral,
        "sockets": sorted(obj.name for obj in collection.all_objects if obj.type == "EMPTY" and obj.name.startswith("SOCKET_")),
        "materials": sorted(
            {
                slot.material.name
                for obj in visible
                for slot in obj.material_slots
                if slot.material is not None
            }
        ),
    }
    write_json(output / "geometry_rig_receipt.json", payload)
    return payload


def create_pose_receipt(output: Path, collection: Any) -> dict[str, Any]:
    visible = [
        obj
        for obj in collection.all_objects
        if obj.type == "MESH" and not obj.hide_render and not obj.name.startswith("UCX_")
    ]
    frames = {"neutral": 1, "rifle_support": 20, "rifle_trigger_ads": 40, "igla_support": 60}
    bounds = {name: mesh_bounds_at_frame(visible, frame) for name, frame in frames.items()}
    for name, record in bounds.items():
        extents = [record["x_max"] - record["x_min"], record["y_max"] - record["y_min"], record["z_max"] - record["z_min"]]
        if min(extents) <= 0.02 or max(extents) >= 1.20:
            raise RefinementError(f"Pose bounds indicate collapse or runaway deformation: {name} {extents}")
    payload = {
        "schema": "skyguard.phase2.reargunner-hand-forearm-refinement01.pose-deformation-receipt.v1",
        "asset_id": ASSET_ID,
        "frames": frames,
        "evaluated_bounds": bounds,
        "checks": {
            "finite_noncollapsed_bounds": True,
            "weapon_contact_is_provisional": True,
            "cockpit_clearance_requires_unreal": True,
        },
    }
    write_json(output / "pose_deformation_receipt.json", payload)
    return payload


def main() -> int:
    args = sdk.parse_worker_args()
    if args.asset_id != ASSET_ID:
        raise RefinementError(f"Unexpected asset id: {args.asset_id}")
    source_records = verify_authorities()
    sdk.render_review_views = render_hand_views
    sdk.export_asset = export_rigged_asset
    code = sdk.run_worker(ASSET_ID, build_asset, REQUIRED_SOCKETS)
    bpy = __import__("bpy")
    collection = bpy.data.collections["ASSET"]
    geometry = create_geometry_rig_receipt(Path(args.output), collection)
    poses = create_pose_receipt(Path(args.output), collection)
    source_parity = {
        "schema": "skyguard.phase2.reargunner-hand-forearm-refinement01.source-parity-receipt.v1",
        "asset_id": ASSET_ID,
        "authorities": source_records,
        "blockout_geometry_imported": False,
        "external_geometry_imported": False,
        "fresh_source_collection": "SOURCE_HIGH",
    }
    write_json(Path(args.output) / "source_parity_receipt.json", source_parity)
    write_production_receipt(
        Path(args.output),
        ASSET_ID,
        collection,
        source_records,
        {
            "geometry_rig": geometry,
            "pose_deformation": poses,
            "render_count": 12,
            "render_resolution": [2048, 2048],
            "coordinate_contract": {"forward": "+X", "right": "+Y", "up": "+Z", "units": "metres"},
        },
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
