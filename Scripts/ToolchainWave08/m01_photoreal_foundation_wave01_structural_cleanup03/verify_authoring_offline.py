from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / r"Scripts\ToolchainWave08\m01_photoreal_foundation_wave01_structural_cleanup03\author_structural_cleanup03.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01PhotorealFoundationStructuralCleanup03\quality_contract.json"
INPUT = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_LightingRoadsWaterline02.umap")
OUTPUT = Path(r"D:\SG52T08_ENV01\Content\M01\Lvl_M01_PhotorealFoundation_StructuralCleanup03.umap")
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_AUTHORING\attempt_01"
TERMINAL = ROOT / r"Saved\Reports\M01_PHOTOREAL_FOUNDATION_WAVE01_STRUCTURAL_CLEANUP03_AUTHORING_TERMINAL_MANIFEST.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
source = SCRIPT.read_text(encoding="utf-8")
compile(source, str(SCRIPT), "exec")
require(contract["contract_id"] == "M01-PHOTOREAL-FOUNDATION-WAVE01-STRUCTURAL-CLEANUP03", "Contract identity changed")
require(INPUT.stat().st_size == 739952, "Input byte count changed")
require(sha256(INPUT) == "34b93c53b208fa061538674a36f1aef2a087376ec66a5254465fdafbd8488149", "Input hash changed")
require(not OUTPUT.exists(), "Fresh output map already exists")
require(not ATTEMPT.exists(), "Fresh attempt namespace already exists")
require(not TERMINAL.exists(), "Fresh terminal namespace already exists")
for token in (
    "M_ENV_Asphalt_2K",
    "M_ENV_Concrete_Pavers_2K",
    "component.set_material(0, asphalt)",
    "component.set_material(2, asphalt)",
    "TARGET_SUN_INTENSITY = 8.0",
    "TARGET_FILL_INTENSITY = 5.5",
    "TARGET_SKYLIGHT_INTENSITY = 6.25",
    "TARGET_EXPOSURE_BIAS = 0.95",
    "TARGET_FILM_TOE = 0.55",
    "TARGET_ZONE_EXTENT_CM = 800_000.0",
    "zone_extent",
    "Water_FarMesh",
    "levels.new_level_from_template(OUTPUT_ASSET, INPUT_ASSET)",
):
    require(token in source, f"Required authoring token missing: {token}")
require("destroy_actor" not in source, "Authoring must not delete actors")
require("spawn_actor" not in source, "Authoring must not spawn actors")
print("PASS")
