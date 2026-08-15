"""Read-only UE 5.8 Python reflection probe for the vegetation Interchange contract."""

from __future__ import annotations

import json
import traceback
from pathlib import Path

import unreal


RECEIPT = Path(r"D:\Skyguard52\Saved\BuildAttempts\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_REFLECTION_PROBE\attempt_01\reflection_receipt.json")


def probe_property(obj: object, name: str, value: object | None = None) -> dict[str, object]:
    row: dict[str, object] = {"name": name, "readable": False, "writable": None, "value": None, "error": None}
    try:
        current = obj.get_editor_property(name)
        row["readable"] = True
        row["value"] = str(current)
        if value is not None:
            obj.set_editor_property(name, value)
            row["writable"] = True
            row["assigned_value"] = str(obj.get_editor_property(name))
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
    return row


result: dict[str, object] = {
    "schema": "skyguard.m01-polyhaven-vegetation-staging01-recovery01-reflection-probe.v1",
    "classification": "FAILED_WITH_EVIDENCE",
    "pipeline": {},
    "common_meshes": {},
    "mesh_pipeline": {},
    "material_pipeline": {},
    "texture_pipeline": {},
    "combine_enum": {},
    "error": None,
    "traceback": None,
    "content_mutated": False,
}

try:
    pipeline = unreal.InterchangeGenericAssetsPipeline()
    common = pipeline.get_editor_property("common_meshes_properties")
    mesh = pipeline.get_editor_property("mesh_pipeline")
    material = pipeline.get_editor_property("material_pipeline")
    texture = material.get_editor_property("texture_pipeline")
    enum_type = getattr(unreal, "InterchangeCombineStaticMeshesBehavior", None)
    if enum_type is None:
        raise RuntimeError("InterchangeCombineStaticMeshesBehavior is absent")
    enum_names = [name for name in dir(enum_type) if name.isupper()]
    result["combine_enum"] = {"python_type": str(enum_type), "members": enum_names}
    all_value = getattr(enum_type, "ALL", None)
    if all_value is None:
        raise RuntimeError(f"ALL combine enum is absent: {enum_names}")

    result["pipeline"] = {
        name: probe_property(pipeline, name, value)
        for name, value in (
            ("scene_name_sub_folder", False),
            ("asset_type_sub_folders", False),
            ("use_source_name_for_asset", True),
        )
    }
    result["common_meshes"] = {
        name: probe_property(common, name, value)
        for name, value in (("import_sockets", False), ("bake_meshes", True))
    }
    result["mesh_pipeline"] = {
        name: probe_property(mesh, name, value)
        for name, value in (
            ("combine_static_meshes_behavior", all_value),
            ("collision", False),
            ("build_nanite", True),
            ("nanite_triangle_threshold", 0),
            ("generate_lightmap_u_vs", True),
            ("generate_lightmap_uvs", True),
            ("generate_distance_field_as_if_two_sided", True),
        )
    }
    result["material_pipeline"] = {"import_materials": probe_property(material, "import_materials", True)}
    result["texture_pipeline"] = {"import_textures": probe_property(texture, "import_textures", True)}

    required = [
        *result["pipeline"].values(),
        *result["common_meshes"].values(),
        result["mesh_pipeline"]["combine_static_meshes_behavior"],
        result["mesh_pipeline"]["collision"],
        result["mesh_pipeline"]["build_nanite"],
        result["mesh_pipeline"]["nanite_triangle_threshold"],
        result["mesh_pipeline"]["generate_lightmap_u_vs"],
        result["mesh_pipeline"]["generate_distance_field_as_if_two_sided"],
        result["material_pipeline"]["import_materials"],
        result["texture_pipeline"]["import_textures"],
    ]
    if not all(row["readable"] and row["writable"] for row in required):
        raise RuntimeError("One or more required reflected properties are unavailable")
    if result["mesh_pipeline"]["generate_lightmap_uvs"]["readable"]:
        raise RuntimeError("Previously rejected spelling unexpectedly became readable")
    result["classification"] = "PASSED_UE58_INTERCHANGE_REFLECTION_READY_FOR_RECOVERY01_STAGING_DESIGN"
except Exception as exc:
    result["error"] = f"{type(exc).__name__}: {exc}"
    result["traceback"] = traceback.format_exc()
finally:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

if result["classification"] != "PASSED_UE58_INTERCHANGE_REFLECTION_READY_FOR_RECOVERY01_STAGING_DESIGN":
    raise RuntimeError(str(result["error"]))
