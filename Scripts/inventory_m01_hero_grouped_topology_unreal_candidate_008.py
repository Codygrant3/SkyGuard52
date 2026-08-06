"""Hash-inventory the exact isolated candidate before an authorized rollback."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CANDIDATE = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008"
CONTRACT = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_ACCEPTANCE_008_CONTRACT.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    expected_candidate = (
        ROOT / contract["unreal"]["candidate_root"].removeprefix("/Game/")
    )
    # /Game maps to the project's Content directory.
    expected_candidate = ROOT / "Content" / contract["unreal"]["candidate_root"].removeprefix("/Game/")
    if CANDIDATE.resolve() != expected_candidate.resolve():
        raise RuntimeError("candidate filesystem path differs from contract")
    files = [
        {
            "path": str(path),
            "relative_path": str(path.relative_to(CANDIDATE)).replace("\\", "/"),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(CANDIDATE.rglob("*"))
        if path.is_file()
    ]
    canonical = []
    for name in ("manifest", "low_glb", "master_blend"):
        record = contract["bound_sources"][name]
        path = ROOT / record["path"]
        canonical.append(
            {
                "name": name,
                "path": str(path),
                "expected_bytes": record["bytes"],
                "actual_bytes": path.stat().st_size,
                "expected_sha256": record["sha256"],
                "actual_sha256": sha256(path),
                "matches": (
                    path.stat().st_size == record["bytes"]
                    and sha256(path) == record["sha256"]
                ),
            }
        )
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-candidate-rollback-inventory.v1",
        "build_id": contract["build_id"],
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "attempt": str(args.attempt),
        "candidate_root": contract["unreal"]["candidate_root"],
        "candidate_filesystem_path": str(CANDIDATE),
        "candidate_path_matches_contract": True,
        "candidate_file_count": len(files),
        "candidate_files": files,
        "canonical_inputs": canonical,
        "canonical_inputs_unchanged": all(item["matches"] for item in canonical),
        "rollback_authorized": True,
        "rollback_completed": False,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    output = args.attempt / "rollback_inventory.json"
    if output.exists():
        raise RuntimeError("rollback inventory already exists; never overwrite")
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
