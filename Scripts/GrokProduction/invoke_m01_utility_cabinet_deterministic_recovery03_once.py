from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
BASE = PROJECT / "Scripts" / "GrokProduction" / "invoke_m01_utility_cabinet_deterministic_recovery02_once.py"
SCRIPT = PROJECT / "Scripts" / "GrokProduction" / "recover_m01_utility_cabinet_recovery03_scene.py"
PRIOR_FREEZE = PROJECT / "Docs" / "AAA_Review" / "M01_UTILITY_CABINET_DETERMINISTIC_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json"
ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-utility-cabinet-deterministic-recovery03" / "attempt_20260811T094000000000Z"


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
    module.PRIOR_FREEZE_BYTES = 1351
    module.PRIOR_FREEZE_SHA = "622c77f0b33cc88ff4c2305844f498d06ce21116c9eee6019df94a4440169611"
    module.SCRIPT = SCRIPT
    module.ATTEMPT = ATTEMPT
    module.OUTPUT = ATTEMPT / "output"
    module.TERMINAL = ATTEMPT / "terminal_manifest.json"
    module.STDOUT = ATTEMPT / "blender_stdout.log"
    module.STDERR = ATTEMPT / "blender_stderr.log"
    module.PROCESS_SAMPLES = ATTEMPT / "process_tree_samples.jsonl"
    module.EXPECTED_BLEND = module.OUTPUT / "M01_Promenade_UtilityCabinet_Recovery03.blend"
    module.EXPECTED_GLB = module.OUTPUT / "exports" / "M01_Promenade_UtilityCabinet_Recovery03.glb"
    module.EXPECTED_REPORT = module.OUTPUT / "implementation_report.json"
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
