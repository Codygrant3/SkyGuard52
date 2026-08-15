from __future__ import annotations

"""Blender-side geometry gate intended to run before expensive final renders."""

import json
from pathlib import Path
from typing import Any, Iterable


class PreRenderGateError(RuntimeError):
    pass


def inspect_objects(objects: Iterable[Any], configuration: dict[str, Any]) -> dict[str, Any]:
    excluded_roles = {str(role) for role in configuration.get("excluded_roles", [])}
    primary_roles = {str(role) for role in configuration.get("primary_roles", [])}
    renderable = []
    for obj in objects:
        if getattr(obj, "type", None) != "MESH":
            continue
        data = getattr(obj, "data", None)
        polygons = len(getattr(data, "polygons", []))
        role = str(obj.get("SKG_Role"))
        if polygons <= 0 or role in excluded_roles:
            continue
        renderable.append(obj)

    total_vertices = sum(len(obj.data.vertices) for obj in renderable)
    primary_vertices = sum(
        len(obj.data.vertices)
        for obj in renderable
        if str(obj.get("SKG_Role")) in primary_roles
    )
    missing_uvs = sorted(
        str(obj.name) for obj in renderable if len(getattr(obj.data, "uv_layers", [])) < 1
    )
    material_names = {
        str(slot.material.name)
        for obj in renderable
        for slot in getattr(obj, "material_slots", [])
        if getattr(slot, "material", None) is not None
    }
    errors: list[str] = []
    minimum_total = int(configuration.get("minimum_total_renderable_vertices", 0))
    minimum_primary = int(configuration.get("minimum_primary_vertices", 0))
    minimum_materials = int(configuration.get("minimum_material_count", 0))
    if missing_uvs:
        errors.append(f"Renderable meshes without UVs: {missing_uvs}")
    if total_vertices < minimum_total:
        errors.append(f"Renderable vertex count {total_vertices} is below {minimum_total}.")
    if primary_vertices < minimum_primary:
        errors.append(f"Primary-form vertex count {primary_vertices} is below {minimum_primary}.")
    if len(material_names) < minimum_materials:
        errors.append(
            f"Distinct renderable material count {len(material_names)} is below {minimum_materials}."
        )
    return {
        "schema": "skyguard.blender-pre-render-quality-gate.v1",
        "pass": not errors,
        "errors": errors,
        "renderable_mesh_count": len(renderable),
        "total_renderable_vertices": total_vertices,
        "minimum_total_renderable_vertices": minimum_total,
        "primary_vertices": primary_vertices,
        "minimum_primary_vertices": minimum_primary,
        "distinct_material_count": len(material_names),
        "minimum_material_count": minimum_materials,
        "missing_uvs": missing_uvs,
        "human_visual_review_still_required": True,
        "unreal_import_authorized": False,
    }


def enforce(collection: Any, configuration: dict[str, Any], receipt_path: Path) -> dict[str, Any]:
    report = inspect_objects(collection.all_objects, configuration)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = receipt_path.with_name(receipt_path.name + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(receipt_path)
    if not report["pass"]:
        raise PreRenderGateError("; ".join(report["errors"]))
    return report
