from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
ASSET_ID = "m01-environment-hero-streetshore-proof01-recovery02"
FILES = {
    ROOT / r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01.py": "94a831f9c0c70c67741e2b1bb7448796f8da70cc875e84c8d5c925583f933866",
    ROOT / r"Docs\AAA_Review\M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json": "b49d338c68f7c32f229ac16ed0671d9844172c0ad0c0b705bd5a5953bd5d12d3",
    ROOT / r"Scripts\Workers\worker_m01_environment_hero_streetshore_proof01_recovery02.py": "dd857d4c8a46f9308ecb2569d567eff67376e45a6de407ab1439fdf4ad2bbde4",
    ROOT / r"Scripts\Workers\adjudicate_m01_environment_hero_streetshore_proof01_recovery02.py": "5cf769dfba8e99f6f7d9c1d186cac87f46109b9b1681ad0a500517280d4e8b78",
    ROOT / r"Scripts\Workers\test_m01_environment_hero_streetshore_proof01_recovery02.py": "b325338ade960b38f514c8972e94d84f91268d6c8ff42888a183bb77647f10a7",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> dict:
    errors = []
    for path, digest in FILES.items():
        if not path.is_file() or sha256(path) != digest:
            errors.append(f"authority mismatch: {path}")
    for path in list(FILES)[2:]:
        if path.suffix == ".py" and path.is_file():
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                errors.append(f"syntax failure: {path}: {exc}")
    worker = list(FILES)[2]
    if worker.is_file():
        text = worker.read_text(encoding="utf-8")
        required = (
            "refined_build_building",
            "refined_add_vehicle",
            "refined_add_tree",
            "refined_build_shore_and_street",
            "refined_configure_condition",
            "refined_render_checkpoints",
            '"shoreline_close": ((31.0, 9.0, 8.2), (1.0, -12.0, -0.15), 50.0)',
        )
        for token in required:
            if token not in text:
                errors.append(f"missing refinement token: {token}")
        for forbidden in ("bpy.ops.import", "requests.", "http://", "https://"):
            if forbidden in text:
                errors.append(f"forbidden source token: {forbidden}")
    try:
        manifest = json.loads((ROOT / r"Production\production_manifest.json").read_text(encoding="utf-8"))
        assets = [a for a in manifest["assets"] if a.get("id") == ASSET_ID]
        if len(assets) != 1 or assets[0].get("status") != "ready":
            errors.append("manifest recovery asset is not uniquely ready")
    except Exception as exc:
        errors.append(f"manifest failure: {exc}")
    attempt_root = ROOT / "Production" / "Attempts" / ASSET_ID
    if attempt_root.exists():
        errors.append("future attempt root already exists")
    return {
        "schema": "skyguard.m01-environment-production-reset01.hero-streetshore-proof01-recovery02.offline-verification.v1",
        "classification": "PASS" if not errors else "FAIL",
        "asset_id": ASSET_ID,
        "errors": errors,
        "verified_authorities": len(FILES),
        "future_attempt_root_absent": not attempt_root.exists(),
    }


if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, indent=2, sort_keys=True))
    sys.exit(0 if result["classification"] == "PASS" else 4)
