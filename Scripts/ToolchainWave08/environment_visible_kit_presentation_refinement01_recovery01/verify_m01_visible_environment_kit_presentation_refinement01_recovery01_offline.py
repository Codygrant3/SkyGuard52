import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
ORIGINAL = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_presentation_refinement01/author_m01_visible_environment_kit_presentation_refinement01.py"
AUTHOR = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_presentation_refinement01_recovery01/author_m01_visible_environment_kit_presentation_refinement01_recovery01.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01VisibleEnvironmentPresentationRefinement01Recovery01/execution_contract.json"
FAILED_FREEZE = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_ATTEMPT01_TERMINAL_FREEZE.json"
INPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01.umap"
FAILED_OUTPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01.umap"
OUTPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01_Recovery01.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_TERMINAL_SUPERVISOR.json"
EMERGENCY = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_RECOVERY01_EMERGENCY_RECEIPT.jsonl"

EXPECTED_ORIGINAL_SHA256 = "2899658124ce2dbf66d6ac15551b6213745184df02958e835e5bc208d3785d7c"
EXPECTED_INPUT_SHA256 = "d5a134978dec578f2833647d95545d228928cd6d30aee86f69e51e69506c8669"
EXPECTED_FAILED_OUTPUT_SHA256 = "016332bec0f58bf245867ace4c8550f237cd9c4f92648c3f89d08208f15e5932"
EXPECTED_FAILED_FREEZE_SHA256 = "aceb486483b51a0a41347ad1fe0b8753f5df61fcf6173dc856821ca7a41115a2"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    for path in (ORIGINAL, AUTHOR, CONTRACT, FAILED_FREEZE, INPUT_MAP, FAILED_OUTPUT_MAP):
        require(path.is_file(), f"required authority missing: {path}")
    require(sha256(ORIGINAL) == EXPECTED_ORIGINAL_SHA256, "original author changed")
    require(sha256(INPUT_MAP) == EXPECTED_INPUT_SHA256, "accepted input map changed")
    require(sha256(FAILED_OUTPUT_MAP) == EXPECTED_FAILED_OUTPUT_SHA256, "failed output changed")
    require(sha256(FAILED_FREEZE) == EXPECTED_FAILED_FREEZE_SHA256, "failed freeze changed")

    wrapper = AUTHOR.read_text(encoding="utf-8")
    ast.parse(wrapper, filename=str(AUTHOR))
    require('("lower_hemisphere_is_solid_color", "lower_hemisphere_is_black", 3)' in wrapper, "bounded property correction missing")
    require('("PresentationRefinement01", "PresentationRefinement01_Recovery01", 5)' in wrapper, "output namespace correction missing")
    require("exec(compile(source" in wrapper, "frozen-source execution binding missing")

    source = ORIGINAL.read_text(encoding="utf-8")
    source = source.replace("lower_hemisphere_is_solid_color", "lower_hemisphere_is_black")
    source = source.replace("PresentationRefinement01", "PresentationRefinement01_Recovery01")
    source = source.replace("PRESENTATION_REFINEMENT01", "PRESENTATION_REFINEMENT01_RECOVERY01")
    source = source.replace("presentation-refinement01", "presentation-refinement01-recovery01")
    ast.parse(source, filename=str(ORIGINAL) + "::Recovery01")
    require("lower_hemisphere_is_solid_color" not in source, "incompatible property remains")
    require("Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01.umap" not in source, "failed map namespace remains")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["correction"]["functional_change_count"] == 1, "correction count mismatch")
    require(contract["execution"]["automatic_retries"] == 0, "retry contract mismatch")
    require(contract["output"]["actor_count"] == 180, "output actor contract mismatch")

    require(not OUTPUT_MAP.exists(), f"future output exists: {OUTPUT_MAP}")
    require(not ATTEMPT.exists(), f"future attempt exists: {ATTEMPT}")
    require(not TERMINAL.exists(), f"future terminal exists: {TERMINAL}")
    require(not EMERGENCY.exists(), f"future emergency receipt exists: {EMERGENCY}")
    print("PASS")


if __name__ == "__main__":
    main()
