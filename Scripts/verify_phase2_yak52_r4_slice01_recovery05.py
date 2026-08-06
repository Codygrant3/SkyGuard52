"""Fail-closed offline verifier for Phase 2 Yak-52 Slice01 Recovery05."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


CONTRACT = (
    "Docs/AAA_Review/"
    "PHASE2_YAK52_R4_SLICE01_RECOVERY05_OUTPUT_CONTRACT.json"
)
PRODUCTION_ROOT = "Saved/Reports/Phase2Yak52R4Slice01Recovery05Production"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(root: Path) -> list[str]:
    contract = json.loads((root / CONTRACT).read_text(encoding="utf-8-sig"))
    errors: list[str] = []

    for authority in contract["authority_inputs"]:
        path = root / authority["path"]
        if not path.is_file():
            errors.append(f"missing authority: {authority['path']}")
            continue
        if path.stat().st_size != authority["bytes"]:
            errors.append(f"authority byte drift: {authority['path']}")
        if sha256(path) != authority["sha256"]:
            errors.append(f"authority hash drift: {authority['path']}")

    for key in ("authoring_script", "launch_wrapper"):
        artifact = contract[key]
        path = root / artifact["path"]
        if not path.is_file():
            errors.append(f"missing {key}")
            continue
        if path.stat().st_size != artifact["bytes"]:
            errors.append(f"{key} byte drift")
        if sha256(path) != artifact["sha256"]:
            errors.append(f"{key} hash drift")

    source = (root / contract["authoring_script"]["path"]).read_text(
        encoding="utf-8"
    )
    required_source_markers = (
        'obj.empty_display_type = "PLAIN_AXES"',
        'patched["render_contract"]["engine"] = "BLENDER_EEVEE"',
        'module.bpy.data.worlds.new("WORLD_R4S01_Recovery05")',
        'appended_path = Path(str(requested_temp_path) + ".glb")',
        "appended_path.replace(requested_temp_path)",
    )
    for marker in required_source_markers:
        if marker not in source:
            errors.append(f"missing source marker: {marker}")

    for name, value in contract["claims"].items():
        if value is not False:
            errors.append(f"premature claim: {name}")

    for name, relative in contract["outputs"].items():
        if (root / relative).exists():
            errors.append(f"Recovery05 output already exists: {name}")

    if (root / PRODUCTION_ROOT).exists():
        errors.append("Recovery05 production-attempt root already exists")

    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    failures = run(args.root)
    print(
        json.dumps(
            {
                "gate": (
                    "PASS_RECOVERY05_READY_NOT_RUN"
                    if not failures
                    else "FAIL_RECOVERY05_READINESS"
                ),
                "errors": failures,
                "blender_launched": False,
                "unreal_launched": False,
            },
            indent=2,
        )
    )
    sys.exit(0 if not failures else 1)
