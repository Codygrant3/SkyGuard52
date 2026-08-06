"""Build a deterministic offline inventory for one manually acquired Fab kit.

This tool never downloads, imports, extracts, or launches another process. It
only hashes an already populated, slot-specific quarantine payload directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = Path("Saved/FabQuarantine/M01_FAB_QUARANTINE_INTAKE_001")
SLOT_ROOTS = {
    "CITY_KIT": EVIDENCE_ROOT / "staging/CITY_KIT/payload",
    "BEACH_COAST_KIT": EVIDENCE_ROOT / "staging/BEACH_COAST_KIT/payload",
}
OUTPUTS = {
    slot: EVIDENCE_ROOT / f"manifests/{slot}_FILES.json"
    for slot in SLOT_ROOTS
}
EXECUTABLE_SUFFIXES = {
    ".bat", ".cmd", ".com", ".dll", ".exe", ".msi", ".ps1", ".py",
    ".sh", ".so", ".vbs",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_hash(files: list[dict]) -> str:
    digest = hashlib.sha256()
    for item in files:
        digest.update(
            (
                f"{item['path']}\0{item['bytes']}\0{item['sha256']}\n"
            ).encode("utf-8")
        )
    return digest.hexdigest()


def build_inventory(project_root: Path, slot: str) -> dict:
    if slot not in SLOT_ROOTS:
        raise ValueError(f"Unsupported slot: {slot}")
    project_root = project_root.resolve()
    relative_root = SLOT_ROOTS[slot]
    payload_root = (project_root / relative_root).resolve()
    expected_parent = (project_root / EVIDENCE_ROOT / "staging").resolve()
    if expected_parent not in payload_root.parents:
        raise ValueError("Resolved staging root escaped the quarantine tree")
    if not payload_root.is_dir():
        raise FileNotFoundError(f"Staging payload is missing: {relative_root}")

    files: list[dict] = []
    symlinks: list[str] = []
    executables: list[str] = []
    for path in sorted(payload_root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(project_root).as_posix()
        if path.is_symlink():
            symlinks.append(relative)
            continue
        if not path.is_file():
            continue
        item = {
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        files.append(item)
        if path.suffix.lower() in EXECUTABLE_SUFFIXES:
            executables.append(relative)
    if not files:
        raise ValueError(f"Staging payload is empty: {relative_root}")

    return {
        "schema": "skyguard.m01.fab-staging-inventory.v1",
        "slot": slot,
        "staging_root": relative_root.as_posix(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "tree_sha256": tree_hash(files),
        "files": files,
        "symlink_files": symlinks,
        "unexpected_executable_files": executables,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--slot", required=True, choices=sorted(SLOT_ROOTS)
    )
    parser.add_argument("--project-root", type=Path, default=ROOT)
    args = parser.parse_args()
    inventory = build_inventory(args.project_root, args.slot)
    output = args.project_root / OUTPUTS[args.slot]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(inventory, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "slot": args.slot,
        "output": output.relative_to(args.project_root).as_posix(),
        "file_count": inventory["file_count"],
        "total_bytes": inventory["total_bytes"],
        "tree_sha256": inventory["tree_sha256"],
        "unexpected_executable_files":
            inventory["unexpected_executable_files"],
        "symlink_files": inventory["symlink_files"],
    }, indent=2))
    return 0 if not inventory["unexpected_executable_files"] and not inventory["symlink_files"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
