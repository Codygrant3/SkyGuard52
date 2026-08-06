"""Source-only Yak-52 refinement for BLD-M01-YAK-PROD-002.

The 001 Python file is used only for clean geometry/UV/material helper
functions.  This script never opens or imports the 001 blend/GLB, never imports
L88 geometry, and writes to an isolated 002 source directory.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path
from typing import Iterable

import bpy
from mathutils import Vector


BUILD_ID = "BLD-M01-YAK-PROD-002"
ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "Docs" / "AAA_Review" / "BLD_M01_YAK_PROD_002_CONTRACT.json"
)
BASE_SOURCE_PATH = ROOT / "Scripts" / "blender_bld_m01_yak_prod_001.py"
L88_REFERENCE_PATH = (
    ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "L88"
    / "yak52_l88_silhouette_blockout.glb"
)
OUTPUT_DIR = (
    ROOT
    / "Content"
    / "Skyguard"
    / "Meshes"
    / "Source"
    / "Mission01"
    / "Yak52_Production_002"
)
BLEND_PATH = OUTPUT_DIR / "BLD_M01_YAK_PROD_002_MASTER.blend"
GLB_PATH = OUTPUT_DIR / "bld_m01_yak_prod_002.glb"
MANIFEST_PATH = ROOT / "Saved" / "Reports" / "BLD_M01_YAK_PROD_002_MANIFEST.json"
COLLECTION_NAME = "BLD_M01_YAK_PROD_002_EXPORT"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_base_helpers():
    spec = importlib.util.spec_from_file_location("skyguard_yak_001_helpers", BASE_SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load governed 001 helper source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base_helpers()


REQUIRED_EXPORT_MESH_NAMES = (
    "GEO_PROD002_FuselageShell",
    "GEO_PROD002_CowlingShell",
    "GEO_PROD002_CowlingFrontRing",
    "GEO_PROD002_CowlingShutters",
    "GEO_PROD002_CowlingInletCone",
    "GEO_PROD002_Spinner",
    "GEO_PROD002_PropBlade_A",
    "GEO_PROD002_PropBlade_B",
    "GEO_PROD002_Wing_L",
    "GEO_PROD002_Wing_R",
    "GEO_PROD002_WingRootFairing_L",
    "GEO_PROD002_WingRootFairing_R",
    "GEO_PROD002_Flap_L",
    "GEO_PROD002_Flap_R",
    "GEO_PROD002_Aileron_L",
    "GEO_PROD002_Aileron_R",
    "GEO_PROD002_HorizontalStabilizer_L",
    "GEO_PROD002_HorizontalStabilizer_R",
    "GEO_PROD002_TailplaneFairing_L",
    "GEO_PROD002_TailplaneFairing_R",
    "GEO_PROD002_Elevator_L",
    "GEO_PROD002_Elevator_R",
    "GEO_PROD002_VerticalStabilizer",
    "GEO_PROD002_Rudder",
    "GEO_PROD002_CanopyFrontGlass",
    "GEO_PROD002_CanopyRearSlidingGlass",
    "GEO_PROD002_CanopyBowFront",
    "GEO_PROD002_CanopyBowCenter",
    "GEO_PROD002_CanopyBowRear",
    "GEO_PROD002_CanopyRail_L",
    "GEO_PROD002_CanopyRail_R",
    "GEO_PROD002_CockpitSill_L",
    "GEO_PROD002_CockpitSill_R",
    "GEO_PROD002_CockpitFloorRear",
    "GEO_PROD002_CockpitSidewall_L",
    "GEO_PROD002_CockpitSidewall_R",
    "GEO_PROD002_CockpitBulkheadFront",
    "GEO_PROD002_CockpitBulkheadRear",
    "GEO_PROD002_InstrumentPanelRear",
    "GEO_PROD002_InstrumentCoamingRear",
    "GEO_PROD002_GaugeClusterRear",
    "GEO_PROD002_SeatPanRear",
    "GEO_PROD002_SeatBackRear",
    "GEO_PROD002_SeatCushionRear",
    "GEO_PROD002_SeatHarnessRear",
    "GEO_PROD002_ControlStickRear",
    "GEO_PROD002_ThrottleRear",
    "GEO_PROD002_TrimWheelRear",
    "GEO_PROD002_PedalRear_L",
    "GEO_PROD002_PedalRear_R",
    "GEO_PROD002_MainWheelWell_L",
    "GEO_PROD002_MainWheelWell_R",
    "GEO_PROD002_MainGearStrut_L",
    "GEO_PROD002_MainGearStrut_R",
    "GEO_PROD002_MainWheel_L",
    "GEO_PROD002_MainWheel_R",
    "GEO_PROD002_MainGearDoor_L",
    "GEO_PROD002_MainGearDoor_R",
    "GEO_PROD002_NoseWheelWell",
    "GEO_PROD002_NoseGearStrut",
    "GEO_PROD002_NoseWheel",
    "GEO_PROD002_NoseGearDoor",
)


def load_contract() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    if contract["build_id"] != BUILD_ID:
        raise RuntimeError("002 contract id mismatch")
    return contract


def verify_source_lineage(contract: dict) -> None:
    records = (
        (BASE_SOURCE_PATH, contract["base_source_reference"]["sha256"], "001 source"),
        (L88_REFERENCE_PATH, contract["l88_reference"]["sha256"], "L88 datum"),
    )
    for path, expected, label in records:
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError(f"{label} reference missing or drifted")
    for record in contract["review_evidence"]:
        path = ROOT / record["path"]
        if (
            not path.is_file()
            or path.stat().st_size != record["bytes"]
            or sha256_file(path) != record["sha256"]
        ):
            raise RuntimeError(f"Review evidence drifted: {path}")


def require_blender_52() -> None:
    if bpy.app.version[:2] != (5, 2):
        raise RuntimeError(
            f"{BUILD_ID} requires Blender 5.2, found "
            f"{bpy.app.version[0]}.{bpy.app.version[1]}"
        )


def reset_factory_scene() -> bpy.types.Collection:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)
    return collection


def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "MAT002_YakPaint": base.material(
            "MAT002_YakPaint", (0.28, 0.31, 0.32, 1.0), 0.18, 0.30
        ),
        "MAT002_YakBareMetal": base.material(
            "MAT002_YakBareMetal", (0.46, 0.49, 0.50, 1.0), 0.84, 0.22
        ),
        "MAT002_CowlingDark": base.material(
            "MAT002_CowlingDark", (0.025, 0.028, 0.029, 1.0), 0.34, 0.30
        ),
        "MAT002_CockpitGreen": base.material(
            "MAT002_CockpitGreen", (0.14, 0.23, 0.19, 1.0), 0.05, 0.49
        ),
        "MAT002_CockpitBlack": base.material(
            "MAT002_CockpitBlack", (0.015, 0.017, 0.016, 1.0), 0.08, 0.37
        ),
        "MAT002_InstrumentGlass": base.material(
            "MAT002_InstrumentGlass", (0.10, 0.16, 0.17, 0.5), 0.0, 0.08, 0.65, 0.5
        ),
        "MAT002_CanopyGlass": base.material(
            "MAT002_CanopyGlass", (0.27, 0.43, 0.49, 0.16), 0.0, 0.06, 0.94, 0.16
        ),
        "MAT002_SeatVinyl": base.material(
            "MAT002_SeatVinyl", (0.22, 0.21, 0.18, 1.0), 0.0, 0.66
        ),
        "MAT002_HarnessWebbing": base.material(
            "MAT002_HarnessWebbing", (0.48, 0.055, 0.038, 1.0), 0.0, 0.75
        ),
        "MAT002_Propeller": base.material(
            "MAT002_Propeller", (0.04, 0.045, 0.048, 1.0), 0.22, 0.25
        ),
        "MAT002_Rubber": base.material(
            "MAT002_Rubber", (0.012, 0.014, 0.014, 1.0), 0.0, 0.82
        ),
        "MAT002_WheelWell": base.material(
            "MAT002_WheelWell", (0.08, 0.10, 0.09, 1.0), 0.18, 0.58
        ),
        "MAT002_PanelLine": base.material(
            "MAT002_PanelLine", (0.012, 0.013, 0.013, 1.0), 0.0, 0.42
        ),
        "MAT002_Rivet": base.material(
            "MAT002_Rivet", (0.52, 0.54, 0.54, 1.0), 0.9, 0.19
        ),
    }


def create_loft(
    name: str,
    stations: list[tuple[float, float, float, float]],
    segments: int,
    collection: bpy.types.Collection,
    materials: Iterable[bpy.types.Material],
    cockpit_opening: tuple[float, float, int] | None = None,
    cap_start: bool = True,
    cap_end: bool = True,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    for x, ry, rz, z_center in stations:
        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            shoulder = 1.0 - 0.06 * math.cos(2.0 * angle)
            vertices.append(
                (
                    x,
                    ry * shoulder * math.sin(angle),
                    z_center + rz * math.cos(angle),
                )
            )
    faces: list[tuple[int, ...]] = []
    for ring in range(len(stations) - 1):
        x_mid = 0.5 * (stations[ring][0] + stations[ring + 1][0])
        for index in range(segments):
            next_index = (index + 1) % segments
            if cockpit_opening is not None:
                x_start, x_end, opening_segments = cockpit_opening
                top_segment = (
                    index < opening_segments
                    or index >= segments - opening_segments
                )
                if x_start <= x_mid <= x_end and top_segment:
                    continue
            a = ring * segments + index
            b = ring * segments + next_index
            c = (ring + 1) * segments + next_index
            d = (ring + 1) * segments + index
            faces.append((a, b, c, d))
    if cap_start:
        faces.append(tuple(reversed(range(segments))))
    last = (len(stations) - 1) * segments
    if cap_end:
        faces.append(tuple(last + index for index in range(segments)))
    return base.mesh_from_data(name, vertices, faces, collection, materials)


def create_refined_fuselage(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> bpy.types.Object:
    stations = [
        (-3.10, 0.08, 0.11, 0.66),
        (-2.95, 0.16, 0.20, 0.64),
        (-2.65, 0.27, 0.34, 0.59),
        (-2.25, 0.38, 0.48, 0.53),
        (-1.80, 0.48, 0.61, 0.46),
        (-1.50, 0.54, 0.70, 0.40),
        (-1.05, 0.59, 0.76, 0.36),
        (-0.55, 0.61, 0.78, 0.34),
        (0.00, 0.62, 0.79, 0.33),
        (0.55, 0.63, 0.79, 0.32),
        (1.05, 0.64, 0.78, 0.31),
        (1.50, 0.66, 0.77, 0.29),
        (2.00, 0.69, 0.75, 0.27),
        (2.55, 0.73, 0.73, 0.24),
        (3.05, 0.76, 0.72, 0.21),
        (3.55, 0.78, 0.70, 0.18),
        (4.00, 0.75, 0.66, 0.15),
        (4.18, 0.68, 0.58, 0.13),
    ]
    obj = create_loft(
        "GEO_PROD002_FuselageShell",
        stations,
        96,
        collection,
        [mats["MAT002_YakPaint"], mats["MAT002_YakBareMetal"]],
        cockpit_opening=(-1.62, 1.55, 10),
    )
    obj["SKG_SurfaceRole"] = "primary_airframe"
    return obj


def create_annulus(
    name: str,
    x: float,
    outer_radius: float,
    inner_radius: float,
    segments: int,
    collection: bpy.types.Collection,
    materials: Iterable[bpy.types.Material],
) -> bpy.types.Object:
    vertices = []
    for radius in (outer_radius, inner_radius):
        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            vertices.append((x, radius * math.sin(angle), 0.13 + radius * math.cos(angle)))
    faces = []
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.append((index, nxt, segments + nxt, segments + index))
    return base.mesh_from_data(name, vertices, faces, collection, materials, 0.008)


def create_radial_cowling(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    create_loft(
        "GEO_PROD002_CowlingShell",
        [
            (3.72, 0.76, 0.74, 0.14),
            (4.02, 0.78, 0.76, 0.13),
            (4.25, 0.75, 0.73, 0.13),
            (4.36, 0.70, 0.68, 0.13),
        ],
        144,
        collection,
        [mats["MAT002_YakPaint"], mats["MAT002_YakBareMetal"]],
        cap_start=False,
        cap_end=False,
    )
    create_annulus(
        "GEO_PROD002_CowlingFrontRing",
        4.37,
        0.70,
        0.46,
        96,
        collection,
        [mats["MAT002_YakBareMetal"], mats["MAT002_CowlingDark"]],
    )
    segments = 36
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for index in range(segments):
        angle_a = 2.0 * math.pi * index / segments + 0.025
        angle_b = 2.0 * math.pi * (index + 1) / segments - 0.025
        for radius in (0.24, 0.455):
            vertices.append(
                (4.385, radius * math.sin(angle_a), 0.13 + radius * math.cos(angle_a))
            )
            vertices.append(
                (4.385, radius * math.sin(angle_b), 0.13 + radius * math.cos(angle_b))
            )
        start = index * 4
        faces.append((start, start + 1, start + 3, start + 2))
    shutters = base.mesh_from_data(
        "GEO_PROD002_CowlingShutters",
        vertices,
        faces,
        collection,
        [mats["MAT002_CowlingDark"], mats["MAT002_YakBareMetal"]],
        0.004,
    )
    shutters["SKG_Movable"] = True
    shutters["SKG_PivotRole"] = "cowling_shutter_ring"
    set_origin_world(shutters, Vector((4.385, 0.0, 0.13)))
    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=0.21,
        radius2=0.09,
        depth=0.26,
        location=(4.41, 0.0, 0.13),
        rotation=(0.0, math.pi / 2.0, 0.0),
    )
    cone = bpy.context.object
    cone.name = "GEO_PROD002_CowlingInletCone"
    base.finish_mesh(
        cone,
        collection,
        [mats["MAT002_YakBareMetal"], mats["MAT002_CowlingDark"]],
        0.008,
    )


def create_blade(
    name: str,
    sign: float,
    hub: Vector,
    collection: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    sections = 40
    vertices: list[tuple[float, float, float]] = []
    for index in range(sections + 1):
        t = index / sections
        radius = 0.18 + 1.02 * t
        chord = 0.19 - 0.085 * t
        thickness = 0.026 - 0.010 * t
        twist = math.radians(31.0 - 23.0 * t)
        for chord_sign, thick_sign in (
            (-1.0, -1.0),
            (1.0, -1.0),
            (1.0, 1.0),
            (-1.0, 1.0),
        ):
            chord_offset = chord_sign * chord * 0.5
            x = hub.x + chord_offset * math.sin(twist) + thick_sign * thickness * 0.5
            y = hub.y + chord_offset * math.cos(twist)
            z = hub.z + sign * radius
            vertices.append((x, y, z))
    faces: list[tuple[int, ...]] = []
    for index in range(sections):
        a = index * 4
        b = (index + 1) * 4
        faces.extend(
            [
                (a, a + 1, b + 1, b),
                (a + 1, a + 2, b + 2, b + 1),
                (a + 2, a + 3, b + 3, b + 2),
                (a + 3, a, b, b + 3),
            ]
        )
    faces.append((0, 3, 2, 1))
    end = sections * 4
    faces.append((end, end + 1, end + 2, end + 3))
    obj = base.mesh_from_data(name, vertices, faces, collection, [mat], 0.004)
    obj["SKG_Movable"] = True
    obj["SKG_PivotRole"] = "propeller_axis"
    obj["SKG_PivotWorld"] = list(hub)
    set_origin_world(obj, hub)
    return obj


def create_propeller(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    hub = Vector((4.405, 0.0, 0.13))
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64, ring_count=32, location=hub
    )
    spinner = bpy.context.object
    spinner.name = "GEO_PROD002_Spinner"
    spinner.scale = (0.24, 0.22, 0.22)
    base.finish_mesh(
        spinner,
        collection,
        [mats["MAT002_YakBareMetal"], mats["MAT002_YakPaint"]],
    )
    spinner["SKG_Movable"] = True
    spinner["SKG_PivotRole"] = "propeller_axis"
    set_origin_world(spinner, hub)
    create_blade(
        "GEO_PROD002_PropBlade_A", 1.0, hub, collection, mats["MAT002_Propeller"]
    )
    create_blade(
        "GEO_PROD002_PropBlade_B", -1.0, hub, collection, mats["MAT002_Propeller"]
    )


def create_fairing(
    name: str,
    center: tuple[float, float, float],
    scale: tuple[float, float, float],
    collection: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return base.finish_mesh(obj, collection, [mat])


def create_wings_and_tail(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    for side, suffix in ((-1, "L"), (1, "R")):
        base.create_lifting_surface(
            f"GEO_PROD002_Wing_{suffix}",
            side,
            1.12,
            1.72,
            0.86,
            0.42,
            4.65,
            0.20,
            0.27,
            0.23,
            0.12,
            0.0,
            0.72,
            20,
            26,
            collection,
            mats["MAT002_YakPaint"],
        )
        create_fairing(
            f"GEO_PROD002_WingRootFairing_{suffix}",
            (0.85, side * 0.53, 0.22),
            (1.05, 0.20, 0.18),
            collection,
            mats["MAT002_YakPaint"],
        )
        flap = base.create_lifting_surface(
            f"GEO_PROD002_Flap_{suffix}",
            side,
            1.12,
            1.72,
            0.86,
            0.55,
            2.10,
            0.21,
            0.23,
            0.23,
            0.10,
            0.72,
            1.0,
            12,
            12,
            collection,
            mats["MAT002_YakPaint"],
        )
        flap["SKG_Movable"] = True
        flap["SKG_PivotRole"] = "flap_hinge"
        set_origin_world(flap, Vector((1.12 + 1.72 * 0.72, side * 0.55, 0.21)))
        aileron = base.create_lifting_surface(
            f"GEO_PROD002_Aileron_{suffix}",
            side,
            1.12,
            1.72,
            0.86,
            2.10,
            4.65,
            0.23,
            0.27,
            0.23,
            0.10,
            0.72,
            1.0,
            16,
            12,
            collection,
            mats["MAT002_YakPaint"],
        )
        aileron["SKG_Movable"] = True
        aileron["SKG_PivotRole"] = "aileron_hinge"
        set_origin_world(
            aileron, Vector((1.12 + 1.72 * 0.72, side * 2.10, 0.23))
        )
        base.create_lifting_surface(
            f"GEO_PROD002_HorizontalStabilizer_{suffix}",
            side,
            -2.90,
            1.20,
            0.68,
            0.08,
            1.58,
            0.63,
            0.69,
            0.13,
            0.09,
            0.0,
            0.70,
            14,
            20,
            collection,
            mats["MAT002_YakPaint"],
        )
        create_fairing(
            f"GEO_PROD002_TailplaneFairing_{suffix}",
            (-2.36, side * 0.18, 0.64),
            (0.62, 0.14, 0.12),
            collection,
            mats["MAT002_YakPaint"],
        )
        elevator = base.create_lifting_surface(
            f"GEO_PROD002_Elevator_{suffix}",
            side,
            -2.90,
            1.20,
            0.68,
            0.08,
            1.58,
            0.63,
            0.69,
            0.13,
            0.08,
            0.70,
            1.0,
            14,
            12,
            collection,
            mats["MAT002_YakPaint"],
        )
        elevator["SKG_Movable"] = True
        elevator["SKG_PivotRole"] = "elevator_hinge"
        set_origin_world(
            elevator, Vector((-2.90 + 1.20 * 0.70, side * 0.08, 0.64))
        )


def subdivide_profile(
    profile: list[tuple[float, float]], steps: int
) -> list[tuple[float, float]]:
    result: list[tuple[float, float]] = []
    for index, start in enumerate(profile):
        end = profile[(index + 1) % len(profile)]
        for step in range(steps):
            t = step / steps
            result.append(
                (
                    start[0] + (end[0] - start[0]) * t,
                    start[1] + (end[1] - start[1]) * t,
                )
            )
    return result


def extrude_profile_y(
    name: str,
    profile: list[tuple[float, float]],
    half_thickness: float,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> bpy.types.Object:
    profile = subdivide_profile(profile, 4)
    vertices = [(x, -half_thickness, z) for x, z in profile] + [
        (x, half_thickness, z) for x, z in profile
    ]
    count = len(profile)
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(count + index for index in range(count)),
    ]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    return base.mesh_from_data(name, vertices, faces, collection, [material], 0.012)


def create_vertical_tail(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    fin = extrude_profile_y(
        "GEO_PROD002_VerticalStabilizer",
        [
            (-3.08, 0.64),
            (-2.99, 1.16),
            (-2.80, 1.62),
            (-2.52, 1.96),
            (-2.27, 2.05),
            (-1.86, 1.87),
            (-1.68, 0.72),
        ],
        0.055,
        collection,
        mats["MAT002_YakPaint"],
    )
    fin["SKG_SurfaceRole"] = "vertical_tail_fixed"
    rudder = extrude_profile_y(
        "GEO_PROD002_Rudder",
        [
            (-3.08, 0.68),
            (-3.05, 1.30),
            (-2.88, 1.70),
            (-2.52, 1.96),
            (-2.31, 1.93),
            (-2.42, 0.76),
        ],
        0.047,
        collection,
        mats["MAT002_YakPaint"],
    )
    rudder["SKG_Movable"] = True
    rudder["SKG_PivotRole"] = "rudder_hinge"
    rudder["SKG_PivotWorld"] = [-2.48, 0.0, 1.30]
    set_origin_world(rudder, Vector((-2.48, 0.0, 1.30)))


def create_cockpit_sill(
    name: str,
    side: int,
    collection: bpy.types.Collection,
    materials: Iterable[bpy.types.Material],
) -> bpy.types.Object:
    profile = subdivide_profile(
        [
            (-1.65, 0.92),
            (1.55, 0.98),
            (1.48, 1.27),
            (-1.55, 1.27),
        ],
        5,
    )
    inner_y = side * 0.49
    outer_y = side * 0.59
    vertices = [(x, inner_y, z) for x, z in profile] + [
        (x, outer_y, z) for x, z in profile
    ]
    count = len(profile)
    faces = [
        tuple(reversed(range(count))),
        tuple(count + index for index in range(count)),
    ]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    return base.mesh_from_data(name, vertices, faces, collection, materials, 0.018)


def create_canopy(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    base.create_canopy_shell(
        "GEO_PROD002_CanopyFrontGlass",
        0.02,
        1.46,
        0.56,
        1.29,
        2.08,
        collection,
        mats["MAT002_CanopyGlass"],
    )
    rear = base.create_canopy_shell(
        "GEO_PROD002_CanopyRearSlidingGlass",
        -1.53,
        -0.03,
        0.57,
        1.29,
        2.06,
        collection,
        mats["MAT002_CanopyGlass"],
    )
    rear["SKG_Movable"] = True
    rear["SKG_PivotRole"] = "canopy_slide_origin"
    set_origin_world(rear, Vector((-1.53, 0.0, 1.34)))
    for name, x in (
        ("GEO_PROD002_CanopyBowFront", 1.44),
        ("GEO_PROD002_CanopyBowCenter", -0.03),
        ("GEO_PROD002_CanopyBowRear", -1.53),
    ):
        base.create_arch(
            name,
            x,
            0.58,
            1.29,
            2.07,
            collection,
            mats["MAT002_YakBareMetal"],
        )
    for side, suffix in ((-1, "L"), (1, "R")):
        create_cockpit_sill(
            f"GEO_PROD002_CockpitSill_{suffix}",
            side,
            collection,
            [mats["MAT002_YakPaint"], mats["MAT002_YakBareMetal"]],
        )
        rail = base.add_beveled_box(
            f"GEO_PROD002_CanopyRail_{suffix}",
            (-0.04, side * 0.575, 1.29),
            (1.58, 0.035, 0.035),
            collection,
            [mats["MAT002_YakBareMetal"]],
            0.01,
        )
        rail["SKG_PivotRole"] = "canopy_rail"


def create_panel_shape(
    name: str,
    x: float,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> bpy.types.Object:
    profile = [
        (-0.56, 0.78),
        (-0.51, 1.26),
        (-0.34, 1.47),
        (0.34, 1.47),
        (0.51, 1.26),
        (0.56, 0.78),
    ]
    half_thickness = 0.06
    vertices = [(x - half_thickness, y, z) for y, z in profile] + [
        (x + half_thickness, y, z) for y, z in profile
    ]
    count = len(profile)
    faces = [
        tuple(reversed(range(count))),
        tuple(count + index for index in range(count)),
    ]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    return base.mesh_from_data(name, vertices, faces, collection, [material], 0.018)


def create_cockpit_sidewall(
    name: str,
    side: int,
    collection: bpy.types.Collection,
    materials: Iterable[bpy.types.Material],
) -> bpy.types.Object:
    profile = subdivide_profile(
        [
            (-1.70, 0.64),
            (0.20, 0.64),
            (0.18, 1.27),
            (-0.10, 1.31),
            (-1.55, 1.31),
        ],
        4,
    )
    inner_y = side * 0.47
    outer_y = side * 0.58
    vertices = [(x, inner_y, z) for x, z in profile] + [
        (x, outer_y, z) for x, z in profile
    ]
    count = len(profile)
    faces = [
        tuple(reversed(range(count))),
        tuple(count + index for index in range(count)),
    ]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    return base.mesh_from_data(name, vertices, faces, collection, materials, 0.025)


def create_gauge_cluster(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> bpy.types.Object:
    gauge_objects = []
    layout = [
        (-0.30, 1.30, 0.085),
        (-0.10, 1.34, 0.095),
        (0.12, 1.34, 0.095),
        (0.32, 1.29, 0.080),
        (-0.31, 1.10, 0.075),
        (-0.12, 1.12, 0.082),
        (0.08, 1.12, 0.082),
        (0.28, 1.08, 0.072),
        (-0.19, 0.92, 0.065),
        (0.00, 0.93, 0.067),
        (0.19, 0.91, 0.063),
    ]
    for index, (y, z, radius) in enumerate(layout):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=radius,
            depth=0.025,
            location=(0.145, y, z),
            rotation=(0.0, math.pi / 2.0, 0.0),
        )
        gauge = bpy.context.object
        gauge.name = f"PART002_Gauge_{index:02d}"
        base.finish_mesh(
            gauge,
            collection,
            [mats["MAT002_CockpitBlack"], mats["MAT002_InstrumentGlass"]],
            0.004,
        )
        gauge_objects.append(gauge)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in gauge_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = gauge_objects[0]
    bpy.ops.object.join()
    cluster = bpy.context.object
    cluster.name = "GEO_PROD002_GaugeClusterRear"
    base.ensure_uv0(cluster)
    return cluster


def create_rear_cockpit(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    base.add_beveled_box(
        "GEO_PROD002_CockpitFloorRear",
        (-0.78, 0.0, 0.58),
        (1.12, 0.49, 0.055),
        collection,
        [mats["MAT002_CockpitGreen"]],
        0.025,
    )
    for side, suffix in ((-1, "L"), (1, "R")):
        sidewall = create_cockpit_sidewall(
            f"GEO_PROD002_CockpitSidewall_{suffix}",
            side,
            collection,
            [mats["MAT002_CockpitGreen"], mats["MAT002_CockpitBlack"]],
        )
        sidewall["SKG_CockpitRole"] = "rear_sidewall"
    create_panel_shape(
        "GEO_PROD002_CockpitBulkheadFront",
        0.20,
        collection,
        mats["MAT002_CockpitGreen"],
    )
    create_panel_shape(
        "GEO_PROD002_CockpitBulkheadRear",
        -1.70,
        collection,
        mats["MAT002_CockpitGreen"],
    )
    create_panel_shape(
        "GEO_PROD002_InstrumentPanelRear",
        0.11,
        collection,
        mats["MAT002_CockpitBlack"],
    )
    base.add_beveled_box(
        "GEO_PROD002_InstrumentCoamingRear",
        (0.03, 0.0, 1.47),
        (0.20, 0.53, 0.055),
        collection,
        [mats["MAT002_CockpitBlack"]],
        0.025,
    )
    create_gauge_cluster(collection, mats)
    seat_pan = base.add_beveled_box(
        "GEO_PROD002_SeatPanRear",
        (-1.12, 0.0, 0.72),
        (0.44, 0.43, 0.08),
        collection,
        [mats["MAT002_YakBareMetal"]],
        0.045,
    )
    seat_pan["SKG_CockpitRole"] = "seat_structure"
    seat_back = base.add_beveled_box(
        "GEO_PROD002_SeatBackRear",
        (-1.44, 0.0, 1.02),
        (0.08, 0.43, 0.42),
        collection,
        [mats["MAT002_YakBareMetal"]],
        0.04,
    )
    seat_back.rotation_euler.y = math.radians(-8.0)
    base.add_beveled_box(
        "GEO_PROD002_SeatCushionRear",
        (-1.09, 0.0, 0.80),
        (0.38, 0.39, 0.09),
        collection,
        [mats["MAT002_SeatVinyl"]],
        0.055,
    )
    harness = base.add_beveled_box(
        "GEO_PROD002_SeatHarnessRear",
        (-1.48, 0.0, 1.12),
        (0.34, 0.025, 0.045),
        collection,
        [mats["MAT002_HarnessWebbing"]],
        0.012,
    )
    harness.rotation_euler.x = math.radians(18.0)
    stick = base.add_cylinder(
        "GEO_PROD002_ControlStickRear",
        0.027,
        0.56,
        (-0.68, 0.0, 0.84),
        (0.0, 0.13, 0.0),
        collection,
        [mats["MAT002_CockpitBlack"]],
        32,
        0.006,
    )
    stick["SKG_Movable"] = True
    stick["SKG_PivotRole"] = "control_stick_base"
    set_origin_world(stick, Vector((-0.68, 0.0, 0.56)))
    throttle = base.add_beveled_box(
        "GEO_PROD002_ThrottleRear",
        (-0.52, -0.50, 0.98),
        (0.17, 0.065, 0.10),
        collection,
        [mats["MAT002_CockpitBlack"]],
        0.015,
    )
    throttle["SKG_Movable"] = True
    throttle["SKG_PivotRole"] = "throttle_axis"
    set_origin_world(throttle, Vector((-0.52, -0.50, 0.93)))
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.105,
        minor_radius=0.018,
        major_segments=40,
        minor_segments=10,
        location=(-0.78, 0.50, 0.96),
        rotation=(math.pi / 2.0, 0.0, 0.0),
    )
    trim = bpy.context.object
    trim.name = "GEO_PROD002_TrimWheelRear"
    base.finish_mesh(trim, collection, [mats["MAT002_CockpitBlack"]])
    trim["SKG_Movable"] = True
    trim["SKG_PivotRole"] = "trim_wheel_axis"
    set_origin_world(trim, Vector((-0.78, 0.50, 0.96)))
    for side, suffix in ((-1, "L"), (1, "R")):
        pedal = base.add_beveled_box(
            f"GEO_PROD002_PedalRear_{suffix}",
            (-0.20, side * 0.20, 0.62),
            (0.15, 0.095, 0.035),
            collection,
            [mats["MAT002_YakBareMetal"]],
            0.012,
        )
        pedal["SKG_Movable"] = True
        pedal["SKG_PivotRole"] = "pedal_hinge"
        set_origin_world(pedal, Vector((-0.28, side * 0.20, 0.62)))


def set_origin_world(obj: bpy.types.Object, pivot: Vector) -> None:
    previous = bpy.context.scene.cursor.location.copy()
    bpy.context.scene.cursor.location = pivot
    base.set_active(obj)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    bpy.context.scene.cursor.location = previous


def add_strut_between(
    name: str,
    start: Vector,
    end: Vector,
    radius: float,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> bpy.types.Object:
    direction = end - start
    midpoint = (start + end) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius,
        depth=direction.length,
        location=midpoint,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(direction.normalized())
    obj.rotation_mode = "XYZ"
    obj = base.finish_mesh(obj, collection, [material], 0.006)
    set_origin_world(obj, start)
    return obj


def add_wheel(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    width: float,
    collection: bpy.types.Collection,
    mats: dict[str, bpy.types.Material],
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius - width * 0.5,
        minor_radius=width * 0.5,
        major_segments=64,
        minor_segments=16,
        location=location,
        rotation=(math.pi / 2.0, 0.0, 0.0),
    )
    wheel = bpy.context.object
    wheel.name = name
    return base.finish_mesh(
        wheel, collection, [mats["MAT002_Rubber"], mats["MAT002_YakBareMetal"]]
    )


def create_landing_gear(
    collection: bpy.types.Collection, mats: dict[str, bpy.types.Material]
) -> None:
    for side, suffix in ((-1, "L"), (1, "R")):
        well = base.add_cylinder(
            f"GEO_PROD002_MainWheelWell_{suffix}",
            0.33,
            0.08,
            (0.75, side * 1.05, 0.04),
            (0.0, math.pi / 2.0, 0.0),
            collection,
            [mats["MAT002_WheelWell"]],
            64,
            0.01,
        )
        well["SKG_GearRole"] = "main_wheel_well"
        strut = add_strut_between(
            f"GEO_PROD002_MainGearStrut_{suffix}",
            Vector((0.78, side * 0.92, 0.15)),
            Vector((0.48, side * 1.12, -0.19)),
            0.035,
            collection,
            mats["MAT002_YakBareMetal"],
        )
        strut["SKG_Movable"] = True
        strut["SKG_PivotRole"] = "main_gear_pivot"
        wheel = add_wheel(
            f"GEO_PROD002_MainWheel_{suffix}",
            (0.45, side * 1.12, -0.31),
            0.30,
            0.11,
            collection,
            mats,
        )
        wheel["SKG_Movable"] = True
        wheel["SKG_PivotRole"] = "wheel_axle"
        door = base.add_beveled_box(
            f"GEO_PROD002_MainGearDoor_{suffix}",
            (0.72, side * 0.96, -0.08),
            (0.36, 0.055, 0.15),
            collection,
            [mats["MAT002_YakPaint"], mats["MAT002_WheelWell"]],
            0.015,
        )
        door["SKG_Movable"] = True
        door["SKG_PivotRole"] = "main_gear_door_hinge"
        set_origin_world(door, Vector((0.72, side * 0.91, 0.02)))
    base.add_cylinder(
        "GEO_PROD002_NoseWheelWell",
        0.23,
        0.07,
        (3.05, 0.0, -0.18),
        (0.0, math.pi / 2.0, 0.0),
        collection,
        [mats["MAT002_WheelWell"]],
        64,
        0.01,
    )
    nose_strut = add_strut_between(
        "GEO_PROD002_NoseGearStrut",
        Vector((3.02, 0.0, 0.04)),
        Vector((3.26, 0.0, -0.29)),
        0.03,
        collection,
        mats["MAT002_YakBareMetal"],
    )
    nose_strut["SKG_Movable"] = True
    nose_strut["SKG_PivotRole"] = "nose_gear_pivot"
    nose_wheel = add_wheel(
        "GEO_PROD002_NoseWheel",
        (3.28, 0.0, -0.39),
        0.22,
        0.085,
        collection,
        mats,
    )
    nose_wheel["SKG_Movable"] = True
    nose_wheel["SKG_PivotRole"] = "wheel_axle"
    nose_door = base.add_beveled_box(
        "GEO_PROD002_NoseGearDoor",
        (3.08, 0.13, -0.20),
        (0.29, 0.035, 0.12),
        collection,
        [mats["MAT002_YakPaint"], mats["MAT002_WheelWell"]],
        0.012,
    )
    nose_door["SKG_Movable"] = True
    nose_door["SKG_PivotRole"] = "nose_gear_door_hinge"
    set_origin_world(nose_door, Vector((3.08, 0.10, -0.10)))


def create_datums(collection: bpy.types.Collection) -> None:
    specs = {
        "DATUM_AircraftOrigin": ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        "DATUM_PropAxis": ((4.405, 0.0, 0.13), (0.0, math.pi / 2.0, 0.0)),
        "DATUM_RearSeatEye": ((-0.88, 0.0, 1.52), (0.0, 0.0, 0.0)),
        "DATUM_LengthNose": ((4.645, 0.0, 0.13), (0.0, 0.0, 0.0)),
        "DATUM_LengthTail": ((-3.10, 0.0, 0.66), (0.0, 0.0, 0.0)),
        "DATUM_Wingtip_L": ((0.0, -4.65, 0.25), (0.0, 0.0, 0.0)),
        "DATUM_Wingtip_R": ((0.0, 4.65, 0.25), (0.0, 0.0, 0.0)),
        "DATUM_HeightTop": ((0.0, 0.0, 2.09), (0.0, 0.0, 0.0)),
        "DATUM_HeightBottom": ((0.0, 0.0, -0.61), (0.0, 0.0, 0.0)),
        "DATUM_PropTipTop": ((4.405, 0.0, 1.33), (0.0, 0.0, 0.0)),
        "DATUM_PropTipBottom": ((4.405, 0.0, -1.07), (0.0, 0.0, 0.0)),
        "DATUM_CockpitClear_L": ((-0.88, -0.36, 1.34), (0.0, 0.0, 0.0)),
        "DATUM_CockpitClear_R": ((-0.88, 0.36, 1.34), (0.0, 0.0, 0.0)),
        "DATUM_CockpitRail": ((-0.88, 0.0, 1.34), (0.0, 0.0, 0.0)),
        "SOCKET_PilotSeat": ((0.82, 0.0, 0.84), (0.0, 0.0, 0.0)),
        "SOCKET_RearGunnerSeat": ((-0.92, 0.0, 0.84), (0.0, 0.0, 0.0)),
        "SOCKET_ADSEye": ((-0.88, 0.0, 1.52), (0.0, 0.0, 0.0)),
        "SOCKET_RifleGrip_R": ((-0.42, 0.25, 1.35), (0.0, 0.0, 0.0)),
        "SOCKET_RifleGrip_L": ((0.02, 0.25, 1.38), (0.0, 0.0, 0.0)),
        "SOCKET_RifleMuzzle": ((1.03, 0.25, 1.43), (0.0, 0.0, 0.0)),
        "SOCKET_IglaGrip_R": ((-0.34, 0.30, 1.30), (0.0, 0.0, 0.0)),
        "SOCKET_IglaGrip_L": ((0.10, 0.30, 1.34), (0.0, 0.0, 0.0)),
        "SOCKET_IglaLaunchAxis": ((1.28, 0.30, 1.42), (0.0, 0.0, 0.0)),
        "SOCKET_CanopyRearTravel": ((-1.25, 0.0, 1.33), (0.0, 0.0, 0.0)),
        "SOCKET_CockpitSafetyOrigin": ((-0.30, 0.0, 1.20), (0.0, 0.0, 0.0)),
        "SOCKET_CameraRearGunner": ((-0.88, 0.0, 1.52), (0.0, 0.0, 0.0)),
    }
    for name, (location, rotation) in specs.items():
        obj = base.add_empty(name, location, rotation, collection)
        obj["datum_contract"] = BUILD_ID


def apply_decal_metadata(
    contract: dict,
    collection: bpy.types.Collection,
    mats: dict[str, bpy.types.Material],
) -> None:
    objects = {obj.name: obj for obj in collection.all_objects}
    ids = contract["material_id_contract"]
    for name in contract["decal_ready_objects"]:
        obj = objects[name]
        if mats["MAT002_PanelLine"].name not in [
            slot.material.name for slot in obj.material_slots if slot.material
        ]:
            obj.data.materials.append(mats["MAT002_PanelLine"])
        if mats["MAT002_Rivet"].name not in [
            slot.material.name for slot in obj.material_slots if slot.material
        ]:
            obj.data.materials.append(mats["MAT002_Rivet"])
        obj["SKG_DecalReady"] = True
        obj["SKG_MaterialID_PanelLine"] = ids["panel_line_decal"]
        obj["SKG_MaterialID_Rivet"] = ids["rivet_decal"]
        obj["SKG_PanelLineUVChannel"] = "UV0"
        obj["SKG_RivetPlacement"] = "decal_or_geometry_node_source"


def reject_forbidden_names(contract: dict, collection: bpy.types.Collection) -> None:
    tokens = [token.lower() for token in contract["forbidden_name_tokens"]]
    violations = [
        obj.name
        for obj in collection.all_objects
        if any(token in obj.name.lower() for token in tokens)
    ]
    if violations:
        raise RuntimeError(f"Forbidden export names: {violations}")


def create_aircraft(
    contract: dict,
    collection: bpy.types.Collection,
    mats: dict[str, bpy.types.Material],
) -> None:
    create_refined_fuselage(collection, mats)
    create_radial_cowling(collection, mats)
    create_propeller(collection, mats)
    create_wings_and_tail(collection, mats)
    create_vertical_tail(collection, mats)
    create_canopy(collection, mats)
    create_rear_cockpit(collection, mats)
    create_landing_gear(collection, mats)
    create_datums(collection)
    apply_decal_metadata(contract, collection, mats)


def measured_dimensions(collection: bpy.types.Collection) -> dict[str, float]:
    objects = {obj.name: obj for obj in collection.all_objects}

    def distance(a: str, b: str) -> float:
        return (objects[a].location - objects[b].location).length

    return {
        "overall_length": abs(
            objects["DATUM_LengthNose"].location.x
            - objects["DATUM_LengthTail"].location.x
        ),
        "wingspan": abs(
            objects["DATUM_Wingtip_R"].location.y
            - objects["DATUM_Wingtip_L"].location.y
        ),
        "overall_height": abs(
            objects["DATUM_HeightTop"].location.z
            - objects["DATUM_HeightBottom"].location.z
        ),
        "propeller_diameter": abs(
            objects["DATUM_PropTipTop"].location.z
            - objects["DATUM_PropTipBottom"].location.z
        ),
        "rear_cockpit_clear_width": abs(
            objects["DATUM_CockpitClear_R"].location.y
            - objects["DATUM_CockpitClear_L"].location.y
        ),
        "rear_cockpit_rail_height": objects["DATUM_CockpitRail"].location.z,
    }


def validate_contract(
    contract: dict, collection: bpy.types.Collection
) -> dict[str, object]:
    if set(contract["required_mesh_objects"]) != set(REQUIRED_EXPORT_MESH_NAMES):
        raise RuntimeError("002 generator/contract mesh-list drift")
    objects = {obj.name: obj for obj in collection.all_objects}
    missing_meshes = sorted(set(contract["required_mesh_objects"]) - set(objects))
    missing_sockets = sorted(set(contract["required_socket_objects"]) - set(objects))
    missing_datums = sorted(set(contract["required_datum_objects"]) - set(objects))
    uv_failures = []
    material_failures = []
    minimum_vertex_failures = []
    for name in contract["required_mesh_objects"]:
        obj = objects.get(name)
        if obj is None or obj.type != "MESH":
            continue
        if contract["required_uv_layer"] not in obj.data.uv_layers:
            uv_failures.append(name)
        if not obj.data.materials:
            material_failures.append(name)
        minimum = contract["minimum_mesh_vertices"].get(name)
        if minimum is not None and len(obj.data.vertices) < minimum:
            minimum_vertex_failures.append(
                {"name": name, "actual": len(obj.data.vertices), "minimum": minimum}
            )
    movable_failures = []
    pivot_position_failures = []
    for name, pivot_role in contract["movable_parts"].items():
        obj = objects.get(name)
        if (
            obj is None
            or obj.get("SKG_Movable") is not True
            or obj.get("SKG_PivotRole") != pivot_role
        ):
            movable_failures.append(name)
        expected_position = Vector(contract["movable_pivot_positions_m"][name])
        if obj is None or (obj.location - expected_position).length > 0.005:
            pivot_position_failures.append(name)
    decal_failures = []
    for name in contract["decal_ready_objects"]:
        obj = objects.get(name)
        if (
            obj is None
            or obj.get("SKG_DecalReady") is not True
            or obj.get("SKG_MaterialID_PanelLine")
            != contract["material_id_contract"]["panel_line_decal"]
            or obj.get("SKG_MaterialID_Rivet")
            != contract["material_id_contract"]["rivet_decal"]
        ):
            decal_failures.append(name)
    result = {
        "missing_meshes": missing_meshes,
        "missing_sockets": missing_sockets,
        "missing_datums": missing_datums,
        "uv_failures": uv_failures,
        "material_failures": material_failures,
        "minimum_vertex_failures": minimum_vertex_failures,
        "movable_failures": movable_failures,
        "pivot_position_failures": pivot_position_failures,
        "decal_failures": decal_failures,
    }
    result["pass"] = not any(result.values())
    return result


def object_record(obj: bpy.types.Object) -> dict:
    record = {
        "name": obj.name,
        "type": obj.type,
        "location_m": [round(float(value), 6) for value in obj.location],
        "rotation_radians": [round(float(value), 6) for value in obj.rotation_euler],
        "scale": [round(float(value), 6) for value in obj.scale],
        "custom_properties": {
            key: obj[key]
            for key in obj.keys()
            if key != "_RNA_UI"
            and isinstance(obj[key], (str, int, float, bool))
        },
    }
    if obj.type == "MESH":
        record.update(
            {
                "vertices": len(obj.data.vertices),
                "polygons": len(obj.data.polygons),
                "uv_layers": [layer.name for layer in obj.data.uv_layers],
                "material_slots": [
                    slot.material.name for slot in obj.material_slots if slot.material
                ],
            }
        )
    return record


def save_and_export(collection: bpy.types.Collection) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in collection.all_objects:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_yup=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_extras=True,
        export_animations=False,
    )


def write_manifest(
    contract: dict,
    collection: bpy.types.Collection,
    validation: dict[str, object],
    elapsed_seconds: float,
) -> None:
    manifest = {
        "schema": "skyguard.bld-m01-yak-prod-002.artifact-manifest.v1",
        "build_id": BUILD_ID,
        "blender_version": ".".join(str(value) for value in bpy.app.version),
        "coordinate_contract": contract["coordinate_contract"],
        "reference_dimensions_m": contract["reference_dimensions_m"],
        "measured_dimensions_m": measured_dimensions(collection),
        "base_source_reference": {
            "path": str(BASE_SOURCE_PATH),
            "sha256": sha256_file(BASE_SOURCE_PATH),
            "use": "python_helpers_only_no_001_artifact_or_datablock_import",
        },
        "l88_reference": {
            "path": str(L88_REFERENCE_PATH),
            "sha256": sha256_file(L88_REFERENCE_PATH),
            "use": "datum_reference_only_not_imported",
        },
        "review_evidence": contract["review_evidence"],
        "generator": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "contract": {
            "path": str(CONTRACT_PATH),
            "sha256": sha256_file(CONTRACT_PATH),
        },
        "outputs": {
            "blend": {
                "path": str(BLEND_PATH),
                "bytes": BLEND_PATH.stat().st_size,
                "sha256": sha256_file(BLEND_PATH),
            },
            "glb": {
                "path": str(GLB_PATH),
                "bytes": GLB_PATH.stat().st_size,
                "sha256": sha256_file(GLB_PATH),
            },
        },
        "objects": [
            object_record(obj)
            for obj in sorted(collection.all_objects, key=lambda item: item.name)
        ],
        "validation": validation,
        "forbidden_name_violations": [],
        "elapsed_seconds": round(elapsed_seconds, 3),
        "gate": "PASS" if validation["pass"] else "FAIL",
        "promotion": contract["promotion"],
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    started = time.perf_counter()
    require_blender_52()
    contract = load_contract()
    verify_source_lineage(contract)
    collection = reset_factory_scene()
    mats = build_materials()
    create_aircraft(contract, collection, mats)
    reject_forbidden_names(contract, collection)
    validation = validate_contract(contract, collection)
    if not validation["pass"]:
        raise RuntimeError(f"002 source contract failed: {validation}")
    save_and_export(collection)
    write_manifest(contract, collection, validation, time.perf_counter() - started)
    print(f"[{BUILD_ID}] source build complete")
    print(f"[{BUILD_ID}] blend={BLEND_PATH}")
    print(f"[{BUILD_ID}] glb={GLB_PATH}")
    print(f"[{BUILD_ID}] manifest={MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[{BUILD_ID}] FAILED: {exc}", file=sys.stderr)
        raise
