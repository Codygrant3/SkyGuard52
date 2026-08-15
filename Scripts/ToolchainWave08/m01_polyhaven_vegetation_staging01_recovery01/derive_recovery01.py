"""Derive the bounded Recovery01 staging files from frozen Attempt01 sources."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging01"
DEST = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging01_recovery01"
REFLECTION_FREEZE = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_REFLECTION_PROBE_TERMINAL_FREEZE.json"
REFLECTION_RECEIPT = ROOT / "Saved/BuildAttempts/M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_REFLECTION_PROBE/attempt_01/reflection_receipt.json"

SOURCE_RECORDS = {
    "vegetation_staging01_contract.json": (6178, "b3eff1db116e9f02889f4c4c114590d2e9e38170bfa017d4292154c0ec676e53"),
    "author_m01_polyhaven_vegetation_staging01.py": (20040, "3bba42250770fb471db7813f7b1d15e599c977ce00ed17a3adce4e44ed33d2c6"),
    "invoke_m01_polyhaven_vegetation_staging01_once.ps1": (11920, "61fdfb64c35161558d1f172768befdcb88a6192b4a0698a42243e180473b4f02"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def frozen(path: Path, size: int, digest: str) -> None:
    require(path.is_file() and path.stat().st_size == size and sha(path) == digest, f"Frozen source changed: {path}")


def replace_exact(text: str, old: str, new: str, count: int) -> str:
    require(text.count(old) == count, f"Expected {count} occurrence(s) of {old!r}, found {text.count(old)}")
    return text.replace(old, new)


for name, (size, digest) in SOURCE_RECORDS.items():
    frozen(SOURCE / name, size, digest)
frozen(REFLECTION_FREEZE, 2404, "45407419e75220df5a2ca0337418ec8487d7ef8313ada500d04f1f19a543db31")
frozen(REFLECTION_RECEIPT, 3697, "c7eb7e429aec3308a658bbe4e16550698745c2c6761262f7eaafe97f5951b5b0")
reflection = json.loads(REFLECTION_RECEIPT.read_text(encoding="utf-8"))
require(reflection["classification"] == "PASSED_UE58_INTERCHANGE_REFLECTION_READY_FOR_RECOVERY01_STAGING_DESIGN", "Reflection receipt classification changed")
require(reflection["mesh_pipeline"]["generate_lightmap_u_vs"]["readable"] and reflection["mesh_pipeline"]["generate_lightmap_u_vs"]["writable"], "Corrected property is not read/write")

contract = json.loads((SOURCE / "vegetation_staging01_contract.json").read_text(encoding="utf-8"))
contract["schema"] = "skyguard.m01-polyhaven-vegetation-staging01-recovery01.contract.v1"
contract["contract_id"] = "M01-POLYHAVEN-VEGETATION-STAGING01-RECOVERY01"
contract["compatibility_authority"] = {
    "reflection_freeze": {"path": str(REFLECTION_FREEZE), "bytes": 2404, "sha256": sha(REFLECTION_FREEZE)},
    "reflection_receipt": {"path": str(REFLECTION_RECEIPT), "bytes": 3697, "sha256": sha(REFLECTION_RECEIPT)},
    "corrected_property": "generate_lightmap_u_vs",
    "rejected_property": "generate_lightmap_uvs",
}
fresh = contract["fresh_outputs"]
fresh["asset_root"] = "/Game/M01/SourceBacked/VegetationStaging01Recovery01"
fresh["asset_disk_root"] = r"D:\SG52T08_ENV01\Content\M01\SourceBacked\VegetationStaging01Recovery01"
fresh["map_asset"] = "/Game/M01/Lvl_M01_PolyHavenVegetationStaging01Recovery01"
fresh["map_path"] = r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PolyHavenVegetationStaging01Recovery01.umap"
fresh["attempt"] = r"D:\Skyguard52\Saved\BuildAttempts\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01\attempt_01"
fresh["terminal_manifest"] = r"D:\Skyguard52\Saved\Reports\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_TERMINAL_MANIFEST.json"
fresh["emergency_receipt"] = r"D:\Skyguard52\Saved\Reports\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_EMERGENCY_RECEIPT.jsonl"
(DEST / "vegetation_staging01_recovery01_contract.json").write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

worker = (SOURCE / "author_m01_polyhaven_vegetation_staging01.py").read_text(encoding="utf-8")
worker = replace_exact(worker, "m01_polyhaven_vegetation_staging01/vegetation_staging01_contract.json", "m01_polyhaven_vegetation_staging01_recovery01/vegetation_staging01_recovery01_contract.json", 1)
worker = replace_exact(worker, "M01_POLYHAVEN_VEGETATION_STAGING01/attempt_01", "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01/attempt_01", 1)
worker = replace_exact(worker, 'set_editor_property("generate_lightmap_uvs", True)', 'set_editor_property("generate_lightmap_u_vs", True)', 1)
worker = replace_exact(worker, "skyguard.m01-polyhaven-vegetation-staging01.authoring-receipt.v1", "skyguard.m01-polyhaven-vegetation-staging01-recovery01.authoring-receipt.v1", 1)
(DEST / "author_m01_polyhaven_vegetation_staging01_recovery01.py").write_text(worker, encoding="utf-8")

supervisor = (SOURCE / "invoke_m01_polyhaven_vegetation_staging01_once.ps1").read_text(encoding="utf-8")
supervisor = replace_exact(supervisor, "Scripts\\ToolchainWave08\\m01_polyhaven_vegetation_staging01\\vegetation_staging01_contract.json", "Scripts\\ToolchainWave08\\m01_polyhaven_vegetation_staging01_recovery01\\vegetation_staging01_recovery01_contract.json", 1)
supervisor = replace_exact(supervisor, "Scripts\\ToolchainWave08\\m01_polyhaven_vegetation_staging01\\author_m01_polyhaven_vegetation_staging01.py", "Scripts\\ToolchainWave08\\m01_polyhaven_vegetation_staging01_recovery01\\author_m01_polyhaven_vegetation_staging01_recovery01.py", 1)
supervisor = replace_exact(supervisor, "M01_POLYHAVEN_VEGETATION_STAGING01\\attempt_01", "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01\\attempt_01", 1)
supervisor = replace_exact(supervisor, "author_m01_polyhaven_vegetation_staging01.py'", "author_m01_polyhaven_vegetation_staging01_recovery01.py'", 1)
supervisor = replace_exact(supervisor, "M01_POLYHAVEN_VEGETATION_STAGING01_TERMINAL_MANIFEST.json", "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_TERMINAL_MANIFEST.json", 1)
supervisor = replace_exact(supervisor, "M01_POLYHAVEN_VEGETATION_STAGING01_EMERGENCY_RECEIPT.jsonl", "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_EMERGENCY_RECEIPT.jsonl", 1)
supervisor = replace_exact(supervisor, "VegetationStaging01'", "VegetationStaging01Recovery01'", 1)
supervisor = replace_exact(supervisor, "Lvl_M01_PolyHavenVegetationStaging01.umap'", "Lvl_M01_PolyHavenVegetationStaging01Recovery01.umap'", 1)
supervisor = replace_exact(supervisor, "skyguard.m01-polyhaven-vegetation-staging01.preflight.v1", "skyguard.m01-polyhaven-vegetation-staging01-recovery01.preflight.v1", 1)
supervisor = replace_exact(supervisor, "skyguard.m01-polyhaven-vegetation-staging01.terminal-supervisor.v1", "skyguard.m01-polyhaven-vegetation-staging01-recovery01.terminal-supervisor.v1", 1)
(DEST / "invoke_m01_polyhaven_vegetation_staging01_recovery01_once.ps1").write_text(supervisor, encoding="utf-8")

print(json.dumps({"classification": "PASSED_RECOVERY01_DERIVATION", "contract": sha(DEST / "vegetation_staging01_recovery01_contract.json"), "worker": sha(DEST / "author_m01_polyhaven_vegetation_staging01_recovery01.py"), "supervisor": sha(DEST / "invoke_m01_polyhaven_vegetation_staging01_recovery01_once.ps1")}, indent=2))
