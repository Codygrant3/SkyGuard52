"""Bake deterministic PBR texture packages for Mission 01 hero assets.

The source refinement geometry is not a separate high-poly sculpt / low-poly
game mesh pair.  Consequently this script performs same-mesh tangent-space
normal baking (including authored shader bump) and does not claim high-to-low
normal provenance.

Outputs per hero:
* BaseColor (sRGB)
* Normal (tangent-space, non-color)
* ORM (R=AO, G=Roughness, B=Metallic, non-color)
* MaterialID (stable material-slot colors, non-color mask)
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import bpy


ROOT = Path(r"D:\Skyguard52")
SOURCE_BLEND = (
    ROOT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01"
    / "Wave1_Refinement" / "M01_WAVE1_AAA_REFINEMENT_MASTER.blend"
)
SOURCE_GLB = (
    ROOT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01"
    / "Wave1_Refinement" / "m01_wave1_aaa_refinement.glb"
)
OUTPUT_DIR = (
    ROOT / "Content" / "Skyguard" / "Textures" / "Source" / "Mission01"
    / "HeroPBR_v1"
)
REPORT_DIR = ROOT / "Saved" / "Reports"
MANIFEST_PATH = REPORT_DIR / "M01_HERO_PBR_BAKE_MANIFEST.json"
REPORT_PATH = REPORT_DIR / "M01_HERO_PBR_BAKE_REPORT.json"

HEROES = {
    "Pathfinder": {
        "object": "SM_Boss_Pathfinder_Body_AAA",
        "resolution": 1024,
        "prefix": "T_M01_Pathfinder",
    },
    "Lighthouse": {
        "object": "SM_M01_Landmark_Lighthouse_Hero_A",
        "resolution": 1024,
        "prefix": "T_M01_Lighthouse",
    },
    "RadarPost": {
        "object": "SM_M01_Landmark_RadarPost_Hero_A",
        "resolution": 1024,
        "prefix": "T_M01_RadarPost",
    },
}

ID_PALETTE = (
    (1.0, 0.0, 0.0, 1.0),
    (0.0, 1.0, 0.0, 1.0),
    (0.0, 0.0, 1.0, 1.0),
    (1.0, 1.0, 0.0, 1.0),
    (1.0, 0.0, 1.0, 1.0),
    (0.0, 1.0, 1.0, 1.0),
    (1.0, 0.45, 0.0, 1.0),
    (0.48, 0.0, 1.0, 1.0),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_new(name: str, resolution: int, color=(0.0, 0.0, 0.0, 1.0), data=False):
    image = bpy.data.images.new(
        name=name,
        width=resolution,
        height=resolution,
        alpha=True,
        float_buffer=False,
    )
    image.generated_color = color
    try:
        image.colorspace_settings.name = "Non-Color" if data else "sRGB"
    except TypeError:
        pass
    return image


def save_png(image, path: Path, data=False):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.color_management = "OVERRIDE"
    image.file_format = "PNG"
    image.filepath_raw = str(path)
    image.save()


def material_nodes(obj):
    result = []
    seen = set()
    for slot in obj.material_slots:
        material = slot.material
        if material and material.name not in seen:
            material.use_nodes = True
            result.append(material)
            seen.add(material.name)
    return result


def set_active_image(materials, image, tag):
    nodes = []
    for material in materials:
        node = material.node_tree.nodes.new("ShaderNodeTexImage")
        node.name = f"SKG_BAKE_{tag}"
        node.label = f"SKG_BAKE_{tag}"
        node.image = image
        material.node_tree.nodes.active = node
        node.select = True
        nodes.append((material, node))
    return nodes


def remove_nodes(nodes):
    for material, node in nodes:
        material.node_tree.nodes.remove(node)


def choose_output_and_bsdf(material):
    output = next(
        (node for node in material.node_tree.nodes if node.type == "OUTPUT_MATERIAL" and node.is_active_output),
        None,
    )
    if output is None:
        output = next((node for node in material.node_tree.nodes if node.type == "OUTPUT_MATERIAL"), None)
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    return output, bsdf


def activate_object(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.hide_set(False)
    obj.hide_viewport = False
    obj.hide_render = False
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def bake(obj, image, bake_type, pass_filter=None):
    materials = material_nodes(obj)
    nodes = set_active_image(materials, image, bake_type)
    activate_object(obj)
    kwargs = {"type": bake_type}
    if pass_filter is not None:
        kwargs["pass_filter"] = pass_filter
    bpy.ops.object.bake(**kwargs)
    remove_nodes(nodes)
    return materials


def bake_emission_values(obj, image, value_getter, tag):
    materials = material_nodes(obj)
    image_nodes = set_active_image(materials, image, tag)
    restore = []
    for index, material in enumerate(materials):
        tree = material.node_tree
        output, bsdf = choose_output_and_bsdf(material)
        if output is None:
            continue
        surface = output.inputs["Surface"]
        old_link = surface.links[0].from_socket if surface.links else None
        emission = tree.nodes.new("ShaderNodeEmission")
        emission.name = f"SKG_TEMP_EMISSION_{tag}"
        value = value_getter(index, material, bsdf)
        emission.inputs["Color"].default_value = value
        emission.inputs["Strength"].default_value = 1.0
        tree.links.new(emission.outputs["Emission"], surface)
        restore.append((material, output, old_link, emission))
    activate_object(obj)
    bpy.ops.object.bake(type="EMIT")
    for material, output, old_link, emission in restore:
        tree = material.node_tree
        if old_link:
            tree.links.new(old_link, output.inputs["Surface"])
        tree.nodes.remove(emission)
    remove_nodes(image_nodes)
    return materials


def channel_stats(image):
    pixels = list(image.pixels[:])
    channels = [pixels[index::4] for index in range(4)]
    return {
        "min": [round(min(channel), 6) for channel in channels],
        "max": [round(max(channel), 6) for channel in channels],
        "range": [round(max(channel) - min(channel), 6) for channel in channels],
    }


def combine_orm(ao_image, values_image, output_image):
    ao = list(ao_image.pixels[:])
    values = list(values_image.pixels[:])
    result = [0.0] * len(ao)
    for index in range(0, len(ao), 4):
        result[index] = ao[index]
        result[index + 1] = values[index + 1]
        result[index + 2] = values[index + 2]
        result[index + 3] = 1.0
    output_image.pixels.foreach_set(result)
    output_image.update()


def rough_metal_value(_index, _material, bsdf):
    roughness = 0.65
    metallic = 0.0
    if bsdf:
        roughness = float(bsdf.inputs["Roughness"].default_value)
        metallic = float(bsdf.inputs["Metallic"].default_value)
    return (1.0, roughness, metallic, 1.0)


def stable_id_value(index, _material, _bsdf):
    return ID_PALETTE[index % len(ID_PALETTE)]


def configure_cycles():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 1
    # Blender's bake operator is available through the current engine in 5.2;
    # use conservative bake padding to avoid mip-edge bleeding in Unreal.
    scene.render.bake.margin = 24
    scene.render.bake.use_clear = True
    scene.render.bake.target = "IMAGE_TEXTURES"
    scene.render.bake.normal_space = "TANGENT"


def main():
    started = time.perf_counter()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    configure_cycles()

    source_provenance = {
        "blend": str(SOURCE_BLEND),
        "blend_sha256": sha256(SOURCE_BLEND),
        "glb": str(SOURCE_GLB),
        "glb_sha256": sha256(SOURCE_GLB),
    }
    package = []
    failures = []

    for hero_name, spec in HEROES.items():
        obj = bpy.data.objects.get(spec["object"])
        if obj is None:
            failures.append(f"{hero_name}: source object missing: {spec['object']}")
            continue
        resolution = spec["resolution"]
        prefix = spec["prefix"]
        hero_dir = OUTPUT_DIR / hero_name
        hero_dir.mkdir(parents=True, exist_ok=True)

        base = image_new(prefix + "_BaseColor", resolution)
        bake(obj, base, "DIFFUSE", {"COLOR"})
        base_path = hero_dir / f"{prefix}_BaseColor.png"
        base_stats = channel_stats(base)
        save_png(base, base_path)

        normal = image_new(prefix + "_Normal", resolution, (0.5, 0.5, 1.0, 1.0), True)
        bake(obj, normal, "NORMAL")
        normal_path = hero_dir / f"{prefix}_Normal.png"
        normal_stats = channel_stats(normal)
        save_png(normal, normal_path, True)

        ao = image_new(prefix + "_AO_TEMP", resolution, (1.0, 1.0, 1.0, 1.0), True)
        bake(obj, ao, "AO")
        values = image_new(prefix + "_ORM_VALUES_TEMP", resolution, (1.0, 0.65, 0.0, 1.0), True)
        bake_emission_values(obj, values, rough_metal_value, "ORM_VALUES")
        orm = image_new(prefix + "_ORM", resolution, (1.0, 0.65, 0.0, 1.0), True)
        combine_orm(ao, values, orm)
        orm_path = hero_dir / f"{prefix}_ORM.png"
        orm_stats = channel_stats(orm)
        save_png(orm, orm_path, True)

        material_id = image_new(prefix + "_MaterialID", resolution, (0.0, 0.0, 0.0, 1.0), True)
        mats = bake_emission_values(obj, material_id, stable_id_value, "MATERIAL_ID")
        id_path = hero_dir / f"{prefix}_MaterialID.png"
        id_stats = channel_stats(material_id)
        save_png(material_id, id_path, True)

        records = []
        for map_type, path, stats, color_space in (
            ("BaseColor", base_path, base_stats, "sRGB"),
            ("Normal", normal_path, normal_stats, "Non-Color"),
            ("ORM", orm_path, orm_stats, "Non-Color"),
            ("MaterialID", id_path, id_stats, "Non-Color"),
        ):
            varied_channels = sum(1 for value in stats["range"][:3] if value > 0.0005)
            record = {
                "type": map_type,
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "width": resolution,
                "height": resolution,
                "channels": 4,
                "color_space": color_space,
                "stats": stats,
                "varied_rgb_channels": varied_channels,
            }
            records.append(record)
            if path.stat().st_size < 256 or varied_channels == 0:
                failures.append(f"{hero_name}/{map_type}: empty or invariant bake")

        package.append({
            "hero": hero_name,
            "source_object": obj.name,
            "resolution": resolution,
            "material_slots": [material.name for material in mats],
            "textures": records,
            "normal_provenance": "same_mesh_tangent_space_with_authored_shader_bump_not_high_to_low",
        })

        for image in (base, normal, ao, values, orm, material_id):
            bpy.data.images.remove(image)

    manifest = {
        "schema": "skyguard.m01.hero-pbr-bake.manifest.v1",
        "determinism_contract": "source hashes + stable object names + stable material-slot order",
        "source_provenance": source_provenance,
        "unreal_channel_contract": {
            "BaseColor": "sRGB RGBA",
            "Normal": "Non-Color tangent-space OpenGL convention; Unreal import must flip green or use Flip Green Channel",
            "ORM": "Non-Color; R=Ambient Occlusion, G=Roughness, B=Metallic",
            "MaterialID": "Non-Color discrete RGB material-slot mask",
        },
        "heroes": package,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    ordered_texture_hashes = [
        texture["sha256"]
        for hero in package
        for texture in hero["textures"]
    ]
    package_fingerprint = hashlib.sha256(
        "\n".join(ordered_texture_hashes).encode("ascii")
    ).hexdigest()
    report = {
        "schema": "skyguard.m01.hero-pbr-bake.report.v1",
        "manifest": str(MANIFEST_PATH),
        "hero_count": len(package),
        "texture_count": sum(len(item["textures"]) for item in package),
        "package_fingerprint_sha256": package_fingerprint,
        "determinism_contract": (
            "Ordered texture hashes form the package fingerprint; consecutive "
            "runs from identical source hashes must match."
        ),
        "failures": failures,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "gate": "PASS" if len(package) == len(HEROES) and not failures else "FAIL",
        "normal_bake_claim": (
            "Same-mesh tangent-space normal maps preserving authored geometry/shader bump. "
            "No high-to-low sculpt bake is claimed because no defensible high/low pair exists."
        ),
        "promotion": "hero_texture_candidate_requires_unreal_import_shader_and_visual_validation",
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("[SkyguardM01HeroPBR] " + json.dumps(report))


if __name__ == "__main__":
    main()
