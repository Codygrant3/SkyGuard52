"""Offline Recovery11 audit. Never invokes UBT, Unreal, or Blender."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY11_COMPILE_FIX_CONTRACT.json"
REPORT = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY11_COMPILE_FIX_READINESS.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(name: str, passed: bool, detail: str) -> dict[str, object]:
    return {"name": name, "passed": bool(passed), "detail": detail}


def audit(write_report: bool = True) -> dict[str, object]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    bridge_path = ROOT / contract["correction"]["path"]
    rules_path = ROOT / "Source/Skyguard52/Skyguard52.Build.cs"
    source_path = ROOT / contract["frozen_inputs"]["recovery09_source"]["path"]
    header_path = ROOT / contract["frozen_inputs"]["recovery09_header"]["path"]
    recovery10_path = ROOT / contract["frozen_inputs"]["recovery10_bridge"]["path"]
    supervisor_path = ROOT / contract["execution"]["compile_supervisor"]

    bridge = bridge_path.read_text(encoding="utf-8-sig")
    rules = rules_path.read_text(encoding="utf-8-sig")
    source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
    checks = [
        check(
            "frozen_recovery09_header_exact",
            sha256_file(header_path) == contract["frozen_inputs"]["recovery09_header"]["sha256"],
            "Recovery09 header remains byte-identical",
        ),
        check(
            "frozen_recovery09_source_exact",
            sha256_file(source_path) == contract["frozen_inputs"]["recovery09_source"]["sha256"],
            "Recovery09 source remains byte-identical",
        ),
        check(
            "frozen_recovery10_bridge_exact",
            sha256_file(recovery10_path) == contract["frozen_inputs"]["recovery10_bridge"]["sha256"],
            "Recovery10 bridge remains byte-identical",
        ),
        check(
            "only_two_owned_copy_adapters",
            bridge.count("SkyguardRecovery11::OwnColors(Colors)") == 2
            and "SKYGUARD_RECOVERY11_BUILD_RECORD_699" in bridge
            and "SKYGUARD_RECOVERY11_WRITE_PNG_728" in bridge,
            "Only Recovery09 lines 699 and 728 receive owned-array temporaries",
        ),
        check(
            "target_lines_still_match",
            len(source_lines) >= 728
            and "BuildRecord(Width, Height, Colors)" in source_lines[698]
            and "WritePng(PendingPath, Width, Height, Colors)" in source_lines[727],
            "Frozen source call sites still occupy lines 699 and 728",
        ),
        check(
            "force_include_order_exact",
            rules.index("Recovery06CompileFix.h")
            < rules.index("Recovery08CompileFix.h")
            < rules.index("Recovery10CompileFix.h")
            < rules.index("Recovery11CompileFix.h"),
            "Recovery11 is force-included after the declaration bridge",
        ),
        check(
            "unexpected_sites_fail_closed",
            "An unexpected occurrence intentionally fails closed" in bridge
            and "#define BuildRecord(...)" in bridge
            and "#define WritePng(...)" in bridge,
            "Line-dispatch macros have no permissive default",
        ),
        check(
            "single_attempt_supervisor_present",
            supervisor_path.is_file()
            and "--authorize-single-recovery11-compile" in supervisor_path.read_text(encoding="utf-8-sig")
            and "RECOVERY11_COMPILE" in supervisor_path.read_text(encoding="utf-8-sig"),
            "Recovery11 compile has a distinct explicit-authority namespace",
        ),
    ]
    passed = all(item["passed"] for item in checks)
    report = {
        "schema": "skyguard.m01.recovery11.compile-readiness.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "gate": "PASS_RECOVERY11_COMPILE_READY_NOT_RUN" if passed else "FAIL_RECOVERY11_COMPILE_NOT_READY",
        "checks": checks,
        "native_build_executed": False,
        "unreal_launched": False,
        "promotion_allowed": False,
    }
    if write_report:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["gate"].startswith("PASS_") else 1)
