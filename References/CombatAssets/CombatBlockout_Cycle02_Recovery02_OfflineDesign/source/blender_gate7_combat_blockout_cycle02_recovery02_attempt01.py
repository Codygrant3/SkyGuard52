from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


GATE = "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY02_ATTEMPT01"


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        pass
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)


def collection(name: str, classification: str) -> bpy.types.Collection:
    value = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(value)
    value["gate"] = GATE
    value["classification"] = classification
    value["provisional"] = True
    return value


def material(name: str, color: tuple[float, float, float, float], metallic: float = 0.0, roughness: float = 0.55):
    value = bpy.data.materials.new(name)
    value.diffuse_color = color
    value.use_nodes = True
    bsdf = value.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return value


def move_to_collection(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)


def box(name: str, size: tuple[float, float, float], location: tuple[float, float, float], target, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("PROVISIONAL_EdgeSoftening", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    obj.data.materials.append(mat)
    obj["provisional"] = True
    move_to_collection(obj, target)
    return obj


def cylinder_x(name: str, length: float, radius: float, location, target, mat, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=location, rotation=(0, math.pi / 2, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj["provisional"] = True
    move_to_collection(obj, target)
    return obj


def sphere(name: str, radius: float, scale: tuple[float, float, float], location, target, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    obj["provisional"] = True
    move_to_collection(obj, target)
    return obj


def torus_y(name: str, major: float, minor: float, location, target, mat):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major,
        minor_radius=minor,
        major_segments=40,
        minor_segments=10,
        location=location,
        rotation=(math.pi / 2, 0, 0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj["provisional"] = True
    move_to_collection(obj, target)
    return obj


def prism_x(name: str, x_length: float, width_bottom: float, width_top: float, z_bottom: float, z_top: float, x: float, target, mat):
    x0, x1 = x - x_length / 2, x + x_length / 2
    yb, yt = width_bottom / 2, width_top / 2
    verts = [
        (x0, -yb, z_bottom), (x0, yb, z_bottom), (x0, -yt, z_top), (x0, yt, z_top),
        (x1, -yb, z_bottom), (x1, yb, z_bottom), (x1, -yt, z_top), (x1, yt, z_top),
    ]
    faces = [(0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5)]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    obj.data.materials.append(mat)
    obj["provisional"] = True
    return obj


def empty(name: str, location, target, role: str):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "ARROWS"
    obj.empty_display_size = 0.08
    obj.location = location
    obj["role"] = role
    obj["provisional"] = True
    target.objects.link(obj)
    return obj


def build_rail(mat):
    coll = collection("PROVISIONAL_MIL_STD_1913_VALIDATION_COUPON", "PASSED_PROVISIONAL_BLOCKOUT")
    length = 0.120
    top_width = 0.021209
    dovetail_width = 0.018999
    lower_width = 0.015672
    profile_height = 0.009322
    base_height = 0.004
    groove_width = 0.005232
    pitch = 0.010008
    tooth_length = pitch - groove_width
    box("RAIL_Base", (length, lower_width, base_height), (0, 0, base_height / 2), coll, mat, 0.0004)
    count = int(length / pitch)
    start = -((count - 1) * pitch) / 2
    for index in range(count):
        prism_x(
            f"RAIL_Tooth_{index:02d}",
            tooth_length,
            dovetail_width,
            top_width,
            base_height,
            profile_height,
            start + index * pitch,
            coll,
            mat,
        )
    coll["authoritative_top_width_mm"] = 21.209
    coll["authoritative_dovetail_width_mm"] = 18.999
    coll["authoritative_lower_width_mm"] = 15.672
    coll["authoritative_profile_height_min_mm"] = 9.322
    coll["authoritative_groove_width_mm"] = 5.232
    coll["authoritative_pitch_mm"] = 10.008
    coll["scope"] = "validation coupon only; not a final rifle component"
    empty("SOCKET_Rail_Origin", (0, 0, 0), coll, "validation origin")
    return coll


def build_rifle(metal, fde, dark):
    coll = collection("PROVISIONAL_AR_M4_FAMILY_RIFLE_BLOCKOUT", "PASSED_PROVISIONAL_BLOCKOUT")
    coll["identity"] = "AR/M4 family only; exact configuration unresolved"
    coll["non_authoritative_overall_scale"] = True
    receiver = box("RIFLE_PROVISIONAL_ReceiverVolume", (0.205, 0.060, 0.075), (-0.205, 0, 0.0), coll, dark, 0.006)
    receiver["detail_prohibited"] = "controls, markings, magazine, chambering and manufacturer"
    handguard_start, handguard_end = -0.105, 0.235
    handguard_length = handguard_end - handguard_start
    for y, z, name in [
        (-0.032, 0.025, "LeftUpper"), (0.032, 0.025, "RightUpper"),
        (-0.032, -0.025, "LeftLower"), (0.032, -0.025, "RightLower"),
    ]:
        box(f"RIFLE_HandguardRail_{name}", (handguard_length, 0.010, 0.010), ((handguard_start + handguard_end) / 2, y, z), coll, fde, 0.002)
    for index in range(8):
        x = handguard_start + 0.018 + index * (handguard_length - 0.036) / 7
        box(f"RIFLE_HandguardRib_{index:02d}", (0.012, 0.072, 0.066), (x, 0, 0), coll, fde, 0.003)
    rail_length = 0.50
    rail_start = -0.29
    for index in range(35):
        x = rail_start + index * rail_length / 34
        box(f"RIFLE_TopRailTooth_{index:02d}", (0.009, 0.024, 0.009), (x, 0, 0.054), coll, fde, 0.0008)
    box("RIFLE_TopRailSpine", (rail_length, 0.020, 0.007), (rail_start + rail_length / 2, 0, 0.046), coll, fde, 0.001)
    cylinder_x("RIFLE_PROVISIONAL_BarrelVolume", 0.245, 0.009, (0.3575, 0, 0), coll, metal)
    cylinder_x("RIFLE_MuzzleCollar", 0.030, 0.015, (0.495, 0, 0), coll, metal)
    for angle in (-0.48, -0.16, 0.16, 0.48):
        prong = cylinder_x("RIFLE_PROVISIONAL_MuzzleProng", 0.050, 0.0032, (0.535, math.sin(angle) * 0.008, math.cos(angle) * 0.008), coll, metal, 20)
        prong["exact_tine_count_unresolved"] = True
    torus_y("RIFLE_PROVISIONAL_RearAperture", 0.013, 0.0025, (-0.14, 0, 0.081), coll, metal)
    empty("SOCKET_Rifle_MuzzleAxis_PROVISIONAL", (0.565, 0, 0), coll, "muzzle axis provisional")
    empty("SOCKET_Rifle_ADSRear_PROVISIONAL", (-0.14, 0, 0.081), coll, "rear sight provisional")
    empty("SOCKET_Rifle_ADSFront_PROVISIONAL", (0.23, 0, 0.081), coll, "front sight location provisional")
    empty("SOCKET_Rifle_SupportHand_PROVISIONAL", (0.05, -0.04, -0.02), coll, "support hand provisional")
    empty("SOCKET_Rifle_TriggerHand_PROVISIONAL", (-0.22, -0.04, -0.02), coll, "trigger hand provisional")
    return coll


def build_missile(mat, accent):
    coll = collection("PROVISIONAL_9K38_MISSILE_ENVELOPE", "PASSED_PROVISIONAL_BLOCKOUT")
    body = cylinder_x("IGLA_9K38_AuthoritativeEnvelope", 1.574, 0.036, (0, 0, 0), coll, mat, 64)
    body["authoritative_length_mm"] = 1574.0
    body["authoritative_body_diameter_mm"] = 72.0
    body["not_final_geometry"] = True
    cylinder_x("IGLA_FrontMeasurementDisc", 0.003, 0.040, (0.7855, 0, 0), coll, accent, 48)
    cylinder_x("IGLA_RearMeasurementDisc", 0.003, 0.040, (-0.7855, 0, 0), coll, accent, 48)
    empty("SOCKET_IglaMissile_ForwardOrigin_PROVISIONAL", (0.787, 0, 0), coll, "forward end")
    empty("SOCKET_IglaMissile_RearAxis_PROVISIONAL", (-0.787, 0, 0), coll, "rear axis")
    coll["prohibited"] = "launcher, gripstock, battery, sight, caps, bands, fasteners and markings"
    return coll


def build_hand(glove, sleeve):
    coll = collection("PROVISIONAL_REAR_GUNNER_HAND_FOREARM_MANNEQUIN", "PASSED_PROVISIONAL_BLOCKOUT")
    coll["profile"] = "replaceable project mannequin; not a measured percentile"
    coll["selected_hand_length_mm"] = 190.0
    coll["selected_hand_breadth_mm"] = 85.0
    coll["selected_forearm_plus_hand_mm"] = 460.0
    cylinder_x("HAND_Forearm", 0.270, 0.045, (-0.23, 0, 0), coll, sleeve, 40)
    sphere("HAND_Wrist", 0.05, (1.1, 0.85, 0.85), (-0.075, 0, 0), coll, glove)
    box("HAND_Palm", (0.105, 0.085, 0.032), (0.015, 0, 0), coll, glove, 0.014)
    finger_y = [-0.032, -0.011, 0.011, 0.032]
    finger_lengths = [0.072, 0.082, 0.078, 0.064]
    for index, (y, length) in enumerate(zip(finger_y, finger_lengths)):
        cylinder_x(f"HAND_Finger_{index + 1}", length, 0.010, (0.065 + length / 2, y, 0), coll, glove, 24)
        sphere(f"HAND_FingerTip_{index + 1}", 0.010, (1.0, 1.0, 1.0), (0.065 + length, y, 0), coll, glove)
    thumb = cylinder_x("HAND_Thumb", 0.060, 0.012, (0.045, -0.052, -0.004), coll, glove, 24)
    thumb.rotation_euler[2] = math.radians(-35)
    box("HAND_KnucklePad", (0.055, 0.070, 0.009), (0.015, 0, 0.022), coll, glove, 0.004)
    empty("SOCKET_Hand_GripCenter_PROVISIONAL", (0.07, 0, 0), coll, "grip center")
    empty("SOCKET_Hand_Wrist_PROVISIONAL", (-0.075, 0, 0), coll, "wrist")
    coll["nasa_bounds_mm"] = json.dumps(
        {
            "hand_length": [158, 221],
            "hand_breadth": [71, 102],
            "hand_circumference": [168, 241],
            "forearm_hand_length": [387, 546],
        }
    )
    return coll


def build_shahed(mat, edge):
    coll = collection("PROVISIONAL_SHAHED136_ENVELOPE", "PASSED_PROVISIONAL_BLOCKOUT")
    verts = [
        (1.65, 0.0, 0.0),
        (-0.55, 1.50, 0.0),
        (-1.65, 0.55, 0.0),
        (-1.65, -0.55, 0.0),
        (-0.55, -1.50, 0.0),
    ]
    mesh = bpy.data.meshes.new("SHAHED_EnvelopePlanform_Mesh")
    mesh.from_pydata(verts, [], [(0, 1, 2, 3, 4)])
    mesh.update()
    obj = bpy.data.objects.new("SHAHED_OfficialReportedPlanform", mesh)
    coll.objects.link(obj)
    obj.data.materials.append(mat)
    obj["authoritative_length_mm"] = 3300.0
    obj["authoritative_wingspan_mm"] = 3000.0
    obj["cross_section_unknown"] = True
    for x, y, length, rotation in [
        (0, 0, 3.30, 0),
        (-0.55, 0, 3.00, math.pi / 2),
    ]:
        line = box("SHAHED_DimensionGuide", (length, 0.012, 0.012), (x, y, 0.025), coll, edge, 0.002)
        line.rotation_euler[2] = rotation
    empty("SOCKET_Shahed_DamageCore_PROVISIONAL", (0, 0, 0), coll, "damage core provisional")
    empty("SOCKET_Shahed_WingL_PROVISIONAL", (-0.55, 1.5, 0), coll, "left wing tip")
    empty("SOCKET_Shahed_WingR_PROVISIONAL", (-0.55, -1.5, 0), coll, "right wing tip")
    coll["prohibited"] = "airfoil, thickness, cross-sections, propeller and internal dimensions"
    return coll


def bbox_for_collection(coll: bpy.types.Collection) -> dict[str, list[float]]:
    points = []
    for obj in coll.all_objects:
        if obj.type != "MESH":
            continue
        points.extend([obj.matrix_world @ Vector(corner) for corner in obj.bound_box])
    low = [min(p[i] for p in points) for i in range(3)]
    high = [max(p[i] for p in points) for i in range(3)]
    size = [high[i] - low[i] for i in range(3)]
    return {"min_m": low, "max_m": high, "size_m": size}


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_render_stage():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.035, 0.045, 0.065)
    bpy.ops.object.light_add(type="AREA", location=(3.5, -4.0, 5.0))
    key = bpy.context.object
    key.name = "RENDER_Key"
    key.data.energy = 1000
    key.data.shape = "DISK"
    key.data.size = 4.0
    look_at(key, (0, 0, 0))
    bpy.ops.object.light_add(type="AREA", location=(-4.0, -1.0, 2.0))
    fill = bpy.context.object
    fill.name = "RENDER_Fill"
    fill.data.energy = 650
    fill.data.size = 3.0
    look_at(fill, (0, 0, 0))
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "RENDER_Camera"
    camera.data.type = "ORTHO"
    scene.camera = camera
    return camera, [key, fill]


def render_collection(coll, camera, lights, output: Path, camera_location, ortho_scale):
    for candidate in bpy.data.collections:
        if candidate.name.startswith("PROVISIONAL_"):
            candidate.hide_render = candidate != coll
    camera.location = camera_location
    camera.data.ortho_scale = ortho_scale
    look_at(camera, (0, 0, 0))
    bpy.context.scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)


def export_collection(coll, output: Path):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in coll.all_objects:
        if obj.type in {"MESH", "EMPTY"}:
            obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_extras=True,
    )


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    renders = output / "renders"
    exports = output / "exports"
    renders.mkdir()
    exports.mkdir()

    clear_scene()
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "METERS"
    bpy.context.scene.unit_settings.scale_length = 1.0

    metal = material("MAT_PROVISIONAL_Gunmetal", (0.12, 0.15, 0.18, 1), 0.65, 0.30)
    fde = material("MAT_PROVISIONAL_FDE", (0.47, 0.29, 0.13, 1), 0.10, 0.48)
    dark = material("MAT_PROVISIONAL_DarkPolymer", (0.035, 0.045, 0.055, 1), 0.0, 0.62)
    olive = material("MAT_PROVISIONAL_IglaOlive", (0.24, 0.29, 0.12, 1), 0.25, 0.50)
    orange = material("MAT_PROVISIONAL_Measurement", (0.95, 0.30, 0.035, 1), 0.0, 0.35)
    glove = material("MAT_PROVISIONAL_Glove", (0.028, 0.035, 0.045, 1), 0.0, 0.78)
    sleeve = material("MAT_PROVISIONAL_Sleeve", (0.18, 0.23, 0.13, 1), 0.0, 0.86)
    shahed_mat = material("MAT_PROVISIONAL_ShahedEnvelope", (0.22, 0.25, 0.20, 1), 0.10, 0.64)

    assets = [
        build_rail(metal),
        build_rifle(metal, fde, dark),
        build_missile(olive, orange),
        build_hand(glove, sleeve),
        build_shahed(shahed_mat, orange),
    ]

    camera, lights = setup_render_stage()
    render_specs = {
        "PROVISIONAL_MIL_STD_1913_VALIDATION_COUPON": ((0.18, -0.18, 0.14), 0.17),
        "PROVISIONAL_AR_M4_FAMILY_RIFLE_BLOCKOUT": ((0.90, -0.95, 0.50), 0.80),
        "PROVISIONAL_9K38_MISSILE_ENVELOPE": ((1.80, -1.80, 0.80), 1.85),
        "PROVISIONAL_REAR_GUNNER_HAND_FOREARM_MANNEQUIN": ((0.85, -0.80, 0.50), 0.70),
        "PROVISIONAL_SHAHED136_ENVELOPE": ((4.20, -4.20, 4.00), 4.00),
    }

    dimensions = {}
    artifacts = []
    for coll in assets:
        render_path = renders / f"{coll.name}.png"
        export_path = exports / f"{coll.name}.glb"
        camera_location, scale = render_specs[coll.name]
        render_collection(coll, camera, lights, render_path, camera_location, scale)
        export_collection(coll, export_path)
        dimensions[coll.name] = bbox_for_collection(coll)
        artifacts.extend([render_path, export_path])

    blend_path = output / f"{GATE}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    artifacts.append(blend_path)

    receipt = {
        "gate": GATE,
        "blender_version": bpy.app.version_string,
        "classification": {coll.name: coll["classification"] for coll in assets},
        "units": "metres",
        "dimensions": dimensions,
        "authoritative_validations": {
            "9K38_missile": {"expected_length_m": 1.574, "expected_diameter_m": 0.072},
            "Shahed136": {"expected_length_m": 3.3, "expected_wingspan_m": 3.0},
            "MIL_STD_1913": {
                "top_width_m": 0.021209,
                "dovetail_width_m": 0.018999,
                "profile_height_min_m": 0.009322,
                "groove_width_m": 0.005232,
                "pitch_m": 0.010008,
            },
            "hand_mannequin": {
                "selected_hand_length_m": 0.190,
                "selected_hand_breadth_m": 0.085,
                "selected_forearm_plus_hand_m": 0.460,
                "claim": "project blockout only; not a measured percentile",
            },
        },
        "prohibited_claims": [
            "exact rifle make/model, chambering or accessory configuration",
            "final Igla launcher or missile detail",
            "measured character percentile",
            "Shahed airfoil, cross-section, propeller or internal dimensions",
        ],
        "artifacts": [],
    }
    for path in artifacts:
        receipt["artifacts"].append(
            {
                "path": path.relative_to(output).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    (output / "dimension_and_artifact_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    terminal = {
        "gate": GATE,
        "status": "BLENDER_COMPLETED_AWAITING_EXTERNAL_VALIDATION",
        "blender_version": bpy.app.version_string,
        "collections": [coll.name for coll in assets],
        "render_count": len(list(renders.glob("*.png"))),
        "export_count": len(list(exports.glob("*.glb"))),
    }
    (output / "terminal_receipt.json").write_text(json.dumps(terminal, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(terminal, indent=2))


if __name__ == "__main__":
    main()
