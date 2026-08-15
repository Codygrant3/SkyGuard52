from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
REQUIREMENTS = ROOT / "Docs/Toolchain/ToolchainWave08/EnvironmentVisibleKitRefinement01StageBRecovery03Binding/requirements.json"
PROMPT = ROOT / "Docs/AAA_Review/NEXT_PROMPT_M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB_RECOVERY03_POST_STAGEA_RECOVERY03_BINDING.md"
STAGEB_FREEZE = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB_RECOVERY02_PREVENTIVE_FREEZE.json"
STAGEB_WORKER = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stageb_recovery02/build_m01_visible_environment_kit_refinement01_stageb_recovery02.py"
STAGEA_WORKER = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stagea_recovery02/build_m01_visible_environment_kit_refinement01_stagea_recovery02.py"


class ValidationError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate() -> dict[str, object]:
    requirements = json.loads(REQUIREMENTS.read_text(encoding="utf-8"))
    prompt = PROMPT.read_text(encoding="utf-8")
    require(requirements["classification"] == "NONEXECUTABLE_TEMPLATE_AWAITING_ACCEPTED_STAGEA_RECOVERY03", "template classification drift")
    require(len(requirements["future_required_stagea_recovery03_evidence"]) == 4, "future evidence cardinality drift")
    require(all(not Path(row["path"]).exists() for row in requirements["future_required_stagea_recovery03_evidence"]), "StageA Recovery03 evidence unexpectedly exists; bind it in a new immutable gate")
    rules = requirements["binding_rules"]
    require(rules["stageb_supervisor_may_be_created_before_stagea_acceptance"] is False, "premature supervisor creation permitted")
    require(rules["stageb_blender_execution_may_be_authorized_by_binding_gate"] is False, "binding gate permits Blender")
    require(rules["separate_stageb_execution_authorization_required"] is True, "separate authorization missing")
    require(rules["automatic_retry_count"] == 0 and rules["failed_namespace_reuse"] is False, "retry or namespace policy drift")
    require(sha256(STAGEB_FREEZE) == "6d13e2da1ef4ca1569c36abf2adc028298bedf6558553d68854b832a970bd544", "StageB preventive freeze drift")
    require(sha256(STAGEB_WORKER) == "a5c901411511939fd2e2a63b48dc22455280e9f8c9409151ef1465e8e19d7c6b", "StageB worker drift")
    require(sha256(STAGEA_WORKER) == "ec787aae6b0017078634e11ef4d5ad56ada06ba0133d8c3f6a81ad9206374c61", "StageA worker drift")
    require("nonexecutable until StageA Recovery03" in prompt, "prompt does not fail closed")
    require("Do not execute StageB Blender" in prompt, "execution boundary missing")
    require("PASSED_READY_FOR_M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB" in prompt, "acceptance classification missing")
    return {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stageb-recovery03-binding-template.verification.v1",
        "classification": "PASS",
        "existing_authorities": 4,
        "future_acceptance_authorities": 4,
        "future_acceptance_authorities_absent": True,
        "stageb_worker_changed": False,
        "blender_launches": 0,
        "unreal_launches": 0,
    }


def main() -> int:
    try:
        print(json.dumps(validate(), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"classification": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
