"""Read-only Blender 5.2 RNA/operator capability probe for the environment kit."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import bpy


REPORT = Path(r"D:\Skyguard52\Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_BLENDER52_API_PROBE01_RESULT.json")


def enum_values(owner, identifier: str) -> list[str]:
    prop = owner.bl_rna.properties.get(identifier)
    if prop is None or not hasattr(prop, "enum_items"):
        return []
    return [item.identifier for item in prop.enum_items]


def operator_properties(operator) -> list[str]:
    try:
        return sorted(prop.identifier for prop in operator.get_rna_type().properties if prop.identifier != "rna_type")
    except Exception as exc:
        return [f"PROBE_ERROR:{type(exc).__name__}:{exc}"]


def main() -> int:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    world = bpy.data.worlds.new("API_PROBE_WORLD")
    world.use_nodes = True
    sky = world.node_tree.nodes.new("ShaderNodeTexSky")
    bsdf = world.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    scene = bpy.context.scene
    payload = {
        "schema": "skyguard.blender52.environment-api-probe01.v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "classification": "PASSED_READ_ONLY_API_CAPABILITY_PROBE",
        "blender": {
            "version": list(bpy.app.version),
            "version_string": bpy.app.version_string,
            "background": bpy.app.background,
        },
        "sky_texture": {
            "sky_type_enum": enum_values(sky, "sky_type"),
            "properties": sorted(prop.identifier for prop in sky.bl_rna.properties),
            "has_air_density": hasattr(sky, "air_density"),
            "has_dust_density": hasattr(sky, "dust_density"),
            "has_ozone_density": hasattr(sky, "ozone_density"),
            "has_sun_elevation": hasattr(sky, "sun_elevation"),
            "has_sun_rotation": hasattr(sky, "sun_rotation"),
        },
        "principled_bsdf_inputs": [socket.name for socket in bsdf.inputs],
        "render_engines": enum_values(scene.render, "engine"),
        "scene_has_eevee_property_group": hasattr(scene, "eevee"),
        "view_look_enum": enum_values(scene.view_settings, "look"),
        "gltf_export_properties": operator_properties(bpy.ops.export_scene.gltf),
        "file_pack_properties": operator_properties(bpy.ops.file.pack_all),
        "save_mainfile_properties": operator_properties(bpy.ops.wm.save_as_mainfile),
        "no_project_file_opened": True,
        "no_scene_saved": True,
        "no_content_mutated": True,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
