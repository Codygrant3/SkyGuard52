import unreal

ROOT = (
    "/Game/Skyguard/Meshes/WebGame/yak52-detail-kit/"
    "yak52-detail-kit-blender/StaticMeshes"
)


def text(vector):
    return f"({vector.x:.3f},{vector.y:.3f},{vector.z:.3f})"


assets = unreal.EditorAssetLibrary.list_assets(ROOT, recursive=False, include_folder=False)
for path in sorted(assets):
    name = path.rsplit("/", 1)[-1].split(".", 1)[0]
    if not (name.startswith("production-yak52") or name.startswith("production-rear")):
        continue
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not asset:
        unreal.log(f"[SkyguardYakAsset] missing path={path}")
        continue
    bounds = asset.get_bounds()
    unreal.log(
        f"[SkyguardYakAsset] name={name} path={path} "
        f"origin={text(bounds.origin)} extent={text(bounds.box_extent)} "
        f"radius={bounds.sphere_radius:.3f}"
    )
unreal.log("[SkyguardYakAsset] COMPLETE")
