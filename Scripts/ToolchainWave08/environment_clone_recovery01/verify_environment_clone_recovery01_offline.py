import ast
import difflib
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ORIGINAL = ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE\attempt_01\environment_clone_probe.py"
PROBE = ROOT / r"Scripts\ToolchainWave08\environment_clone_recovery01\environment_clone_probe_recovery01.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_clone_recovery01\invoke_environment_clone_recovery01_once.ps1"
ATTEMPT = ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY01\attempt_01"
CLONE = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


authorities = {
    Path(r"D:\Skyguard52\Docs\AAA_Review\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_ATTEMPT01_TERMINAL_FREEZE.json"): (4229, "add1b36607fc51c3224fe4618cebd6bb7d80ea8ef5db7602d3c65044908c1e5d"),
    Path(r"D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE\attempt_01\terminal_manifest.json"): (3960, "203b60b942143b7f492d00a95aaca8c6d9a9fc23e2898273f74a79ee0257119b"),
    Path(r"D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE\attempt_01\probe_result.json"): (2961, "9b56b8610cbb4b77917ba6f4d16802c45eaa02a700875d9b673ccf359344b75b"),
    Path(r"D:\Skyguard52\Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE\attempt_01\unreal_stdout.log"): (225846, "01994691ba55681fc7715430f63003c6a3baeb8c7cf165684173f93655ebf249"),
    Path(r"D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_ENVIRONMENT_PREPARE_TERMINAL.json"): (735239, "1e467aa78e73cf117c4d13a8116022587479c83f0a952fcee43c151eb0059387"),
    Path(r"D:\Skyguard52\Docs\Toolchain\ToolchainWave08\environment_prototype_contract.json"): (3645, "d48c1f86ea5cf6c8387446c75dd99fd905cf01c81d1181d409dcb1ff35317ef8"),
    Path(r"D:\SG52T08_ENV01\Skyguard52.uproject"): (3703, "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"),
    Path(r"D:\Skyguard52\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap"): (6599, "3a3026f0387d2329c8c45e8b28e8889065d0098367933bf0193be39f744f9fd3"),
    Path(r"D:\SG52T08_ENV01\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap"): (6599, "3a3026f0387d2329c8c45e8b28e8889065d0098367933bf0193be39f744f9fd3"),
}

reflection = {
    Path(r"D:\UE_5.8\Engine\Plugins\Experimental\Water\Intermediate\Build\Win64\UnrealEditor\Inc\Water\UHT\WaterBodyOceanActor.generated.h"): (5334, "1627302c59610317812c076b6e276dc4abb8175eb5e2d4a4933aa409bd385908", 'TEXT("/Script/Water")', "AWaterBodyOcean"),
    Path(r"D:\UE_5.8\Engine\Plugins\Experimental\Landmass\Intermediate\Build\Win64\UnrealEditor\Inc\LandmassEditor\UHT\LandmassActor.generated.h"): (4763, "433f64d4c9e1ef37a0624fa9e86af36bd2b3027d6a99e30062bda3e17e08a2c6", 'TEXT("/Script/LandmassEditor")', "ALandmassActor"),
    Path(r"D:\UE_5.8\Engine\Plugins\PCGInterops\PCGGeometryScriptInterop\Intermediate\Build\Win64\UnrealEditor\Inc\PCGGeometryScriptInterop\UHT\PCGCreateEmptyDynamicMesh.generated.h"): (3914, "40ac05a3645df561c33afd709761fc1b03e61c551faeae8d881d3d58081e2e27", 'TEXT("/Script/PCGGeometryScriptInterop")', "UPCGCreateEmptyDynamicMeshSettings"),
}

for path, (size, digest) in authorities.items():
    require(path.is_file(), f"missing authority: {path}")
    require(path.stat().st_size == size, f"byte mismatch: {path}")
    require(sha256(path) == digest, f"hash mismatch: {path}")

for path, (size, digest, package_token, class_token) in reflection.items():
    require(path.is_file(), f"missing reflection authority: {path}")
    require(path.stat().st_size == size, f"reflection byte mismatch: {path}")
    require(sha256(path) == digest, f"reflection hash mismatch: {path}")
    text = path.read_text(encoding="utf-8", errors="strict")
    require(package_token in text and class_token in text, f"reflection evidence missing: {path}")

probe_text = PROBE.read_text(encoding="utf-8")
ast.parse(probe_text, filename=str(PROBE))
required_paths = (
    "/Script/Water.WaterBodyOcean",
    "/Script/LandmassEditor.LandmassActor",
    "/Script/PCGGeometryScriptInterop.PCGCreateEmptyDynamicMeshSettings",
)
for token in required_paths:
    require(token in probe_text, f"corrected class path missing: {token}")
require("/Script/Landmass.LandmassBlueprintBrushBase" not in probe_text, "invalid Landmass path remains")
require(probe_text.index("for class_path, expected_module in CLASS_PROBES") < probe_text.index("duplicate_asset"), "capability probes do not precede duplication")
require("duplicate_asset(SOURCE_ASSET, CLONE_ASSET)" in probe_text, "Unreal API duplication changed")
require("save_asset(CLONE_ASSET" in probe_text, "clone save allowlist changed")
require("save_asset(SOURCE_ASSET" not in probe_text, "source save is present")

old_lines = ORIGINAL.read_text(encoding="utf-8").splitlines()
new_lines = probe_text.splitlines()
diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
changed = [line for line in diff if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]
allowed_fragments = (
    "TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE",
    "environment-clone-smoke-probe",
    "/Script/Landmass.LandmassBlueprintBrushBase",
    "/Script/LandmassEditor.LandmassActor",
    '"Landmass"',
    '"LandmassEditor"',
)
require(changed, "probe diff is empty")
for line in changed:
    require(any(fragment in line for fragment in allowed_fragments), f"out-of-contract probe change: {line}")

supervisor_text = SUPERVISOR.read_text(encoding="utf-8")
require(supervisor_text.count("Invoke-CapturedProcess -FilePath $Editor") == 1, "future Unreal launch count is not exactly one")
require("Start-Process" not in supervisor_text, "alternate Start-Process launcher exists")
require("while (-not $process.WaitForExit(1000))" in supervisor_text, "asynchronous process wait missing")
require("ReadToEndAsync" in supervisor_text, "asynchronous stdout/stderr draining missing")
require("retry_count=0" in supervisor_text, "zero-retry terminal evidence missing")
for token in required_paths:
    require(token in supervisor_text, f"supervisor class authority missing: {token}")

require(not ATTEMPT.exists(), "future Recovery01 attempt namespace exists")
require(not CLONE.exists(), "future clone target exists")

preparation = json.loads(Path(r"D:\Skyguard52\Saved\Reports\TOOLCHAIN_WAVE08_ENVIRONMENT_PREPARE_TERMINAL.json").read_text(encoding="utf-8-sig"))
require(preparation["classification"] == "PASSED_ISOLATED_M01_VIEW_READY_FOR_SINGLE_UNREAL_CLONE_SMOKE", "preparation classification changed")
require(len(preparation["output_inventory"]) == 2006, "preparation inventory count changed")

print("PASS")
