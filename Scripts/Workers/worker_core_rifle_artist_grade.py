from __future__ import annotations

import hashlib
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


ASSET_ID = "core-rifle"
IDENTITY = "generic AR/M4-family rifle; exact configuration unresolved"
OUTPUT: Path
ASSET: Any
HIGH_POLY: Any
MATERIALS: dict[str, Any] = {}
GAME_PARTS: list[Any] = []
HIGH_DETAIL: list[Any] = []

SOURCE_RECEIPT = (
    PROJECT_ROOT
    / "Blender"
    / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01"
    / "dimension_and_artifact_receipt.json"
)
SOURCE_GLB = (
    PROJECT_ROOT
    / "Blender"
    / "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01"
    / "exports"
    / "PROVISIONAL_AR_M4_FAMILY_RIFLE_BLOCKOUT.glb"
)
IDENTITY_DECISION = (
    PROJECT_ROOT
    / "References"
    / "CombatAssets"
    / "TechnicalIntake_Cycle02"
    / "reports"
    / "GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_RIFLE_IDENTITY_DECISION.json"
)
FEATURE_COMPARISON = (
    PROJECT_ROOT
    / "References"
    / "CombatAssets"
    / "TechnicalIntake_Cycle02"
    / "reports"
    / "GATE7_COMBAT_ASSET_REFERENCE_RESOLUTION_CYCLE02_RIFLE_FEATURE_COMPARISON.json"
)
RAIL_ACCEPTANCE = (
    PROJECT_ROOT
    / "Docs"
    / "AAA_Review"
    / "GATE7_COMBAT_ASSET_REFINEMENT_CYCLE03_RAIL_COUPON_ATTEMPT01_TERMINAL_FREEZE.json"
)
REFERENCE_CROPS = [
    PROJECT_ROOT
    / "References"
    / "CombatAssets"
    / "TechnicalIntake_Cycle02"
    / "rifle_crops"
    / name
    for name in (
        "frame_0000_0000.000s_rifle_crop.png",
        "frame_0435_0014.500s_rifle_crop.png",
        "frame_0450_0015.000s_rifle_crop.png",
        "frame_0510_0017.000s_rifle_crop.png",
        "frame_0675_0022.500s_rifle_crop.png",
    )
]

REQUIRED_SOCKETS = [
    "SOCKET_Origin",
    "SOCKET_Muzzle",
    "SOCKET_Ejection",
    "SOCKET_Magazine",
    "SOCKET_FiringHand",
    "SOCKET_SupportHand",
    "SOCKET_ADS_Eye",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def finish_mesh(
    obj: Any,
    collection: Any,
    material: Any,
    *,
    bevel: float = 0.0,
    bevel_segments: int = 3,
    apply_bevel: bool = True,
    game_part: bool = True,
) -> Any:
    import bpy

    link_only(obj, collection)
    activate(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if material is not None:
        obj.data.materials.append(material)
    if bevel > 0.0:
        modifier = obj.modifiers.new("BEVEL_SurfaceControl", "BEVEL")
        modifier.width = bevel
        modifier.segments = bevel_segments
        modifier.limit_method = "ANGLE"
        modifier.angle_limit = math.radians(22.0)
        if apply_bevel:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj["SKG_AssetID"] = ASSET_ID
    obj["SKG_Identity"] = IDENTITY
    obj["SKG_SurfaceRole"] = "game_renderable" if game_part else "high_poly_detail"
    if game_part:
        GAME_PARTS.append(obj)
    else:
        HIGH_DETAIL.append(obj)
    return obj


def rounded_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: Any,
    *,
    bevel: float = 0.003,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    collection: Any | None = None,
    game_part: bool = True,
) -> Any:
    import bpy

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    return finish_mesh(
        obj,
        collection or ASSET,
        material,
        bevel=bevel,
        bevel_segments=4,
        game_part=game_part,
    )


def cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: Any,
    *,
    axis: str = "X",
    vertices: int = 48,
    bevel: float = 0.001,
    collection: Any | None = None,
    game_part: bool = True,
) -> Any:
    import bpy

    rotation = {
        "X": (0.0, math.pi / 2.0, 0.0),
        "Y": (math.pi / 2.0, 0.0, 0.0),
        "Z": (0.0, 0.0, 0.0),
    }[axis]
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    return finish_mesh(
        obj,
        collection or ASSET,
        material,
        bevel=bevel,
        bevel_segments=3,
        game_part=game_part,
    )


def torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    material: Any,
    *,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    collection: Any | None = None,
    game_part: bool = True,
) -> Any:
    import bpy

    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=48,
        minor_segments=12,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    return finish_mesh(
        obj,
        collection or ASSET,
        material,
        game_part=game_part,
    )


def curve_tube(
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    material: Any,
    *,
    collection: Any | None = None,
    game_part: bool = True,
) -> Any:
    import bpy

    curve_data = bpy.data.curves.new(f"{name}_Curve", "CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 16
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 4
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points):
        point.co = coordinate
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve_data)
    (collection or ASSET).objects.link(obj)
    curve_data.materials.append(material)
    activate(obj)
    bpy.ops.object.convert(target="MESH")
    return finish_mesh(
        obj,
        collection or ASSET,
        None,
        game_part=game_part,
    )


def extrude_profile(
    name: str,
    profile_xz: list[tuple[float, float]],
    width: float,
    material: Any,
    *,
    bevel: float = 0.003,
    collection: Any | None = None,
    game_part: bool = True,
) -> Any:
    import bpy

    vertices = [(x, -width / 2.0, z) for x, z in profile_xz]
    vertices += [(x, width / 2.0, z) for x, z in profile_xz]
    count = len(profile_xz)
    faces: list[tuple[int, ...]] = []
    faces.append(tuple(range(count)))
    faces.append(tuple(range(count, count * 2))[::-1])
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    (collection or ASSET).objects.link(obj)
    return finish_mesh(
        obj,
        collection or ASSET,
        material,
        bevel=bevel,
        bevel_segments=4,
        game_part=game_part,
    )


def rounded_rect_loop(
    width: float,
    height: float,
    radius: float,
    segments: int = 4,
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for cy, cz, start in (
        (width / 2.0 - radius, height / 2.0 - radius, 0.0),
        (-width / 2.0 + radius, height / 2.0 - radius, math.pi / 2.0),
        (-width / 2.0 + radius, -height / 2.0 + radius, math.pi),
        (width / 2.0 - radius, -height / 2.0 + radius, math.pi * 1.5),
    ):
        for step in range(segments + 1):
            angle = start + step * (math.pi / 2.0) / segments
            points.append((cy + math.cos(angle) * radius, cz + math.sin(angle) * radius))
    return points


def loft_sections(
    name: str,
    sections: list[tuple[float, float, float, float, float]],
    material: Any,
    *,
    bevel: float = 0.0015,
    collection: Any | None = None,
    game_part: bool = True,
) -> Any:
    import bpy

    loops: list[list[tuple[float, float, float]]] = []
    for x, width, height, radius, z_offset in sections:
        loops.append([(x, y, z + z_offset) for y, z in rounded_rect_loop(width, height, radius)])
    ring = len(loops[0])
    vertices = [vertex for loop in loops for vertex in loop]
    faces: list[tuple[int, ...]] = []
    faces.append(tuple(range(ring))[::-1])
    last = (len(loops) - 1) * ring
    faces.append(tuple(range(last, last + ring)))
    for section_index in range(len(loops) - 1):
        base = section_index * ring
        nxt_base = (section_index + 1) * ring
        for index in range(ring):
            nxt = (index + 1) % ring
            faces.append((base + index, base + nxt, nxt_base + nxt, nxt_base + index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    (collection or ASSET).objects.link(obj)
    return finish_mesh(
        obj,
        collection or ASSET,
        material,
        bevel=bevel,
        bevel_segments=3,
        game_part=game_part,
    )


def handguard_shell(
    name: str,
    x0: float,
    x1: float,
    outer_y: float,
    outer_z: float,
    thickness: float,
    material: Any,
    center_z: float = 0.071,
) -> Any:
    import bpy

    segments = 16
    outer = [
        (
            math.sin(index * math.tau / segments) * outer_y,
            math.cos(index * math.tau / segments) * outer_z,
        )
        for index in range(segments)
    ]
    inner = [
        (
            math.sin(index * math.tau / segments) * (outer_y - thickness),
            math.cos(index * math.tau / segments) * (outer_z - thickness),
        )
        for index in range(segments)
    ]
    vertices: list[tuple[float, float, float]] = []
    for x in (x0, x1):
        vertices.extend((x, y, z + center_z) for y, z in outer)
        vertices.extend((x, y, z + center_z) for y, z in inner)
    faces: list[tuple[int, ...]] = []
    outer0 = 0
    inner0 = segments
    outer1 = segments * 2
    inner1 = segments * 3
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.append((outer0 + index, outer1 + index, outer1 + nxt, outer0 + nxt))
        faces.append((inner0 + index, inner0 + nxt, inner1 + nxt, inner1 + index))
        faces.append((outer0 + index, outer0 + nxt, inner0 + nxt, inner0 + index))
        faces.append((outer1 + index, inner1 + index, inner1 + nxt, outer1 + nxt))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    ASSET.objects.link(obj)
    finish_mesh(obj, ASSET, material, bevel=0.0016, bevel_segments=3)

    cutter_collection = bpy.data.collections.new("TEMP_BOOLEAN_CUTTERS")
    bpy.context.scene.collection.children.link(cutter_collection)
    for index, x in enumerate([0.105, 0.145, 0.185, 0.225, 0.265, 0.305]):
        cutter = rounded_box(
            f"CUTTER_Vent_{index:02d}",
            (x, 0.0, center_z - 0.003),
            (0.025, outer_y * 3.0, 0.026),
            None,
            bevel=0.008,
            collection=cutter_collection,
            game_part=False,
        )
        modifier = obj.modifiers.new(f"BOOLEAN_Vent_{index:02d}", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        activate(obj)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
        if cutter in HIGH_DETAIL:
            HIGH_DETAIL.remove(cutter)
    bpy.data.collections.remove(cutter_collection)
    return obj


def make_material(
    name: str,
    base_color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    micro_scale: float,
    micro_strength: float,
) -> Any:
    import bpy

    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = base_color
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = base_color
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"{name}_MicroSurface"
    noise.inputs["Scale"].default_value = micro_scale
    noise.inputs["Detail"].default_value = 7.0
    noise.inputs["Roughness"].default_value = 0.58
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = micro_strength
    bump.inputs["Distance"].default_value = 0.00035
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def create_materials() -> None:
    MATERIALS.update(
        {
            "anodized": make_material(
                "MAT_Rifle_BlackAnodized",
                (0.022, 0.026, 0.030, 1.0),
                0.78,
                0.29,
                175.0,
                0.16,
            ),
            "steel": make_material(
                "MAT_Rifle_CoatedSteel",
                (0.046, 0.052, 0.057, 1.0),
                0.90,
                0.23,
                210.0,
                0.10,
            ),
            "tan": make_material(
                "MAT_Rifle_TanCoatedAluminum",
                (0.27, 0.20, 0.105, 1.0),
                0.67,
                0.35,
                150.0,
                0.18,
            ),
            "polymer": make_material(
                "MAT_Rifle_BlackPolymer",
                (0.024, 0.027, 0.026, 1.0),
                0.0,
                0.50,
                120.0,
                0.27,
            ),
            "rubber": make_material(
                "MAT_Rifle_Rubber",
                (0.018, 0.020, 0.019, 1.0),
                0.0,
                0.71,
                155.0,
                0.35,
            ),
            "wear": make_material(
                "MAT_Rifle_RestrainedEdgeWear",
                (0.135, 0.145, 0.15, 1.0),
                0.75,
                0.31,
                220.0,
                0.06,
            ),
            "collision": make_material(
                "MAT_Rifle_CollisionHidden",
                (0.1, 0.2, 0.3, 1.0),
                0.0,
                1.0,
                1.0,
                0.0,
            ),
        }
    )


def rail_tooth(name: str, x: float, z: float, width_y: float, material: Any) -> Any:
    profile = [
        (x - 0.0031, z - 0.0040),
        (x - 0.0040, z - 0.0010),
        (x - 0.0031, z + 0.0040),
        (x + 0.0031, z + 0.0040),
        (x + 0.0040, z - 0.0010),
        (x + 0.0031, z - 0.0040),
    ]
    return extrude_profile(name, profile, width_y, material, bevel=0.00055)


def create_major_geometry() -> None:
    # Major surfaces are custom section lofts and side-profile extrusions rather
    # than scaled primitive slabs.
    loft_sections(
        "GEO_Rifle_UpperReceiver",
        [
            (-0.145, 0.046, 0.058, 0.007, 0.072),
            (-0.120, 0.052, 0.064, 0.008, 0.073),
            (0.055, 0.052, 0.064, 0.008, 0.073),
            (0.085, 0.046, 0.056, 0.007, 0.072),
        ],
        MATERIALS["anodized"],
        bevel=0.0015,
    )
    extrude_profile(
        "GEO_Rifle_LowerReceiver",
        [
            (-0.135, 0.066),
            (-0.105, 0.021),
            (-0.045, 0.006),
            (0.050, 0.012),
            (0.075, 0.045),
            (0.072, 0.080),
            (-0.128, 0.080),
        ],
        0.050,
        MATERIALS["anodized"],
        bevel=0.0035,
    )
    # Sculpted magazine well transition.
    loft_sections(
        "GEO_Rifle_MagazineWell",
        [
            (-0.020, 0.047, 0.060, 0.006, -0.002),
            (0.025, 0.051, 0.070, 0.007, -0.010),
            (0.060, 0.055, 0.080, 0.008, -0.018),
        ],
        MATERIALS["anodized"],
        bevel=0.002,
    )
    handguard_shell(
        "GEO_Rifle_FreeFloatHandguard",
        0.075,
        0.335,
        0.038,
        0.043,
        0.004,
        MATERIALS["tan"],
    )

    # Curved, tapered magazine with a mechanically readable insertion neck.
    extrude_profile(
        "GEO_Rifle_CurvedMagazine",
        [
            (-0.006, 0.004),
            (0.052, 0.003),
            (0.060, -0.055),
            (0.075, -0.112),
            (0.098, -0.184),
            (0.094, -0.220),
            (0.050, -0.230),
            (0.026, -0.200),
            (0.005, -0.140),
            (-0.008, -0.065),
        ],
        0.044,
        MATERIALS["polymer"],
        bevel=0.0055,
    )
    rounded_box(
        "GEO_Rifle_MagazineInsertionNeck",
        (0.026, 0.0, -0.005),
        (0.052, 0.046, 0.054),
        MATERIALS["steel"],
        bevel=0.0025,
    )

    # Ergonomic grip: sloped custom profile with separate tactile panels.
    extrude_profile(
        "GEO_Rifle_PistolGrip",
        [
            (-0.125, 0.010),
            (-0.078, 0.004),
            (-0.080, -0.047),
            (-0.095, -0.106),
            (-0.120, -0.147),
            (-0.160, -0.145),
            (-0.172, -0.118),
            (-0.153, -0.050),
        ],
        0.052,
        MATERIALS["polymer"],
        bevel=0.0075,
    )
    for side, y in (("L", 0.027), ("R", -0.027)):
        extrude_profile(
            f"GEO_Rifle_GripPanel_{side}",
            [
                (-0.151, -0.047),
                (-0.098, -0.050),
                (-0.103, -0.120),
                (-0.132, -0.137),
                (-0.162, -0.112),
            ],
            0.0025,
            MATERIALS["rubber"],
            bevel=0.0012,
        ).location.y = y

    # Skeletal stock silhouette with curved cheek, support struts and rubber pad.
    cylinder(
        "GEO_Rifle_BufferTube",
        (-0.235, 0.0, 0.070),
        0.017,
        0.235,
        MATERIALS["steel"],
        vertices=64,
    )
    loft_sections(
        "GEO_Rifle_StockCheek",
        [
            (-0.180, 0.051, 0.031, 0.010, 0.101),
            (-0.285, 0.058, 0.038, 0.012, 0.102),
            (-0.355, 0.063, 0.042, 0.013, 0.094),
        ],
        MATERIALS["polymer"],
        bevel=0.002,
    )
    for side, y in (("L", 0.023), ("R", -0.023)):
        curve_tube(
            f"GEO_Rifle_StockLowerStrut_{side}",
            [
                (-0.175, y, 0.060),
                (-0.265, y, 0.010),
                (-0.355, y, -0.055),
            ],
            0.007,
            MATERIALS["polymer"],
        )
    extrude_profile(
        "GEO_Rifle_StockButtBody",
        [
            (-0.372, 0.112),
            (-0.345, 0.096),
            (-0.343, 0.040),
            (-0.365, -0.078),
            (-0.398, -0.071),
            (-0.406, 0.080),
        ],
        0.068,
        MATERIALS["polymer"],
        bevel=0.008,
    )
    extrude_profile(
        "GEO_Rifle_ButtPad",
        [
            (-0.402, 0.092),
            (-0.394, 0.075),
            (-0.390, -0.065),
            (-0.405, -0.074),
            (-0.414, -0.062),
            (-0.418, 0.074),
        ],
        0.071,
        MATERIALS["rubber"],
        bevel=0.004,
    )

    # External barrel and pronged muzzle silhouette; no internal mechanism.
    cylinder(
        "GEO_Rifle_Barrel",
        (0.405, 0.0, 0.071),
        0.009,
        0.155,
        MATERIALS["steel"],
        vertices=64,
    )
    cylinder(
        "GEO_Rifle_MuzzleCollar",
        (0.498, 0.0, 0.071),
        0.0135,
        0.045,
        MATERIALS["steel"],
        vertices=64,
    )
    for index, angle in enumerate((0.0, math.pi / 2.0, math.pi, math.pi * 1.5)):
        y = math.cos(angle) * 0.009
        z = 0.071 + math.sin(angle) * 0.009
        rounded_box(
            f"GEO_Rifle_MuzzleProng_{index:02d}",
            (0.535, y, z),
            (0.056, 0.0065, 0.0065),
            MATERIALS["steel"],
            bevel=0.0018,
            rotation=(angle, 0.0, 0.0),
        )


def create_surface_detail() -> None:
    # Proper coupon-scaled rail rhythm: 10.008 mm pitch and restrained teeth.
    pitch = 0.010008
    receiver_start = -0.132
    for index in range(20):
        rail_tooth(
            f"GEO_Rifle_ReceiverRailTooth_{index:02d}",
            receiver_start + index * pitch,
            0.122,
            0.021209,
            MATERIALS["anodized"],
        )
    handguard_start = 0.078
    for index in range(27):
        rail_tooth(
            f"GEO_Rifle_HandguardRailTooth_{index:02d}",
            handguard_start + index * pitch,
            0.122,
            0.021209,
            MATERIALS["tan"],
        )

    # Ejection-side panels, cover, charging handle and identity-neutral controls.
    rounded_box(
        "GEO_Rifle_EjectionPortRecess",
        (-0.015, -0.0272, 0.079),
        (0.082, 0.003, 0.027),
        MATERIALS["steel"],
        bevel=0.0018,
    )
    extrude_profile(
        "GEO_Rifle_DustCover",
        [
            (-0.060, 0.094),
            (0.034, 0.094),
            (0.036, 0.068),
            (-0.057, 0.067),
        ],
        0.0022,
        MATERIALS["anodized"],
        bevel=0.0013,
    ).location.y = -0.0295
    rounded_box(
        "GEO_Rifle_ChargingHandle",
        (-0.135, 0.0, 0.108),
        (0.030, 0.062, 0.013),
        MATERIALS["steel"],
        bevel=0.003,
    )
    cylinder(
        "GEO_Rifle_ForwardAssist",
        (-0.085, -0.034, 0.071),
        0.009,
        0.017,
        MATERIALS["steel"],
        axis="Y",
        vertices=36,
    )
    cylinder(
        "GEO_Rifle_MagazineRelease",
        (0.030, -0.0295, 0.032),
        0.008,
        0.006,
        MATERIALS["steel"],
        axis="Y",
        vertices=32,
    )
    cylinder(
        "GEO_Rifle_SelectorHub",
        (-0.102, 0.029, 0.037),
        0.0085,
        0.006,
        MATERIALS["steel"],
        axis="Y",
        vertices=32,
    )
    rounded_box(
        "GEO_Rifle_SelectorLever",
        (-0.085, 0.033, 0.040),
        (0.034, 0.005, 0.009),
        MATERIALS["steel"],
        bevel=0.002,
        rotation=(0.0, math.radians(-18.0), 0.0),
    )
    extrude_profile(
        "GEO_Rifle_BoltCatch",
        [
            (-0.054, 0.060),
            (-0.030, 0.064),
            (-0.027, 0.038),
            (-0.048, 0.034),
        ],
        0.006,
        MATERIALS["steel"],
        bevel=0.0015,
    ).location.y = 0.029
    curve_tube(
        "GEO_Rifle_TriggerGuard",
        [
            (-0.090, 0.0, 0.010),
            (-0.055, 0.0, -0.021),
            (-0.015, 0.0, 0.004),
        ],
        0.0032,
        MATERIALS["anodized"],
    )
    curve_tube(
        "GEO_Rifle_Trigger",
        [
            (-0.058, 0.0, 0.018),
            (-0.050, 0.0, -0.004),
            (-0.041, 0.0, -0.012),
        ],
        0.0022,
        MATERIALS["steel"],
    )
    for index, x in enumerate((0.083, 0.327)):
        for side, y in (("L", 0.039), ("R", -0.039)):
            cylinder(
                f"GEO_Rifle_HandguardFastener_{index}_{side}",
                (x, y, 0.066),
                0.005,
                0.004,
                MATERIALS["steel"],
                axis="Y",
                vertices=24,
            )
    for index in range(6):
        x = 0.020 + index * 0.013
        curve_tube(
            f"GEO_Rifle_MagazineRib_{index:02d}",
            [
                (x, -0.0223, -0.040),
                (x + 0.012, -0.0223, -0.120),
                (x + 0.035, -0.0223, -0.205),
            ],
            0.0014,
            MATERIALS["wear"],
        )

    # Aperture and post stay on a single governed sight axis.
    sight_z = 0.162
    rounded_box(
        "GEO_Rifle_RearSightBase",
        (-0.105, 0.0, 0.136),
        (0.038, 0.030, 0.015),
        MATERIALS["steel"],
        bevel=0.004,
    )
    for side, y in (("L", 0.013), ("R", -0.013)):
        extrude_profile(
            f"GEO_Rifle_RearSightEar_{side}",
            [
                (-0.119, 0.138),
                (-0.094, 0.138),
                (-0.092, 0.170),
                (-0.116, 0.174),
            ],
            0.006,
            MATERIALS["steel"],
            bevel=0.0025,
        ).location.y = y
    torus(
        "GEO_Rifle_RearAperture",
        (-0.099, 0.0, sight_z),
        0.0045,
        0.0012,
        MATERIALS["steel"],
        rotation=(0.0, math.pi / 2.0, 0.0),
    )
    rounded_box(
        "GEO_Rifle_FrontSightBase",
        (0.315, 0.0, 0.132),
        (0.033, 0.029, 0.014),
        MATERIALS["tan"],
        bevel=0.0035,
    )
    for side, y in (("L", 0.012), ("R", -0.012)):
        extrude_profile(
            f"GEO_Rifle_FrontSightEar_{side}",
            [
                (0.302, 0.136),
                (0.330, 0.136),
                (0.326, 0.171),
                (0.306, 0.171),
            ],
            0.006,
            MATERIALS["steel"],
            bevel=0.0023,
        ).location.y = y
    rounded_box(
        "GEO_Rifle_FrontSightPost",
        (0.316, 0.0, 0.157),
        (0.006, 0.006, 0.026),
        MATERIALS["steel"],
        bevel=0.0012,
    )

    # Restrained edge accents and external takedown-pin silhouettes.
    for name, x in (("Front", 0.057), ("Rear", -0.108)):
        cylinder(
            f"GEO_Rifle_TakedownPin_{name}",
            (x, 0.0285, 0.043),
            0.0065,
            0.004,
            MATERIALS["wear"],
            axis="Y",
            vertices=28,
        )
    for side, y in (("L", 0.031), ("R", -0.031)):
        curve_tube(
            f"GEO_Rifle_StockSlingLoop_{side}",
            [
                (-0.345, y, -0.020),
                (-0.365, y * 1.45, -0.042),
                (-0.382, y, -0.018),
            ],
            0.0027,
            MATERIALS["steel"],
        )


def join_game_source() -> Any:
    import bpy

    bpy.ops.object.select_all(action="DESELECT")
    for obj in GAME_PARTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = GAME_PARTS[0]
    bpy.ops.object.join()
    game = bpy.context.object
    game.name = "GEO_Rifle_GameNaniteSource"
    for polygon in game.data.polygons:
        polygon.use_smooth = True

    activate(game)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(58.0),
        island_margin=0.012,
        area_weight=0.25,
        correct_aspect=True,
        scale_to_bounds=True,
    )
    bpy.ops.object.mode_set(mode="OBJECT")
    game.data.uv_layers.active.name = "UV0"
    uv1 = game.data.uv_layers.new(name="UV1_Bake")
    uv1.data.foreach_set(
        "uv",
        [
            component
            for loop in game.data.uv_layers["UV0"].data
            for component in loop.uv
        ],
    )
    game.data.uv_layers.active = game.data.uv_layers["UV0"]
    game["SKG_HighToLowTarget"] = True
    game["SKG_NaniteSuitableSource"] = True
    return game


def create_high_poly(game: Any) -> list[Any]:
    import bpy

    high = game.copy()
    high.data = game.data.copy()
    high.name = "HP_Rifle_MasterSurface"
    HIGH_POLY.objects.link(high)
    high["SKG_SurfaceRole"] = "high_poly_master"
    high["SKG_HighToLowSource"] = True
    high.hide_render = False
    bevel = high.modifiers.new("HP_MicroBevel", "BEVEL")
    bevel.width = 0.00065
    bevel.segments = 3
    bevel.limit_method = "ANGLE"
    activate(high)
    bpy.ops.object.modifier_apply(modifier=bevel.name)

    # High-only surface details survive as normal/AO information.
    for side, y in (("L", 0.0265), ("R", -0.0265)):
        for row in range(5):
            for column in range(5):
                cylinder(
                    f"HP_GripStipple_{side}_{row}_{column}",
                    (-0.145 + column * 0.010, y, -0.060 - row * 0.014),
                    0.00125,
                    0.0010,
                    MATERIALS["rubber"],
                    axis="Y",
                    vertices=16,
                    bevel=0.0003,
                    collection=HIGH_POLY,
                    game_part=False,
                )
    for index, x in enumerate((-0.100, -0.065, -0.030, 0.005, 0.040)):
        cylinder(
            f"HP_ReceiverFastener_{index:02d}",
            (x, -0.029, 0.057),
            0.0022,
            0.0012,
            MATERIALS["steel"],
            axis="Y",
            vertices=20,
            bevel=0.0003,
            collection=HIGH_POLY,
            game_part=False,
        )
    for index in range(7):
        curve_tube(
            f"HP_ButtPadGroove_{index:02d}",
            [
                (-0.413, -0.033, 0.070 - index * 0.020),
                (-0.416, 0.0, 0.070 - index * 0.020),
                (-0.413, 0.033, 0.070 - index * 0.020),
            ],
            0.0010,
            MATERIALS["rubber"],
            collection=HIGH_POLY,
            game_part=False,
        )
    return [high, *HIGH_DETAIL]


def assign_bake_target(game: Any, image: Any, label: str) -> None:
    for material in game.data.materials:
        if material is None:
            continue
        material.use_nodes = True
        nodes = material.node_tree.nodes
        node = nodes.get(f"BAKE_TARGET_{label}") or nodes.new("ShaderNodeTexImage")
        node.name = f"BAKE_TARGET_{label}"
        node.label = f"High-to-low {label} bake"
        node.image = image
        nodes.active = node
        node.select = True


def bake_selected(
    game: Any,
    high_objects: list[Any],
    name: str,
    bake_type: str,
    *,
    colorspace: str = "Non-Color",
) -> Path:
    import bpy

    image = bpy.data.images.new(
        f"T_Rifle_{name}",
        width=2048,
        height=2048,
        alpha=False,
        float_buffer=False,
    )
    image.colorspace_settings.name = colorspace
    image.generated_color = (0.5, 0.5, 1.0, 1.0) if name == "Normal" else (0.5, 0.5, 0.5, 1.0)
    assign_bake_target(game, image, name)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in high_objects:
        obj.hide_render = False
        obj.hide_set(False)
        obj.select_set(True)
    game.select_set(True)
    bpy.context.view_layer.objects.active = game
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.render.bake.use_selected_to_active = True
    scene.render.bake.cage_extrusion = 0.0025
    scene.render.bake.max_ray_distance = 0.012
    scene.render.bake.margin = 24
    bpy.ops.object.bake(type=bake_type)
    path = OUTPUT / "bakes" / f"T_Rifle_{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()
    return path


def emission_material(name: str, mode: str, color: tuple[float, float, float, float] | None = None) -> Any:
    import bpy

    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    if mode == "color":
        emission.inputs["Color"].default_value = color or (0.5, 0.5, 0.5, 1.0)
    elif mode == "curvature":
        geometry = nodes.new("ShaderNodeNewGeometry")
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.25
        ramp.color_ramp.elements[1].position = 0.75
        links.new(geometry.outputs["Pointiness"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], emission.inputs["Color"])
    elif mode == "thickness":
        ambient = nodes.new("ShaderNodeAmbientOcclusion")
        ambient.inputs["Distance"].default_value = 0.035
        invert = nodes.new("ShaderNodeMath")
        invert.operation = "SUBTRACT"
        invert.inputs[0].default_value = 1.0
        links.new(ambient.outputs["AO"], invert.inputs[1])
        links.new(invert.outputs[0], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def override_materials(objects: Iterable[Any], replacement_map: dict[str, Any], fallback: Any) -> dict[str, list[Any]]:
    originals: dict[str, list[Any]] = {}
    for obj in objects:
        if obj.type != "MESH":
            continue
        originals[obj.name] = [slot.material for slot in obj.material_slots]
        if not obj.material_slots:
            obj.data.materials.append(fallback)
        for slot in obj.material_slots:
            original_name = slot.material.name if slot.material else ""
            slot.material = replacement_map.get(original_name, fallback)
    return originals


def restore_materials(objects: Iterable[Any], originals: dict[str, list[Any]]) -> None:
    for obj in objects:
        if obj.name not in originals:
            continue
        values = originals[obj.name]
        while len(obj.data.materials) > len(values):
            obj.data.materials.pop(index=len(obj.data.materials) - 1)
        for index, material in enumerate(values):
            if index < len(obj.material_slots):
                obj.material_slots[index].material = material


def bake_emission_pass(
    game: Any,
    high_objects: list[Any],
    name: str,
    mode: str,
) -> Path:
    import bpy

    image = bpy.data.images.new(f"T_Rifle_{name}", width=2048, height=2048, alpha=False)
    image.colorspace_settings.name = "Non-Color"
    assign_bake_target(game, image, name)

    if mode == "material_id":
        palette = [
            (0.85, 0.12, 0.08, 1.0),
            (0.10, 0.55, 0.95, 1.0),
            (0.95, 0.65, 0.08, 1.0),
            (0.25, 0.85, 0.32, 1.0),
            (0.70, 0.20, 0.88, 1.0),
            (0.10, 0.85, 0.80, 1.0),
        ]
        replacements = {
            material.name: emission_material(f"BAKE_ID_{index:02d}", "color", palette[index % len(palette)])
            for index, material in enumerate(MATERIALS.values())
        }
        fallback = emission_material("BAKE_ID_Fallback", "color", (0.5, 0.5, 0.5, 1.0))
    else:
        fallback = emission_material(f"BAKE_{name}", mode)
        replacements = {}
    originals = override_materials(high_objects, replacements, fallback)
    try:
        bpy.ops.object.select_all(action="DESELECT")
        for obj in high_objects:
            obj.select_set(True)
        game.select_set(True)
        bpy.context.view_layer.objects.active = game
        scene = bpy.context.scene
        scene.render.engine = "CYCLES"
        scene.cycles.samples = 16
        scene.cycles.use_denoising = False
        scene.render.bake.use_selected_to_active = True
        scene.render.bake.cage_extrusion = 0.0025
        scene.render.bake.max_ray_distance = 0.012
        scene.render.bake.margin = 24
        bpy.ops.object.bake(type="EMIT")
    finally:
        restore_materials(high_objects, originals)
    path = OUTPUT / "bakes" / f"T_Rifle_{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.filepath_raw = str(path)
    image.file_format = "PNG"
    image.save()
    return path


def attach_normal_map(game: Any) -> None:
    import bpy

    image = bpy.data.images.get("T_Rifle_Normal")
    for material in game.data.materials:
        if material is None:
            continue
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        principled = nodes.get("Principled BSDF")
        tex = nodes.get("T_Rifle_Normal_Runtime") or nodes.new("ShaderNodeTexImage")
        tex.name = "T_Rifle_Normal_Runtime"
        tex.image = image
        tex.interpolation = "Linear"
        normal = nodes.get("Rifle_BakedNormal") or nodes.new("ShaderNodeNormalMap")
        normal.name = "Rifle_BakedNormal"
        normal.inputs["Strength"].default_value = 0.78
        links.new(tex.outputs["Color"], normal.inputs["Color"])
        links.new(normal.outputs["Normal"], principled.inputs["Normal"])


def create_bakes(game: Any, high_objects: list[Any]) -> list[Path]:
    # Blender 5.2 exposes baking through the stable object operator while the
    # review renderer remains Eevee. These maps are generated from the separate
    # HP collection into the packed UV0 game source.
    paths = [
        bake_selected(game, high_objects, "Normal", "NORMAL"),
        bake_selected(game, high_objects, "AO", "AO"),
        bake_emission_pass(game, high_objects, "Curvature", "curvature"),
        bake_emission_pass(game, high_objects, "Thickness", "thickness"),
        bake_emission_pass(game, high_objects, "MaterialID", "material_id"),
    ]
    attach_normal_map(game)
    for obj in high_objects:
        obj.hide_render = True
        obj.hide_set(True)
    return paths


def add_socket(name: str, location: tuple[float, float, float]) -> Any:
    import bpy

    socket = bpy.data.objects.new(name, None)
    socket.empty_display_type = "PLAIN_AXES"
    socket.empty_display_size = 0.025
    socket.location = location
    socket["SKG_AssetID"] = ASSET_ID
    ASSET.objects.link(socket)
    return socket


def add_collision(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Any:
    obj = rounded_box(
        name,
        location,
        dimensions,
        MATERIALS["collision"],
        bevel=0.001,
        rotation=rotation,
    )
    obj.hide_render = True
    obj["SKG_Collision"] = True
    return obj


def create_game_contract() -> None:
    add_socket("SOCKET_Origin", (0.0, 0.0, 0.0))
    add_socket("SOCKET_Muzzle", (0.565, 0.0, 0.071))
    add_socket("SOCKET_Ejection", (-0.015, -0.031, 0.079))
    add_socket("SOCKET_Magazine", (0.030, 0.0, -0.015))
    add_socket("SOCKET_FiringHand", (-0.125, 0.0, -0.075))
    add_socket("SOCKET_SupportHand", (0.220, 0.0, 0.015))
    add_socket("SOCKET_ADS_Eye", (-0.485, 0.0, 0.162))
    add_collision("UCX_Rifle_Receiver", (-0.025, 0.0, 0.045), (0.255, 0.060, 0.145))
    add_collision("UCX_Rifle_Handguard", (0.205, 0.0, 0.071), (0.278, 0.082, 0.092))
    add_collision("UCX_Rifle_Barrel", (0.425, 0.0, 0.071), (0.180, 0.035, 0.035))
    add_collision("UCX_Rifle_Stock", (-0.300, 0.0, 0.030), (0.245, 0.078, 0.190))
    add_collision(
        "UCX_Rifle_Grip",
        (-0.126, 0.0, -0.074),
        (0.070, 0.060, 0.155),
        rotation=(0.0, math.radians(-12.0), 0.0),
    )
    add_collision(
        "UCX_Rifle_Magazine",
        (0.055, 0.0, -0.110),
        (0.080, 0.052, 0.225),
        rotation=(0.0, math.radians(-7.0), 0.0),
    )


def object_stats(obj: Any) -> dict[str, Any]:
    if obj.type != "MESH":
        return {"name": obj.name, "type": obj.type}
    obj.data.calc_loop_triangles()
    return {
        "name": obj.name,
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
        "triangles": len(obj.data.loop_triangles),
        "uv_layers": [layer.name for layer in obj.data.uv_layers],
        "materials": [slot.material.name for slot in obj.material_slots if slot.material],
        "modifiers": [modifier.type for modifier in obj.modifiers],
    }


def create_receipts(game: Any, high_objects: list[Any], bake_paths: list[Path]) -> None:
    source_paths = [SOURCE_RECEIPT, SOURCE_GLB, IDENTITY_DECISION, FEATURE_COMPARISON, RAIL_ACCEPTANCE, *REFERENCE_CROPS]
    source_register = {
        "schema": "skyguard.artist-grade-source-register.v1",
        "asset_id": ASSET_ID,
        "identity": IDENTITY,
        "authoritative_boundary": {
            "family": "AR/M4-pattern",
            "visible_supported_features": [
                "continuous top rail",
                "long free-float ventilated handguard",
                "pronged muzzle silhouette",
                "rear aperture-like silhouette",
            ],
            "unresolved": [
                "manufacturer",
                "model",
                "chambering",
                "receiver-control configuration",
                "magazine and stock configuration",
                "exact sights",
                "exact muzzle device",
                "markings",
                "accessories",
            ],
            "use": "external game-art surfaces only; no functional internal mechanism",
        },
        "sources": [
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in source_paths
        ],
    }
    write_json(OUTPUT / "source_reference_register.json", source_register)

    topology = {
        "schema": "skyguard.artist-grade-topology-inventory.v1",
        "asset_id": ASSET_ID,
        "game_nanite_source": object_stats(game),
        "high_poly": [object_stats(obj) for obj in high_objects],
        "high_poly_collection": HIGH_POLY.name,
        "game_collection": ASSET.name,
        "derivation": "game source assembled from custom loft/profile/boolean/bevel surfaces; HP master adds micro-bevel and detail geometry",
    }
    write_json(OUTPUT / "topology_inventory.json", topology)

    uv_material = {
        "schema": "skyguard.artist-grade-uv-material-inventory.v1",
        "asset_id": ASSET_ID,
        "uv_layers": [layer.name for layer in game.data.uv_layers],
        "uv_policy": "packed non-overlapping UV0 with duplicate UV1_Bake",
        "materials": [
            {
                "name": material.name,
                "uses_nodes": material.use_nodes,
                "surface_family": key,
            }
            for key, material in MATERIALS.items()
            if key != "collision"
        ],
        "pbr_calibration": "metallic/roughness workflow with restrained procedural micro-normal and baked high-poly normal",
    }
    write_json(OUTPUT / "uv_material_inventory.json", uv_material)

    bake_inventory = {
        "schema": "skyguard.artist-grade-bake-inventory.v1",
        "asset_id": ASSET_ID,
        "resolution": [2048, 2048],
        "source": HIGH_POLY.name,
        "target": game.name,
        "maps": [
            {
                "type": path.stem.removeprefix("T_Rifle_"),
                "path": str(path.relative_to(OUTPUT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in bake_paths
        ],
    }
    write_json(OUTPUT / "bake_inventory.json", bake_inventory)

    sight = {
        "schema": "skyguard.rifle-sight-alignment.v2",
        "asset_id": ASSET_ID,
        "rear_aperture": [-0.099, 0.0, 0.162],
        "front_post": [0.316, 0.0, 0.162],
        "ads_eye": [-0.485, 0.0, 0.162],
        "axis": {"direction": "+X", "y_m": 0.0, "z_m": 0.162},
        "status": "aligned_and_unobstructed_by_design",
    }
    write_json(OUTPUT / "sight_alignment_receipt.json", sight)

    game_contract = {
        "schema": "skyguard.rifle-game-contract.v2",
        "asset_id": ASSET_ID,
        "units": "metres",
        "forward_axis": "+X",
        "right_axis": "+Y",
        "up_axis": "+Z",
        "origin_m": [0.0, 0.0, 0.0],
        "sockets": {
            obj.name: list(obj.location)
            for obj in ASSET.all_objects
            if obj.type == "EMPTY" and obj.name.startswith("SOCKET_")
        },
        "collision": [obj.name for obj in ASSET.all_objects if obj.name.startswith("UCX_")],
        "glb_contents": "game/Nanite source, sockets, and UCX collision only; HP retained in governed blend",
    }
    write_json(OUTPUT / "pivot_axis_socket_collision_receipt.json", game_contract)


def build_asset(collection: Any) -> None:
    global ASSET, HIGH_POLY
    import bpy

    ASSET = collection
    HIGH_POLY = bpy.data.collections.new("HIGH_POLY")
    bpy.context.scene.collection.children.link(HIGH_POLY)
    create_materials()
    create_major_geometry()
    create_surface_detail()
    game = join_game_source()
    high_objects = create_high_poly(game)
    bake_paths = create_bakes(game, high_objects)
    create_game_contract()
    create_receipts(game, high_objects, bake_paths)


VIEWS = [
    {"name": "hero_left", "camera": (0.08, -2.05, 0.50), "target": (0.04, 0.0, 0.005), "lens": 60},
    {"name": "hero_right", "camera": (0.08, 2.05, 0.50), "target": (0.04, 0.0, 0.005), "lens": 60},
    {"name": "side_profile_left", "camera": (0.04, -2.18, 0.13), "target": (0.04, 0.0, -0.005), "lens": 62},
    {"name": "top_mechanical", "camera": (0.02, -0.02, 1.92), "target": (0.02, 0.0, 0.015), "lens": 60},
    {"name": "muzzle_front", "camera": (1.30, -0.66, 0.38), "target": (0.20, 0.0, 0.045), "lens": 64},
    {"name": "stock_rear", "camera": (-1.23, 0.62, 0.38), "target": (-0.02, 0.0, 0.020), "lens": 64},
    {"name": "first_person_hip", "camera": (-0.78, -0.36, 0.39), "target": (0.38, 0.0, 0.060), "lens": 54},
    {"name": "first_person_ads", "camera": (-0.485, 0.0, 0.162), "target": (0.48, 0.0, 0.162), "lens": 72},
]


def add_review_stage() -> tuple[Any, Any]:
    import bpy
    from mathutils import Vector

    review = bpy.data.collections.new("REVIEW_ONLY")
    bpy.context.scene.collection.children.link(review)
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0.0, 0.0, -0.25))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    link_only(ground, review)
    ground.data.materials.append(
        sdk.pbr_material("MAT_REVIEW_GroundArtist", (0.055, 0.065, 0.080, 1.0), 0.0, 0.72)
    )
    for name, kind, location, energy, size, color in (
        ("REVIEW_Key", "AREA", (0.35, -1.00, 1.15), 260.0, 1.45, (1.0, 0.86, 0.70)),
        ("REVIEW_Fill", "AREA", (-0.45, 0.85, 0.65), 115.0, 1.25, (0.68, 0.82, 1.0)),
        ("REVIEW_Rim", "AREA", (0.55, 0.75, 1.25), 190.0, 1.05, (0.90, 0.94, 1.0)),
    ):
        bpy.ops.object.light_add(type=kind, location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        light.rotation_euler = (Vector((0.02, 0.0, 0.02)) - light.location).to_track_quat("-Z", "Y").to_euler()
        link_only(light, review)
    camera_data = bpy.data.cameras.new("REVIEW_CameraArtist")
    camera = bpy.data.objects.new("REVIEW_CameraArtist", camera_data)
    review.objects.link(camera)
    bpy.context.scene.camera = camera
    return review, camera


def render_review_views(_collection: Any, output: Path) -> list[Path]:
    import bpy
    from mathutils import Vector

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -1.05
    if scene.world:
        scene.world.use_nodes = True
        background = scene.world.node_tree.nodes.get("Background")
        background.inputs["Color"].default_value = (0.018, 0.025, 0.040, 1.0)
        background.inputs["Strength"].default_value = 0.12
    _review, camera = add_review_stage()
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for view in VIEWS:
        camera.location = Vector(view["camera"])
        target = Vector(view["target"])
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.lens = float(view["lens"])
        camera.data.dof.use_dof = False
        path = render_dir / f"{view['name']}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def main() -> int:
    global OUTPUT

    args = sdk.parse_worker_args()
    OUTPUT = Path(args.output)
    sdk.render_review_views = render_review_views
    code = sdk.run_worker(ASSET_ID, build_asset, REQUIRED_SOCKETS)
    collection = __import__("bpy").data.collections["ASSET"]
    validation = sdk.validate_asset(collection, REQUIRED_SOCKETS)
    validation.update(
        {
            "identity": IDENTITY,
            "prohibited_claims": [
                "manufacturer",
                "model",
                "chambering",
                "serial number",
                "trademark",
                "unit marking",
                "optic",
                "unsupported accessory",
                "internal mechanism",
            ],
            "render_count": 8,
            "render_resolution": [2560, 1440],
            "high_poly_collection": "HIGH_POLY",
            "game_nanite_source": "GEO_Rifle_GameNaniteSource",
            "bake_types": ["Normal", "AO", "Curvature", "Thickness", "MaterialID"],
            "coordinate_contract": {
                "units": "metres",
                "forward": "+X",
                "right": "+Y",
                "up": "+Z",
            },
            "method": "custom hard-surface loft/profile/boolean/bevel construction with separate HP source, packed UVs, and high-to-low bakes",
        }
    )
    sources = [
        {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in [SOURCE_RECEIPT, SOURCE_GLB, IDENTITY_DECISION, FEATURE_COMPARISON, RAIL_ACCEPTANCE, *REFERENCE_CROPS]
    ]
    from skyguard_worker_geometry import write_production_receipt  # noqa: E402

    write_production_receipt(OUTPUT, ASSET_ID, collection, sources, validation)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
