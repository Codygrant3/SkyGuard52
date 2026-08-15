"""Offline verifier for M01 accepted-module assembly reversible contract."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / r"Docs\Toolchain\M01_ACCEPTED_MODULE_ASSEMBLY_REVERSIBLE_CONTRACT.json"
AUTHOR = ROOT / r"Scripts\GrokProduction\author_m01_accepted_module_assembly_v1.py"
SUPERVISOR = ROOT / r"Scripts\GrokProduction\invoke_m01_accepted_module_assembly_v1_once.ps1"
PLAYABLE = ROOT / r"Content\Skyguard\Maps\Lvl_M01_CoastalIntercept_Playable_v1.umap"
GW02 = Path(r"D:\SG52T08_ENV01\Content\T08\GW02")
CORRIDOR = Path(
    r"D:\SG52T08_ENV01\Content\M01\CoastalCorridorC06R01\M01_CoastalCorridor_C06R01_UNREAL_READY"
)
PRIOR_FAILED_ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_v1\attempt_01"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_v1_RECOVERY01\attempt_01"
MAP_DISK = ROOT / r"Content\Skyguard\Maps\Assembly\Lvl_M01_AcceptedModuleAssembly_v1.umap"
PLAYABLE_BYTES = 70_545
PLAYABLE_SHA256 = "9d2ca2e50b446f488926bdd8a29eca9fe33d62ec25656fc77ca55997f5a08afa"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (CONTRACT, AUTHOR, SUPERVISOR, PLAYABLE):
        require(path.is_file(), f"Missing required file: {path}")

    require(PLAYABLE.stat().st_size == PLAYABLE_BYTES, "Playable map byte count changed")
    require(sha256(PLAYABLE) == PLAYABLE_SHA256, "Playable map hash changed")
    require(GW02.is_dir(), "GW02 accepted import root missing on SG52T08")
    require(CORRIDOR.is_dir(), "Corridor UNREAL_READY root missing on SG52T08")

    for name in (
        "SM_M01_PrewarWindowBay_A01_FrameFacadeHardware.uasset",
        "SM_M01_PrewarWindowBay_A01_Glass.uasset",
        "SM_M01_PrewarWindowBay_A01_Interior.uasset",
    ):
        require(
            (GW02 / "StaticMeshes" / name).is_file(),
            f"GW02 mesh missing: {name}",
        )

    for name in (
        "SM_M01_CoastalCorridor_C06R01_TERRAIN.uasset",
        "SM_M01_CoastalCorridor_C06R01_HARDSCAPE.uasset",
        "SM_M01_CoastalCorridor_C06R01_DETAILS.uasset",
        "SM_M01_CoastalCorridor_C06R01_CONTACT.uasset",
    ):
        require(
            (CORRIDOR / "StaticMeshes" / name).is_file(),
            f"Corridor mesh missing: {name}",
        )

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["rules"]["runtime_promotion"] is False, "runtime_promotion must be false")
    require(
        contract["source_playable_map"]["immutable"] is True,
        "Playable must be marked immutable",
    )
    require(
        contract["fresh_derived_map"]["game_path"]
        == "/Game/Skyguard/Maps/Assembly/Lvl_M01_AcceptedModuleAssembly_v1",
        "Fresh derived map path changed",
    )
    require(
        contract["accepted_window_module"]["candidates_game_path"]
        == "/Game/Skyguard/Candidates/M01/WindowBayR06",
        "Window Candidates path changed",
    )
    require(contract["launch_policy"]["null_rhi_structural_only"] is True, "NullRHI policy missing")
    require(contract["rules"]["blender"] is False, "Blender must be forbidden")

    author_text = AUTHOR.read_text(encoding="utf-8")
    ast.parse(author_text)
    for token in (
        "phase_a(",
        "phase_b(",
        "WINDOW_CANDIDATES_GAME",
        "M01/AcceptedModules",
        "runtime_promotion\": False",
        "Lvl_M01_AcceptedModuleAssembly_v1",
        "ensure_junction",
        "validate_playable_immutable",
        "duplicate_asset(\n        source_package, dest_package_path\n    )",
        "M01_ACCEPTED_MODULE_ASSEMBLY_v1_RECOVERY01",
    ):
        require(token in author_text, f"Author token missing: {token}")
    for forbidden in (
        "worker_m01_hero",
        "bpy.",
        "PLAYABLE_DISK.write",
        "save_asset(PLAYABLE",
    ):
        require(forbidden not in author_text, f"Forbidden author behavior: {forbidden}")

    supervisor_text = SUPERVISOR.read_text(encoding="utf-8")
    require(
        supervisor_text.count("Start-Process -FilePath $Editor") == 1,
        "Supervisor must contain exactly one Unreal launch",
    )
    require("-NullRHI" in supervisor_text, "NullRHI switch missing")
    require("AuthorizeSingleUnreal" in supervisor_text, "Mechanical guard missing")
    require("Skyguard52.uproject" in supervisor_text, "Canonical project missing")
    require(
        "standing_heavy_process_authorization.json" in supervisor_text,
        "Standing authorization missing",
    )
    require("retry_count = 0" in supervisor_text or "retry_count=0" in supervisor_text, "Zero-retry evidence missing")

    require(PRIOR_FAILED_ATTEMPT.is_dir(), "Prior failed attempt_01 must remain as evidence")
    require(
        "duplicate_asset() takes at most 2 arguments"
        in (PRIOR_FAILED_ATTEMPT / "assembly_receipt.json").read_text(encoding="utf-8"),
        "Prior failed receipt does not record the duplicate_asset API failure",
    )
    require(not ATTEMPT.exists(), "Fresh Recovery01 attempt namespace already exists")
    require(not MAP_DISK.exists(), "Fresh assembly map already exists")

    print("PASS_M01_ACCEPTED_MODULE_ASSEMBLY_V1_OFFLINE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
