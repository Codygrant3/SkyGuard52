import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AAA = ROOT / r"Docs\AAA_Review"
REPORTS = ROOT / r"Saved\Reports"
ATTEMPT = ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06\attempt_01"
MANIFEST = REPORTS / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_TERMINAL_SUPERVISOR_MANIFEST.json"
RECEIPT = ATTEMPT / "authoring_receipt.json"
OFFLINE_FREEZE = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_OFFLINE_DESIGN_FREEZE.json"
POSTFLIGHT_TOOL_FREEZE = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_POSTFLIGHT_OFFLINE_DESIGN_FREEZE.json"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery06.umap")
CRASH_ROOT = Path(r"D:\SG52T08_ENV01\Saved\Crashes")

POSTFLIGHT = REPORTS / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_ATTEMPT01_POSTFLIGHT.json"
ADDENDUM = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_ATTEMPT01_ADDENDUM_2026-08-08.md"
PHASE_ADDENDUM = AAA / "PHASE1_8_COMPLETION_AUDIT_ADDENDUM_TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_ATTEMPT01_2026-08-08.md"
FREEZE = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_ATTEMPT01_TERMINAL_FREEZE.json"
NEXT_SUCCESS = AAA / "NEXT_PROMPT_TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_MAPPED_VISUAL_PROOF_OFFLINE_DESIGN.md"
NEXT_FAILURE = AAA / "NEXT_PROMPT_TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_OFFLINE_CORRECTION.md"

EXPECTED_OFFLINE_FREEZE = "ea3ad66bf3fa440fdd1802c170ba19bdd6abc4e1fd373034031cc183e28f3632"
EXPECTED_INPUT = "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4"
SUCCESS_MANIFEST = "PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_AUTOMATIC_AWAITING_VISUAL_PROOF"
SUCCESS_RECEIPT = "PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_AUTOMATIC"
OUTPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery06"
ALLOWED_ACTIONS = {"SPAWNED_DETERMINISTICALLY_IN_FRESH_OUTPUT", "REUSED_SINGLE_EXISTING_OUTPUT_DIRECTOR"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": digest(path)}


def require(value, message):
    if not value:
        raise RuntimeError(message)


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise RuntimeError(f"temporary output already exists: {temporary}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def write_json(path: Path, value: dict) -> None:
    write_new(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def failure_message(manifest: dict, receipt: dict | None) -> str:
    if receipt:
        message = (receipt.get("error") or {}).get("message")
        if message:
            return str(message)
    if manifest.get("failure"):
        return str(manifest["failure"])
    return "Governed Recovery06 execution failed without a detailed failure message"


def evaluate(manifest: dict, receipt: dict | None, *, input_hash: str, output_exists: bool, output_hash: str | None) -> dict:
    launch_count = manifest.get("unreal_launch_count")
    require(launch_count in (0, 1), "Unreal launch count must be zero or one")
    require(manifest.get("retry_count") == 0, "retry count must be zero")
    require(manifest.get("timed_out") in (True, False), "timeout state is not Boolean")
    require(input_hash == EXPECTED_INPUT, "accepted input map changed")
    if launch_count == 1:
        require(manifest.get("exit_code_type") == "System.Int32", "exit-code type mismatch")
        require(isinstance(manifest.get("exit_code"), int), "exit code is not numeric")
    else:
        require(manifest.get("exit_code") is None, "zero-launch manifest contains an exit code")

    success = manifest.get("classification") == SUCCESS_MANIFEST
    if not success:
        require(manifest.get("classification") == "FAILED_WITH_EVIDENCE", "unknown terminal classification")
        if receipt is not None:
            require(receipt.get("classification") == "FAILED_WITH_EVIDENCE", "failure receipt classification mismatch")
        return {
            "classification": "FAILED_WITH_EVIDENCE",
            "failure": failure_message(manifest, receipt),
            "exit_code": manifest.get("exit_code"),
            "output_map_exists": output_exists,
            "output_sha256": output_hash,
            "receipt_present": receipt is not None,
            "next_gate": "OFFLINE_ONLY_RECOVERY07_CORRECTION_DESIGN",
        }

    require(launch_count == 1, "successful manifest did not launch Unreal exactly once")
    require(manifest.get("exit_code") == 0, "successful manifest exit code is not zero")
    require(manifest.get("timed_out") is False, "successful attempt timed out")
    require(receipt is not None, "successful attempt lacks an authoring receipt")
    require(receipt.get("classification") == SUCCESS_RECEIPT, "success receipt classification mismatch")
    require(receipt.get("error") is None, "success receipt contains an error")
    require(receipt.get("input_sha256_before") == EXPECTED_INPUT, "input before hash mismatch")
    require(receipt.get("input_sha256_after") == EXPECTED_INPUT, "input after hash mismatch")
    require(output_exists, "successful attempt lacks output map")
    require(output_hash == receipt.get("output_sha256"), "output hash differs from receipt")
    require(receipt.get("saved_assets") == [OUTPUT_ASSET], "save allowlist evidence mismatch")
    require(receipt.get("unexpected_assets") == [], "unexpected assets were recorded")
    require(receipt.get("pcg_seed") == 520801, "PCG seed mismatch")
    require(receipt.get("pcg_generation") == "DISABLED_FIXED_DIRECT_PLACEMENT_ONLY", "PCG fail-closed state mismatch")
    require((receipt.get("pcg_registry_initialization") or {}).get("passed") is True, "PCG registry initialization failed")
    trees = receipt.get("pcg_tree_validation") or []
    require(len(trees) == 3 and all(row.get("passed") is True for row in trees), "PCG tree validation is not 3 of 3")
    acquisition = receipt.get("director_acquisition") or {}
    require(acquisition.get("after_count") == 1, "director acquisition count mismatch")
    require(acquisition.get("action") in ALLOWED_ACTIONS, "director acquisition action mismatch")
    actors = receipt.get("post_actor_inventory") or []
    labels = [row.get("label") for row in actors]
    require(len(labels) == len(set(labels)), "duplicate actor labels recorded")
    require(labels.count("M01_A01_EnvironmentDirector") == 1, "director actor count is not one")
    require(sum(str(label).startswith("M01_A01_Tree_") for label in labels) == 15, "tree count is not fifteen")
    grounding = receipt.get("grounding_records") or []
    require(grounding and max(abs(float(row.get("gap_cm", 999999.0))) for row in grounding) <= 1.0, "grounding tolerance failed")
    shore = receipt.get("shore_contact_checks") or {}
    require(shore.get("passed") is True, "shore-contact check failed")
    require(shore.get("beach_station_count") == 6, "beach station count is not six")
    observed = float(shore.get("observed_vertical_delta_cm", -1.0))
    require(0.0 <= observed <= 120.0, "shore vertical relationship failed")
    return {
        "classification": SUCCESS_MANIFEST,
        "failure": None,
        "exit_code": 0,
        "output_map_exists": True,
        "output_sha256": output_hash,
        "receipt_present": True,
        "director_action": acquisition.get("action"),
        "pcg_tree_validation": "3_OF_3",
        "tree_count": 15,
        "next_gate": "OFFLINE_MAPPED_VISUAL_PROOF_DESIGN",
    }


def success_fixture():
    manifest = {
        "classification": SUCCESS_MANIFEST,
        "unreal_launch_count": 1,
        "retry_count": 0,
        "exit_code": 0,
        "exit_code_type": "System.Int32",
        "timed_out": False,
    }
    receipt = {
        "classification": SUCCESS_RECEIPT,
        "error": None,
        "input_sha256_before": EXPECTED_INPUT,
        "input_sha256_after": EXPECTED_INPUT,
        "output_sha256": "fixture-output",
        "saved_assets": [OUTPUT_ASSET],
        "unexpected_assets": [],
        "pcg_seed": 520801,
        "pcg_generation": "DISABLED_FIXED_DIRECT_PLACEMENT_ONLY",
        "pcg_registry_initialization": {"passed": True},
        "pcg_tree_validation": [{"passed": True}, {"passed": True}, {"passed": True}],
        "director_acquisition": {"after_count": 1, "action": "SPAWNED_DETERMINISTICALLY_IN_FRESH_OUTPUT"},
        "post_actor_inventory": ([{"label": "M01_A01_EnvironmentDirector"}] + [{"label": f"M01_A01_Tree_{i:02d}"} for i in range(15)]),
        "grounding_records": [{"gap_cm": 0.0}],
        "shore_contact_checks": {"passed": True, "beach_station_count": 6, "observed_vertical_delta_cm": 60.0},
    }
    return manifest, receipt


def run_offline_contract_test():
    manifest, receipt = success_fixture()
    passed = evaluate(manifest, receipt, input_hash=EXPECTED_INPUT, output_exists=True, output_hash="fixture-output")
    require(passed["classification"] == SUCCESS_MANIFEST, "success fixture failed")
    failed_manifest = dict(manifest, classification="FAILED_WITH_EVIDENCE", exit_code=-1, failure="fixture failure")
    failed_receipt = {"classification": "FAILED_WITH_EVIDENCE", "error": {"message": "fixture failure"}}
    failed = evaluate(failed_manifest, failed_receipt, input_hash=EXPECTED_INPUT, output_exists=False, output_hash=None)
    require(failed["classification"] == "FAILED_WITH_EVIDENCE", "failure fixture failed")
    missing_receipt = evaluate(failed_manifest, None, input_hash=EXPECTED_INPUT, output_exists=False, output_hash=None)
    require(missing_receipt["receipt_present"] is False, "missing receipt failure was not preserved")
    print("CLASSIFICATION=PASSED_RECOVERY06_POSTFLIGHT_OFFLINE_CONTRACT_TEST")


def parse_started_at(manifest: dict) -> float | None:
    value = manifest.get("started_at_utc")
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def crash_evidence(manifest: dict) -> list[Path]:
    started = parse_started_at(manifest)
    if started is None or not CRASH_ROOT.is_dir():
        return []
    evidence = []
    for path in CRASH_ROOT.glob("UECC-Windows-*"):
        if path.is_dir() and path.stat().st_mtime >= started - 5.0:
            evidence.extend(sorted(item for item in path.rglob("*") if item.is_file()))
    return evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    args = parser.parse_args()
    if args.offline_contract_test:
        run_offline_contract_test()
        return

    for path in (POSTFLIGHT, ADDENDUM, PHASE_ADDENDUM, FREEZE, NEXT_SUCCESS, NEXT_FAILURE):
        require(not path.exists(), f"terminal evidence already exists: {path}")
    require(digest(OFFLINE_FREEZE) == EXPECTED_OFFLINE_FREEZE, "Recovery06 offline freeze mismatch")
    require(POSTFLIGHT_TOOL_FREEZE.is_file(), "Recovery06 postflight tool freeze is missing")
    require(INPUT_MAP.stat().st_size == 8681 and digest(INPUT_MAP) == EXPECTED_INPUT, "accepted input map mismatch")
    require(MANIFEST.is_file(), "Recovery06 terminal supervisor manifest is missing")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    receipt = None
    receipt_error = None
    if RECEIPT.is_file():
        try:
            receipt = json.loads(RECEIPT.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            receipt_error = f"authoring receipt is unreadable: {exc}"

    artifact_paths = []
    integrity_failures = []
    for expected in manifest.get("artifacts", []):
        path = Path(expected.get("path", ""))
        if not path.is_file():
            integrity_failures.append(f"missing artifact: {path}")
            continue
        actual = record(path)
        if actual["bytes"] != expected.get("bytes") or actual["sha256"] != expected.get("sha256"):
            integrity_failures.append(f"artifact mismatch: {path}")
        artifact_paths.append(path)
    if receipt_error:
        integrity_failures.append(receipt_error)

    try:
        outcome = evaluate(manifest, receipt, input_hash=digest(INPUT_MAP), output_exists=OUTPUT_MAP.is_file(), output_hash=digest(OUTPUT_MAP) if OUTPUT_MAP.is_file() else None)
    except Exception as exc:
        outcome = {
            "classification": "FAILED_WITH_EVIDENCE",
            "failure": f"Recovery06 postflight contract violation: {exc}",
            "exit_code": manifest.get("exit_code"),
            "output_map_exists": OUTPUT_MAP.is_file(),
            "output_sha256": digest(OUTPUT_MAP) if OUTPUT_MAP.is_file() else None,
            "receipt_present": receipt is not None,
            "next_gate": "OFFLINE_ONLY_RECOVERY07_CORRECTION_DESIGN",
        }
    if integrity_failures:
        outcome = {**outcome, "classification": "FAILED_WITH_EVIDENCE", "failure": "; ".join(integrity_failures), "next_gate": "OFFLINE_ONLY_RECOVERY07_CORRECTION_DESIGN"}

    postflight = {
        "schema": "skyguard.toolchain-wave08.m01-authoring01-recovery06.attempt01-postflight.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        **outcome,
        "unreal_launch_count": manifest.get("unreal_launch_count"),
        "retry_count": manifest.get("retry_count"),
        "exit_code_type": manifest.get("exit_code_type"),
        "timed_out": manifest.get("timed_out"),
        "input_map_unchanged": True,
        "artifact_integrity_failures": integrity_failures,
        "automatic_retry_performed": False,
    }
    write_json(POSTFLIGHT, postflight)

    if outcome["classification"] == SUCCESS_MANIFEST:
        next_path = NEXT_SUCCESS
        next_text = """Resume only D:\\Skyguard52. Perform one offline-only design gate for a mapped, full-resolution Mission 1 visual proof of the accepted Recovery06 environment output. Launch no Unreal or Blender. Verify the Recovery06 terminal freeze and output map, freeze rear-gunner gameplay and exterior cameras, visual and temporal rubrics, shader readiness, performance limits, evidence requirements, one-heavy-process and one-attempt rules, and create a separate one-shot Unreal proof prompt. Classify PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY06_MAPPED_VISUAL_PROOF_AUTHORIZATION or FAILED_WITH_EVIDENCE.\n"""
        status = "Automatic Recovery06 authoring passed. Full-resolution visual acceptance remains unproven."
    else:
        next_path = NEXT_FAILURE
        next_text = f"""Resume only D:\\Skyguard52. Perform one offline-only Recovery07 correction design using the immutable Recovery06 failure evidence. Do not launch Unreal or Blender. Diagnose only this exact failure: {outcome['failure']!r}. Preserve the accepted input and every failed attempt, create a fresh namespace and one bounded correction, validate it offline, and stop after a separate one-shot execution prompt.\n"""
        status = f"Automatic Recovery06 authoring failed with immutable evidence: {outcome['failure']}"
    write_new(next_path, next_text)

    addendum = f"""# Toolchain Wave08 Mission 1 Environment Authoring01 Recovery06 Attempt01

Date: 2026-08-08

Classification: `{outcome['classification']}`

{status}

- Unreal launches: `{manifest.get('unreal_launch_count')}`
- Retries: `{manifest.get('retry_count')}`
- Exit code: `{manifest.get('exit_code')}` (`{manifest.get('exit_code_type')}`)
- Timed out: `{str(manifest.get('timed_out')).lower()}`
- Input map unchanged: `true`
- Output map exists: `{str(outcome['output_map_exists']).lower()}`
- Authoring receipt present: `{str(outcome['receipt_present']).lower()}`
- Artifact integrity failures: `{len(integrity_failures)}`
- Next gate: `{outcome['next_gate']}`
"""
    write_new(ADDENDUM, addendum)
    write_new(PHASE_ADDENDUM, "# Phase 1-8 Completion Audit Addendum: Recovery06 Attempt01\n\n" + addendum.split("\n", 1)[1])

    freeze_paths = [OFFLINE_FREEZE, POSTFLIGHT_TOOL_FREEZE, MANIFEST, *artifact_paths, POSTFLIGHT, ADDENDUM, PHASE_ADDENDUM, INPUT_MAP, next_path, *crash_evidence(manifest)]
    if RECEIPT.is_file() and RECEIPT not in freeze_paths:
        freeze_paths.append(RECEIPT)
    if OUTPUT_MAP.is_file():
        freeze_paths.append(OUTPUT_MAP)
    unique = []
    seen = set()
    for path in freeze_paths:
        key = str(path).lower()
        if key not in seen and path.is_file():
            seen.add(key)
            unique.append(path)
    terminal = {
        "schema": "skyguard.toolchain-wave08.m01-authoring01-recovery06.attempt01-terminal-freeze.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        **outcome,
        "member_count": len(unique),
        "members": [record(path) for path in unique],
        "unreal_launch_count": manifest.get("unreal_launch_count"),
        "retry_count": manifest.get("retry_count"),
        "exit_code_type": manifest.get("exit_code_type"),
        "timed_out": manifest.get("timed_out"),
        "input_map_sha256": EXPECTED_INPUT,
        "artifact_integrity_failures": integrity_failures,
    }
    write_json(FREEZE, terminal)
    print(json.dumps({"classification": terminal["classification"], "freeze": record(FREEZE), "member_count": terminal["member_count"], "next_prompt": record(next_path)}, indent=2))


if __name__ == "__main__":
    main()
