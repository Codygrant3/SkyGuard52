"""Normal-editor D3D12 Attempt06 capture entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import capture_skyguard_phase4_m01_landscape_visible_review as capture
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract


def main() -> None:
    capture.load_effective_contract = load_attempt06_contract
    capture.main()


if __name__ == "__main__":
    main()
