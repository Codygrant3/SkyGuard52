"""Evidence-backed visual feedback memory for Skyguard production.

The production pipeline already preserves every attempt.  This module adds the
missing decision layer: repeated visual failures become a durable strategy
constraint instead of another cosmetic recovery with a new suffix.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEMORY_PATH = ROOT / "Production" / "visual_feedback_memory.json"
SCHEMA = "skyguard.visual-feedback-memory.v1"
DEFAULT_PIVOT_THRESHOLD = 2

CATEGORY_ALIASES = {
    "facade": "facades",
    "façade": "facades",
    "building": "architecture",
    "buildings": "architecture",
    "city": "urban_density",
    "exposure": "lighting",
    "shadow": "lighting",
    "shadows": "lighting",
    "ocean": "water",
    "surf": "shoreline",
    "beach": "shoreline",
    "material": "surfaces",
    "materials": "surfaces",
    "lighthouse": "landmarks",
    "tree": "vegetation",
    "trees": "vegetation",
    "vehicle": "urban_density",
    "vehicles": "urban_density",
}

KEYWORD_CATEGORIES = (
    ("lighting", ("exposure", "shadow", "black", "ambient fill", "crushed")),
    ("architecture", ("building", "apartment", "midrise", "silhouette", "blockout")),
    ("facades", ("facade", "façade", "window", "balcon", "entrance", "roofline")),
    ("urban_density", ("vehicle", "street furniture", "empty", "parcel", "signage", "utility")),
    ("vegetation", ("tree", "vegetation", "canop", "foliage")),
    ("shoreline", ("shore", "surf", "foam", "wet sand", "waterline", "beach")),
    ("water", ("water", "ocean", "tiling", "cyan")),
    ("landmarks", ("lighthouse", "landmark", "radar")),
    ("surfaces", ("material", "roughness", "grime", "weather", "asphalt", "concrete", "plaster")),
)

PIVOT_REQUIRED_TAGS = (
    "asset_specific",
    "authored_geometry",
    "checkpointed_visual_review",
    "governed_local_pbr",
    "small_hero_cell",
)

PIVOT_FORBIDDEN_TAGS = (
    "cosmetic_only_recovery",
    "full_corridor_proof_before_hero_cell_acceptance",
    "lighting_only_recovery",
    "same_namespace_retry",
    "whole_scene_procedural_primitive_generation",
)

CATEGORY_REQUIREMENTS = {
    "architecture": "At least three visibly distinct authored building silhouettes with different massing and rooflines.",
    "facades": "Recessed openings, real balcony/entrance depth and nonrepeating facade rhythms at gameplay distance.",
    "landmarks": "Replace proxy landmark silhouettes with an asset-specific hero model.",
    "lighting": "Validate readable shadow-side facades under the fixed rear-gunner cameras before final rendering.",
    "shoreline": "Author a natural water-to-wet-sand-to-dry-sand transition with broken surf contact.",
    "surfaces": "Use governed PBR families with calibrated macro variation, roughness, weathering, salt and grime.",
    "urban_density": "Ground secondary structures, parked vehicles, utilities, signage and street furniture in the hero cell.",
    "vegetation": "Use credible nonproxy coastal vegetation or explicitly defer vegetation rather than inserting primitive stand-ins.",
    "water": "Use Unreal water for the final mapped proof; Blender review water must be clearly review-only.",
}


class FeedbackError(RuntimeError):
    pass


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FeedbackError(f"Missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise FeedbackError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FeedbackError(f"JSON root must be an object: {path}")
    return value


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def empty_memory(pivot_threshold: int = DEFAULT_PIVOT_THRESHOLD) -> dict[str, Any]:
    if pivot_threshold < 2:
        raise FeedbackError("Pivot threshold must be at least two independent failed reviews.")
    return {
        "schema": SCHEMA,
        "updated_at_utc": None,
        "policy": {
            "pivot_threshold": pivot_threshold,
            "same_source_hash_is_idempotent": True,
            "automatic_visual_acceptance": False,
            "cosmetic_retry_after_pivot": False,
        },
        "reviews": [],
        "lanes": {},
    }


def normalize_category(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
    return CATEGORY_ALIASES.get(normalized, normalized or "unclassified")


def infer_category(text: str) -> str:
    lowered = text.lower()
    for category, keywords in KEYWORD_CATEGORIES:
        if any(keyword in lowered for keyword in keywords):
            return category
    return "unclassified"


def extract_findings(review: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    raw_blocking = review.get("blocking_findings", [])
    if isinstance(raw_blocking, list):
        for item in raw_blocking:
            if isinstance(item, dict):
                text = str(item.get("finding", "")).strip()
                category = normalize_category(str(item.get("category", "")))
                if not category or category == "unclassified":
                    category = infer_category(text)
            else:
                text = str(item).strip()
                category = infer_category(text)
            if text:
                findings.append({"category": category, "finding": text})

    raw_remaining = review.get("remaining_failures", [])
    if isinstance(raw_remaining, list):
        for item in raw_remaining:
            text = str(item).strip()
            if text:
                findings.append({"category": infer_category(text), "finding": text})

    if not findings:
        error = str(review.get("error", "")).strip()
        if error:
            findings.append({"category": infer_category(error), "finding": error})
    return findings


def is_failed_review(review: dict[str, Any]) -> bool:
    classification = str(review.get("classification", "")).upper()
    decision = str(review.get("decision", "")).upper()
    return classification.startswith("FAILED") or decision.startswith("REJECT")


def validate_memory(memory: dict[str, Any]) -> None:
    if memory.get("schema") != SCHEMA:
        raise FeedbackError("Unexpected visual-feedback memory schema.")
    policy = memory.get("policy", {})
    threshold = policy.get("pivot_threshold")
    if not isinstance(threshold, int) or threshold < 2:
        raise FeedbackError("Visual-feedback pivot threshold must be an integer >= 2.")
    if not isinstance(memory.get("reviews"), list):
        raise FeedbackError("Visual-feedback reviews must be a list.")
    if not isinstance(memory.get("lanes"), dict):
        raise FeedbackError("Visual-feedback lanes must be an object.")


def _requirements(categories: Iterable[str]) -> list[str]:
    return [CATEGORY_REQUIREMENTS[key] for key in sorted(set(categories)) if key in CATEGORY_REQUIREMENTS]


def recompute(memory: dict[str, Any]) -> dict[str, Any]:
    validate_memory(memory)
    threshold = int(memory["policy"]["pivot_threshold"])
    lanes: dict[str, Any] = {}
    lane_names = sorted({str(record["lane"]) for record in memory["reviews"]})
    for lane in lane_names:
        records = [record for record in memory["reviews"] if record["lane"] == lane]
        failed = [record for record in records if record["failed"]]
        counts = Counter(
            finding["category"]
            for record in failed
            for finding in record.get("findings", [])
            if finding.get("category") != "unclassified"
        )
        repeated = sorted(category for category, count in counts.items() if count >= threshold)
        explicit_primitive_ceiling = any(
            "procedural primitive" in str(record.get("root_cause", "")).lower()
            or "procedural blockout" in str(record.get("root_cause", "")).lower()
            for record in failed
        )
        pivot = len(failed) >= threshold and (bool(repeated) or explicit_primitive_ceiling)
        lanes[lane] = {
            "classification": "PIVOT_REQUIRED" if pivot else "CONTINUE_BOUNDED",
            "review_count": len(records),
            "failed_review_count": len(failed),
            "category_counts": dict(sorted(counts.items())),
            "repeated_categories": repeated,
            "explicit_procedural_primitive_ceiling": explicit_primitive_ceiling,
            "required_strategy_tags": list(PIVOT_REQUIRED_TAGS) if pivot else [],
            "forbidden_strategy_tags": list(PIVOT_FORBIDDEN_TAGS) if pivot else [],
            "next_work_requirements": _requirements(repeated or counts.keys()),
            "evidence_sha256": sorted(record["source_sha256"] for record in failed),
        }
    memory["lanes"] = lanes
    memory["updated_at_utc"] = now_utc()
    return memory


def ingest_review(
    memory: dict[str, Any],
    review_path: Path,
    lane: str,
    attempt_id: str,
    strategy_tags: Iterable[str],
) -> tuple[dict[str, Any], bool]:
    validate_memory(memory)
    resolved = review_path.resolve()
    review = load_json(resolved)
    digest = sha256(resolved)
    existing = next(
        (record for record in memory["reviews"] if record.get("source_sha256") == digest),
        None,
    )
    if existing:
        if existing.get("lane") != lane:
            raise FeedbackError("The same immutable review hash is already assigned to another lane.")
        return recompute(memory), False

    findings = extract_findings(review)
    if is_failed_review(review) and not findings:
        raise FeedbackError(f"Failed review has no actionable findings: {resolved}")
    record = {
        "lane": lane,
        "attempt_id": attempt_id,
        "source_path": str(resolved),
        "source_bytes": resolved.stat().st_size,
        "source_sha256": digest,
        "source_schema": review.get("schema"),
        "classification": review.get("classification"),
        "decision": review.get("decision"),
        "failed": is_failed_review(review),
        "strategy_tags": sorted(set(strategy_tags)),
        "root_cause": review.get("root_cause")
        or review.get("repeated_failure_pattern", {}).get("conclusion"),
        "findings": findings,
        "ingested_at_utc": now_utc(),
    }
    memory["reviews"].append(record)
    memory["reviews"].sort(key=lambda item: (item["lane"], item["attempt_id"], item["source_sha256"]))
    return recompute(memory), True


def evaluate_strategy(memory: dict[str, Any], lane: str, strategy_tags: Iterable[str]) -> dict[str, Any]:
    validate_memory(memory)
    decision = memory.get("lanes", {}).get(lane)
    tags = set(strategy_tags)
    if not decision or decision.get("classification") != "PIVOT_REQUIRED":
        return {
            "pass": True,
            "classification": "STRATEGY_ALLOWED",
            "lane": lane,
            "missing_required_tags": [],
            "present_forbidden_tags": [],
        }
    required = set(decision.get("required_strategy_tags", []))
    forbidden = set(decision.get("forbidden_strategy_tags", []))
    missing = sorted(required - tags)
    present_forbidden = sorted(forbidden & tags)
    passed = not missing and not present_forbidden
    return {
        "pass": passed,
        "classification": "STRATEGY_ALLOWED_AFTER_PIVOT" if passed else "STRATEGY_BLOCKED_BY_VISUAL_FEEDBACK",
        "lane": lane,
        "missing_required_tags": missing,
        "present_forbidden_tags": present_forbidden,
        "repeated_categories": decision.get("repeated_categories", []),
        "next_work_requirements": decision.get("next_work_requirements", []),
    }


def load_memory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_memory()
    memory = load_json(path)
    validate_memory(memory)
    return memory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Skyguard visual-feedback memory controller.")
    parser.add_argument("--memory", type=Path, default=DEFAULT_MEMORY_PATH)
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Ingest one immutable structured visual review.")
    ingest.add_argument("--review", type=Path, required=True)
    ingest.add_argument("--lane", required=True)
    ingest.add_argument("--attempt-id", required=True)
    ingest.add_argument("--strategy-tag", action="append", default=[])
    ingest.add_argument("--dry-run", action="store_true")

    evaluate = subparsers.add_parser("evaluate", help="Show the durable decision for one lane.")
    evaluate.add_argument("--lane", required=True)

    guard = subparsers.add_parser("guard", help="Fail if a proposed strategy violates a durable pivot.")
    guard.add_argument("--lane", required=True)
    guard.add_argument("--strategy-tag", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        memory = load_memory(args.memory)
        if args.command == "ingest":
            memory, inserted = ingest_review(
                memory,
                args.review,
                args.lane,
                args.attempt_id,
                args.strategy_tag,
            )
            if not args.dry_run:
                atomic_write_json(args.memory, memory)
            print(json.dumps({"inserted": inserted, "memory": memory}, indent=2))
            return 0
        if args.command == "evaluate":
            print(json.dumps(memory.get("lanes", {}).get(args.lane, {"classification": "NO_EVIDENCE"}), indent=2))
            return 0
        result = evaluate_strategy(memory, args.lane, args.strategy_tag)
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 3
    except FeedbackError as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
