from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY01"
BASE_SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stagea.py"
)
BASE_BYTES = 42238
BASE_SHA256 = "773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12"
OLD_TOKEN = "    rough = np.repeat(rough, size, axis=1)\n"
NEW_TOKEN = (
    "    require(rough.shape == (size, size, 1), "
    "f\"Roughness texture shape drift: {rough.shape}\")\n"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_bounded_source() -> tuple[str, dict[str, object]]:
    raw = BASE_SOURCE.read_bytes()
    if len(raw) != BASE_BYTES:
        raise RuntimeError(f"Frozen StageA source byte mismatch: {len(raw)}")
    digest = sha256_bytes(raw)
    if digest != BASE_SHA256:
        raise RuntimeError(f"Frozen StageA source hash mismatch: {digest}")
    source = raw.decode("utf-8")
    count = source.count(OLD_TOKEN)
    if count != 1:
        raise RuntimeError(f"Expected exactly one redundant roughness repeat, found {count}")
    corrected = source.replace(OLD_TOKEN, NEW_TOKEN, 1)
    if OLD_TOKEN in corrected:
        raise RuntimeError("Redundant roughness repeat remains after bounded correction")
    if corrected.count(NEW_TOKEN) != 1:
        raise RuntimeError("Recovery01 shape assertion cardinality is not one")
    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery01.in-memory-patch.v1",
        "gate": GATE,
        "base_source": str(BASE_SOURCE),
        "base_bytes": BASE_BYTES,
        "base_sha256": BASE_SHA256,
        "old_token_count": count,
        "new_token_count": corrected.count(NEW_TOKEN),
        "behavioral_changes": [
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
        "__name__": "skyguard_stagea_recovery01_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(corrected, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Frozen StageA main() was not recovered")
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
