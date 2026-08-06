"""Read-only UE 5.8 MetaSound Python binding return-shape probe.

This creates one transient source builder, records only Python wrapper
introspection, unregisters the builder, and writes no Unreal assets.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import unreal


REPORT_PATH = Path(
    os.environ.get(
        "SKYGUARD_PHASE5_METASOUND_DIAGNOSTIC_REPORT",
        r"D:\Skyguard52\Saved\Reports"
        r"\PHASE5_METASOUND_UE58_RETURN_SHAPES.json",
    )
)
BUILDER_NAME = "Skyguard_Phase5_ReturnShapeProbe"


def safe_value(function):
    try:
        value = function()
        return {
            "ok": True,
            "type": type(value).__name__,
            "repr": repr(value)[:2000],
            "str": str(value)[:2000],
        }
    except Exception as error:
        return {
            "ok": False,
            "error_type": type(error).__name__,
            "error": str(error)[:2000],
        }


def describe(value, depth=0):
    type_name = type(value).__name__
    useful_names = [
        name
        for name in dir(value)
        if any(
            token in name.lower()
            for token in (
                "node",
                "vertex",
                "tuple",
                "export",
                "editor_property",
                "iter",
            )
        )
    ]
    result = {
        "type": type_name,
        "module": type(value).__module__,
        "repr": repr(value)[:2000],
        "str": str(value)[:2000],
        "useful_dir": useful_names,
        "attribute_reads": {},
        "editor_property_reads": {},
        "method_calls": {},
    }
    for name in (
        "node_id",
        "vertex_id",
        "NodeID",
        "VertexID",
        "nodeid",
        "vertexid",
    ):
        result["attribute_reads"][name] = safe_value(
            lambda name=name: getattr(value, name)
        )
    getter = getattr(value, "get_editor_property", None)
    if getter is not None:
        for name in (
            "node_id",
            "vertex_id",
            "NodeID",
            "VertexID",
            "nodeid",
            "vertexid",
        ):
            result["editor_property_reads"][name] = safe_value(
                lambda name=name: getter(name)
            )
    for method_name in ("to_tuple", "export_text"):
        method = getattr(value, method_name, None)
        if method is not None:
            result["method_calls"][method_name] = safe_value(method)
    if depth < 1 and not isinstance(value, (str, bytes, dict)):
        try:
            entries = list(value)
        except Exception as error:
            result["iteration"] = {
                "ok": False,
                "error_type": type(error).__name__,
                "error": str(error)[:2000],
            }
        else:
            result["iteration"] = {
                "ok": True,
                "count": len(entries),
                "entries": [describe(entry, depth + 1) for entry in entries],
            }
    return result


def main():
    subsystem = unreal.get_engine_subsystem(
        unreal.MetaSoundBuilderSubsystem
    )
    if subsystem is None:
        raise RuntimeError("MetaSoundBuilderSubsystem unavailable")
    try:
        raw = subsystem.create_source_builder(
            BUILDER_NAME,
            unreal.MetaSoundOutputAudioFormat.STEREO,
            False,
        )
        outer = list(raw) if isinstance(raw, tuple) else [raw]
        report = {
            "schema": "skyguard.phase5.metasound-ue58-return-shape.v1",
            "engine_version": unreal.SystemLibrary.get_engine_version(),
            "builder_name": BUILDER_NAME,
            "transient_only": True,
            "asset_written": False,
            "outer_type": type(raw).__name__,
            "outer_count": len(outer),
            "items": [
                {"index": index, **describe(item)}
                for index, item in enumerate(outer)
            ],
            "status": "PASS_TRANSIENT_RETURN_SHAPE_CAPTURED",
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        unreal.log("[Skyguard52] PHASE5_RETURN_SHAPE_PROBE_COMPLETE")
    finally:
        subsystem.unregister_builder(BUILDER_NAME)


if __name__ == "__main__":
    main()
