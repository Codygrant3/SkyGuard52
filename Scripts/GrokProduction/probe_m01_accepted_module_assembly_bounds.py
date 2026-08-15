"""Record actor bounds for the quarantined M01 assembly map."""

from __future__ import annotations

import json
import os
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
TARGET_MAP = "/Game/Skyguard/Maps/Assembly/Lvl_M01_AcceptedModuleAssembly_v1"
OUTPUT = (
    ROOT
    / r"Saved\Reports\M01_ACCEPTED_MODULE_ASSEMBLY_V1_BOUNDS_PROBE_2026-08-11.json"
)


def vector_row(value: unreal.Vector) -> list[float]:
    return [float(value.x), float(value.y), float(value.z)]


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def main() -> None:
    loaded = unreal.EditorLoadingAndSavingUtils.load_map(TARGET_MAP)
    if loaded is None:
        raise RuntimeError(f"Failed to load {TARGET_MAP}")
    rows: list[dict[str, object]] = []
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if not isinstance(actor, unreal.StaticMeshActor):
            continue
        origin, extent = actor.get_actor_bounds(False)
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        mesh = component.get_editor_property("static_mesh") if component else None
        rows.append(
            {
                "label": actor.get_actor_label(),
                "location_cm": vector_row(actor.get_actor_location()),
                "bounds_origin_cm": vector_row(origin),
                "bounds_extent_cm": vector_row(extent),
                "mesh": mesh.get_path_name() if mesh else None,
            }
        )
    write_json_atomic(
        OUTPUT,
        {
            "schema": "skyguard.m01-assembly.bounds-probe.v1",
            "target_map": TARGET_MAP,
            "actor_count": len(rows),
            "actors": rows,
        },
    )


main()
