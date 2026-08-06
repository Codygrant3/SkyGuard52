"""Offline fail-closed readiness gate for Yak-52 R4 Slice 01 Recovery01."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUILD_ID = "BLD-M01-YAK-FINAL-ART-R4-S01-RECOVERY01"
CONTRACT_REL = Path(
    "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY01_OUTPUT_CONTRACT.json"
)
RECOVERY_SCRIPT_REL = Path(
    "Scripts/blender_phase2_yak52_r4_slice01_recovery01.py"
)
FROZEN_SCRIPT_REL = Path(
    "Scripts/blender_phase2_yak52_r4_slice01_silhouette.py"
)
WRAPPER_REL = Path(
    "Scripts/invoke_phase2_yak52_r4_slice01_recovery01.ps1"
)
REPORT_ROOT_REL = Path(
    "Saved/Reports/Phase2Yak52R4Slice01Recovery01Readiness"
)
FALSE_CLAIMS = {
    "blender_launched",
    "unreal_launched",
    "outputs_created",
    "reference_package_complete",
    "silhouette_locked",
    "slice01_human_accepted",
    "final",
    "aaa",
    "unreal_imported",
    "runtime_replaced",
    "promotion_allowed",
}
EXPECTED_ACCESS_PATHS = {
    "build_id",
    "authority_inputs",
    "authority_inputs[]",
    "authority_inputs[].path",
    "authority_inputs[].bytes",
    "authority_inputs[].sha256",
    "authoring_script",
    "authoring_script.sha256",
    "outputs",
    "outputs.blend",
    "outputs.glb",
    "outputs.manifest",
    "outputs.comparison_directory",
    "claims",
    "claims.silhouette_locked",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def contract_path_exists(contract: dict[str, Any], key_path: str) -> bool:
    current: Any = contract
    parts = key_path.split(".")
    for index, part in enumerate(parts):
        if part.endswith("[]"):
            key = part[:-2]
            if not isinstance(current, dict) or key not in current:
                return False
            current = current[key]
            if not isinstance(current, list) or not current:
                return False
            remainder = ".".join(parts[index + 1 :])
            return not remainder or all(
                isinstance(item, dict) and contract_path_exists(item, remainder)
                for item in current
            )
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def _contract_chain(
    node: ast.AST, aliases: dict[str, tuple[str, ...]]
) -> tuple[str, ...] | None:
    if isinstance(node, ast.Name) and node.id in aliases:
        return aliases[node.id]
    if isinstance(node, ast.Subscript):
        base = _contract_chain(node.value, aliases)
        if (
            base is not None
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            return base + (node.slice.value,)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    ):
        base = _contract_chain(node.func.value, aliases)
        if base is not None:
            return base + (node.args[0].value,)
    return None


def extract_frozen_contract_paths(source: str) -> set[str]:
    tree = ast.parse(source)
    aliases: dict[str, tuple[str, ...]] = {"contract": ()}
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            chain = _contract_chain(node.iter, aliases)
            if chain:
                aliases[node.target.id] = chain[:-1] + (chain[-1] + "[]",)
    paths: set[str] = set()
    for node in ast.walk(tree):
        chain = _contract_chain(node, aliases)
        if chain:
            paths.add(".".join(chain))
    return paths


def validate_contract_data(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema") != (
        "skyguard.phase2.yak52-r4-slice01-recovery01-output-contract.v1"
    ):
        errors.append("Recovery01 schema mismatch")
    if contract.get("contract_id") != (
        "PHASE2-YAK52-R4-S01-RECOVERY01-OUTPUTS-20260802-V1"
    ):
        errors.append("Recovery01 contract id mismatch")
    if contract.get("build_id") != BUILD_ID:
        errors.append("Recovery01 build id mismatch")
    if contract.get("current_status") != (
        "RECOVERY01_AUTHORING_SOURCE_READY_NOT_RUN"
    ):
        errors.append("Recovery01 status must remain ready-not-run")

    evidence = contract.get("recovery_evidence", {})
    if evidence.get("exact_failure") != "KeyError: 'outputs'":
        errors.append("Recovery01 exact failure evidence mismatch")
    if evidence.get("root_cause") != (
        "The frozen Blender source accessed contract['outputs'] while the "
        "frozen Slice 01 contract exposed only output_policy.paths."
    ):
        errors.append("Recovery01 root cause mismatch")
    for field in (
        "canonical_outputs_created",
        "frozen_package_modified",
    ):
        if evidence.get(field) is not False:
            errors.append(f"Recovery01 evidence must remain false: {field}")
    if evidence.get("failed_invocation_preserved") is not True:
        errors.append("failed invocation must remain preserved")

    claims = contract.get("claims", {})
    for claim in sorted(FALSE_CLAIMS):
        if claims.get(claim) is not False:
            errors.append(f"claim must remain false: {claim}")

    manifest = contract.get("frozen_contract_access_manifest")
    if not isinstance(manifest, list) or set(manifest) != EXPECTED_ACCESS_PATHS:
        errors.append("frozen contract access manifest mismatch")
    elif len(manifest) != len(EXPECTED_ACCESS_PATHS):
        errors.append("frozen contract access manifest contains duplicates")
    for path in EXPECTED_ACCESS_PATHS:
        if not contract_path_exists(contract, path):
            errors.append(f"Recovery01 contract key path missing: {path}")

    outputs = contract.get("outputs", {})
    policy = contract.get("output_policy", {})
    policy_paths = policy.get("paths", {})
    alias = {
        "blend": policy_paths.get("blend"),
        "glb": policy_paths.get("glb"),
        "manifest": policy_paths.get("manifest"),
        "comparison_directory": policy_paths.get("screenshot_directory"),
    }
    if outputs != alias:
        errors.append("Recovery01 output alias and output policy disagree")
    if not all(
        isinstance(value, str) and "recovery01" in value.lower()
        for value in outputs.values()
    ):
        errors.append("Recovery01 outputs are not isolated in a new namespace")
    for field in (
        "overwrite_allowed",
        "automatic_promotion_allowed",
        "unreal_import_allowed",
    ):
        if policy.get(field) is not False:
            errors.append(f"Recovery01 output policy must forbid {field}")
    for field in (
        "atomic_canonical_publication_required",
        "canonical_outputs_must_be_absent_before_run",
    ):
        if policy.get(field) is not True:
            errors.append(f"Recovery01 output policy must require {field}")

    source = contract.get("source_policy", {})
    if source.get("frozen_source_reused_as_code_only") is not True:
        errors.append("frozen source reuse boundary missing")
    if source.get("scene_origin") != "FACTORY_EMPTY_ONLY":
        errors.append("Recovery01 must start factory-empty")
    for field in (
        "accepted_blend_open_allowed",
        "accepted_blend_append_allowed",
        "accepted_blend_link_allowed",
        "r3_donor_geometry_allowed",
        "external_mesh_import_allowed",
        "network_access_allowed",
    ):
        if source.get(field) is not False:
            errors.append(f"Recovery01 source policy must forbid {field}")

    launch = contract.get("launch_contract", {})
    if launch.get("wrapper") != WRAPPER_REL.as_posix():
        errors.append("Recovery01 launch wrapper path mismatch")
    if launch.get("mode") != "background_factory_startup_python":
        errors.append("Recovery01 launch mode mismatch")
    if launch.get("required_attempt_files") != [
        "blender.stdout.log",
        "blender.stderr.log",
        "launch_receipt.json",
        "SHA256SUMS.txt",
    ]:
        errors.append("Recovery01 attempt file contract mismatch")
    if launch.get("launch_authorized") is not False:
        errors.append("Recovery01 launch must remain unauthorized")
    if launch.get("launched") is not False:
        errors.append("Recovery01 contract cannot claim launch")

    return errors


def validate_authorities(root: Path, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    authorities = contract.get("authority_inputs", [])
    if len(authorities) != 12:
        errors.append("Recovery01 authority input count mismatch")
    for authority in authorities:
        relative = authority.get("path")
        if not isinstance(relative, str):
            errors.append("Recovery01 authority path invalid")
            continue
        path = root / relative
        if not path.is_file():
            errors.append(f"Recovery01 authority missing: {relative}")
            continue
        if path.stat().st_size != authority.get("bytes"):
            errors.append(f"Recovery01 authority size drift: {relative}")
        if sha256_file(path) != authority.get("sha256"):
            errors.append(f"Recovery01 authority hash drift: {relative}")
    return errors


def validate_sources(root: Path, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    authoring = contract.get("authoring_script", {})
    recovery_path = root / RECOVERY_SCRIPT_REL
    if not recovery_path.is_file():
        errors.append("Recovery01 authoring script missing")
    else:
        if recovery_path.stat().st_size != authoring.get("bytes"):
            errors.append("Recovery01 authoring script size drift")
        if sha256_file(recovery_path) != authoring.get("sha256"):
            errors.append("Recovery01 authoring script hash drift")
        recovery_source = recovery_path.read_text(encoding="utf-8")
        for literal in (
            BUILD_ID,
            "prove_contract_accesses(contract)",
            "configure_recovery_namespace(frozen)",
            "frozen.main()",
        ):
            if literal not in recovery_source:
                errors.append(f"Recovery01 authoring marker missing: {literal}")

    frozen_path = root / FROZEN_SCRIPT_REL
    frozen_source = frozen_path.read_text(encoding="utf-8")
    extracted = extract_frozen_contract_paths(frozen_source)
    declared = set(contract.get("frozen_contract_access_manifest", []))
    if extracted != EXPECTED_ACCESS_PATHS:
        errors.append(
            "frozen source contract access extraction changed: "
            f"{sorted(extracted)}"
        )
    if extracted != declared:
        errors.append("Recovery01 contract does not cover every frozen key path")
    for path in extracted:
        if not contract_path_exists(contract, path):
            errors.append(f"extracted frozen contract key path missing: {path}")

    wrapper = contract.get("launch_contract", {})
    wrapper_path = root / WRAPPER_REL
    if not wrapper_path.is_file():
        errors.append("Recovery01 launch wrapper missing")
    else:
        if wrapper_path.stat().st_size != wrapper.get("wrapper_bytes"):
            errors.append("Recovery01 launch wrapper size drift")
        if sha256_file(wrapper_path) != wrapper.get("wrapper_sha256"):
            errors.append("Recovery01 launch wrapper hash drift")
        wrapper_source = wrapper_path.read_text(encoding="utf-8")
        for marker in (
            "[switch]$AuthorizeProduction",
            "if (-not $AuthorizeProduction)",
            "--background",
            "--factory-startup",
            "--python",
            "-RedirectStandardOutput $stdoutPath",
            "-RedirectStandardError $stderrPath",
            "launch_receipt.json",
            "SHA256SUMS.txt",
            "automatic_promotion_allowed = $false",
        ):
            if marker not in wrapper_source:
                errors.append(f"Recovery01 wrapper marker missing: {marker}")
    return errors


def validate_failure_evidence(root: Path) -> list[str]:
    errors: list[str] = []
    stdout = (
        root
        / "Saved/Logs/phase2_r4_slice01_blender_20260802T190637Z.stdout.log"
    ).read_text(encoding="utf-8-sig")
    stderr = (
        root
        / "Saved/Logs/phase2_r4_slice01_blender_20260802T190637Z.stderr.log"
    ).read_text(encoding="utf-8-sig")
    if "Blender 5.2.0 LTS" not in stdout or "Blender quit" not in stdout:
        errors.append("failed-invocation stdout evidence mismatch")
    if "KeyError: 'outputs'" not in stderr:
        errors.append("failed-invocation stderr does not prove exact KeyError")
    if "ensure_canonical_outputs_absent" not in stderr:
        errors.append("failed-invocation traceback stage mismatch")
    return errors


def validate_output_absence(root: Path, contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for name, relative in contract.get("outputs", {}).items():
        if (root / relative).exists():
            errors.append(f"Recovery01 output must be absent: {name}:{relative}")
    frozen = read_json(
        root
        / "Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_OUTPUT_CONTRACT.json"
    )
    for name, relative in frozen.get("output_policy", {}).get("paths", {}).items():
        if (root / relative).exists():
            errors.append(f"frozen failed-attempt output must remain absent: {name}")
    production_root = (
        root / "Saved/Reports/Phase2Yak52R4Slice01Recovery01Production"
    )
    if production_root.exists():
        errors.append("Recovery01 production attempt root must not exist at readiness")
    return errors


def run_validation(root: Path) -> tuple[dict[str, Any], list[str]]:
    contract = read_json(root / CONTRACT_REL)
    errors = validate_contract_data(contract)
    errors.extend(validate_authorities(root, contract))
    errors.extend(validate_sources(root, contract))
    errors.extend(validate_failure_evidence(root))
    errors.extend(validate_output_absence(root, contract))
    blender = Path(
        contract.get("launch_contract", {}).get("blender_executable", "")
    )
    if not blender.is_file():
        errors.append("contracted Blender 5.2 executable missing")
    return contract, errors


def write_report(
    root: Path, contract: dict[str, Any], errors: list[str]
) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    contract_hash = sha256_file(root / CONTRACT_REL)
    attempt = (
        root
        / REPORT_ROOT_REL
        / f"attempt_{timestamp}_{contract_hash[:8]}_{os.getpid():08x}"
    )
    attempt.mkdir(parents=True, exist_ok=False)
    report = {
        "schema": "skyguard.phase2.yak52-r4-slice01-recovery01-readiness-report.v1",
        "build_id": BUILD_ID,
        "status": (
            "PASS_RECOVERY01_READY_NOT_RUN"
            if not errors
            else "FAIL_RECOVERY01_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "contract": {
            "path": CONTRACT_REL.as_posix(),
            "bytes": (root / CONTRACT_REL).stat().st_size,
            "sha256": contract_hash,
        },
        "frozen_contract_access_paths": sorted(EXPECTED_ACCESS_PATHS),
        "failed_invocation_preserved": True,
        "canonical_outputs_absent": not any("output must" in e for e in errors),
        "blender_launched_by_gate": False,
        "unreal_launched_by_gate": False,
        "production_started": False,
        "errors": errors,
    }
    report_path = attempt / "recovery01_readiness_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (attempt / "SHA256SUMS.txt").write_text(
        f"{sha256_file(report_path)}  {report_path.name}\n",
        encoding="utf-8",
    )
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    contract, errors = run_validation(root)
    result: dict[str, Any] = {
        "build_id": BUILD_ID,
        "status": (
            "PASS_RECOVERY01_READY_NOT_RUN"
            if not errors
            else "FAIL_RECOVERY01_NOT_READY"
        ),
        "error_count": len(errors),
        "errors": errors,
        "blender_launched_by_gate": False,
        "unreal_launched_by_gate": False,
        "production_started": False,
    }
    if not args.no_write:
        result["report_path"] = str(
            write_report(root, contract, errors).relative_to(root)
        ).replace("\\", "/")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
