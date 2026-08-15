from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
ORIGINAL_WORKER = ROOT / r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01.py"
ORIGINAL_POSTFLIGHT = ROOT / r"Scripts\Workers\adjudicate_m01_environment_hero_streetshore_proof01.py"
WORKER = ROOT / r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01_recovery01.py"
POSTFLIGHT = ROOT / r"Scripts\Workers\adjudicate_m01_environment_hero_streetshore_proof01_recovery01.py"
MANIFEST = ROOT / r"Production\production_manifest.json"
FAILED_FREEZE = ROOT / r"Docs\AAA_Review\M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01_ATTEMPT01_TERMINAL_FREEZE.json"
ASSET_ID = "m01-environment-hero-streetshore-proof01-recovery01"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify() -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        ORIGINAL_WORKER: "94a831f9c0c70c67741e2b1bb7448796f8da70cc875e84c8d5c925583f933866",
        ORIGINAL_POSTFLIGHT: "59cff240704a40b68a70c71b6002391b14e06a9296b7fecbaaeaaecb539c6cac",
    }
    for path, digest in expected.items():
        if not path.is_file() or sha256(path) != digest:
            errors.append(f"frozen authority mismatch: {path}")

    for path in (WORKER, POSTFLIGHT):
        if not path.is_file():
            errors.append(f"missing recovery source: {path}")
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"syntax failure {path}: {exc}")

    if WORKER.is_file():
        source = WORKER.read_text(encoding="utf-8")
        required = (
            "EXPECTED_SOURCE_SHA256",
            "RECOVERY_ASSET_ID",
            "RECOVERY_GATE_ID",
            'scene.render.engine = "BLENDER_EEVEE"',
            "if recovery_text.count(old_value) != 1",
        )
        for token in required:
            if token not in source:
                errors.append(f"worker token missing: {token}")
        if source.count("REPLACEMENTS = (") != 1:
            errors.append("worker replacement declaration cardinality mismatch")

    if not FAILED_FREEZE.is_file():
        errors.append("failed-attempt freeze missing")
    else:
        freeze = load_json(FAILED_FREEZE)
        if freeze.get("classification") != "FAILED_WITH_EVIDENCE":
            errors.append("failed-attempt freeze classification mismatch")
        for member in freeze.get("members", []):
            path = Path(member["path"])
            if not path.is_file() or path.stat().st_size != int(member["bytes"]) or sha256(path) != member["sha256"]:
                errors.append(f"failed-attempt member mismatch: {path}")

    try:
        manifest = load_json(MANIFEST)
        assets = [item for item in manifest.get("assets", []) if item.get("id") == ASSET_ID]
        if len(assets) != 1:
            errors.append(f"recovery manifest cardinality is {len(assets)}")
        else:
            asset = assets[0]
            if asset.get("status") != "ready":
                errors.append(f"recovery asset status is {asset.get('status')!r}")
            if asset.get("worker", {}).get("script") != r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01_recovery01.py":
                errors.append("recovery worker binding mismatch")
            if asset.get("worker", {}).get("postflight", {}).get("script") != r"Scripts\Workers\adjudicate_m01_environment_hero_streetshore_proof01_recovery01.py":
                errors.append("recovery postflight binding mismatch")
    except Exception as exc:
        errors.append(f"manifest validation failed: {exc}")

    attempts = ROOT / "Production" / "Attempts" / ASSET_ID
    if attempts.exists():
        errors.append(f"future recovery attempt root already exists: {attempts}")

    return {
        "schema": "skyguard.m01-environment-production-reset01.hero-streetshore-proof01-recovery01.offline-verification.v1",
        "asset_id": ASSET_ID,
        "classification": "PASS" if not errors else "FAIL",
        "errors": errors,
        "verified_frozen_authorities": len(expected),
        "replacement_count": 3,
        "future_attempt_root_absent": not attempts.exists(),
    }


if __name__ == "__main__":
    report = verify()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["classification"] == "PASS" else 4)
