"""Recovery01 for the UE 5.8 Rotator API mismatch in the v2 author pass."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
BASE_PATH = (
    ROOT
    / r"Scripts\GrokProduction"
    / "author_m01_accepted_module_assembly_v2_remediation01.py"
)
ATTEMPT = (
    ROOT
    / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_V2_REMEDIATION01_RECOVERY01"
    / "attempt_01"
)

spec = importlib.util.spec_from_file_location(
    "m01_assembly_v2_remediation01_authority",
    BASE_PATH,
)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load author authority: {BASE_PATH}")
authority = importlib.util.module_from_spec(spec)
spec.loader.exec_module(authority)
authority.ATTEMPT = ATTEMPT
authority.RECEIPT = ATTEMPT / "author_receipt.json"
authority.ALLOW_EXISTING_TARGET = True
authority.main()
