from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", required=True)
    parser.add_argument("--recovery", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    original = Path(args.original)
    recovery = Path(args.recovery)
    original_lines = original.read_text(encoding="utf-8").splitlines()
    recovery_lines = recovery.read_text(encoding="utf-8").splitlines()
    if len(original_lines) != len(recovery_lines):
        raise SystemExit("line count changed")

    changes = []
    for line_number, (before, after) in enumerate(zip(original_lines, recovery_lines), start=1):
        if before != after:
            changes.append({"line": line_number, "before": before, "after": after})

    expected = [
        {
            "before": 'GATE = "GATE7_COMBAT_BLOCKOUT_CYCLE02_ATTEMPT01"',
            "after": 'GATE = "GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01_ATTEMPT01"',
        },
        {
            "before": '    scene.render.engine = "BLENDER_EEVEE_NEXT"',
            "after": '    scene.render.engine = "BLENDER_EEVEE"',
        },
    ]
    if [{k: row[k] for k in ("before", "after")} for row in changes] != expected:
        raise SystemExit(f"unexpected diff: {changes}")

    ast.parse(recovery.read_text(encoding="utf-8"))
    text = recovery.read_text(encoding="utf-8")
    checks = {
        "exactly_two_changed_lines": len(changes) == 2,
        "recovery_gate_identity": 'GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY01_ATTEMPT01' in text,
        "blender_5_2_eevee_enum": 'scene.render.engine = "BLENDER_EEVEE"' in text,
        "invalid_enum_absent": "BLENDER_EEVEE_NEXT" not in text,
        "no_unreal_launch": "UnrealEditor" not in text,
        "no_external_model": "grok" not in text.lower() and "claude" not in text.lower(),
    }
    if not all(checks.values()):
        raise SystemExit(f"check failed: {checks}")

    payload = {
        "classification": "PASSED_READY_FOR_EXPLICIT_SINGLE_BLENDER_RECOVERY01_AUTHORIZATION",
        "original": {"path": str(original), "bytes": original.stat().st_size, "sha256": digest(original)},
        "recovery": {"path": str(recovery), "bytes": recovery.stat().st_size, "sha256": digest(recovery)},
        "changes": changes,
        "checks": checks,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=False)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
