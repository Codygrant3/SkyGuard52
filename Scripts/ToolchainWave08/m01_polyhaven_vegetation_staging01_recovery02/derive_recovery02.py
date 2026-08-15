"""Derive bounded Recovery02 from frozen Recovery01 and exact glTF vertex bounds."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging01_recovery01"
DEST = ROOT / "Scripts/ToolchainWave08/m01_polyhaven_vegetation_staging01_recovery02"
BOUNDS = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_EXACT_GLTF_VERTEX_BOUNDS_AUTHORITY.json"
FAILURE = ROOT / "Docs/AAA_Review/M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json"
SOURCE_RECORDS = {
    "vegetation_staging01_recovery01_contract.json": (7309, "5341488f0a119414b1d44188b0e383a7e50faf6c1cb88be55decceca8e2cf70e"),
    "author_m01_polyhaven_vegetation_staging01_recovery01.py": (20491, "09c8bce91a0dd069f357dd498d210c21c21b7f6e35a46647a38f19a92e4ea3ef"),
    "invoke_m01_polyhaven_vegetation_staging01_recovery01_once.ps1": (12281, "9ea7212b026868132c188ecc955f9f8ff9bfed6881dced329b8d771e6bdceb0c"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def frozen(path: Path, size: int, digest: str) -> None:
    require(path.is_file() and path.stat().st_size == size and sha(path) == digest, f"Frozen authority changed: {path}")


def replace_exact(text: str, old: str, new: str, count: int) -> str:
    require(text.count(old) == count, f"Expected {count} occurrence(s) of {old!r}, found {text.count(old)}")
    return text.replace(old, new)


for name, (size, digest) in SOURCE_RECORDS.items():
    frozen(SOURCE / name, size, digest)
frozen(BOUNDS, 7858, "3528b8c143d6f77f383a13787519d491fc32a5b92cc9d9e882ee0883334c67ab")
frozen(FAILURE, 8712, "fef9027bdbe914b1690572b101c225758a7da27f6250aeee62abe1fc82f0cfe7")

authority = json.loads(BOUNDS.read_text(encoding="utf-8"))
require(authority["classification"] == "PASSED_OFFLINE_EXACT_GLTF_VERTEX_BOUNDS_AUTHORITY", "Bounds authority classification changed")
by_id = {row["asset_id"]: row for row in authority["assets"]}
contract = json.loads((SOURCE / "vegetation_staging01_recovery01_contract.json").read_text(encoding="utf-8"))
contract["schema"] = "skyguard.m01-polyhaven-vegetation-staging01-recovery02.contract.v1"
contract["contract_id"] = "M01-POLYHAVEN-VEGETATION-STAGING01-RECOVERY02"
contract["exact_bounds_authority"] = {"path": str(BOUNDS), "bytes": BOUNDS.stat().st_size, "sha256": sha(BOUNDS)}
contract["recovery01_failure_authority"] = {"path": str(FAILURE), "bytes": FAILURE.stat().st_size, "sha256": sha(FAILURE)}
for asset in contract["assets"]:
    row = by_id[asset["id"]]
    asset["catalog_dimensions_cm"] = asset["expected_dimensions_cm"]
    asset["expected_dimensions_cm"] = row["dimensions_cm"]
    asset["dimension_authority"] = "EXACT_GLTF_TRANSFORMED_POSITION_VERTICES"
fresh = contract["fresh_outputs"]
fresh["asset_root"] = "/Game/M01/SourceBacked/VegetationStaging01Recovery02"
fresh["asset_disk_root"] = r"D:\SG52T08_ENV01\Content\M01\SourceBacked\VegetationStaging01Recovery02"
fresh["map_asset"] = "/Game/M01/Lvl_M01_PolyHavenVegetationStaging01Recovery02"
fresh["map_path"] = r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PolyHavenVegetationStaging01Recovery02.umap"
fresh["attempt"] = r"D:\Skyguard52\Saved\BuildAttempts\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02\attempt_01"
fresh["terminal_manifest"] = r"D:\Skyguard52\Saved\Reports\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02_TERMINAL_MANIFEST.json"
fresh["emergency_receipt"] = r"D:\Skyguard52\Saved\Reports\M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02_EMERGENCY_RECEIPT.jsonl"
(DEST / "vegetation_staging01_recovery02_contract.json").write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

worker = (SOURCE / "author_m01_polyhaven_vegetation_staging01_recovery01.py").read_text(encoding="utf-8")
worker = replace_exact(worker, "m01_polyhaven_vegetation_staging01_recovery01/vegetation_staging01_recovery01_contract.json", "m01_polyhaven_vegetation_staging01_recovery02/vegetation_staging01_recovery02_contract.json", 1)
worker = replace_exact(worker, "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01/attempt_01", "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02/attempt_01", 1)
worker = replace_exact(worker, "skyguard.m01-polyhaven-vegetation-staging01-recovery01.authoring-receipt.v1", "skyguard.m01-polyhaven-vegetation-staging01-recovery02.authoring-receipt.v1", 1)
worker = replace_exact(worker, "PASS_M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_OFFLINE_CONTRACT", "PASS_M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02_OFFLINE_CONTRACT", 1)
worker = replace_exact(worker, "VegetationStaging01Recovery01/{asset_id}", "VegetationStaging01Recovery02/{asset_id}", 1)
(DEST / "author_m01_polyhaven_vegetation_staging01_recovery02.py").write_text(worker, encoding="utf-8")

supervisor = (SOURCE / "invoke_m01_polyhaven_vegetation_staging01_recovery01_once.ps1").read_text(encoding="utf-8")
supervisor = replace_exact(supervisor, "m01_polyhaven_vegetation_staging01_recovery01\\vegetation_staging01_recovery01_contract.json", "m01_polyhaven_vegetation_staging01_recovery02\\vegetation_staging01_recovery02_contract.json", 1)
supervisor = replace_exact(supervisor, "m01_polyhaven_vegetation_staging01_recovery01\\author_m01_polyhaven_vegetation_staging01_recovery01.py", "m01_polyhaven_vegetation_staging01_recovery02\\author_m01_polyhaven_vegetation_staging01_recovery02.py", 1)
supervisor = replace_exact(supervisor, "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01\\attempt_01", "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02\\attempt_01", 1)
supervisor = replace_exact(supervisor, "author_m01_polyhaven_vegetation_staging01_recovery01.py'", "author_m01_polyhaven_vegetation_staging01_recovery02.py'", 1)
supervisor = replace_exact(supervisor, "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_TERMINAL_MANIFEST.json", "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02_TERMINAL_MANIFEST.json", 1)
supervisor = replace_exact(supervisor, "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_EMERGENCY_RECEIPT.jsonl", "M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02_EMERGENCY_RECEIPT.jsonl", 1)
supervisor = replace_exact(supervisor, "VegetationStaging01Recovery01'", "VegetationStaging01Recovery02'", 1)
supervisor = replace_exact(supervisor, "Lvl_M01_PolyHavenVegetationStaging01Recovery01.umap'", "Lvl_M01_PolyHavenVegetationStaging01Recovery02.umap'", 1)
supervisor = replace_exact(supervisor, "skyguard.m01-polyhaven-vegetation-staging01-recovery01.preflight.v1", "skyguard.m01-polyhaven-vegetation-staging01-recovery02.preflight.v1", 1)
supervisor = replace_exact(supervisor, "skyguard.m01-polyhaven-vegetation-staging01-recovery01.terminal-supervisor.v1", "skyguard.m01-polyhaven-vegetation-staging01-recovery02.terminal-supervisor.v1", 1)
supervisor = replace_exact(supervisor, "PASSED_M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY01_OFFLINE_CONTRACT", "PASSED_M01_POLYHAVEN_VEGETATION_STAGING01_RECOVERY02_OFFLINE_CONTRACT", 1)
(DEST / "invoke_m01_polyhaven_vegetation_staging01_recovery02_once.ps1").write_text(supervisor, encoding="utf-8")

print(json.dumps({"classification": "PASSED_RECOVERY02_DERIVATION", "contract": sha(DEST / "vegetation_staging01_recovery02_contract.json"), "worker": sha(DEST / "author_m01_polyhaven_vegetation_staging01_recovery02.py"), "supervisor": sha(DEST / "invoke_m01_polyhaven_vegetation_staging01_recovery02_once.ps1")}, indent=2))
