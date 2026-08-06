"""Load the immutable Phase 4 M01 base contract plus attempt02 amendment."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
BASE_PATH = (
    ROOT
    / "Docs/AAA_Review/PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_CONTRACT.json"
)
AMENDMENT_PATH = (
    ROOT
    / "Docs/AAA_Review/PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_CONTRACT_ATTEMPT02.json"
)
ATTEMPT03_PATH = (
    ROOT
    / "Docs/AAA_Review/PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_CONTRACT_ATTEMPT03.json"
)
ATTEMPT04_PATH = (
    ROOT
    / "Docs/AAA_Review/PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_CONTRACT_ATTEMPT04.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def deep_merge(target: dict, overlay: dict) -> dict:
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge(target[key], value)
        else:
            target[key] = copy.deepcopy(value)
    return target


def load_effective_contract() -> dict:
    base = json.loads(BASE_PATH.read_text(encoding="utf-8-sig"))
    amendment = json.loads(AMENDMENT_PATH.read_text(encoding="utf-8-sig"))
    if sha256_file(BASE_PATH) != amendment["base_contract_sha256"]:
        raise RuntimeError("Attempt02 base contract hash mismatch")
    if amendment["supersedes_contract_id"] != base["contract_id"]:
        raise RuntimeError("Attempt02 superseded contract ID mismatch")
    attempt03 = json.loads(ATTEMPT03_PATH.read_text(encoding="utf-8-sig"))
    if sha256_file(AMENDMENT_PATH) != attempt03["prior_amendment_sha256"]:
        raise RuntimeError("Attempt03 prior amendment hash mismatch")
    if attempt03["supersedes_contract_id"] != amendment["contract_id"]:
        raise RuntimeError("Attempt03 superseded contract ID mismatch")
    attempt04 = json.loads(ATTEMPT04_PATH.read_text(encoding="utf-8-sig"))
    if sha256_file(ATTEMPT03_PATH) != attempt04["prior_amendment_sha256"]:
        raise RuntimeError("Attempt04 prior amendment hash mismatch")
    if attempt04["supersedes_contract_id"] != attempt03["contract_id"]:
        raise RuntimeError("Attempt04 superseded contract ID mismatch")
    effective = deep_merge(copy.deepcopy(base), amendment["overrides"])
    effective = deep_merge(effective, attempt03["overrides"])
    effective = deep_merge(effective, attempt04["overrides"])
    effective["schema"] = attempt04["effective_schema"]
    effective["contract_id"] = attempt04["contract_id"]
    effective["status"] = attempt04["status"]
    effective["amendment"] = {
        "path": str(ATTEMPT04_PATH),
        "sha256": sha256_file(ATTEMPT04_PATH),
        "prior_path": str(ATTEMPT03_PATH),
        "prior_sha256": attempt04["prior_amendment_sha256"],
        "base_path": str(BASE_PATH),
        "base_sha256": amendment["base_contract_sha256"],
        "failed_attempt01_evidence": amendment["failed_attempt_evidence"],
        "failed_attempt02_evidence": attempt03["failed_attempt_evidence"],
        "failed_attempt03_evidence": attempt04["failed_attempt_evidence"],
    }
    return effective
