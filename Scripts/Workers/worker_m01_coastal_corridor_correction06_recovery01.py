from __future__ import annotations

"""Bounded visual recovery for the continuous Mission 1 coastal corridor.

The failed Correction06 attempt is preserved.  This binding reuses only the
valid continuous-corridor construction contract and adds the missing authored
terrain relief, closed curbs, broken surf contact, and grounded streetscape
detail identified by direct full-resolution review.
"""

import hashlib
import json
import math
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\Workers\worker_m01_coastal_corridor_correction06.py")
EXPECTED_SOURCE_SHA256 = "0342665641472e111668deefe128b9cc77d64ed45ee30d40be87ccf62ccaf6bf"
FAILED_REVIEW = Path(
    r"D:\Skyguard52\Production\Attempts\m01-coastal-corridor-correction06\attempt_20260810T201523968795Z\visual_review.json"
)
EXPECTED_FAILED_REVIEW_SHA256 = "ae65758fdc4a400e5d8ae0fb5cf0f723cd2a26c5aad401f87ba904e32cdc762b"
ASSET_ID = "m01-coastal-corridor-correction06-recovery01"
GATE_ID = "M01_ENVIRONMENT_ART_DIRECTION_CORRECTION06_CONTINUOUS_COASTAL_CORRIDOR_RECOVERY01"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_file() or sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Correction06 frozen source authority mismatch")
if not FAILED_REVIEW.is_file() or sha256(FAILED_REVIEW) != EXPECTED_FAILED_REVIEW_SHA256:
    raise RuntimeError("Correction06 failed visual-review authority mismatch")

source_text = SOURCE.read_text(encoding="utf-8")
substitutions = (
    ('ASSET_ID = "m01-coastal-corridor-correction06"', f'ASSET_ID = "{ASSET_ID}"'),
    (
        'GATE = "M01_ENVIRONMENT_ART_DIRECTION_CORRECTION06_CONTINUOUS_COASTAL_CORRIDOR"',
        f'GATE = "{GATE_ID}"',
    ),
    ('"M01_CoastalCorridor_Correction06.blend"', '"M01_CoastalCorridor_Correction06_Recovery01.blend"'),
    ('"M01_CoastalCorridor_Correction06.glb"', '"M01_CoastalCorridor_Correction06_Recovery01.glb"'),
)
for old_value, new_value in substitutions:
    if source_text.count(old_value) != 1:
        raise RuntimeError(f"Frozen source substitution cardinality mismatch: {old_value}")
    source_text = source_text.replace(old_value, new_value, 1)
source_text = source_text.replace(
    "skyguard.m01-coastal-corridor-correction06.",
    "skyguard.m01-coastal-corridor-correction06-recovery01.",
)

namespace = {"__name__": "_skyguard_m01_c06_recovery01_base", "__file__": str(SOURCE)}
exec(compile(source_text, str(SOURCE) + "::Recovery01Base", "exec"), namespace)

bpy = namespace["bpy"]
Vector = namespace["Vector"]
ORIGINAL_CREATE_BAND = namespace["create_band"]
ORIGINAL_CREATE_REVIEW_OCEAN = namespace["create_review_ocean"]
ORIGINAL_BUILD_MATERIALS = namespace["build_materials"]
ORIGINAL_BUILD_CORRIDOR = namespace["build_corridor"]
add_mesh = namespace["add_mesh"]
add_box = namespace["add_box"]
add_cylinder = namespace["add_cylinder"]
boundary_profile = namespace["boundary_profile"]
boundary_height = namespace["boundary_height"]
shoreline_y = namespace["shoreline_y"]
make_simple_material = namespace["make_simple_material"]


namespace["CAMERAS"] = {
    "route_aerial": ((-5.0, -32.0, 25.0), (170.0, 91.0, 1.0), 58.0),
    "shoreline_oblique": ((56.0, 7.0, 5.8), (138.0, 54.0, 0.15), 62.0),
    "promenade_furniture": ((170.0, 67.0, 3.2), (245.0, 83.0, 1.05), 66.0),
    "integrated_intersection": ((236.0, 88.0, 8.5), (260.0, 126.0, 0.65), 61.0),
    "urban_service_detail": ((396.0, 97.0, 7.0), (445.0, 116.0, 0.8), 64.0),
    "wet_contact_close": ((330.0, 14.0, 4.6), (380.0, 44.0, -0.15), 66.0),
}


def refined_create_band(name, xs, left_key, right_key, material, target):
    if name not in {"SM_M01_C06_WetSand", "SM_M01_C06_DrySand", "SM_M01_C06_DuneTransition"}:
        return ORIGINAL_CREATE_BAND(name, xs, left_key, right_key, material, target)

    row_count = 4 if name.endswith("WetSand") else 6 if name.endswith("DrySand") else 8
    amplitude = 0.035 if name.endswith("WetSand") else 0.095 if name.endswith("DrySand") else 0.24
    vertices = []
    for x in xs:
        profile = boundary_profile(x)
        y0 = profile[left_key]
        y1 = profile[right_key]
        z0 = boundary_height(x, left_key)
        z1 = boundary_height(x, right_key)
        for row in range(row_count + 1):
            t = row / row_count
            y = y0 + (y1 - y0) * t
            envelope = math.sin(math.pi * t)
            relief = amplitude * envelope * (
                0.55 * math.sin(x / 15.5 + row * 0.91)
                + 0.30 * math.sin(x / 5.7 - row * 0.43)
                + 0.15 * math.sin(y / 3.8)
            )
            vertices.append((x, y, z0 + (z1 - z0) * t + relief))
    faces = []
    stride = row_count + 1
    for x_index in range(len(xs) - 1):
        for row in range(row_count):
            a = x_index * stride + row
            b = (x_index + 1) * stride + row
            faces.append((a, a + 1, b + 1, b))
    return add_mesh(name, vertices, faces, material, target)


def refined_create_review_ocean(xs, material, review):
    row_count = 9
    vertices = []
    for x in xs:
        y0 = -110.0
        y1 = shoreline_y(x) - 0.72
        for row in range(row_count + 1):
            t = row / row_count
            y = y0 + (y1 - y0) * t
            wave = (
                0.12 * math.sin(x / 13.0 + y / 9.0)
                + 0.055 * math.sin(x / 4.2 - y / 6.5)
                + 0.025 * math.sin(x / 1.9 + y / 2.8)
            )
            shoal = 0.10 * t * t
            vertices.append((x, y, -0.58 + wave + shoal))
    faces = []
    stride = row_count + 1
    for x_index in range(len(xs) - 1):
        for row in range(row_count):
            a = x_index * stride + row
            b = (x_index + 1) * stride + row
            faces.append((a, a + 1, b + 1, b))
    return add_mesh("REVIEW_ONLY_M01_C06_Ocean", vertices, faces, material, review)


def refined_build_materials():
    materials = ORIGINAL_BUILD_MATERIALS()
    materials.update(
        {
            "soil": make_simple_material("M_M01_C06R01_PlantingSoil", (0.075, 0.046, 0.025, 1.0), 0.96),
            "wood": make_simple_material("M_M01_C06R01_WeatheredWood", (0.24, 0.13, 0.065, 1.0), 0.82),
            "paint": make_simple_material("M_M01_C06R01_PaintedMetal", (0.12, 0.20, 0.22, 1.0), 0.46, 0.62),
            "tactile": make_simple_material("M_M01_C06R01_TactilePaving", (0.50, 0.38, 0.12, 1.0), 0.78),
        }
    )
    return materials


def cylinder_between(name, start, end, radius, material, target):
    a = Vector(start)
    b = Vector(end)
    direction = b - a
    obj = add_cylinder(name, tuple((a + b) * 0.5), radius, direction.length, material, target, 24)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    obj.rotation_mode = "XYZ"
    return obj


def add_bench(prefix, x, y, materials, visible):
    objects = []
    for slat in range(4):
        objects.append(
            add_box(
                f"{prefix}_SeatSlat_{slat:02d}",
                (x, y - 0.48 + slat * 0.32, 1.12),
                (2.55, 0.22, 0.09),
                materials["wood"],
                visible,
                0.025,
            )
        )
    for slat in range(4):
        objects.append(
            add_box(
                f"{prefix}_BackSlat_{slat:02d}",
                (x, y + 0.72, 1.38 + slat * 0.22),
                (2.55, 0.09, 0.13),
                materials["wood"],
                visible,
                0.025,
            )
        )
    for side in (-0.92, 0.92):
        objects.append(add_box(f"{prefix}_Leg_{side:+.2f}", (x + side, y, 0.89), (0.12, 0.72, 0.52), materials["metal"], visible, 0.025))
        objects.append(cylinder_between(f"{prefix}_BackSupport_{side:+.2f}", (x + side, y + 0.52, 0.93), (x + side, y + 0.72, 2.02), 0.055, materials["metal"], visible))
    return objects


def add_lamp(prefix, x, y, materials, visible):
    objects = [
        add_cylinder(f"{prefix}_Foot", (x, y, 0.84), 0.30, 0.16, materials["metal"], visible, 28),
        add_cylinder(f"{prefix}_Pole", (x, y, 3.30), 0.075, 5.0, materials["paint"], visible, 24),
        cylinder_between(f"{prefix}_Arm", (x, y, 5.76), (x + 0.78, y, 5.98), 0.065, materials["paint"], visible),
        add_box(f"{prefix}_Head", (x + 0.94, y, 5.94), (0.52, 0.25, 0.14), materials["metal"], visible, 0.045),
    ]
    return objects


def add_tree_pit(prefix, x, y, materials, visible):
    objects = [
        add_box(f"{prefix}_Soil", (x, y, 0.785), (2.15, 2.15, 0.055), materials["soil"], visible, 0.02),
        add_box(f"{prefix}_FrameN", (x, y + 1.10, 0.83), (2.35, 0.12, 0.10), materials["metal"], visible, 0.02),
        add_box(f"{prefix}_FrameS", (x, y - 1.10, 0.83), (2.35, 0.12, 0.10), materials["metal"], visible, 0.02),
        add_box(f"{prefix}_FrameE", (x + 1.10, y, 0.83), (0.12, 2.08, 0.10), materials["metal"], visible, 0.02),
        add_box(f"{prefix}_FrameW", (x - 1.10, y, 0.83), (0.12, 2.08, 0.10), materials["metal"], visible, 0.02),
    ]
    return objects


def refined_build_corridor(materials, visible, collision, sockets, review):
    result = ORIGINAL_BUILD_CORRIDOR(materials, visible, collision, sockets, review)
    objects = result["objects"]

    continuous_foam = bpy.data.objects.get("SM_M01_C06_FoamContactGuide")
    if continuous_foam is not None:
        mesh = continuous_foam.data
        bpy.data.objects.remove(continuous_foam, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

    # Broken, irregular contact patches avoid the rejected bright continuous line.
    foam_ranges = ((-36.0, 18.0), (34.0, 83.0), (112.0, 169.0), (196.0, 244.0), (279.0, 335.0), (365.0, 421.0), (451.0, 516.0))
    for patch_index, (start, end) in enumerate(foam_ranges):
        count = max(2, int((end - start) / 4.0))
        vertices = []
        for sample in range(count + 1):
            x = start + (end - start) * sample / count
            y = shoreline_y(x)
            width = 0.26 + 0.18 * (0.5 + 0.5 * math.sin(x / 7.7 + patch_index))
            vertices.extend(((x, y - width, -0.43), (x, y + width, -0.42)))
        faces = [(index * 2, index * 2 + 1, index * 2 + 3, index * 2 + 2) for index in range(count)]
        objects.append(add_mesh(f"SM_M01_C06R01_FoamPatch_{patch_index:02d}", vertices, faces, materials["foam"], visible))

    cross_streets = (60.0, 160.0, 260.0, 360.0, 460.0)
    half_width = 5.4

    # Curb faces close every height discontinuity that previously exposed sky-blue seams.
    add_box("SM_M01_C06R01_SeawardRoadCurb", (250.0, 85.87, 0.67), (580.0, 0.34, 0.27), materials["concrete"], visible, 0.035)
    inland_segments = [(-40.0, 54.6), (65.4, 154.6), (165.4, 254.6), (265.4, 354.6), (365.4, 454.6), (465.4, 540.0)]
    for index, (start, end) in enumerate(inland_segments):
        objects.append(add_box(f"SM_M01_C06R01_InlandRoadCurb_{index:02d}", ((start + end) * 0.5, 100.15, 0.70), (end - start, 0.34, 0.29), materials["concrete"], visible, 0.035))
    for street_index, center in enumerate(cross_streets):
        for side_index, x in enumerate((center - half_width, center + half_width)):
            objects.append(add_box(f"SM_M01_C06R01_CrossStreetCurb_{street_index:02d}_{side_index}", (x, 149.5, 0.70), (0.30, 91.0, 0.30), materials["concrete"], visible, 0.035))
        for stripe in range(6):
            objects.append(add_box(f"SM_M01_C06R01_Crosswalk_{street_index:02d}_{stripe:02d}", (center - 4.1 + stripe * 1.64, 103.1, 0.645), (0.72, 3.9, 0.025), materials["marking"], visible, 0.012))
        objects.append(add_box(f"SM_M01_C06R01_TactilePad_{street_index:02d}_L", (center - half_width - 0.82, 102.55, 0.84), (1.25, 1.15, 0.055), materials["tactile"], visible, 0.02))
        objects.append(add_box(f"SM_M01_C06R01_TactilePad_{street_index:02d}_R", (center + half_width + 0.82, 102.55, 0.84), (1.25, 1.15, 0.055), materials["tactile"], visible, 0.02))

    for bench_index, x in enumerate((8.0, 102.0, 198.0, 302.0, 405.0, 505.0)):
        objects.extend(add_bench(f"SM_M01_C06R01_Bench_{bench_index:02d}", x, 82.65, materials, visible))
    for lamp_index, x in enumerate((-18.0, 38.0, 94.0, 151.0, 209.0, 268.0, 328.0, 389.0, 451.0, 515.0)):
        objects.extend(add_lamp(f"SM_M01_C06R01_Lamp_{lamp_index:02d}", x, 83.15, materials, visible))

    pit_positions = ((20.0, 112.0), (83.0, 116.0), (124.0, 112.0), (183.0, 116.0), (222.0, 112.0), (286.0, 116.0), (326.0, 112.0), (389.0, 116.0), (425.0, 112.0), (505.0, 116.0))
    for pit_index, (x, y) in enumerate(pit_positions):
        objects.extend(add_tree_pit(f"SM_M01_C06R01_TreePit_{pit_index:02d}", x, y, materials, visible))

    for cabinet_index, (x, y, height) in enumerate(((35.0, 108.5, 1.55), (138.0, 109.0, 1.35), (238.0, 108.5, 1.75), (338.0, 109.0, 1.45), (438.0, 108.5, 1.65))):
        objects.append(add_box(f"SM_M01_C06R01_UtilityCabinet_{cabinet_index:02d}", (x, y, 0.76 + height * 0.5), (1.05, 0.58, height), materials["paint"], visible, 0.065))
        objects.append(add_box(f"SM_M01_C06R01_UtilityCabinet_{cabinet_index:02d}_Door", (x, y - 0.305, 0.76 + height * 0.54), (0.78, 0.035, height * 0.72), materials["metal"], visible, 0.018))
        objects.append(add_cylinder(f"SM_M01_C06R01_UtilityCabinet_{cabinet_index:02d}_Latch", (x + 0.28, y - 0.34, 0.76 + height * 0.58), 0.035, 0.07, materials["drain"], visible, 18))

    # Sparse dune fencing provides parallax and scale while remaining a built
    # environment detail; Unreal still owns all vegetation.
    for fence_index, start_x in enumerate((18.0, 150.0, 318.0, 468.0)):
        y_base = boundary_profile(start_x)["dry_end"] + 4.8
        for post in range(5):
            x = start_x + post * 3.2
            z_ground = boundary_height(x, "dry_end") + 0.15
            objects.append(add_box(f"SM_M01_C06R01_DuneFence_{fence_index:02d}_Post_{post:02d}", (x, y_base, z_ground + 0.78), (0.10, 0.10, 1.56), materials["wood"], visible, 0.018))
        for rail in (0.58, 1.05):
            objects.append(add_box(f"SM_M01_C06R01_DuneFence_{fence_index:02d}_Rail_{rail:.2f}", (start_x + 6.4, y_base, z_ground + rail), (13.0, 0.075, 0.10), materials["wood"], visible, 0.018))

    result["objects"] = objects
    result["authored_detail_groups"] = {
        "benches": 6,
        "lamps": 10,
        "tree_pits": 10,
        "utility_cabinets": 5,
        "crosswalks": 5,
        "foam_patches": len(foam_ranges),
        "dune_fence_sections": 4,
    }
    return result


namespace["create_band"] = refined_create_band
namespace["create_review_ocean"] = refined_create_review_ocean
namespace["build_materials"] = refined_build_materials
namespace["build_corridor"] = refined_build_corridor


if __name__ == "__main__":
    raise SystemExit(namespace["main"]())
