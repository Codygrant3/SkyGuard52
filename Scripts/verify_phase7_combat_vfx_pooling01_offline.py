#!/usr/bin/env python3
"""Offline contract verifier for the bounded combat VFX pooling correction."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / "Source" / "Skyguard52"
CONTRACT = ROOT / "Docs" / "AAA_Review" / "PHASE7_COMBAT_VFX_POOLING01_CONTRACT.json"
PRECHANGE = ROOT / "Saved" / "Reports" / "PHASE7_COMBAT_VFX_POOLING01_PRECHANGE_INVENTORY.json"

FACADE_HEADER = SOURCE / "SkyguardCombatVFX.h"
FACADE_SOURCE = SOURCE / "SkyguardCombatVFX.cpp"
POOL_HEADER = SOURCE / "SkyguardCombatVFXPoolSubsystem.h"
POOL_SOURCE = SOURCE / "SkyguardCombatVFXPoolSubsystem.cpp"
AUTOMATION_TEST = SOURCE / "SkyguardCombatVFXTests.cpp"

PUBLIC_ENTRY_POINTS = (
    "SpawnMuzzleFlash",
    "SpawnGunSmoke",
    "SpawnHitSparks",
    "SpawnExplosion",
    "SpawnMissileTrail",
    "SpawnIglaLaunch",
    "SpawnTracer",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def function_body(source: str, qualified_name: str) -> str:
    match = re.search(rf"\b{re.escape(qualified_name)}\s*\([^)]*\)\s*\{{", source, re.DOTALL)
    if not match:
        raise ValueError(f"function not found: {qualified_name}")
    brace = source.find("{", match.start())
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1 : index]
    raise ValueError(f"unterminated function: {qualified_name}")


def require(checks: list[dict[str, object]], name: str, condition: bool, detail: object) -> None:
    checks.append({"name": name, "passed": bool(condition), "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    checks: list[dict[str, object]] = []
    required_files = (
        CONTRACT,
        PRECHANGE,
        FACADE_HEADER,
        FACADE_SOURCE,
        POOL_HEADER,
        POOL_SOURCE,
        AUTOMATION_TEST,
    )
    for path in required_files:
        require(checks, f"file_exists:{path.name}", path.is_file(), str(path))

    if not all(path.is_file() for path in required_files):
        report = {
            "schema": "skyguard.phase7.combat-vfx-pooling01.offline-validation.v1",
            "classification": "FAILED_WITH_EVIDENCE",
            "checks": checks,
        }
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 1

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    prechange = json.loads(PRECHANGE.read_text(encoding="utf-8"))
    facade_h = FACADE_HEADER.read_text(encoding="utf-8")
    facade_cpp = FACADE_SOURCE.read_text(encoding="utf-8")
    pool_h = POOL_HEADER.read_text(encoding="utf-8")
    pool_cpp = POOL_SOURCE.read_text(encoding="utf-8")
    test_cpp = AUTOMATION_TEST.read_text(encoding="utf-8")

    require(
        checks,
        "contract_capacity_192",
        contract["required_invariants"]["pool_capacity"] == 192,
        contract["required_invariants"]["pool_capacity"],
    )
    require(
        checks,
        "source_capacity_192",
        "static constexpr int32 PoolCapacity = 192;" in pool_h,
        "fixed compile-time capacity",
    )

    for entry_point in PUBLIC_ENTRY_POINTS:
        declaration_count = len(re.findall(rf"static void\s+{entry_point}\s*\(", facade_h))
        definition_count = len(re.findall(rf"USkyguardCombatVFX::{entry_point}\s*\(", facade_cpp))
        require(
            checks,
            f"public_facade_preserved:{entry_point}",
            declaration_count == 1 and definition_count == 1,
            {"declarations": declaration_count, "definitions": definition_count},
        )

    forbidden_facade_tokens = ("LoadObject<", "SpawnActor<", "SpawnActor(", "NewObject<")
    for token in forbidden_facade_tokens:
        require(
            checks,
            f"facade_forbids:{token}",
            token not in facade_cpp,
            facade_cpp.count(token),
        )

    prewarm_body = function_body(pool_cpp, "USkyguardCombatVFXPoolSubsystem::PrewarmAssets")
    allocate_body = function_body(pool_cpp, "USkyguardCombatVFXPoolSubsystem::AllocatePool")
    emit_body = function_body(pool_cpp, "USkyguardCombatVFXPoolSubsystem::EmitMesh")
    acquire_body = function_body(pool_cpp, "USkyguardCombatVFXPoolSubsystem::AcquireSlot")
    deinitialize_body = function_body(pool_cpp, "USkyguardCombatVFXPoolSubsystem::Deinitialize")

    require(
        checks,
        "asset_loads_confined_to_prewarm",
        pool_cpp.count("LoadObject<") == prewarm_body.count("LoadObject<")
        and pool_cpp.count("LoadObject<") > 0,
        {"total": pool_cpp.count("LoadObject<"), "prewarm": prewarm_body.count("LoadObject<")},
    )
    require(
        checks,
        "component_allocation_confined_to_initialize",
        pool_cpp.count("NewObject<UStaticMeshComponent>") == 1
        and allocate_body.count("NewObject<UStaticMeshComponent>") == 1,
        pool_cpp.count("NewObject<UStaticMeshComponent>"),
    )
    require(
        checks,
        "emit_has_no_growth_or_loading",
        all(token not in emit_body for token in ("AllocatePool", "NewObject", "LoadObject", "SpawnActor", ".Add(")),
        "combat emission recycles prepared slots only",
    )
    require(
        checks,
        "earliest_expiry_recycling",
        "EarliestExpiry" in acquire_body
        and "ReleaseSlot(EarliestSlot)" in acquire_body
        and "++RecycleCount" in acquire_body,
        "earliest active slot is reused",
    )
    require(
        checks,
        "collision_disabled",
        "SetCollisionEnabled(ECollisionEnabled::NoCollision)" in allocate_body,
        "pool components are non-colliding",
    )
    require(
        checks,
        "world_lifetime_cleanup",
        "DestroyComponent()" in deinitialize_body
        and "Components.Reset()" in deinitialize_body,
        "components destroyed during subsystem deinitialization",
    )
    require(
        checks,
        "pool_is_initialized_once",
        pool_cpp.count("AllocatePool();") == 1
        and "AllocatePool();" in function_body(pool_cpp, "USkyguardCombatVFXPoolSubsystem::Initialize"),
        pool_cpp.count("AllocatePool();"),
    )

    unchanged_authorities: list[dict[str, object]] = []
    mutable_names = {"SkyguardCombatVFX.cpp", "SkyguardCombatVFX.h"}
    for record in prechange["records"]:
        path = Path(record["path"])
        if path.name in mutable_names:
            continue
        actual = sha256(path) if path.is_file() else None
        matched = actual == record["sha256"]
        unchanged_authorities.append(
            {"path": str(path), "expected": record["sha256"], "actual": actual, "matched": matched}
        )
    require(
        checks,
        "unrelated_authorities_unchanged",
        all(record["matched"] for record in unchanged_authorities),
        unchanged_authorities,
    )

    call_sites: dict[str, int] = {}
    for entry_point in PUBLIC_ENTRY_POINTS:
        total = 0
        needle = f"USkyguardCombatVFX::{entry_point}("
        for path in SOURCE.glob("*.cpp"):
            if path in {FACADE_SOURCE, AUTOMATION_TEST}:
                continue
            total += path.read_text(encoding="utf-8", errors="replace").count(needle)
        call_sites[entry_point] = total
    require(
        checks,
        "gameplay_callers_remain_connected",
        sum(call_sites.values()) > 0
        and call_sites["SpawnExplosion"] > 0
        and call_sites["SpawnMuzzleFlash"] > 0
        and call_sites["SpawnIglaLaunch"] > 0,
        call_sites,
    )

    test_requirements = (
        "GetAllocatedCount()",
        "GetRecycleCount()",
        "CountActors(World)",
        "SpawnMuzzleFlash",
        "SpawnExplosion",
        "SpawnIglaLaunch",
        "PoolCapacity",
    )
    require(
        checks,
        "automation_test_covers_pool_and_actor_invariants",
        all(token in test_cpp for token in test_requirements),
        list(test_requirements),
    )

    failures = [check for check in checks if not check["passed"]]
    report = {
        "schema": "skyguard.phase7.combat-vfx-pooling01.offline-validation.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "PASSED_READY_FOR_EXPLICIT_SINGLE_NATIVE_BUILD_AUTHORIZATION"
        if not failures
        else "FAILED_WITH_EVIDENCE",
        "heavy_processes_launched": 0,
        "checks_passed": len(checks) - len(failures),
        "checks_total": len(checks),
        "checks": checks,
        "artifacts": [
            {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in required_files
        ],
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
