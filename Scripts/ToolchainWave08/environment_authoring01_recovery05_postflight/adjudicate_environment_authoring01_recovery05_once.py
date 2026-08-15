import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AAA = ROOT / r"Docs\AAA_Review"
REPORTS = ROOT / r"Saved\Reports"
ATTEMPT = ROOT / r"Saved\BuildAttempts\TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05\attempt_01"
MANIFEST = REPORTS / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_TERMINAL_SUPERVISOR_MANIFEST.json"
RECEIPT = ATTEMPT / "authoring_receipt.json"
OFFLINE_FREEZE = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_OFFLINE_DESIGN_FREEZE.json"
POSTFLIGHT_TOOL_FREEZE = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_POSTFLIGHT_OFFLINE_DESIGN_FREEZE.json"
INPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_WaterLandmassPCG_Prototype01.umap")
OUTPUT_MAP = Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery05.umap")

POSTFLIGHT = REPORTS / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_ATTEMPT01_POSTFLIGHT.json"
ADDENDUM = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_ATTEMPT01_ADDENDUM_2026-08-08.md"
PHASE_ADDENDUM = AAA / "PHASE1_8_COMPLETION_AUDIT_ADDENDUM_TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_ATTEMPT01_2026-08-08.md"
FREEZE = AAA / "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_ATTEMPT01_TERMINAL_FREEZE.json"
NEXT_SUCCESS = AAA / "NEXT_PROMPT_TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_MAPPED_VISUAL_PROOF_OFFLINE_DESIGN.md"
NEXT_FAILURE = AAA / "NEXT_PROMPT_TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY06_OFFLINE_CORRECTION.md"

EXPECTED_OFFLINE_FREEZE = "9f3e4bc329b16b8d952b88035506ba29bb943aa56eafbb0aa9025eab7731e960"
EXPECTED_INPUT = "5c8b7c6b0c6024767fa8a671523b5626213bd029d591270654080aed5fc7ced4"
SUCCESS_MANIFEST = "PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_AUTOMATIC_AWAITING_VISUAL_PROOF"
SUCCESS_RECEIPT = "PASSED_M01_ENVIRONMENT_AUTHORING01_RECOVERY05_AUTOMATIC"
OUTPUT_ASSET = "/Game/ToolchainWave08/Environment/Lvl_M01_T08_EnvironmentAuthoring01_Recovery05"
ALLOWED_ACTIONS = {"SPAWNED_DETERMINISTICALLY_IN_FRESH_OUTPUT", "REUSED_SINGLE_EXISTING_OUTPUT_DIRECTOR"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
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
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: dict) -> None:
    write_new(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def evaluate(manifest: dict, receipt: dict, *, input_hash: str, output_exists: bool, output_hash: str | None) -> dict:
    require(manifest.get("unreal_launch_count") == 1, "Unreal launch count must be one")
    require(manifest.get("retry_count") == 0, "retry count must be zero")
    require(manifest.get("exit_code_type") == "System.Int32", "exit-code type mismatch")
    require(manifest.get("timed_out") is False, "attempt timed out")
    require(input_hash == EXPECTED_INPUT, "accepted input map changed")

    success = manifest.get("classification") == SUCCESS_MANIFEST
    if not success:
        require(manifest.get("classification") == "FAILED_WITH_EVIDENCE", "unknown terminal classification")
        require(receipt.get("classification") == "FAILED_WITH_EVIDENCE", "failure receipt classification mismatch")
        return {
            "classification": "FAILED_WITH_EVIDENCE",
            "failure": (receipt.get("error") or {}).get("message") or manifest.get("failure") or "Unknown governed authoring failure",
            "exit_code": manifest.get("exit_code"),
            "output_map_exists": output_exists,
            "next_gate": "OFFLINE_ONLY_RECOVERY06_CORRECTION_DESIGN",
        }

    require(manifest.get("exit_code") == 0, "successful manifest exit code is not zero")
    require(receipt.get("classification") == SUCCESS_RECEIPT, "success receipt classification mismatch")
    require(receipt.get("error") is None, "success receipt contains an error")
    require(receipt.get("input_sha256_before") == EXPECTED_INPUT, "input before hash mismatch")
    require(receipt.get("input_sha256_after") == EXPECTED_INPUT, "input after hash mismatch")
    require(output_exists, "successful attempt lacks output map")
    require(output_hash == receipt.get("output_sha256"), "output hash differs from receipt")
    require(receipt.get("saved_assets") == [OUTPUT_ASSET], "save allowlist evidence mismatch")
    require(receipt.get("unexpected_assets") == [], "unexpected assets were recorded")
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
        "director_action": acquisition.get("action"),
        "pcg_tree_validation": "3_OF_3",
        "tree_count": 15,
        "next_gate": "OFFLINE_MAPPED_VISUAL_PROOF_DESIGN",
    }


def success_fixture():
    manifest = {"classification": SUCCESS_MANIFEST, "unreal_launch_count": 1, "retry_count": 0, "exit_code": 0, "exit_code_type": "System.Int32", "timed_out": False}
    receipt = {
        "classification": SUCCESS_RECEIPT, "error": None,
        "input_sha256_before": EXPECTED_INPUT, "input_sha256_after": EXPECTED_INPUT,
        "output_sha256": "fixture-output", "saved_assets": [OUTPUT_ASSET], "unexpected_assets": [],
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
    failure_manifest = dict(manifest, classification="FAILED_WITH_EVIDENCE", exit_code=-1)
    failure_receipt = {"classification": "FAILED_WITH_EVIDENCE", "error": {"message": "fixture failure"}}
    failed = evaluate(failure_manifest, failure_receipt, input_hash=EXPECTED_INPUT, output_exists=False, output_hash=None)
    require(failed["classification"] == "FAILED_WITH_EVIDENCE", "failure fixture failed")
    print("CLASSIFICATION=PASSED_RECOVERY05_POSTFLIGHT_OFFLINE_CONTRACT_TEST")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-contract-test", action="store_true")
    args = parser.parse_args()
    if args.offline_contract_test:
        run_offline_contract_test()
        return

    for path in (POSTFLIGHT, ADDENDUM, PHASE_ADDENDUM, FREEZE, NEXT_SUCCESS, NEXT_FAILURE):
        require(not path.exists(), f"terminal evidence already exists: {path}")
    require(digest(OFFLINE_FREEZE) == EXPECTED_OFFLINE_FREEZE, "Recovery05 offline freeze mismatch")
    require(POSTFLIGHT_TOOL_FREEZE.is_file(), "postflight tool freeze is missing")
    require(INPUT_MAP.stat().st_size == 8681 and digest(INPUT_MAP) == EXPECTED_INPUT, "accepted input map mismatch")
    require(MANIFEST.is_file() and RECEIPT.is_file(), "Recovery05 execution evidence is incomplete")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8-sig"))
    artifact_paths = []
    for expected in manifest.get("artifacts", []):
        path = Path(expected["path"])
        actual = record(path)
        require(actual["bytes"] == expected["bytes"] and actual["sha256"] == expected["sha256"], f"artifact mismatch: {path}")
        artifact_paths.append(path)
    outcome = evaluate(
        manifest,
        receipt,
        input_hash=digest(INPUT_MAP),
        output_exists=OUTPUT_MAP.is_file(),
        output_hash=digest(OUTPUT_MAP) if OUTPUT_MAP.is_file() else None,
    )
    postflight = {
        "schema": "skyguard.toolchain-wave08.m01-authoring01-recovery05.attempt01-postflight.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        **outcome,
        "unreal_launch_count": 1,
        "retry_count": 0,
        "exit_code_type": "System.Int32",
        "input_map_unchanged": True,
        "automatic_retry_performed": False,
    }
    write_json(POSTFLIGHT, postflight)

    if outcome["classification"] == SUCCESS_MANIFEST:
        next_path = NEXT_SUCCESS
        next_text = """Resume only D:\\Skyguard52. Perform one offline-only design gate for a mapped, full-resolution Mission 1 visual proof of the accepted Recovery05 environment output. Launch no Unreal or Blender. Verify the Recovery05 terminal freeze and output map, freeze gameplay/exterior cameras, visual and temporal rubrics, shader readiness, performance limits, evidence requirements, one-heavy-process/one-attempt rules, and create a separate one-shot Unreal proof prompt. Classify PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY05_MAPPED_VISUAL_PROOF_AUTHORIZATION or FAILED_WITH_EVIDENCE.\n"""
        status = "Automatic authoring passed. Visual acceptance remains unproven."
    else:
        next_path = NEXT_FAILURE
        next_text = f"""Resume only D:\\Skyguard52. Perform one offline-only Recovery06 correction design using the immutable Recovery05 failure evidence. Do not launch Unreal or Blender. Diagnose only this exact failure: {outcome['failure']!r}. Preserve the accepted input and all failed attempts, create a fresh namespace and bounded correction, validate offline, and stop after a separate one-shot execution prompt.\n"""
        status = f"Automatic authoring failed with immutable evidence: {outcome['failure']}"
    write_new(next_path, next_text)

    addendum = f"""# Toolchain Wave08 Mission 1 Environment Authoring01 Recovery05 Attempt01

Date: 2026-08-08

Classification: `{outcome['classification']}`

{status}

- Unreal launches: `1`
- Retries: `0`
- Exit code: `{outcome['exit_code']}` (`System.Int32`)
- Input map unchanged: `true`
- Output map exists: `{str(outcome['output_map_exists']).lower()}`
- Next gate: `{outcome['next_gate']}`
"""
    write_new(ADDENDUM, addendum)
    write_new(PHASE_ADDENDUM, "# Phase 1-8 Completion Audit Addendum: Recovery05 Attempt01\n\n" + addendum.split("\n", 1)[1])

    freeze_paths = [OFFLINE_FREEZE, POSTFLIGHT_TOOL_FREEZE, MANIFEST, *artifact_paths, POSTFLIGHT, ADDENDUM, PHASE_ADDENDUM, INPUT_MAP, next_path]
    if OUTPUT_MAP.is_file():
        freeze_paths.append(OUTPUT_MAP)
    unique = []
    seen = set()
    for path in freeze_paths:
        key = str(path).lower()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    terminal = {
        "schema": "skyguard.toolchain-wave08.m01-authoring01-recovery05.attempt01-terminal-freeze.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        **outcome,
        "member_count": len(unique),
        "members": [record(path) for path in unique],
        "unreal_launch_count": 1,
        "retry_count": 0,
        "exit_code_type": "System.Int32",
        "input_map_sha256": EXPECTED_INPUT,
    }
    write_json(FREEZE, terminal)
    print(json.dumps({"classification": terminal["classification"], "freeze": record(FREEZE), "member_count": terminal["member_count"], "next_prompt": record(next_path)}, indent=2))


if __name__ == "__main__":
    main()
