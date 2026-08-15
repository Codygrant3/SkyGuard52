from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\author_m01_bicycle_rack_recovery02_unreal_integration01.py")
BASE_BYTES = 17617
BASE_SHA256 = "6106577e20f3622f5d8d3b7e2b3f17f2eb8f285a812b48ff37f63e0ae0bbaf5d"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Bicycle-rack integration author authority changed")

text = BASE.read_text(encoding="utf-8")
for old_word, new_word in [
    ("BICYCLE_RACK", "UTILITY_CABINET"),
    ("BicycleRack", "UtilityCabinet"),
    ("Bicycle-rack", "Utility-cabinet"),
    ("bicycle-rack", "utility-cabinet"),
    ("Bicycle rack", "Utility cabinet"),
    ("bicycle rack", "utility cabinet"),
    ("RECOVERY02", "RECOVERY04"),
    ("recovery02", "recovery04"),
    ("rack_mesh", "cabinet_mesh"),
]:
    text = text.replace(old_word, new_word)
start = text.index('ROOT = Path(r"D:\\Skyguard52")\n')
end_marker = "EXPECTED_ACTORS_BEFORE = 113\n"
end = text.index(end_marker, start) + len(end_marker)
constants = r'''ROOT = Path(r"D:\\Skyguard52")
ISOLATED = Path(r"D:\\SG52T08_ENV01")
SOURCE = ROOT / r"Production\Attempts\m01-utility-cabinet-deterministic-recovery04\attempt_20260811T095000000000Z\output\exports\M01_Promenade_UtilityCabinet_Recovery04.glb"
SOURCE_BYTES = 305_848
SOURCE_SHA256 = "5df31f7b4119599f760bf28e142f5800cdbc4fd043232701c5b3312a4c26e0d2"
ACCEPTANCE_FREEZE = ROOT / r"Docs\AAA_Review\M01_UTILITY_CABINET_DETERMINISTIC_RECOVERY04_ACCEPTANCE_FREEZE.json"
ACCEPTANCE_FREEZE_BYTES = 1_396
ACCEPTANCE_FREEZE_SHA256 = "72e10e409f4b81b0deb0eda53265ade5926236386052b5e0e7c6cdb9f1cf89df"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01"
OUTPUT_ASSET = "/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01"
INPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01.umap"
OUTPUT_FILE = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01.umap"
INPUT_BYTES = 751_559
INPUT_SHA256 = "d175aefdb4d6767e4ef42330ff0652c5d9689130b73b3610537db5c73905cc4e"
DESTINATION = "/Game/M01/PromenadeUtilityCabinetRecovery04"
DESTINATION_DISK = ISOLATED / "Content/M01/PromenadeUtilityCabinetRecovery04"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01\attempt_01"
RECEIPT = ATTEMPT / "integration_receipt.json"
MESH_NAME = "SM_M01_Promenade_UtilityCabinet_A"
SOCKET_NODE = "SOCKET_UtilityCabinet_Origin"
CANONICAL_SOCKET = "M01_UtilityCabinet_Origin"
PLACEMENT_COUNT = 5
EXPECTED_ACTORS_BEFORE = 121
'''
text = text[:start] + constants + text[end:]

old = 'require(freeze.get("classification") == "PASSED_DIRECT_VISUAL_REVIEW_FOR_MID_DISTANCE_ENVIRONMENT_USE", "Unexpected acceptance classification")\n    require(freeze.get("glb", {}).get("sha256") == SOURCE_SHA256, "Accepted GLB is not bound by the freeze")'
new = 'require(freeze.get("classification") == "PASSED_PROVISIONAL_MID_DISTANCE_RUNTIME_CANDIDATE", "Unexpected acceptance classification")\n    require(freeze.get("accepted_glb", {}).get("sha256") == SOURCE_SHA256, "Accepted GLB is not bound by the freeze")'
if text.count(old) != 1:
    raise RuntimeError("Acceptance-freeze validation block drifted")
text = text.replace(old, new, 1)

old = 'require(len(meshes) == 1, f"Accepted GLB mesh count changed: {meshes}")\n    require(MESH_NAME in nodes and SOCKET_NODE in nodes, f"Accepted node contract changed: {sorted(nodes)}")\n    require(materials == ["M_M01_Promenade_GalvanizedSteel_Rack"], f"Accepted material contract changed: {materials}")'
new = 'require(len(meshes) == 4 and MESH_NAME in meshes and len([name for name in meshes if name.startswith("UCX_")]) == 3, f"Accepted GLB mesh contract changed: {meshes}")\n    require(MESH_NAME in nodes and SOCKET_NODE in nodes and len([name for name in nodes if name.startswith("UCX_")]) == 3, f"Accepted node contract changed: {sorted(nodes)}")\n    require(materials == ["M_M01_UtilCab_PaintSteel", "M_M01_UtilCab_RubberGasket", "M_M01_UtilCab_Hardware", "M_M01_UtilCab_Concrete", "M_M01_UtilCab_PaintDark"], f"Accepted material contract changed: {materials}")'
if text.count(old) != 1:
    raise RuntimeError("GLB validation block drifted")
text = text.replace(old, new, 1)

old = 'require(85.0 <= extent[0] <= 100.0 and 25.0 <= extent[1] <= 35.0 and 35.0 <= extent[2] <= 45.0, f"Utility-cabinet bounds changed: {extent}")'
new = 'require(47.0 <= extent[0] <= 52.0 and 24.0 <= extent[1] <= 28.0 and 70.0 <= extent[2] <= 75.0, f"Utility-cabinet bounds changed: {extent}")'
if text.count(old) != 1:
    raise RuntimeError("Bounds validation line drifted")
text = text.replace(old, new, 1)

old = 'require(len(materials) == 1, f"Utility-cabinet material-slot count changed: {len(materials)}")'
new = 'require(len(materials) == 5, f"Utility-cabinet material-slot count changed: {len(materials)}")'
if text.count(old) != 1:
    raise RuntimeError("Material-slot validation line drifted")
text = text.replace(old, new, 1)

old = '''        x_positions = [6500.0 + 7500.0 * index for index in range(PLACEMENT_COUNT)]
        y_offsets = (-120.0, 40.0, 130.0, -35.0)
        yaw_offsets = (0.0, 1.5, -1.0, 0.5)
        scale_values = (0.98, 1.00, 1.02, 0.99)
        for index, x_cm in enumerate(x_positions):
            y_cm = 8000.0 + y_offsets[index % len(y_offsets)]
'''
new = '''        x_positions = [10000.0 + 16000.0 * index for index in range(PLACEMENT_COUNT)]
        y_offsets = (-90.0, 40.0, 100.0, -25.0, 65.0)
        yaw_offsets = (0.0, 2.0, -2.0, 1.0, -1.0)
        scale_values = (1.00, 0.98, 1.02, 1.00, 0.99)
        for index, x_cm in enumerate(x_positions):
            y_cm = 9700.0 + y_offsets[index % len(y_offsets)]
'''
if text.count(old) != 1:
    raise RuntimeError("Placement block drifted")
text = text.replace(old, new, 1)

namespace = {"__name__": "__main__", "__file__": __file__}
exec(compile(text, str(BASE), "exec"), namespace, namespace)
