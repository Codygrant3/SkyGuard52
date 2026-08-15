from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB_RECOVERY01"
BASE_SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stageb.py"
)
BASE_BYTES = 37220
BASE_SHA256 = "d73abc1fc8f25b7bb167aa3287fa754eab906bcd0c5950b2c01abd5fc452570a"
REPLACEMENTS = (
    (
        "    base = np.repeat(base, size, axis=1)\n",
        (
            "    require(base.shape == (size, size, 3), "
            "f\"Base-color texture shape drift: {base.shape}\")\n"
        ),
    ),
    (
        "    rough = np.repeat(rough, size, axis=1)\n",
        (
            "    require(rough.shape == (size, size, 1), "
            "f\"Roughness texture shape drift: {rough.shape}\")\n"
        ),
    ),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_bounded_source() -> tuple[str, dict[str, object]]:
    raw = BASE_SOURCE.read_bytes()
    if len(raw) != BASE_BYTES:
        raise RuntimeError(f"Frozen StageB source byte mismatch: {len(raw)}")
    digest = sha256_bytes(raw)
    if digest != BASE_SHA256:
        raise RuntimeError(f"Frozen StageB source hash mismatch: {digest}")

    corrected = raw.decode("utf-8")
    replacement_receipts: list[dict[str, object]] = []
    for old_token, new_token in REPLACEMENTS:
        count = corrected.count(old_token)
        if count != 1:
            raise RuntimeError(
                f"Expected exactly one redundant texture repeat, found {count}: {old_token.strip()}"
            )
        corrected = corrected.replace(old_token, new_token, 1)
        if old_token in corrected:
            raise RuntimeError(f"Redundant texture repeat remains: {old_token.strip()}")
        if corrected.count(new_token) != 1:
            raise RuntimeError(f"Shape assertion cardinality is not one: {new_token.strip()}")
        replacement_receipts.append(
            {
                "removed": old_token.strip(),
                "added": new_token.strip(),
                "old_token_count": count,
                "new_token_count": corrected.count(new_token),
            }
        )

    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stageb-recovery01.in-memory-patch.v1",
        "gate": GATE,
        "base_source": str(BASE_SOURCE),
        "base_bytes": BASE_BYTES,
        "base_sha256": BASE_SHA256,
        "replacements": replacement_receipts,
        "behavioral_changes": [
            "remove redundant base-color-map axis-1 repeat",
            "add fail-closed base-color shape assertion",
            "remove redundant roughness-map axis-1 repeat",
            "add fail-closed roughness shape assertion",
        ],
        "geometry_render_export_receipt_changes": 0,
        "passed": True,
    }
    return corrected, receipt


def main() -> int:
    corrected, receipt = load_bounded_source()
    print(json.dumps(receipt, sort_keys=True))
    namespace: dict[str, object] = {
        "__name__": "skyguard_stageb_recovery01_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(corrected, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Frozen StageB main() was not recovered")
    return int(embedded_main())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps(
                {
                    "gate": GATE,
                    "status": "FAILED_WITH_EVIDENCE",
                    "error": f"{type(exc).__name__}: {exc}",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise
