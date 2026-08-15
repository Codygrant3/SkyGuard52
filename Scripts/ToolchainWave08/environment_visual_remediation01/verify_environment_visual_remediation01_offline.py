from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_file(path: Path, size: int, expected_hash: str) -> None:
    require(path.is_file(), f"missing authority: {path}")
    require(path.stat().st_size == size, f"byte mismatch: {path}")
    require(sha256(path) == expected_hash, f"hash mismatch: {path}")


def verify(root: Path) -> dict[str, object]:
    docs = root / "Docs/Toolchain/ToolchainWave08/EnvironmentVisualRemediation01"
    required_json = [
        "recovery04_evidence_reconciliation.json",
        "full_resolution_defect_matrix.json",
        "installed_ue58_authority_report.json",
        "environment_remediation_contract.json",
        "visible_asset_material_readiness_inventory.json",
        "production_gap_and_sequence.json",
    ]
    for name in required_json:
        require(isinstance(load_json(docs / name), dict), f"invalid JSON object: {name}")

    verify_file(
        root / "Docs/AAA_Review/TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY04_ATTEMPT01_TERMINAL_FREEZE.json",
        10431,
        "3af0c3f9e9a4c7f38ef0294702422d9c5aafd026c8a08da73e3680115d798851",
    )
    verify_file(
        root / "Scripts/ToolchainWave08/environment_authoring01_recovery07/author_m01_environment_authoring01_recovery07.py",
        22741,
        "faf3120733e9fcd3a8c10244a1cf72a9018944422b7a0588689ad892531bb6a1",
    )
    verify_file(
        Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentAuthoring01_Recovery07.umap"),
        625041,
        "401fb7a86321c05f977347185e41fd0ea0436ef7ec3d06d635935ad5f4ce702f",
    )
    verify_file(
        root / "Content/Skyguard/Meshes/Source/Mission01/Coastal_Production_001/BLD_M01_COAST_PROD_001_MASTER.blend",
        201985,
        "4cb6bc2acc06310c4328687d65c808db6adfe5b1c5e49774a81bec60bf4a08cb",
    )
    manifest = load_json(root / "Saved/Reports/BLD_M01_COAST_PROD_001_MANIFEST.json")
    require(len(manifest["assets"]) == 38, "coastal scaffold asset count changed")

    readiness = load_json(docs / "visible_asset_material_readiness_inventory.json")
    require(readiness["classification"] == "VISIBLE_ASSET_GATE_BLOCKED", "asset gate softened")
    sequence = load_json(docs / "production_gap_and_sequence.json")
    require(sequence["first_executable_gate"]["process"] == "Blender 5.2", "wrong next heavy process")
    contract = load_json(docs / "environment_remediation_contract.json")
    require(contract["grounding"]["primary_api"].startswith("ALandscapeProxy::GetHeightAtLocation"), "constant grounding retained")
    require(contract["supervisor_lifecycle"]["retries"] == 0, "retry contract changed")

    forbidden_future = [
        root / "Saved/BuildAttempts/TOOLCHAIN_WAVE08_M01_ENVIRONMENT_VISUAL_REMEDIATION01/attempt_01",
        Path(r"D:\SG52T08_ENV01\Content\ToolchainWave08\Environment\Lvl_M01_T08_EnvironmentVisualRemediation01.umap"),
        root / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA/attempt_01",
        root / "Content/Skyguard/Meshes/Source/Mission01/VisibleEnvironmentKit_Refinement01_StageA",
    ]
    for path in forbidden_future:
        require(not path.exists(), f"future namespace already exists: {path}")

    return {
        "classification": "PASS",
        "required_json": len(required_json),
        "immutable_authorities_verified": 4,
        "coastal_scaffold_assets": 38,
        "next_heavy_gate": "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA",
        "future_namespaces_absent": len(forbidden_future),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.root)
    except Exception as exc:
        result = {"classification": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
        code = 1
    else:
        code = 0
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
