"""Recovery03 namespace wrapper for the frozen deferred Recovery02 proof."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import prove_skyguard_phase4_m01_landscape_attempt07_recovery02_tiny_live as deferred


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY03_CONTRACT.json"
)
CONTRACT_ID = "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-03"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_switch(name: str) -> str:
    command_line = unreal.SystemLibrary.get_command_line()
    match = re.search(
        rf'(?:^|\s)-{re.escape(name)}=(?:"([^"]+)"|(\S+))',
        command_line,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Missing required -" + name + " switch")
    return match.group(1) or match.group(2)


def validate_activation(contract: dict) -> dict:
    activation_path = Path(
        parse_switch("SkyguardRecovery03CompileActivation")
    ).resolve()
    expected_hash = parse_switch(
        "SkyguardRecovery03CompileActivationSha256"
    ).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        raise RuntimeError("Recovery03 activation SHA256 is malformed")
    if not activation_path.is_file():
        raise RuntimeError(
            "Recovery03 compile activation is missing: "
            + str(activation_path)
        )
    if sha256_file(activation_path) != expected_hash:
        raise RuntimeError("Recovery03 compile activation hash mismatch")
    activation = json.loads(
        activation_path.read_text(encoding="utf-8-sig")
    )
    prerequisite = contract["full_module_compile_prerequisite"]
    if (
        activation.get("schema") != prerequisite["activation_schema"]
        or activation.get("contract_id") != contract["contract_id"]
        or activation.get("gate") != prerequisite["required_gate"]
        or activation.get("target") != "Skyguard52Editor"
        or activation.get("platform") != "Win64"
        or activation.get("configuration") != "Development"
        or activation.get("build_exit_code") != 0
    ):
        raise RuntimeError(
            "Recovery03 compile activation identity/gate mismatch"
        )
    module = activation.get("compiled_module") or {}
    module_path = ROOT / module.get("file", "")
    if (
        module.get("file") != "Binaries/Win64/UnrealEditor-Skyguard52.dll"
        or not module_path.is_file()
        or module_path.stat().st_size != module.get("bytes")
        or sha256_file(module_path) != module.get("sha256")
    ):
        raise RuntimeError(
            "Recovery03 activated DLL is absent or hash-mismatched"
        )
    return activation


def validate_recovery02(contract: dict) -> None:
    recovery02 = contract["immutable_recovery02_failure"]
    root = ROOT / recovery02["root"]
    for name, item in recovery02["files"].items():
        path = root / item["file"]
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or sha256_file(path) != item["sha256"]
        ):
            raise RuntimeError(
                "Recovery02 immutable evidence changed: " + name
            )


def main() -> None:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Recovery03 contract ID mismatch")
    validate_recovery02(contract)
    validate_activation(contract)

    original_parse_switch = deferred.proof_base.parse_switch

    def recovery03_switch(name: str) -> str:
        if name == "SkyguardAttempt07Recovery02ProofRoot":
            return original_parse_switch(
                "SkyguardAttempt07Recovery03ProofRoot"
            )
        return original_parse_switch(name)

    deferred.CONTRACT_PATH = CONTRACT_PATH
    deferred.CONTRACT_ID = CONTRACT_ID
    deferred.proof_base.parse_switch = recovery03_switch
    deferred.main()


if __name__ == "__main__":
    main()
