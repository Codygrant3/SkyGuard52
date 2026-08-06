import unreal

MAP = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"
AAA_PREFIXES = ("AAA_L", "AAA_Cam_L")
HERO_ASSETS = (
    "/Game/Skyguard/Meshes/Hero/yak52_hd_proxy",
    "/Game/Skyguard/Meshes/Hero/yak52_proxy",
    "/Game/Skyguard/Meshes/WebGame/yak52-detail-kit/yak52-detail-kit-blender/StaticMeshes/yak52-detail-kit-blender",
    "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-fde",
    "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-glove",
    "/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-sleeve",
    "/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-body",
    "/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-wing",
    "/Game/Skyguard/Meshes/Hero/shahed_proxy",
    "/Game/Skyguard/Meshes/Hero/cockpit_tub_proxy",
    "/Game/Skyguard/Meshes/Hero/gunner_station_proxy",
    "/Game/Skyguard/Meshes/Hero/instrument_cluster_proxy",
    "/Game/Skyguard/Meshes/Hero/harbor_crane_proxy",
    "/Game/Skyguard/Meshes/Hero/container_ship_proxy",
    "/Game/Skyguard/Meshes/Hero/submarine_proxy",
)


def log(message):
    unreal.log(f"[SkyguardInspectL86] {message}")


def vector_text(vector):
    return f"({vector.x:.1f},{vector.y:.1f},{vector.z:.1f})"


def inspect_mesh(path):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not asset:
        log(f"ASSET missing path={path}")
        return
    try:
        bounds = asset.get_bounds()
        log(
            "ASSET "
            f"path={path} class={asset.get_class().get_name()} "
            f"origin={vector_text(bounds.origin)} "
            f"extent={vector_text(bounds.box_extent)} "
            f"radius={bounds.sphere_radius:.1f}"
        )
    except Exception as exc:
        log(
            f"ASSET path={path} class={asset.get_class().get_name()} "
            f"bounds_error={exc}"
        )


if not unreal.EditorLoadingAndSavingUtils.load_map(MAP):
    raise RuntimeError(f"failed to load map {MAP}")

actors = unreal.EditorLevelLibrary.get_all_level_actors()
base_actors = []
aaa_count = 0
for actor in actors:
    label = actor.get_actor_label()
    if label.startswith(AAA_PREFIXES):
        aaa_count += 1
        continue
    base_actors.append(actor)

log(
    f"MAP actor_total={len(actors)} aaa_actor_count={aaa_count} "
    f"base_actor_count={len(base_actors)}"
)

for actor in sorted(base_actors, key=lambda item: item.get_actor_label())[:500]:
    label = actor.get_actor_label()
    location = actor.get_actor_location()
    class_name = actor.get_class().get_name()
    mesh_path = ""
    try:
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component and component.static_mesh:
            mesh_path = component.static_mesh.get_path_name()
    except Exception:
        mesh_path = ""
    try:
        origin, extent = actor.get_actor_bounds(False)
        bounds_text = f" bounds_origin={vector_text(origin)} extent={vector_text(extent)}"
    except Exception:
        bounds_text = ""
    log(
        f"ACTOR label={label} class={class_name} loc={vector_text(location)}"
        f"{bounds_text} mesh={mesh_path}"
    )

for asset_path in HERO_ASSETS:
    inspect_mesh(asset_path)

log("COMPLETE")
