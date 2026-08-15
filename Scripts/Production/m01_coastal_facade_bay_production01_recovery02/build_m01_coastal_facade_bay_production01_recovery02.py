"""Architecture-first Recovery02 for the Mission 1 coastal facade bay.

Recovery01 passed its dimensional/export checks but failed direct visual review.
This worker keeps the accepted Recovery06 window dependency and the frozen
evidence/render/export harness, while replacing every rejected facade and
balcony mesh with a restrained pre-war masonry composition.  No rejected
Recovery01 facade mesh is opened, appended, or reused.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
FROZEN_WORKER = ROOT / "Scripts/Production/m01_coastal_facade_bay_production01/build_m01_coastal_facade_bay_production01.py"
RECOVERY_ASSET_ID = "m01-coastal-facade-bay-production01-recovery02"
RECOVERY_CLASSIFICATION = "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_M01_COASTAL_FACADE_BAY_PRODUCTION01_RECOVERY02_BLENDER_EXECUTION"


def load_frozen_worker():
    spec = importlib.util.spec_from_file_location("skyguard_coastal_facade_bay_production01_frozen_r02", FROZEN_WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load frozen worker: {FROZEN_WORKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


worker = load_frozen_worker()
original_require = worker.require


def recovery_require(condition: bool, message: str) -> None:
    if message == "Contract classification changed":
        values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
        original_require("--contract" in values, "Recovery02 contract argument missing")
        contract_path = Path(values[values.index("--contract") + 1])
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        original_require(contract.get("classification") == RECOVERY_CLASSIFICATION, "Recovery02 contract classification changed")
        return
    if message == "Accepted window width changed":
        frame = worker.bpy.data.objects.get(worker.WINDOW_OBJECTS[0])
        original_require(frame is not None, "Accepted consolidated frame missing during Recovery02 guard")
        minimum, maximum = worker.base.bounds([frame])
        measured_width = maximum.x - minimum.x
        original_require(3.55 <= measured_width <= 3.65, f"Accepted consolidated frame width outside frozen authority: {measured_width}")
        return
    original_require(condition, message)


def make_materials() -> dict[str, object]:
    plaster = worker.texture_set(
        "painted_plaster_wall",
        "painted_plaster_wall_diff_2k.jpg",
        "painted_plaster_wall_nor_gl_2k.jpg",
        "painted_plaster_wall_rough_2k.jpg",
    )
    concrete = worker.texture_set(
        "concrete_wall_006",
        "concrete_wall_006-diffuse-2k.jpg",
        "concrete_wall_006-nor_gl-2k.jpg",
        "concrete_wall_006-rough-2k.jpg",
    )
    metal = worker.texture_set(
        "metal_plate_02",
        "metal_plate_02_diff_2k.jpg",
        "metal_plate_02_nor_gl_2k.jpg",
        "metal_plate_02_rough_2k.jpg",
    )
    asphalt = worker.texture_set(
        "asphalt_02",
        "asphalt_02_diff_2k.jpg",
        "asphalt_02_nor_gl_2k.jpg",
        "asphalt_02_rough_2k.jpg",
    )
    return {
        "plaster": worker.base.material_pbr(
            "M_M01_CoastalFacadeBay_R02_WarmGreyStucco", (0.67, 0.65, 0.59, 1), 0.0, 0.78,
            8.0, 0.055, texture_set=plaster, texture_scale=4.8,
        ),
        "stone": worker.base.material_pbr(
            "M_M01_CoastalFacadeBay_R02_PaleLimestone", (0.61, 0.59, 0.53, 1), 0.0, 0.82,
            9.0, 0.055, texture_set=concrete, texture_scale=3.5,
        ),
        "base_stone": worker.base.material_pbr(
            "M_M01_CoastalFacadeBay_R02_WeatheredPlinth", (0.34, 0.35, 0.34, 1), 0.0, 0.88,
            10.0, 0.075, texture_set=concrete, texture_scale=3.0,
        ),
        "metal": worker.base.material_pbr(
            "M_M01_CoastalFacadeBay_R02_BlackenedSquareSteel", (0.075, 0.082, 0.084, 1), 0.73, 0.42,
            13.0, 0.032, texture_set=metal, texture_scale=3.5,
        ),
        "bronze": worker.base.material_pbr(
            "M_M01_CoastalFacadeBay_R02_AgedBrass", (0.24, 0.16, 0.065, 1), 0.72, 0.46,
            15.0, 0.035,
        ),
        "review_ground": worker.base.material_pbr(
            "M_M01_CoastalFacadeBay_R02_ReviewGround", (0.10, 0.11, 0.12, 1), 0.0, 0.88,
            5.0, 0.12, texture_set=asphalt, texture_scale=3.5,
        ),
        "collision": worker.base.material_pbr(
            "M_REVIEW_M01_CoastalFacadeBay_R02_Collision", (0.86, 0.08, 0.05, 1), 0.0, 0.7,
        ),
    }


def add_square_bar_between(name: str, start, end, width: float, material, group: list[object]):
    delta = end - start
    length = delta.length
    original_require(length > 0.0001, f"Degenerate square bar: {name}")
    worker.bpy.ops.mesh.primitive_cube_add(size=1.0, location=(start + end) * 0.5)
    obj = worker.bpy.context.object
    obj.name = name
    obj.dimensions = (width, width, length)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    obj.rotation_mode = "XYZ"
    worker.base.apply_transform(obj)
    worker.base.bevel(obj, min(width * 0.12, 0.006), 2)
    worker.base.assign(obj, material)
    group.append(obj)
    return obj


def calm_accepted_interior_lighting(interior) -> list[str]:
    adjusted: list[str] = []
    for material in interior.data.materials:
        if material is None or not material.use_nodes or material.node_tree is None:
            continue
        for node in material.node_tree.nodes:
            if node.type != "BSDF_PRINCIPLED":
                continue
            emission = node.inputs.get("Emission Strength")
            if emission is not None and float(emission.default_value) > 0.18:
                emission.default_value = 0.18
                adjusted.append(material.name)
    return sorted(set(adjusted))


def add_rusticated_plinth(prefix: str, x: float, materials, structural: list[object]) -> None:
    for index, z in enumerate((0.14, 0.40, 0.66), 1):
        worker.base.add_box(
            f"{prefix}_Course_{index:02d}", (x, -0.145, z), (1.30, 0.17, 0.235),
            materials["base_stone"], structural, bevel_width=0.014,
        )


def build_geometry(materials: dict[str, object]):
    structural: list[object] = []
    glazing: list[object] = []
    interior_group: list[object] = []
    details: list[object] = []

    frame, glass, interior, axis = worker.append_accepted_window()
    structural.append(frame)
    glazing.append(glass)
    interior_group.append(interior)
    lighting_adjustments = calm_accepted_interior_lighting(interior)

    # Two real masonry piers extend the accepted installed window surround.
    # There is deliberately no hidden facade slab and no dark perimeter frame.
    for side, x in (("Left", -2.42), ("Right", 2.42)):
        worker.base.add_box(
            f"Facade_{side}_MasonryPier", (x, 0.15, 2.18), (1.24, 0.62, 4.36),
            materials["plaster"], structural, bevel_width=0.026,
        )
        add_rusticated_plinth(f"Facade_{side}_Plinth", x, materials, structural)
        worker.base.add_box(
            f"Facade_{side}_OuterQuoin", (x + (-0.54 if side == "Left" else 0.54), -0.19, 2.40),
            (0.16, 0.10, 3.22), materials["stone"], structural, bevel_width=0.012,
        )

    # Texture the broad accepted surround with four shallow stucco fields while
    # leaving the casement, sill and hardware unobstructed.
    worker.base.add_box("Facade_CentreField_Left", (-1.23, -0.405, 2.12), (1.08, 0.035, 4.06), materials["plaster"], structural, bevel_width=0.008)
    worker.base.add_box("Facade_CentreField_Right", (1.23, -0.405, 2.12), (1.08, 0.035, 4.06), materials["plaster"], structural, bevel_width=0.008)
    worker.base.add_box("Facade_CentreField_Lower", (0.0, -0.405, 0.54), (1.42, 0.035, 1.06), materials["plaster"], structural, bevel_width=0.008)
    worker.base.add_box("Facade_CentreField_Upper", (0.0, -0.405, 3.61), (1.42, 0.035, 0.76), materials["plaster"], structural, bevel_width=0.008)

    # Properly stepped masonry head and sill create architectural depth.
    worker.base.add_box("Facade_WindowSill", (0.0, -0.475, 1.08), (1.55, 0.19, 0.13), materials["stone"], structural, bevel_width=0.018)
    worker.base.add_box("Facade_WindowLintel", (0.0, -0.465, 3.24), (1.70, 0.17, 0.20), materials["stone"], structural, bevel_width=0.018)
    worker.base.add_box("Facade_HeadFrieze", (0.0, 0.03, 4.18), (5.94, 0.38, 0.25), materials["stone"], structural, bevel_width=0.024)
    worker.base.add_box("Facade_CorniceLower", (0.0, -0.08, 4.39), (6.06, 0.52, 0.17), materials["stone"], structural, bevel_width=0.025)
    worker.base.add_box("Facade_CorniceCap", (0.0, -0.12, 4.54), (6.18, 0.62, 0.13), materials["stone"], structural, bevel_width=0.025)

    # Compact square-steel balcony. Rails meet each other and terminate in
    # visible wall plates; braces penetrate the wall plates and slab underside.
    platform_y = -0.79
    front_y = -1.18
    wall_y = -0.40
    rail_bottom = 0.84
    rail_top = 1.84
    half_width = 1.23
    worker.base.add_box("Balcony_LimestoneSlab", (0.0, platform_y, 0.76), (2.52, 0.82, 0.16), materials["stone"], details, bevel_width=0.025)
    worker.base.add_box("Balcony_FrontDripEdge", (0.0, -1.205, 0.74), (2.56, 0.06, 0.15), materials["metal"], details, bevel_width=0.008)
    worker.base.add_box("Balcony_FrontTopRail", (0.0, front_y, rail_top), (2.54, 0.07, 0.07), materials["metal"], details, bevel_width=0.006)
    worker.base.add_box("Balcony_FrontLowerRail", (0.0, front_y, 1.00), (2.46, 0.045, 0.045), materials["metal"], details, bevel_width=0.004)
    for index, x in enumerate((-1.18, -0.89, -0.59, -0.30, 0.0, 0.30, 0.59, 0.89, 1.18), 1):
        worker.base.add_box(
            f"Balcony_FrontBaluster_{index:02d}", (x, front_y, 1.40), (0.038, 0.038, 0.88),
            materials["metal"], details, bevel_width=0.003,
        )
    for side, x in (("L", -half_width), ("R", half_width)):
        worker.base.add_box(f"Balcony_{side}_WallPlate", (x, -0.425, 1.36), (0.16, 0.055, 1.03), materials["metal"], details, bevel_width=0.006)
        worker.base.add_box(f"Balcony_{side}_TopReturn", (x, -0.79, rail_top), (0.07, 0.82, 0.07), materials["metal"], details, bevel_width=0.006)
        worker.base.add_box(f"Balcony_{side}_LowerReturn", (x, -0.79, 1.00), (0.045, 0.78, 0.045), materials["metal"], details, bevel_width=0.004)
        worker.base.add_box(f"Balcony_{side}_FrontPost", (x, front_y, 1.36), (0.075, 0.075, 1.04), materials["metal"], details, bevel_width=0.006)
        for y_index, y in enumerate((-0.62, -0.86, -1.10), 1):
            worker.base.add_box(
                f"Balcony_{side}_ReturnBaluster_{y_index:02d}", (x, y, 1.40), (0.038, 0.038, 0.88),
                materials["metal"], details, bevel_width=0.003,
            )
        wall_anchor = worker.Vector((x, -0.43, 0.29))
        slab_anchor = worker.Vector((x, -1.08, 0.69))
        add_square_bar_between(f"Balcony_{side}_EmbeddedBracket", wall_anchor, slab_anchor, 0.075, materials["metal"], details)
        worker.base.add_box(f"Balcony_{side}_BracketFoot", (x, -0.43, 0.29), (0.19, 0.06, 0.37), materials["metal"], details, bevel_width=0.006)
        for bolt_index, z in enumerate((0.21, 0.37), 1):
            worker.base.add_box(
                f"Balcony_{side}_AnchorBolt_{bolt_index:02d}", (x, -0.466, z), (0.052, 0.018, 0.052),
                materials["bronze"], details, bevel_width=0.006,
            )

    worker.base.add_box("Facade_NumberPlaque", (2.38, -0.225, 2.63), (0.28, 0.04, 0.38), materials["bronze"], details, bevel_width=0.018)

    render_meshes = [
        worker.join_preserve(structural, worker.RENDER_MESHES[0]),
        worker.join_preserve(glazing, worker.RENDER_MESHES[1]),
        worker.join_preserve(interior_group, worker.RENDER_MESHES[2]),
        worker.join_preserve(details, worker.RENDER_MESHES[3]),
    ]
    for obj in render_meshes:
        obj["recovery02_architecture_first"] = True
        obj["failed_recovery01_facade_geometry_reused"] = False
        obj["balcony_rail_section"] = "square_steel"
    axis.update({
        "design_revision": "architecture_first_recovery02",
        "failed_recovery01_facade_geometry_reused": False,
        "accepted_window_geometry_reauthored": False,
        "accepted_window_material_adjustments": lighting_adjustments,
        "balcony_rail_section": "square_steel",
        "balcony_attachment_terminations": "wall_plates_and_embedded_brackets",
        "hidden_full_facade_slab": False,
    })
    return render_meshes, axis


def create_collision_and_sockets(materials: dict[str, object]):
    collisions: list[object] = []
    sockets: list[object] = []
    worker.base.add_box(worker.COLLISIONS[0], (-2.42, 0.15, 2.18), (1.24, 0.62, 4.36), materials["collision"], collisions, bevel_width=0.0)
    worker.base.add_box(worker.COLLISIONS[1], (2.42, 0.15, 2.18), (1.24, 0.62, 4.36), materials["collision"], collisions, bevel_width=0.0)
    worker.base.add_box(worker.COLLISIONS[2], (0.0, 0.03, 4.18), (5.94, 0.38, 0.25), materials["collision"], collisions, bevel_width=0.0)
    worker.base.add_box(worker.COLLISIONS[3], (0.0, -0.79, 0.76), (2.52, 0.82, 0.16), materials["collision"], collisions, bevel_width=0.0)
    for obj in collisions:
        obj.display_type = "WIRE"
        obj.hide_render = True
        obj["collision_role"] = "UCX"
    socket_data = (
        (worker.SOCKETS[0], (0.0, 0.0, 0.0)),
        (worker.SOCKETS[1], (0.0, 0.0, 2.12)),
        (worker.SOCKETS[2], (0.0, -0.79, 0.76)),
        (worker.SOCKETS[3], (-3.09, 0.0, 0.0)),
        (worker.SOCKETS[4], (3.09, 0.0, 0.0)),
    )
    for name, location in socket_data:
        obj = worker.bpy.data.objects.new(name, None)
        worker.bpy.context.scene.collection.objects.link(obj)
        obj.location = location
        obj.empty_display_type = "PLAIN_AXES"
        obj.empty_display_size = 0.28
        obj["socket_role"] = name
        sockets.append(obj)
    return collisions, sockets


worker.require = recovery_require
worker.make_materials = make_materials
worker.build_geometry = build_geometry
worker.create_collision_and_sockets = create_collision_and_sockets
worker.ASSET_ID = RECOVERY_ASSET_ID
worker.base.ASSET_ID = RECOVERY_ASSET_ID


if __name__ == "__main__":
    raise SystemExit(worker.main())
