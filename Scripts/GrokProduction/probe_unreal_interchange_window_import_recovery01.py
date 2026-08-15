"""Read-only UE 5.8 reflection probe for the corrected window import contract."""

from __future__ import annotations

import hashlib
import json
import os
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_WINDOW_INTERCHANGE_PIPELINE_PROBE01\attempt_01"
RECEIPT = ATTEMPT / "probe_receipt.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-window.interchange-pipeline-probe01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "pipeline_class_available": False,
        "stack_override_class_available": False,
        "import_rotation_roundtrip": None,
        "common_mesh_properties": {},
        "task_options_class": None,
        "static_mesh_editor_methods": [],
        "asset_tools_methods": [],
        "static_mesh_socket": {},
        "project_content_mutations": 0,
        "error": None,
        "traceback": None,
    }
    try:
        pipeline = unreal.InterchangeGenericAssetsPipeline()
        result["pipeline_class_available"] = True
        rotation = unreal.Rotator()
        rotation.roll = 90.0
        rotation.pitch = 0.0
        rotation.yaw = 0.0
        pipeline.set_editor_property("import_offset_rotation", rotation)
        observed = pipeline.get_editor_property("import_offset_rotation")
        result["import_rotation_roundtrip"] = {
            "roll": float(observed.roll),
            "pitch": float(observed.pitch),
            "yaw": float(observed.yaw),
        }
        if abs(float(observed.roll) - 90.0) > 0.001:
            raise RuntimeError(f"Import rotation did not round-trip: {result['import_rotation_roundtrip']}")

        common = pipeline.get_editor_property("common_meshes_properties")
        common.set_editor_property("import_sockets", True)
        common.set_editor_property("bake_meshes", True)
        result["common_mesh_properties"] = {
            "import_sockets": bool(common.get_editor_property("import_sockets")),
            "bake_meshes": bool(common.get_editor_property("bake_meshes")),
        }

        stack = unreal.InterchangePipelineStackOverride()
        result["stack_override_class_available"] = True
        stack.add_pipeline(pipeline)
        task = unreal.AssetImportTask()
        task.options = stack
        result["task_options_class"] = task.options.get_class().get_name()

        mesh_editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        result["static_mesh_editor_methods"] = sorted(
            name for name in dir(mesh_editor) if "material" in name.lower() or "collision" in name.lower() or "socket" in name.lower()
        )
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        result["asset_tools_methods"] = sorted(name for name in dir(tools) if "rename" in name.lower())

        socket = unreal.StaticMeshSocket()
        socket.set_editor_property("socket_name", "M01_Window_Probe")
        socket.set_editor_property("relative_location", unreal.Vector(5.0, 5.2, 200.0))
        result["static_mesh_socket"] = {
            "class": socket.get_class().get_name(),
            "name": str(socket.get_editor_property("socket_name")),
            "relative_location": [
                float(socket.get_editor_property("relative_location").x),
                float(socket.get_editor_property("relative_location").y),
                float(socket.get_editor_property("relative_location").z),
            ],
        }
        result["classification"] = "PASSED_INTERCHANGE_PIPELINE_REFLECTION_READY_FOR_RECOVERY01_IMPORT"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "Interchange reflection probe failed")


main()
