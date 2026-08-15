import ast
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
OLD_SOURCE = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_authoring01/author_environment_realism_stack01.py"
SOURCE = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_authoring01_recovery01/author_environment_realism_stack01_recovery01.py"
SUPERVISOR = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_authoring01_recovery01/invoke_environment_realism_stack_authoring01_recovery01_once.ps1"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01EnvironmentRealismStackAuthoring01Recovery01/recovery_contract.json"
FAILURE_FREEZE = ROOT / "Docs/AAA_Review/M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_ATTEMPT01_TERMINAL_FREEZE.json"
HEADER = Path(r"D:\UE_5.8\Engine\Source\Runtime\Engine\Classes\Components\ExponentialHeightFogComponent.h")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack01_Recovery01.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01_TERMINAL_MANIFEST.json"
EMERGENCY = ROOT / "Saved/Reports/M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01_EMERGENCY_RECEIPT.jsonl"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def verify_freeze(errors: list[str]) -> None:
    require(FAILURE_FREEZE.is_file(), "Attempt01 failure freeze is missing", errors)
    if not FAILURE_FREEZE.is_file():
        return
    require(FAILURE_FREEZE.stat().st_size == 3322, "Attempt01 failure freeze byte mismatch", errors)
    require(sha256(FAILURE_FREEZE) == "5a4d50cc7d292e941624764e9c3dbb69e4d85b73771a4409fc7206035d6b9e57", "Attempt01 failure freeze hash mismatch", errors)
    payload = json.loads(FAILURE_FREEZE.read_text(encoding="utf-8"))
    for member in payload.get("members", []):
        raw = member["path"]
        path = Path(raw.replace("/", "\\")) if re.match(r"^[A-Za-z]:/", raw) else ROOT / raw
        require(path.is_file(), f"Frozen member missing: {raw}", errors)
        if path.is_file():
            require(path.stat().st_size == member["bytes"], f"Frozen member byte mismatch: {raw}", errors)
            require(sha256(path) == member["sha256"], f"Frozen member hash mismatch: {raw}", errors)


def normalize_recovery_source(text: str) -> str:
    normalized = text.replace("M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01", "M01_ENVIRONMENT_REALISM_STACK_AUTHORING01")
    normalized = normalized.replace("_Recovery01", "")
    normalized = normalized.replace("-recovery01", "")
    normalized = normalized.replace(" Recovery01", "")
    normalized = normalized.replace(
        '    fog_component.set_volumetric_fog(True)\n    result["atmosphere_properties"].append({"property": "set_volumetric_fog", "value": "True", "passed": True})',
        '    result["atmosphere_properties"].append(set_property(fog_component, "volumetric_fog", True))',
    )
    return normalized


def main() -> int:
    errors: list[str] = []
    verify_freeze(errors)
    for path in (OLD_SOURCE, SOURCE, SUPERVISOR, CONTRACT, HEADER):
        require(path.is_file(), f"Required authority missing: {path}", errors)

    if SOURCE.is_file() and OLD_SOURCE.is_file():
        source = SOURCE.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as exc:
            errors.append(f"Recovery01 Python syntax failed: {exc}")
        require(normalize_recovery_source(source) == OLD_SOURCE.read_text(encoding="utf-8"), "Recovery01 source exceeds the namespace and fog-API allowlist", errors)
        require("fog_component.set_volumetric_fog(True)" in source, "Authoritative fog setter is missing", errors)
        require('set_property(fog_component, "volumetric_fog", True)' not in source, "Unsupported fog property write remains", errors)
        require("len(result[\"grounding_records\"]) == 175" in source, "Grounding count contract changed", errors)
        require('"building": 36' in source and '"tree": 60' in source, "Density contract changed", errors)
        require("random.Random(RANDOM_SEED)" in source, "Deterministic vegetation changed", errors)

    if HEADER.is_file():
        require(HEADER.stat().st_size == 19831, "UE fog header byte mismatch", errors)
        require(sha256(HEADER) == "35381d9c97aaae5020409fe3fd98d65723b22be594ec5154e3a888fd78723669", "UE fog header hash mismatch", errors)
        header = HEADER.read_text(encoding="utf-8", errors="replace")
        require("void SetVolumetricFog(bool bNewValue);" in header, "SetVolumetricFog authority is missing", errors)

    if SUPERVISOR.is_file():
        supervisor = SUPERVISOR.read_text(encoding="utf-8")
        require(supervisor.count("Start-Process -FilePath $Editor") == 1, "Supervisor must contain exactly one Unreal launch path", errors)
        require("$NativeHandle = $Process.Handle" in supervisor, "Native handle retention is missing", errors)
        require("Assert-NumericExitCode $CapturedExitCode" in supervisor, "Numeric exit-code guard is missing", errors)
        require("retry_count = 0" in supervisor, "Zero-retry evidence is missing", errors)
        require("M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_RECOVERY01" in supervisor, "Fresh Recovery01 attempt namespace is missing", errors)
        require("Lvl_M01_T08_EnvironmentRealismStack01_Recovery01.umap" in supervisor, "Fresh Recovery01 output map is missing", errors)
        require(not re.findall(r"(?m)\bthrow(?=['\"A-Za-z])", supervisor), "Malformed compact throw tokenization is present", errors)

    if CONTRACT.is_file():
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        require(contract["invariants"]["density_contract_unchanged"] is True, "Density invariant is not frozen", errors)
        require(contract["invariants"]["grounding_contract_unchanged"] is True, "Grounding invariant is not frozen", errors)
        require(contract["invariants"]["automatic_retries"] == 0, "Zero-retry invariant changed", errors)

    require(not ATTEMPT.exists(), "Recovery01 attempt namespace already exists", errors)
    require(not OUTPUT_MAP.exists(), "Recovery01 output map already exists", errors)
    require(not TERMINAL.exists(), "Recovery01 terminal manifest already exists", errors)
    require(not EMERGENCY.exists(), "Recovery01 emergency receipt already exists", errors)

    result = {
        "schema": "skyguard.m01-environment-realism-stack-authoring01-recovery01-offline-verification.v1",
        "classification": "PASS" if not errors else "FAIL",
        "errors": errors,
        "checks": {
            "failed_attempt_frozen": not any("Attempt01" in error or "Frozen member" in error for error in errors),
            "source_diff_bounded": not any("allowlist" in error for error in errors),
            "authoritative_fog_setter": not any("fog" in error.lower() for error in errors),
            "density_and_grounding_unchanged": not any("contract changed" in error.lower() or "invariant" in error.lower() for error in errors),
            "single_unreal_launch_path": not any("launch path" in error for error in errors),
            "future_namespaces_absent": not any("already exists" in error for error in errors),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
