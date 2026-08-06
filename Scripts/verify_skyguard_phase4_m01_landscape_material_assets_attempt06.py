"""Fresh-process immutable Attempt06 editor acceptance entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import verify_skyguard_phase4_m01_landscape_material_assets as verifier
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract


REPORT_PATH = (
    ROOT
    / "Saved/Reports"
    / "PHASE4_M01_LANDSCAPE_MATERIAL_EDITOR_ACCEPTANCE_ATTEMPT06.json"
)


def main() -> None:
    verifier.REPORT_PATH = REPORT_PATH
    verifier.load_effective_contract = load_attempt06_contract
    verifier.main()


if __name__ == "__main__":
    main()
