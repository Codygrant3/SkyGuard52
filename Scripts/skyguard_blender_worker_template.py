from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "Scripts"))

from skyguard_blender_worker_sdk import create_socket, run_worker  # noqa: E402


ASSET_ID = "replace-with-manifest-asset-id"
REQUIRED_SOCKETS = ["SOCKET_Origin"]


def build_asset(asset_collection) -> None:
    """Create only governed asset geometry inside asset_collection.

    Replace this example with reference-backed modeling. Every mesh must have:
    - applied transforms;
    - at least one UV map;
    - production naming;
    - assigned PBR material intent.
    """
    import bpy

    bpy.ops.mesh.primitive_cube_add(size=1.0)
    mesh = bpy.context.object
    mesh.name = "GEO_ReplaceMe"
    for owner in list(mesh.users_collection):
        owner.objects.unlink(mesh)
    asset_collection.objects.link(mesh)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if not mesh.data.uv_layers:
        mesh.data.uv_layers.new(name="UV0")
    create_socket("SOCKET_Origin", (0.0, 0.0, 0.0), asset_collection)


if __name__ == "__main__":
    raise SystemExit(run_worker(ASSET_ID, build_asset, REQUIRED_SOCKETS))
