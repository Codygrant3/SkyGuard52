from __future__ import annotations

import hashlib
import json
import pathlib

package_root = pathlib.Path(r"D:\SG52R03B04")
output = pathlib.Path(
    r"D:\Skyguard52\Saved\Reports"
    r"\PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_ATTEMPT01_PARTIAL_PACKAGE_INVENTORY.json"
)

rows = []
for path in sorted(
    (candidate for candidate in package_root.rglob("*") if candidate.is_file()),
    key=lambda candidate: candidate.as_posix().lower(),
):
    payload = path.read_bytes()
    rows.append(
        {
            "file": path.relative_to(package_root).as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    )

canonical = json.dumps(rows, separators=(",", ":"), sort_keys=True).encode("utf-8")
report = {
    "schema": "skyguard.recovery03-native-build-recovery03-partial-package-inventory.v1",
    "root": str(package_root),
    "file_count": len(rows),
    "total_bytes": sum(row["bytes"] for row in rows),
    "canonical_inventory_sha256": hashlib.sha256(canonical).hexdigest(),
    "expected_plugin_dll_present": (
        package_root
        / "Binaries/Win64/UnrealEditor-SkyguardRecovery03NativeRecovery01.dll"
    ).is_file(),
    "expected_plugin_pdb_present": (
        package_root
        / "Binaries/Win64/UnrealEditor-SkyguardRecovery03NativeRecovery01.pdb"
    ).is_file(),
    "expected_module_receipt_present": (
        package_root / "Binaries/Win64/UnrealEditor.modules"
    ).is_file(),
    "files": rows,
}
output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(output)
