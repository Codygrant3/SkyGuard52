from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path


PROJECT = Path(r"D:\Skyguard52")
BASE_SUPERVISOR = PROJECT / "Scripts" / "GrokProduction" / "invoke_m01_promenade_prop_kit_grok_mcp_attempt01_once.py"
SOURCE = PROJECT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01" / "Coastal_Production_001" / "BLD_M01_COAST_PROD_001_MASTER.blend"
SOURCE_BYTES = 201_985
SOURCE_SHA = "4cb6bc2acc06310c4328687d65c808db6adfe5b1c5e49774a81bec60bf4a08cb"
PROMPT = PROJECT / "Production" / "Prompts" / "M01_STORM_DRAIN_GROK_MCP_RECOVERY01.md"
FINALIZER = PROJECT / "Scripts" / "GrokProduction" / "finalize_m01_storm_drain_recovery01_scene.py"
ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-storm-drain-grok-mcp-recovery01" / "attempt_20260811T101500000000Z"
BASE_SUPERVISOR_BYTES = 17_814
BASE_SUPERVISOR_SHA256 = "c770cad25e3ced45eb2ae0baae7d242d246a19a235f522a82d9f00f55a11bc75"
PROMPT_BYTES = 4_901
PROMPT_SHA256 = "7cca83a39ae9b79388401985dd5dbc948575a64153217da1780e1c1914ffc119"
FINALIZER_BYTES = 11_849
FINALIZER_SHA256 = "3dcf1f8cd3f7ddc0c7b1ca79319e4b341c411cabf3209fea402913e8afc37cf7"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_authority(path: Path, size: int, digest: str) -> None:
    if not path.is_file() or path.stat().st_size != size or sha256(path) != digest:
        raise RuntimeError(f"Frozen Grok storm-drain authority changed: {path}")


def load_base():
    spec = importlib.util.spec_from_file_location("skyguard_storm_drain_recovery01_base", BASE_SUPERVISOR)
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
    module.EXPECTED_BLEND = module.OUTPUT / "M01_Promenade_StormDrain_Recovery01.blend"
    module.EXPECTED_GLB = module.OUTPUT / "exports" / "M01_Promenade_StormDrain_Recovery01.glb"
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
    value["schema"] = "skyguard.m01-storm-drain.grok-mcp.recovery01.terminal.v1"
    value["asset"] = "M01 promenade storm drain"
    value["base_supervisor_authority"] = module.file_record(BASE_SUPERVISOR)
    module.write_json(module.TERMINAL, value)


def main() -> int:
    require_authority(BASE_SUPERVISOR, BASE_SUPERVISOR_BYTES, BASE_SUPERVISOR_SHA256)
    require_authority(PROMPT, PROMPT_BYTES, PROMPT_SHA256)
    require_authority(FINALIZER, FINALIZER_BYTES, FINALIZER_SHA256)
    module = load_base()
    configure(module)
    result = module.main()
    normalize_terminal(module)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
