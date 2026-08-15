"""Fresh Recovery02 derivation of the frozen Recovery01 UE import author.

The executable body is mechanically derived from the immutable Recovery01
source after its exact hash is verified.  Recovery02 changes only the fresh
namespace, import roll, explicit positive-Z origin checks, and the UE 5.8 save
lifecycle that replaces the unavailable StaticMesh.post_edit_change call.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\author_m01_window_recovery06_unrealready01_import01_recovery01.py")
BASE_SHA256 = "1bbc40d6c0063a60e26be1921698ec43aa18d522a520fb6e5e75532d602e6d79"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen Recovery01 author is missing or changed")

source = BASE.read_text(encoding="utf-8")
source = source.replace("Recovery01", "Recovery02").replace("RECOVERY01", "RECOVERY02").replace("recovery01", "recovery02")
source = source.replace(
    "PASSED_INTERCHANGE_PIPELINE_REFLECTION_READY_FOR_RECOVERY02_IMPORT",
    "PASSED_INTERCHANGE_PIPELINE_REFLECTION_READY_FOR_RECOVERY01_IMPORT",
)
source = source.replace('DESTINATION = "/Game/T08/GW01"', 'DESTINATION = "/Game/T08/GW02"')
source = source.replace('DESTINATION_DISK = ISOLATED / "Content/T08/GW01"', 'DESTINATION_DISK = ISOLATED / "Content/T08/GW02"')
source = source.replace("rotation.roll = 90.0", "rotation.roll = -90.0")

save_helper = '''\n\ndef save_loaded_asset(asset: object, unreal: object) -> None:\n    try:\n        saved = unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False)\n    except TypeError:\n        saved = unreal.EditorAssetLibrary.save_loaded_asset(asset)\n    require(saved is not False, f\"Failed to save normalized StaticMesh: {asset.get_path_name()}\")\n'''
marker = "\n\ndef normalize_frame_materials(frame: object) -> dict[str, object]:"
if source.count(marker) != 1:
    raise RuntimeError("Recovery01 material-normalization marker changed")
source = source.replace(marker, save_helper + marker)

old_post_edit = "    frame.post_edit_change()"
if source.count(old_post_edit) != 2:
    raise RuntimeError("Recovery01 post-edit lifecycle count changed")
source = source.replace(old_post_edit, "    save_loaded_asset(frame, unreal)")
source = source.replace(
    "def normalize_frame_materials(frame: object) -> dict[str, object]:",
    "def normalize_frame_materials(frame: object, unreal: object) -> dict[str, object]:",
)
source = source.replace("normalize_frame_materials(frame)", "normalize_frame_materials(frame, unreal)")

origin_helper = '''\n\ndef validate_origin(name: str, origin: list[float]) -> None:\n    expected = {\n        FRAME: (0.0, -3.7, 200.0),\n        GLASS: (0.0, -6.4, 214.8),\n        INTERIOR: (0.0, -131.0, 195.0),\n    }\n    for axis, target in enumerate(expected[name]):\n        require(abs(origin[axis] - target) <= 1.0, f\"Corrected positive-Z origin failed for {name} axis {axis}: {origin}\")\n'''
origin_marker = "\n\ndef run_unreal() -> None:"
if source.count(origin_marker) != 1:
    raise RuntimeError("Recovery01 Unreal entry marker changed")
source = source.replace(origin_marker, origin_helper + origin_marker)
source = source.replace(
    "            validate_bounds(name, vector(mesh.get_bounds().box_extent))",
    "            validate_bounds(name, vector(mesh.get_bounds().box_extent))\n            validate_origin(name, vector(mesh.get_bounds().origin))",
)

prior_freeze_constants = '''\nPRIOR_RECOVERY01_FREEZE = ROOT / r"Docs\\AAA_Review\\M01_WINDOW_REVERSIBLE_UNREAL_IMPORT01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json"\nPRIOR_RECOVERY01_FREEZE_BYTES = 1_869\nPRIOR_RECOVERY01_FREEZE_SHA256 = "e4c8baf00d3d580482c44b45104e9f1a68b95ddb0a665b65555ec7fd999be02b"\nPROBE02_FREEZE = ROOT / r"Docs\\AAA_Review\\M01_WINDOW_INTERCHANGE_PIPELINE_PROBE02_ATTEMPT01_TERMINAL_FREEZE.json"\n'''
authority_marker = 'PIPELINE_PROBE = ROOT / r"Saved\\BuildAttempts\\M01_WINDOW_INTERCHANGE_PIPELINE_PROBE01\\attempt_01\\probe_receipt.json"'
if source.count(authority_marker) != 1:
    raise RuntimeError("Recovery01 probe authority marker changed")
source = source.replace(authority_marker, prior_freeze_constants + authority_marker)

authority_checks = '''\n    require(PRIOR_RECOVERY01_FREEZE.is_file() and PRIOR_RECOVERY01_FREEZE.stat().st_size == PRIOR_RECOVERY01_FREEZE_BYTES, "Prior Recovery01 freeze is missing or changed")\n    require(sha256(PRIOR_RECOVERY01_FREEZE) == PRIOR_RECOVERY01_FREEZE_SHA256, "Prior Recovery01 freeze hash changed")\n    require(PROBE02_FREEZE.is_file(), "Probe02 terminal evidence is missing")\n'''
check_marker = "    document = read_glb_document(SOURCE)"
if source.count(check_marker) != 1:
    raise RuntimeError("Recovery01 source-validation marker changed")
source = source.replace(check_marker, authority_checks + "\n" + check_marker)

if "post_edit_change" in source:
    raise RuntimeError("Recovery02 still contains unavailable post_edit_change calls")
if source.count("rotation.roll = -90.0") != 1:
    raise RuntimeError("Recovery02 import-roll correction is not singular")
if source.count('DESTINATION = "/Game/T08/GW02"') != 1:
    raise RuntimeError("Recovery02 destination correction is not singular")

compiled = compile(source, str(Path(__file__)), "exec")
exec(compiled, globals(), globals())
