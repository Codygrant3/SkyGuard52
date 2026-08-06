from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
REPORTS = ROOT / "Saved" / "Reports"
DOCS = ROOT / "Docs" / "AAA_Review"
SCRIPTS = ROOT / "Scripts"

FILES = {
    "reconciliation": REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_TERMINAL_RECONCILIATION.json",
    "authority": REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_UBT_PLUGIN_DISCOVERY_AUTHORITY.json",
    "collision": REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_PLUGIN_COLLISION_INVENTORY.json",
    "options": REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_OPTIONS_MATRIX.json",
    "architecture": REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_SELECTED_ARCHITECTURE.json",
    "namespace": REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_NAMESPACE_CONTRACT.json",
    "parity": REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_SOURCE_PARITY_CONTRACT.json",
    "supervisor": SCRIPTS
    / "build_phase4_m01_recovery05_environment_native_build_recovery02_once.ps1",
}

FUTURE_PATHS = [
    Path(r"D:\SG52M01R02"),
    ROOT
    / "Saved"
    / "BuildAttempts"
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02"
    / "build_attempt_01",
    REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_TERMINAL_SUPERVISOR_MANIFEST.json",
    REPORTS
    / "PHASE4_M01_RECOVERY05_ENVIRONMENT_NATIVE_BUILD_RECOVERY02_EMERGENCY_RECEIPT.jsonl",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    payloads: dict[str, object] = {}
    for name, path in FILES.items():
        require(path.is_file(), f"missing artifact: {path}")
        if path.suffix == ".json":
            payloads[name] = json.loads(path.read_text(encoding="utf-8-sig"))

    parity = payloads["parity"]
    require(isinstance(parity, dict), "parity contract is not an object")
    records = parity.get("records")
    require(isinstance(records, list), "parity records missing")
    require(len(records) == 170, f"expected 170 parity records, got {len(records)}")
    relative_paths: set[str] = set()
    for record in records:
        require(isinstance(record, dict), "invalid parity record")
        source = Path(record["source"])
        require(source.is_file(), f"missing parity source: {source}")
        require(source.stat().st_size == int(record["bytes"]), f"byte mismatch: {source}")
        require(sha256(source) == record["sha256"], f"hash mismatch: {source}")
        relative = str(record["relative_path"])
        require(relative not in relative_paths, f"duplicate relative path: {relative}")
        relative_paths.add(relative)

    require(
        "Source/Skyguard52/SkyguardMission01EnvironmentDirector.cpp"
        in relative_paths,
        "environment source absent from parity contract",
    )
    require(
        not any("SkyguardRecovery03NativeRecovery01" in value for value in relative_paths),
        "Recovery01 collision evidence leaked into build view",
    )
    require(
        not any("SkyguardRecovery03NativeRecovery04" in value for value in relative_paths),
        "Recovery04 collision evidence leaked into build view",
    )

    supervisor = FILES["supervisor"].read_text(encoding="utf-8-sig")
    require(len(re.findall(r"\bStart-Process\b", supervisor)) == 1, "expected one Start-Process")
    require("-AuthorizeSingleBuild" in supervisor, "authorization guard missing")
    require(
        r"D:\UE_5.8\Engine\Binaries\ThirdParty\DotNet\10.0\win-x64\dotnet.exe"
        in supervisor,
        "bundled dotnet missing",
    )
    require(
        r"D:\UE_5.8\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll"
        in supervisor,
        "UBT assembly missing",
    )
    require(r"-Project=D:\SG52M01R02\Skyguard52.uproject" in supervisor, "view project missing")
    require("RunUAT.bat" not in supervisor, "RunUAT path forbidden")
    require("Build.bat" not in supervisor, "Build.bat path forbidden")
    require("cmd.exe" not in supervisor, "cmd.exe path forbidden")
    require("UnrealEditor.exe" not in supervisor, "UnrealEditor launch path forbidden")
    require("UnrealEditor-Cmd.exe" not in supervisor, "UnrealEditor-Cmd launch path forbidden")
    require("blender.exe" not in supervisor.lower(), "Blender launch path forbidden")
    require("$State.retry_count = 0" not in supervisor, "runtime retry mutation found")
    require("copy_back_performed = false" in supervisor, "copy-back prohibition missing")

    architecture = payloads["architecture"]
    require(
        architecture["architecture"] == "fresh_isolated_native_build_view",
        "unexpected selected architecture",
    )
    require(
        architecture["output_policy"]["copy_back_to_source_project"] is False,
        "copy-back must remain disabled",
    )

    options = payloads["options"]["options"]
    selected = [option for option in options if option["decision"] == "SELECTED"]
    require(len(selected) == 1 and selected[0]["id"] == "A", "option A not uniquely selected")

    for path in FUTURE_PATHS:
        require(not path.exists(), f"future namespace already exists: {path}")

    print(
        json.dumps(
            {
                "classification": "PASS",
                "parity_record_count": len(records),
                "start_process_count": 1,
                "future_namespaces_absent": True,
                "build_launched": False,
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
