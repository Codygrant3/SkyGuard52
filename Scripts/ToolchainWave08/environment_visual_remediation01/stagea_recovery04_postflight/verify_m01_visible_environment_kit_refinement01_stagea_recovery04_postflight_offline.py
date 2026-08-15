from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery04_postflight\adjudicate_m01_visible_environment_kit_refinement01_stagea_recovery04.py"
TEST = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery04_postflight\test_m01_visible_environment_kit_refinement01_stagea_recovery04_postflight.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery04Postflight\contract.json"
RECOVERY04_FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04_OFFLINE_SOURCE_FREEZE.json"
FUTURE = (
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04_POSTFLIGHT.json",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04_VISUAL_REVIEW_MANIFEST.json",
)


def require(value, message):
    if not value:
        raise RuntimeError(message)


def main() -> None:
    for path in (SCRIPT, TEST, CONTRACT, RECOVERY04_FREEZE):
        require(path.is_file() and path.stat().st_size > 0, f"missing offline authority: {path}")
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
    imported_roots = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    require(not ({"subprocess", "socket", "requests", "urllib"} & imported_roots), "postflight contains process or network imports")
    source = SCRIPT.read_text(encoding="utf-8")
    for token in (
        "exact_expected_files",
        "verify_supervisor",
        "verify_inventories",
        "verify_glbs",
        "validate_attempt",
        "PASSED_AUTOMATIC_READY_FOR_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
        "DIRECT_FULL_RESOLUTION_VISUAL_REVIEW_OF_18_ORIGINAL_RENDERS",
        "recovery03_terminal_members_verified",
        "recovery03_artifact_members_verified",
        "refusing to overwrite",
    ):
        require(token in source, f"required postflight token missing: {token}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    require(contract.get("classification") == "OFFLINE_SUPPLEMENTAL_POSTFLIGHT_DESIGN", "contract classification mismatch")
    boundaries = contract.get("boundaries") or {}
    require(boundaries.get("launches_blender") == 0 and boundaries.get("launches_unreal") == 0, "contract permits a heavy launch")
    require(boundaries.get("mutates_attempt_or_output") is False, "contract permits attempt or output mutation")
    freeze = json.loads(RECOVERY04_FREEZE.read_text(encoding="utf-8-sig"))
    require(freeze.get("classification") == "PASSED_READY_FOR_RECOVERY04_POSTFLIGHT_BINDING", "Recovery04 freeze classification mismatch")
    require(freeze.get("member_count") == 16 and len(freeze.get("members") or []) == 16, "Recovery04 freeze cardinality mismatch")
    require(all(not path.exists() for path in FUTURE), "future postflight evidence already exists")
    print("CLASSIFICATION=PASS")


if __name__ == "__main__":
    main()
