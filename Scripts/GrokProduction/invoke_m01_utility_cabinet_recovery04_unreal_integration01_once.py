from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\invoke_m01_bicycle_rack_recovery02_unreal_integration01_once.py")
BASE_BYTES = 11633
BASE_SHA256 = "5e53aced1f3fc4a1fa99f4e0bc6db885cb4638eab2d7b4ff0cd6efefaa23a3d5"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Bicycle-rack integration supervisor authority changed")

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
]:
    text = text.replace(old_word, new_word)

start = text.index('ROOT = Path(r"D:\\Skyguard52")\n')
end_marker = "TIMEOUT_SECONDS = 1800\n"
end = text.index(end_marker, start) + len(end_marker)
constants = r'''ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
AUTHORIZATION = ROOT / "Production" / "standing_heavy_process_authorization.json"
AUTHORIZATION_BYTES = 2146
AUTHORIZATION_SHA = "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"
AUTHOR = ROOT / "Scripts" / "GrokProduction" / "author_m01_utility_cabinet_recovery04_unreal_integration01.py"
AUTHOR_BYTES = 6557
AUTHOR_SHA = "52f99be57de2a02ab14dd7e21b4728dd426b6750f4166693e87653641faa9127"
ACCEPTANCE = ROOT / "Docs" / "AAA_Review" / "M01_UTILITY_CABINET_DETERMINISTIC_RECOVERY04_ACCEPTANCE_FREEZE.json"
ACCEPTANCE_BYTES = 1396
ACCEPTANCE_SHA = "72e10e409f4b81b0deb0eda53265ade5926236386052b5e0e7c6cdb9f1cf89df"
SOURCE = ROOT / r"Production\Attempts\m01-utility-cabinet-deterministic-recovery04\attempt_20260811T095000000000Z\output\exports\M01_Promenade_UtilityCabinet_Recovery04.glb"
SOURCE_BYTES = 305848
SOURCE_SHA = "5df31f7b4119599f760bf28e142f5800cdbc4fd043232701c5b3312a4c26e0d2"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3703
PROJECT_SHA = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_MAP = ISOLATED / "Content" / "M01" / "Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01.umap"
INPUT_MAP_BYTES = 751559
INPUT_MAP_SHA = "d175aefdb4d6767e4ef42330ff0652c5d9689130b73b3610537db5c73905cc4e"
OUTPUT_MAP = ISOLATED / "Content" / "M01" / "Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01.umap"
DESTINATION = ISOLATED / "Content" / "M01" / "PromenadeUtilityCabinetRecovery04"
EDITOR = Path(r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe")
EDITOR_BYTES = 512952
EDITOR_SHA = "0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0"
ATTEMPT = ROOT / "Saved" / "BuildAttempts" / "M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01" / "attempt_01"
RECEIPT = ATTEMPT / "integration_receipt.json"
TERMINAL = ROOT / "Saved" / "Reports" / "M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_TERMINAL_SUPERVISOR.json"
TIMEOUT_SECONDS = 1800
'''
text = text[:start] + constants + text[end:]

old = 'if receipt.get("actor_count_before") != 113 or receipt.get("actor_count_after") != 121 or len(receipt.get("placements", [])) != 8:'
new = 'if receipt.get("actor_count_before") != 121 or receipt.get("actor_count_after") != 126 or len(receipt.get("placements", [])) != 5:'
if text.count(old) != 1:
    raise RuntimeError("Actor-count postflight line drifted")
text = text.replace(old, new, 1)

namespace = {"__name__": "__main__", "__file__": __file__}
exec(compile(text, str(BASE), "exec"), namespace, namespace)
