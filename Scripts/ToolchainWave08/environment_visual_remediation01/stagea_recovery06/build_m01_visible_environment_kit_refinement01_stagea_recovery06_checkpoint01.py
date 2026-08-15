from __future__ import annotations

import ast
import builtins
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01"
RECOVERY05_WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery05\build_m01_visible_environment_kit_refinement01_stagea_recovery05_checkpoint01.py"
RECOVERY05_WORKER_BYTES = 79498
RECOVERY05_WORKER_SHA256 = "11c87230cfd1464bc83fea7b4b7d14efe4341be5f1adeb0512116e5e0a3aaa95"
RECOVERY05_GATE_TOKEN = 'GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01"'
RECOVERY06_GATE_TOKEN = f'GATE = "{GATE}"'


SIDE_WINDOW_HELPER = r'''
def add_side_window(
    prefix: str,
    x: float,
    y: float,
    z: float,
    right_side: bool,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
) -> list[bpy.types.Object]:
    sign = 1.0 if right_side else -1.0
    occupancy = ("window_dark", "window_warm", "window_dark", "window_cool")[(int(abs(y) * 3) + int(z * 5)) % 4]
    result = [
        add_box(prefix + "_Reveal", (x - sign * 0.02, y, z), (0.20, 2.05, 2.02), materials["concrete_dark"], target, 0.025),
        add_box(prefix + "_Interior", (x - sign * 0.13, y, z), (0.025, 1.58, 1.56), materials[occupancy], target, 0.01),
        add_box(prefix + "_Glass", (x + sign * 0.11, y, z), (0.055, 1.72, 1.70), materials["glass"], target, 0.018),
        add_box(prefix + "_FrameTop", (x + sign * 0.21, y, z + 0.92), (0.13, 2.02, 0.105), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameBottom", (x + sign * 0.21, y, z - 0.92), (0.13, 2.02, 0.105), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameA", (x + sign * 0.21, y - 0.96, z), (0.13, 0.105, 1.84), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameB", (x + sign * 0.21, y + 0.96, z), (0.13, 0.105, 1.84), materials["metal"], target, 0.018),
        add_box(prefix + "_Mullion", (x + sign * 0.23, y, z), (0.14, 0.065, 1.70), materials["metal"], target, 0.012),
        add_box(prefix + "_Drip", (x + sign * 0.31, y, z + 1.06), (0.20, 2.20, 0.10), materials["concrete"], target, 0.022),
    ]
    return result
'''.strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_recovery05_module():
    if not RECOVERY05_WORKER.is_file():
        raise RuntimeError(f"Frozen Recovery05 worker is missing: {RECOVERY05_WORKER}")
    if RECOVERY05_WORKER.stat().st_size != RECOVERY05_WORKER_BYTES:
        raise RuntimeError("Frozen Recovery05 worker byte count changed")
    digest = sha256_file(RECOVERY05_WORKER)
    if digest != RECOVERY05_WORKER_SHA256:
        raise RuntimeError(f"Frozen Recovery05 worker hash changed: {digest}")
    spec = importlib.util.spec_from_file_location("skyguard_recovery05_frozen_worker", RECOVERY05_WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not create a module specification for the frozen Recovery05 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def static_named_call_graph(source: str) -> dict[str, object]:
    tree = ast.parse(source)
    definitions = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    imports: set[str] = set()
    assigned: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned.add(node.target.id)
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    allowed = set(dir(builtins)) | definitions | imports | assigned
    unresolved = sorted(called - allowed)
    return {
        "function_and_class_definition_count": len(definitions),
        "named_call_count": len(called),
        "unresolved_named_calls": unresolved,
        "passed": not unresolved,
    }


def load_recovery06_source() -> tuple[str, dict[str, object]]:
    module = load_recovery05_module()
    source, recovery05_receipt = module.load_recovery05_source()
    if source.count(RECOVERY05_GATE_TOKEN) != 1:
        raise RuntimeError("Generated Recovery05 gate token cardinality is not one")
    source = source.replace(RECOVERY05_GATE_TOKEN, RECOVERY06_GATE_TOKEN, 1)
    if "def add_side_window(" in source:
        raise RuntimeError("Generated Recovery05 source unexpectedly already defines add_side_window")
    insertion_token = "\ndef add_balcony("
    if source.count(insertion_token) != 1:
        raise RuntimeError("add_balcony insertion token cardinality is not one")
    source = source.replace(insertion_token, "\n" + SIDE_WINDOW_HELPER + "\n\ndef add_balcony(", 1)
    graph = static_named_call_graph(source)
    if not graph["passed"]:
        raise RuntimeError(f"Generated Recovery06 source has unresolved named calls: {graph['unresolved_named_calls']}")
    required = (
        RECOVERY06_GATE_TOKEN,
        "def add_side_window(",
        'require(len(results) == 9, "Checkpoint render count is not exactly nine")',
        '"status":"CHECKPOINT_COMPLETED_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW"',
        '"finalization_authorized":False',
    )
    for token in required:
        if token not in source:
            raise RuntimeError(f"Required Recovery06 token is absent: {token}")
    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery06-checkpoint01.in-memory-correction.v1",
        "gate": GATE,
        "recovery05_worker": str(RECOVERY05_WORKER),
        "recovery05_worker_bytes": RECOVERY05_WORKER_BYTES,
        "recovery05_worker_sha256": RECOVERY05_WORKER_SHA256,
        "recovery05_design_receipt": recovery05_receipt,
        "bounded_correction": "ADD_MISSING_SIDE_WINDOW_HELPER",
        "generated_call_graph": graph,
        "recovery05_attempt_or_output_reused": False,
        "checkpoint_only": True,
        "checkpoint_count": 9,
        "final_render_count": 0,
        "texture_count": 0,
        "glb_count": 0,
        "finalization_authorized": False,
        "passed": True,
    }
    return source, receipt


def main() -> int:
    corrected, receipt = load_recovery06_source()
    print(json.dumps(receipt, sort_keys=True))
    namespace: dict[str, object] = {
        "__name__": "skyguard_stagea_recovery06_checkpoint01_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(corrected, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Recovery06 checkpoint embedded main is unavailable")
    return int(embedded_main())


if __name__ == "__main__":
    raise SystemExit(main())
