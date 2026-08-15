"""Recovery01 handshake correction for the frozen mapped-preview executor."""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\author_and_capture_m01_window_recovery06_unrealready01_mapped_preview01.py")
BASE_SHA256 = "bf114b348475ff29bee80c7ec7c15e1c0d73a567422a38690639cb9df25ea893"
FAILED_FREEZE = Path(r"D:\Skyguard52\Docs\AAA_Review\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_ATTEMPT01_TERMINAL_FREEZE.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen mapped-preview Attempt01 executor changed")
if not FAILED_FREEZE.is_file():
    raise RuntimeError("Mapped-preview Attempt01 failure freeze is absent")

source = BASE.read_text(encoding="utf-8")
source = source.replace(
    'MAP_ASSET = "/Game/T08/GW02Preview/Lvl_GW02_WindowPreview01"',
    'MAP_ASSET = "/Game/T08/GW02PreviewR01/Lvl_GW02_WindowPreview01_Recovery01"',
)
source = source.replace(
    'MAP_FILE = ISOLATED / r"Content\\T08\\GW02Preview\\Lvl_GW02_WindowPreview01.umap"',
    'MAP_FILE = ISOLATED / r"Content\\T08\\GW02PreviewR01\\Lvl_GW02_WindowPreview01_Recovery01.umap"',
)
source = source.replace(
    'ATTEMPT = ROOT / r"Saved\\BuildAttempts\\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01\\attempt_01"',
    'ATTEMPT = ROOT / r"Saved\\BuildAttempts\\M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY01\\attempt_01"',
)
old_handshake = '''    if ATTEMPT.exists() and any(ATTEMPT.iterdir()):\n        raise RuntimeError("Fresh mapped-preview attempt is not empty")'''
new_handshake = '''    allowed_launcher_files = {"unreal.stdout.log", "unreal.stderr.log", "unreal.engine.log", "process_tree_samples.jsonl"}\n    unexpected_launcher_files = []\n    if ATTEMPT.exists():\n        unexpected_launcher_files = sorted(path.name for path in ATTEMPT.iterdir() if path.name not in allowed_launcher_files)\n    if unexpected_launcher_files:\n        raise RuntimeError(f"Fresh Recovery01 attempt contains unexpected launcher files: {unexpected_launcher_files}")\n    if RECEIPT.exists() or PROOF.exists():\n        raise RuntimeError("Fresh Recovery01 executor output namespace already exists")'''
if source.count(old_handshake) != 1:
    raise RuntimeError("Frozen executor handshake marker changed")
source = source.replace(old_handshake, new_handshake)
source = source.replace("mapped-preview01.v1", "mapped-preview01-recovery01.v1")
source = source.replace("PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW", "PASSED_RECOVERY01_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW")

for required in (
    "/Game/T08/GW02PreviewR01/Lvl_GW02_WindowPreview01_Recovery01",
    "M01_WINDOW_RECOVERY06_UNREALREADY01_MAPPED_PREVIEW01_RECOVERY01",
    "allowed_launcher_files",
):
    if required not in source:
        raise RuntimeError(f"Recovery01 correction missing: {required}")

compiled = compile(source, str(Path(__file__)), "exec")
exec(compiled, globals(), globals())
