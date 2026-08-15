"""Fresh-namespace wrapper around the proven one-shot Unreal supervisor."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
BASE = ROOT / "Scripts/GrokProduction/invoke_core_igla_missile_refinement01_unreal_integration01_once.py"
SPEC = importlib.util.spec_from_file_location("igla_unreal_supervisor_base", BASE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load supervisor base: {BASE}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

MODULE.AUTHOR = ROOT / "Scripts/GrokProduction/author_core_igla_missile_refinement01_unreal_integration01_recovery01.py"
MODULE.DESTINATION = Path(r"D:\SG52T08_ENV01\Content\Skyguard\Combat\Weapons\IglaMissileRefinement01Recovery01")
MODULE.OUTPUT_MAP = MODULE.DESTINATION / "Lvl_CORE_IglaMissile_Refinement01_Recovery01_ImportAudit.umap"
MODULE.ATTEMPT = ROOT / "Saved/BuildAttempts/CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01_RECOVERY01/attempt_01"
MODULE.RECEIPT = MODULE.ATTEMPT / "integration_receipt.json"
MODULE.TERMINAL = ROOT / "Saved/Reports/CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01_RECOVERY01_TERMINAL_SUPERVISOR.json"

raise SystemExit(MODULE.main())
