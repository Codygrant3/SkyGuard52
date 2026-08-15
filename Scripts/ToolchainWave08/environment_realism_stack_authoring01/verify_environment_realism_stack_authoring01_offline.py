import ast
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_authoring01/author_environment_realism_stack01.py"
SUPERVISOR = ROOT / "Scripts/ToolchainWave08/environment_realism_stack_authoring01/invoke_environment_realism_stack_authoring01_once.ps1"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/M01EnvironmentRealismStackAuthoring01/authoring_contract.json"
BRIDGE_FREEZE = ROOT / "Docs/AAA_Review/M01_LANDSCAPE_GROUNDING_BRIDGE01_RUNTIME_PROBE_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentRealismStack01.umap")
ATTEMPT = ROOT / "Saved/BuildAttempts/M01_ENVIRONMENT_REALISM_STACK_AUTHORING01/attempt_01"
TERMINAL = ROOT / "Saved/Reports/M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_TERMINAL_MANIFEST.json"
EMERGENCY = ROOT / "Saved/Reports/M01_ENVIRONMENT_REALISM_STACK_AUTHORING01_EMERGENCY_RECEIPT.jsonl"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def verify_freeze(path: Path, size: int, digest: str, errors: list[str]) -> None:
    require(path.is_file(), f"Freeze is missing: {path}", errors)
    if not path.is_file():
        return
    require(path.stat().st_size == size, f"Freeze byte mismatch: {path.name}", errors)
    require(sha256(path) == digest, f"Freeze hash mismatch: {path.name}", errors)
    payload = json.loads(path.read_text(encoding="utf-8"))
    for member in payload.get("members", []):
        member_path = ROOT / member["path"]
        require(member_path.is_file(), f"Frozen member missing: {member['path']}", errors)
        if member_path.is_file():
            require(member_path.stat().st_size == member["bytes"], f"Frozen member byte mismatch: {member['path']}", errors)
            require(sha256(member_path) == member["sha256"], f"Frozen member hash mismatch: {member['path']}", errors)


def main() -> int:
    errors: list[str] = []
    for path in (SOURCE, SUPERVISOR, CONTRACT, INPUT_MAP):
        require(path.is_file(), f"Required authority is missing: {path}", errors)
    verify_freeze(BRIDGE_FREEZE, 2874, "9a03a0162b521618d23e12c4fc84b84c0b2bf475c82864773da3201037a90a32", errors)
    if INPUT_MAP.is_file():
        require(INPUT_MAP.stat().st_size == 625041, "Input map byte mismatch", errors)
        require(sha256(INPUT_MAP) == "401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f", "Input map hash mismatch", errors)

    if SOURCE.is_file():
        source = SOURCE.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as exc:
            errors.append(f"Authoring Python syntax failed: {exc}")
        required_source = (
            "sample_landscape_height",
            "sample_landscape_footprint",
            "ground_by_footprint",
            "ground_point",
            "M01_RS01_CrossStreet_",
            "M01_RS01_City_",
            "M01_RS01_Tree_",
            "AEM_MANUAL",
            "continuous_coverage_cm\": 48000.0",
            "\"building\": 36",
            "\"tree\": 60",
            "len(result[\"grounding_records\"]) == 175",
            "expected_counts =",
        )
        for token in required_source:
            require(token in source, f"Authoring source token missing: {token}", errors)
        require("ground_targets" not in source, "Legacy hard-coded ground-target table is present", errors)
        require("(x, y, -20.0)" not in source, "Legacy hard-coded building Z is present", errors)
        require("random.Random(RANDOM_SEED)" in source, "Deterministic vegetation seed is missing", errors)
        require(source.count("save_asset(OUTPUT_ASSET") == 1, "Authoring must save exactly one governed output path", errors)
        require("INPUT_ASSET = \"/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery07\"" in source, "Recovery07 template authority changed", errors)

    if SUPERVISOR.is_file():
        supervisor = SUPERVISOR.read_text(encoding="utf-8")
        require(supervisor.count("Start-Process -FilePath $Editor") == 1, "Supervisor must contain exactly one Unreal launch path", errors)
        require("$NativeHandle = $Process.Handle" in supervisor, "Native process-handle retention is missing", errors)
        require("Assert-NumericExitCode $CapturedExitCode" in supervisor, "Numeric exit-code guard is missing", errors)
        require("retry_count = 0" in supervisor, "Zero-retry evidence is missing", errors)
        require("$TimeoutSeconds = 900" in supervisor, "Authoring timeout changed", errors)
        require("-NullRHI" in supervisor, "NullRHI authoring mode is missing", errors)
        require("Write-JsonAtomic $TerminalManifest $State" in supervisor, "Terminal evidence lifecycle is missing", errors)
        require(not re.findall(r"(?m)\bthrow(?=['\"A-Za-z])", supervisor), "Malformed compact throw tokenization is present", errors)
        offline_body = supervisor.split("function Invoke-OfflineContractTest", 1)[1].split("if ($OfflineContractTest)", 1)[0]
        require("Start-Process" not in offline_body, "Offline contract mode contains a child launch", errors)

    if CONTRACT.is_file():
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        density = contract["visible_density"]
        require(density == {
            "beach_modules": 10,
            "seawall_modules": 20,
            "promenade_modules": 16,
            "coastal_road_modules": 16,
            "cross_street_modules": 15,
            "buildings": 36,
            "building_depth_bands": 4,
            "building_signatures": 4,
            "minimum_each_building_signature": 8,
            "trees": 60,
            "landmarks": 2,
            "atmosphere_actors": 6,
            "continuous_shoreline_coverage_cm": 48000.0,
        }, "Visible-density contract changed", errors)
        require(contract["execution_policy"]["automatic_retries"] == 0, "Zero-retry contract changed", errors)
        require(contract["execution_policy"]["one_unreal_launch"] is True, "One-launch contract changed", errors)

    require(not ATTEMPT.exists(), "Authoring attempt namespace already exists", errors)
    require(not OUTPUT_MAP.exists(), "Authoring output map already exists", errors)
    require(not TERMINAL.exists(), "Authoring terminal manifest already exists", errors)
    require(not EMERGENCY.exists(), "Authoring emergency receipt already exists", errors)

    result = {
        "schema": "skyguard.m01-environment-realism-stack-authoring01-offline-verification.v1",
        "classification": "PASS" if not errors else "FAIL",
        "errors": errors,
        "checks": {
            "bridge_authority_verified": not any("Freeze" in error or "Frozen member" in error for error in errors),
            "measured_grounding_required": not any("ground" in error.lower() for error in errors),
            "density_contract_verified": not any("density" in error.lower() for error in errors),
            "single_unreal_launch_path": not any("launch path" in error for error in errors),
            "native_handle_retained": not any("process-handle" in error for error in errors),
            "future_namespaces_absent": not any("already exists" in error for error in errors),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
