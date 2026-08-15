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
from skyguard_worker_geometry import add_socket, pbr_material, sha256, write_json, write_production_receipt  # noqa: E402


ASSET_ID = "core-reargunner-character-refinement01"
CONTRACT = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_CHARACTER_REFINEMENT01_CONTRACT.json"
POLICY = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_CHARACTER_REFINEMENT01_REFERENCE_POLICY.json"
CAMERAS = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_CHARACTER_REFINEMENT01_CAMERAS.json"
RUBRIC = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_CHARACTER_REFINEMENT01_VISUAL_RUBRIC.json"
ANTHROPOMETRIC = (
    PROJECT_ROOT
    / "References"
    / "CombatAssets"
    / "TechnicalIntake_Cycle02"
    / "reports"
    / "GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_CHARACTER_ANTHROPOMETRIC_CONTRACT.json"
)
CHARACTER_SMOKE_ADDENDUM = PROJECT_ROOT / "Docs" / "AAA_Review" / "TOOLCHAIN_WAVE08_CHARACTER_SMOKE_RECOVERY01_ACCEPTANCE_ADDENDUM_2026-08-08.md"
CHARACTER_SMOKE_RESULT = (
    PROJECT_ROOT
    / "Saved"
    / "BuildAttempts"
    / "TOOLCHAIN_WAVE08_CHARACTER_SMOKE_RECOVERY01"
    / "attempt_01"
    / "probe_result.json"
)
CHARACTER_SMOKE_TERMINAL = CHARACTER_SMOKE_RESULT.with_name("terminal_manifest.json")
PHOTO_FREEZE = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_R6_PHOTO_INTAKE_CYCLE03_FREEZE_2026-08-04.json"
TECHNICAL_FREEZE = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_YAK52_R6_TECHNICAL_REFERENCE_INTAKE_CYCLE04_FREEZE.json"
ONBOARD_VIDEO = (
    PROJECT_ROOT
    / "References"
    / "Yak52"
    / "R6_PhotoIntake_Cycle03"
    / "Raw"
    / "yak52_onboard_rear_gunner_user_reference_001.mp4"
)
EXTERIOR_IMAGE = ONBOARD_VIDEO.with_name("yak52_exterior_side_user_reference_001.png")
COCKPIT_PAGE_111 = (
    PROJECT_ROOT
    / "References"
    / "Yak52"
    / "R6_TechnicalIntake_Cycle04"
    / "DerivedPages"
    / "render_rle_cockpit-111.png"
)
COCKPIT_PAGE_112 = COCKPIT_PAGE_111.with_name("render_rle_cockpit-112.png")
HAND_OFFLINE_FREEZE = PROJECT_ROOT / "Docs" / "AAA_Review" / "PHASE2_REARGUNNER_HAND_FOREARM_REFINEMENT01_OFFLINE_DESIGN_FREEZE.json"

EXPECTED_AUTHORITIES: dict[Path, tuple[int, str]] = {
    ANTHROPOMETRIC: (2195, "9702492331d8b2e73e45f4c42f2a9933081e48f1aac00aa2c3f02bb5591c0e09"),
    CHARACTER_SMOKE_ADDENDUM: (3029, "54f488005e544f4f53981a370c030b64512e9fcf65d9ba504fc1717b0e670487"),
    CHARACTER_SMOKE_RESULT: (1555, "debd17f57a08b0587c6e4e9221cffbbcaa7efb4b65127662d365de5fcf11d60f"),
    CHARACTER_SMOKE_TERMINAL: (3690, "47199051cf63f4d3ba6b17d12173b7f6d1692f82b6e0c8b65eb8c153cd882068"),
    PHOTO_FREEZE: (6710, "41e9df1a9116ed2cbb7816be73aa428a73e9d67b22d8a3407cc9d8bb2d96dac2"),
    TECHNICAL_FREEZE: (6695, "23a65a59e687f3e8ebdce85a27a6d205bed37fc542d0d25830bc8dd640397ee0"),
    ONBOARD_VIDEO: (4271526, "91c9b0a1d595ab2cf5df6c9b37d4b5e76c46e32d1373e2e7d7871bcafcf62061"),
    EXTERIOR_IMAGE: (2959485, "390162ac3d3c73c0567bcf822de2363908b27de9ea79b7796c6bcca143c41f5d"),
    COCKPIT_PAGE_111: (912637, "0d78e37d77bc879fbeb814d5d2a8bfd64a3a127b646424f0428536c6a8bd95db"),
    COCKPIT_PAGE_112: (819340, "ecd0925445d0899628196751e74657fb81a9784836cc6c2a1d63f65ae5880863"),
    HAND_OFFLINE_FREEZE: (3972, "5156fb442b892165213eef627b85d9bc1d80d0661d9086f53e39ecd8279d2a1d"),
}

REQUIRED_SOCKETS = [
    "SOCKET_Origin",
    "SOCKET_SeatDatum",
    "SOCKET_Pelvis",
    "SOCKET_Head",
    "SOCKET_RearGunnerCamera",
    "SOCKET_Wrist_R",
    "SOCKET_Wrist_L",
    "SOCKET_RifleShoulder",
    "SOCKET_IglaShoulder",
    "SOCKET_WeaponSweepOrigin",
]
REQUIRED_ACTIONS = [
    "ACT_SeatedNeutral",
    "ACT_RifleSupport",
    "ACT_RifleTriggerADS",
    "ACT_IglaSupport",
    "ACT_TurbulenceBrace",
]
MINIMUM_VISIBLE_VERTICES = 30000
VISIBLE_TRIANGLE_BUDGET = 180000

SEAT_DATUM = (0.0, 0.0, 0.0)
HEAD_TOP_Z = 0.895
EYE_Z = 0.780
SHOULDER_Y = 0.230
HIP_Y = 0.165
SHOULDER = {"R": (0.0, -SHOULDER_Y, 0.590), "L": (0.0, SHOULDER_Y, 0.590)}
ELBOW = {"R": (0.270, -0.300, 0.370), "L": (0.270, 0.300, 0.370)}
WRIST = {"R": (0.550, -0.180, 0.350), "L": (0.550, 0.180, 0.350)}
HIP = {"R": (0.020, -HIP_Y, 0.145), "L": (0.020, HIP_Y, 0.145)}
KNEE = {"R": (0.380, -0.135, -0.080), "L": (0.380, 0.135, -0.080)}
ANKLE = {"R": (0.300, -0.135, -0.475), "L": (0.300, 0.135, -0.475)}
TOE = {"R": (0.530, -0.135, -0.500), "L": (0.530, 0.135, -0.500)}


class CharacterError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CharacterError(f"Expected JSON object: {path}")
    return payload


def verify_authorities() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path, (expected_bytes, expected_hash) in EXPECTED_AUTHORITIES.items():
        if not path.is_file():
            raise CharacterError(f"Missing immutable authority: {path}")
        actual_bytes = path.stat().st_size
        actual_hash = sha256(path)
        if actual_bytes != expected_bytes or actual_hash != expected_hash:
            raise CharacterError(f"Immutable authority mismatch: {path}")
        records.append(
            {
                "path": str(path),
                "bytes": actual_bytes,
                "sha256": actual_hash,
                "use": "read-only capability, reference, dimensional or compatibility authority",
            }
        )
    for path in (CONTRACT, POLICY, CAMERAS, RUBRIC):
        if not path.is_file():
            raise CharacterError(f"Missing governed contract: {path}")
        records.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    smoke = load_json(CHARACTER_SMOKE_RESULT)
    if smoke.get("classification") != "PASSED_CHARACTER_STACK_CAPABILITY_SMOKE":
        raise CharacterError("The accepted UE character-stack capability smoke is not passing.")
    if smoke.get("asset_or_world_save_attempted") is not False:
        raise CharacterError("Character-stack smoke preservation boundary changed.")
    return records


def activate(obj: Any) -> None:
    import bpy

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def smooth_mesh(obj: Any) -> None:
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def smart_uv(obj: Any) -> None:
    import bpy

    activate(obj)
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UV0")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(64.0), island_margin=0.010)
    bpy.ops.object.mode_set(mode="OBJECT")


def apply_modifier(obj: Any, name: str) -> None:
    import bpy

    activate(obj)
    bpy.ops.object.modifier_apply(modifier=name)


def triangulated_count(obj: Any) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def prepare_high_source(obj: Any, *, levels: int = 2) -> Any:
    modifier = obj.modifiers.new(name="SUBDIV_HighSource", type="SUBSURF")
    modifier.subdivision_type = "CATMULL_CLARK"
    modifier.levels = levels
    modifier.render_levels = levels
    apply_modifier(obj, modifier.name)
    smooth_mesh(obj)
    obj["SKG_HighPolySource"] = True
    obj["SKG_GeometryOrigin"] = "fresh_governed_parametric_surface"
    return obj


def duplicate_game_mesh(high: Any, name: str, collection: Any, material: Any, target_triangles: int) -> Any:
    game = high.copy()
    game.data = high.data.copy()
    game.name = name
    collection.objects.link(game)
    triangles = triangulated_count(game)
    if triangles > target_triangles:
        modifier = game.modifiers.new(name="DECIMATE_GameBudget", type="DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = max(0.06, min(1.0, target_triangles / triangles))
        modifier.use_collapse_triangulate = True
        apply_modifier(game, modifier.name)
    smart_uv(game)
    game.data.materials.append(material)
    smooth_mesh(game)
    game["SKG_VisibleFinalShell"] = True
    game["SKG_DimensionsClaim"] = "PROJECT_PROVISIONAL_NOT_A_MEASURED_PERCENTILE"
    return game


def signed_power(value: float, exponent: float) -> float:
    return math.copysign(abs(value) ** exponent, value)


def create_superellipsoid(
    name: str,
    center: tuple[float, float, float],
    radii: tuple[float, float, float],
    collection: Any,
    *,
    segments: int = 48,
    rings: int = 24,
    shape: float = 1.15,
    forward_bias: float = 0.0,
) -> Any:
    import bpy

    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    exponent = 2.0 / max(shape, 0.2)
    for ring in range(rings + 1):
        latitude = -math.pi * 0.5 + math.pi * ring / rings
        cos_lat = math.cos(latitude)
        sin_lat = math.sin(latitude)
        for segment in range(segments):
            longitude = math.tau * segment / segments
            cos_lon = math.cos(longitude)
            sin_lon = math.sin(longitude)
            x = radii[0] * signed_power(cos_lat, exponent) * signed_power(cos_lon, exponent)
            y = radii[1] * signed_power(cos_lat, exponent) * signed_power(sin_lon, exponent)
            z = radii[2] * signed_power(sin_lat, exponent)
            if x > 0.0:
                x *= 1.0 + forward_bias
            vertices.append((center[0] + x, center[1] + y, center[2] + z))
    for ring in range(rings):
        first = ring * segments
        second = (ring + 1) * segments
        for segment in range(segments):
            nxt = (segment + 1) % segments
            faces.append((first + segment, first + nxt, second + nxt, second + segment))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    smooth_mesh(obj)
    return obj


def stable_frame(points: list[Any], index: int) -> tuple[Any, Any]:
    from mathutils import Vector

    if index == 0:
        tangent = (points[1] - points[0]).normalized()
    elif index == len(points) - 1:
        tangent = (points[-1] - points[-2]).normalized()
    else:
        tangent = (points[index + 1] - points[index - 1]).normalized()
    reference = Vector((0.0, 0.0, 1.0))
    if abs(tangent.dot(reference)) > 0.90:
        reference = Vector((1.0, 0.0, 0.0))
    axis_u = tangent.cross(reference).normalized()
    axis_v = tangent.cross(axis_u).normalized()
    return axis_u, axis_v


def create_path_loft(
    name: str,
    sections: list[tuple[tuple[float, float, float], float, float, float]],
    collection: Any,
    *,
    segments: int = 36,
) -> Any:
    import bpy
    from mathutils import Vector

    points = [Vector(item[0]) for item in sections]
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for section_index, (center, radius_u, radius_v, wrinkle) in enumerate(sections):
        center_vector = Vector(center)
        axis_u, axis_v = stable_frame(points, section_index)
        for segment in range(segments):
            angle = math.tau * segment / segments
            ripple = 1.0 + wrinkle * math.sin(angle * 3.0 + section_index * 1.37)
            point = center_vector + axis_u * (math.cos(angle) * radius_u * ripple) + axis_v * (math.sin(angle) * radius_v * ripple)
            vertices.append(tuple(point))
    for section_index in range(len(sections) - 1):
        first = section_index * segments
        second = (section_index + 1) * segments
        for segment in range(segments):
            nxt = (segment + 1) % segments
            faces.append((first + segment, first + nxt, second + nxt, second + segment))
    faces.append(tuple(reversed(tuple(range(segments)))))
    last = (len(sections) - 1) * segments
    faces.append(tuple(last + segment for segment in range(segments)))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    smooth_mesh(obj)
    return obj


def create_curve_tube(name: str, points: Iterable[tuple[float, float, float]], radius: float, collection: Any, material: Any) -> Any:
    import bpy

    curve = bpy.data.curves.new(f"{name}_Curve", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 8
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    curve.use_fill_caps = True
    spline = curve.splines.new("BEZIER")
    coordinates = list(points)
    spline.bezier_points.add(len(coordinates) - 1)
    for point, coordinate in zip(spline.bezier_points, coordinates):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.materials.append(material)
    activate(obj)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    smart_uv(obj)
    smooth_mesh(obj)
    return obj


def create_materials() -> dict[str, Any]:
    olive = pbr_material(
        "MAT_FlightSuit_Olive_R01",
        (0.075, 0.105, 0.080, 1.0),
        0.0,
        0.78,
        micro_scale=220.0,
        micro_strength=0.18,
    )
    shadow = pbr_material(
        "MAT_FlightSuit_Shadow_R01",
        (0.045, 0.060, 0.050, 1.0),
        0.0,
        0.84,
        micro_scale=190.0,
        micro_strength=0.14,
    )
    footwear = pbr_material(
        "MAT_Footwear_Black_R01",
        (0.018, 0.020, 0.021, 1.0),
        0.0,
        0.50,
        micro_scale=115.0,
        micro_strength=0.15,
    )
    headform = pbr_material(
        "MAT_Headform_NeutralCloth_R01",
        (0.035, 0.041, 0.039, 1.0),
        0.0,
        0.74,
        micro_scale=175.0,
        micro_strength=0.16,
    )
    stitch = pbr_material("MAT_Character_Stitch_R01", (0.19, 0.18, 0.14, 1.0), 0.0, 0.68)
    zipper = pbr_material("MAT_Character_Zipper_R01", (0.12, 0.13, 0.12, 1.0), 0.65, 0.32)
    collision = pbr_material("MAT_Character_Collision_R01", (0.025, 0.045, 0.065, 1.0), 0.0, 0.95)
    return {
        "olive": olive,
        "shadow": shadow,
        "footwear": footwear,
        "headform": headform,
        "stitch": stitch,
        "zipper": zipper,
        "collision": collision,
    }


def add_source_and_game(
    source_collection: Any,
    asset_collection: Any,
    high: Any,
    game_name: str,
    material: Any,
    target_triangles: int,
) -> Any:
    high.name = f"SRC_High_{game_name.removeprefix('GEO_')}"
    prepare_high_source(high)
    game = duplicate_game_mesh(high, game_name, asset_collection, material, target_triangles)
    high.hide_render = True
    high.hide_set(True)
    return game


def create_rig(collection: Any) -> Any:
    import bpy

    data = bpy.data.armatures.new("RIG_RearGunnerCharacter_R01_Data")
    rig = bpy.data.objects.new("RIG_RearGunnerCharacter_R01", data)
    collection.objects.link(rig)
    rig.show_in_front = True
    activate(rig)
    bpy.ops.object.mode_set(mode="EDIT")

    specs: list[tuple[str, tuple[float, float, float], tuple[float, float, float], str | None, bool]] = [
        ("ROOT", (0.0, 0.0, -0.06), (0.0, 0.0, 0.04), None, False),
        ("DEF_Pelvis", (0.0, 0.0, 0.08), (0.0, 0.0, 0.20), "ROOT", True),
        ("DEF_Abdomen", (0.0, 0.0, 0.20), (0.0, 0.0, 0.32), "DEF_Pelvis", True),
        ("DEF_Spine01", (0.0, 0.0, 0.32), (0.0, 0.0, 0.43), "DEF_Abdomen", True),
        ("DEF_Spine02", (0.0, 0.0, 0.43), (0.0, 0.0, 0.53), "DEF_Spine01", True),
        ("DEF_Chest", (0.0, 0.0, 0.53), (0.0, 0.0, 0.62), "DEF_Spine02", True),
        ("DEF_Neck", (0.0, 0.0, 0.62), (0.0, 0.0, 0.70), "DEF_Chest", True),
        ("DEF_Head", (0.0, 0.0, 0.70), (0.0, 0.0, 0.84), "DEF_Neck", True),
    ]
    for side in ("R", "L"):
        shoulder = SHOULDER[side]
        elbow = ELBOW[side]
        wrist = WRIST[side]
        clavicle_head = (0.0, 0.0, 0.575)
        upper_mid = tuple((shoulder[index] + elbow[index]) * 0.5 for index in range(3))
        lower_mid = tuple((elbow[index] + wrist[index]) * 0.5 for index in range(3))
        specs.extend(
            [
                (f"DEF_Clavicle_{side}", clavicle_head, shoulder, "DEF_Chest", True),
                (f"DEF_UpperArm_{side}", shoulder, upper_mid, f"DEF_Clavicle_{side}", True),
                (f"DEF_UpperArmTwist_{side}", upper_mid, elbow, f"DEF_UpperArm_{side}", True),
                (f"DEF_Forearm_{side}", elbow, lower_mid, f"DEF_UpperArmTwist_{side}", True),
                (f"DEF_ForearmTwist_{side}", lower_mid, wrist, f"DEF_Forearm_{side}", True),
                (f"DEF_Wrist_{side}", wrist, (wrist[0] + 0.05, wrist[1], wrist[2]), f"DEF_ForearmTwist_{side}", True),
            ]
        )
        hip = HIP[side]
        knee = KNEE[side]
        ankle = ANKLE[side]
        toe = TOE[side]
        thigh_mid = tuple((hip[index] + knee[index]) * 0.5 for index in range(3))
        calf_mid = tuple((knee[index] + ankle[index]) * 0.5 for index in range(3))
        foot_mid = tuple((ankle[index] + toe[index]) * 0.5 for index in range(3))
        specs.extend(
            [
                (f"DEF_Thigh_{side}", hip, thigh_mid, "DEF_Pelvis", True),
                (f"DEF_ThighTwist_{side}", thigh_mid, knee, f"DEF_Thigh_{side}", True),
                (f"DEF_Calf_{side}", knee, calf_mid, f"DEF_ThighTwist_{side}", True),
                (f"DEF_CalfTwist_{side}", calf_mid, ankle, f"DEF_Calf_{side}", True),
                (f"DEF_Foot_{side}", ankle, foot_mid, f"DEF_CalfTwist_{side}", True),
                (f"DEF_Toe_{side}", foot_mid, toe, f"DEF_Foot_{side}", True),
            ]
        )

    for name, head, tail, parent_name, deform in specs:
        bone = data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
        bone.use_deform = deform
        if parent_name:
            bone.parent = data.edit_bones[parent_name]
    bpy.ops.object.mode_set(mode="OBJECT")
    rig["SKG_RigRole"] = "rear_gunner_seated_body_refinement01"
    rig["SKG_DimensionsClaim"] = "PROJECT_PROVISIONAL_NOT_A_MEASURED_PERCENTILE"
    return rig


def add_armature_modifier(obj: Any, rig: Any) -> None:
    modifier = obj.modifiers.new(name="ARMATURE_Deform", type="ARMATURE")
    modifier.object = rig
    obj.parent = rig


def add_weight(obj: Any, group_name: str, vertex_index: int, weight: float) -> None:
    group = obj.vertex_groups.get(group_name) or obj.vertex_groups.new(name=group_name)
    group.add([vertex_index], max(0.0, min(1.0, weight)), "REPLACE")


def assign_single(obj: Any, rig: Any, bone: str) -> None:
    for vertex in obj.data.vertices:
        add_weight(obj, bone, vertex.index, 1.0)
    add_armature_modifier(obj, rig)


def assign_torso(obj: Any, rig: Any) -> None:
    chain = [
        (0.17, "DEF_Pelvis"),
        (0.28, "DEF_Abdomen"),
        (0.39, "DEF_Spine01"),
        (0.50, "DEF_Spine02"),
        (0.62, "DEF_Chest"),
    ]
    for vertex in obj.data.vertices:
        bone = min(chain, key=lambda item: abs(vertex.co.z - item[0]))[1]
        add_weight(obj, bone, vertex.index, 1.0)
    add_armature_modifier(obj, rig)


def nearest_segment_parameter(point: Any, start: Any, end: Any) -> tuple[float, float]:
    direction = end - start
    length_squared = direction.length_squared
    if length_squared <= 1e-12:
        return 0.0, (point - start).length
    parameter = max(0.0, min(1.0, (point - start).dot(direction) / length_squared))
    closest = start + direction * parameter
    return parameter, (point - closest).length


def assign_limb(obj: Any, rig: Any, side: str, kind: str) -> None:
    from mathutils import Vector

    if kind == "arm":
        points = [Vector(SHOULDER[side]), Vector(ELBOW[side]), Vector(WRIST[side])]
        segments = [
            (f"DEF_UpperArm_{side}", f"DEF_UpperArmTwist_{side}"),
            (f"DEF_Forearm_{side}", f"DEF_ForearmTwist_{side}"),
        ]
    elif kind == "leg":
        points = [Vector(HIP[side]), Vector(KNEE[side]), Vector(ANKLE[side])]
        segments = [
            (f"DEF_Thigh_{side}", f"DEF_ThighTwist_{side}"),
            (f"DEF_Calf_{side}", f"DEF_CalfTwist_{side}"),
        ]
    else:
        raise CharacterError(f"Unknown limb kind: {kind}")
    for vertex in obj.data.vertices:
        point = vertex.co.copy()
        candidates = []
        for index in range(2):
            parameter, distance = nearest_segment_parameter(point, points[index], points[index + 1])
            candidates.append((distance, index, parameter))
        _distance, segment_index, parameter = min(candidates)
        primary, twist = segments[segment_index]
        add_weight(obj, primary, vertex.index, 1.0 - parameter)
        add_weight(obj, twist, vertex.index, parameter)
    add_armature_modifier(obj, rig)


def pose_map(kind: str) -> dict[str, tuple[float, float, float]]:
    names = [
        "DEF_Pelvis",
        "DEF_Abdomen",
        "DEF_Spine01",
        "DEF_Spine02",
        "DEF_Chest",
        "DEF_Neck",
        "DEF_Head",
    ]
    for side in ("R", "L"):
        names.extend(
            [
                f"DEF_Clavicle_{side}",
                f"DEF_UpperArm_{side}",
                f"DEF_UpperArmTwist_{side}",
                f"DEF_Forearm_{side}",
                f"DEF_ForearmTwist_{side}",
                f"DEF_Wrist_{side}",
                f"DEF_Thigh_{side}",
                f"DEF_ThighTwist_{side}",
                f"DEF_Calf_{side}",
                f"DEF_CalfTwist_{side}",
                f"DEF_Foot_{side}",
                f"DEF_Toe_{side}",
            ]
        )
    rotations = {name: (0.0, 0.0, 0.0) for name in names}
    if kind == "neutral":
        return rotations
    if kind == "rifle_support":
        rotations["DEF_Chest"] = (0.0, math.radians(-4.0), 0.0)
        rotations["DEF_UpperArm_R"] = (math.radians(-18.0), math.radians(-24.0), math.radians(-12.0))
        rotations["DEF_Forearm_R"] = (0.0, math.radians(-38.0), math.radians(12.0))
        rotations["DEF_UpperArm_L"] = (math.radians(16.0), math.radians(-30.0), math.radians(18.0))
        rotations["DEF_Forearm_L"] = (0.0, math.radians(-46.0), math.radians(-16.0))
        return rotations
    if kind == "rifle_ads":
        rotations.update(pose_map("rifle_support"))
        rotations["DEF_Chest"] = (0.0, math.radians(-8.0), math.radians(-2.0))
        rotations["DEF_Neck"] = (0.0, math.radians(-5.0), math.radians(2.0))
        rotations["DEF_Head"] = (0.0, math.radians(-4.0), math.radians(1.0))
        return rotations
    if kind == "igla_support":
        rotations["DEF_Chest"] = (math.radians(-2.0), math.radians(-6.0), math.radians(5.0))
        rotations["DEF_UpperArm_R"] = (math.radians(-30.0), math.radians(-42.0), math.radians(-18.0))
        rotations["DEF_Forearm_R"] = (0.0, math.radians(-52.0), math.radians(15.0))
        rotations["DEF_UpperArm_L"] = (math.radians(24.0), math.radians(-38.0), math.radians(26.0))
        rotations["DEF_Forearm_L"] = (0.0, math.radians(-48.0), math.radians(-20.0))
        return rotations
    if kind == "brace":
        rotations["DEF_Abdomen"] = (math.radians(7.0), 0.0, 0.0)
        rotations["DEF_Chest"] = (math.radians(-6.0), math.radians(-10.0), 0.0)
        rotations["DEF_UpperArm_R"] = (math.radians(-25.0), math.radians(-18.0), math.radians(-20.0))
        rotations["DEF_UpperArm_L"] = (math.radians(25.0), math.radians(-18.0), math.radians(20.0))
        rotations["DEF_Forearm_R"] = (0.0, math.radians(-62.0), 0.0)
        rotations["DEF_Forearm_L"] = (0.0, math.radians(-62.0), 0.0)
        return rotations
    raise CharacterError(f"Unknown pose kind: {kind}")


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
        "ACT_SeatedNeutral": "neutral",
        "ACT_RifleSupport": "rifle_support",
        "ACT_RifleTriggerADS": "rifle_ads",
        "ACT_IglaSupport": "igla_support",
        "ACT_TurbulenceBrace": "brace",
    }
    for action_name, pose_name in mapping.items():
        action = bpy.data.actions.new(action_name)
        key_pose(rig, action, 1, pose_name)
    review = bpy.data.actions.new("ACT_PoseReview")
    for frame, pose_name in ((1, "neutral"), (20, "rifle_support"), (40, "rifle_ads"), (60, "igla_support"), (80, "brace")):
        key_pose(rig, review, frame, pose_name)
    rig.animation_data.action = review
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 80
    bpy.context.scene.frame_set(1)


def build_asset(collection: Any) -> None:
    import bpy

    source = bpy.data.collections.new("SOURCE_HIGH")
    bpy.context.scene.collection.children.link(source)
    materials = create_materials()
    rig = create_rig(collection)

    torso_high = create_path_loft(
        "TorsoBase",
        [
            ((0.020, 0.0, 0.200), 0.155, 0.125, 0.025),
            ((0.030, 0.0, 0.285), 0.180, 0.145, 0.035),
            ((0.025, 0.0, 0.385), 0.205, 0.155, 0.025),
            ((0.010, 0.0, 0.485), 0.225, 0.150, 0.030),
            ((0.000, 0.0, 0.575), 0.235, 0.135, 0.015),
            ((0.000, 0.0, 0.625), 0.170, 0.110, 0.010),
        ],
        source,
        segments=48,
    )
    torso = add_source_and_game(source, collection, torso_high, "GEO_FlightSuit_Torso", materials["olive"], 34000)
    assign_torso(torso, rig)

    pelvis_high = create_superellipsoid("PelvisBase", (0.015, 0.0, 0.145), (0.180, 0.180, 0.150), source, shape=1.35, forward_bias=0.08)
    pelvis = add_source_and_game(source, collection, pelvis_high, "GEO_FlightSuit_SeatedPelvis", materials["shadow"], 18000)
    assign_single(pelvis, rig, "DEF_Pelvis")

    neck_high = create_path_loft(
        "NeckBase",
        [((0.0, 0.0, 0.610), 0.076, 0.070, 0.0), ((0.0, 0.0, 0.695), 0.072, 0.066, 0.0)],
        source,
        segments=36,
    )
    neck = add_source_and_game(source, collection, neck_high, "GEO_Character_NeckCover", materials["headform"], 6000)
    assign_single(neck, rig, "DEF_Neck")

    head_high = create_superellipsoid("HeadformBase", (0.0, 0.0, 0.785), (0.100, 0.087, 0.110), source, segments=56, rings=28, shape=1.05, forward_bias=0.06)
    head = add_source_and_game(source, collection, head_high, "GEO_Character_NeutralHeadform", materials["headform"], 18000)
    assign_single(head, rig, "DEF_Head")
    head["SKG_IdentityPolicy"] = "neutral_nonidentifying_cloth_headform_not_actual_headgear"

    for side in ("R", "L"):
        shoulder = SHOULDER[side]
        elbow = ELBOW[side]
        wrist = WRIST[side]
        sign = -1.0 if side == "R" else 1.0
        arm_high = create_path_loft(
            f"ArmBase_{side}",
            [
                (shoulder, 0.078, 0.070, 0.015),
                ((shoulder[0] * 0.65 + elbow[0] * 0.35, shoulder[1] * 0.65 + elbow[1] * 0.35, shoulder[2] * 0.65 + elbow[2] * 0.35), 0.072, 0.064, 0.025),
                ((shoulder[0] * 0.25 + elbow[0] * 0.75, shoulder[1] * 0.25 + elbow[1] * 0.75, shoulder[2] * 0.25 + elbow[2] * 0.75), 0.064, 0.058, 0.040),
                (elbow, 0.062, 0.055, 0.050),
                ((elbow[0] * 0.65 + wrist[0] * 0.35, elbow[1] * 0.65 + wrist[1] * 0.35, elbow[2] * 0.65 + wrist[2] * 0.35), 0.058, 0.051, 0.030),
                ((elbow[0] * 0.25 + wrist[0] * 0.75, elbow[1] * 0.25 + wrist[1] * 0.75, elbow[2] * 0.25 + wrist[2] * 0.75), 0.049, 0.044, 0.025),
                (wrist, 0.043, 0.038, 0.010),
            ],
            source,
            segments=40,
        )
        arm = add_source_and_game(source, collection, arm_high, f"GEO_FlightSuit_Arm_{side}", materials["olive"], 18000)
        assign_limb(arm, rig, side, "arm")

        hip = HIP[side]
        knee = KNEE[side]
        ankle = ANKLE[side]
        leg_high = create_path_loft(
            f"LegBase_{side}",
            [
                (hip, 0.105, 0.095, 0.020),
                ((hip[0] * 0.60 + knee[0] * 0.40, hip[1] * 0.60 + knee[1] * 0.40, hip[2] * 0.60 + knee[2] * 0.40), 0.096, 0.086, 0.030),
                ((hip[0] * 0.20 + knee[0] * 0.80, hip[1] * 0.20 + knee[1] * 0.80, hip[2] * 0.20 + knee[2] * 0.80), 0.084, 0.077, 0.045),
                (knee, 0.078, 0.072, 0.050),
                ((knee[0] * 0.60 + ankle[0] * 0.40, knee[1] * 0.60 + ankle[1] * 0.40, knee[2] * 0.60 + ankle[2] * 0.40), 0.071, 0.065, 0.028),
                ((knee[0] * 0.20 + ankle[0] * 0.80, knee[1] * 0.20 + ankle[1] * 0.80, knee[2] * 0.20 + ankle[2] * 0.80), 0.058, 0.054, 0.020),
                (ankle, 0.052, 0.050, 0.010),
            ],
            source,
            segments=40,
        )
        leg = add_source_and_game(source, collection, leg_high, f"GEO_FlightSuit_Leg_{side}", materials["shadow"], 20000)
        assign_limb(leg, rig, side, "leg")

        boot_center = ((ankle[0] + TOE[side][0]) * 0.5, ankle[1], (ankle[2] + TOE[side][2]) * 0.5)
        boot_high = create_superellipsoid(f"BootBase_{side}", boot_center, (0.135, 0.062, 0.065), source, segments=44, rings=22, shape=1.35, forward_bias=0.12)
        boot = add_source_and_game(source, collection, boot_high, f"GEO_Footwear_{side}", materials["footwear"], 9000)
        assign_single(boot, rig, f"DEF_Foot_{side}")
        boot["SKG_FootwearIdentity"] = "generic_unmarked_project_provisional"

        shoulder_seam = create_curve_tube(
            f"GEO_ShoulderSeam_{side}",
            [
                (0.02, sign * 0.17, 0.59),
                (0.03, sign * 0.205, 0.575),
                (0.055, sign * 0.245, 0.545),
            ],
            0.0014,
            collection,
            materials["stitch"],
        )
        assign_single(shoulder_seam, rig, f"DEF_Clavicle_{side}")

    zipper = create_curve_tube(
        "GEO_FlightSuit_Zipper",
        [(0.142, 0.0, 0.270), (0.150, 0.0, 0.410), (0.132, 0.0, 0.565)],
        0.0020,
        collection,
        materials["zipper"],
    )
    assign_torso(zipper, rig)

    for side, y in (("R", -0.092), ("L", 0.092)):
        pocket_high = create_superellipsoid(f"PocketBase_{side}", (0.148, y, 0.370), (0.012, 0.060, 0.055), source, segments=32, rings=16, shape=1.45)
        pocket = add_source_and_game(source, collection, pocket_high, f"GEO_FlightSuit_ChestPocket_{side}", materials["olive"], 3000)
        assign_single(pocket, rig, "DEF_Spine01")

    collision_specs = [
        ("UCX_RearGunner_Torso", (0.02, 0.0, 0.41), (0.17, 0.22, 0.25), "DEF_Spine01"),
        ("UCX_RearGunner_Pelvis", (0.02, 0.0, 0.15), (0.18, 0.18, 0.15), "DEF_Pelvis"),
        ("UCX_RearGunner_Head", (0.0, 0.0, 0.785), (0.10, 0.087, 0.11), "DEF_Head"),
    ]
    for name, center, radii, bone in collision_specs:
        collision = create_superellipsoid(name, center, radii, collection, segments=20, rings=10, shape=1.25)
        smart_uv(collision)
        collision.data.materials.append(materials["collision"])
        collision.hide_render = True
        collision["SKG_Collision"] = True
        assign_single(collision, rig, bone)

    sockets = {
        "SOCKET_Origin": SEAT_DATUM,
        "SOCKET_SeatDatum": SEAT_DATUM,
        "SOCKET_Pelvis": (0.0, 0.0, 0.145),
        "SOCKET_Head": (0.0, 0.0, 0.785),
        "SOCKET_RearGunnerCamera": (0.025, 0.0, EYE_Z),
        "SOCKET_Wrist_R": WRIST["R"],
        "SOCKET_Wrist_L": WRIST["L"],
        "SOCKET_RifleShoulder": (0.08, -0.155, 0.540),
        "SOCKET_IglaShoulder": (0.04, 0.155, 0.565),
        "SOCKET_WeaponSweepOrigin": (0.02, 0.0, 0.520),
    }
    for name, location in sockets.items():
        socket = add_socket(name, location, collection)
        socket["SKG_SocketContract"] = "character_refinement01_integration_datum"

    create_actions(rig)
    for obj in collection.all_objects:
        obj["SKG_AssetID"] = ASSET_ID
        obj["SKG_DimensionsClaim"] = "PROJECT_PROVISIONAL_NOT_A_MEASURED_PERCENTILE"


def set_lighting(mood: str) -> None:
    import bpy

    settings = {
        "daylight": ((0.060, 0.075, 0.095), 1650.0, 650.0, (1.0, 0.86, 0.70)),
        "overcast": ((0.045, 0.052, 0.060), 850.0, 720.0, (0.78, 0.86, 1.0)),
        "night": ((0.006, 0.010, 0.022), 300.0, 170.0, (0.44, 0.62, 1.0)),
        "wet": ((0.035, 0.045, 0.060), 1080.0, 540.0, (0.72, 0.82, 1.0)),
        "cockpit": ((0.010, 0.016, 0.020), 540.0, 250.0, (0.62, 1.0, 0.72)),
    }
    color, key_energy, fill_energy, key_color = settings[mood]
    bpy.context.scene.world.color = color
    key = bpy.data.objects.get("REVIEW_Key")
    fill = bpy.data.objects.get("REVIEW_Fill")
    if key:
        key.data.energy = key_energy
        key.data.color = key_color
    if fill:
        fill.data.energy = fill_energy
        fill.data.color = (0.55, 0.70, 1.0) if mood in {"night", "wet"} else (0.82, 0.90, 1.0)


def render_character_views(asset_collection: Any, output: Path) -> list[Path]:
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
    paths: list[Path] = []
    for view in load_json(CAMERAS)["views"]:
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
        raise CharacterError("No evaluated character mesh points were available.")
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
    from mathutils import Vector

    visible = [obj for obj in collection.all_objects if obj.type == "MESH" and not obj.hide_render and not obj.name.startswith("UCX_")]
    vertices = sum(len(obj.data.vertices) for obj in visible)
    triangles = sum(triangulated_count(obj) for obj in visible)
    manifold = [manifold_report(obj) for obj in visible]
    if vertices < MINIMUM_VISIBLE_VERTICES:
        raise CharacterError(f"Visible vertex count {vertices} is below {MINIMUM_VISIBLE_VERTICES}.")
    if triangles > VISIBLE_TRIANGLE_BUDGET:
        raise CharacterError(f"Visible triangle count {triangles} exceeds {VISIBLE_TRIANGLE_BUDGET}.")
    if any(record["nonmanifold_edges"] for record in manifold):
        raise CharacterError(f"Visible mesh has nonmanifold edges: {manifold}")
    if any("hand" in obj.name.lower() for obj in visible):
        raise CharacterError("Visible hand geometry is prohibited in the body export.")
    rig = next(obj for obj in collection.all_objects if obj.type == "ARMATURE")
    deform_bones = [bone.name for bone in rig.data.bones if bone.use_deform]
    if len(deform_bones) < 31:
        raise CharacterError(f"Rig has {len(deform_bones)} deform bones, below 31.")
    actions = sorted(action.name for action in bpy.data.actions)
    missing = sorted(set(REQUIRED_ACTIONS) - set(actions))
    if missing:
        raise CharacterError(f"Required actions are missing: {missing}")
    shoulder_elbow = (Vector(SHOULDER["R"]) - Vector(ELBOW["R"])).length
    elbow_wrist = (Vector(ELBOW["R"]) - Vector(WRIST["R"])).length
    payload = {
        "schema": "skyguard.phase2.reargunner-character-refinement01.geometry-rig-receipt.v1",
        "asset_id": ASSET_ID,
        "dimension_claim": "PROJECT_PROVISIONAL_NOT_A_MEASURED_PERCENTILE",
        "selected_seated_profile_m": {
            "sitting_height": HEAD_TOP_Z,
            "sitting_eye_height": EYE_Z,
            "shoulder_elbow": shoulder_elbow,
            "shoulder_breadth": SHOULDER_Y * 2.0,
            "hip_breadth": HIP_Y * 2.0,
            "lower_arm_to_wrist": elbow_wrist,
        },
        "visible_vertices": vertices,
        "visible_triangles": triangles,
        "manifold": manifold,
        "deform_bone_count": len(deform_bones),
        "actions": actions,
        "sockets": sorted(obj.name for obj in collection.all_objects if obj.type == "EMPTY" and obj.name.startswith("SOCKET_")),
        "exported_hand_mesh_count": 0,
        "materials": sorted({slot.material.name for obj in visible for slot in obj.material_slots if slot.material}),
    }
    write_json(output / "geometry_rig_receipt.json", payload)
    return payload


def create_pose_receipt(output: Path, collection: Any) -> dict[str, Any]:
    visible = [obj for obj in collection.all_objects if obj.type == "MESH" and not obj.hide_render and not obj.name.startswith("UCX_")]
    frames = {"seated_neutral": 1, "rifle_support": 20, "rifle_trigger_ads": 40, "igla_support": 60, "turbulence_brace": 80}
    bounds = {name: mesh_bounds_at_frame(visible, frame) for name, frame in frames.items()}
    for name, record in bounds.items():
        extents = [record["x_max"] - record["x_min"], record["y_max"] - record["y_min"], record["z_max"] - record["z_min"]]
        if min(extents) <= 0.08 or max(extents) >= 2.50:
            raise CharacterError(f"Pose bounds indicate collapse or runaway deformation: {name} {extents}")
    payload = {
        "schema": "skyguard.phase2.reargunner-character-refinement01.pose-deformation-receipt.v1",
        "asset_id": ASSET_ID,
        "frames": frames,
        "evaluated_bounds": bounds,
        "checks": {"finite_noncollapsed_bounds": True, "hands_are_separate": True, "weapon_contact_is_provisional": True, "cockpit_clearance_requires_unreal": True},
    }
    write_json(output / "pose_deformation_receipt.json", payload)
    return payload


def create_cockpit_datum_receipt(output: Path) -> dict[str, Any]:
    payload = {
        "schema": "skyguard.phase2.reargunner-character-refinement01.cockpit-clearance-datum-receipt.v1",
        "asset_id": ASSET_ID,
        "classification": "PASS_OFFLINE_DATUMS_ONLY_NOT_COCKPIT_CLEARANCE",
        "seat_datum": SEAT_DATUM,
        "eye_datum": (0.025, 0.0, EYE_Z),
        "wrist_datums": WRIST,
        "shoulder_datums": SHOULDER,
        "weapon_shoulders": {"rifle": (0.08, -0.155, 0.540), "igla": (0.04, 0.155, 0.565)},
        "remaining": ["accepted Yak-52 cockpit source", "accepted hands", "accepted rifle", "accepted Igla", "Unreal camera/pilot-safety/weapon-sweep validation"],
    }
    write_json(output / "cockpit_clearance_datum_receipt.json", payload)
    return payload


def main() -> int:
    args = sdk.parse_worker_args()
    if args.asset_id != ASSET_ID:
        raise CharacterError(f"Unexpected asset id: {args.asset_id}")
    source_records = verify_authorities()
    sdk.render_review_views = render_character_views
    sdk.export_asset = export_rigged_asset
    code = sdk.run_worker(ASSET_ID, build_asset, REQUIRED_SOCKETS)
    bpy = __import__("bpy")
    collection = bpy.data.collections["ASSET"]
    geometry = create_geometry_rig_receipt(Path(args.output), collection)
    poses = create_pose_receipt(Path(args.output), collection)
    datums = create_cockpit_datum_receipt(Path(args.output))
    source_parity = {
        "schema": "skyguard.phase2.reargunner-character-refinement01.source-parity-receipt.v1",
        "asset_id": ASSET_ID,
        "authorities": source_records,
        "webgame_geometry_imported": False,
        "provisional_geometry_imported": False,
        "metahuman_geometry_imported": False,
        "external_geometry_imported": False,
        "exported_hand_mesh_count": 0,
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
            "cockpit_datums": datums,
            "render_count": 12,
            "render_resolution": [2048, 2048],
            "coordinate_contract": {"forward": "+X", "right": "+Y", "up": "+Z", "units": "metres", "origin": "SOCKET_SeatDatum"},
        },
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
