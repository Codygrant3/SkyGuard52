import unreal
import math

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def clear_prefix(prefix):
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def list_static_meshes(folder):
    out = []
    try:
        for a in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            asset = unreal.EditorAssetLibrary.load_asset(a)
            if isinstance(asset, unreal.StaticMesh):
                out.append((a, asset))
    except Exception as e:
        log("list fail " + str(e))
    return out

def bounds_size(mesh):
    try:
        e = mesh.get_bounds().box_extent
        return (abs(e.x) * 2.0, abs(e.y) * 2.0, abs(e.z) * 2.0)
    except Exception:
        return (100.0, 100.0, 100.0)

def spawn_sm(mesh, loc, scale=(1, 1, 1), rot=None, label=None, mat=None):
    if not mesh:
        return None
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator()
    )
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if mat:
        try:
            a.static_mesh_component.set_material(0, mat)
        except Exception:
            pass
    if label:
        a.set_actor_label(label)
    return a

def load_mat(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    return None

def make_emissive_mi(name, color, intensity):
    ensure_dir("/Game/Skyguard/Materials/Generated")
    path = "/Game/Skyguard/Materials/Generated/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    try:
        parent = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow")
        if not parent:
            # fallback create constant MI from engine default
            parent = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial")
        factory = unreal.MaterialInstanceConstantFactoryNew()
        mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/Materials/Generated", unreal.MaterialInstanceConstant, factory
        )
        if mi and parent:
            mi.set_editor_property("parent", parent)
            try:
                unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                    mi, "EmissiveColor", unreal.LinearColor(color[0], color[1], color[2], 1.0)
                )
            except Exception:
                pass
            try:
                unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
                    mi, "EmissiveStrength", float(intensity)
                )
            except Exception:
                pass
            unreal.EditorAssetLibrary.save_loaded_asset(mi)
            log("created MI " + name)
            return mi
    except Exception as e:
        log("mi fail " + name + " " + str(e))
    return load_mat("/Game/Skyguard/Materials/M_ExhaustGlow")

def ensure_ns(name):
    path = "/Game/Skyguard/VFX/" + name
    ensure_dir("/Game/Skyguard/VFX")
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    try:
        factory = unreal.NiagaraSystemFactoryNew()
        asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/VFX", unreal.NiagaraSystem, factory
        )
        if asset:
            unreal.EditorAssetLibrary.save_loaded_asset(asset)
            log("created ns " + name)
        return asset
    except Exception as e:
        log("ns fail " + name + " " + str(e))
        return None

def spawn_niagara(label, loc, asset_name):
    try:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.NiagaraActor, unreal.Vector(*loc), unreal.Rotator()
        )
        if not a:
            return None
        a.set_actor_label(label)
        asset = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/VFX/" + asset_name)
        try:
            comp = a.niagara_component
            if comp and asset:
                comp.set_asset(asset)
                try:
                    comp.activate(True)
                except Exception:
                    pass
        except Exception:
            pass
        return a
    except Exception as e:
        log("niagara spawn " + str(e))
        return None

def densify_city_materials():
    # Re-skin obvious proxy city meshes with PolyHaven-backed materials when labels match
    mats = {
        "asphalt": load_mat("/Game/Skyguard/Materials/M_Tex_L3_asphalt2") or load_mat("/Game/Skyguard/Materials/M_Asphalt") or load_mat("/Game/Skyguard/Materials/M_Road"),
        "concrete": load_mat("/Game/Skyguard/Materials/M_Tex_concrete") or load_mat("/Game/Skyguard/Materials/M_CityConcrete"),
        "brick": load_mat("/Game/Skyguard/Materials/M_Tex_brick"),
        "plaster": load_mat("/Game/Skyguard/Materials/M_Tex_L8_plaster2") or load_mat("/Game/Skyguard/Materials/M_Tex_L7_plaster2"),
        "metal": load_mat("/Game/Skyguard/Materials/M_Tex_metal") or load_mat("/Game/Skyguard/Materials/M_Metal"),
        "beach": load_mat("/Game/Skyguard/Materials/M_Tex_L7_beach2") or load_mat("/Game/Skyguard/Materials/M_Beach") or load_mat("/Game/Skyguard/Materials/M_Sand"),
        "ocean": load_mat("/Game/Skyguard/Materials/M_OceanDeep") or load_mat("/Game/Skyguard/Materials/M_Ocean"),
        "corrugated": load_mat("/Game/Skyguard/Materials/M_Tex_L8_corrugated") or load_mat("/Game/Skyguard/Materials/M_Tex_L7_corrugated"),
        "airframe": load_mat("/Game/Skyguard/Materials/M_Tex_airframe_metal") or load_mat("/Game/Skyguard/Materials/M_YakAirframe") or load_mat("/Game/Skyguard/Materials/M_Metal"),
    }
    applied = 0
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            if not isinstance(a, unreal.StaticMeshActor):
                continue
            label = (a.get_actor_label() or "").lower()
            smc = a.static_mesh_component
            if not smc:
                continue
            mat = None
            if any(k in label for k in ["road", "asphalt", "street", "district_ground", "terrain"]):
                mat = mats["asphalt"]
            elif any(k in label for k in ["beach", "sand"]):
                mat = mats["beach"]
            elif any(k in label for k in ["ocean", "water", "sea"]):
                mat = mats["ocean"]
            elif any(k in label for k in ["crane", "ship", "container", "metal", "sub", "harbor"]):
                mat = mats["metal"] if "corrug" not in label else mats["corrugated"]
            elif any(k in label for k in ["brick"]):
                mat = mats["brick"]
            elif any(k in label for k in ["building", "tower", "apartment", "facade", "city", "ruined"]):
                mat = mats["plaster"] or mats["concrete"]
            elif any(k in label for k in ["yak", "fuselage", "wing", "airframe", "cowling"]):
                mat = mats["airframe"]
            if mat:
                smc.set_material(0, mat)
                applied += 1
        except Exception:
            pass
    log("city/airframe material rebinds=" + str(applied))

def main():
    log("loop13 yak reassembly + vfx densify start")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    # clear previous yak/vfx/critic cam prefixes we own
    for p in ["AAA_L12_", "AAA_L11_Yak", "AAA_L13_", "AAA_L9V_", "AAA_L6V_"]:
        clear_prefix(p)

    ensure_dir("/Game/Skyguard/VFX")
    ensure_dir("/Game/Skyguard/Materials/Generated")

    meshes = list_static_meshes("/Game/Skyguard/Meshes/WebGame/yak52-detail-kit")
    log("yak meshes available=" + str(len(meshes)))

    # Prefer structural production meshes for scale reference
    scale_ref = None
    scale_ref_name = ""
    preferred = []
    for path, mesh in meshes:
        name = path.split("/")[-1].split(".")[0]
        lower = name.lower()
        if lower.startswith("production-yak52") or lower.startswith("production-rear"):
            preferred.append((path, mesh, name))
            if "wings-tail" in lower or "exterior-details" in lower or "fuselage" in lower:
                if scale_ref is None or "wings-tail" in lower:
                    scale_ref = mesh
                    scale_ref_name = name
    if scale_ref is None and preferred:
        scale_ref = preferred[0][1]
        scale_ref_name = preferred[0][2]
    if scale_ref is None and meshes:
        # fallback largest mesh
        best = None
        best_dim = 0
        for path, mesh in meshes:
            sx, sy, sz = bounds_size(mesh)
            m = max(sx, sy, sz)
            if m > best_dim:
                best_dim = m
                best = mesh
                scale_ref_name = path
        scale_ref = best

    # Target ~9.5m major dimension (950 uu)
    s = (1.0, 1.0, 1.0)
    if scale_ref:
        sx, sy, sz = bounds_size(scale_ref)
        m = max(sx, sy, sz, 0.001)
        sc = 950.0 / m
        # clamp
        if sc > 20.0:
            sc = 1.0
        if sc < 0.02:
            sc = 0.25
        s = (sc, sc, sc)
        log("scale_ref=%s bounds=%s scale=%s" % (scale_ref_name, (sx, sy, sz), s))
    else:
        log("NO scale ref; using 1.0")

    airframe_origin = (0.0, 40.0, 320.0)
    placed = 0
    # Place structural production meshes only (BATCH_* are often material-group extracts and can explode silhouette)
    for path, mesh, name in preferred:
        lower = name.lower()
        if lower.startswith("batch_"):
            continue
        spawn_sm(mesh, airframe_origin, s, None, "AAA_L13_Yak_%s" % name[:48])
        placed += 1
    # If no preferred, place all non-batch
    if placed == 0:
        for path, mesh in meshes:
            name = path.split("/")[-1].split(".")[0]
            if name.lower().startswith("batch_"):
                continue
            spawn_sm(mesh, airframe_origin, s, None, "AAA_L13_Yak_%s" % name[:48])
            placed += 1
    log("yak structural parts placed=" + str(placed))

    # Keep HD proxy as ghost under kit for silhouette fill if kit sparse
    proxy = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy")
    if proxy and placed < 5:
        spawn_sm(proxy, (0, 40, 300), (95, 95, 95), None, "AAA_L13_YakProxyFill")

    # Prop disc visual
    prop = unreal.EditorAssetLibrary.load_asset("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    prop_mat = load_mat("/Game/Skyguard/Materials/M_PropDisc")
    if prop:
        spawn_sm(prop, (-180, 40, 330), (s[0] * 1.2, s[1] * 1.2, s[2] * 1.2), unreal.Rotator(0, 0, 90), "AAA_L13_PropDisc", prop_mat)

    # Combat VFX materials
    muzzle_mi = make_emissive_mi("MI_MuzzleFlash_Hot", (1.0, 0.72, 0.25), 40.0)
    explosion_mi = make_emissive_mi("MI_ExplosionCore", (1.0, 0.35, 0.05), 25.0)
    trail_mi = make_emissive_mi("MI_DroneTrail", (0.6, 0.75, 1.0), 8.0)
    flak_mi = make_emissive_mi("MI_FlakFlash", (1.0, 0.9, 0.55), 18.0)
    smoke_mat = load_mat("/Game/Skyguard/Materials/M_Tex_L8_plaster2") or load_mat("/Game/Skyguard/Materials/M_CityConcrete")

    sphere = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    cone = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cone")
    cyl = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")

    # Authored visual FX volumes (mesh-based, readable in stills + PIE) + empty NS hooks
    for n in [
        "NS_MuzzleFlash", "NS_DroneTrail", "NS_DroneExplosion", "NS_FlakBurst",
        "NS_MissileTrail", "NS_GunSmoke", "NS_IglaLaunch", "NS_HitSparks",
        "NS_ShellCasings", "NS_TracerBurst", "NS_OceanSpray", "NS_PropWash"
    ]:
        ensure_ns(n)

    # Muzzle burst cloud near gunner
    for i in range(36):
        ang = (i / 36.0) * math.pi * 2.0
        r = 8.0 + (i % 5) * 2.5
        loc = (35 + math.cos(ang) * r, 150 + math.sin(ang) * r * 0.4, 364 + (i % 6) * 1.5)
        scale = 0.05 + (i % 4) * 0.02
        spawn_sm(sphere, loc, (scale, scale, scale * 1.2), None, "AAA_L13_Muzzle_%02d" % i, muzzle_mi)
    spawn_niagara("AAA_L13_NS_Muzzle", (40, 155, 365), "NS_MuzzleFlash")
    spawn_niagara("AAA_L13_NS_GunSmoke", (28, 142, 360), "NS_GunSmoke")

    # Tracer beads along firing lane
    for i in range(40):
        t = i / 40.0
        loc = (60 + t * 2200, 80 + math.sin(i * 0.35) * 20, 360 + math.cos(i * 0.2) * 12)
        spawn_sm(sphere, loc, (0.08, 0.08, 0.18), None, "AAA_L13_Tracer_%02d" % i, muzzle_mi)

    # Explosion shells over ocean approach
    for i in range(24):
        loc = (-1600 + (i % 8) * 90, -500 + (i // 8) * 220, 120 + (i % 5) * 25)
        sc = 1.1 + (i % 4) * 0.35
        spawn_sm(sphere, loc, (sc, sc, sc * 0.85), None, "AAA_L13_Explode_%02d" % i, explosion_mi)
        if smoke_mat and i % 2 == 0:
            spawn_sm(sphere, (loc[0], loc[1], loc[2] + 40), (sc * 1.6, sc * 1.6, sc * 1.2), None, "AAA_L13_Smoke_%02d" % i, smoke_mat)
    spawn_niagara("AAA_L13_NS_Explosion", (-1650, 0, 150), "NS_DroneExplosion")
    spawn_niagara("AAA_L13_NS_Flak", (-1500, 450, 180), "NS_FlakBurst")

    # Flak puffs
    for i in range(20):
        loc = (-1400 + i * 40, 200 + (i % 7) * 70, 160 + (i % 4) * 35)
        spawn_sm(sphere, loc, (1.4, 1.4, 1.2), None, "AAA_L13_Flak_%02d" % i, flak_mi)

    # Drone trail ribbons (cones)
    for i in range(30):
        loc = (1800 - i * 55, math.sin(i * 0.4) * 120, 430 + math.cos(i * 0.25) * 20)
        spawn_sm(cone if cone else sphere, loc, (0.35, 0.35, 1.2), unreal.Rotator(0, 90, 0), "AAA_L13_Trail_%02d" % i, trail_mi)
    spawn_niagara("AAA_L13_NS_Trail", (2000, 0, 430), "NS_DroneTrail")
    spawn_niagara("AAA_L13_NS_Missile", (1400, 300, 410), "NS_MissileTrail")
    spawn_niagara("AAA_L13_NS_Igla", (-30, 160, 355), "NS_IglaLaunch")

    # Prop wash + ocean spray
    for i in range(18):
        ang = (i / 18.0) * math.pi * 2.0
        loc = (-160 + math.cos(ang) * 70, 40 + math.sin(ang) * 70, 300)
        spawn_sm(sphere, loc, (0.5, 0.5, 0.2), None, "AAA_L13_PropWash_%02d" % i, trail_mi)
    spawn_niagara("AAA_L13_NS_PropWash", (0, -520, 300), "NS_PropWash")
    for i in range(16):
        loc = (-700 + i * 30, -40 + (i % 3) * 25, 6 + (i % 4) * 3)
        spawn_sm(sphere, loc, (0.7, 0.7, 0.25), None, "AAA_L13_Spray_%02d" % i, trail_mi)
    spawn_niagara("AAA_L13_NS_Spray", (-700, 0, 8), "NS_OceanSpray")

    densify_city_materials()

    # Critic cameras
    cams = [
        ("AAA_Cam_L13_YakBeauty", (700, -1200, 560), (-12, 145, 0)),
        ("AAA_Cam_L13_YakCockpitExt", (120, 200, 380), (-8, 200, 0)),
        ("AAA_Cam_L13_YakNose", (-220, -520, 340), (-5, 30, 0)),
        ("AAA_Cam_L13_Cockpit", (30, 115, 372), (-7, 8, 0)),
        ("AAA_Cam_L13_ADS", (18, 140, 366), (-1, 8, 0)),
        ("AAA_Cam_L13_CityApproach", (-900, -800, 420), (-10, 35, 0)),
        ("AAA_Cam_L13_OceanCombat", (1200, -600, 500), (-12, 160, 0)),
        ("AAA_Cam_L13_Explosion", (-1500, -300, 220), (-8, 20, 0)),
    ]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot)
        )
        if c:
            c.set_actor_label(name)

    # Reseed C++ combat actors
    try:
        gunner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardGunner")
        spawner_cls = unreal.load_class(None, "/Script/Skyguard52.SkyguardDroneSpawner")
        if gunner_cls:
            g = unreal.EditorLevelLibrary.spawn_actor_from_class(
                gunner_cls, unreal.Vector(20, 105, 360), unreal.Rotator()
            )
            if g:
                g.set_actor_label("AAA_L13_CPP_Gunner")
        if spawner_cls:
            sact = unreal.EditorLevelLibrary.spawn_actor_from_class(
                spawner_cls, unreal.Vector(2800, 0, 520), unreal.Rotator()
            )
            if sact:
                sact.set_actor_label("AAA_L13_CPP_Spawner")
    except Exception as e:
        log("cpp place " + str(e))

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop13 yak reassembly + vfx densify complete placed_yak=%d scale=%s" % (placed, s))
    log("CRITIC: still FAIL vs AAA until authored Niagara graphs + full environment heroes + blind win")

if __name__ == "__main__":
    main()
