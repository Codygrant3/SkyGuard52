from __future__ import annotations

import math
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = PROJECT_ROOT / "Scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "Workers"))

import skyguard_blender_worker_sdk as sdk  # noqa: E402
from skyguard_worker_geometry import (  # noqa: E402
    add_box,
    add_collision_box,
    add_curve,
    add_cylinder_between,
    add_socket,
    add_uv_sphere,
    pbr_material,
    render_fixed_views,
    sha256,
    write_production_receipt,
)


ASSET_ID = "core-hand-forearm"
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
    / "PROVISIONAL_REAR_GUNNER_HAND_FOREARM_MANNEQUIN.glb"
)
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


def create_rig(collection):
    import bpy

    data = bpy.data.armatures.new("RIG_RearGunnerHands_Data")
    rig = bpy.data.objects.new("RIG_RearGunnerHands", data)
    collection.objects.link(rig)
    rig.show_in_front = True
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for side, y in (("R", -0.13), ("L", 0.13)):
        specs = [
            (f"Forearm.{side}", (-0.36, y, 0.0), (-0.11, y, 0.0), None),
            (f"Wrist.{side}", (-0.11, y, 0.0), (-0.04, y, 0.0), f"Forearm.{side}"),
            (f"Palm.{side}", (-0.04, y, 0.0), (0.11, y, 0.0), f"Wrist.{side}"),
        ]
        for finger in ("Thumb", "Index", "Middle", "Ring", "Little"):
            specs.append((f"{finger}1.{side}", (0.07, y, 0.0), (0.13, y, -0.015), f"Palm.{side}"))
            specs.append((f"{finger}2.{side}", (0.13, y, -0.015), (0.16, y, -0.045), f"{finger}1.{side}"))
        for name, head, tail, parent in specs:
            bone = data.edit_bones.new(name)
            bone.head = head
            bone.tail = tail
            if parent:
                bone.parent = data.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    rig["SKG_RigRole"] = "rear_gunner_first_person_hands"
    rig["SKG_DimensionsAreProjectProvisional"] = True
    return rig


def skin_to_bone(obj, rig, bone_name: str) -> None:
    group = obj.vertex_groups.new(name=bone_name)
    group.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    modifier = obj.modifiers.new(name="ARMATURE_Deform", type="ARMATURE")
    modifier.object = rig
    obj.parent = rig


def add_finger(
    prefix: str,
    side: str,
    y: float,
    z: float,
    length: float,
    radius: float,
    spread: float,
    collection,
    leather,
    rig,
) -> None:
    sign = -1.0 if side == "R" else 1.0
    start = (0.055, y + sign * spread, z)
    middle = (0.105, y + sign * (spread + 0.004), z - 0.040)
    end = (0.082 + length * 0.06, y + sign * (spread + 0.002), z - 0.094)
    first = add_cylinder_between(
        f"GEO_Glove_{prefix}1_{side}",
        start,
        middle,
        radius,
        collection,
        leather,
        vertices=32,
        bevel=0.002,
    )
    second = add_cylinder_between(
        f"GEO_Glove_{prefix}2_{side}",
        middle,
        end,
        radius * 0.90,
        collection,
        leather,
        vertices=32,
        bevel=0.002,
    )
    base_joint = add_uv_sphere(
        f"GEO_Glove_{prefix}BaseJoint_{side}",
        start,
        (radius * 1.04, radius * 1.12, radius * 0.88),
        collection,
        leather,
        segments=32,
        rings=16,
    )
    middle_joint = add_uv_sphere(
        f"GEO_Glove_{prefix}MiddleJoint_{side}",
        middle,
        (radius * 0.98, radius * 1.02, radius * 0.86),
        collection,
        leather,
        segments=32,
        rings=16,
    )
    tip = add_uv_sphere(
        f"GEO_Glove_{prefix}Tip_{side}",
        end,
        (radius * 0.94, radius * 0.94, radius * 1.10),
        collection,
        leather,
        segments=32,
        rings=16,
    )
    skin_to_bone(first, rig, f"{prefix}1.{side}")
    skin_to_bone(second, rig, f"{prefix}2.{side}")
    skin_to_bone(base_joint, rig, f"{prefix}1.{side}")
    skin_to_bone(middle_joint, rig, f"{prefix}2.{side}")
    skin_to_bone(tip, rig, f"{prefix}2.{side}")


def build_hand(side: str, y: float, collection, materials, rig) -> None:
    leather = materials["leather"]
    patch = materials["patch"]
    stitch = materials["stitch"]
    cloth = materials["cloth"]
    sign = -1.0 if side == "R" else 1.0
    sleeve = add_cylinder_between(
        f"GEO_Sleeve_{side}",
        (-0.36, y, 0.0),
        (-0.12, y, 0.0),
        0.052,
        collection,
        cloth,
        vertices=48,
        bevel=0.004,
    )
    cuff = add_box(
        f"GEO_Glove_Cuff_{side}",
        (-0.095, y, 0.0),
        (0.085, 0.112, 0.086),
        collection,
        leather,
        bevel=0.025,
    )
    palm = add_box(
        f"GEO_Glove_Palm_{side}",
        (-0.005, y, -0.002),
        (0.145, 0.092, 0.055),
        collection,
        leather,
        bevel=0.026,
    )
    dorsum = add_box(
        f"GEO_Glove_KnucklePad_{side}",
        (0.025, y, 0.031),
        (0.095, 0.078, 0.014),
        collection,
        patch,
        bevel=0.008,
    )
    for index, offset in enumerate((0.028, 0.010, -0.009, -0.027)):
        knuckle = add_uv_sphere(
            f"GEO_Glove_Knuckle_{index:02d}_{side}",
            (0.061, y + sign * offset, 0.026),
            (0.020, 0.015, 0.010),
            collection,
            patch,
            segments=32,
            rings=16,
        )
        skin_to_bone(knuckle, rig, f"Palm.{side}")
    for obj, bone in (
        (sleeve, f"Forearm.{side}"),
        (cuff, f"Wrist.{side}"),
        (palm, f"Palm.{side}"),
        (dorsum, f"Palm.{side}"),
    ):
        skin_to_bone(obj, rig, bone)
    finger_specs = [
        ("Index", 0.028, 0.078, 0.012, 0.031),
        ("Middle", 0.010, 0.085, 0.013, 0.013),
        ("Ring", -0.009, 0.078, 0.012, -0.006),
        ("Little", -0.027, 0.068, 0.011, -0.025),
    ]
    for name, z, length, radius, spread in finger_specs:
        add_finger(name, side, y, z, length, radius, spread, collection, leather, rig)
    thumb_start = (-0.005, y + sign * 0.045, -0.005)
    thumb_mid = (0.045, y + sign * 0.070, -0.018)
    thumb_end = (0.080, y + sign * 0.060, -0.045)
    thumb1 = add_cylinder_between(
        f"GEO_Glove_Thumb1_{side}",
        thumb_start,
        thumb_mid,
        0.015,
        collection,
        leather,
        vertices=32,
    )
    thumb2 = add_cylinder_between(
        f"GEO_Glove_Thumb2_{side}",
        thumb_mid,
        thumb_end,
        0.013,
        collection,
        leather,
        vertices=32,
    )
    thumb_web = add_uv_sphere(
        f"GEO_Glove_ThumbWeb_{side}",
        (0.008, y + sign * 0.044, -0.008),
        (0.035, 0.025, 0.025),
        collection,
        leather,
        segments=40,
        rings=20,
    )
    thumb_tip = add_uv_sphere(
        f"GEO_Glove_ThumbTip_{side}",
        thumb_end,
        (0.014, 0.014, 0.017),
        collection,
        leather,
        segments=32,
        rings=16,
    )
    skin_to_bone(thumb1, rig, f"Thumb1.{side}")
    skin_to_bone(thumb2, rig, f"Thumb2.{side}")
    skin_to_bone(thumb_web, rig, f"Palm.{side}")
    skin_to_bone(thumb_tip, rig, f"Thumb2.{side}")
    add_curve(
        f"GEO_Glove_PalmSeam_{side}",
        [(-0.07, y + sign * 0.046, -0.018), (-0.005, y + sign * 0.048, -0.026), (0.06, y + sign * 0.041, -0.020)],
        0.0015,
        collection,
        stitch,
    )
    add_curve(
        f"GEO_Glove_CuffStitch_{side}",
        [(-0.13, y + sign * 0.050, 0.025), (-0.09, y + sign * 0.054, 0.030), (-0.05, y + sign * 0.050, 0.025)],
        0.0013,
        collection,
        stitch,
    )


def build_asset(collection) -> None:
    leather = pbr_material("MAT_Glove_Leather", (0.035, 0.025, 0.019, 1.0), 0.0, 0.48, micro_scale=85.0, micro_strength=0.22)
    patch = pbr_material("MAT_Glove_Reinforcement", (0.055, 0.045, 0.035, 1.0), 0.0, 0.60, micro_scale=70.0, micro_strength=0.18)
    stitch = pbr_material("MAT_Glove_Stitch", (0.20, 0.16, 0.10, 1.0), 0.0, 0.72)
    cloth = pbr_material("MAT_Sleeve_Cloth", (0.12, 0.17, 0.13, 1.0), 0.0, 0.82, micro_scale=120.0, micro_strength=0.24)
    collision = pbr_material("MAT_Hand_Collision", (0.08, 0.10, 0.12, 1.0), 0.0, 0.95)
    materials = {"leather": leather, "patch": patch, "stitch": stitch, "cloth": cloth}
    rig = create_rig(collection)
    build_hand("R", -0.13, collection, materials, rig)
    build_hand("L", 0.13, collection, materials, rig)
    add_socket("SOCKET_Origin", (0.0, 0.0, 0.0), collection)
    add_socket("SOCKET_Wrist_R", (-0.11, -0.13, 0.0), collection)
    add_socket("SOCKET_Wrist_L", (-0.11, 0.13, 0.0), collection)
    add_socket("SOCKET_Rifle_FiringHand", (0.02, -0.13, -0.015), collection)
    add_socket("SOCKET_Rifle_SupportHand", (0.02, 0.13, -0.015), collection)
    add_socket("SOCKET_Igla_FiringHand", (0.02, -0.13, 0.025), collection)
    add_socket("SOCKET_Igla_SupportHand", (0.02, 0.13, 0.025), collection)
    add_socket("SOCKET_ADS_HandAlignment", (-0.02, 0.0, 0.10), collection)
    add_collision_box("UCX_HandForearm_R", (-0.10, -0.13, 0.0), (0.52, 0.11, 0.09), collection, collision)
    add_collision_box("UCX_HandForearm_L", (-0.10, 0.13, 0.0), (0.52, 0.11, 0.09), collection, collision)
    for obj in collection.all_objects:
        obj["SKG_AssetID"] = ASSET_ID
        obj["SKG_DimensionsClaim"] = "project_provisional_not_measured_percentile"


VIEWS = [
    {"name": "hero_dorsal", "camera": (0.62, -0.92, 0.52), "target": (-0.08, 0.0, 0.0), "lens": 58},
    {"name": "hero_palmar", "camera": (0.58, 0.90, -0.46), "target": (-0.06, 0.0, -0.01), "lens": 58},
    {"name": "right_hand_detail", "camera": (0.44, -0.72, 0.25), "target": (0.00, -0.13, 0.0), "lens": 66},
    {"name": "left_hand_detail", "camera": (0.44, 0.72, 0.25), "target": (0.00, 0.13, 0.0), "lens": 66},
    {"name": "first_person_rifle_grip", "camera": (-0.72, 0.0, 0.25), "target": (0.16, 0.0, -0.01), "lens": 55},
    {"name": "first_person_ads_clearance", "camera": (-0.62, 0.0, 0.18), "target": (0.18, 0.0, 0.02), "lens": 62},
    {"name": "cuff_sleeve_transition", "camera": (-0.34, -0.72, 0.29), "target": (-0.18, -0.06, 0.0), "lens": 66},
    {"name": "topology_silhouette", "camera": (0.10, -0.05, 0.92), "target": (-0.08, 0.0, 0.0), "lens": 58},
]


def render_hand_views(collection, output):
    import bpy

    bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"
    bpy.context.scene.view_settings.exposure = -4.65
    return render_fixed_views(sdk, collection, output, VIEWS)


def main() -> int:
    args = sdk.parse_worker_args()
    sdk.render_review_views = render_hand_views
    code = sdk.run_worker(ASSET_ID, build_asset, REQUIRED_SOCKETS)
    bpy = __import__("bpy")
    collection = bpy.data.collections["ASSET"]
    validations = {
        "render_count": 8,
        "selected_hand_length_m": 0.19,
        "selected_hand_breadth_m": 0.085,
        "selected_forearm_plus_hand_m": 0.46,
        "dimension_claim": "project blockout only; not a measured percentile",
        "rig": "RIG_RearGunnerHands",
        "weighted_mesh_count": sum(
            1 for obj in collection.all_objects if obj.type == "MESH" and obj.vertex_groups
        ),
        "pose_contract": ["rifle_firing", "rifle_support", "igla_firing", "igla_support", "ads_clearance"],
        "coordinate_contract": {"forward": "+X", "right": "+Y", "up": "+Z", "units": "metres"},
    }
    sources = [
        {"path": str(SOURCE_RECEIPT), "bytes": SOURCE_RECEIPT.stat().st_size, "sha256": sha256(SOURCE_RECEIPT), "use": "accepted provisional dimensions"},
        {"path": str(SOURCE_GLB), "bytes": SOURCE_GLB.stat().st_size, "sha256": sha256(SOURCE_GLB), "use": "silhouette evidence only; geometry not imported"},
    ]
    write_production_receipt(Path(args.output), ASSET_ID, collection, sources, validations)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
