"""Generate the clean Recovery12 capture from quarantined Recovery09 evidence.

This is a deterministic mechanical migration. It never edits the quarantined
inputs and never launches Unreal.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
QUARANTINE = ROOT / "Saved/Quarantine/Phase3FailedCaptureSources/Recovery12Retirement"
SOURCE = ROOT / "Source/Skyguard52"
INPUT_HEADER = QUARANTINE / "SkyguardM01GroupedTopologyRecovery09Capture.h"
INPUT_SOURCE = QUARANTINE / "SkyguardM01GroupedTopologyRecovery09Capture.cpp"
OUTPUT_HEADER = SOURCE / "SkyguardM01GroupedTopologyRecovery12Capture.h"
OUTPUT_SOURCE = SOURCE / "SkyguardM01GroupedTopologyRecovery12Capture.cpp"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def migrate(text: str) -> str:
    return (
        text.replace("Recovery09", "Recovery12")
        .replace("RECOVERY09", "RECOVERY12")
        .replace("recovery09", "recovery12")
    )


def main() -> int:
    if OUTPUT_HEADER.exists() or OUTPUT_SOURCE.exists():
        raise RuntimeError("Recovery12 outputs already exist; regeneration is forbidden")
    header = migrate(INPUT_HEADER.read_text(encoding="utf-8-sig"))
    source = migrate(INPUT_SOURCE.read_text(encoding="utf-8-sig"))

    owned_signature = "const TArray<FColor>& Colors) const"
    view_signature = "const TArrayView64<const FColor> Colors) const"
    if source.count(owned_signature) != 2:
        raise RuntimeError("Expected exactly two owned-array definition signatures")
    source = source.replace(owned_signature, view_signature)

    bad_printf = "\t\t\tLexToString(GMaxRHIFeatureLevel));"
    fixed_printf = "\t\t\t*LexToString(GMaxRHIFeatureLevel));"
    if source.count(bad_printf) != 1:
        raise RuntimeError("Expected the one FString::Printf feature-level site")
    source = source.replace(bad_printf, fixed_printf, 1)

    forbidden = (
        "#define BuildRecord",
        "#define WritePng",
        "#define Colors",
        "#define TArray",
        "#define TArrayView",
        "__LINE__",
        "Recovery09",
        "RECOVERY09",
        "recovery09",
    )
    combined = header + source
    found = [token for token in forbidden if token in combined]
    if found:
        raise RuntimeError(f"Forbidden Recovery12 tokens: {found}")
    if header.count("TArrayView64<const FColor> Colors") != 3:
        raise RuntimeError("Recovery12 header does not expose three governed views")
    if source.count(view_signature) != 2:
        raise RuntimeError("Recovery12 source definitions are not type-consistent")

    OUTPUT_HEADER.write_text(header, encoding="utf-8", newline="\n")
    OUTPUT_SOURCE.write_text(source, encoding="utf-8", newline="\n")
    print(json.dumps({
        "gate": "PASS_RECOVERY12_SOURCE_GENERATED",
        "header": {
            "path": str(OUTPUT_HEADER),
            "bytes": OUTPUT_HEADER.stat().st_size,
            "sha256": sha256(OUTPUT_HEADER),
        },
        "source": {
            "path": str(OUTPUT_SOURCE),
            "bytes": OUTPUT_SOURCE.stat().st_size,
            "sha256": sha256(OUTPUT_SOURCE),
        },
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
