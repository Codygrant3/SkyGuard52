import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
AUTHOR = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_presentation_refinement01/author_m01_visible_environment_kit_presentation_refinement01.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01VisibleEnvironmentPresentationRefinement01/execution_contract.json"
INPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01.umap"
OUTPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_TERMINAL_SUPERVISOR.json"
EMERGENCY = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01_EMERGENCY_RECEIPT.jsonl"

EXPECTED_INPUT_BYTES = 841114
EXPECTED_INPUT_SHA256 = "d5a134978dec578f2833647d95545d228928cd6d30aee86f69e51e69506c8669"


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
    require(AUTHOR.is_file(), f"author missing: {AUTHOR}")
    require(CONTRACT.is_file(), f"contract missing: {CONTRACT}")
    require(INPUT_MAP.is_file(), f"input map missing: {INPUT_MAP}")
    require(INPUT_MAP.stat().st_size == EXPECTED_INPUT_BYTES, "input map bytes changed")
    require(sha256(INPUT_MAP) == EXPECTED_INPUT_SHA256, "input map hash changed")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["contract_id"] == "M01-VISIBLE-ENVIRONMENT-PRESENTATION-REFINEMENT01", "contract id mismatch")
    require(contract["lighting"]["intensity_lux"] == 2.75, "fill intensity drift")
    require(contract["lighting"]["cast_shadows"] is False, "fill shadow policy drift")
    require(contract["material_variation"]["changed_actors"] == 14, "variation count drift")
    require(contract["execution"]["automatic_retries"] == 0, "retry policy drift")

    source = AUTHOR.read_text(encoding="utf-8")
    ast.parse(source, filename=str(AUTHOR))
    required_tokens = (
        'FILL_LABEL = "M01_PR01_FillSun"',
        "FILL_INTENSITY = 2.75",
        '"pitch": -25.0, "yaw": -105.0',
        'set_editor_property("cast_shadows", False)',
        'set_editor_property("atmosphere_sun_light", False)',
        "should_vary = (row + column) % 2 == 0",
        'PLASTER_SLOT_BY_FAMILY = {',
        'require(transform_state(actor) == before_transform',
        'EXPECTED_OUTPUT_ACTOR_COUNT = 180',
    )
    for token in required_tokens:
        require(token in source, f"author contract token missing: {token}")

    forbidden_tokens = (
        "delete_actor(",
        "delete_asset(",
        "import_asset_tasks(",
        "generate_local(",
        "save_asset(",
        "Start-Process",
    )
    for token in forbidden_tokens:
        require(token not in source, f"forbidden author token present: {token}")

    require(not OUTPUT_MAP.exists(), f"future output map exists: {OUTPUT_MAP}")
    require(not ATTEMPT.exists(), f"future attempt exists: {ATTEMPT}")
    require(not TERMINAL.exists(), f"future terminal exists: {TERMINAL}")
    require(not EMERGENCY.exists(), f"future emergency receipt exists: {EMERGENCY}")

    print("PASS")


if __name__ == "__main__":
    main()
