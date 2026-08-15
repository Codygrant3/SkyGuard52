"""Recovery01 visual proof after the single bounded assembly correction."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
BASE_PATH = (
    ROOT
    / r"Scripts\GrokProduction"
    / "capture_m01_accepted_module_assembly_v1_integration_gate01.py"
)
ATTEMPT = (
    ROOT
    / r"Saved\BuildAttempts\M01_ACCEPTED_MODULE_ASSEMBLY_V1_INTEGRATION_GATE01_RECOVERY01"
    / "attempt_01"
)

spec = importlib.util.spec_from_file_location("m01_assembly_gate01_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load capture authority: {BASE_PATH}")
authority = importlib.util.module_from_spec(spec)
spec.loader.exec_module(authority)

authority.ATTEMPT = ATTEMPT
authority.PROOF = ATTEMPT / "proof"
authority.RECEIPT = ATTEMPT / "integration_gate_receipt.json"
authority.CAMERAS = (
    {
        "id": "assembly_aerial",
        "location": (4000.0, -17000.0, 7200.0),
        "target": (2500.0, -5000.0, 100.0),
        "fov": 58.0,
    },
    {
        "id": "facade_coastal_front",
        "location": (0.0, -6500.0, 700.0),
        "target": (0.0, -3300.0, 260.0),
        "fov": 46.0,
    },
    {
        "id": "facade_coastal_reverse",
        "location": (0.0, -300.0, 700.0),
        "target": (0.0, -3300.0, 260.0),
        "fov": 46.0,
    },
    {
        "id": "shoreline_contact_oblique",
        "location": (5200.0, -7800.0, 1700.0),
        "target": (1400.0, -3400.0, 100.0),
        "fov": 52.0,
    },
)

authority.main()
