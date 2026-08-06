"""Verify the Phase 1-8 completion audit as a fail-closed evidence matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROW_RE = re.compile(
    r"^\| (?P<id>P(?P<phase>[1-8])\.(?P<index>\d+)) "
    r"\| (?P<requirement>.+?) "
    r"\| \*\*(?P<classification>.+?)\*\* "
    r"\| (?P<evidence>.+?) \|$"
)
SUMMARY_RE = re.compile(
    r"^- (?P<count>\d+) \*\*(?P<classification>"
    r"PROVEN COMPLETE|INCOMPLETE|INSUFFICIENTLY EVIDENCED|"
    r"BLOCKED — EXTERNAL LICENSED SOURCE)\*\*[.;]$"
)
ALLOWED_CLASSIFICATIONS = (
    "PROVEN COMPLETE",
    "PROVEN COMPLETE — AUTOMATED CONTRACT",
    "PROVEN COMPLETE — BASELINE ONLY",
    "PROVEN COMPLETE — CURRENT USED SET",
    "INCOMPLETE",
    "INSUFFICIENTLY EVIDENCED",
    "BLOCKED — EXTERNAL LICENSED SOURCE",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_classification(value: str) -> str:
    if value.startswith("PROVEN COMPLETE"):
        return "PROVEN COMPLETE"
    return value


def verify(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    rows = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = ROW_RE.match(line)
        if match:
            row = match.groupdict()
            row["line"] = line_number
            row["phase"] = int(row["phase"])
            row["index"] = int(row["index"])
            rows.append(row)

    issues: list[dict[str, object]] = []
    ids = [row["id"] for row in rows]
    duplicate_ids = sorted(
        requirement_id
        for requirement_id, count in Counter(ids).items()
        if count > 1
    )
    if duplicate_ids:
        issues.append(
            {
                "code": "DUPLICATE_REQUIREMENT_IDS",
                "detail": duplicate_ids,
            }
        )

    phase_ids: dict[int, list[str]] = defaultdict(list)
    counts = Counter()
    for row in rows:
        phase_ids[row["phase"]].append(row["id"])
        classification = row["classification"]
        if classification not in ALLOWED_CLASSIFICATIONS:
            issues.append(
                {
                    "code": "UNKNOWN_CLASSIFICATION",
                    "requirement_id": row["id"],
                    "detail": classification,
                }
            )
        counts[normalized_classification(classification)] += 1
        if len(row["requirement"].strip()) < 12:
            issues.append(
                {
                    "code": "EMPTY_OR_WEAK_REQUIREMENT",
                    "requirement_id": row["id"],
                }
            )
        if len(row["evidence"].strip()) < 20:
            issues.append(
                {
                    "code": "EMPTY_OR_WEAK_EVIDENCE",
                    "requirement_id": row["id"],
                }
            )

    missing_phases = [phase for phase in range(1, 9) if not phase_ids[phase]]
    if missing_phases:
        issues.append(
            {
                "code": "MISSING_PHASE_REQUIREMENTS",
                "detail": missing_phases,
            }
        )

    stated_counts = {
        match.group("classification"): int(match.group("count"))
        for line in text.splitlines()
        if (match := SUMMARY_RE.match(line))
    }
    expected_summary_keys = {
        "PROVEN COMPLETE",
        "INCOMPLETE",
        "INSUFFICIENTLY EVIDENCED",
        "BLOCKED — EXTERNAL LICENSED SOURCE",
    }
    if set(stated_counts) != expected_summary_keys:
        issues.append(
            {
                "code": "SUMMARY_CLASSIFICATION_SET_MISMATCH",
                "detail": sorted(stated_counts),
            }
        )
    calculated_counts = {
        key: counts.get(key, 0)
        for key in sorted(expected_summary_keys)
    }
    if stated_counts != calculated_counts:
        issues.append(
            {
                "code": "SUMMARY_COUNT_MISMATCH",
                "stated": stated_counts,
                "calculated": calculated_counts,
            }
        )

    if "**M01 Gold Visual and Input-Driven Performance Candidate**" not in text:
        issues.append(
            {
                "code": "MISSING_RECOMMENDED_MILESTONE",
            }
        )

    return {
        "schema": "skyguard.phase1-8-completion-audit-verification.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "audit": {
            "path": str(path.resolve()),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "gate": "PASS" if not issues else "FAIL",
        "requirement_count": len(rows),
        "classification_counts": calculated_counts,
        "requirements_by_phase": {
            f"P{phase}": phase_ids[phase] for phase in range(1, 9)
        },
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.audit.resolve())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2))
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
