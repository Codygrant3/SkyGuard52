"""Corrected execution binding for the unexecuted Recovery12 visual proof.

The frozen implementation and original supervisor remain unchanged. This
wrapper changes only the governed review-map constant before delegating to the
single-attempt supervisor.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


SUPERVISOR = Path(
    r"D:\Skyguard52\Scripts\invoke_m01_grouped_topology_recovery12_visual_proof.py"
)
SPEC = importlib.util.spec_from_file_location("recovery12_visual", SUPERVISOR)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

MODULE.REVIEW_MAP = (
    "/Game/Skyguard/Candidates/Mission01/"
    "HeroGroupedTopology_008_Attempt03/Review/"
    "Lvl_M01_HeroGroupedTopology_008_Attempt03"
)

if __name__ == "__main__":
    raise SystemExit(MODULE.main())
