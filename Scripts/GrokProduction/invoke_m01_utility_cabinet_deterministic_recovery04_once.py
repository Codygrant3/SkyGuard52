from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
BASE = PROJECT / "Scripts" / "GrokProduction" / "invoke_m01_utility_cabinet_deterministic_recovery02_once.py"
SCRIPT = PROJECT / "Scripts" / "GrokProduction" / "recover_m01_utility_cabinet_recovery04_scene.py"
PRIOR_FREEZE = PROJECT / "Docs" / "AAA_Review" / "M01_UTILITY_CABINET_DETERMINISTIC_RECOVERY03_ATTEMPT01_TERMINAL_FREEZE.json"
ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-utility-cabinet-deterministic-recovery04" / "attempt_20260811T095000000000Z"


def load_base():
    spec = importlib.util.spec_from_file_location("skyguard_utility_cabinet_recovery02_supervisor_authority", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load supervisor authority: {BASE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_base()
    module.PRIOR_FREEZE = PRIOR_FREEZE
    module.PRIOR_FREEZE_BYTES = 1245
    module.PRIOR_FREEZE_SHA = "f1259d1d7dda13fd91a11dfa6de371e543beb87231b2e8604bebad9ba0b43159"
    module.SCRIPT = SCRIPT
    module.ATTEMPT = ATTEMPT
    module.OUTPUT = ATTEMPT / "output"
    module.TERMINAL = ATTEMPT / "terminal_manifest.json"
    module.STDOUT = ATTEMPT / "blender_stdout.log"
    module.STDERR = ATTEMPT / "blender_stderr.log"
    module.PROCESS_SAMPLES = ATTEMPT / "process_tree_samples.jsonl"
    module.EXPECTED_BLEND = module.OUTPUT / "M01_Promenade_UtilityCabinet_Recovery04.blend"
    module.EXPECTED_GLB = module.OUTPUT / "exports" / "M01_Promenade_UtilityCabinet_Recovery04.glb"
    module.EXPECTED_REPORT = module.OUTPUT / "implementation_report.json"
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
