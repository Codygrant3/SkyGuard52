from __future__ import annotations

"""Recovery01 identity/camera binding for the frozen corridor postflight."""

import hashlib
import importlib.util
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\Workers\adjudicate_m01_coastal_corridor_correction06.py")
EXPECTED_SOURCE_SHA256 = "fdab30a50a117e11d48a9b4f75c47586c38765995a3c5105d4a9d4f62778b062"
FAILED_REVIEW = Path(
    r"D:\Skyguard52\Production\Attempts\m01-coastal-corridor-correction06\attempt_20260810T201523968795Z\visual_review.json"
)
EXPECTED_FAILED_REVIEW_SHA256 = "ae65758fdc4a400e5d8ae0fb5cf0f723cd2a26c5aad401f87ba904e32cdc762b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if not SOURCE.is_file() or sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Correction06 frozen postflight authority mismatch")
if not FAILED_REVIEW.is_file() or sha256(FAILED_REVIEW) != EXPECTED_FAILED_REVIEW_SHA256:
    raise RuntimeError("Correction06 failed visual-review authority mismatch")

spec = importlib.util.spec_from_file_location("_skyguard_m01_c06_postflight", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load frozen corridor postflight")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.ASSET_ID = "m01-coastal-corridor-correction06-recovery01"
module.EXPECTED_RENDER_NAMES = {
    "daylight_route_aerial.png",
    "daylight_shoreline_oblique.png",
    "daylight_promenade_furniture.png",
    "overcast_integrated_intersection.png",
    "daylight_urban_service_detail.png",
    "overcast_wet_contact_close.png",
}


if __name__ == "__main__":
    raise SystemExit(module.main())
