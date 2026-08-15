"""Independent offline verifier for the accepted window-bay UE import gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUTHOR = ROOT / r"Scripts\GrokProduction\author_m01_window_recovery06_unrealready01_import01.py"
CONTRACT = ROOT / r"Docs\GrokProduction\Wave02\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_CONTRACT.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    require(AUTHOR.is_file(), "Author script missing")
    require(CONTRACT.is_file(), "Execution contract missing")
    compile(AUTHOR.read_text(encoding="utf-8"), str(AUTHOR), "exec")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["classification"] == "READY_FOR_SINGLE_REVERSIBLE_UNREAL_IMPORT", "Contract classification changed")
    require(contract["launch_policy"] == {"heavy_processes": 1, "unreal_launches": 1, "retries": 0}, "Launch policy changed")

    spec = importlib.util.spec_from_file_location("window_import_author", AUTHOR)
    require(spec is not None and spec.loader is not None, "Cannot load author module")
    module = importlib.util.module_from_spec(spec)
    original_argv = sys.argv[:]
    try:
        sys.argv = [str(AUTHOR), "--offline-contract-test"]
        try:
            spec.loader.exec_module(module)
        except SystemExit as exc:
            require(exc.code == 0, f"Author contract test returned {exc.code}")
    finally:
        sys.argv = original_argv

    source = Path(contract["source"]["path"])
    require(source.stat().st_size == contract["source"]["bytes"], "Source byte count changed")
    require(sha256(source) == contract["source"]["sha256"], "Source hash changed")
    with source.open("rb") as stream:
        magic, version, total = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF" and version == 2 and total == source.stat().st_size, "GLB header invalid")
        json_length, json_type = struct.unpack("<II", stream.read(8))
        require(json_type == 0x4E4F534A, "GLB JSON chunk missing")
        document = json.loads(stream.read(json_length).decode("utf-8").rstrip("\x00 \t\r\n"))
    mesh_names = {str(row.get("name", "")) for row in document.get("meshes", [])}
    node_names = {str(row.get("name", "")) for row in document.get("nodes", [])}
    require(set(contract["required_render_meshes"]).issubset(mesh_names), "Required render meshes missing")
    require(set(contract["required_collision_nodes"]).issubset(mesh_names), "Required collision meshes missing")
    require(set(contract["required_socket_nodes"]).issubset(node_names), "Required socket nodes missing")
    require(not Path(contract["destination_disk"]).exists(), "Fresh destination namespace exists")
    require(not Path(contract["attempt"]).exists(), "Fresh attempt namespace exists")
    require(not Path(contract["terminal_manifest"]).exists(), "Fresh terminal namespace exists")
    print("PASS_M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_OFFLINE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
