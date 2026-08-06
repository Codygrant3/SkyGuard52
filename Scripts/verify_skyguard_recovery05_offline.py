from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
UE = Path(r"D:\UE_5.8")
OLD = ROOT / "Plugins/SkyguardRecovery03NativeRecovery04"
NEW = ROOT / "Plugins/SkyguardRecovery03NativeRecovery05"
DOCS = ROOT / "Docs/AAA_Review"
REPORTS = ROOT / "Saved/Reports"

OLD_SYMBOL = "SkyguardRecovery03NativeRecovery01"
NEW_SYMBOL = "SkyguardRecovery03NativeRecovery05"

AUTHORITIES = {
    ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY04_BINDING01_ATTEMPT01_TERMINAL_FREEZE.json":
        (4933, "483e1c2489ded78db7763a12c8b85836c2151940fe7c82eff6ac102d196c4258"),
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY04_BINDING01_TERMINAL_EVIDENCE.json":
        (4522, "d7cdf8937b82d7d7974ba9c74d0f9c6c0dc1e160d68611d107da4eecf9f49c04"),
    ROOT / "Docs/AAA_Review/PHASE4_M01_RECOVERY04_RUNTIME_BINDING_FREEZE.json":
        (4585, "f68b263354e9b4663d1bb28e518ba38343f0aad35005e8ab2722fe92c07f2a24"),
    OLD / "Binaries/Win64/UnrealEditor-SkyguardRecovery03NativeRecovery01.dll":
        (177664, "2070765a5d44199f7116c2038c97d866b91a509706de73953ead1cad057cb6e3"),
    ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY04_BINDING01/launcher_attempt_01/logs/recovery04.engine.log":
        (258342, "ee61045d84f2937ed6ea54d113e16151895f7916d82181939411c5b4536b8d90"),
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY04_BINDING01_TERMINAL_SUPERVISOR.json":
        (911, "32c61e39bd37a2656f73a5a05eebb25770e3032b46e9cb38647556cbd4aa6e79"),
    ROOT / "Saved/Reports/PHASE4_M01_RECOVERY04_BINDING01_EXECUTION_PREFLIGHT.json":
        (1036, "218c1b61d114c0325ada1257f7b63a9cea744fa8c228c9fda7f319838c1b6d4b"),
    ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.cpp":
        (14984, "7cb7dae93bce8c2b0ff3f1eca45ce84cb5f74194f4e38a1ed02bb07c55262980"),
    ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.h":
        (9413, "64f1e798084fe5c8c8fce93fc5aac7289d3afe5112817d2cb7c3bf50128376cb"),
    UE / "Engine/Plugins/Messaging/TcpMessaging/TcpMessaging.uplugin":
        (870, "a47d14505131225b926c7324f49fa856d55b9e02a4b1fefc977c621b1b32880d"),
    UE / "Engine/Plugins/Messaging/UdpMessaging/UdpMessaging.uplugin":
        (1437, "7d8dbd8f1f3227aabfb0958905e0f6eae059c0dc6435cdaef2cbf235a412c994"),
    UE / "Engine/Source/Runtime/Projects/Private/PluginManager.cpp":
        (143416, "b2aa3a2c551fcbd86a3de72103030331591f619ca2c66aff8b6eae7e662bd2df"),
    UE / "Engine/Source/Runtime/Engine/Private/Components/SceneComponent.cpp":
        (167288, "58c6337430d41c3fb9acd8060221a8b46696e0f372c2cc590bc2b865ed89b757"),
}

JSON_ARTIFACTS = [
    REPORTS / "PHASE4_M01_RECOVERY05_TERMINAL_RECONCILIATION.json",
    DOCS / "PHASE4_M01_RECOVERY05_UE58_AUTHORITY_REPORT.json",
    DOCS / "PHASE4_M01_RECOVERY05_MODULE_IDENTITY_CONTRACT.json",
    REPORTS / "PHASE4_M01_RECOVERY05_STRICT_DIFF_REPORT.json",
    DOCS / "PHASE4_M01_RECOVERY05_MESSAGING_ISOLATION_CONTRACT.json",
    DOCS / "PHASE4_M01_RECOVERY05_ENVIRONMENT_AUTHORITY_REPORT.json",
    DOCS / "PHASE4_M01_RECOVERY05_ENVIRONMENT_CORRECTION_CONTRACT.json",
    DOCS / "PHASE4_M01_RECOVERY05_STARTUP_RECEIPT_SCHEMA.json",
    DOCS / "PHASE4_M01_RECOVERY05_FUTURE_LIFECYCLE_CONTRACT.json",
    REPORTS / "PHASE4_M01_RECOVERY05_PROJECTED_PATHS.json",
]

FUTURE_NAMESPACES = [
    Path(r"D:\SG52R03B06"),
    ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY05/build_attempt_01",
    ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY05/runtime_attempt_01",
    ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY05/proof_attempt_01",
    ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY05/launcher_attempt_01",
    REPORTS / "PHASE4_M01_RECOVERY05_EXECUTION_PREFLIGHT.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check(condition: bool, label: str, failures: list[str]) -> None:
    if not condition:
        failures.append(label)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized_source_parity(failures: list[str]) -> None:
    pairs = [
        (
            OLD / "Source/SkyguardRecovery03NativeRecovery01/SkyguardRecovery03NativeRecovery01.Build.cs",
            NEW / "Source/SkyguardRecovery03NativeRecovery05/SkyguardRecovery03NativeRecovery05.Build.cs",
        ),
        (
            OLD / "Source/SkyguardRecovery03NativeRecovery01/Public/SkyguardRecovery03NativeRecovery01Module.h",
            NEW / "Source/SkyguardRecovery03NativeRecovery05/Public/SkyguardRecovery03NativeRecovery05Module.h",
        ),
        (
            OLD / "Source/SkyguardRecovery03NativeRecovery01/Private/SkyguardRecovery03NativeRecovery01Module.cpp",
            NEW / "Source/SkyguardRecovery03NativeRecovery05/Private/SkyguardRecovery03NativeRecovery05Module.cpp",
        ),
    ]
    for old_path, new_path in pairs:
        check(new_path.is_file(), f"missing Recovery05 source: {new_path}", failures)
        if new_path.is_file():
            normalized = read(new_path).replace(NEW_SYMBOL, OLD_SYMBOL)
            check(normalized == read(old_path), f"unallowlisted source difference: {new_path}", failures)

    old_filter = OLD / "Config/FilterPlugin.ini"
    new_filter = NEW / "Config/FilterPlugin.ini"
    check(new_filter.is_file() and new_filter.read_bytes() == old_filter.read_bytes(),
          "FilterPlugin.ini parity failed", failures)


def descriptor_contract(failures: list[str]) -> None:
    descriptor_path = NEW / "SkyguardRecovery03NativeRecovery05.uplugin"
    check(descriptor_path.is_file(), "Recovery05 descriptor missing", failures)
    if not descriptor_path.is_file():
        return
    descriptor = json.loads(read(descriptor_path))
    check(descriptor.get("EnabledByDefault") is False, "Recovery05 enabled by default", failures)
    check(descriptor.get("CanContainContent") is False, "Recovery05 can contain content", failures)
    modules = descriptor.get("Modules", [])
    check(len(modules) == 1, "Recovery05 module count is not one", failures)
    if len(modules) == 1:
        check(modules[0].get("Name") == NEW_SYMBOL, "Recovery05 module identity mismatch", failures)
        check(modules[0].get("Type") == "Editor", "Recovery05 module is not Editor", failures)
        check(modules[0].get("LoadingPhase") == "PostEngineInit",
              "Recovery05 loading phase changed", failures)


def messaging_contract(failures: list[str]) -> None:
    contract = json.loads(read(DOCS / "PHASE4_M01_RECOVERY05_MESSAGING_ISOLATION_CONTRACT.json"))
    disabled = set(contract["future_disable_plugins"])
    check({"TcpMessaging", "UdpMessaging", OLD_SYMBOL,
           "SkyguardRecovery03NativeRecovery04"}.issubset(disabled),
          "future disable list incomplete", failures)
    required_patterns = {
        "Initializing TcpMessaging bridge",
        "Initializing bridge on interface",
        "Unicast socket bound",
        "multicast group",
        "Added local interface",
    }
    check(required_patterns.issubset(set(contract["reject_log_patterns"])),
          "network log rejection patterns incomplete", failures)
    manager = read(UE / "Engine/Source/Runtime/Projects/Private/PluginManager.cpp")
    check('ParsePluginsList(TEXT("DisablePlugins="))' in manager,
          "UE DisablePlugins authority absent", failures)


def environment_contract(failures: list[str]) -> None:
    source = read(ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.cpp")
    check('Root = CreateDefaultSubobject<USceneComponent>(TEXT("Mission01EnvironmentRoot"));' in source,
          "environment root construction authority missing", failures)
    check("Root->SetMobility(EComponentMobility::Static);" not in source,
          "accepted environment source was already mutated", failures)
    for component in ("OceanTiles", "BeachTiles", "LandTiles"):
        check(f"ConfigureInstanceComponent({component});" in source,
              f"{component} static configuration authority missing", failures)
    patch = read(ROOT / "SourceCorrections/Recovery05/SkyguardMission01EnvironmentDirector.mobility.patch")
    added = [
        line for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    removed = [
        line for line in patch.splitlines()
        if line.startswith("-") and not line.startswith("---")
    ]
    check(added == ["+\tRoot->SetMobility(EComponentMobility::Static);"],
          "environment patch added-line allowlist failed", failures)
    check(not removed, "environment patch removes source lines", failures)
    scene = read(UE / "Engine/Source/Runtime/Engine/Private/Components/SceneComponent.cpp")
    check("Mobility == EComponentMobility::Static && Parent->Mobility != EComponentMobility::Static"
          in scene, "UE mobility rejection authority missing", failures)


def no_generated_plugin_outputs(failures: list[str]) -> None:
    for name in ("Binaries", "Intermediate", "Saved", "DerivedDataCache"):
        check(not (NEW / name).exists(), f"forbidden Recovery05 generated directory exists: {name}", failures)


def heavy_processes() -> list[str]:
    completed = subprocess.run(
        ["tasklist.exe", "/FO", "CSV", "/NH"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    rows = csv.reader(io.StringIO(completed.stdout))
    forbidden = (
        "unrealeditor",
        "shadercompileworker",
        "blender",
        "automationtool",
        "unrealbuildtool",
        "cl.exe",
        "link.exe",
    )
    return [row[0] for row in rows if row and any(item in row[0].lower() for item in forbidden)]


def run_checks() -> dict:
    failures: list[str] = []
    for path, (expected_bytes, expected_hash) in AUTHORITIES.items():
        check(path.is_file(), f"missing authority: {path}", failures)
        if path.is_file():
            check(path.stat().st_size == expected_bytes, f"byte mismatch: {path}", failures)
            check(sha256(path) == expected_hash, f"hash mismatch: {path}", failures)

    check(NEW.is_dir(), "Recovery05 plugin namespace missing", failures)
    normalized_source_parity(failures)
    descriptor_contract(failures)
    no_generated_plugin_outputs(failures)

    for artifact in JSON_ARTIFACTS:
        check(artifact.is_file(), f"missing JSON artifact: {artifact}", failures)
        if artifact.is_file():
            try:
                json.loads(read(artifact))
            except Exception as exc:  # noqa: BLE001
                failures.append(f"invalid JSON {artifact}: {exc}")

    patch_path = ROOT / "SourceCorrections/Recovery05/SkyguardMission01EnvironmentDirector.mobility.patch"
    check(patch_path.is_file(), "environment patch missing", failures)
    if patch_path.is_file():
        environment_contract(failures)
    messaging_contract(failures)

    new_text = "\n".join(
        read(path) for path in NEW.rglob("*")
        if path.is_file() and path.suffix.lower() in {".h", ".cpp", ".cs", ".uplugin"}
    )
    check(OLD_SYMBOL not in new_text, "old module identifier remains in Recovery05 source", failures)
    check(f"IMPLEMENT_MODULE(\n    F{NEW_SYMBOL}Module,\n    {NEW_SYMBOL})" in new_text,
          "unique Recovery05 module registration missing", failures)

    for path in FUTURE_NAMESPACES:
        check(not path.exists(), f"future governed namespace exists: {path}", failures)

    process_hits = heavy_processes()
    check(not process_hits, f"heavy processes active: {process_hits}", failures)

    projected = json.loads(read(REPORTS / "PHASE4_M01_RECOVERY05_PROJECTED_PATHS.json"))
    check(projected["longest_projected_path_characters"] <= 213,
          "projected path exceeds 213 characters", failures)
    check(projected["hard_contract_maximum"] < 240,
          "hard path contract is not below 240", failures)

    return {
        "schema": "skyguard.phase4.m01-recovery05-offline-verification.v1",
        "classification": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "authority_count": len(AUTHORITIES),
        "recovery05_plugin_present": NEW.is_dir(),
        "future_namespace_count": len(FUTURE_NAMESPACES),
        "heavy_processes": process_hits,
        "build_launched": False,
        "unreal_launched": False,
        "blender_launched": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_checks()
    payload = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["classification"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
