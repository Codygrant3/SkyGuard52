from __future__ import annotations

import importlib.util
import json
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
BASE_SUPERVISOR = PROJECT / "Scripts" / "GrokProduction" / "invoke_m01_promenade_prop_kit_grok_mcp_attempt01_once.py"
SOURCE = PROJECT / "Production" / "Attempts" / "m01-street-detail-kit-finalizer-recovery01" / "attempt_20260811T071500000000Z" / "output" / "M01_StreetDetailKit_GrokMCP_Production_A.blend"
SOURCE_BYTES = 494714
SOURCE_SHA = "cf0d2b275d1299e686fb1e772e6d35db0ae099b3a255661061427679ef8c0bba"
PROMPT = PROJECT / "Production" / "Prompts" / "M01_BICYCLE_RACK_GROK_MCP_RECOVERY02.md"
FINALIZER = PROJECT / "Scripts" / "GrokProduction" / "finalize_m01_bicycle_rack_recovery02_scene.py"
ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-bicycle-rack-grok-mcp-recovery02" / "attempt_20260811T073000000000Z"


def load_base():
    spec = importlib.util.spec_from_file_location("skyguard_bicycle_rack_recovery02_base", BASE_SUPERVISOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load frozen base supervisor: {BASE_SUPERVISOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configure(module) -> None:
    module.SOURCE = SOURCE
    module.SOURCE_BYTES = SOURCE_BYTES
    module.SOURCE_SHA = SOURCE_SHA
    module.PROMPT = PROMPT
    module.FINALIZER = FINALIZER
    module.ATTEMPT = ATTEMPT
    module.OUTPUT = ATTEMPT / "output"
    module.TERMINAL = ATTEMPT / "terminal_manifest.json"
    module.EXPECTED_BLEND = module.OUTPUT / "M01_Promenade_BicycleRack_Recovery02.blend"
    module.EXPECTED_GLB = module.OUTPUT / "exports" / "M01_Promenade_BicycleRack_Recovery02.glb"
    module.EXPECTED_REPORT = module.OUTPUT / "grok_implementation_report.json"
    module.EVENTS = ATTEMPT / "grok_events.jsonl"
    module.GROK_STDERR = ATTEMPT / "grok_stderr.log"
    module.GROK_FINAL = ATTEMPT / "grok_final.md"
    module.GROK_EXIT = ATTEMPT / "grok_process_exit.json"
    module.BLENDER_STDOUT = ATTEMPT / "blender_stdout.log"
    module.BLENDER_STDERR = ATTEMPT / "blender_stderr.log"
    module.FINALIZER_STDOUT = ATTEMPT / "finalizer_stdout.log"
    module.FINALIZER_STDERR = ATTEMPT / "finalizer_stderr.log"
    module.PROCESS_SAMPLES = ATTEMPT / "process_tree_samples.jsonl"
    module.__file__ = __file__


def normalize_terminal(module) -> None:
    if not module.TERMINAL.is_file():
        return
    value = json.loads(module.TERMINAL.read_text(encoding="utf-8"))
    value["schema"] = "skyguard.m01-bicycle-rack.grok-mcp.recovery02.terminal.v1"
    value["asset"] = "M01 promenade bicycle rack"
    value["base_supervisor_authority"] = module.file_record(BASE_SUPERVISOR)
    module.write_json(module.TERMINAL, value)


def main() -> int:
    module = load_base()
    configure(module)
    result = module.main()
    normalize_terminal(module)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
