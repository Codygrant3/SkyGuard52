#!/usr/bin/env python3
"""Fail-closed local revalidation for the Skyguard 52 Poly Haven source set."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


EXPECTED_EMPTY_FAMILIES = {
    "metal_walkway_01",
    "painted_metal_02",
    "ship_hull",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def verify(project_root: Path) -> dict[str, Any]:
    texture_root = (
        project_root / "Content" / "Skyguard" / "Textures" / "PolyHaven"
    )
    manifest_path = texture_root / "polyhaven-provenance-manifest.json"
    readme_path = texture_root / "README.md"
    surface_manifest_path = texture_root / "surface-build-manifest.json"

    for required in (texture_root, manifest_path, readme_path, surface_manifest_path):
        if not required.exists():
            fail(f"required authority is missing: {required}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest.get("records")
    if not isinstance(records, list):
        fail("expanded provenance manifest records must be a list")
    if manifest.get("record_count") != len(records):
        fail("declared record_count does not equal actual record count")
    if manifest.get("verified_record_count") != len(records):
        fail("not every expanded provenance record is declared verified")
    if manifest.get("failed_records") not in ([], None):
        fail("expanded provenance manifest contains failed_records")

    failures: list[str] = []
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        path = Path(record["path"])
        if not path.exists():
            failures.append(f"missing:{path}")
            continue

        size = path.stat().st_size
        digest = sha256_file(path)
        if size != int(record["local_bytes"]):
            failures.append(f"bytes:{path}")
        if digest != record["local_sha256"]:
            failures.append(f"sha256:{path}")
        if record.get("source") != "Poly Haven":
            failures.append(f"source:{path}")
        if record.get("license") != "CC0-1.0":
            failures.append(f"license:{path}")
        if record.get("license_url") != "https://polyhaven.com/license":
            failures.append(f"license_url:{path}")
        if not record.get("canonical_url_and_length_verified"):
            failures.append(f"canonical_remote_length:{path}")
        if int(record.get("head_status", 0)) != 200:
            failures.append(f"head_status:{path}")
        if int(record.get("remote_content_length", -1)) != size:
            failures.append(f"remote_length:{path}")

        by_family[record["family"]].append(
            {
                "file": record["file"],
                "bytes": size,
                "sha256": digest,
                "source_url": record["source_url"],
            }
        )

    all_directories = {
        path.name for path in texture_root.iterdir() if path.is_dir()
    }
    empty_families = {
        name
        for name in all_directories
        if not any((texture_root / name).rglob("*.*"))
    }

    if failures:
        fail("; ".join(failures))
    if len(records) != 64:
        fail(f"expected 64 records, found {len(records)}")
    if len(by_family) != 21:
        fail(f"expected 21 nonempty verified families, found {len(by_family)}")
    if empty_families != EXPECTED_EMPTY_FAMILIES:
        fail(
            "empty-family set differs: "
            f"expected {sorted(EXPECTED_EMPTY_FAMILIES)}, "
            f"found {sorted(empty_families)}"
        )

    families = []
    for family in sorted(by_family):
        file_rows = sorted(by_family[family], key=lambda row: row["file"])
        payload = "\n".join(
            f"{row['file']}|{row['bytes']}|{row['sha256']}|{row['source_url']}"
            for row in file_rows
        ).encode("utf-8")
        families.append(
            {
                "family": family,
                "file_count": len(file_rows),
                "bytes": sum(int(row["bytes"]) for row in file_rows),
                "family_record_digest_sha256": hashlib.sha256(payload).hexdigest(),
                "all_records_match": True,
            }
        )

    return {
        "schema": "skyguard52.polyhaven-provenance-local-revalidation.v1",
        "classification": "PASSED_LOCAL_AND_RECORDED_REMOTE_PROVENANCE_REVALIDATION",
        "project_root": str(project_root),
        "manifest": {
            "path": str(manifest_path),
            "bytes": manifest_path.stat().st_size,
            "sha256": sha256_file(manifest_path),
            "declared_records": manifest["record_count"],
            "declared_verified_records": manifest["verified_record_count"],
        },
        "license_declaration": {
            "path": str(readme_path),
            "bytes": readme_path.stat().st_size,
            "sha256": sha256_file(readme_path),
            "license": "CC0-1.0",
            "license_url": "https://polyhaven.com/license",
        },
        "surface_build_manifest": {
            "path": str(surface_manifest_path),
            "bytes": surface_manifest_path.stat().st_size,
            "sha256": sha256_file(surface_manifest_path),
        },
        "verified_family_count": len(families),
        "verified_file_count": len(records),
        "verified_bytes": sum(row["bytes"] for row in families),
        "families": families,
        "empty_unverified_families": sorted(empty_families),
        "failures": [],
        "policy_note": (
            "This receipt verifies local file integrity against the expanded "
            "manifest and rechecks its recorded canonical URL/HTTP 200/remote "
            "length evidence. It does not perform a new network request."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(r"D:\Skyguard52"),
    )
    args = parser.parse_args()
    try:
        receipt = verify(args.project_root.resolve())
    except Exception as exc:  # fail closed with machine-readable evidence
        print(
            json.dumps(
                {
                    "schema": "skyguard52.polyhaven-provenance-local-revalidation.v1",
                    "classification": "FAILED_WITH_EVIDENCE",
                    "error": str(exc),
                },
                indent=2,
            )
        )
        return 1
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
