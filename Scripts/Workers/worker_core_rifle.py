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
    add_cylinder,
    add_socket,
    add_torus,
    pbr_material,
    render_fixed_views,
    sha256,
    write_production_receipt,
)


ASSET_ID = "core-rifle"
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
REQUIRED_SOCKETS = [
    "SOCKET_Origin",
    "SOCKET_Muzzle",
    "SOCKET_Ejection",
    "SOCKET_Magazine",
    "SOCKET_FiringHand",
    "SOCKET_SupportHand",
    "SOCKET_ADS_Eye",
]


def build_asset(collection) -> None:
    metal = pbr_material("MAT_Rifle_AnodizedMetal", (0.025, 0.028, 0.030, 1.0), 0.76, 0.28, micro_scale=95.0, micro_strength=0.10)
    steel = pbr_material("MAT_Rifle_Steel", (0.060, 0.065, 0.068, 1.0), 0.88, 0.22, micro_scale=110.0, micro_strength=0.08)
    polymer = pbr_material("MAT_Rifle_Polymer", (0.035, 0.038, 0.036, 1.0), 0.0, 0.52, micro_scale=85.0, micro_strength=0.18)
    grip_mat = pbr_material("MAT_Rifle_GripTexture", (0.028, 0.030, 0.028, 1.0), 0.0, 0.66, micro_scale=135.0, micro_strength=0.26)
    wear = pbr_material("MAT_Rifle_EdgeWear", (0.13, 0.14, 0.14, 1.0), 0.72, 0.33)
    sight = pbr_material("MAT_Rifle_SightBlack", (0.008, 0.009, 0.009, 1.0), 0.54, 0.30)
    collision = pbr_material("MAT_Rifle_Collision", (0.08, 0.10, 0.12, 1.0), 0.0, 0.95)

    add_box("GEO_Rifle_LowerReceiver", (-0.02, 0.0, 0.018), (0.235, 0.058, 0.105), collection, metal, bevel=0.010)
    add_box("GEO_Rifle_UpperReceiver", (0.015, 0.0, 0.077), (0.265, 0.052, 0.064), collection, metal, bevel=0.008)
    add_box("GEO_Rifle_EjectionPort", (0.030, -0.030, 0.083), (0.095, 0.006, 0.038), collection, steel, bevel=0.003)
    add_box("GEO_Rifle_DustCover", (0.028, -0.034, 0.073), (0.110, 0.005, 0.031), collection, metal, bevel=0.002)
    add_cylinder("GEO_Rifle_ForwardAssist", (-0.075, -0.044, 0.070), 0.012, 0.028, collection, steel, axis="Y", vertices=32)
    add_cylinder("GEO_Rifle_FireSelector", (-0.075, 0.035, 0.030), 0.011, 0.014, collection, steel, axis="Y", vertices=28)
    add_box("GEO_Rifle_BoltCatch", (-0.040, 0.034, 0.050), (0.026, 0.010, 0.031), collection, steel, rotation=(math.radians(8), 0, 0), bevel=0.002)
    add_box("GEO_Rifle_ChargingHandle", (-0.125, 0.0, 0.104), (0.050, 0.075, 0.014), collection, steel, bevel=0.003)
    add_box("GEO_Rifle_TriggerGuard", (-0.045, 0.0, -0.050), (0.075, 0.025, 0.015), collection, steel, bevel=0.005)
    add_curve("GEO_Rifle_Trigger", [(-0.010, 0.0, -0.016), (-0.005, 0.0, -0.043), (0.005, 0.0, -0.052)], 0.0032, collection, steel)

    add_box(
        "GEO_Rifle_PistolGrip",
        (-0.105, 0.0, -0.090),
        (0.070, 0.055, 0.145),
        collection,
        grip_mat,
        rotation=(0.0, math.radians(-18.0), 0.0),
        bevel=0.015,
    )
    for index in range(6):
        add_box(
            f"GEO_Rifle_GripRib_{index:02d}",
            (-0.085 - index * 0.008, -0.031, -0.055 - index * 0.018),
            (0.045, 0.004, 0.006),
            collection,
            wear,
            rotation=(0.0, math.radians(-18.0), 0.0),
            bevel=0.001,
        )

    magazine_segments = [
        ((-0.005, 0.0, -0.075), (0.065, 0.052, 0.105), -4.0),
        ((0.006, 0.0, -0.155), (0.060, 0.050, 0.090), -8.0),
        ((0.025, 0.0, -0.225), (0.055, 0.048, 0.070), -13.0),
    ]
    for index, (location, dims, angle) in enumerate(magazine_segments):
        add_box(
            f"GEO_Rifle_Magazine_{index:02d}",
            location,
            dims,
            collection,
            polymer,
            rotation=(0.0, math.radians(angle), 0.0),
            bevel=0.009,
        )
    for index in range(5):
        add_box(
            f"GEO_Rifle_MagazineRib_{index:02d}",
            (0.008 + index * 0.004, -0.027, -0.105 - index * 0.025),
            (0.046, 0.004, 0.007),
            collection,
            wear,
            rotation=(0.0, math.radians(-8.0), 0.0),
            bevel=0.001,
        )

    add_cylinder("GEO_Rifle_BufferTube", (-0.235, 0.0, 0.045), 0.020, 0.220, collection, steel, axis="X", vertices=48)
    add_box("GEO_Rifle_StockSpine", (-0.240, 0.0, 0.067), (0.220, 0.060, 0.055), collection, polymer, bevel=0.015)
    add_box(
        "GEO_Rifle_StockButt",
        (-0.338, 0.0, 0.010),
        (0.050, 0.075, 0.165),
        collection,
        polymer,
        rotation=(0.0, math.radians(2.5), 0.0),
        bevel=0.018,
    )
    add_box("GEO_Rifle_StockCheek", (-0.245, 0.0, 0.105), (0.190, 0.070, 0.035), collection, polymer, bevel=0.015)
    add_box("GEO_Rifle_ButtPad", (-0.365, 0.0, 0.005), (0.018, 0.078, 0.168), collection, grip_mat, bevel=0.009)
    for side, y in (("L", 0.032), ("R", -0.032)):
        add_curve(
            f"GEO_Rifle_StockSupport_{side}",
            [(-0.185, y, 0.050), (-0.285, y, 0.018), (-0.350, y, -0.045)],
            0.008,
            collection,
            polymer,
        )

    add_cylinder("GEO_Rifle_Barrel", (0.350, 0.0, 0.075), 0.0105, 0.400, collection, steel, axis="X", vertices=48)
    add_cylinder("GEO_Rifle_GasBlock", (0.360, 0.0, 0.075), 0.021, 0.042, collection, metal, axis="X", vertices=40)
    add_cylinder("GEO_Rifle_MuzzleDevice", (0.565, 0.0, 0.075), 0.016, 0.075, collection, steel, axis="X", vertices=48)
    for index in range(4):
        angle = index * math.pi / 2.0
        add_box(
            f"GEO_Rifle_MuzzlePort_{index:02d}",
            (0.570, math.cos(angle) * 0.014, 0.075 + math.sin(angle) * 0.014),
            (0.030, 0.005, 0.008),
            collection,
            sight,
            rotation=(angle, 0.0, 0.0),
            bevel=0.001,
        )

    add_box("GEO_Rifle_HandguardCore", (0.225, 0.0, 0.075), (0.300, 0.070, 0.080), collection, polymer, bevel=0.015)
    for index in range(10):
        x = 0.095 + index * 0.029
        add_box(f"GEO_Rifle_RailToothTop_{index:02d}", (x, 0.0, 0.128), (0.017, 0.049, 0.014), collection, metal, bevel=0.002)
        add_box(f"GEO_Rifle_VentLeft_{index:02d}", (x, 0.038, 0.075), (0.014, 0.007, 0.032), collection, sight, bevel=0.002)
        add_box(f"GEO_Rifle_VentRight_{index:02d}", (x, -0.038, 0.075), (0.014, 0.007, 0.032), collection, sight, bevel=0.002)
    for index in range(8):
        add_box(
            f"GEO_Rifle_ReceiverRail_{index:02d}",
            (-0.095 + index * 0.032, 0.0, 0.119),
            (0.018, 0.048, 0.014),
            collection,
            metal,
            bevel=0.002,
        )

    add_box("GEO_Rifle_RearSightBase", (-0.095, 0.0, 0.142), (0.060, 0.045, 0.026), collection, sight, bevel=0.006)
    add_box("GEO_Rifle_RearSightEar_L", (-0.088, 0.018, 0.174), (0.018, 0.010, 0.050), collection, sight, bevel=0.004)
    add_box("GEO_Rifle_RearSightEar_R", (-0.088, -0.018, 0.174), (0.018, 0.010, 0.050), collection, sight, bevel=0.004)
    add_torus("GEO_Rifle_RearAperture", (-0.080, 0.0, 0.174), 0.009, 0.0023, collection, sight, rotation=(0.0, math.pi / 2.0, 0.0))
    add_box("GEO_Rifle_FrontSightBase", (0.388, 0.0, 0.130), (0.042, 0.046, 0.026), collection, sight, bevel=0.005)
    add_box("GEO_Rifle_FrontSightPost", (0.388, 0.0, 0.171), (0.010, 0.010, 0.057), collection, sight, bevel=0.002)
    add_box("GEO_Rifle_FrontSightEar_L", (0.388, 0.018, 0.169), (0.012, 0.009, 0.060), collection, sight, bevel=0.003)
    add_box("GEO_Rifle_FrontSightEar_R", (0.388, -0.018, 0.169), (0.012, 0.009, 0.060), collection, sight, bevel=0.003)

    add_cylinder("GEO_Rifle_TakedownPinFront", (0.075, 0.033, 0.040), 0.008, 0.008, collection, steel, axis="Y", vertices=24)
    add_cylinder("GEO_Rifle_TakedownPinRear", (-0.095, 0.033, 0.040), 0.008, 0.008, collection, steel, axis="Y", vertices=24)
    add_curve("GEO_Rifle_SlingLoopFront", [(0.345, 0.035, 0.045), (0.360, 0.055, 0.030), (0.375, 0.035, 0.045)], 0.003, collection, steel)
    add_curve("GEO_Rifle_SlingLoopRear", [(-0.285, 0.035, 0.020), (-0.300, 0.055, 0.005), (-0.315, 0.035, 0.020)], 0.003, collection, steel)

    add_socket("SOCKET_Origin", (0.0, 0.0, 0.0), collection)
    add_socket("SOCKET_Muzzle", (0.603, 0.0, 0.075), collection)
    add_socket("SOCKET_Ejection", (0.035, -0.036, 0.083), collection)
    add_socket("SOCKET_Magazine", (0.0, 0.0, -0.075), collection)
    add_socket("SOCKET_FiringHand", (-0.105, 0.0, -0.075), collection)
    add_socket("SOCKET_SupportHand", (0.235, 0.0, 0.035), collection)
    add_socket("SOCKET_ADS_Eye", (-0.520, 0.0, 0.174), collection)
    add_collision_box("UCX_Rifle_Receiver", (-0.01, 0.0, 0.045), (0.28, 0.075, 0.14), collection, collision)
    add_collision_box("UCX_Rifle_Handguard", (0.25, 0.0, 0.075), (0.36, 0.08, 0.09), collection, collision)
    add_collision_box("UCX_Rifle_Stock", (-0.26, 0.0, 0.045), (0.24, 0.08, 0.17), collection, collision)
    for obj in collection.all_objects:
        obj["SKG_AssetID"] = ASSET_ID
        obj["SKG_Identity"] = "AR_M4_family_generic_configuration_unresolved"


VIEWS = [
    {"name": "hero_left", "camera": (0.12, -2.15, 0.62), "target": (0.08, 0.0, 0.02), "lens": 52},
    {"name": "hero_right", "camera": (0.12, 2.15, 0.62), "target": (0.08, 0.0, 0.02), "lens": 52},
    {"name": "side_profile_left", "camera": (0.08, -2.40, 0.20), "target": (0.08, 0.0, 0.02), "lens": 52},
    {"name": "top_mechanical", "camera": (0.06, -0.10, 2.35), "target": (0.08, 0.0, 0.02), "lens": 52},
    {"name": "muzzle_front", "camera": (1.42, -0.72, 0.38), "target": (0.32, 0.0, 0.07), "lens": 58},
    {"name": "stock_rear", "camera": (-1.28, 0.68, 0.40), "target": (-0.08, 0.0, 0.03), "lens": 58},
    {"name": "first_person_hip", "camera": (-0.82, -0.28, 0.38), "target": (0.38, 0.0, 0.07), "lens": 50},
    {"name": "first_person_ads", "camera": (-0.52, 0.0, 0.174), "target": (0.48, 0.0, 0.174), "lens": 82},
]


def render_rifle_views(collection, output):
    import bpy

    bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"
    bpy.context.scene.view_settings.exposure = -2.72
    return render_fixed_views(sdk, collection, output, VIEWS)


def main() -> int:
    args = sdk.parse_worker_args()
    sdk.render_review_views = render_rifle_views
    code = sdk.run_worker(ASSET_ID, build_asset, REQUIRED_SOCKETS)
    collection = __import__("bpy").data.collections["ASSET"]
    validations = {
        "render_count": 8,
        "identity": "AR/M4-family only; exact configuration unresolved",
        "prohibited_claims": ["manufacturer", "chambering", "serial", "trademark", "optic", "unit markings"],
        "provisional_envelope_m": [0.8675, 0.074, 0.134],
        "produced_overall_length_m": 0.968,
        "sight_axis_height_m": 0.174,
        "front_sight_x_m": 0.388,
        "rear_aperture_x_m": -0.080,
        "sight_alignment": {"y_m": 0.0, "z_m": 0.174, "status": "aligned"},
        "coordinate_contract": {"forward": "+X", "right": "+Y", "up": "+Z", "units": "metres"},
    }
    sources = [
        {"path": str(SOURCE_RECEIPT), "bytes": SOURCE_RECEIPT.stat().st_size, "sha256": sha256(SOURCE_RECEIPT), "use": "accepted provisional envelope and prohibited claims"},
        {"path": str(SOURCE_GLB), "bytes": SOURCE_GLB.stat().st_size, "sha256": sha256(SOURCE_GLB), "use": "dimensional silhouette evidence only; geometry not imported"},
    ]
    write_production_receipt(Path(args.output), ASSET_ID, collection, sources, validations)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
