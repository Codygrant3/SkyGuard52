"""Fail-closed attempt05 visible/GPU verifier entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import verify_skyguard_phase4_m01_landscape_visible_gpu_gate as verifier
from phase4_m01_landscape_repair_contract import load_attempt05_contract


def main() -> int:
    verifier.load_effective_contract = load_attempt05_contract
    return verifier.main()


if __name__ == "__main__":
    raise SystemExit(main())
