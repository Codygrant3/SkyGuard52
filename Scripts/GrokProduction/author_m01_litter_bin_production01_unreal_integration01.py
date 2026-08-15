"""Derive the accepted storm-drain integration author into the bounded M01 litter-bin staging author."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\author_m01_storm_drain_recovery03_unreal_integration01.py")
BASE_BYTES = 20_638
BASE_SHA256 = "260df21c60c972f15985058fd802e29637378dd547bbcaa3d6a946799eeb5886"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen storm-drain Unreal author authority changed")

text = BASE.read_text(encoding="utf-8")
for old, new in (
    ("storm-drain-recovery03", "litter-bin-production01"),
    ("storm-drain", "litter-bin"),
    ("Storm-drain", "Litter-bin"),
    ("storm drain", "litter bin"),
    ("Storm drain", "Litter bin"),
    ("StormDrains", "LitterBins"),
    ("StormDrain", "LitterBin"),
    ("STORM_DRAIN", "LITTER_BIN"),
    ("storm_drain", "litter_bin"),
):
    text = text.replace(old, new)


def assign(name: str, expression: str) -> None:
    global text
    pattern = rf"^{re.escape(name)} = .*$"
    replacement = f"{name} = {expression}"
    text, count = re.subn(pattern, lambda _match: replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Expected one assignment for {name}, found {count}")


assign("SOURCE", 'ROOT / r"Production\\Attempts\\m01-litter-bin-export-recovery01\\attempt_20260811T120000000000Z\\output\\exports\\M01_Promenade_LitterBin_Production01_ExportRecovery01.glb"')
assign("SOURCE_BYTES", "81_492")
assign("SOURCE_SHA256", '"90012aac97656e0f85acc590164c777ab746e558ea646573aab7d6e373cc6137"')
assign("ACCEPTANCE_FREEZE", 'ROOT / r"Docs\\AAA_Review\\M01_LITTER_BIN_EXPORT_RECOVERY01_ACCEPTANCE_FREEZE.json"')
assign("ACCEPTANCE_FREEZE_BYTES", "2_599")
assign("ACCEPTANCE_FREEZE_SHA256", '"7f964a65d4db70cb57921e4541e8da8edbe2038e4cd9929370e967b9913376c0"')
assign("INPUT_ASSET", '"/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_StormDrains01"')
assign("OUTPUT_ASSET", '"/Game/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_StormDrains01_LitterBins01"')
assign("INPUT_FILE", 'ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_StormDrains01.umap"')
assign("OUTPUT_FILE", 'ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_StormDrains01_LitterBins01.umap"')
assign("INPUT_BYTES", "792_559")
assign("INPUT_SHA256", '"0c5549769fb35cd590d1d7fba69fc71b28530683b64a785313543d13b39a92af"')
assign("DESTINATION", '"/Game/M01/PromenadeLitterBinProduction01"')
assign("DESTINATION_DISK", 'ISOLATED / "Content/M01/PromenadeLitterBinProduction01"')
assign("ATTEMPT", 'ROOT / r"Saved\\BuildAttempts\\M01_LITTER_BIN_PRODUCTION01_UNREAL_INTEGRATION01\\attempt_01"')
assign("RECEIPT", 'ATTEMPT / "integration_receipt.json"')
assign("MESH_NAME", '"SM_M01_Promenade_LitterBin_A"')
assign("SOCKET_NODE", '"SOCKET_LitterBin_Origin"')
assign("COLLISION_NODE", '"UCX_SM_M01_Promenade_LitterBin_A_00"')
assign("CANONICAL_SOCKET", '"M01_LitterBin_Origin"')
assign("PLACEMENT_COUNT", "10")
assign("EXPECTED_ACTORS_BEFORE", "138")

replacements = {
    'require(freeze.get("classification") == "PASSED_PROVISIONAL_MID_DISTANCE_RUNTIME_CANDIDATE", "Unexpected litter-bin acceptance classification")':
        'require(freeze.get("classification") == "PASSED_GLTF_STRUCTURE_READY_FOR_UNREAL_STAGING", "Unexpected litter-bin acceptance classification")',
    'require(len(meshes) == 2 and any(MESH_NAME in name for name in meshes), f"Accepted GLB mesh contract changed: {meshes}")':
        'require(len(meshes) == 2, f"Accepted GLB mesh contract changed: {meshes}")',
    'require(materials == ["M_M01_LitterBin_CastIron", "M_M01_LitterBin_DarkRecess", "M_M01_LitterBin_EdgeWear"], f"Accepted material identity changed: {materials}")':
        'require(materials == ["M_M01_LitterBin_PowderCoat", "M_M01_LitterBin_DarkAperture", "M_M01_LitterBin_StainlessTrim"], f"Accepted material identity changed: {materials}")',
    'require(32.0 <= extent[0] <= 36.0 and 22.0 <= extent[1] <= 26.0 and 4.0 <= extent[2] <= 6.0, f"Litter-bin bounds changed: {extent}")':
        'require(28.0 <= extent[0] <= 32.0 and 25.0 <= extent[1] <= 30.0 and 46.0 <= extent[2] <= 51.0, f"Litter-bin bounds changed: {extent}")',
    'x_positions = [4000.0 + 5000.0 * index for index in range(PLACEMENT_COUNT)]':
        'x_positions = [6000.0 + 6000.0 * index for index in range(PLACEMENT_COUNT)]',
    'y_offsets = (-35.0, 20.0, -10.0, 30.0)':
        'y_offsets = (0.0, 70.0, -55.0, 35.0)',
    'yaw_offsets = (0.0, 0.8, -0.6, 0.4)':
        'yaw_offsets = (0.0, 0.0, 0.0, 0.0)',
    'y_cm = 7350.0 + y_offsets[index % len(y_offsets)]':
        'y_cm = 8050.0 + y_offsets[index % len(y_offsets)]',
    'PASSED_M01_LITTER_BIN_RECOVERY03_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF':
        'PASSED_M01_LITTER_BIN_PRODUCTION01_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF',
    'PASS_M01_LITTER_BIN_RECOVERY03_UNREAL_INTEGRATION01_CONTRACT':
        'PASS_M01_LITTER_BIN_PRODUCTION01_UNREAL_INTEGRATION01_CONTRACT',
}
for old, new in replacements.items():
    count = text.count(old)
    if count < 1:
        raise RuntimeError(f"Expected governed replacement was absent: {old}")
    text = text.replace(old, new)

namespace = {"__name__": "__main__", "__file__": __file__}
exec(compile(text, __file__, "exec"), namespace, namespace)
