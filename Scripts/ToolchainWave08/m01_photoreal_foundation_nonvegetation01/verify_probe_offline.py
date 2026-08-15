from __future__ import annotations

import ast
import pathlib


ROOT = pathlib.Path(r"D:\Skyguard52")
HERE = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_nonvegetation01"
PROBE = HERE / "probe_current_map.py"
SUPERVISOR = HERE / "invoke_probe_once.ps1"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_NONVEGETATION01_PROBE\attempt_01"
OUTPUT_MAP = pathlib.Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_NonVegetation01.umap")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


probe = PROBE.read_text(encoding="utf-8")
supervisor = SUPERVISOR.read_text(encoding="utf-8")
ast.parse(probe, filename=str(PROBE))
require(supervisor.count("Start-Process -FilePath $Editor") == 1, "Supervisor must contain exactly one Unreal launch")
require("retry_count = 0" in supervisor, "Zero-retry evidence missing")
require("-NullRHI" in supervisor and "-NoSaveOnExit" in supervisor, "Read-only Unreal switches missing")
require("save_current_level" not in probe and "save_asset" not in probe, "Probe contains a save path")
require("spawn_actor" not in probe and "destroy_actor" not in probe, "Probe contains an actor mutation path")
require("PASSED_READY_FOR_M01_NONVEGETATION01_AUTHORING" in probe, "Probe success classification missing")
require(not ATTEMPT.exists(), "Future probe attempt already exists")
require(not OUTPUT_MAP.exists(), "Future authoring output map already exists")
print("PASS")
