from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
DOC_ROOT = ROOT / r"Docs\Toolchain\ToolchainWave08\M01EnvironmentProductionReset01HeroStreetshoreProof01"
WORKER = ROOT / r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01.py"
POSTFLIGHT = ROOT / r"Scripts\Workers\adjudicate_m01_environment_hero_streetshore_proof01.py"
MANIFEST = ROOT / r"Production\production_manifest.json"
ATTEMPT_ROOT = ROOT / r"Production\Attempts\m01-environment-hero-streetshore-proof01"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    required_docs = (
        "evidence_reconciliation.json",
        "local_pbr_authority_inventory.json",
        "production_reset_contract.json",
        "visual_acceptance_rubric.json",
        "execution_contract.json",
    )
    documents: dict[str, Any] = {}
    for name in required_docs:
        path = DOC_ROOT / name
        if not path.is_file():
            errors.append(f"missing document: {path}")
            continue
        try:
            documents[name] = load_json(path)
        except Exception as exc:
            errors.append(f"invalid JSON {name}: {exc}")

    for path in (WORKER, POSTFLIGHT):
        if not path.is_file():
            errors.append(f"missing source: {path}")
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"Python syntax failure {path}: {exc}")

    if WORKER.is_file():
        source = WORKER.read_text(encoding="utf-8")
        required_tokens = (
            'ASSET_ID = "m01-environment-hero-streetshore-proof01"',
            'GATE = "M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01"',
            '"daylight", "wet_overcast", "night"',
            '"route_composite"',
            '"facade_close"',
            '"shoreline_close"',
            'stats["vertices"] >= 12000',
            'SOCKET_Shoreline_Origin',
            'UCX_',
            'bpy.ops.export_scene.gltf',
            'bpy.ops.wm.save_as_mainfile',
            'recovery10_mesh_reuse": False',
            'external_model_use": False',
        )
        for token in required_tokens:
            if token not in source:
                errors.append(f"worker missing required token: {token}")
        if source.count("bpy.ops.export_scene.gltf") != 1:
            errors.append("worker must contain exactly one GLB export call")
        if source.count("bpy.ops.wm.save_as_mainfile") != 1:
            errors.append("worker must contain exactly one governed blend save call")
        prohibited = (
            "stagea_recovery10",
            "VisibleEnvironmentKit_Refinement01_StageA_Recovery10",
            "requests.get(",
            "urllib.request",
            "bpy.ops.wm.open_mainfile",
            "bpy.data.libraries.load",
        )
        for token in prohibited:
            if token in source:
                errors.append(f"worker contains prohibited dependency or reuse token: {token}")

    inventory = documents.get("local_pbr_authority_inventory.json", {})
    authorities = inventory.get("texture_authorities", []) if isinstance(inventory, dict) else []
    if len(authorities) != 20:
        errors.append(f"expected twenty texture authorities, found {len(authorities)}")
    for record in authorities:
        path = ROOT / record.get("path", "")
        if not path.is_file():
            errors.append(f"missing texture authority: {path}")
            continue
        if path.stat().st_size != int(record.get("bytes", -1)):
            errors.append(f"texture byte mismatch: {path}")
        elif sha256(path) != record.get("sha256"):
            errors.append(f"texture hash mismatch: {path}")
    provenance = inventory.get("provenance", {}) if isinstance(inventory, dict) else {}
    provenance_path = ROOT / provenance.get("path", "")
    if not provenance_path.is_file():
        errors.append("provenance manifest missing")
    elif provenance_path.stat().st_size != int(provenance.get("bytes", -1)) or sha256(provenance_path) != provenance.get("sha256"):
        errors.append("provenance manifest authority mismatch")

    try:
        manifest = load_json(MANIFEST)
        assets = [asset for asset in manifest.get("assets", []) if asset.get("id") == "m01-environment-hero-streetshore-proof01"]
        if len(assets) != 1:
            errors.append(f"manifest asset cardinality is {len(assets)}")
        elif assets[0].get("status") != "ready":
            errors.append(f"manifest asset is {assets[0].get('status')}, not ready")
        elif assets[0].get("worker", {}).get("script") != r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01.py":
            errors.append("manifest worker binding mismatch")
    except Exception as exc:
        errors.append(f"manifest validation failed: {exc}")

    if ATTEMPT_ROOT.exists():
        errors.append(f"future attempt root already exists: {ATTEMPT_ROOT}")

    result = {
        "schema": "skyguard.m01-environment-production-reset01.hero-streetshore-proof01.offline-verification.v1",
        "classification": "PASS" if not errors else "FAIL",
        "errors": errors,
        "worker": {"path": str(WORKER), "bytes": WORKER.stat().st_size if WORKER.is_file() else None, "sha256": sha256(WORKER) if WORKER.is_file() else None},
        "postflight": {"path": str(POSTFLIGHT), "bytes": POSTFLIGHT.stat().st_size if POSTFLIGHT.is_file() else None, "sha256": sha256(POSTFLIGHT) if POSTFLIGHT.is_file() else None},
        "texture_authorities_verified": len(authorities) - sum(1 for error in errors if "texture" in error),
        "future_attempt_root_absent": not ATTEMPT_ROOT.exists(),
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 4


if __name__ == "__main__":
    raise SystemExit(main())
