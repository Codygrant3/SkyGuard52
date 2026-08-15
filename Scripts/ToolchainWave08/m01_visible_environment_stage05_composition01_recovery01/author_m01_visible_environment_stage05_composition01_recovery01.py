"""Bind Stage05 Recovery01 to the immutable failed source with two Rotator fixes."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_AUTHORING01\attempt_01\author_m01_visible_environment_stage05_composition01.py"
)
EXPECTED_BYTES = 21_696
EXPECTED_SHA256 = "59706c1e9257c5fe426d3e8bf1b36b444667ad3f91ae186615134abd0e3e5c33"
OLD_NAMESPACE = "M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_AUTHORING01/attempt_01"
NEW_NAMESPACE = "M01_VISIBLE_ENVIRONMENT_STAGE05_COMPOSITION01_AUTHORING01_RECOVERY01/attempt_01"
OLD_MAP = "Lvl_M01_VisibleEnvironmentStage05Composition01"
NEW_MAP = "Lvl_M01_VisibleEnvironmentStage05Composition01Recovery01"
OLD_ASSET_NAMESPACE = "VisibleEnvironmentStage05Composition01"
NEW_ASSET_NAMESPACE = "VisibleEnvironmentStage05Composition01Recovery01"
OLD_LABEL_PREFIX = "M01_STAGE05_"
NEW_LABEL_PREFIX = "M01_STAGE05R01_"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_BYTES or sha256(SOURCE) != EXPECTED_SHA256:
        raise RuntimeError("Immutable failed Stage05 source changed")
    transformed = SOURCE.read_text(encoding="utf-8")
    # The asset-namespace token is also embedded in the map name. Replace it
    # exactly once instead of replacing the map first and accidentally creating
    # a ``Recovery01Recovery01`` suffix.
    replacements = (
        (OLD_NAMESPACE, NEW_NAMESPACE),
        (OLD_ASSET_NAMESPACE, NEW_ASSET_NAMESPACE),
        (OLD_LABEL_PREFIX, NEW_LABEL_PREFIX),
    )
    for old, new in replacements:
        if old not in transformed:
            raise RuntimeError(f"Recovery01 namespace token absent: {old}")
        transformed = transformed.replace(old, new)

    contract_anchor = 'contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))'
    contract_fix = "\n".join(
        (
            contract_anchor,
            '    contract["output"]["asset"] = OUTPUT_ASSET',
            '    contract["output"]["file"] = str(OUTPUT_FILE)',
            '    contract["output"]["asset_namespace"] = DESTINATION',
            '    contract["output"]["disk_namespace"] = str(DESTINATION_DISK)',
            '    contract["output"]["attempt"] = str(ATTEMPT)',
            '    contract["material"]["output"] = DESTINATION + "/Materials/MI_M01_Stage05_UrbanGround_GrassRock"',
        )
    )
    if transformed.count(contract_anchor) != 1:
        raise RuntimeError("Runtime contract transformation anchor changed")
    transformed = transformed.replace(contract_anchor, contract_fix)

    rotation_anchor = '"rotation_degrees": vector(actor.get_actor_rotation()),'
    rotation_fix = '"rotation_degrees": [float(actor.get_actor_rotation().pitch), float(actor.get_actor_rotation().yaw), float(actor.get_actor_rotation().roll)],'
    if transformed.count(rotation_anchor) != 1:
        raise RuntimeError("Building Rotator serialization anchor changed")
    transformed = transformed.replace(rotation_anchor, rotation_fix)

    prop_anchor = '"rotation": vector(actor.get_actor_rotation()),'
    prop_fix = '"rotation": [float(actor.get_actor_rotation().pitch), float(actor.get_actor_rotation().yaw), float(actor.get_actor_rotation().roll)],'
    if transformed.count(prop_anchor) != 1:
        raise RuntimeError("Prop Rotator serialization anchor changed")
    transformed = transformed.replace(prop_anchor, prop_fix)
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE) + "::recovery01", "exec"), globals(), globals())
