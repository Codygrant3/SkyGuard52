"""Author and bake defensible Mission 01 high/low hero pairs.

This is intentionally separate from ``blender_m01_hero_pbr_bake.py``.  The
older package bakes a mesh onto itself and is retained as honest historical
evidence.  This build:

* preserves the accepted Wave 1 object as a UV-bearing low target;
* creates a distinct high mesh datablock with asset-specific geometric detail;
* creates and records an explicit projection cage for every target;
* bakes tangent-space Normal and AO with selected-to-active projection; and
* hashes the source, native master, low-only GLB, and every texture.

The script must be executed by the serialized Blender supervisor.  Merely
passing the offline source verifier is not an artifact or visual acceptance.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import bpy


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT / "Docs" / "AAA_Review" / "M01_HERO_HIGH_TO_LOW_BAKE_CONTRACT.json"
)


def contract_path_from_argv() -> Path:
    """Allow immutable corrective contracts without copying the generator."""
    if "--" not in sys.argv:
        return CONTRACT_PATH
    script_args = sys.argv[sys.argv.index("--") + 1 :]
    for index, value in enumerate(script_args):
        if value == "--contract" and index + 1 < len(script_args):
            return Path(script_args[index + 1]).resolve()
    return CONTRACT_PATH


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_evidence(path: Path) -> dict:
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def resolve(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def select_only(objects, active=None) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = active or objects[-1]


def duplicate_mesh(source, name: str, collection):
    obj = source.copy()
    obj.data = source.data.copy()
    obj.animation_data_clear()
    obj.name = name
    obj.data.name = name + "_Mesh"
    collection.objects.link(obj)
    obj.matrix_world = source.matrix_world.copy()
    return obj


def apply_bevel(obj, width: float) -> None:
    modifier = obj.modifiers.new("HILO_HighSourceBevel", "BEVEL")
    modifier.width = width
    modifier.segments = 3
    modifier.limit_method = "ANGLE"
    select_only([obj], obj)
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def add_sphere(name, radius, location, collection, segments=16, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        radius=radius,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def add_torus(name, major_radius, minor_radius, location, collection):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=96,
        minor_segments=10,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def add_cube(name, dimensions, location, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        apply_bevel(obj, bevel)
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def join_high_sources(base, details, final_name):
    select_only([base, *details], base)
    bpy.ops.object.join()
    high = bpy.context.object
    high.name = final_name
    high.data.name = final_name + "_Mesh"
    return high


def pathfinder_details(collection, settings=None):
    settings = settings or {}
    wing_radius = float(settings.get("wing_fastener_radius_m", 0.028))
    wing_z = float(settings.get("wing_fastener_z_m", 0.145))
    hatch_radius = float(settings.get("hatch_fastener_radius_m", 0.024))
    seam_height = float(settings.get("seam_height_m", 0.025))
    hatch_outline_width = float(settings.get("hatch_outline_width_m", 0.022))
    details = []
    # Real geometry above the authored shell: wing fasteners, hatch fasteners,
    # and raised seams.  Coordinates follow the Wave 1 Pathfinder datum.
    for x in (-1.35, -0.75, -0.15, 0.45, 1.05):
        for y in (-1.42, 1.42):
            details.append(
                add_sphere(
                    f"HILO_Pathfinder_WingFastener_{x}_{y}",
                    wing_radius,
                    (x, y, wing_z),
                    collection,
                )
            )
    for x in (-1.02, -0.42):
        for y in (-0.24, 0.24):
            details.append(
                add_sphere(
                    f"HILO_Pathfinder_HatchFastener_{x}_{y}",
                    hatch_radius,
                    (x, y, 0.385),
                    collection,
                )
            )
    details.extend(
        [
            add_cube(
                "HILO_Pathfinder_CenterSeam",
                (2.65, 0.018, seam_height),
                (-0.15, 0.0, 0.39 + seam_height * 0.5),
                collection,
                0.003,
            ),
            add_cube(
                "HILO_Pathfinder_HatchSeam_Front",
                (hatch_outline_width, 0.68, seam_height),
                (-0.28, 0.0, 0.37 + seam_height * 0.5),
                collection,
                0.003,
            ),
            add_cube(
                "HILO_Pathfinder_HatchSeam_Rear",
                (hatch_outline_width, 0.68, seam_height),
                (-1.16, 0.0, 0.37 + seam_height * 0.5),
                collection,
                0.003,
            ),
            add_cube(
                "HILO_Pathfinder_HatchSeam_Left",
                (0.88, hatch_outline_width, seam_height),
                (-0.72, -0.34, 0.37 + seam_height * 0.5),
                collection,
                0.003,
            ),
            add_cube(
                "HILO_Pathfinder_HatchSeam_Right",
                (0.88, hatch_outline_width, seam_height),
                (-0.72, 0.34, 0.37 + seam_height * 0.5),
                collection,
                0.003,
            ),
        ]
    )
    return details, [
        "beveled_primary_shell",
        "wing_panel_fasteners",
        "service_hatch_fasteners",
        "raised_panel_seams",
    ]


def lighthouse_details(collection, settings=None):
    settings = settings or {}
    seam_minor = float(settings.get("tower_seam_minor_radius_m", 0.025))
    gallery_radius = float(settings.get("gallery_fastener_radius_m", 0.027))
    access_radius = float(settings.get("access_fastener_radius_m", 0.032))
    seam_radii = settings.get(
        "tower_seam_major_radii_m",
        [3.02, 2.62, 2.25],
    )
    details = []
    for z, radius in zip((5.95, 12.95, 19.92), seam_radii):
        details.append(
            add_torus(
                f"HILO_Lighthouse_SectionSeam_{z}",
                radius,
                seam_minor,
                (0.0, 0.0, z),
                collection,
            )
        )
    for index in range(24):
        angle = math.tau * index / 24
        details.append(
            add_sphere(
                f"HILO_Lighthouse_GalleryFastener_{index:02d}",
                gallery_radius,
                (3.36 * math.cos(angle), 3.36 * math.sin(angle), 20.42),
                collection,
            )
        )
    for y in (-0.58, 0.58):
        for z in (0.55, 1.55, 2.55):
            details.append(
                add_sphere(
                    f"HILO_Lighthouse_AccessFastener_{y}_{z}",
                    access_radius,
                    (-3.205, y, z),
                    collection,
                )
            )
    return details, [
        "beveled_primary_shell",
        "tower_section_seams",
        "gallery_fasteners",
        "access_panel_fasteners",
    ]


def radar_details(collection, settings=None):
    settings = settings or {}
    access_radius = float(settings.get("access_fastener_radius_m", 0.038))
    mount_radius = float(settings.get("dish_mount_fastener_radius_m", 0.032))
    mast_radius = float(settings.get("mast_joint_fastener_radius_m", 0.045))
    details = []
    for y in (-1.1, 1.1):
        for z in (0.55, 1.45, 2.35, 3.25):
            details.append(
                add_sphere(
                    f"HILO_Radar_AccessFastener_{y}_{z}",
                    access_radius,
                    (-5.11, y, z),
                    collection,
                )
            )
    # Mount fasteners belong on the turntable, not in the dish plane.  The 001
    # recipe placed them in an untilted YZ ring even though the dish is tilted;
    # those floating/intersecting studs caused the rejected speckled projection.
    for index in range(12):
        angle = math.tau * index / 12
        details.append(
            add_sphere(
                f"HILO_Radar_DishFastener_{index:02d}",
                mount_radius,
                (
                    0.82 * math.cos(angle),
                    0.82 * math.sin(angle),
                    16.585,
                ),
                collection,
            )
        )
    for z in (5.1, 8.1, 11.1, 14.1):
        for y in (-1.02, 1.02):
            details.append(
                add_sphere(
                    f"HILO_Radar_MastJoint_{z}_{y}",
                    mast_radius,
                    (0.0, y, z),
                    collection,
                )
            )
    return details, [
        "beveled_primary_shell",
        "bunker_access_fasteners",
        "dish_mount_fasteners",
        "mast_joint_fasteners",
    ]


DETAIL_BUILDERS = {
    "Pathfinder": pathfinder_details,
    "Lighthouse": lighthouse_details,
    "RadarPost": radar_details,
}


def make_cage(low, name: str, extrusion: float, collection):
    cage = duplicate_mesh(low, name, collection)
    select_only([cage], cage)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.transform.shrink_fatten(value=extrusion, use_even_offset=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    cage.display_type = "WIRE"
    cage.hide_render = True
    cage["SKG_BakeCage"] = True
    cage["SKG_CageExtrusionM"] = extrusion
    return cage


def mesh_stats(obj):
    dimensions = tuple(float(value) for value in obj.dimensions)
    triangles = sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons)
    return {
        "object": obj.name,
        "mesh_datablock": obj.data.name,
        "vertices": len(obj.data.vertices),
        "triangles": triangles,
        "dimensions_m": [round(value, 6) for value in dimensions],
        "uv_layers": [layer.name for layer in obj.data.uv_layers],
    }


def new_image(name, resolution, map_type, data=True):
    image = bpy.data.images.new(
        name=name,
        width=resolution,
        height=resolution,
        alpha=False,
        float_buffer=False,
    )
    image.generated_color = (
        (1.0, 1.0, 1.0, 1.0)
        if map_type == "AO"
        else (0.5, 0.5, 1.0, 1.0)
    )
    image.colorspace_settings.name = "Non-Color" if data else "sRGB"
    return image


def attach_bake_image(low, image, tag):
    nodes = []
    for slot in low.material_slots:
        material = slot.material
        if material is None:
            continue
        material.use_nodes = True
        node = material.node_tree.nodes.new("ShaderNodeTexImage")
        node.name = f"SKG_HILO_BAKE_{tag}"
        node.label = node.name
        node.image = image
        material.node_tree.nodes.active = node
        node.select = True
        nodes.append((material, node))
    return nodes


def remove_bake_nodes(nodes):
    for material, node in nodes:
        material.node_tree.nodes.remove(node)


def channel_stats(image):
    pixels = list(image.pixels[:])
    channels = [pixels[index::4] for index in range(4)]
    return {
        "min": [round(min(channel), 6) for channel in channels],
        "max": [round(max(channel), 6) for channel in channels],
        "range": [round(max(channel) - min(channel), 6) for channel in channels],
    }


def remap_ao(image, minimum: float, strength: float):
    """Keep geometric AO readable without shipping clipped black cavities."""
    pixels = list(image.pixels[:])
    for index in range(0, len(pixels), 4):
        for channel in range(3):
            value = pixels[index + channel]
            pixels[index + channel] = max(
                minimum,
                1.0 - ((1.0 - value) * strength),
            )
    image.pixels.foreach_set(pixels)
    image.update()


def save_png(image, path: Path):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    image.file_format = "PNG"
    image.filepath_raw = str(path)
    image.save()


def bake_selected_to_active(high, low, cage, image, map_type, spec):
    scene = bpy.context.scene
    bake = scene.render.bake
    bake.use_selected_to_active = True
    bake.use_cage = True
    # Blender 5.2's RNA property accepts the Object datablock itself. Older
    # name-string assignment raises TypeError before the first bake begins.
    bake.cage_object = cage
    bake.cage_extrusion = float(spec["cage_extrusion_m"])
    bake.max_ray_distance = float(spec["max_ray_distance_m"])
    nodes = attach_bake_image(low, image, map_type)
    select_only([high, low], low)
    # Operator enums are uppercase in Blender 5.2 even though the governed
    # manifest keeps reader-facing map labels such as "Normal".
    bpy.ops.object.bake(type=map_type.upper())
    remove_bake_nodes(nodes)


def export_low_glb(low_objects, path: Path) -> None:
    select_only(low_objects, low_objects[0])
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials="EXPORT",
    )


def main() -> None:
    started = time.perf_counter()
    active_contract_path = contract_path_from_argv()
    contract = json.loads(
        active_contract_path.read_text(encoding="utf-8-sig")
    )
    source_path = resolve(contract["source_blend"])
    output_paths = {
        key: resolve(value)
        for key, value in contract["outputs"].items()
        if key != "texture_root"
    }
    texture_root = resolve(contract["outputs"]["texture_root"])
    for path in [*output_paths.values(), texture_root]:
        (path if path.suffix == "" else path.parent).mkdir(
            parents=True, exist_ok=True
        )

    bpy.ops.wm.open_mainfile(filepath=str(source_path))
    scene = bpy.context.scene
    scene.render.engine = contract["bake_contract"]["engine"]
    scene.cycles.device = contract["bake_contract"]["device"]
    scene.cycles.samples = int(contract["bake_contract"]["samples"])
    scene.render.bake.margin = int(contract["bake_contract"]["margin_pixels"])
    scene.render.bake.use_clear = True
    scene.render.bake.target = "IMAGE_TEXTURES"
    scene.render.bake.normal_space = contract["bake_contract"]["normal_space"]

    high_collection = bpy.data.collections.new("HILO_HIGH_SOURCES")
    low_collection = bpy.data.collections.new("HILO_LOW_TARGETS")
    cage_collection = bpy.data.collections.new("HILO_CAGES")
    scene.collection.children.link(high_collection)
    scene.collection.children.link(low_collection)
    scene.collection.children.link(cage_collection)

    failures = []
    asset_records = []
    low_objects = []
    resolution = int(contract["bake_contract"]["resolution"])
    uv_layer = contract["bake_contract"]["uv_layer"]

    for spec in contract["assets"]:
        source = bpy.data.objects.get(spec["source_object"])
        if source is None or source.type != "MESH":
            failures.append(
                f"{spec['id']}: missing mesh source {spec['source_object']}"
            )
            continue

        low = duplicate_mesh(source, spec["low_object"], low_collection)
        low["SKG_BakeRole"] = "production_low_target"
        low["SKG_BakeUV"] = uv_layer
        low_objects.append(low)

        high_base = duplicate_mesh(source, spec["high_object"], high_collection)
        high_base["SKG_BakeRole"] = "high_source"
        apply_bevel(
            high_base,
            min(0.035, float(spec["cage_extrusion_m"]) * 0.8),
        )
        details, detail_groups = DETAIL_BUILDERS[spec["id"]](
            high_collection,
            spec.get("detail_settings", {}),
        )
        high = join_high_sources(high_base, details, spec["high_object"])
        high["SKG_BakeRole"] = "high_source"
        high["SKG_DetailGroups"] = json.dumps(detail_groups)
        cage = make_cage(
            low,
            spec["cage_object"],
            float(spec["cage_extrusion_m"]),
            cage_collection,
        )

        low_stats = mesh_stats(low)
        high_stats = mesh_stats(high)
        cage_stats = mesh_stats(cage)
        if low.data is high.data or low_stats["mesh_datablock"] == high_stats["mesh_datablock"]:
            failures.append(f"{spec['id']}: low/high mesh datablocks are not distinct")
        if uv_layer not in low_stats["uv_layers"]:
            failures.append(f"{spec['id']}: low target lacks required UV {uv_layer}")
        ratio = high_stats["vertices"] / max(1, low_stats["vertices"])
        if ratio < float(spec["minimum_high_to_low_vertex_ratio"]):
            failures.append(
                f"{spec['id']}: high/low vertex ratio {ratio:.3f} below contract"
            )
        bounds_delta = max(
            abs(high_stats["dimensions_m"][index] - low_stats["dimensions_m"][index])
            for index in range(3)
        )
        if bounds_delta > float(spec["maximum_high_to_low_bounds_delta_m"]):
            failures.append(
                f"{spec['id']}: high/low bounds delta {bounds_delta:.4f}m exceeds contract"
            )
        if set(detail_groups) != set(spec["required_detail_groups"]):
            failures.append(f"{spec['id']}: detail group contract mismatch")

        map_records = []
        asset_dir = texture_root / spec["id"]
        asset_dir.mkdir(parents=True, exist_ok=True)
        for map_spec in contract["bake_contract"]["maps"]:
            map_type = map_spec["type"]
            image = new_image(
                f"{spec['texture_prefix']}_{map_type}",
                resolution,
                map_type,
                data=True,
            )
            bake_selected_to_active(high, low, cage, image, map_type, spec)
            if map_type == "AO" and isinstance(spec.get("ao_remap"), dict):
                remap_ao(
                    image,
                    float(spec["ao_remap"]["minimum"]),
                    float(spec["ao_remap"]["strength"]),
                )
            stats = channel_stats(image)
            output = asset_dir / f"{spec['texture_prefix']}_{map_type}.png"
            save_png(image, output)
            varied = sum(
                value > 0.0005 for value in stats["range"][:3]
            )
            if varied < int(map_spec["minimum_varied_rgb_channels"]):
                failures.append(f"{spec['id']}/{map_type}: invariant bake")
            map_records.append(
                {
                    **file_evidence(output),
                    "type": map_type,
                    "width": resolution,
                    "height": resolution,
                    "channels": 3,
                    "color_space": map_spec["color_space"],
                    "stats": stats,
                    "varied_rgb_channels": varied,
                    "projection": {
                        "selected_to_active": True,
                        "cage_object": cage.name,
                        "cage_extrusion_m": spec["cage_extrusion_m"],
                        "max_ray_distance_m": spec["max_ray_distance_m"],
                    },
                    "ao_remap": (
                        spec.get("ao_remap")
                        if map_type == "AO"
                        else None
                    ),
                }
            )
            bpy.data.images.remove(image)

        asset_records.append(
            {
                "id": spec["id"],
                "source_object": source.name,
                "low": low_stats,
                "high": high_stats,
                "cage": cage_stats,
                "high_to_low_vertex_ratio": round(ratio, 6),
                "high_to_low_bounds_delta_m": round(bounds_delta, 6),
                "detail_groups": detail_groups,
                "maps": map_records,
            }
        )

    bpy.ops.wm.save_as_mainfile(filepath=str(output_paths["master_blend"]))
    export_low_glb(low_objects, output_paths["low_glb"])

    ordered_hashes = [
        item["sha256"]
        for asset in sorted(asset_records, key=lambda item: item["id"])
        for item in sorted(asset["maps"], key=lambda item: item["type"])
    ]
    package_fingerprint = hashlib.sha256(
        "\n".join(ordered_hashes).encode("ascii")
    ).hexdigest()
    manifest = {
        "schema": "skyguard.m01.hero-high-to-low-bake.manifest.v1",
        "build_id": contract["build_id"],
        "source": file_evidence(source_path),
        "contract": file_evidence(active_contract_path),
        "generator": file_evidence(Path(__file__).resolve()),
        "bake_contract": contract["bake_contract"],
        "outputs": {
            "master_blend": file_evidence(output_paths["master_blend"]),
            "low_glb": file_evidence(output_paths["low_glb"]),
        },
        "assets": asset_records,
        "package_fingerprint_sha256": package_fingerprint,
        "validation": {
            "pass": len(asset_records) == len(contract["assets"]) and not failures,
            "failures": failures,
        },
        "promotion": contract["promotion"],
    }
    output_paths["manifest"].write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    report = {
        "schema": "skyguard.m01.hero-high-to-low-bake.report.v1",
        "build_id": contract["build_id"],
        "manifest": file_evidence(output_paths["manifest"]),
        "asset_count": len(asset_records),
        "texture_count": sum(len(asset["maps"]) for asset in asset_records),
        "package_fingerprint_sha256": package_fingerprint,
        "failures": failures,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "gate": (
            "PASS"
            if len(asset_records) == len(contract["assets"]) and not failures
            else "FAIL"
        ),
        "projection_claim": (
            "Separate high and low mesh datablocks, asset-specific geometric "
            "detail, explicit cages, and selected-to-active tangent projection."
        ),
        "promotion": contract["promotion"],
    }
    output_paths["report"].write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print("[SkyguardM01HeroHiLo] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Mission 01 high-to-low bake validation failed")


if __name__ == "__main__":
    main()
