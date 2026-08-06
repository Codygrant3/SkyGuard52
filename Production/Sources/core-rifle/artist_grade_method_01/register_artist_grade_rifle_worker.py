from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
MANIFEST = ROOT / "Production" / "production_manifest.json"
EXPECTED_OLD_WORKER = r"Scripts\Workers\worker_core_rifle.py"
NEW_WORKER = r"Scripts\Workers\worker_core_rifle_artist_grade.py"


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = {asset["id"]: asset for asset in payload["assets"]}
    asset = assets["core-rifle"]
    if asset["status"] != "failed":
        raise RuntimeError(f"Expected core-rifle failed, found {asset['status']}")
    if asset["worker"]["script"] != EXPECTED_OLD_WORKER:
        raise RuntimeError(
            f"Original worker authority changed: {asset['worker']['script']}"
        )
    asset["worker"] = {
        "script": NEW_WORKER,
        "arguments": [
            "--output",
            "{output_dir}",
            "--asset-id",
            "core-rifle",
        ],
        "minimum_renders": 8,
    }
    asset["artist_grade_method"] = {
        "version": 1,
        "identity": "generic AR/M4-family rifle; exact configuration unresolved",
        "authorized_reason": (
            "Authorized artist-grade method replacement after Wave 01 terminal "
            "procedural rejection"
        ),
        "wave01_worker_immutable": EXPECTED_OLD_WORKER,
        "method": (
            "custom hard-surface high/low construction, packed UVs, high-to-low "
            "bakes, calibrated PBR, governed 2560x1440 review"
        ),
        "maximum_total_attempts": 3,
    }
    payload["project"]["updated_at_utc"] = (
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    MANIFEST.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
