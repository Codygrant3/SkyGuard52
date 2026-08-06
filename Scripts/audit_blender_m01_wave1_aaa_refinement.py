"""Round-trip structural audit for the Mission 01 refinement GLB."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(r"D:\Skyguard52")
GLB = ROOT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01" / "Wave1_Refinement" / "m01_wave1_aaa_refinement.glb"
MANIFEST = ROOT / "Saved" / "Reports" / "M01_WAVE1_AAA_REFINEMENT_MANIFEST.json"
OUTPUT = ROOT / "Saved" / "Reports" / "M01_WAVE1_AAA_REFINEMENT_ROUNDTRIP_AUDIT.json"


def main():
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(GLB))
    meshes = sorted(
        (obj for obj in bpy.context.scene.objects if obj.type == "MESH"),
        key=lambda obj: obj.name,
    )
    names = {obj.name for obj in meshes}
    expected_names = {asset["name"] for asset in expected["assets"]}
    missing = sorted(expected_names - names)
    unexpected = sorted(names - expected_names)
    weak_points = set(expected["boss"]["weak_points"])
    breakup = set(expected["boss"]["breakup_pool"])
    zero_dimension = sorted(
        obj.name for obj in meshes if min(abs(float(v)) for v in obj.dimensions) < 0.00001
    )
    report = {
        "schema": "skyguard.m01.wave1.aaa-refinement.roundtrip-audit.v1",
        "glb": str(GLB),
        "glb_bytes": GLB.stat().st_size,
        "glb_sha256": hashlib.sha256(GLB.read_bytes()).hexdigest(),
        "expected_asset_count": expected["asset_count"],
        "imported_mesh_count": len(meshes),
        "missing_assets": missing,
        "unexpected_assets": unexpected,
        "weak_points_present": sorted(weak_points & names),
        "breakup_pool_present": sorted(breakup & names),
        "zero_dimension_meshes": zero_dimension,
        "imported_triangles": sum(
            sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons)
            for obj in meshes
        ),
    }
    report["gate"] = "PASS" if (
        len(meshes) == expected["asset_count"]
        and not missing
        and not unexpected
        and weak_points <= names
        and breakup <= names
        and not zero_dimension
    ) else "FAIL"
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("[SkyguardM01AAARoundTrip] " + json.dumps(report))


if __name__ == "__main__":
    main()
