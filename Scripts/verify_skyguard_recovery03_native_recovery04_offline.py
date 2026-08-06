from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(r"D:\Skyguard52")
BASE = ROOT / "Plugins/SkyguardRecovery03NativeRecovery01"
CORRECTED = ROOT / "Plugins/SkyguardRecovery03NativeRecovery04"
SUPERVISOR = ROOT / "Scripts/build_skyguard_recovery03_native_recovery04_once.ps1"
EXACT = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY04_EXACT_HOST_TEST.json"
PATHS = ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY04_PROJECTED_PATHS.json"


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    authorities = {
        ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_ATTEMPT01_TERMINAL_FREEZE.json":
            "b88f849c2f5cf9012a801a2ecce0caec105400cee21c201b92607a9edb6787bc",
        ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_FREEZE.json":
            "1d82d76d613b3e5fbf638f2c14630f9a90e7644e74f7902a8d16e167f452c7d9",
        ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01_FREEZE.json":
            "35791f4e8b6557d5c85d354cbb2e0a6ab57933fc9d6942381f462d7077315258",
        ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY03_TERMINAL_SUPERVISOR_MANIFEST.json":
            "879cea521a7d6066badc3072162ad5796b8ed1a1f7cdee79b8aa735f99cafcb6",
    }
    for path, expected in authorities.items():
        require(sha256(path) == expected, f"authority mismatch: {path}")

    base_header = BASE / "Source/SkyguardRecovery03NativeRecovery01/Public/SkyguardRecovery03NativeRecovery01Module.h"
    corrected_header = CORRECTED / "Source/SkyguardRecovery03NativeRecovery01/Public/SkyguardRecovery03NativeRecovery01Module.h"
    base_cpp = BASE / "Source/SkyguardRecovery03NativeRecovery01/Private/SkyguardRecovery03NativeRecovery01Module.cpp"
    corrected_cpp = CORRECTED / "Source/SkyguardRecovery03NativeRecovery01/Private/SkyguardRecovery03NativeRecovery01Module.cpp"
    base_build = BASE / "Source/SkyguardRecovery03NativeRecovery01/SkyguardRecovery03NativeRecovery01.Build.cs"
    corrected_build = CORRECTED / "Source/SkyguardRecovery03NativeRecovery01/SkyguardRecovery03NativeRecovery01.Build.cs"
    base_filter = BASE / "Config/FilterPlugin.ini"
    corrected_filter = CORRECTED / "Config/FilterPlugin.ini"

    require(sha256(base_header) == "3f1be719e2a33314b2954858521e49955999b547a581c92c27426d647873a9a4", "base header")
    require(sha256(base_cpp) == "65b9e514819cbd531edcb71fb4d754e5180dde2996bc883125c31c2cd27d73c6", "base cpp")
    require(sha256(base_build) == "503a39136a154158474f5d54ad55a00ccaed50c975b008174c3678434d2f1831", "base Build.cs")
    require(base_build.read_bytes() == corrected_build.read_bytes(), "Build.cs changed")
    require(base_filter.read_bytes() == corrected_filter.read_bytes(), "filter changed")

    header_addition = '#include "UObject/WeakObjectPtr.h"\n'
    cpp_addition = '#include "Editor.h"\n'
    corrected_header_text = corrected_header.read_text(encoding="utf-8")
    corrected_cpp_text = corrected_cpp.read_text(encoding="utf-8")
    require(corrected_header_text.count(header_addition.strip()) == 1, "weak pointer include")
    require(corrected_cpp_text.count(cpp_addition.strip()) == 1, "Editor include")
    require(
        corrected_header_text.replace(header_addition, "", 1)
        == base_header.read_text(encoding="utf-8"),
        "header diff exceeds allowlist",
    )
    require(
        corrected_cpp_text.replace(cpp_addition, "", 1)
        == base_cpp.read_text(encoding="utf-8"),
        "cpp diff exceeds allowlist",
    )

    base_descriptor = json.loads((BASE / "SkyguardRecovery03NativeRecovery01.uplugin").read_text(encoding="utf-8"))
    corrected_descriptor = json.loads((CORRECTED / "SkyguardRecovery03NativeRecovery04.uplugin").read_text(encoding="utf-8"))
    for key in ("Version", "VersionName", "FriendlyName", "Description"):
        base_descriptor.pop(key)
        corrected_descriptor.pop(key)
    require(base_descriptor == corrected_descriptor, "descriptor diff exceeds allowlist")
    require(corrected_descriptor["EnabledByDefault"] is False, "plugin enabled by default")
    require(corrected_descriptor["Modules"] == [{"Name": "SkyguardRecovery03NativeRecovery01", "Type": "Editor", "LoadingPhase": "PostEngineInit"}], "module identity")

    generated = {"Binaries", "Intermediate", "Saved", "DerivedDataCache"}
    require(not any(path.is_dir() and path.name in generated for path in CORRECTED.rglob("*")), "generated directory present")
    require(not any(path.suffix.lower() in {".dll", ".pdb", ".lib", ".obj"} for path in CORRECTED.rglob("*") if path.is_file()), "binary file present")

    weak_header = pathlib.Path(r"D:\UE_5.8\Engine\Source\Runtime\CoreUObject\Public\UObject\WeakObjectPtr.h")
    editor_header = pathlib.Path(r"D:\UE_5.8\Engine\Source\Editor\UnrealEd\Public\Editor.h")
    require(sha256(weak_header) == "0f56ed91ef7446327b4370b5b771ce7470cb236334fc6673ab094105075b30c8", "weak authority")
    require("struct FWeakObjectPtr" in weak_header.read_text(encoding="utf-8", errors="replace"), "weak symbol")
    require(sha256(editor_header) == "36f1922af026945b3461fbafd3240f04a2abb7a6e9d20848f9b6acc4650c804e", "editor authority")
    require("GEditor;" in editor_header.read_text(encoding="utf-8", errors="replace"), "GEditor symbol")

    source = SUPERVISOR.read_text(encoding="utf-8")
    require(source.count("Start-Process -FilePath $dotnet") == 1, "single build launch")
    require("D:\\SG52R03B05" in source, "fresh package root")
    require("SkyguardRecovery03NativeRecovery04.uplugin" in source, "Recovery04 descriptor")
    require("automatic_retry = $false" in source and "retry_count = 0" in source, "retry prohibition")
    require("AutomationTool.exe" not in source and "RunUAT.bat" not in source and "cmd.exe" not in source, "forbidden launcher")

    exact = json.loads(EXACT.read_text(encoding="utf-8"))
    require(exact["gate"] == "PASS", "exact-host test")
    require(exact["powershell_host"]["exit_code"] == 0, "PowerShell host exit")
    require(exact["powershell_host"]["exit_code_type"] == "System.Int32", "PowerShell exit type")
    require(exact["automation_tool_launched"] is False and exact["native_build_launched"] is False, "build launched")
    paths = json.loads(PATHS.read_text(encoding="utf-8"))
    require(paths["gate"] == "PASS" and paths["longest_projected_length"] <= 213, "path gate")

    future = [
        pathlib.Path(r"D:\SG52R03B05"),
        ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY04/build_attempt_01",
        ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY04/runtime_attempt_01",
        ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY04_TERMINAL_SUPERVISOR_MANIFEST.json",
        ROOT / "Saved/Reports/PHASE4_M01_RECOVERY03_NATIVE_BUILD_RECOVERY04_EMERGENCY_RECEIPT.jsonl",
    ]
    require(all(not path.exists() for path in future), "future namespace exists")

    print(json.dumps({
        "schema": "skyguard.recovery03-native-build-recovery04-offline-verification.v1",
        "gate": "PASS",
        "corrected_descriptor_sha256": sha256(CORRECTED / "SkyguardRecovery03NativeRecovery04.uplugin"),
        "corrected_header_sha256": sha256(corrected_header),
        "corrected_cpp_sha256": sha256(corrected_cpp),
        "supervisor_sha256": sha256(SUPERVISOR),
        "exact_host_test_sha256": sha256(EXACT),
        "future_namespaces_absent": True,
        "compiler_launched": False,
        "unreal_launched": False,
        "blender_launched": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"gate": "FAIL", "error": str(exc)}, indent=2), file=sys.stderr)
        raise
