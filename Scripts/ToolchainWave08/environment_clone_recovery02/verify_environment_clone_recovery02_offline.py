import ast
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
R1_ATTEMPT = ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY01\attempt_01"
R1_SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_clone_recovery01\invoke_environment_clone_recovery01_once.ps1"
R2_PROBE = ROOT / r"Scripts\ToolchainWave08\environment_clone_recovery02\environment_clone_probe_recovery02.py"
R2_SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_clone_recovery02\invoke_environment_clone_recovery02_once.ps1"
R2_ATTEMPT = ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY02\attempt_01"
R1_CLONE = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
R2_CLONE = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype02.umap")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


authorities = {
    ROOT / r"Docs\AAA_Review\TOOLCHAIN_WAVE08_ENVIRONMENT_M01_CLONE_SMOKE_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json": (4404, "dc763167d80901256c651638e141fc0e73a1ac81d002252806e2d8454b1903ec"),
    R1_ATTEMPT / "probe_result.json": (3535, "db3da125155ecfe0513ac151d5514f994f4315b0a0ef7d23ff5ab6c74ef50cee"),
    R1_ATTEMPT / "terminal_manifest.json": (2723, "7fafd97d452c57b02bb5f75af0a6c442871db5fdd8ddf90365e4b39eeedf6dcb"),
    R1_ATTEMPT / "unreal_stdout.log": (225498, "5f9ac1ef84cb5c1c20d1d8651c7db65089c88658a58c5f285e897313a0a29d25"),
    R1_ATTEMPT / "unreal_stderr.log": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    R1_ATTEMPT / "process_tree_samples.json": (6075, "7b5e2204c67a4a79b762e81df4dd7aa47f2a768fe4a8168916b09bc5600a2233"),
    R1_SUPERVISOR: (15532, "324cc9d88de68ff6540c09e58a3227f08043c102075eb9f04e9beec1f101008a"),
    ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentCloneRecovery01\attempt01_postflight.json": (2834, "7d195dab6aa92f3fa81f57f92eb3b96b4221542513a004583fd2c164caa8931f"),
    R1_CLONE: (8681, "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4"),
    ROOT / "Skyguard52.uproject": (1542, "99461a1a562ede732da52c84f05002dcc88f772cd30fdccd45ff46d6836f3b60"),
    Path(r"D:\SG52T08_ENV01\Skyguard52.uproject"): (3703, "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"),
    ROOT / r"Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap": (6599, "3a3026f0387d2329c8c45e8b28e8889065d0098367933bf0193be39f744f9fd3"),
    Path(r"D:\SG52T08_ENV01\Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_ProductionEnvironment_v4.umap"): (6599, "3a3026f0387d2329c8c45e8b28e8889065d0098367933bf0193be39f744f9fd3"),
}

for path, (size, sha) in authorities.items():
    require(path.is_file(), f"missing authority: {path}")
    require(path.stat().st_size == size, f"byte mismatch: {path}")
    require(digest(path) == sha, f"hash mismatch: {path}")

terminal = json.loads((R1_ATTEMPT / "terminal_manifest.json").read_text(encoding="utf-8-sig"))
probe = json.loads((R1_ATTEMPT / "probe_result.json").read_text(encoding="utf-8-sig"))
stdout = (R1_ATTEMPT / "unreal_stdout.log").read_text(encoding="utf-8", errors="replace")
stderr = (R1_ATTEMPT / "unreal_stderr.log").read_bytes()
samples = json.loads((R1_ATTEMPT / "process_tree_samples.json").read_text(encoding="utf-8-sig"))

require(terminal["classification"] == "FAILED_WITH_EVIDENCE", "failed terminal classification was not preserved")
require(terminal["unreal_launch_count"] == 1 and terminal["retry_count"] == 0, "launch/retry evidence failed")
require(terminal["exit_code"] == 0 and terminal["exit_code_type"] == "System.Int32", "numeric exit evidence failed")
require(not terminal["timed_out"], "attempt timed out")
require(probe["classification"] == "PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE", "probe did not pass")
require(probe["error"] is None, "probe contains an error")
require(len(probe["class_probes"]) == 3, "class probe count is not three")
require(all(row["module_match"] for row in probe["class_probes"]), "module mismatch exists")
require(all((probe[key] for key in ("source_asset_loaded", "clone_asset_absent_before", "clone_asset_created", "clone_asset_saved", "clone_asset_loaded_after", "distinct_package_paths"))), "clone lifecycle evidence failed")
require(not any((probe["source_map_save_attempted"], probe["canonical_asset_save_attempted"], probe["environment_authoring_attempted"])), "prohibited mutation evidence exists")
require(digest(R1_CLONE) == probe["clone_file_sha256"], "clone hash differs from probe receipt")
require(probe["canonical_descriptor_sha256_before"] == probe["canonical_descriptor_sha256_after"], "canonical descriptor changed")
require(probe["isolated_descriptor_sha256_before"] == probe["isolated_descriptor_sha256_after"], "isolated descriptor changed")
require(probe["canonical_source_sha256_before"] == probe["canonical_source_sha256_after"], "canonical map changed")
require(probe["isolated_source_sha256_before"] == probe["isolated_source_sha256_after"], "isolated map changed")
require("SKYGUARD_ENVIRONMENT_CLONE_SMOKE=PASSED_ISOLATED_M01_CLONE_AND_ENVIRONMENT_CAPABILITY_SMOKE" in stdout, "probe success marker missing")
require("Python script executed successfully" in stdout, "Python success marker missing")
require(re.search(r"Success - 0 error\(s\)", stdout) is not None, "zero-error summary missing")
require(stderr == b"", "stderr is not empty")
unreal_pids = {proc["Id"] for sample in samples for proc in sample.get("processes", []) if proc.get("ProcessName", "").startswith("UnrealEditor")}
require(unreal_pids == {40568}, f"unexpected Unreal PID evidence: {unreal_pids}")

probe_source = R2_PROBE.read_text(encoding="utf-8")
ast.parse(probe_source, filename=str(R2_PROBE))
for token in ("/Script/Water.WaterBodyOcean", "/Script/LandmassEditor.LandmassActor", "/Script/PCGGeometryScriptInterop.PCGCreateEmptyDynamicMeshSettings", "duplicate_asset(SOURCE_ASSET, CLONE_ASSET)", "save_asset(CLONE_ASSET"):
    require(token in probe_source, f"Recovery02 probe contract token missing: {token}")

supervisor = R2_SUPERVISOR.read_text(encoding="utf-8")
require("function Assert-PreflightAuthorities" in supervisor, "separate preflight function missing")
require("function Assert-PostflightAuthorities" in supervisor, "separate postflight function missing")
require("function Assert-Authorities([bool]" not in supervisor, "ambiguous Recovery01 authority function remains")
require(supervisor.count("Invoke-CapturedProcess -FilePath $Editor") == 1, "future Unreal launch path count is not one")
require("ReadToEndAsync" in supervisor and "while (-not $process.WaitForExit(1000))" in supervisor, "asynchronous process handling changed")
require("retry_count=0" in supervisor, "zero-retry evidence missing")
require("Clone target already exists before launch" in supervisor, "preflight clone-absence invariant missing")
require("Clone target is missing after execution" in supervisor, "postflight clone-existence invariant missing")
require("Clone hash does not match probe receipt" in supervisor, "postflight clone-hash invariant missing")

require(not R2_ATTEMPT.exists(), "governed Recovery02 attempt namespace exists")
require(not R2_CLONE.exists(), "governed Recovery02 clone exists")
print("PASS")
