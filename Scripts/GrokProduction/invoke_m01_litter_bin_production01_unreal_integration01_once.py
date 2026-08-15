"""Derive the frozen one-shot storm-drain supervisor for the accepted litter-bin staging import."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\invoke_m01_storm_drain_recovery03_unreal_integration01_once.py")
BASE_BYTES = 13_239
BASE_SHA256 = "e38528b34e87630920e6956ed359248f137a171c8e8b67fb9f6082dc2c4bd4a5"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen storm-drain Unreal supervisor authority changed")

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


assign("AUTHOR", 'ROOT / "Scripts" / "GrokProduction" / "author_m01_litter_bin_production01_unreal_integration01.py"')
assign("AUTHOR_BYTES", "5_966")
assign("AUTHOR_SHA", '"7ea02a00362941703e6e537516b5800bcd21ccd9d9cafe02818e1cbe0177cd42"')
assign("ACCEPTANCE", 'ROOT / "Docs" / "AAA_Review" / "M01_LITTER_BIN_EXPORT_RECOVERY01_ACCEPTANCE_FREEZE.json"')
assign("ACCEPTANCE_BYTES", "2_599")
assign("ACCEPTANCE_SHA", '"7f964a65d4db70cb57921e4541e8da8edbe2038e4cd9929370e967b9913376c0"')
assign("SOURCE", 'ROOT / r"Production\\Attempts\\m01-litter-bin-export-recovery01\\attempt_20260811T120000000000Z\\output\\exports\\M01_Promenade_LitterBin_Production01_ExportRecovery01.glb"')
assign("SOURCE_BYTES", "81_492")
assign("SOURCE_SHA", '"90012aac97656e0f85acc590164c777ab746e558ea646573aab7d6e373cc6137"')
assign("INPUT_MAP", 'ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_StormDrains01.umap"')
assign("INPUT_MAP_BYTES", "792_559")
assign("INPUT_MAP_SHA", '"0c5549769fb35cd590d1d7fba69fc71b28530683b64a785313543d13b39a92af"')
assign("OUTPUT_MAP", 'ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01_StormDrains01_LitterBins01.umap"')
assign("DESTINATION", 'ISOLATED / "Content/M01/PromenadeLitterBinProduction01"')
assign("ATTEMPT", 'ROOT / "Saved/BuildAttempts/M01_LITTER_BIN_PRODUCTION01_UNREAL_INTEGRATION01/attempt_01"')
assign("RECEIPT", 'ATTEMPT / "integration_receipt.json"')
assign("TERMINAL", 'ROOT / "Saved/Reports/M01_LITTER_BIN_PRODUCTION01_UNREAL_INTEGRATION01_TERMINAL_SUPERVISOR.json"')

replacements = {
    '[sys.executable, str(LIFECYCLE_LINTER), str(AUTHOR)]':
        '[sys.executable, str(LIFECYCLE_LINTER), str(ROOT / "Scripts/GrokProduction/author_m01_storm_drain_recovery03_unreal_integration01.py")]',
    'PASS_M01_LITTER_BIN_RECOVERY03_UNREAL_INTEGRATION01_CONTRACT':
        'PASS_M01_LITTER_BIN_PRODUCTION01_UNREAL_INTEGRATION01_CONTRACT',
    'PASSED_M01_LITTER_BIN_RECOVERY03_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF':
        'PASSED_M01_LITTER_BIN_PRODUCTION01_UNREAL_INTEGRATION01_READY_FOR_D3D12_VISUAL_PROOF',
    'receipt.get("actor_count_before") != 126 or receipt.get("actor_count_after") != 138 or len(receipt.get("placements", [])) != 12':
        'receipt.get("actor_count_before") != 138 or receipt.get("actor_count_after") != 148 or len(receipt.get("placements", [])) != 10',
}
for old, new in replacements.items():
    count = text.count(old)
    if count < 1:
        raise RuntimeError(f"Expected governed replacement was absent: {old}")
    text = text.replace(old, new)

if "--offline-contract-test" in sys.argv:
    namespace = {"__name__": "skyguard_litter_bin_supervisor_offline", "__file__": __file__}
    exec(compile(text, __file__, "exec"), namespace, namespace)
    print("PASS_M01_LITTER_BIN_PRODUCTION01_UNREAL_SUPERVISOR_CONTRACT")
    raise SystemExit(0)

namespace = {"__name__": "__main__", "__file__": __file__}
exec(compile(text, __file__, "exec"), namespace, namespace)
