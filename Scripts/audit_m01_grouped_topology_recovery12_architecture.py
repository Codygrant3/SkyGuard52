"""Offline Recovery12 architecture audit; never launches Unreal or Blender."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / "Source"
MODULE = SOURCE / "Skyguard52"
CONTRACT = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY12_ARCHITECTURE_CONTRACT.json"
QUARANTINE = ROOT / "Saved/Quarantine/Phase3FailedCaptureSources/Recovery12Retirement"
INVENTORY = ROOT / "Saved/Reports/M01_GROUPED_TOPOLOGY_RECOVERY12_SOURCE_INVENTORY.json"
READINESS = ROOT / "Saved/Reports/M01_GROUPED_TOPOLOGY_RECOVERY12_READINESS.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory() -> dict[str, object]:
    files = []
    for path in sorted(item for item in SOURCE.rglob("*") if item.is_file()):
        files.append({
            "file": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    return {
        "schema": "skyguard.m01.grouped-topology.recovery12-source-inventory.v1",
        "files": files,
    }


def add(checks: list[dict[str, object]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def audit(write_outputs: bool = True) -> dict[str, object]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    manifest = json.loads((QUARANTINE / "MANIFEST.json").read_text(encoding="utf-8"))
    header = MODULE / "SkyguardM01GroupedTopologyRecovery12Capture.h"
    source = MODULE / "SkyguardM01GroupedTopologyRecovery12Capture.cpp"
    rules = MODULE / "Skyguard52.Build.cs"
    header_text = header.read_text(encoding="utf-8-sig")
    source_text = source.read_text(encoding="utf-8-sig")
    rules_text = rules.read_text(encoding="utf-8-sig")
    checks: list[dict[str, object]] = []

    retired_ok = True
    for record in manifest["files"]:
        path = QUARANTINE / record["file"]
        retired_ok &= (
            path.is_file()
            and path.stat().st_size == record["bytes"]
            and sha256(path) == record["sha256"]
        )
    add(checks, "quarantine_hashes_exact", retired_ok, "All 11 retired files remain byte-exact")

    obsolete_active = [
        path.name
        for path in MODULE.glob("SkyguardM01GroupedTopologyRecovery*")
        if any(token in path.name for token in ("Recovery05", "Recovery06", "Recovery07", "Recovery08", "Recovery09", "Recovery10", "Recovery11"))
    ]
    add(checks, "obsolete_capture_sources_inactive", not obsolete_active, str(obsolete_active))
    add(checks, "force_include_removed", "ForceIncludeFiles" not in rules_text, "Module rules contain no force includes")

    forbidden = (
        "#define BuildRecord",
        "#define WritePng",
        "#define Colors",
        "#define TArray",
        "#define TArrayView",
        "__LINE__",
    )
    combined = header_text + source_text
    add(checks, "no_forbidden_macros", not any(token in combined for token in forbidden), "Recovery12 has no line or name rewriting macros")
    add(
        checks,
        "type_contract_consistent",
        header_text.count("TArrayView64<const FColor> Colors") == 3
        and source_text.count("const TArrayView64<const FColor> Colors") == 3
        and "const TArray<FColor>& Colors) const" not in source_text,
        "Header and source consistently use UE 5.8 color views",
    )
    add(
        checks,
        "png_api_uses_view_directly",
        "FImageUtils::PNGCompressImageArray(" in source_text
        and "SkyguardRecovery12::OwnColors" not in source_text,
        "PNG compression receives the view without an owned-copy bridge",
    )
    add(
        checks,
        "recovery12_identity_exact",
        "USkyguardM01GroupedTopologyRecovery12Capture" in header_text
        and "SkyguardM01Recovery12ContractId=" in source_text
        and "M01-HERO-GROUPED-TOPOLOGY-ATTEMPT03-RECOVERY12" in source_text
        and "Recovery09" not in combined,
        "Class, CLI, contract, logs, and receipts are Recovery12-only",
    )
    add(
        checks,
        "format_argument_is_type_correct",
        "*LexToString(GMaxRHIFeatureLevel));" in source_text,
        "The FString::Printf percent-s argument is explicitly dereferenced",
    )
    add(
        checks,
        "single_attempt_tools_present",
        (ROOT / contract["compile"]["supervisor"]).is_file()
        and (ROOT / contract["visual_proof"]["supervisor"]).is_file(),
        "Distinct compile and visual-proof supervisors exist",
    )

    current_inventory = inventory()
    passed = all(item["passed"] for item in checks)
    result = {
        "schema": "skyguard.m01.grouped-topology.recovery12-readiness.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "gate": "PASS_RECOVERY12_ARCHITECTURE_READY_NOT_RUN" if passed else "FAIL_RECOVERY12_ARCHITECTURE_NOT_READY",
        "checks": checks,
        "source_inventory_sha256": hashlib.sha256((json.dumps(current_inventory, indent=2, sort_keys=True) + "\n").encode()).hexdigest(),
        "compile_executed": False,
        "unreal_launched": False,
        "promotion_allowed": False,
    }
    if write_outputs:
        INVENTORY.parent.mkdir(parents=True, exist_ok=True)
        INVENTORY.write_text(json.dumps(current_inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        READINESS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["gate"].startswith("PASS_") else 1)
