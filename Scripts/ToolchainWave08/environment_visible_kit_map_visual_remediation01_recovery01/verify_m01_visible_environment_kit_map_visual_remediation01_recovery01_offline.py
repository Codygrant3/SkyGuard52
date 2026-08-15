import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ORIGINAL = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_map_visual_remediation01/author_m01_visible_environment_kit_map_visual_remediation01.py"
AUTHOR = ROOT / "Scripts/ToolchainWave08/environment_visible_kit_map_visual_remediation01_recovery01/author_m01_visible_environment_kit_map_visual_remediation01_recovery01.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01VisibleEnvironmentKitMapVisualRemediation01Recovery01/execution_contract.json"
FAILURE_FREEZE = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_ATTEMPT01_TERMINAL_FREEZE.json"
HEADER = Path(r"D:\UE_5.8\Engine\Source\Runtime\Engine\Classes\Components\SkyLightComponent.h")
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_Recovery02.umap")
FAILED_OUTPUT = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01_Recovery01.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01_RECOVERY01_TERMINAL_SUPERVISOR.json"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


expected = {
    ORIGINAL: "517044b54109fd951b4135594f47cc514047fd60e43254435c1e30913cbce0d2",
    FAILURE_FREEZE: "e13134fdfaefdf8e471599c0238eed12898e43cf038dc1f685cdda188d26662b",
    HEADER: "cb30c4f34c2d354a3b09d60ca9dfce0ddd98a6cad3a1a053782573866935cd20",
    INPUT_MAP: "186cb23fc67c78613453552d1da9c203161a63b12cc894f66019784e04b00fee",
    FAILED_OUTPUT: "7ac73d1928abbf13214a0ea3f61e5b1fa21b2d11ec9d1136200f0d1e8022ddfc",
}
for path, digest in expected.items():
    require(path.is_file(), f"Missing Recovery01 authority: {path}")
    require(sha256(path) == digest, f"Recovery01 authority hash mismatch: {path}")
for path in (AUTHOR, CONTRACT):
    require(path.is_file(), f"Missing Recovery01 offline artifact: {path}")
require(not OUTPUT_MAP.exists(), f"Fresh Recovery01 output exists: {OUTPUT_MAP}")
require(not ATTEMPT.exists(), f"Fresh Recovery01 attempt exists: {ATTEMPT}")
require(not TERMINAL.exists(), f"Fresh Recovery01 terminal exists: {TERMINAL}")

author_source = AUTHOR.read_text(encoding="utf-8")
compile(author_source, str(AUTHOR), "exec")
for token in (
    "lower_hemisphere_is_solid_color",
    "lower_hemisphere_is_black",
    "VisualRemediation01_Recovery01",
    "VISUAL_REMEDIATION01_RECOVERY01",
    "EXPECTED_ORIGINAL_SHA256",
):
    require(token in author_source, f"Recovery01 binding token missing: {token}")

header_source = HEADER.read_text(encoding="utf-8", errors="strict")
require("bool bLowerHemisphereIsBlack;" in header_source, "Installed UE 5.8 lower-hemisphere authority changed")
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_UNREAL_AUTHORING", "Unexpected Recovery01 contract classification")
require(contract["installed_authority"]["python_property"] == "lower_hemisphere_is_black", "Recovery01 Python property contract changed")
require(contract["unchanged_functional_contract"]["lower_hemisphere_is_black"] is False, "Recovery01 lower-hemisphere value changed")

print("PASS")
