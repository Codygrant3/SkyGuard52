from __future__ import annotations

import importlib.util
import json
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
BASE_SUPERVISOR = PROJECT / "Scripts/GrokProduction/invoke_m01_promenade_prop_kit_grok_mcp_attempt01_once.py"
SOURCE = PROJECT / "Blender/GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01/GATE7_COMBAT_BLOCKOUT_CYCLE02_RECOVERY03_ATTEMPT01.blend"
SOURCE_BYTES = 205836
SOURCE_SHA = "a9a05718c3359392d3dc0d994b9cafb0b3ac5873f17a904e15a8c4ffe8e7239d"
PROMPT = PROJECT / "Production/Prompts/CORE_SHAHED136_GROK_MCP_ARTIST_GRADE_REDESIGN01.md"
FINALIZER = PROJECT / "Scripts/GrokProduction/finalize_core_shahed136_artist_grade_redesign01_scene.py"
ATTEMPT = PROJECT / "Production/Attempts/core-shahed136-grok-mcp-redesign01/attempt_20260811T0830000000000Z"


def load_base():
    spec = importlib.util.spec_from_file_location("skyguard_core_shahed136_artist_grade_redesign01_base", BASE_SUPERVISOR)
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
    module.EXPECTED_BLEND = module.OUTPUT / "CORE_Shahed136_ArtistGrade_Redesign01.blend"
    module.EXPECTED_GLB = module.OUTPUT / "exports/CORE_Shahed136_ArtistGrade_Redesign01.glb"
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
    value["schema"] = "skyguard.core-shahed136.grok-mcp.artist-grade-redesign01.terminal.v1"
    value["asset"] = "Shahed-136 provisional artist-grade exterior source"
    value["representation_boundary"] = "Only 3.300 m overall length and 3.000 m wingspan are authoritative; remaining visible construction is provisional"
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
