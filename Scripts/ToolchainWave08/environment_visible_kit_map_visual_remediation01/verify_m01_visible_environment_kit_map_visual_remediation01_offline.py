import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUTHOR = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_map_visual_remediation01/author_m01_visible_environment_kit_map_visual_remediation01.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01VisibleEnvironmentKitMapVisualRemediation01/execution_contract.json"
AUTHORIZATION = ROOT / "Production/standing_heavy_process_authorization.json"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_Recovery02.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_TERMINAL_SUPERVISOR.json"
EXPECTED_INPUT_BYTES = 827791
EXPECTED_INPUT_SHA256 = "186cb23fc67c78613453552d1da9c203161a63b12cc894f66019784e04b00fee"
EXPECTED_AUTHORIZATION_SHA256 = "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


for path in (AUTHOR, CONTRACT, AUTHORIZATION, INPUT_MAP):
    require(path.is_file(), f"Missing offline authority: {path}")
require(INPUT_MAP.stat().st_size == EXPECTED_INPUT_BYTES, "Accepted input map byte count changed")
require(sha256(INPUT_MAP) == EXPECTED_INPUT_SHA256, "Accepted input map hash changed")
require(sha256(AUTHORIZATION) == EXPECTED_AUTHORIZATION_SHA256, "Standing authorization hash changed")
require(not OUTPUT_MAP.exists(), f"Fresh output map already exists: {OUTPUT_MAP}")
require(not ATTEMPT.exists(), f"Fresh attempt namespace already exists: {ATTEMPT}")
require(not TERMINAL.exists(), f"Fresh terminal namespace already exists: {TERMINAL}")

source = AUTHOR.read_text(encoding="utf-8")
compile(source, str(AUTHOR), "exec")
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_UNREAL_AUTHORING", "Unexpected contract classification")
require(contract["bounded_changes"]["building_yaw_degrees"] == 180.0, "Building yaw contract changed")
require(contract["bounded_changes"]["skylight"]["intensity"] == 3.25, "Skylight intensity contract changed")

required_tokens = (
    "TARGET_BUILDING_YAW = 180.0",
    "TARGET_SKYLIGHT_INTENSITY = 3.25",
    "actor_location_for_center",
    "lower_hemisphere_is_solid_color",
    "EXPECTED_BUILDING_PLACEMENTS = 27",
    "EXPECTED_CITY_ACTORS = 81",
    "facade_facing_ocean",
    "levels.new_level_from_template",
    "levels.save_current_level()",
)
for token in required_tokens:
    require(token in source, f"Required authoring token missing: {token}")

for forbidden in (
    "delete_asset",
    "rename_asset",
    "import_asset",
    "import_task",
    "SystemLibrary.execute_console_command",
    "subprocess",
):
    require(forbidden not in source, f"Forbidden authoring token present: {forbidden}")

print("PASS")
