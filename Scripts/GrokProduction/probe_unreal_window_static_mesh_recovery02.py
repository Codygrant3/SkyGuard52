"""Read-only UE 5.8 reflection probe for Recovery02 window mesh normalization.

The probe loads the immutable failed-Recovery01 frame mesh only to inspect the
Python surface.  It neither adds sockets nor saves any package.
"""

from __future__ import annotations

import json
import os
import traceback
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_WINDOW_INTERCHANGE_PIPELINE_PROBE02\attempt_01"
RECEIPT = ATTEMPT / "probe_receipt.json"
FRAME_PATH = "/Game/T08/GW01/StaticMeshes/SM_M01_PrewarWindowBay_A01_FrameFacadeHardware.SM_M01_PrewarWindowBay_A01_FrameFacadeHardware"


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> None:
    import unreal

    result: dict[str, object] = {
        "schema": "skyguard.m01-window.static-mesh-reflection-probe02.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "frame_path": FRAME_PATH,
        "frame_class": None,
        "frame_methods": [],
        "editor_asset_library_methods": [],
        "socket_outer_supported": False,
        "socket_outer_path": None,
        "socket_created_but_not_attached": False,
        "frame_socket_count_before": None,
        "frame_socket_count_after": None,
        "asset_saved": False,
        "project_content_mutations": 0,
        "error": None,
        "traceback": None,
    }
    try:
        frame = unreal.load_asset(FRAME_PATH)
        if frame is None or not isinstance(frame, unreal.StaticMesh):
            raise RuntimeError(f"Immutable Recovery01 frame did not load: {FRAME_PATH}")

        frame_methods = sorted(name for name in dir(frame) if name in {"add_socket", "find_socket", "modify", "remove_socket"})
        result["frame_class"] = frame.get_class().get_name()
        result["frame_methods"] = frame_methods
        required = {"add_socket", "find_socket", "modify"}
        if not required.issubset(set(frame_methods)):
            raise RuntimeError(f"Required StaticMesh methods missing: {sorted(required - set(frame_methods))}")

        library_methods = sorted(name for name in dir(unreal.EditorAssetLibrary) if name in {"save_loaded_asset", "save_directory"})
        result["editor_asset_library_methods"] = library_methods
        if "save_loaded_asset" not in library_methods:
            raise RuntimeError("EditorAssetLibrary.save_loaded_asset is unavailable")

        before = list(frame.get_editor_property("sockets"))
        result["frame_socket_count_before"] = len(before)
        socket = unreal.StaticMeshSocket(outer=frame)
        socket.set_editor_property("socket_name", "M01_Window_Probe02_Unattached")
        socket.set_editor_property("relative_location", unreal.Vector(5.0, 5.2, 200.0))
        result["socket_outer_supported"] = True
        outer = socket.get_outer() if hasattr(socket, "get_outer") else None
        result["socket_outer_path"] = outer.get_path_name() if outer is not None else None
        result["socket_created_but_not_attached"] = frame.find_socket("M01_Window_Probe02_Unattached") is None
        after = list(frame.get_editor_property("sockets"))
        result["frame_socket_count_after"] = len(after)
        if len(after) != len(before):
            raise RuntimeError("Read-only probe unexpectedly changed the frame socket array")
        if not result["socket_created_but_not_attached"]:
            raise RuntimeError("Transient socket was unexpectedly attached to the immutable frame")

        result["classification"] = "PASSED_STATIC_MESH_REFLECTION_READY_FOR_RECOVERY02_IMPORT"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if result["classification"].startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
    else:
        raise RuntimeError(result["error"] or "StaticMesh reflection probe failed")


main()
