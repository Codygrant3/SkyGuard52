from __future__ import annotations

import importlib.util
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
    add_cylinder,
    add_socket,
    add_torus,
    add_uv_sphere,
    pbr_material,
    render_fixed_views,
    sha256,
    write_production_receipt,
)


ASSET_ID = "core-yak52-cockpit"
SOURCE_GENERATOR = SCRIPTS / "blender_bld_m01_yak_prod_002.py"
SOURCE_BLEND = (
    PROJECT_ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "Mission01"
    / "Yak52_Production_002"
    / "BLD_M01_YAK_PROD_002_MASTER.blend"
)
SOURCE_CONTRACT = PROJECT_ROOT / "Docs" / "AAA_Review" / "BLD_M01_YAK_PROD_002_CONTRACT.json"
REQUIRED_SOCKETS = [
    "SOCKET_Origin",
    "SOCKET_PilotSeat",
    "SOCKET_RearGunnerSeat",
    "SOCKET_ADSEye",
    "SOCKET_CanopyRearTravel",
    "SOCKET_CameraRearGunner",
    "SOCKET_RifleGrip_R",
    "SOCKET_RifleGrip_L",
    "SOCKET_IglaGrip_R",
    "SOCKET_IglaGrip_L",
]


def load_generator():
    spec = importlib.util.spec_from_file_location("skyguard_yak_prod_002", SOURCE_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the governed Yak-52 production generator.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_gauge(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    collection,
    bezel,
    face,
    glass,
) -> None:
    tick = pbr_material("MAT_COCKPIT_InstrumentMarking", (0.82, 0.84, 0.78, 1.0), 0.0, 0.42)
    needle = pbr_material("MAT_COCKPIT_InstrumentNeedle", (0.76, 0.08, 0.035, 1.0), 0.0, 0.34)
    add_cylinder(
        f"{name}_Bezel",
        location,
        radius,
        0.022,
        collection,
        bezel,
        axis="X",
        vertices=48,
    )
    add_cylinder(
        f"{name}_Face",
        (location[0] + 0.013, location[1], location[2]),
        radius * 0.82,
        0.004,
        collection,
        face,
        axis="X",
        vertices=48,
        bevel=0.0,
    )
    face_x = location[0] + 0.019
    for index in range(12):
        angle = math.radians(index * 30.0)
        radial = radius * 0.60
        add_box(
            f"{name}_Tick_{index:02d}",
            (
                face_x,
                location[1] + math.sin(angle) * radial,
                location[2] + math.cos(angle) * radial,
            ),
            (0.003, radius * 0.065, radius * 0.20),
            collection,
            tick,
            rotation=(angle, 0.0, 0.0),
            bevel=0.001,
        )
    needle_angle = math.radians(-38.0 + (sum(ord(ch) for ch in name) % 58))
    needle_end = (
        face_x + 0.002,
        location[1] + math.sin(needle_angle) * radius * 0.52,
        location[2] + math.cos(needle_angle) * radius * 0.52,
    )
    add_curve(
        f"{name}_Needle",
        [(face_x + 0.002, location[1], location[2]), needle_end],
        radius * 0.022,
        collection,
        needle,
    )
    add_uv_sphere(
        f"{name}_NeedleHub",
        (face_x + 0.003, location[1], location[2]),
        (radius * 0.045, radius * 0.06, radius * 0.06),
        collection,
        metal if (metal := bezel) else bezel,
        segments=24,
        rings=12,
    )
    add_cylinder(
        f"{name}_Glass",
        (location[0] + 0.016, location[1], location[2]),
        radius * 0.78,
        0.002,
        collection,
        glass,
        axis="X",
        vertices=48,
        bevel=0.0,
    )


def add_front_station(collection, mats) -> None:
    green = mats["MAT002_CockpitGreen"]
    black = mats["MAT002_CockpitBlack"]
    metal = mats["MAT002_YakBareMetal"]
    vinyl = mats["MAT002_SeatVinyl"]
    harness = mats["MAT002_HarnessWebbing"]
    glass = mats["MAT002_InstrumentGlass"]
    add_box("GEO_COCKPIT_FloorFront", (0.73, 0.0, 0.55), (1.02, 0.78, 0.10), collection, green, bevel=0.035)
    for side, suffix in ((-1.0, "L"), (1.0, "R")):
        add_box(
            f"GEO_COCKPIT_SidewallFront_{suffix}",
            (0.72, side * 0.47, 0.92),
            (1.05, 0.10, 0.66),
            collection,
            green,
            bevel=0.035,
        )
        for index in range(5):
            add_box(
                f"GEO_COCKPIT_QuiltFront_{suffix}_{index:02d}",
                (0.50 + 0.16 * index, side * 0.525, 0.98 + 0.035 * (index % 2)),
                (0.14, 0.025, 0.29),
                collection,
                vinyl,
                rotation=(0.0, math.radians(4.0 * (-1) ** index), 0.0),
                bevel=0.028,
            )
    add_box("GEO_COCKPIT_InstrumentPanelFront", (1.14, 0.0, 1.18), (0.10, 0.78, 0.50), collection, black, bevel=0.055)
    add_box("GEO_COCKPIT_CoamingFront", (1.07, 0.0, 1.47), (0.30, 0.82, 0.10), collection, black, bevel=0.04)
    gauge_positions = [
        (-0.22, 1.31, 0.075),
        (0.00, 1.33, 0.085),
        (0.23, 1.30, 0.068),
        (-0.24, 1.11, 0.060),
        (0.00, 1.12, 0.074),
        (0.22, 1.10, 0.058),
    ]
    for index, (y, z, radius) in enumerate(gauge_positions):
        add_gauge(
            f"GEO_COCKPIT_FrontGauge_{index:02d}",
            (1.085, y, z),
            radius,
            collection,
            metal,
            black,
            glass,
        )
    add_box("GEO_COCKPIT_SeatPanFront", (0.42, 0.0, 0.73), (0.48, 0.46, 0.10), collection, metal, bevel=0.05)
    add_box(
        "GEO_COCKPIT_SeatBackFront",
        (0.18, 0.0, 1.02),
        (0.11, 0.46, 0.55),
        collection,
        metal,
        rotation=(0.0, math.radians(-8.0), 0.0),
        bevel=0.05,
    )
    add_box("GEO_COCKPIT_CushionFront", (0.44, 0.0, 0.81), (0.40, 0.40, 0.10), collection, vinyl, bevel=0.06)
    for index in range(4):
        add_curve(
            f"GEO_COCKPIT_CushionFrontSeam_{index:02d}",
            [(0.27 + 0.11 * index, -0.18, 0.865), (0.27 + 0.11 * index, 0.18, 0.865)],
            0.004,
            collection,
            harness,
        )
    for side, suffix in ((-1.0, "L"), (1.0, "R")):
        add_curve(
            f"GEO_COCKPIT_HarnessFront_{suffix}",
            [(0.14, side * 0.18, 1.28), (0.31, side * 0.12, 1.06), (0.43, side * 0.08, 0.84)],
            0.025,
            collection,
            harness,
        )
        add_box(
            f"GEO_COCKPIT_PedalFront_{suffix}",
            (0.98, side * 0.20, 0.65),
            (0.16, 0.10, 0.035),
            collection,
            metal,
            rotation=(0.0, math.radians(-12.0), 0.0),
            bevel=0.01,
        )
    add_cylinder("GEO_COCKPIT_ControlStickFront", (0.69, 0.0, 0.89), 0.028, 0.52, collection, black, axis="Z")
    add_uv_sphere("GEO_COCKPIT_ControlGripFront", (0.69, 0.0, 1.16), (0.05, 0.04, 0.085), collection, black)


def add_rear_details(collection, mats) -> None:
    green = mats["MAT002_CockpitGreen"]
    black = mats["MAT002_CockpitBlack"]
    metal = mats["MAT002_YakBareMetal"]
    vinyl = mats["MAT002_SeatVinyl"]
    glass = mats["MAT002_InstrumentGlass"]
    for side, suffix in ((-1.0, "L"), (1.0, "R")):
        for index in range(6):
            add_box(
                f"GEO_COCKPIT_QuiltRear_{suffix}_{index:02d}",
                (-1.26 + 0.16 * index, side * 0.525, 1.02 + 0.03 * (index % 2)),
                (0.14, 0.025, 0.31),
                collection,
                vinyl,
                rotation=(0.0, math.radians(4.0 * (-1) ** index), 0.0),
                bevel=0.028,
            )
        for index in range(9):
            add_cylinder(
                f"GEO_COCKPIT_RivetRail_{suffix}_{index:02d}",
                (-1.53 + 0.38 * index, side * 0.535, 1.34),
                0.009,
                0.008,
                collection,
                metal,
                axis="Y",
                vertices=20,
                bevel=0.0,
            )
    for index, (y, z, radius) in enumerate(
        [(-0.22, 1.27, 0.07), (0.0, 1.30, 0.085), (0.23, 1.26, 0.065), (-0.13, 1.09, 0.055), (0.14, 1.08, 0.052)]
    ):
        add_gauge(
            f"GEO_COCKPIT_RearGaugeDetail_{index:02d}",
            (-0.255, y, z),
            radius,
            collection,
            metal,
            black,
            glass,
        )
    for index in range(8):
        add_cylinder(
            f"GEO_COCKPIT_ToggleRear_{index:02d}",
            (-0.272, -0.31 + index * 0.09, 0.98 + 0.04 * (index % 2)),
            0.009,
            0.035,
            collection,
            metal,
            axis="X",
            vertices=20,
            bevel=0.001,
        )
    add_box("GEO_COCKPIT_RadioRear", (-0.44, 0.34, 1.02), (0.22, 0.16, 0.18), collection, black, bevel=0.018)
    add_box("GEO_COCKPIT_MapPocketRear", (-1.03, -0.51, 1.02), (0.35, 0.025, 0.24), collection, green, bevel=0.015)
    warning = pbr_material("MAT_COCKPIT_WarningPlacard", (0.62, 0.08, 0.035, 1.0), 0.0, 0.48)
    add_box("GEO_COCKPIT_WarningPlacardRear", (-0.277, 0.31, 1.37), (0.008, 0.15, 0.035), collection, warning, bevel=0.003)
    for index in range(3):
        add_box(
            f"GEO_COCKPIT_CircuitBreakerBankRear_{index:02d}",
            (-0.278, -0.34 + index * 0.07, 1.38),
            (0.010, 0.045, 0.035),
            collection,
            black,
            bevel=0.006,
        )
    for index in range(4):
        add_curve(
            f"GEO_COCKPIT_CushionRearSeam_{index:02d}",
            [(-1.27 + 0.11 * index, -0.17, 0.855), (-1.27 + 0.11 * index, 0.17, 0.855)],
            0.004,
            collection,
            mats["MAT002_HarnessWebbing"],
        )


def add_canopy_rig(collection) -> None:
    import bpy

    armature_data = bpy.data.armatures.new("RIG_CanopyRear_Data")
    armature = bpy.data.objects.new("RIG_CanopyRear", armature_data)
    collection.objects.link(armature)
    armature.show_in_front = True
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bone = armature.data.edit_bones.new("BONE_CanopyRearSlide")
    bone.head = (-1.53, 0.0, 1.34)
    bone.tail = (-1.23, 0.0, 1.34)
    bpy.ops.object.mode_set(mode="POSE")
    pose_bone = armature.pose.bones["BONE_CanopyRearSlide"]
    pose_bone.location = (0.0, 0.0, 0.0)
    pose_bone.keyframe_insert(data_path="location", frame=1)
    pose_bone.location = (-0.70, 0.0, 0.0)
    pose_bone.keyframe_insert(data_path="location", frame=30)
    bpy.ops.object.mode_set(mode="OBJECT")
    for name in ("GEO_PROD002_CanopyRearSlidingGlass", "GEO_PROD002_CanopyBowRear"):
        obj = bpy.data.objects.get(name)
        if obj is not None:
            matrix = obj.matrix_world.copy()
            obj.parent = armature
            obj.parent_type = "BONE"
            obj.parent_bone = "BONE_CanopyRearSlide"
            obj.matrix_world = matrix
    armature["SKG_RigRole"] = "rear_canopy_slide"
    armature["SKG_TravelMetres"] = 0.70


def build_asset(asset_collection) -> None:
    generator = load_generator()
    mats = generator.build_materials()
    generator.create_canopy(asset_collection, mats)
    generator.create_rear_cockpit(asset_collection, mats)
    generator.create_datums(asset_collection)
    add_socket("SOCKET_Origin", (0.0, 0.0, 0.0), asset_collection)
    add_front_station(asset_collection, mats)
    add_rear_details(asset_collection, mats)
    add_canopy_rig(asset_collection)
    collision = pbr_material("MAT_COCKPIT_Collision", (0.08, 0.12, 0.15, 1.0), 0.0, 0.95)
    add_collision_box("UCX_COCKPIT_Tub", (-0.12, 0.0, 0.82), (3.20, 0.88, 0.58), asset_collection, collision)
    add_collision_box("UCX_COCKPIT_PanelFront", (1.14, 0.0, 1.18), (0.12, 0.78, 0.50), asset_collection, collision)
    add_collision_box("UCX_COCKPIT_PanelRear", (-0.25, 0.0, 1.17), (0.12, 0.78, 0.48), asset_collection, collision)
    for obj in asset_collection.all_objects:
        obj["SKG_AssetID"] = ASSET_ID


VIEWS = [
    {"name": "exterior_left_closed", "camera": (0.1, -7.2, 2.8), "target": (-0.1, 0.0, 1.05), "lens": 64, "frame": 1},
    {"name": "exterior_right_closed", "camera": (0.1, 7.2, 2.8), "target": (-0.1, 0.0, 1.05), "lens": 64, "frame": 1},
    {"name": "exterior_rear_open", "camera": (-5.6, -4.7, 3.25), "target": (-0.55, 0.0, 1.08), "lens": 64, "frame": 30},
    {"name": "top_open", "camera": (-0.2, -0.3, 7.5), "target": (-0.2, 0.0, 0.88), "lens": 70, "frame": 30},
    {"name": "rear_gunner_forward", "camera": (-0.76, -1.18, 2.12), "target": (-0.02, 0.0, 1.18), "lens": 44, "frame": 30},
    {"name": "rear_station_left_detail", "camera": (-1.05, -2.65, 2.25), "target": (-0.12, 0.0, 1.16), "lens": 54, "frame": 30},
    {"name": "rear_station_right_detail", "camera": (-1.05, 2.65, 2.25), "target": (-0.12, 0.0, 1.16), "lens": 54, "frame": 30},
    {"name": "front_station", "camera": (0.30, -2.65, 2.35), "target": (1.05, 0.0, 1.18), "lens": 54, "frame": 1},
]


def main() -> int:
    args = sdk.parse_worker_args()
    sdk.render_review_views = lambda collection, output: render_fixed_views(sdk, collection, output, VIEWS)
    code = sdk.run_worker(ASSET_ID, build_asset, REQUIRED_SOCKETS)
    collection = __import__("bpy").data.collections["ASSET"]
    validations = {
        "render_count": 8,
        "canopy_rig": "RIG_CanopyRear/BONE_CanopyRearSlide",
        "canopy_closed_frame": 1,
        "canopy_open_frame": 30,
        "rear_canopy_travel_m": 0.70,
        "front_canopy_state": "closed_static",
        "rear_gunner_eye_m": [-0.88, 0.0, 1.52],
        "rear_cockpit_clear_width_m": 0.72,
        "coordinate_contract": {"forward": "+X", "right": "+Y", "up": "+Z", "units": "metres"},
    }
    sources = [
        {"path": str(SOURCE_BLEND), "bytes": SOURCE_BLEND.stat().st_size, "sha256": sha256(SOURCE_BLEND), "use": "reference-backed source candidate"},
        {"path": str(SOURCE_GENERATOR), "bytes": SOURCE_GENERATOR.stat().st_size, "sha256": sha256(SOURCE_GENERATOR), "use": "governed geometry helper lineage"},
        {"path": str(SOURCE_CONTRACT), "bytes": SOURCE_CONTRACT.stat().st_size, "sha256": sha256(SOURCE_CONTRACT), "use": "dimension and socket authority"},
    ]
    write_production_receipt(Path(args.output), ASSET_ID, collection, sources, validations)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
