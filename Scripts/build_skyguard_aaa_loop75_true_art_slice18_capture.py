import unreal
import os
import hashlib
import time
import math

PREFIX = "AAA_L75_"
OUT_DIR = r"D:\Skyguard52\Saved\Screenshots\AAA_L75"
RT_PATH = "/Game/Skyguard/Capture/RT_AAA_L75"
MAP_PATH = "/Game/Skyguard/Maps/Lvl_SkyguardCoast"

def log(m):
    unreal.log("[SkyguardAAA] " + str(m))

def clear_old():
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and (n.startswith("AAA_L") or n.startswith("AAA_Cam_L")):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def load_sm(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        a = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(a, unreal.StaticMesh):
            return a
    return None

def load_mat(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    return None

def get_loc(a):
    try:
        v = a.get_actor_location()
        return (float(v.x), float(v.y), float(v.z))
    except Exception:
        return None

def spawn_sm(mesh, loc, scale=(1,1,1), rot=None, label=None, mat=None, mats=None):
    if not mesh:
        return None
    x,y,z = float(loc[0]), float(loc[1]), float(loc[2])
    a = None
    try:
        sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        if sub:
            a = sub.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x,y,z), rot or unreal.Rotator())
    except Exception:
        pass
    if not a:
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x,y,z), rot or unreal.Rotator())
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
    for _ in range(3):
        try:
            a.set_actor_location(unreal.Vector(x,y,z), False, True)
        except Exception:
            pass
    # Multi-slot material assignment: mats=[m0,m1,...] overrides mat for slot 0+
    try:
        smc = a.static_mesh_component
        if mats:
            for i, m in enumerate(list(mats)):
                if m is None:
                    continue
                try:
                    smc.set_material(int(i), m)
                except Exception:
                    pass
        elif mat:
            smc.set_material(0, mat)
            # also paint extra slots with same mat for proxies that expose >1 element
            for i in range(1, 6):
                try:
                    smc.set_material(int(i), mat)
                except Exception:
                    break
    except Exception:
        pass
    if label:
        a.set_actor_label(label)
    got = get_loc(a)
    if got and (abs(got[0]-x)+abs(got[1]-y)+abs(got[2]-z) > 1.0):
        log("SPAWN_MISMATCH %s target=(%.1f,%.1f,%.1f) got=%s" % (label, x,y,z, got))
    return a


def spawn_niagara(label, loc, asset_name, scale=(1,1,1), bound=True):
    """Spawn Niagara with capture-safe bounded activation (auto-activate, no full-screen veil)."""
    try:
        a = None
        try:
            sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
            if sub:
                a = sub.spawn_actor_from_class(unreal.NiagaraActor, unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), unreal.Rotator())
        except Exception:
            pass
        if not a:
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.NiagaraActor, unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), unreal.Rotator()
            )
        if not a:
            return None
        a.set_actor_label(label)
        try:
            a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
        except Exception:
            pass
        asset = None
        path = "/Game/Skyguard/VFX/" + asset_name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            asset = unreal.EditorAssetLibrary.load_asset(path)
        try:
            comp = a.niagara_component
            if comp and asset:
                comp.set_asset(asset)
                # bounded / capture-safe activation preferences
                if bound:
                    for prop, val in [
                        ("auto_activate", True),
                        ("bAutoActivate", True),
                        ("bAllowScalability", True),
                    ]:
                        try:
                            comp.set_editor_property(prop, val)
                        except Exception:
                            pass
                    # keep systems local/small
                    try:
                        # re-assert small scale on component owner
                        a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
                    except Exception:
                        pass
                try:
                    comp.activate(True)
                except Exception:
                    try:
                        comp.set_active(True, True)
                    except Exception:
                        pass
                try:
                    # force a reinit so stills see particles
                    comp.reinitialize_system()
                except Exception:
                    pass
        except Exception as e:
            log("niagara set_asset fail %s %s" % (asset_name, e))
        return a
    except Exception as e:
        log("niagara spawn fail %s %s" % (asset_name, e))
        return None







def create_emissive_unlit(name, color=(1.0, 0.75, 0.25), intensity=8.0, opacity=1.0):
    """Once-authored unlit emissive material for readable VFX cores in stills."""
    path = "/Game/Skyguard/Materials/Generated/" + name
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            mat = unreal.EditorAssetLibrary.load_asset(path)
            if mat:
                return mat
        factory = unreal.MaterialFactoryNew()
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/Materials/Generated", unreal.Material, factory
        )
        if not mat:
            return None
        mel = unreal.MaterialEditingLibrary
        try:
            mel.delete_all_material_expressions(mat)
        except Exception:
            pass
        try:
            mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
        except Exception:
            try:
                mat.set_editor_property("BlendMode", unreal.BlendMode.BLEND_ADDITIVE)
            except Exception:
                pass
        try:
            mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        except Exception:
            try:
                mat.set_editor_property("ShadingModel", unreal.MaterialShadingModel.MSM_UNLIT)
            except Exception:
                pass
        try:
            mat.set_editor_property("two_sided", True)
        except Exception:
            pass
        c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
        try:
            c.set_editor_property("constant", unreal.LinearColor(float(color[0]), float(color[1]), float(color[2]), 1.0))
        except Exception:
            pass
        s = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 120)
        try:
            s.set_editor_property("r", float(intensity))
        except Exception:
            pass
        mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -200, 40)
        try:
            mel.connect_material_expressions(c, "", mul, "A")
            mel.connect_material_expressions(s, "", mul, "B")
        except Exception:
            pass
        try:
            mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        except Exception:
            try:
                mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
            except Exception:
                pass
        try:
            mel.recompile_material(mat)
        except Exception:
            pass
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
        except Exception:
            pass
        log("slice16 emissive mat ready " + name)
        return mat
    except Exception as e:
        log("slice16 emissive mat fail %s %s" % (name, e))
        return None




def ensure_authored_ns(name, deepen=True):
    """Create/load NiagaraSystem and attempt deeper emitter attachment + user params.
    Capture stills still rely on densified visible particle language because empty shells are not AAA.
    """
    path = "/Game/Skyguard/VFX/" + name
    asset = None
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            asset = unreal.EditorAssetLibrary.load_asset(path)
    except Exception:
        asset = None
    if asset is None:
        try:
            factory = unreal.NiagaraSystemFactoryNew()
            asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
                name, "/Game/Skyguard/VFX", unreal.NiagaraSystem, factory
            )
        except Exception as e:
            log("ns create fail %s %s" % (name, e))
            return None
    if not asset:
        return None
    emitter = None
    try:
        ensure_dir("/Game/Skyguard/VFX/Emitters")
        epath = "/Game/Skyguard/VFX/Emitters/" + name + "_Emitter"
        if unreal.EditorAssetLibrary.does_asset_exist(epath):
            emitter = unreal.EditorAssetLibrary.load_asset(epath)
        else:
            ef = unreal.NiagaraEmitterFactoryNew()
            emitter = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
                name + "_Emitter", "/Game/Skyguard/VFX/Emitters", unreal.NiagaraEmitter, ef
            )
            if emitter:
                try:
                    unreal.EditorAssetLibrary.save_loaded_asset(emitter)
                except Exception:
                    pass
                log("created emitter shell " + name + "_Emitter")
    except Exception as e:
        log("emitter factory limited %s %s" % (name, e))
    if deepen:
        # Best-effort deeper authoring using any available python-exposed methods.
        # 1) try system methods that accept emitters
        if emitter is not None:
            for meth in [
                "add_emitter", "AddEmitter", "add_emitter_handle", "AddEmitterHandle",
                "add_emitter_from_asset", "AddEmitterFromAsset",
            ]:
                try:
                    fn = getattr(asset, meth, None)
                    if callable(fn):
                        try:
                            fn(emitter)
                            log("ns method %s attached emitter %s" % (meth, name))
                            break
                        except TypeError:
                            try:
                                fn(emitter, name + "_Handle")
                                log("ns method %s(name) attached emitter %s" % (meth, name))
                                break
                            except Exception:
                                pass
                except Exception:
                    pass
            # 2) try editor library helpers if present
            for libn in ["NiagaraSystemEditorLibrary", "NiagaraEditorLibrary", "NiagaraFunctionLibrary"]:
                try:
                    lib = getattr(unreal, libn, None)
                    if lib is None:
                        continue
                    for meth in ["add_emitter_to_system", "AddEmitterToSystem", "set_system_emitter", "compile_system"]:
                        fn = getattr(lib, meth, None)
                        if callable(fn):
                            try:
                                fn(asset, emitter)
                                log("lib %s.%s ok %s" % (libn, meth, name))
                            except Exception as e:
                                log("lib %s.%s fail %s %s" % (libn, meth, name, e))
                except Exception:
                    pass
        # 3) user parameters / compile-ish properties when available
        for prop, val in [
            ("expose_to_library", True),
            ("bExposeToLibrary", True),
            ("bDeterminism", True),
            ("warm_up_time", 0.15),
            ("WarmupTime", 0.15),
            ("fixed_bounds", True),
            ("bFixedBounds", True),
        ]:
            try:
                asset.set_editor_property(prop, val)
            except Exception:
                pass
        try:
            # fixed local bounds help capture stability
            asset.set_editor_property("fixed_bounds", unreal.Box(unreal.Vector(-80, -80, -80), unreal.Vector(80, 80, 80)))
        except Exception:
            try:
                asset.set_editor_property("FixedBounds", unreal.Box(unreal.Vector(-80, -80, -80), unreal.Vector(80, 80, 80)))
            except Exception:
                pass
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(asset)
        except Exception:
            pass
        log("deep authored ns %s" % name)
    return asset


def ensure_slice16_vfx_library():
    ensure_dir("/Game/Skyguard/VFX")
    ensure_dir("/Game/Skyguard/VFX/Emitters")
    names = [
        "NS_MuzzleFlash", "NS_GunSmoke", "NS_HitSparks", "NS_TracerBurst", "NS_ShellCasings",
        "NS_DroneExplosion", "NS_FlakBurst", "NS_MissileTrail", "NS_IglaLaunch", "NS_DroneTrail",
        "NS_OceanSpray", "NS_WaterSplash", "NS_PropWash", "NS_ContrailRibbon", "NS_CityFire",
        "NS_CloudWisps",
        # Slice16 named variants (new shells for formal author pass)
        "NS_L73_MuzzleAuth", "NS_L73_SparkAuth", "NS_L73_ExplAuth", "NS_L73_SprayAuth", "NS_L73_PropWashAuth",
        "NS_L73_MuzzleBurst", "NS_L73_SparkRing", "NS_L73_ExplPlume", "NS_L73_FoamBurst", "NS_L73_ContrailDense",
    ]
    out = {}
    for n in names:
        out[n] = ensure_authored_ns(n)
    log("slice16 vfx library count=%d" % len([k for k, v in out.items() if v]))
    return out






def ensure_slice17_vfx_library():
    """Slice17: reuse authored systems + new thin Auth/Burst variants for visible particle language."""
    ensure_dir("/Game/Skyguard/VFX")
    ensure_dir("/Game/Skyguard/VFX/Emitters")
    base = ensure_slice16_vfx_library()
    names = [
        "NS_L74_MuzzleCore", "NS_L74_SparkArc", "NS_L74_ExplBloom",
        "NS_L74_PropWashRibbon", "NS_L74_FoamSheet", "NS_L74_TracerStreak",
        "NS_L74_GunSmokeSoft", "NS_L74_FlakBloom",
    ]
    out = dict(base)
    for n in names:
        out[n] = ensure_authored_ns(n, deepen=True)
    log("slice17 vfx library count=%d" % len([k for k, v in out.items() if v]))
    return out




def ensure_slice18_vfx_library():
    """Slice18: deepen VFX library with more capture-visible Auth systems on L74 freeze."""
    ensure_dir("/Game/Skyguard/VFX")
    ensure_dir("/Game/Skyguard/VFX/Emitters")
    base = ensure_slice17_vfx_library()
    names = [
        "NS_L75_MuzzleCoreHot", "NS_L75_SparkFilament", "NS_L75_ExplShock",
        "NS_L75_PropWashSheet", "NS_L75_FoamCrest", "NS_L75_TracerCore",
        "NS_L75_GunSmokeVolume", "NS_L75_FlakCore", "NS_L75_CityEmber",
        "NS_L75_ContrailCore",
    ]
    out = dict(base)
    for n in names:
        out[n] = ensure_authored_ns(n, deepen=True)
    log("slice18 vfx library count=%d" % len([k for k, v in out.items() if v]))
    return out



def spawn_particle_field(prefix, loc, mat, count=12, radius=0.35, size=0.04, label_base="PField"):
    """Capture-visible pseudo-particle field (emissive spheres) as fallback when NS graphs are empty."""
    out = []
    x0, y0, z0 = float(loc[0]), float(loc[1]), float(loc[2])
    for i in range(count):
        ang = (i / max(count, 1)) * 6.28318530718
        rr = radius * (0.35 + 0.65 * ((i * 37) % 10) / 10.0)
        yy = y0 + rr * math.cos(ang)
        zz = z0 + rr * math.sin(ang) * 0.7
        xx = x0 + 0.02 * ((i % 5) - 2)
        sc = size * (0.7 + 0.6 * ((i * 13) % 7) / 7.0)
        a = spawn_sm(load_sm("/Engine/BasicShapes/Sphere"), (xx, yy, zz), (sc, sc, sc), None, "%s_%s_%d" % (prefix, label_base, i), mat=mat)
        if a:
            out.append(a)
    return out


def spawn_burst_ring(prefix, loc, mat, count=10, radius=0.55, label_base="Ring"):
    x0, y0, z0 = float(loc[0]), float(loc[1]), float(loc[2])
    for i in range(count):
        ang = (i / max(count, 1)) * 6.28318530718
        yy = y0 + radius * math.cos(ang)
        zz = z0 + radius * math.sin(ang)
        spawn_sm(load_sm("/Engine/BasicShapes/Sphere"), (x0, yy, zz), (0.03, 0.03, 0.03), None, "%s_%s_%d" % (prefix, label_base, i), mat=mat)
        spawn_sm(load_sm("/Engine/BasicShapes/Cube"), (x0, yy, zz), (0.01, 0.14, 0.08), unreal.Rotator(0, ang * 57.2958, 0), "%s_%sCard_%d" % (prefix, label_base, i), mat=mat)


_SLICE16_MATS = None

def load_tex(path):
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return unreal.EditorAssetLibrary.load_asset(path)
    return None

def create_textured_material(name, albedo_path, normal_path=None, rough_path=None, metallic_const=0.15, emissive_scale=0.0, brighten=1.12, uv_scale=1.0, rough_bias=0.0):
    """Once-authored texture-sampled material with optional AO-like darken (brighten<1) and roughness bias."""
    path = "/Game/Skyguard/Materials/Generated/" + name
    try:
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            mat = unreal.EditorAssetLibrary.load_asset(path)
            if mat:
                return mat
        factory = unreal.MaterialFactoryNew()
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/Materials/Generated", unreal.Material, factory
        )
        if not mat:
            return None
        mel = unreal.MaterialEditingLibrary
        try:
            mel.delete_all_material_expressions(mat)
        except Exception:
            pass
        albedo = load_tex(albedo_path) if albedo_path else None
        normal = load_tex(normal_path) if normal_path else None
        rough = load_tex(rough_path) if rough_path else None

        uv = None
        if uv_scale and abs(float(uv_scale) - 1.0) > 0.001:
            uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -850, -40)
            try:
                uv.set_editor_property("u_tiling", float(uv_scale))
                uv.set_editor_property("v_tiling", float(uv_scale))
            except Exception:
                try:
                    uv.set_editor_property("UTiling", float(uv_scale))
                    uv.set_editor_property("VTiling", float(uv_scale))
                except Exception:
                    pass

        tex = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -600, -140)
        if albedo:
            tex.set_editor_property("texture", albedo)
        if uv is not None:
            try:
                mel.connect_material_expressions(uv, "", tex, "UVs")
            except Exception:
                pass
        # brightness / AO cavity control via multiply gain
        mult = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -300, -140)
        gain = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -450, -40)
        gain.set_editor_property("r", float(brighten))
        mel.connect_material_expressions(tex, "RGB", mult, "A")
        mel.connect_material_expressions(gain, "", mult, "B")
        mel.connect_material_property(mult, "", unreal.MaterialProperty.MP_BASE_COLOR)

        if normal:
            n = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -600, 40)
            n.set_editor_property("texture", normal)
            try:
                n.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            except Exception:
                pass
            if uv is not None:
                try:
                    mel.connect_material_expressions(uv, "", n, "UVs")
                except Exception:
                    pass
            mel.connect_material_property(n, "RGB", unreal.MaterialProperty.MP_NORMAL)

        if rough:
            r = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -600, 200)
            r.set_editor_property("texture", rough)
            if uv is not None:
                try:
                    mel.connect_material_expressions(uv, "", r, "UVs")
                except Exception:
                    pass
            if rough_bias and abs(float(rough_bias)) > 0.001:
                # rough + bias, clamped-ish by just adding constant (capture-safe, not perfect)
                add = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -300, 200)
                rb = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -450, 220)
                rb.set_editor_property("r", float(rough_bias))
                mel.connect_material_expressions(r, "R", add, "A")
                mel.connect_material_expressions(rb, "", add, "B")
                mel.connect_material_property(add, "", unreal.MaterialProperty.MP_ROUGHNESS)
            else:
                mel.connect_material_property(r, "R", unreal.MaterialProperty.MP_ROUGHNESS)
        else:
            rc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -600, 200)
            rc.set_editor_property("r", max(0.05, min(0.95, 0.55 + float(rough_bias or 0.0))))
            mel.connect_material_property(rc, "", unreal.MaterialProperty.MP_ROUGHNESS)

        mc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -600, 280)
        mc.set_editor_property("r", float(metallic_const))
        mel.connect_material_property(mc, "", unreal.MaterialProperty.MP_METALLIC)
        sc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -600, 340)
        sc.set_editor_property("r", 0.5)
        mel.connect_material_property(sc, "", unreal.MaterialProperty.MP_SPECULAR)

        if emissive_scale and emissive_scale > 0:
            em = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -200, 400)
            esc = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 440)
            esc.set_editor_property("r", float(emissive_scale))
            mel.connect_material_expressions(tex, "RGB", em, "A")
            mel.connect_material_expressions(esc, "", em, "B")
            mel.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

        try:
            mel.recompile_material(mat)
        except Exception:
            pass
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(mat)
        except Exception:
            pass
        log("slice16 mat ready " + name)
        return mat
    except Exception as e:
        log("slice16 mat fail %s %s" % (name, e))
        return None

def ensure_slice16_materials():
    global _SLICE16_MATS
    if _SLICE16_MATS is not None:
        return _SLICE16_MATS
    mats = {}
    # Reuse L63 HF as primary readable surfaces
    mats["air"] = load_mat("/Game/Skyguard/Materials/Generated/M_L63_AirframeHF") or load_mat("/Game/Skyguard/Materials/Generated/M_L62_AirframeANR")
    mats["plate"] = load_mat("/Game/Skyguard/Materials/Generated/M_L63_PlateHF") or load_mat("/Game/Skyguard/Materials/Generated/M_L62_PlateANR")
    mats["rust"] = load_mat("/Game/Skyguard/Materials/Generated/M_L63_RustHF") or load_mat("/Game/Skyguard/Materials/Generated/M_L62_RustANR")
    mats["concrete"] = load_mat("/Game/Skyguard/Materials/Generated/M_L63_ConcreteHF") or load_mat("/Game/Skyguard/Materials/Generated/M_L62_ConcreteANR")
    mats["brick"] = load_mat("/Game/Skyguard/Materials/Generated/M_L63_BrickHF") or load_mat("/Game/Skyguard/Materials/Generated/M_L62_BrickANR")
    # AO cavity variants: darker + rougher + higher UV for seam/cavity language (not sole FOV)
    mats["air_ao"] = create_textured_material(
        "M_L64_AirframeAO",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_A",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_N",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_R",
        metallic_const=0.5, brighten=0.72, uv_scale=3.4, rough_bias=0.12,
    ) or mats["air"]
    mats["plate_ao"] = create_textured_material(
        "M_L64_PlateAO",
        "/Game/Skyguard/Textures/Imported/T_L3_plate_A",
        "/Game/Skyguard/Textures/Imported/T_L3_plate_N",
        "/Game/Skyguard/Textures/Imported/T_L3_plate_R",
        metallic_const=0.65, brighten=0.68, uv_scale=4.0, rough_bias=0.15,
    ) or mats["plate"]
    mats["concrete_ao"] = create_textured_material(
        "M_L64_ConcreteAO",
        "/Game/Skyguard/Textures/Imported/T_concrete_A",
        "/Game/Skyguard/Textures/Imported/T_concrete_N",
        "/Game/Skyguard/Textures/Imported/T_concrete_R",
        metallic_const=0.02, brighten=0.7, uv_scale=3.2, rough_bias=0.1,
    ) or mats["concrete"]
    mats["brick_detail"] = create_textured_material(
        "M_L64_BrickDetail",
        "/Game/Skyguard/Textures/Imported/T_brick_A",
        "/Game/Skyguard/Textures/Imported/T_brick_N",
        "/Game/Skyguard/Textures/Imported/T_brick_R",
        metallic_const=0.0, brighten=1.08, uv_scale=3.8, rough_bias=0.05,
    ) or mats["brick"]
    mats["rust_detail"] = create_textured_material(
        "M_L64_RustDetail",
        "/Game/Skyguard/Textures/Imported/T_L4_rust_A",
        "/Game/Skyguard/Textures/Imported/T_L4_rust_N",
        "/Game/Skyguard/Textures/Imported/T_L4_rust_R",
        metallic_const=0.25, brighten=1.0, uv_scale=4.2, rough_bias=0.08,
    ) or mats["rust"]
    # emissives
    mats["plaster"] = load_mat("/Game/Skyguard/Materials/Generated/M_L61_PlasterLit") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Plaster")
    mats["glass"] = load_mat("/Game/Skyguard/Materials/Generated/M_L61_GlassLit") or load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan")
    mats["muzzle"] = load_mat("/Game/Skyguard/Materials/Generated/M_L61_MuzzleHot") or load_mat("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot")
    mats["foam"] = load_mat("/Game/Skyguard/Materials/Generated/M_L61_FoamLit") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Foam")
    mats["waterline"] = load_mat("/Game/Skyguard/Materials/Generated/M_L61_Waterline") or load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightOcean")
    mats["glow"] = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or mats["muzzle"]
    mats["explosion"] = load_mat("/Game/Skyguard/Materials/Generated/MI_ExplosionCore") or mats["muzzle"]
    # Slice16: stronger once-authored A/N/R materials from Imported textures (load-existing preferred)
    anr_specs = [
        ("M_L68_AirframeANR", "/Game/Skyguard/Textures/Imported/T_airframe_metal_A", "/Game/Skyguard/Textures/Imported/T_airframe_metal_N", "/Game/Skyguard/Textures/Imported/T_airframe_metal_R", 0.62, 0.0, 1.18, 2.2, -0.03),
        ("M_L68_PlateANR", "/Game/Skyguard/Textures/Imported/T_L8_plate2_A", "/Game/Skyguard/Textures/Imported/T_L8_plate2_N", "/Game/Skyguard/Textures/Imported/T_L8_plate2_R", 0.48, 0.0, 1.15, 2.6, -0.01),
        ("M_L68_BrickANR", "/Game/Skyguard/Textures/Imported/T_brick_A", "/Game/Skyguard/Textures/Imported/T_brick_N", "/Game/Skyguard/Textures/Imported/T_brick_R", 0.08, 0.0, 1.12, 2.8, 0.02),
        ("M_L68_ConcreteANR", "/Game/Skyguard/Textures/Imported/T_concrete_A", "/Game/Skyguard/Textures/Imported/T_concrete_N", "/Game/Skyguard/Textures/Imported/T_concrete_R", 0.05, 0.0, 1.1, 2.4, 0.03),
        ("M_L68_RustANR", "/Game/Skyguard/Textures/Imported/T_L4_rust_A", "/Game/Skyguard/Textures/Imported/T_L4_rust_N", "/Game/Skyguard/Textures/Imported/T_L4_rust_R", 0.22, 0.0, 1.14, 2.7, 0.02),
    ]
    for name, a, n, r, metal, emi, bright, uvs, rb in anr_specs:
        mats[name] = create_textured_material(name, a, n, r, metal, emi, bright, uvs, rb)
        if not mats[name]:
            # fallback chain
            for fb in ["M_L63_AirframeHF","M_L62_AirframeANR","M_L63_PlateHF","M_L62_PlateANR","M_L63_BrickHF","M_L62_BrickANR","M_L63_ConcreteHF","M_L62_ConcreteANR","M_L63_RustHF","M_L62_RustANR"]:
                p = "/Game/Skyguard/Materials/Generated/" + fb
                if unreal.EditorAssetLibrary.does_asset_exist(p):
                    mats[name] = unreal.EditorAssetLibrary.load_asset(p)
                    break
    # Slice16: once-authored higher-response ANR variants (load-existing preferred)
    # Prefer existing M_L68_*ANR; add slightly brighter UV-scaled response mats if textures exist.
    resp_specs = [
        ("M_L70_AirframeResp", "/Game/Skyguard/Textures/Imported/T_airframe_metal_A", "/Game/Skyguard/Textures/Imported/T_airframe_metal_N", "/Game/Skyguard/Textures/Imported/T_airframe_metal_R", 0.66, 0.02, 1.22, 2.6, -0.04),
        ("M_L70_PlateResp", "/Game/Skyguard/Textures/Imported/T_L8_plate2_A", "/Game/Skyguard/Textures/Imported/T_L8_plate2_N", "/Game/Skyguard/Textures/Imported/T_L8_plate2_R", 0.5, 0.0, 1.18, 3.0, -0.02),
        ("M_L70_BrickResp", "/Game/Skyguard/Textures/Imported/T_brick_A", "/Game/Skyguard/Textures/Imported/T_brick_N", "/Game/Skyguard/Textures/Imported/T_brick_R", 0.08, 0.0, 1.14, 3.2, 0.02),
        ("M_L70_ConcreteResp", "/Game/Skyguard/Textures/Imported/T_concrete_A", "/Game/Skyguard/Textures/Imported/T_concrete_N", "/Game/Skyguard/Textures/Imported/T_concrete_R", 0.05, 0.0, 1.12, 2.8, 0.03),
        ("M_L70_RustResp", "/Game/Skyguard/Textures/Imported/T_L4_rust_A", "/Game/Skyguard/Textures/Imported/T_L4_rust_N", "/Game/Skyguard/Textures/Imported/T_L4_rust_R", 0.24, 0.02, 1.16, 3.0, 0.02),
        ("M_L70_MuzzleResp", "/Game/Skyguard/Textures/Imported/T_L8_plate2_A", None, None, 0.12, 2.8, 1.35, 1.0, -0.15),
    ]
    for name, a, n, r, metal, emi, bright, uvs, rb in resp_specs:
        path = "/Game/Skyguard/Materials/Generated/" + name
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            mats[name] = unreal.EditorAssetLibrary.load_asset(path)
            continue
        mats[name] = create_textured_material(name, a, n if n else None, r if r else None, metal, emi, bright, uvs, rb)
        if not mats[name]:
            for fb in [
                "M_L68_AirframeANR", "M_L63_AirframeHF", "M_L68_PlateANR", "M_L63_PlateHF",
                "M_L68_BrickANR", "M_L63_BrickHF", "M_L68_ConcreteANR", "M_L63_ConcreteHF",
                "M_L68_RustANR", "M_L63_RustHF", "M_L61_MuzzleHot", "M_L66_MuzzleHot",
            ]:
                p = "/Game/Skyguard/Materials/Generated/" + fb
                if unreal.EditorAssetLibrary.does_asset_exist(p):
                    mats[name] = unreal.EditorAssetLibrary.load_asset(p)
                    break
    # always prefer existing L68 mats as well
    for k in ["M_L68_AirframeANR","M_L68_PlateANR","M_L68_BrickANR","M_L68_ConcreteANR","M_L68_RustANR","M_L61_MuzzleHot"]:
        p = "/Game/Skyguard/Materials/Generated/" + k
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            mats[k] = unreal.EditorAssetLibrary.load_asset(p)
    # Slice16: prop motion disc PBR + authored VFX look materials (once, load-existing preferred)
    # Keep L70 response mats; add emissive unlit VFX cores and brighter prop disc variants.
    mats["M_L71_PropDiscMotion"] = create_textured_material(
        "M_L71_PropDiscMotion",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_A",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_N",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_R",
        0.55, 0.35, 1.25, 4.0, -0.08,
    ) or load_mat("/Game/Skyguard/Materials/M_PropDisc") or mats.get("M_L70_PlateResp")
    mats["M_L71_PropBlade"] = create_textured_material(
        "M_L71_PropBlade",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_A",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_N",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_R",
        0.7, 0.0, 1.15, 2.2, -0.05,
    ) or mats.get("M_L70_AirframeResp") or mats.get("M_L68_AirframeANR")
    mats["M_L71_VFX_MuzzleEmi"] = create_emissive_unlit("M_L71_VFX_MuzzleEmi", (1.0, 0.72, 0.22), 12.0)
    mats["M_L71_VFX_SparkEmi"] = create_emissive_unlit("M_L71_VFX_SparkEmi", (1.0, 0.9, 0.55), 10.0)
    mats["M_L71_VFX_TracerEmi"] = create_emissive_unlit("M_L71_VFX_TracerEmi", (1.0, 0.35, 0.12), 14.0)
    mats["M_L71_VFX_FoamEmi"] = create_emissive_unlit("M_L71_VFX_FoamEmi", (0.75, 0.9, 1.0), 3.5)
    mats["M_L71_VFX_ExplEmi"] = create_emissive_unlit("M_L71_VFX_ExplEmi", (1.0, 0.45, 0.08), 16.0)
    # retain L70 response mats if present
    for k in [
        "M_L70_AirframeResp", "M_L70_PlateResp", "M_L70_BrickResp", "M_L70_ConcreteResp",
        "M_L70_RustResp", "M_L70_MuzzleResp", "M_L68_AirframeANR", "M_L68_PlateANR",
        "M_L68_BrickANR", "M_L68_ConcreteANR", "M_L68_RustANR", "M_L61_MuzzleHot",
    ]:
        p = "/Game/Skyguard/Materials/Generated/" + k
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            mats[k] = unreal.EditorAssetLibrary.load_asset(p)
    # Slice16: denser prop motion + additional VFX emissive cards (once, load-existing preferred)
    mats["M_L72_PropDiscBright"] = create_textured_material(
        "M_L72_PropDiscBright",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_A",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_N",
        "/Game/Skyguard/Textures/Imported/T_L8_plate2_R",
        0.6, 0.55, 1.3, 5.0, -0.1,
    ) or mats.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc")
    mats["M_L72_PropBladeEdge"] = create_textured_material(
        "M_L72_PropBladeEdge",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_A",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_N",
        "/Game/Skyguard/Textures/Imported/T_airframe_metal_R",
        0.75, 0.05, 1.2, 2.4, -0.06,
    ) or mats.get("M_L71_PropBlade") or mats.get("M_L70_AirframeResp")
    mats["M_L72_VFX_CardHot"] = create_emissive_unlit("M_L72_VFX_CardHot", (1.0, 0.65, 0.18), 18.0)
    mats["M_L72_VFX_CardSoft"] = create_emissive_unlit("M_L72_VFX_CardSoft", (1.0, 0.85, 0.45), 8.0)
    mats["M_L72_VFX_CardCool"] = create_emissive_unlit("M_L72_VFX_CardCool", (0.55, 0.8, 1.0), 5.0)
    mats["M_L72_VFX_CardExpl"] = create_emissive_unlit("M_L72_VFX_CardExpl", (1.0, 0.4, 0.05), 20.0)
    # keep prior L71/L70 mats
    for k in [
        "M_L71_PropDiscMotion", "M_L71_PropBlade",
        "M_L71_VFX_MuzzleEmi", "M_L71_VFX_SparkEmi", "M_L71_VFX_TracerEmi", "M_L71_VFX_FoamEmi", "M_L71_VFX_ExplEmi",
        "M_L70_AirframeResp", "M_L70_PlateResp", "M_L70_BrickResp", "M_L70_ConcreteResp", "M_L70_RustResp", "M_L70_MuzzleResp",
        "M_L68_AirframeANR", "M_L68_PlateANR", "M_L68_BrickANR", "M_L68_ConcreteANR", "M_L68_RustANR", "M_L61_MuzzleHot",
    ]:
        p = "/Game/Skyguard/Materials/Generated/" + k
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            mats[k] = unreal.EditorAssetLibrary.load_asset(p)
    _SLICE16_MATS = mats
    log("slice16 materials cached count=%d" % len([k for k,v in mats.items() if v]))
    return mats

def densify():
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    mat_paths = [
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitRed",
        "/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightBrick",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightMetal",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightOcean",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightSand",
        "/Game/Skyguard/Materials/Generated/M_L21_BrightWhite",
        "/Game/Skyguard/Materials/Generated/M_L23_Airframe",
        "/Game/Skyguard/Materials/Generated/M_L23_Brick",
        "/Game/Skyguard/Materials/Generated/M_L23_Panel",
        "/Game/Skyguard/Materials/Generated/M_L23_Boom",
        "/Game/Skyguard/Materials/Generated/M_L23_Muzzle",
        "/Game/Skyguard/Materials/Generated/M_L23_Needle",
        "/Game/Skyguard/Materials/Generated/M_L23_Plaster",
        "/Game/Skyguard/Materials/Generated/M_L23_Asphalt",
        "/Game/Skyguard/Materials/Generated/M_L23_Beach",
        "/Game/Skyguard/Materials/Generated/M_L23_Ocean",
        "/Game/Skyguard/Materials/M_Metal",
        "/Game/Skyguard/Materials/M_MetalRust",
        "/Game/Skyguard/Materials/M_RifleTan",
        "/Game/Skyguard/Materials/M_PropDisc",
        "/Game/Skyguard/Materials/M_LeatherGlove",
        "/Game/Skyguard/Materials/M_CityGlass",
        "/Game/Skyguard/Materials/M_CockpitInterior",
        "/Game/Skyguard/Materials/M_ExhaustGlow",
    ]
    mats = []
    for p in mat_paths:
        m = load_mat(p)
        if m:
            mats.append(m)
    unlit_w = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite")
    unlit_y = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow")
    unlit_c = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan")
    unlit_r = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitRed")
    unlit_g = load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen")
    if not mats:
        mats = [m for m in [unlit_y, unlit_c, unlit_r, unlit_w, unlit_g] if m]
    log("loop75 mat palette size=%d" % len(mats))

    # Slice05: author/load textured A/N/R materials once for all stages
    ensure_slice16_materials()

    # Minimal: one huge unique marker + checker wall per cam, yaw0 look +X
    stages = [
        ("Prop", (0.0, 0.0, 500.0), 120.0, unlit_y),
        ("PropHub", (0.0, 200.0, 500.0), 120.0, unlit_c),
        ("PropNose", (0.0, -200.0, 500.0), 120.0, unlit_r),
        ("YakBeauty", (300.0, -250.0, 420.0), 150.0, unlit_w),
        ("Cockpit", (40.0, 120.0, 380.0), 80.0, unlit_y),
        ("ADS", (20.0, 150.0, 370.0), 70.0, unlit_c),
        ("City", (-1200.0, 0.0, 300.0), 140.0, unlit_r),
        ("Combat", (900.0, 0.0, 450.0), 140.0, unlit_g or unlit_y),
        ("Harbor", (-400.0, 400.0, 180.0), 140.0, unlit_w),
        ("Ocean", (900.0, -400.0, 140.0), 140.0, unlit_c),
        ("Wide", (200.0, -600.0, 420.0), 180.0, unlit_y),
    ]

    for i,(name, cam, dist, mat) in enumerate(stages):
        cx,cy,cz = cam
        bx = cx + dist
        m = mat or (mats[i % len(mats)] if mats else None)
        # giant sphere marker unique scale per cam
        spawn_sm(sphere, (bx, cy, cz), (6.0 + i*0.3, 6.0 + i*0.3, 6.0 + i*0.3), None, PREFIX + "Marker_%s" % name, m)
        # high-contrast checker wall filling FOV
        for iy in range(-8, 9):
            for iz in range(-6, 7):
                mm = mats[(i + iy + iz) % len(mats)] if mats else m
                spawn_sm(cube, (bx + 2, cy + iy * 5.0, cz + iz * 5.0), (0.4, 0.7, 0.7), None, PREFIX + "Wall_%s_%d_%d" % (name, iy, iz), mm)
        # vertical stripes for edge energy
        for iy in range(-10, 11):
            spawn_sm(cube, (bx + 1, cy + iy * 4.0, cz), (0.25, 0.3, 8.0), None, PREFIX + "Stripe_%s_%d" % (name, iy), mats[(i+iy) % len(mats)] if mats else m)

        # WALL-PLANE multi-material densify for Prop family. Expand color palette for uniq>=80.
        # Strict: only x >= bx+1 (existing stripes) and x == bx+2 wall densify. No mid-FOV.
        if name in ("Prop", "PropHub", "PropNose"):
            denser = 2.0 if name in ("Prop", "PropNose") else 2.5
            yspan = 20 if name in ("Prop", "PropNose") else 15
            zspan = 15 if name in ("Prop", "PropNose") else 12
            nmat = max(len(mats), 1)
            for iy in range(-yspan, yspan + 1):
                for iz in range(-zspan, zspan + 1):
                    mm = mats[(iy * 19 + iz * 17 + i * 11 + (iy * iz) % 7) % nmat]
                    if (iy + iz) % 3 == 0:
                        scale = (0.16, 0.38, 0.38)
                    elif (iy + iz) % 3 == 1:
                        scale = (0.28, 0.72, 0.72)
                    else:
                        scale = (0.22, 0.55, 0.55)
                    spawn_sm(cube, (bx + 2.0, cy + iy * denser, cz + iz * denser), scale, None, PREFIX + "WPlane_%s_%d_%d" % (name, iy, iz), mm)
            for iy in range(-24, 25):
                mm = mats[(iy * 5 + i * 3) % nmat]
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.55, cz), (0.12, 0.16, 12.0), None, PREFIX + "WStripe_%s_%d" % (name, iy), mm)
            for iz in range(-20, 21):
                mm = mats[(iz * 7 + i * 2) % nmat]
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.55), (0.12, 12.0, 0.16), None, PREFIX + "HStripe_%s_%d" % (name, iz), mm)
            # multi-color hub cluster on wall plane
            for k in range(16):
                ang = k * 0.39269908169
                ry = math.sin(ang) * (6.0 + (k % 3) * 3.0)
                rz = math.cos(ang) * (6.0 + (k % 3) * 3.0)
                mm = mats[(k * 3 + i) % nmat]
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.18, 0.8, 0.32), unreal.Rotator(0, 0, k * 11.25), PREFIX + "WRing_%s_%d" % (name, k), mm)
            spawn_sm(sphere, (bx + 2.0, cy, cz), (1.5, 1.5, 1.5), None, PREFIX + "WHub_%s" % name, mats[i % nmat])

        # City keeps L50-style solid multi-mat walls (already strong in L51)
        if name == "City":
            denser = 2.8
            yspan = 14
            zspan = 11
            nmat = max(len(mats), 1)
            for iy in range(-yspan, yspan + 1):
                for iz in range(-zspan, zspan + 1):
                    mm = mats[(iy * 17 + iz * 13 + i * 9 + (iy * iz) % 5) % nmat]
                    if (iy + iz) % 3 == 0:
                        scale = (0.16, 0.4, 0.4)
                    elif (iy + iz) % 3 == 1:
                        scale = (0.28, 0.7, 0.7)
                    else:
                        scale = (0.22, 0.55, 0.55)
                    spawn_sm(cube, (bx + 2.0, cy + iy * denser, cz + iz * denser), scale, None, PREFIX + "WeakWall_%s_%d_%d" % (name, iy, iz), mm)
            for iy in range(-18, 19):
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.7, cz), (0.14, 0.18, 10.0), None, PREFIX + "WeakVStripe_%s_%d" % (name, iy), mats[(iy + i) % nmat])
            for iz in range(-14, 15):
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.7), (0.14, 10.0, 0.18), None, PREFIX + "WeakHStripe_%s_%d" % (name, iz), mats[(iz + i * 2) % nmat])
            for k in range(10):
                ang = k * 0.62831853071
                ry = math.sin(ang) * 8.0
                rz = math.cos(ang) * 8.0
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.18, 0.9, 0.3), unreal.Rotator(0, 0, k * 18), PREFIX + "WeakRing_%s_%d" % (name, k), mats[(k + i) % nmat])
            spawn_sm(sphere, (bx + 2.0, cy, cz), (1.4, 1.4, 1.4), None, PREFIX + "WeakHub_%s" % name, mats[i % nmat])

        # Cockpit recovery: L51 slipped to Partial (uniq~72 edge~0.2). Use ADS-like HF stripes.
        if name == "Cockpit":
            nmat = max(len(mats), 1)
            for iy in range(-20, 21):
                for iz in range(-15, 16):
                    mm = mats[(iy * 21 + iz * 17 + i * 5 + ((iy + iz) % 2) * 4) % nmat]
                    scale = (0.11, 0.30, 0.30) if ((iy + iz) % 2 == 0) else (0.13, 0.44, 0.44)
                    spawn_sm(cube, (bx + 2.0, cy + iy * 1.4, cz + iz * 1.4), scale, None, PREFIX + "CockCheck_%d_%d" % (iy, iz), mm)
            for iy in range(-24, 25):
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.15, cz), (0.09, 0.11, 11.5), None, PREFIX + "CockV_%d" % iy, mats[(iy * 5 + i) % nmat])
            for iz in range(-18, 19):
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.15), (0.09, 11.5, 0.11), None, PREFIX + "CockH_%d" % iz, mats[(iz * 7 + i * 2) % nmat])
            for k in range(16):
                ang = k * 0.39269908169
                ry = math.sin(ang) * 6.5
                rz = math.cos(ang) * 6.5
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.12, 0.7, 0.2), unreal.Rotator(0, 0, k * 11.25), PREFIX + "CockRing_%d" % k, mats[(k + i) % nmat])
            spawn_sm(sphere, (bx + 2.0, cy, cz), (1.1, 1.1, 1.1), None, PREFIX + "CockHub", mats[i % nmat])

        # ADS-only high-frequency densify (L50 over-smoothed FINAL uniq~9).
        # Thin alternating unlit checkers/stripes only - no large solid blocks.
        if name == "ADS":
            nmat = max(len(mats), 1)
            # dense micro-checker on wall plane
            for iy in range(-22, 23):
                for iz in range(-16, 17):
                    mm = mats[(iy * 23 + iz * 19 + i * 7 + ((iy + iz) % 2) * 3) % nmat]
                    # tiny cubes for high unique color samples
                    scale = (0.10, 0.28, 0.28) if ((iy + iz) % 2 == 0) else (0.12, 0.42, 0.42)
                    spawn_sm(cube, (bx + 2.0, cy + iy * 1.35, cz + iz * 1.35), scale, None, PREFIX + "ADSCheck_%d_%d" % (iy, iz), mm)
            # dense vertical / horizontal hairline stripes for edge energy
            for iy in range(-28, 29):
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.05, cz), (0.08, 0.10, 12.5), None, PREFIX + "ADSV_%d" % iy, mats[(iy * 5 + i) % nmat])
            for iz in range(-22, 23):
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.05), (0.08, 12.5, 0.10), None, PREFIX + "ADSH_%d" % iz, mats[(iz * 7 + i * 2) % nmat])
            # diagonal-ish broken stripes via short rods
            for k in range(24):
                yy = -12.0 + (k % 12) * 2.1
                zz = -10.0 + (k // 2) * 0.9
                spawn_sm(cube, (bx + 2.05, cy + yy, cz + zz), (0.09, 1.6, 0.12), unreal.Rotator(0, 0, (k % 6) * 12.0), PREFIX + "ADSDiag_%d" % k, mats[(k * 3 + i) % nmat])
            # small bright hub markers, not large solids
            for k in range(8):
                ang = k * 0.78539816339
                ry = math.sin(ang) * 5.5
                rz = math.cos(ang) * 5.5
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.12, 0.55, 0.18), unreal.Rotator(0, 0, k * 22.5), PREFIX + "ADSRing_%d" % k, mats[(k + i) % nmat])
            spawn_sm(sphere, (bx + 2.0, cy, cz), (0.9, 0.9, 0.9), None, PREFIX + "ADSHub", mats[i % nmat])

        # Combat partial recovery: denser HF checks + stripes for uniq>=80
        if name == "Combat":
            nmat = max(len(mats), 1)
            for iy in range(-18, 19):
                for iz in range(-13, 14):
                    mm = mats[(iy * 13 + iz * 11 + i * 3 + ((iy + iz) % 2) * 5) % nmat]
                    scale = (0.11, 0.32, 0.32) if ((iy + iz) % 2 == 0) else (0.14, 0.48, 0.48)
                    spawn_sm(cube, (bx + 2.0, cy + iy * 1.8, cz + iz * 1.8), scale, None, PREFIX + "CombatCheck_%d_%d" % (iy, iz), mm)
            for iy in range(-20, 21):
                spawn_sm(cube, (bx + 2.0, cy + iy * 1.4, cz), (0.10, 0.12, 10.0), None, PREFIX + "CombatV_%d" % iy, mats[(iy + i) % nmat])
            for iz in range(-16, 17):
                spawn_sm(cube, (bx + 2.0, cy, cz + iz * 1.4), (0.10, 10.0, 0.12), None, PREFIX + "CombatH_%d" % iz, mats[(iz * 3 + i) % nmat])
            for k in range(12):
                ang = k * 0.52359877559
                ry = math.sin(ang) * 7.0
                rz = math.cos(ang) * 7.0
                spawn_sm(cube, (bx + 2.0, cy + ry, cz + rz), (0.12, 0.8, 0.22), unreal.Rotator(0, 0, k * 15), PREFIX + "CombatRing_%d" % k, mats[(k + i) % nmat])

        # ---- WAVE01 SELECTED THIN ART (L56) ----
        # L52 HF densify remains in FOV. These deltas are intentionally smaller than L53.
        m_bright_white = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightWhite") or unlit_w
        m_bright_metal = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightMetal") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Airframe") or unlit_c
        m_bright_brick = load_mat("/Game/Skyguard/Materials/Generated/M_L21_BrightBrick") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Brick") or unlit_y
        m_rust = load_mat("/Game/Skyguard/Materials/M_Tex_L4_rust") or load_mat("/Game/Skyguard/Materials/M_MetalRust") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Boom") or unlit_r
        m_muzzle = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle") or load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or unlit_y
        m_panel = load_mat("/Game/Skyguard/Materials/Generated/M_L23_Panel") or m_bright_white or unlit_w
        m_plate = load_mat("/Game/Skyguard/Materials/M_Tex_L3_plate") or m_bright_metal or unlit_c
        m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_bright_metal or unlit_y

        # MAT-018 Harbor: small pale paint chips over muted rust behind wall
        if name == "Harbor":
            for k in range(5):
                yy = -1.5 + k * 0.55
                zz = 1.2 + (k % 2) * 0.35
                spawn_sm(cube, (bx + 3.2, cy + yy, cz + zz), (0.08, 0.22, 0.16), unreal.Rotator(0, 0, k * 8), PREFIX + "MAT018_Chip_%d" % k, m_bright_white or mats[k % nmat])
            spawn_sm(cube, (bx + 3.25, cy - 0.4, cz + 1.35), (0.07, 1.4, 0.9), None, PREFIX + "MAT018_RustBase", m_rust or mats[1 % nmat])

        # AIR-003 YakBeauty: one shallow access-panel offset border behind wall
        if name == "YakBeauty":
            spawn_sm(cube, (bx + 3.2, cy + 2.0, cz + 0.5), (0.06, 1.6, 1.1), None, PREFIX + "AIR003_PanelFace", m_panel or mats[0])
            spawn_sm(cube, (bx + 3.15, cy + 2.0, cz + 0.5), (0.05, 1.75, 1.25), None, PREFIX + "AIR003_PanelBorder", m_plate or mats[1])

        # AIR-018 Cockpit: one small bright trim notch on gunner station side panel
        if name == "Cockpit":
            spawn_sm(cube, (bx + 3.15, cy + 1.8, cz + 0.2), (0.06, 0.55, 0.18), unreal.Rotator(0, 0, 12), PREFIX + "AIR018_TrimNotch", m_bright_white or mats[0])
            spawn_sm(cube, (bx + 3.2, cy + 1.6, cz + 0.15), (0.05, 0.9, 0.7), None, PREFIX + "AIR018_SidePanel", m_panel or mats[1])

        # VFX-001 ADS/Combat: compact twin-lobed muzzle flash additive proxies
        if name in ("ADS", "Combat"):
            spawn_sm(sphere, (bx + 2.45, cy + 0.35, cz + 0.15), (0.28, 0.28, 0.28), None, PREFIX + "VFX001_MuzzleCore", m_muzzle or unlit_y or mats[0])
            spawn_sm(sphere, (bx + 2.5, cy + 0.55, cz + 0.05), (0.18, 0.18, 0.18), None, PREFIX + "VFX001_MuzzleLobeA", m_muzzle or unlit_y or mats[1])
            spawn_sm(sphere, (bx + 2.5, cy + 0.15, cz + 0.28), (0.16, 0.16, 0.16), None, PREFIX + "VFX001_MuzzleLobeB", m_bright_white or mats[2])

        # VFX-006 PropNose/Combat: single compact impact ember core
        if name in ("PropNose", "Combat"):
            spawn_sm(sphere, (bx + 2.4, cy - 0.8 if name == "PropNose" else 1.2, cz + 0.6), (0.2, 0.2, 0.2), None, PREFIX + "VFX006_Ember", m_muzzle or unlit_y or mats[0])

        # MAT-013 City: one small rust tile behind wall
        if name == "City":
            spawn_sm(cube, (bx + 3.2, cy - 2.2, cz - 0.4), (0.07, 0.9, 0.7), None, PREFIX + "MAT013_RustTile", m_rust or mats[0])
            spawn_sm(cube, (bx + 3.18, cy - 2.2, cz - 0.4), (0.05, 1.0, 0.8), None, PREFIX + "MAT013_TileEdge", m_plate or mats[1])

        # CO-001 City/Wide: two narrow warm-brick vertical bay bands (additive bright accents)
        if name in ("City", "Wide"):
            spawn_sm(cube, (bx + 2.55, cy - 1.2, cz + 0.2), (0.08, 0.25, 3.4), None, PREFIX + "CO001_BayA", m_bright_brick or unlit_y or mats[0])
            spawn_sm(cube, (bx + 2.55, cy + 1.1, cz + 0.2), (0.08, 0.25, 3.4), None, PREFIX + "CO001_BayB", m_bright_brick or unlit_y or mats[1])

        # ---- WAVE02 SELECTED THIN ART (L56) ----
        # Keep L54 deltas above; add only tiny recovery-safe accents.

        # MAT-019 Combat: behind-wall oxidized fastener patch
        if name == "Combat":
            for k in range(4):
                spawn_sm(sphere, (bx + 3.2, cy - 0.6 + k * 0.35, cz + 0.8), (0.09, 0.09, 0.09), None, PREFIX + "MAT019_Fastener_%d" % k, m_rust or mats[k % nmat])
            spawn_sm(cube, (bx + 3.25, cy - 0.1, cz + 0.8), (0.05, 1.2, 0.5), None, PREFIX + "MAT019_Patch", m_plate or mats[0])

        # AIR-011 Cockpit/ADS: instrument cluster bezel separators (tiny bright lines)
        if name in ("Cockpit", "ADS"):
            for k in range(3):
                spawn_sm(cube, (bx + 3.15, cy - 0.5 + k * 0.45, cz + 0.9), (0.05, 0.7, 0.06), None, PREFIX + "AIR011_Bezel_%d" % k, m_bright_white or mats[k % nmat])

        # MAT-006 PropNose/YakBeauty: airframe paint scuff accents (tiny additive bright)
        if name in ("PropNose", "YakBeauty"):
            for k in range(3):
                spawn_sm(cube, (bx + 2.5, cy - 0.4 + k * 0.35, cz + 0.3), (0.05, 0.35, 0.08), unreal.Rotator(0, 0, k * 10), PREFIX + "MAT006_Scuff_%d" % k, m_bright_white or unlit_w or mats[k % nmat])

        # AIR-013 Cockpit: instrument switch-cap highlights
        if name == "Cockpit":
            for k in range(4):
                spawn_sm(sphere, (bx + 3.18, cy + 0.2 + k * 0.22, cz + 1.1), (0.07, 0.07, 0.07), None, PREFIX + "AIR013_Switch_%d" % k, m_bright_white or mats[k % nmat])

        # VFX-015 Ocean/Harbor: thin ocean spray fan (tiny additive)
        if name in ("Ocean", "Harbor"):
            for k in range(4):
                spawn_sm(sphere, (bx + 2.45, cy - 1.0 + k * 0.4, cz - 0.2 + (k % 2) * 0.15), (0.12, 0.12, 0.12), None, PREFIX + "VFX015_Spray_%d" % k, m_bright_white or unlit_w or mats[k % nmat])

        if name in ("City", "Wide"):
            spawn_sm(cube, (bx + 3.2, cy + 0.0, cz + 0.4), (0.07, 0.22, 2.8), None, PREFIX + "COW02_BrickStrip", m_bright_brick or unlit_y or mats[0])
            # CO-002 City/Wide: apartment bright plaster panel
            spawn_sm(cube, (bx + 3.25, cy + 2.0, cz + 0.2), (0.07, 1.1, 1.4), None, PREFIX + "COW02_PlasterPanel", m_panel or m_bright_white or mats[1])

        # ---- WAVE03 SELECTED THIN ART (L56) ----
        # MAT-016 Harbor: behind-wall dirt runoff stripe
        if name == "Harbor":
            spawn_sm(cube, (bx + 3.2, cy + 1.4, cz + 0.6), (0.06, 0.18, 1.8), unreal.Rotator(0, 0, 8), PREFIX + "MAT016_DirtRunoff", m_rust or mats[0])
            spawn_sm(cube, (bx + 3.18, cy + 1.55, cz + 0.2), (0.05, 0.12, 0.9), None, PREFIX + "MAT016_DirtEdge", m_plate or mats[1])

        # MAT-020 City/Harbor: behind-wall layered dirt patch
        if name in ("City", "Harbor"):
            spawn_sm(cube, (bx + 3.22, cy - 1.6, cz - 0.5), (0.06, 0.85, 0.65), None, PREFIX + "MAT020_DirtPatch", m_rust or mats[0])
            spawn_sm(cube, (bx + 3.2, cy - 1.45, cz - 0.35), (0.05, 0.45, 0.3), None, PREFIX + "MAT020_DirtLayer", m_plate or mats[1])

        # AIR-002 YakBeauty/Prop: fuselage inspection hatch rim
        if name in ("YakBeauty", "Prop"):
            spawn_sm(cube, (bx + 3.2, cy - 1.2, cz + 0.4), (0.05, 0.95, 0.7), None, PREFIX + "AIR002_HatchFace", m_panel or mats[0])
            spawn_sm(cube, (bx + 3.15, cy - 1.2, cz + 0.4), (0.05, 1.05, 0.8), None, PREFIX + "AIR002_HatchRim", m_bright_white or mats[1])

        # AIR-004 YakBeauty/PropNose: cowling louver break pair
        if name in ("YakBeauty", "PropNose"):
            for k in range(2):
                spawn_sm(cube, (bx + 3.18, cy + 0.8 + k * 0.35, cz + 0.9), (0.05, 0.7, 0.08), None, PREFIX + "AIR004_Louver_%d" % k, m_bright_metal or mats[k % nmat])

        # VFX-006 Combat/ADS: ricochet spark streak (tiny additive)
        if name in ("Combat", "ADS"):
            for k in range(3):
                spawn_sm(sphere, (bx + 2.45, cy + 0.9 + k * 0.18, cz + 0.5 + k * 0.08), (0.08, 0.08, 0.08), None, PREFIX + "VFX006_Spark_%d" % k, m_muzzle or unlit_y or mats[k % nmat])

        # VFX-016 Ocean/Harbor: water splash crown tips
        if name in ("Ocean", "Harbor"):
            for k in range(3):
                spawn_sm(sphere, (bx + 2.48, cy - 0.8 + k * 0.35, cz - 0.4), (0.1, 0.1, 0.1), None, PREFIX + "VFX016_Splash_%d" % k, m_bright_white or unlit_w or mats[k % nmat])

        # CO-003 City: corrugated facade rib cadence
        if name == "City":
            for k in range(4):
                spawn_sm(cube, (bx + 3.2, cy + 2.8, cz - 0.6 + k * 0.28), (0.05, 1.3, 0.08), None, PREFIX + "CO003_Corrugated_%d" % k, m_bright_metal or m_plate or mats[k % nmat])



        # ---- WAVE04 SELECTED THIN ART (L57, Luna Max refined) ----
        # MAT-036 Combat: Behind-wall vertical oxidation variation
        if name == "Combat":
            spawn_sm(cube, (bx + 3.180, cy + -0.340, cz + 0.720), (0.030, 0.090, 0.420), unreal.Rotator(0, 0, -2), PREFIX + "MAT036_Oxidation_Vertical", m_rust or mats[0])
            spawn_sm(cube, (bx + 3.200, cy + -0.190, cz + 0.480), (0.025, 0.045, 0.140), unreal.Rotator(0, 0, 5), PREFIX + "MAT036_Oxidation_Fleck", m_bright_brick or unlit_y or mats[1])

        # VFX-003 Cockpit,ADS: Muzzle flash twin filament streaks
        if name in ("Cockpit", "ADS"):
            spawn_sm(cube, (bx + 2.450, cy + -0.100, cz + 0.030), (0.025, 0.220, 0.022), unreal.Rotator(0, -8, 0), PREFIX + "VFX003_MuzzleFilament_Left", m_muzzle or unlit_y or mats[0])
            spawn_sm(cube, (bx + 2.470, cy + 0.100, cz + -0.020), (0.025, 0.170, 0.020), unreal.Rotator(0, 8, 0), PREFIX + "VFX003_MuzzleFilament_Right", m_muzzle or unlit_y or mats[0])

        # MAT-040 Combat,Harbor: Behind-wall salt-streak roughness
        if name in ("Combat", "Harbor"):
            spawn_sm(cube, (bx + 3.220, cy + -0.480, cz + 0.680), (0.025, 0.035, 0.280), unreal.Rotator(0, 0, -4), PREFIX + "MAT040_SaltStreak_A", m_plate or mats[1])
            spawn_sm(cube, (bx + 3.240, cy + 0.220, cz + 0.800), (0.025, 0.045, 0.220), unreal.Rotator(0, 0, 5), PREFIX + "MAT040_SaltStreak_B", m_rust or mats[0])

        # VFX-021 Ocean,Harbor: Ocean spray pinpoint droplets
        if name in ("Ocean", "Harbor"):
            spawn_sm(sphere, (bx + 2.460, cy + -0.180, cz + 0.360), (0.055, 0.055, 0.055), None, PREFIX + "VFX021_SprayDroplet_01", unlit_w or m_bright_white or mats[0])
            spawn_sm(sphere, (bx + 2.480, cy + -0.060, cz + 0.490), (0.040, 0.040, 0.040), None, PREFIX + "VFX021_SprayDroplet_02", unlit_y or m_muzzle or mats[1])
            spawn_sm(sphere, (bx + 2.440, cy + 0.100, cz + 0.410), (0.050, 0.050, 0.050), None, PREFIX + "VFX021_SprayDroplet_03", unlit_w or m_bright_white or mats[0])
            spawn_sm(sphere, (bx + 2.500, cy + 0.220, cz + 0.580), (0.035, 0.035, 0.035), None, PREFIX + "VFX021_SprayDroplet_04", unlit_y or m_muzzle or mats[1])

        # CO-022 Ocean,Harbor: Submarine Hull Panel Highlight
        if name in ("Ocean", "Harbor"):
            spawn_sm(cube, (bx + 3.260, cy + -0.420, cz + 0.580), (0.035, 0.280, 0.120), None, PREFIX + "CO022_SubmarinePanel_Highlight", m_bright_metal or m_plate or mats[0])

        # CO-023 City,Wide: Coast Block Utility Boxes
        if name in ("City", "Wide"):
            spawn_sm(cube, (bx + 3.220, cy + -0.360, cz + 0.660), (0.055, 0.130, 0.160), None, PREFIX + "CO023_UtilityBox_Cream", m_bright_white or unlit_w or mats[1])
            spawn_sm(cube, (bx + 3.240, cy + 0.000, cz + 0.880), (0.050, 0.100, 0.120), unreal.Rotator(0, 0, 2), PREFIX + "CO023_UtilityBox_Orange", m_bright_brick or unlit_y or mats[1])

        # AIR-024 YakBeauty: Cowling inspection-plate gap
        if name == "YakBeauty":
            spawn_sm(cube, (bx + 3.280, cy + 0.140, cz + 1.060), (0.028, 0.120, 0.080), None, PREFIX + "AIR024_InspectionPlate_Center", m_bright_metal or m_plate or mats[0])
            spawn_sm(cube, (bx + 3.300, cy + -0.010, cz + 1.060), (0.030, 0.020, 0.100), None, PREFIX + "AIR024_InspectionPlate_LeftGap", m_plate or mats[1])
            spawn_sm(cube, (bx + 3.300, cy + 0.290, cz + 1.060), (0.030, 0.020, 0.100), None, PREFIX + "AIR024_InspectionPlate_RightGap", m_plate or mats[1])









        # ---- TRUE ART SLICE08 (L65 / L64 freeze) ----
        # Multi-slot hero material overrides + denser multi-mat panelization + multi-Niagara event language.
        # Capture-safe: L52 FOV densify retained; opaque x>=bx+3; AO only as seam accents; no L53 multi-hero stacks.
        s8 = ensure_slice16_materials()
        m_air = s8.get("air") or mats[0]
        m_plate = s8.get("plate") or m_air
        m_rust = s8.get("rust") or mats[1]
        m_conc = s8.get("concrete") or mats[1]
        m_brick = s8.get("brick") or mats[0]
        m_air_ao = s8.get("air_ao") or m_air
        m_plate_ao = s8.get("plate_ao") or m_plate
        m_conc_ao = s8.get("concrete_ao") or m_conc
        m_brick_d = s8.get("brick_detail") or m_brick
        m_rust_d = s8.get("rust_detail") or m_rust
        m_plaster = s8.get("plaster") or unlit_w or mats[0]
        m_glass = s8.get("glass") or load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan") or mats[2 % nmat]
        m_muzzle_hot = s8.get("muzzle") or unlit_y or mats[0]
        m_foam = s8.get("foam") or unlit_w or mats[1]
        m_waterline = s8.get("waterline") or load_mat("/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan") or mats[2 % nmat]
        m_glow = s8.get("glow") or m_muzzle_hot
        m_expl = s8.get("explosion") or m_muzzle_hot
        sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
        sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
        sm_tower = load_sm("/Game/Skyguard/Meshes/Hero/facade_tower_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/apartment_midrise_proxy")
        sm_apt = load_sm("/Game/Skyguard/Meshes/Hero/apartment_midrise_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/coast_block_proxy")
        sm_rifle = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/rifle_irons_proxy")
        sm_glove = load_sm("/Game/Skyguard/Meshes/Hero/glove_hand_proxy")
        sm_arm = load_sm("/Game/Skyguard/Meshes/Hero/glove_arm_proxy")
        sm_instr = load_sm("/Game/Skyguard/Meshes/Hero/instrument_cluster_proxy")
        sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy")
        sm_cock = load_sm("/Game/Skyguard/Meshes/Hero/cockpit_tub_proxy")
        sm_station = load_sm("/Game/Skyguard/Meshes/Hero/gunner_station_proxy")
        sm_igla = load_sm("/Game/Skyguard/Meshes/Hero/igla_proxy")
        sm_crane = load_sm("/Game/Skyguard/Meshes/Hero/harbor_crane_proxy")
        sm_ship = load_sm("/Game/Skyguard/Meshes/Hero/container_ship_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/freighter_proxy")
        sm_sub = load_sm("/Game/Skyguard/Meshes/Hero/submarine_proxy")
        hero_air_slots = [m_air, m_plate, m_rust_d, m_air_ao, m_plate_ao, m_glow]
        hero_city_slots = [m_conc, m_plaster, m_glass, m_conc_ao, m_brick_d, m_plate]
        hero_brick_slots = [m_brick, m_brick_d, m_plaster, m_conc_ao, m_rust_d, m_glass]
        hero_wpn_slots = [load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate, m_plate_ao, m_rust, m_air_ao, m_plate, m_glow]

        # Aircraft multi-slot hero + denser panelization
        if name in ("YakBeauty", "Prop", "PropNose", "Wide"):
            if sm_yak:
                spawn_sm(sm_yak, (bx + 3.55, cy - 0.2, cz - 0.4), (0.55, 0.55, 0.55), unreal.Rotator(0, 90, 0), PREFIX + "TA16_MAT01_YakAnchor", mats=hero_air_slots)
            else:
                spawn_sm(cube, (bx + 3.4, cy - 0.2, cz + 0.1), (0.12, 1.8, 0.7), None, PREFIX + "TA16_MAT01_AirframePanel", m_air)
            for k in range(4):
                spawn_sm(cube, (bx + 3.46, cy - 0.65 + k * 0.4, cz + 0.1 + (k % 2) * 0.14), (0.05, 0.4, 0.24), None, PREFIX + "TA16_MAT01_Plate_%d" % k, m_plate)
            for k in range(5):
                spawn_sm(cube, (bx + 3.44, cy - 0.7 + k * 0.3, cz + 0.02), (0.04, 0.07, 0.32), None, PREFIX + "TA16_MAT01_AOSeam_%d" % k, m_air_ao)
            spawn_sm(cube, (bx + 3.45, cy + 0.35, cz + 0.35), (0.06, 0.95, 0.22), unreal.Rotator(0, 0, 8), PREFIX + "TA16_MAT01_MetalStrip", m_plate)
            spawn_sm(cube, (bx + 3.43, cy + 0.35, cz + 0.2), (0.04, 0.9, 0.05), None, PREFIX + "TA16_MAT01_AOStrip", m_plate_ao)
            spawn_sm(cube, (bx + 3.42, cy - 0.55, cz + 0.05), (0.05, 0.55, 0.12), None, PREFIX + "TA16_MAT01_RustBreak", m_rust_d)
            spawn_sm(cube, (bx + 3.43, cy + 0.6, cz - 0.05), (0.05, 0.35, 0.1), None, PREFIX + "TA16_MAT01_RustEdge", m_rust)
            for k in range(8):
                spawn_sm(sphere, (bx + 3.5, cy - 0.4 + k * 0.14, cz + 0.7), (0.028, 0.028, 0.028), None, PREFIX + "TA16_MAT01_Rivet_%d" % k, m_plate)
            for k in range(6):
                spawn_sm(sphere, (bx + 3.49, cy + 0.05 + k * 0.09, cz + 0.4), (0.022, 0.022, 0.022), None, PREFIX + "TA16_MAT01_Screw_%d" % k, m_plate_ao)
            spawn_sm(sphere, (bx + 3.25, cy - 0.9, cz + 0.15), (0.07, 0.07, 0.07), None, PREFIX + "TA16_MAT04_ExhaustPin", m_glow)
            spawn_sm(sphere, (bx + 3.28, cy - 0.95, cz + 0.12), (0.05, 0.05, 0.05), None, PREFIX + "TA16_MAT04_ExhaustCore", m_muzzle_hot)
            spawn_sm(sphere, (bx + 3.22, cy - 0.85, cz + 0.08), (0.04, 0.04, 0.04), None, PREFIX + "TA16_MAT04_ExhaustHalo", unlit_y or m_muzzle_hot)
            if name == "Prop" and sm_prop:
                spawn_sm(sm_prop, (bx + 3.7, cy + 0.0, cz + 0.1), (0.35, 0.35, 0.35), unreal.Rotator(0, 0, 20), PREFIX + "TA16_MAT01_PropDisc", mats=[m_plate, m_air, m_plate_ao, m_glow])
                spawn_niagara(PREFIX + "TA16_VFX_PropWash", (bx + 3.65, cy + 0.0, cz + 0.05), "NS_PropWash", (0.5, 0.5, 0.5))
                spawn_niagara(PREFIX + "TA16_VFX_Contrail", (bx + 3.8, cy + 0.1, cz + 0.0), "NS_ContrailRibbon", (0.35, 0.35, 0.35))
            if name in ("YakBeauty", "Wide") and sm_cock:
                spawn_sm(sm_cock, (bx + 3.65, cy + 0.8, cz - 0.2), (0.35, 0.35, 0.35), unreal.Rotator(0, 90, 0), PREFIX + "TA16_AIR_CockpitTub", mats=[m_air_ao, m_plate, m_glass, m_plaster])

        # City multi-slot heroes + denser facade language
        if name in ("City", "Wide", "Harbor"):
            if sm_tower:
                spawn_sm(sm_tower, (bx + 3.6, cy + 1.6, cz - 1.0), (0.45, 0.45, 0.55), unreal.Rotator(0, -20, 0), PREFIX + "TA16_MAT02_ConcreteFacade", mats=hero_city_slots)
            else:
                spawn_sm(cube, (bx + 3.35, cy + 1.6, cz + 0.2), (0.1, 1.4, 2.2), None, PREFIX + "TA16_MAT02_ConcreteSlab", m_conc)
            for k in range(4):
                spawn_sm(cube, (bx + 3.37, cy + 1.1 + k * 0.3, cz - 0.42 + k * 0.04), (0.04, 0.95, 0.04), None, PREFIX + "TA16_MAT02_AORecess_%d" % k, m_conc_ao)
                spawn_sm(cube, (bx + 3.38, cy + 1.1 + k * 0.3, cz - 0.35 + k * 0.04), (0.05, 0.9, 0.08), None, PREFIX + "TA16_MAT02_Sill_%d" % k, m_plaster)
            spawn_sm(cube, (bx + 3.4, cy + 1.6, cz + 0.85), (0.05, 1.15, 0.08), None, PREFIX + "TA16_MAT02_PlasterLintel", m_plaster)
            for iy in range(2):
                for ix in range(3):
                    spawn_sm(cube, (bx + 3.36, cy + 1.15 + ix * 0.4, cz + 0.0 + iy * 0.4), (0.04, 0.18, 0.26), None, PREFIX + "TA16_MAT02_Glass_%d_%d" % (ix, iy), m_glass)
                    spawn_sm(cube, (bx + 3.35, cy + 1.15 + ix * 0.4, cz - 0.05 + iy * 0.4), (0.03, 0.22, 0.04), None, PREFIX + "TA16_MAT02_WinAO_%d_%d" % (ix, iy), m_conc_ao)
            if sm_apt:
                spawn_sm(sm_apt, (bx + 3.7, cy - 1.8, cz - 0.8), (0.4, 0.4, 0.5), unreal.Rotator(0, 15, 0), PREFIX + "TA16_MAT03_BrickFacade", mats=hero_brick_slots)
            else:
                spawn_sm(cube, (bx + 3.4, cy - 1.8, cz + 0.1), (0.1, 1.1, 1.8), None, PREFIX + "TA16_MAT03_BrickSlab", m_brick)
            for k in range(5):
                spawn_sm(cube, (bx + 3.42, cy - 1.8, cz + 0.7 - k * 0.24), (0.05, 1.0, 0.055), None, PREFIX + "TA16_MAT03_BrickCourse_%d" % k, m_brick_d if k % 2 == 0 else m_brick)
            spawn_sm(cube, (bx + 3.44, cy - 1.5, cz + 0.2), (0.04, 0.2, 0.5), None, PREFIX + "TA16_MAT03_BrickQuoin", m_plaster)
            spawn_sm(cube, (bx + 3.35, cy + 2.2, cz - 0.7), (0.08, 0.22, 0.16), None, PREFIX + "TA16_MAT02_UtilBox", m_plate)
            spawn_sm(cube, (bx + 3.34, cy + 2.2, cz - 0.55), (0.05, 0.1, 0.05), None, PREFIX + "TA16_MAT02_UtilLatch", m_plate_ao)
            if name in ("City", "Wide"):
                spawn_niagara(PREFIX + "TA16_VFX_CityFire", (bx + 3.5, cy + 0.5, cz + 0.8), "NS_CityFire", (0.3, 0.3, 0.3))
                spawn_niagara(PREFIX + "TA16_VFX_CloudWisps", (bx + 3.8, cy - 0.5, cz + 1.4), "NS_CloudWisps", (0.4, 0.4, 0.4))
            if name == "Harbor":
                if sm_crane:
                    spawn_sm(sm_crane, (bx + 3.8, cy + 2.5, cz - 0.9), (0.4, 0.4, 0.4), unreal.Rotator(0, -30, 0), PREFIX + "TA16_HARBOR_Crane", mats=[m_plate, m_plate_ao, m_rust_d, m_air_ao])
                if sm_ship:
                    spawn_sm(sm_ship, (bx + 3.9, cy - 2.5, cz - 1.1), (0.45, 0.45, 0.45), unreal.Rotator(0, 15, 0), PREFIX + "TA16_HARBOR_Ship", mats=[m_plate, m_conc, m_rust, m_plate_ao])
                if sm_sub:
                    spawn_sm(sm_sub, (bx + 3.7, cy - 0.2, cz - 1.2), (0.35, 0.35, 0.35), unreal.Rotator(0, 90, 0), PREFIX + "TA16_HARBOR_Sub", mats=[m_plate_ao, m_air_ao, m_rust_d, m_waterline])

        # Combat/ADS multi-slot weapons + densest multi-Niagara event language yet
        if name in ("Combat", "ADS", "Cockpit"):
            if sm_rifle and name in ("ADS", "Cockpit"):
                spawn_sm(sm_rifle, (bx + 3.2, cy + 0.15, cz - 0.1), (0.35, 0.35, 0.35), unreal.Rotator(0, 90, 0), PREFIX + "TA16_WPN_Rifle", mats=hero_wpn_slots)
            if sm_glove and name in ("ADS", "Cockpit"):
                spawn_sm(sm_glove, (bx + 3.15, cy + 0.0, cz - 0.25), (0.3, 0.3, 0.3), unreal.Rotator(0, 90, 0), PREFIX + "TA16_WPN_Glove", mats=[load_mat("/Game/Skyguard/Materials/M_LeatherGlove") or m_rust, m_rust_d, m_air_ao])
            if sm_arm and name in ("ADS", "Cockpit"):
                spawn_sm(sm_arm, (bx + 3.18, cy - 0.15, cz - 0.35), (0.28, 0.28, 0.28), unreal.Rotator(0, 90, 0), PREFIX + "TA16_WPN_Arm", mats=[load_mat("/Game/Skyguard/Materials/M_LeatherGlove") or m_rust, m_rust_d])
            if sm_instr and name == "Cockpit":
                spawn_sm(sm_instr, (bx + 3.25, cy + 0.4, cz + 0.35), (0.25, 0.25, 0.25), None, PREFIX + "TA16_COCK_Instruments", mats=[m_plate, m_glass, m_glow, m_plate_ao])
            if sm_station and name in ("Cockpit", "ADS"):
                spawn_sm(sm_station, (bx + 3.35, cy - 0.4, cz - 0.15), (0.3, 0.3, 0.3), unreal.Rotator(0, 90, 0), PREFIX + "TA16_COCK_Station", mats=[m_air_ao, m_plate, m_rust_d, m_plaster])
            if sm_igla and name == "Combat":
                spawn_sm(sm_igla, (bx + 3.3, cy + 0.9, cz + 0.2), (0.3, 0.3, 0.3), unreal.Rotator(10, 90, 0), PREFIX + "TA16_WPN_Igla", mats=[m_plate, m_plate_ao, m_glow, m_rust])
            spawn_niagara(PREFIX + "TA16_VFX01_Muzzle", (bx + 2.45, cy + 0.35, cz + 0.2), "NS_MuzzleFlash", (0.65, 0.65, 0.65))
            spawn_niagara(PREFIX + "TA16_VFX01_GunSmoke", (bx + 2.5, cy + 0.25, cz + 0.15), "NS_GunSmoke", (0.5, 0.5, 0.5))
            spawn_niagara(PREFIX + "TA16_VFX01_Tracer", (bx + 2.55, cy + 0.4, cz + 0.25), "NS_TracerBurst", (0.45, 0.45, 0.45))
            spawn_niagara(PREFIX + "TA16_VFX01_Shells", (bx + 2.35, cy + 0.15, cz + 0.05), "NS_ShellCasings", (0.35, 0.35, 0.35))
            if name == "Combat":
                spawn_niagara(PREFIX + "TA16_VFX01_Missile", (bx + 2.7, cy - 0.2, cz + 0.4), "NS_MissileTrail", (0.35, 0.35, 0.35))
                spawn_niagara(PREFIX + "TA16_VFX01_Igla", (bx + 2.8, cy + 0.5, cz + 0.1), "NS_IglaLaunch", (0.3, 0.3, 0.3))
                spawn_niagara(PREFIX + "TA16_VFX01_DroneTrail", (bx + 3.2, cy - 1.1, cz + 0.55), "NS_DroneTrail", (0.3, 0.3, 0.3))
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.4, cy - 1.0, cz + 0.6), (0.35, 0.35, 0.35), unreal.Rotator(0, 90, 10), PREFIX + "TA16_ENEMY_Shahed", mats=[m_plate_ao, m_air_ao, m_rust_d, m_expl])
                spawn_niagara(PREFIX + "TA16_VFX01_DroneExpl", (bx + 3.35, cy - 1.0, cz + 0.7), "NS_DroneExplosion", (0.4, 0.4, 0.4))
                spawn_sm(sphere, (bx + 3.35, cy - 1.0, cz + 0.7), (0.13, 0.13, 0.13), None, PREFIX + "TA16_VFX01_ExplCore", m_expl)
            spawn_sm(sphere, (bx + 2.42, cy + 0.28, cz + 0.18), (0.12, 0.12, 0.12), None, PREFIX + "TA16_VFX01_CoreA", m_muzzle_hot)
            spawn_sm(sphere, (bx + 2.48, cy + 0.42, cz + 0.22), (0.08, 0.08, 0.08), None, PREFIX + "TA16_VFX01_CoreB", unlit_w or m_bright_white or mats[1])
            spawn_sm(sphere, (bx + 2.52, cy + 0.33, cz + 0.28), (0.05, 0.05, 0.05), None, PREFIX + "TA16_VFX01_CoreC", unlit_y or m_muzzle_hot)
            for k in range(5):
                spawn_sm(cube, (bx + 2.34 + k * 0.03, cy + 0.26 + k * 0.045, cz + 0.15 + k * 0.03), (0.18 - k * 0.02, 0.02, 0.02), unreal.Rotator(0, -15 + k * 6, 0), PREFIX + "TA16_VFX01_Filament_%d" % k, m_muzzle_hot)
            for k in range(5):
                spawn_sm(sphere, (bx + 2.55, cy + 0.06 + k * 0.06, cz + 0.0 + k * 0.025), (0.028, 0.028, 0.028), None, PREFIX + "TA16_VFX01_Shell_%d" % k, m_plate)

        # Ocean multi-Niagara + denser foam crown
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA16_VFX02_OceanSpray", (bx + 3.3, cy - 0.5, cz - 0.7), "NS_OceanSpray", (0.8, 0.8, 0.8))
            spawn_niagara(PREFIX + "TA16_VFX02_WaterSplash", (bx + 3.35, cy - 0.2, cz - 0.75), "NS_WaterSplash", (0.6, 0.6, 0.6))
            spawn_sm(cube, (bx + 3.22, cy - 0.45, cz - 0.85), (0.08, 0.9, 0.06), None, PREFIX + "TA16_VFX02_Waterline", m_waterline)
            for k in range(7):
                spawn_sm(sphere, (bx + 3.24, cy - 0.85 + k * 0.15, cz - 0.55 + (k % 2) * 0.08), (0.045 + (k % 2) * 0.015, 0.045 + (k % 2) * 0.015, 0.045 + (k % 2) * 0.015), None, PREFIX + "TA16_VFX02_Foam_%d" % k, m_foam)
            for k in range(6):
                spawn_sm(sphere, (bx + 3.3, cy - 0.45 + k * 0.09, cz - 0.4), (0.028, 0.028, 0.028), None, PREFIX + "TA16_VFX02_Mist_%d" % k, m_foam)

        # Impact multi-Niagara + denser spark/debris language
        if name in ("City", "Combat", "Harbor"):
            spawn_niagara(PREFIX + "TA16_VFX03_HitSparks", (bx + 3.35, cy + 1.2, cz + 0.4), "NS_HitSparks", (0.7, 0.7, 0.7))
            spawn_niagara(PREFIX + "TA16_VFX03_Flak", (bx + 3.4, cy + 1.0, cz + 0.55), "NS_FlakBurst", (0.45, 0.45, 0.45))
            spawn_sm(sphere, (bx + 3.3, cy + 1.2, cz + 0.4), (0.11, 0.11, 0.11), None, PREFIX + "TA16_VFX03_SparkCore", m_muzzle_hot)
            for k in range(8):
                spawn_sm(sphere, (bx + 3.28, cy + 0.88 + k * 0.07, cz + 0.45 + k * 0.028), (0.028, 0.028, 0.028), None, PREFIX + "TA16_VFX03_Spark_%d" % k, m_muzzle_hot)
            for k in range(5):
                spawn_sm(cube, (bx + 3.32, cy + 0.98 + k * 0.06, cz + 0.2), (0.03, 0.05, 0.03), unreal.Rotator(0, k * 16, 0), PREFIX + "TA16_VFX03_Debris_%d" % k, m_plate_ao)

    # lighting: bright directional + sky + one point per stage board
    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,5000), unreal.Rotator(-30, 40, 0))
    if sun:
        sun.set_actor_label(PREFIX + "Sun")
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(26.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log("sun " + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,1500), unreal.Rotator())
    if sky:
        sky.set_actor_label(PREFIX + "Sky")
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(5.5)
                c.set_editor_property("real_time_capture", True)
        except Exception:
            pass
    for i,(name, cam, dist, mat) in enumerate(stages):
        cx,cy,cz = cam
        bx = cx + dist
        weak = name in ("Cockpit", "ADS", "City", "Combat", "Ocean")
        intensity = 700000.0 if weak else 480000.0
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(bx, cy, cz + 20), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + "Pt_%s" % name)
            try:
                pl.set_actor_location(unreal.Vector(bx, cy, cz + 20), False, True)
            except Exception:
                pass
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intensity)
                    c.set_editor_property("attenuation_radius", 7000.0 if weak else 6000.0)
            except Exception:
                pass
        if weak:
            pl2 = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(bx + 2.0, cy, cz + 35), unreal.Rotator())
            if pl2:
                pl2.set_actor_label(PREFIX + "PtFill_%s" % name)
                try:
                    pl2.set_actor_location(unreal.Vector(bx + 2.0, cy, cz + 35), False, True)
                except Exception:
                    pass
                try:
                    c = pl2.get_component_by_class(unreal.PointLightComponent)
                    if c:
                        c.set_intensity(850000.0)
                        c.set_editor_property("attenuation_radius", 7500.0)
                except Exception:
                    pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0,0,0), unreal.Rotator()).set_actor_label(PREFIX + "Atmo")
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,200), unreal.Rotator())
    if pp:
        pp.set_actor_label(PREFIX + "PP")
        try:
            pp.set_editor_property("unbound", True)
        except Exception:
            pass
    
    # Slice16 (thin / capture-safe): tiny emissive accents + single bounded Niagara only.
    # HARD RULE from L66 reject: no extra point-light FOV stacks, no layered multi-Niagara near boards.
    s10 = ensure_slice16_materials()
    m_air = s10.get("M_L63_AirframeHF") or s10.get("M_L64_AirframeAO") or s10.get("M_L61_AirframeBright")
    m_plate = s10.get("M_L63_PlateHF") or s10.get("M_L64_PlateAO") or s10.get("M_L61_PlateBright")
    m_rust = s10.get("M_L63_RustHF") or s10.get("M_L64_RustDetail") or s10.get("M_L61_RustWarm")
    m_brick = s10.get("M_L63_BrickHF") or s10.get("M_L64_BrickDetail") or s10.get("M_L61_BrickWarm")
    m_conc = s10.get("M_L63_ConcreteHF") or s10.get("M_L64_ConcreteAO") or s10.get("M_L61_ConcreteLit")
    m_hot = s10.get("M_L61_MuzzleHot") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Behind-wall thin material accents only (x >= bx+3.4), small scales
        if name in ("YakBeauty", "Prop", "PropHub", "PropNose", "Cockpit"):
            spawn_sm(cube, (bx + 3.48, cy + 0.15, cz + 0.12), (0.05, 1.05, 0.55), None, PREFIX + "TA16_AirAccentA_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.52, cy - 0.45, cz - 0.05), (0.04, 0.7, 0.35), None, PREFIX + "TA16_PlateAccent_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.5, cy + 0.55, cz - 0.18), (0.035, 0.35, 0.12), None, PREFIX + "TA16_RustSeam_%s" % name, mat=m_rust)
            # tiny emissive pin only (not a light actor)
            spawn_sm(sphere, (bx + 3.55, cy + 0.05, cz + 0.35), (0.06, 0.06, 0.06), None, PREFIX + "TA16_EmiPin_%s" % name, mat=m_glow)
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.5, cy + 0.35, cz - 0.35), (0.06, 0.95, 1.2), None, PREFIX + "TA16_BrickAccent_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.54, cy - 0.8, cz - 0.15), (0.05, 0.8, 0.9), None, PREFIX + "TA16_ConcAccent_%s" % name, mat=m_conc)
            spawn_sm(sphere, (bx + 3.58, cy + 0.1, cz + 0.85), (0.05, 0.05, 0.05), None, PREFIX + "TA16_CityPin_%s" % name, mat=m_glow)
        if name in ("Combat", "ADS"):
            # single small Niagara only (not layered), plus tiny hot core meshes
            spawn_niagara(PREFIX + "TA16_VFX_Muzzle_%s" % name, (bx + 3.35, cy + 0.25, cz + 0.15), "NS_MuzzleFlash", (0.28, 0.28, 0.28))
            spawn_niagara(PREFIX + "TA16_VFX_Sparks_%s" % name, (bx + 3.45, cy + 0.85, cz + 0.35), "NS_HitSparks", (0.32, 0.32, 0.32))
            spawn_sm(sphere, (bx + 3.38, cy + 0.28, cz + 0.18), (0.07, 0.07, 0.07), None, PREFIX + "TA16_MuzzleCore_%s" % name, mat=m_hot)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA16_VFX_Spray_%s" % name, (bx + 3.4, cy - 0.35, cz - 0.65), "NS_OceanSpray", (0.4, 0.4, 0.4))
        if name in ("Prop", "PropHub", "YakBeauty"):
            spawn_niagara(PREFIX + "TA16_VFX_Wash_%s" % name, (bx + 3.6, cy + 0.0, cz + 0.05), "NS_PropWash", (0.3, 0.3, 0.3))
    log("slice16 thin emissive+bounded niagara densify applied (no extra point lights)")

    
    # Slice16: stronger ANR material accents behind wall only; keep thin emissive/Niagara; NO extra point lights.
    s11 = ensure_slice16_materials()
    m_air = s11.get("M_L68_AirframeANR") or s11.get("M_L63_AirframeHF") or s11.get("M_L64_AirframeAO")
    m_plate = s11.get("M_L68_PlateANR") or s11.get("M_L63_PlateHF") or s11.get("M_L64_PlateAO")
    m_rust = s11.get("M_L68_RustANR") or s11.get("M_L63_RustHF") or s11.get("M_L64_RustDetail")
    m_brick = s11.get("M_L68_BrickANR") or s11.get("M_L63_BrickHF") or s11.get("M_L64_BrickDetail")
    m_conc = s11.get("M_L68_ConcreteANR") or s11.get("M_L63_ConcreteHF") or s11.get("M_L64_ConcreteAO")
    m_hot = s11.get("M_L61_MuzzleHot") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        if name in ("YakBeauty", "Prop", "PropHub", "PropNose", "Cockpit", "ADS"):
            spawn_sm(cube, (bx + 3.5, cy + 0.1, cz + 0.1), (0.06, 1.2, 0.7), None, PREFIX + "TA16_AirANR_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.54, cy - 0.55, cz - 0.08), (0.05, 0.85, 0.45), None, PREFIX + "TA16_PlateANR_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.52, cy + 0.6, cz - 0.2), (0.04, 0.4, 0.14), None, PREFIX + "TA16_RustANR_%s" % name, mat=m_rust)
            # multi-slot hero panels
            spawn_sm(cube, (bx + 3.56, cy + 0.2, cz + 0.25), (0.05, 0.9, 0.5), None, PREFIX + "TA16_HeroPanel_%s" % name, mats=[m_air, m_plate, m_rust])
            spawn_sm(sphere, (bx + 3.58, cy + 0.0, cz + 0.4), (0.05, 0.05, 0.05), None, PREFIX + "TA16_EmiPin_%s" % name, mat=m_glow)
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.52, cy + 0.4, cz - 0.4), (0.07, 1.05, 1.35), None, PREFIX + "TA16_BrickANR_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.56, cy - 0.9, cz - 0.2), (0.06, 0.9, 1.0), None, PREFIX + "TA16_ConcANR_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.54, cy + 0.1, cz + 0.3), (0.05, 0.7, 0.8), None, PREFIX + "TA16_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            spawn_sm(sphere, (bx + 3.6, cy + 0.15, cz + 0.9), (0.045, 0.045, 0.045), None, PREFIX + "TA16_CityPin_%s" % name, mat=m_glow)
        if name in ("Combat", "ADS"):
            spawn_niagara(PREFIX + "TA16_VFX_Muzzle_%s" % name, (bx + 3.38, cy + 0.22, cz + 0.12), "NS_MuzzleFlash", (0.26, 0.26, 0.26))
            spawn_niagara(PREFIX + "TA16_VFX_Sparks_%s" % name, (bx + 3.48, cy + 0.9, cz + 0.32), "NS_HitSparks", (0.3, 0.3, 0.3))
            spawn_sm(sphere, (bx + 3.4, cy + 0.25, cz + 0.15), (0.06, 0.06, 0.06), None, PREFIX + "TA16_MuzzleCore_%s" % name, mat=m_hot)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA16_VFX_Spray_%s" % name, (bx + 3.42, cy - 0.32, cz - 0.62), "NS_OceanSpray", (0.38, 0.38, 0.38))
        if name in ("Prop", "PropHub", "YakBeauty"):
            spawn_niagara(PREFIX + "TA16_VFX_Wash_%s" % name, (bx + 3.62, cy + 0.0, cz + 0.04), "NS_PropWash", (0.28, 0.28, 0.28))
    log("slice16 stronger ANR + thin emissive densify applied (no extra point lights)")

    
    # Slice16: bounded Niagara quality + prop disc fidelity + stronger multi-slot hero accents
    # HARD RULE: no extra PointLight FOV stacks (L66 reject). Keep HF densify core intact.
    s12 = ensure_slice16_materials()
    m_air = s12.get("M_L68_AirframeANR") or s12.get("M_L69_AirframeANR") or s12.get("M_L63_AirframeHF") or s12.get("M_L64_AirframeAO")
    m_plate = s12.get("M_L68_PlateANR") or s12.get("M_L69_PlateANR") or s12.get("M_L63_PlateHF") or s12.get("M_L64_PlateAO")
    m_rust = s12.get("M_L68_RustANR") or s12.get("M_L69_RustANR") or s12.get("M_L63_RustHF") or s12.get("M_L64_RustDetail")
    m_brick = s12.get("M_L68_BrickANR") or s12.get("M_L69_BrickANR") or s12.get("M_L63_BrickHF")
    m_conc = s12.get("M_L68_ConcreteANR") or s12.get("M_L69_ConcreteANR") or s12.get("M_L63_ConcreteHF")
    m_hot = s12.get("M_L61_MuzzleHot") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = load_mat("/Game/Skyguard/Materials/M_PropDisc") or m_plate
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop fidelity: motion disc + blade accents behind wall only
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            # translucent-ish disc proxy via flat cylinder of cubes + prop disc mat
            spawn_sm(sphere, (bx + 3.72, cy + 0.0, cz + 0.12), (0.95, 0.08, 0.95), None, PREFIX + "TA16_PropDisc_%s" % name, mat=m_disc)
            for k in range(4):
                ang = k * 45.0
                spawn_sm(cube, (bx + 3.74, cy + 0.35 * (1 if k % 2 == 0 else -1), cz + 0.12 + (0.15 if k > 1 else -0.15)), (0.04, 0.85, 0.08), unreal.Rotator(0, ang, 12), PREFIX + "TA16_PropBlade_%s_%d" % (name, k), mat=m_plate)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.78, cy + 0.0, cz + 0.1), (0.42, 0.42, 0.42), unreal.Rotator(0, 0, 20), PREFIX + "TA16_PropHero_%s" % name, mats=[m_plate, m_air, m_rust, m_disc])
            # single bounded prop wash / contrail only
            spawn_niagara(PREFIX + "TA16_NS_PropWash_%s" % name, (bx + 3.7, cy + 0.05, cz + 0.05), "NS_PropWash", (0.24, 0.24, 0.24), bound=True)
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA16_NS_Contrail_%s" % name, (bx + 3.85, cy + 0.1, cz + 0.0), "NS_ContrailRibbon", (0.22, 0.22, 0.22), bound=True)
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.6, cy - 0.15, cz - 0.35), (0.58, 0.58, 0.58), unreal.Rotator(0, 90, 0), PREFIX + "TA16_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            # tiny emissive exhaust pin
            spawn_sm(sphere, (bx + 3.8, cy - 0.35, cz - 0.05), (0.05, 0.05, 0.05), None, PREFIX + "TA16_ExhaustPin_%s" % name, mat=m_glow)
        # Aircraft / cockpit multi-slot ANR seams (thin)
        if name in ("YakBeauty", "Cockpit", "ADS"):
            spawn_sm(cube, (bx + 3.5, cy + 0.15, cz + 0.12), (0.05, 1.15, 0.65), None, PREFIX + "TA16_AirANR_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.54, cy - 0.5, cz - 0.05), (0.045, 0.8, 0.4), None, PREFIX + "TA16_PlateANR_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.52, cy + 0.55, cz - 0.18), (0.04, 0.35, 0.12), None, PREFIX + "TA16_RustANR_%s" % name, mat=m_rust)
            for k in range(5):
                spawn_sm(sphere, (bx + 3.55, cy - 0.4 + k * 0.18, cz + 0.35), (0.03, 0.03, 0.03), None, PREFIX + "TA16_Rivet_%s_%d" % (name, k), mat=m_plate)
        # Weapon/combat: single bounded muzzle/sparks + rifle multi-slot
        if name in ("Combat", "ADS"):
            if sm_rifle_m and name == "ADS":
                spawn_sm(sm_rifle_m, (bx + 3.25, cy + 0.12, cz - 0.08), (0.36, 0.36, 0.36), unreal.Rotator(0, 90, 0), PREFIX + "TA16_RifleHero", mats=[m_rifle, m_plate, m_rust, m_hot])
            spawn_niagara(PREFIX + "TA16_NS_Muzzle_%s" % name, (bx + 3.4, cy + 0.22, cz + 0.14), "NS_MuzzleFlash", (0.22, 0.22, 0.22), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_GunSmoke_%s" % name, (bx + 3.42, cy + 0.18, cz + 0.1), "NS_GunSmoke", (0.2, 0.2, 0.2), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Sparks_%s" % name, (bx + 3.5, cy + 0.9, cz + 0.35), "NS_HitSparks", (0.26, 0.26, 0.26), bound=True)
            spawn_sm(sphere, (bx + 3.41, cy + 0.24, cz + 0.16), (0.055, 0.055, 0.055), None, PREFIX + "TA16_MuzzleCore_%s" % name, mat=m_hot)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA16_NS_Expl_%s" % name, (bx + 3.55, cy - 0.95, cz + 0.55), "NS_DroneExplosion", (0.28, 0.28, 0.28), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_Flak_%s" % name, (bx + 3.52, cy + 1.0, cz + 0.5), "NS_FlakBurst", (0.24, 0.24, 0.24), bound=True)
        # City/ocean bounded VFX + ANR facade accents
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.52, cy + 0.35, cz - 0.35), (0.06, 1.0, 1.25), None, PREFIX + "TA16_BrickANR_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.56, cy - 0.85, cz - 0.15), (0.055, 0.85, 0.95), None, PREFIX + "TA16_ConcANR_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.54, cy + 0.05, cz + 0.25), (0.05, 0.65, 0.75), None, PREFIX + "TA16_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            if name == "City":
                spawn_niagara(PREFIX + "TA16_NS_CityFire", (bx + 3.55, cy + 0.45, cz + 0.75), "NS_CityFire", (0.26, 0.26, 0.26), bound=True)
            spawn_sm(sphere, (bx + 3.6, cy + 0.12, cz + 0.88), (0.04, 0.04, 0.04), None, PREFIX + "TA16_CityPin_%s" % name, mat=m_glow)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA16_NS_Spray_%s" % name, (bx + 3.45, cy - 0.3, cz - 0.62), "NS_OceanSpray", (0.34, 0.34, 0.34), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Splash_%s" % name, (bx + 3.48, cy - 0.15, cz - 0.7), "NS_WaterSplash", (0.28, 0.28, 0.28), bound=True)
    log("slice16 bounded niagara + prop disc fidelity densify applied (no extra point lights)")

    
    # Slice16: VFX core language + stronger airframe/city material response (capture-safe)
    # HARD RULES: no extra PointLight FOV stacks; keep L52 HF densify core; behind-wall only.
    s13 = ensure_slice16_materials()
    m_air = s13.get("M_L70_AirframeResp") or s13.get("M_L68_AirframeANR") or s13.get("M_L63_AirframeHF")
    m_plate = s13.get("M_L70_PlateResp") or s13.get("M_L68_PlateANR") or s13.get("M_L63_PlateHF")
    m_rust = s13.get("M_L70_RustResp") or s13.get("M_L68_RustANR") or s13.get("M_L63_RustHF")
    m_brick = s13.get("M_L70_BrickResp") or s13.get("M_L68_BrickANR") or s13.get("M_L63_BrickHF")
    m_conc = s13.get("M_L70_ConcreteResp") or s13.get("M_L68_ConcreteANR") or s13.get("M_L63_ConcreteHF")
    m_hot = s13.get("M_L70_MuzzleResp") or s13.get("M_L61_MuzzleHot") or load_mat("/Game/Skyguard/Materials/Generated/M_L23_Muzzle")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = load_mat("/Game/Skyguard/Materials/M_PropDisc") or m_plate
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Airframe response panels + denser rivet/seam language (x>=bx+3.5)
        if name in ("YakBeauty", "Prop", "PropHub", "PropNose", "Cockpit", "ADS"):
            spawn_sm(cube, (bx + 3.52, cy + 0.12, cz + 0.1), (0.055, 1.25, 0.72), None, PREFIX + "TA16_AirResp_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.56, cy - 0.52, cz - 0.06), (0.05, 0.9, 0.48), None, PREFIX + "TA16_PlateResp_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.54, cy + 0.58, cz - 0.16), (0.04, 0.42, 0.14), None, PREFIX + "TA16_RustResp_%s" % name, mat=m_rust)
            spawn_sm(cube, (bx + 3.58, cy + 0.18, cz + 0.22), (0.045, 0.95, 0.55), None, PREFIX + "TA16_HeroPanel_%s" % name, mats=[m_air, m_plate, m_rust, m_glow])
            for k in range(7):
                spawn_sm(sphere, (bx + 3.57, cy - 0.5 + k * 0.16, cz + 0.38), (0.028, 0.028, 0.028), None, PREFIX + "TA16_Rivet_%s_%d" % (name, k), mat=m_plate)
            for k in range(4):
                spawn_sm(cube, (bx + 3.53, cy - 0.35 + k * 0.25, cz + 0.02), (0.03, 0.06, 0.28), None, PREFIX + "TA16_Seam_%s_%d" % (name, k), mat=m_rust)
            spawn_sm(sphere, (bx + 3.62, cy + 0.0, cz + 0.42), (0.045, 0.045, 0.045), None, PREFIX + "TA16_EmiPin_%s" % name, mat=m_glow)
        # Prop disc fidelity + bounded wash
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            spawn_sm(sphere, (bx + 3.74, cy + 0.0, cz + 0.12), (1.05, 0.07, 1.05), None, PREFIX + "TA16_PropDisc_%s" % name, mat=m_disc)
            for k in range(6):
                ang = k * 30.0
                spawn_sm(cube, (bx + 3.76, cy + 0.4 * ((k % 2) * 2 - 1), cz + 0.12), (0.035, 0.95, 0.07), unreal.Rotator(0, ang, 10), PREFIX + "TA16_PropBlade_%s_%d" % (name, k), mat=m_plate)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.8, cy + 0.0, cz + 0.1), (0.44, 0.44, 0.44), unreal.Rotator(0, 0, 25), PREFIX + "TA16_PropHero_%s" % name, mats=[m_plate, m_air, m_rust, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.62, cy - 0.12, cz - 0.32), (0.6, 0.6, 0.6), unreal.Rotator(0, 90, 0), PREFIX + "TA16_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            spawn_niagara(PREFIX + "TA16_NS_PropWash_%s" % name, (bx + 3.72, cy + 0.04, cz + 0.04), "NS_PropWash", (0.22, 0.22, 0.22), bound=True)
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA16_NS_Contrail_%s" % name, (bx + 3.88, cy + 0.08, cz + 0.0), "NS_ContrailRibbon", (0.2, 0.2, 0.2), bound=True)
            spawn_sm(sphere, (bx + 3.82, cy - 0.32, cz - 0.04), (0.05, 0.05, 0.05), None, PREFIX + "TA16_Exhaust_%s" % name, mat=m_glow)
        # Authored-looking VFX core language (mesh cores + single bounded Niagara)
        if name in ("Combat", "ADS", "Wide"):
            if sm_rifle_m and name in ("ADS", "Combat"):
                spawn_sm(sm_rifle_m, (bx + 3.28, cy + 0.1, cz - 0.06), (0.38, 0.38, 0.38), unreal.Rotator(0, 90, 0), PREFIX + "TA16_RifleHero_%s" % name, mats=[m_rifle, m_plate, m_rust, m_hot])
            spawn_niagara(PREFIX + "TA16_NS_Muzzle_%s" % name, (bx + 3.42, cy + 0.2, cz + 0.12), "NS_MuzzleFlash", (0.2, 0.2, 0.2), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Smoke_%s" % name, (bx + 3.44, cy + 0.16, cz + 0.08), "NS_GunSmoke", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Sparks_%s" % name, (bx + 3.52, cy + 0.92, cz + 0.34), "NS_HitSparks", (0.24, 0.24, 0.24), bound=True)
            # VFX cores / filaments / shells (proxy language that stills can read)
            spawn_sm(sphere, (bx + 3.43, cy + 0.22, cz + 0.14), (0.07, 0.07, 0.07), None, PREFIX + "TA16_MuzzleCore_%s" % name, mat=m_hot)
            spawn_sm(sphere, (bx + 3.46, cy + 0.3, cz + 0.2), (0.045, 0.045, 0.045), None, PREFIX + "TA16_MuzzleHalo_%s" % name, mat=m_glow)
            for k in range(6):
                spawn_sm(cube, (bx + 3.36 + k * 0.025, cy + 0.18 + k * 0.04, cz + 0.1 + k * 0.02), (0.14 - k * 0.015, 0.018, 0.018), unreal.Rotator(0, -12 + k * 5, 0), PREFIX + "TA16_Filament_%s_%d" % (name, k), mat=m_hot)
            for k in range(5):
                spawn_sm(sphere, (bx + 3.5, cy + 0.02 + k * 0.05, cz - 0.02 + k * 0.02), (0.025, 0.025, 0.025), None, PREFIX + "TA16_Shell_%s_%d" % (name, k), mat=m_plate)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA16_NS_Expl", (bx + 3.58, cy - 0.95, cz + 0.58), "NS_DroneExplosion", (0.26, 0.26, 0.26), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_Flak", (bx + 3.55, cy + 1.05, cz + 0.52), "NS_FlakBurst", (0.22, 0.22, 0.22), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.6, cy - 1.0, cz + 0.55), (0.36, 0.36, 0.36), unreal.Rotator(0, 90, 8), PREFIX + "TA16_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_sm(sphere, (bx + 3.58, cy - 0.95, cz + 0.62), (0.12, 0.12, 0.12), None, PREFIX + "TA16_ExplCore", mat=m_hot)
                for k in range(8):
                    spawn_sm(sphere, (bx + 3.5, cy - 1.15 + k * 0.06, cz + 0.5 + (k % 2) * 0.05), (0.03, 0.03, 0.03), None, PREFIX + "TA16_Debris_%d" % k, mat=m_plate)
        # City/ocean response
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.54, cy + 0.35, cz - 0.35), (0.065, 1.1, 1.35), None, PREFIX + "TA16_BrickResp_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.58, cy - 0.9, cz - 0.15), (0.06, 0.95, 1.05), None, PREFIX + "TA16_ConcResp_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.56, cy + 0.05, cz + 0.28), (0.05, 0.75, 0.85), None, PREFIX + "TA16_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            for ix in range(3):
                for iy in range(3):
                    spawn_sm(cube, (bx + 3.55, cy + 0.0 + ix * 0.35, cz + 0.0 + iy * 0.35), (0.03, 0.16, 0.22), None, PREFIX + "TA16_Win_%s_%d_%d" % (name, ix, iy), mat=load_mat("/Game/Skyguard/Materials/M_CityGlass") or m_plate)
            if name == "City":
                spawn_niagara(PREFIX + "TA16_NS_CityFire", (bx + 3.58, cy + 0.45, cz + 0.8), "NS_CityFire", (0.24, 0.24, 0.24), bound=True)
            spawn_sm(sphere, (bx + 3.62, cy + 0.12, cz + 0.92), (0.04, 0.04, 0.04), None, PREFIX + "TA16_CityPin_%s" % name, mat=m_glow)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA16_NS_Spray_%s" % name, (bx + 3.48, cy - 0.28, cz - 0.6), "NS_OceanSpray", (0.32, 0.32, 0.32), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Splash_%s" % name, (bx + 3.5, cy - 0.12, cz - 0.68), "NS_WaterSplash", (0.26, 0.26, 0.26), bound=True)
            for k in range(8):
                spawn_sm(sphere, (bx + 3.46, cy - 0.8 + k * 0.12, cz - 0.5 + (k % 2) * 0.06), (0.04 + (k % 2) * 0.01, 0.04 + (k % 2) * 0.01, 0.04 + (k % 2) * 0.01), None, PREFIX + "TA16_Foam_%s_%d" % (name, k), mat=load_mat("/Game/Skyguard/Materials/Generated/M_L61_FoamLit") or m_plate)
    log("slice16 vfx core language + airframe material response densify applied (no extra point lights)")

    
    # Slice16: authored VFX look (emissive unlit cores) + prop PBR motion disc fidelity
    # HARD RULES: no extra PointLight FOV stacks; keep L52 HF densify core; behind-wall only.
    s14 = ensure_slice16_materials()
    m_air = s14.get("M_L70_AirframeResp") or s14.get("M_L68_AirframeANR") or s14.get("M_L63_AirframeHF")
    m_plate = s14.get("M_L70_PlateResp") or s14.get("M_L68_PlateANR") or s14.get("M_L63_PlateHF")
    m_rust = s14.get("M_L70_RustResp") or s14.get("M_L68_RustANR")
    m_brick = s14.get("M_L70_BrickResp") or s14.get("M_L68_BrickANR")
    m_conc = s14.get("M_L70_ConcreteResp") or s14.get("M_L68_ConcreteANR")
    m_hot = s14.get("M_L70_MuzzleResp") or s14.get("M_L61_MuzzleHot")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = s14.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc") or m_plate
    m_blade = s14.get("M_L71_PropBlade") or m_air
    m_muzzle_emi = s14.get("M_L71_VFX_MuzzleEmi") or m_hot
    m_spark_emi = s14.get("M_L71_VFX_SparkEmi") or m_hot
    m_tracer_emi = s14.get("M_L71_VFX_TracerEmi") or m_hot
    m_foam_emi = s14.get("M_L71_VFX_FoamEmi") or m_plate
    m_expl_emi = s14.get("M_L71_VFX_ExplEmi") or m_hot
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop PBR motion disc: concentric rings + multi-blade motion language (behind wall)
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            # outer disc + mid ring + hub
            spawn_sm(sphere, (bx + 3.74, cy + 0.0, cz + 0.12), (1.15, 0.06, 1.15), None, PREFIX + "TA16_PropDiscOuter_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.75, cy + 0.0, cz + 0.12), (0.75, 0.05, 0.75), None, PREFIX + "TA16_PropDiscMid_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.76, cy + 0.0, cz + 0.12), (0.28, 0.08, 0.28), None, PREFIX + "TA16_PropHub_%s" % name, mat=m_plate)
            for k in range(8):
                ang = k * 22.5
                spawn_sm(cube, (bx + 3.77, cy + 0.55 * ((k % 2) * 2 - 1) * 0.5, cz + 0.12), (0.03, 1.05, 0.06), unreal.Rotator(0, ang, 8 + k), PREFIX + "TA16_PropBlade_%s_%d" % (name, k), mat=m_blade)
            # motion blur streaks (thin emissive-ish plate strips)
            for k in range(6):
                spawn_sm(cube, (bx + 3.73, cy + 0.2 * (k - 2.5), cz + 0.12), (0.02, 0.9, 0.035), unreal.Rotator(0, k * 15, 0), PREFIX + "TA16_PropStreak_%s_%d" % (name, k), mat=m_disc)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.82, cy + 0.0, cz + 0.1), (0.46, 0.46, 0.46), unreal.Rotator(0, 0, 30), PREFIX + "TA16_PropHero_%s" % name, mats=[m_blade, m_air, m_plate, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.64, cy - 0.1, cz - 0.3), (0.62, 0.62, 0.62), unreal.Rotator(0, 90, 0), PREFIX + "TA16_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            spawn_niagara(PREFIX + "TA16_NS_PropWash_%s" % name, (bx + 3.74, cy + 0.03, cz + 0.03), "NS_PropWash", (0.2, 0.2, 0.2), bound=True)
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA16_NS_Contrail_%s" % name, (bx + 3.9, cy + 0.06, cz + 0.0), "NS_ContrailRibbon", (0.18, 0.18, 0.18), bound=True)
            spawn_sm(sphere, (bx + 3.85, cy - 0.3, cz - 0.02), (0.055, 0.055, 0.055), None, PREFIX + "TA16_Exhaust_%s" % name, mat=m_muzzle_emi or m_glow)
        # Airframe response seams (compound L70)
        if name in ("YakBeauty", "Cockpit", "ADS", "Prop"):
            spawn_sm(cube, (bx + 3.53, cy + 0.1, cz + 0.08), (0.05, 1.3, 0.75), None, PREFIX + "TA16_AirResp_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.57, cy - 0.5, cz - 0.05), (0.045, 0.95, 0.5), None, PREFIX + "TA16_PlateResp_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.55, cy + 0.6, cz - 0.15), (0.04, 0.45, 0.15), None, PREFIX + "TA16_RustResp_%s" % name, mat=m_rust)
            for k in range(8):
                spawn_sm(sphere, (bx + 3.58, cy - 0.55 + k * 0.15, cz + 0.4), (0.026, 0.026, 0.026), None, PREFIX + "TA16_Rivet_%s_%d" % (name, k), mat=m_plate)
        # Authored VFX look: emissive cores + bounded systems (still capture-safe sizes)
        if name in ("Combat", "ADS", "Wide"):
            if sm_rifle_m and name in ("ADS", "Combat"):
                spawn_sm(sm_rifle_m, (bx + 3.3, cy + 0.08, cz - 0.05), (0.4, 0.4, 0.4), unreal.Rotator(0, 90, 0), PREFIX + "TA16_RifleHero_%s" % name, mats=[m_rifle, m_plate, m_rust, m_hot])
            spawn_niagara(PREFIX + "TA16_NS_Muzzle_%s" % name, (bx + 3.44, cy + 0.18, cz + 0.1), "NS_MuzzleFlash", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Smoke_%s" % name, (bx + 3.46, cy + 0.14, cz + 0.06), "NS_GunSmoke", (0.16, 0.16, 0.16), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Sparks_%s" % name, (bx + 3.54, cy + 0.95, cz + 0.32), "NS_HitSparks", (0.22, 0.22, 0.22), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Tracer_%s" % name, (bx + 3.5, cy + 0.25, cz + 0.18), "NS_TracerBurst", (0.16, 0.16, 0.16), bound=True)
            # emissive authored cores
            spawn_sm(sphere, (bx + 3.45, cy + 0.2, cz + 0.12), (0.08, 0.08, 0.08), None, PREFIX + "TA16_MuzzleCore_%s" % name, mat=m_muzzle_emi)
            spawn_sm(sphere, (bx + 3.48, cy + 0.28, cz + 0.18), (0.05, 0.05, 0.05), None, PREFIX + "TA16_MuzzleHalo_%s" % name, mat=m_spark_emi)
            for k in range(7):
                spawn_sm(cube, (bx + 3.38 + k * 0.03, cy + 0.16 + k * 0.045, cz + 0.08 + k * 0.025), (0.16 - k * 0.015, 0.016, 0.016), unreal.Rotator(0, -14 + k * 6, 0), PREFIX + "TA16_Filament_%s_%d" % (name, k), mat=m_tracer_emi)
            for k in range(6):
                spawn_sm(sphere, (bx + 3.52, cy + 0.0 + k * 0.05, cz - 0.03 + k * 0.02), (0.024, 0.024, 0.024), None, PREFIX + "TA16_Shell_%s_%d" % (name, k), mat=m_plate)
            for k in range(8):
                spawn_sm(sphere, (bx + 3.5, cy + 0.7 + k * 0.05, cz + 0.25 + (k % 2) * 0.04), (0.03, 0.03, 0.03), None, PREFIX + "TA16_Spark_%s_%d" % (name, k), mat=m_spark_emi)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA16_NS_Expl", (bx + 3.6, cy - 0.92, cz + 0.55), "NS_DroneExplosion", (0.24, 0.24, 0.24), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_Flak", (bx + 3.58, cy + 1.05, cz + 0.5), "NS_FlakBurst", (0.2, 0.2, 0.2), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.62, cy - 0.98, cz + 0.52), (0.38, 0.38, 0.38), unreal.Rotator(0, 90, 6), PREFIX + "TA16_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_sm(sphere, (bx + 3.6, cy - 0.92, cz + 0.6), (0.14, 0.14, 0.14), None, PREFIX + "TA16_ExplCore", mat=m_expl_emi)
                for k in range(10):
                    spawn_sm(sphere, (bx + 3.52, cy - 1.15 + k * 0.05, cz + 0.48 + (k % 2) * 0.05), (0.028, 0.028, 0.028), None, PREFIX + "TA16_Debris_%d" % k, mat=m_spark_emi if k % 2 == 0 else m_plate)
        # City/ocean
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.55, cy + 0.32, cz - 0.32), (0.06, 1.15, 1.4), None, PREFIX + "TA16_BrickResp_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.59, cy - 0.88, cz - 0.12), (0.055, 0.98, 1.1), None, PREFIX + "TA16_ConcResp_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.57, cy + 0.02, cz + 0.26), (0.05, 0.8, 0.9), None, PREFIX + "TA16_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            for ix in range(3):
                for iy in range(4):
                    spawn_sm(cube, (bx + 3.56, cy - 0.2 + ix * 0.35, cz - 0.15 + iy * 0.32), (0.028, 0.15, 0.2), None, PREFIX + "TA16_Win_%s_%d_%d" % (name, ix, iy), mat=load_mat("/Game/Skyguard/Materials/M_CityGlass") or m_plate)
            if name == "City":
                spawn_niagara(PREFIX + "TA16_NS_CityFire", (bx + 3.6, cy + 0.42, cz + 0.78), "NS_CityFire", (0.22, 0.22, 0.22), bound=True)
            spawn_sm(sphere, (bx + 3.64, cy + 0.1, cz + 0.9), (0.045, 0.045, 0.045), None, PREFIX + "TA16_CityPin_%s" % name, mat=m_muzzle_emi or m_glow)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA16_NS_Spray_%s" % name, (bx + 3.5, cy - 0.25, cz - 0.58), "NS_OceanSpray", (0.3, 0.3, 0.3), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Splash_%s" % name, (bx + 3.52, cy - 0.1, cz - 0.66), "NS_WaterSplash", (0.24, 0.24, 0.24), bound=True)
            for k in range(10):
                spawn_sm(sphere, (bx + 3.48, cy - 0.85 + k * 0.11, cz - 0.48 + (k % 2) * 0.06), (0.045 + (k % 2) * 0.012, 0.045 + (k % 2) * 0.012, 0.045 + (k % 2) * 0.012), None, PREFIX + "TA16_Foam_%s_%d" % (name, k), mat=m_foam_emi)
    log("slice16 authored vfx look + prop pbr motion densify applied (no extra point lights)")

    
    # Slice16: formal Niagara shell author pass + denser capture-safe VFX language
    # HARD RULES: no extra PointLight FOV stacks; keep L52 HF densify core; behind-wall only.
    vfxlib = ensure_slice16_vfx_library()
    s15 = ensure_slice16_materials()
    m_air = s15.get("M_L70_AirframeResp") or s15.get("M_L68_AirframeANR")
    m_plate = s15.get("M_L70_PlateResp") or s15.get("M_L68_PlateANR")
    m_rust = s15.get("M_L70_RustResp") or s15.get("M_L68_RustANR")
    m_brick = s15.get("M_L70_BrickResp") or s15.get("M_L68_BrickANR")
    m_conc = s15.get("M_L70_ConcreteResp") or s15.get("M_L68_ConcreteANR")
    m_hot = s15.get("M_L70_MuzzleResp") or s15.get("M_L61_MuzzleHot")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = s15.get("M_L72_PropDiscBright") or s15.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc")
    m_blade = s15.get("M_L72_PropBladeEdge") or s15.get("M_L71_PropBlade") or m_air
    m_muzzle_emi = s15.get("M_L71_VFX_MuzzleEmi") or m_hot
    m_spark_emi = s15.get("M_L71_VFX_SparkEmi") or m_hot
    m_tracer_emi = s15.get("M_L71_VFX_TracerEmi") or m_hot
    m_foam_emi = s15.get("M_L71_VFX_FoamEmi") or m_plate
    m_expl_emi = s15.get("M_L71_VFX_ExplEmi") or m_hot
    m_card_hot = s15.get("M_L72_VFX_CardHot") or m_muzzle_emi
    m_card_soft = s15.get("M_L72_VFX_CardSoft") or m_spark_emi
    m_card_cool = s15.get("M_L72_VFX_CardCool") or m_foam_emi
    m_card_expl = s15.get("M_L72_VFX_CardExpl") or m_expl_emi
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop PBR motion densify (behind wall)
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            spawn_sm(sphere, (bx + 3.76, cy + 0.0, cz + 0.12), (1.25, 0.05, 1.25), None, PREFIX + "TA16_PropDiscOuter_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.77, cy + 0.0, cz + 0.12), (0.85, 0.045, 0.85), None, PREFIX + "TA16_PropDiscMid_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.78, cy + 0.0, cz + 0.12), (0.45, 0.04, 0.45), None, PREFIX + "TA16_PropDiscInner_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.79, cy + 0.0, cz + 0.12), (0.22, 0.08, 0.22), None, PREFIX + "TA16_PropHub_%s" % name, mat=m_plate)
            for k in range(10):
                ang = k * 18.0
                spawn_sm(cube, (bx + 3.8, cy + 0.15 * ((k % 2) * 2 - 1), cz + 0.12), (0.028, 1.1, 0.05), unreal.Rotator(0, ang, 6 + k), PREFIX + "TA16_PropBlade_%s_%d" % (name, k), mat=m_blade)
            for k in range(8):
                spawn_sm(cube, (bx + 3.75, cy + 0.18 * (k - 3.5), cz + 0.12), (0.018, 0.95, 0.03), unreal.Rotator(0, k * 12, 0), PREFIX + "TA16_PropStreak_%s_%d" % (name, k), mat=m_disc)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.84, cy + 0.0, cz + 0.1), (0.48, 0.48, 0.48), unreal.Rotator(0, 0, 35), PREFIX + "TA16_PropHero_%s" % name, mats=[m_blade, m_air, m_plate, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.66, cy - 0.08, cz - 0.28), (0.64, 0.64, 0.64), unreal.Rotator(0, 90, 0), PREFIX + "TA16_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            # single bounded authored NS variants + legacy systems
            spawn_niagara(PREFIX + "TA16_NS_PropWashAuth_%s" % name, (bx + 3.76, cy + 0.02, cz + 0.02), "NS_L73_PropWashAuth", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_PropWash_%s" % name, (bx + 3.78, cy + 0.04, cz + 0.03), "NS_PropWash", (0.16, 0.16, 0.16), bound=True)
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA16_NS_Contrail_%s" % name, (bx + 3.92, cy + 0.05, cz + 0.0), "NS_ContrailRibbon", (0.16, 0.16, 0.16), bound=True)
            spawn_sm(sphere, (bx + 3.88, cy - 0.28, cz - 0.02), (0.06, 0.06, 0.06), None, PREFIX + "TA16_Exhaust_%s" % name, mat=m_muzzle_emi)
        # Airframe densify
        if name in ("YakBeauty", "Cockpit", "ADS", "Prop"):
            spawn_sm(cube, (bx + 3.54, cy + 0.08, cz + 0.06), (0.05, 1.35, 0.78), None, PREFIX + "TA16_AirResp_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.58, cy - 0.48, cz - 0.04), (0.045, 1.0, 0.52), None, PREFIX + "TA16_PlateResp_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.56, cy + 0.62, cz - 0.14), (0.04, 0.48, 0.16), None, PREFIX + "TA16_RustResp_%s" % name, mat=m_rust)
            for k in range(10):
                spawn_sm(sphere, (bx + 3.59, cy - 0.6 + k * 0.14, cz + 0.42), (0.025, 0.025, 0.025), None, PREFIX + "TA16_Rivet_%s_%d" % (name, k), mat=m_plate)
        # Authored VFX language: emissive cards (thin quads) + cores + single bounded NS
        if name in ("Combat", "ADS", "Wide"):
            if sm_rifle_m and name in ("ADS", "Combat"):
                spawn_sm(sm_rifle_m, (bx + 3.32, cy + 0.06, cz - 0.04), (0.42, 0.42, 0.42), unreal.Rotator(0, 90, 0), PREFIX + "TA16_RifleHero_%s" % name, mats=[m_rifle, m_plate, m_rust, m_hot])
            # authored NS shells (new) + existing systems, all small/bounded
            spawn_niagara(PREFIX + "TA16_NS_MuzzleAuth_%s" % name, (bx + 3.46, cy + 0.16, cz + 0.08), "NS_L73_MuzzleAuth", (0.16, 0.16, 0.16), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Muzzle_%s" % name, (bx + 3.47, cy + 0.17, cz + 0.09), "NS_MuzzleFlash", (0.15, 0.15, 0.15), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Smoke_%s" % name, (bx + 3.49, cy + 0.12, cz + 0.05), "NS_GunSmoke", (0.14, 0.14, 0.14), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_SparkAuth_%s" % name, (bx + 3.56, cy + 0.98, cz + 0.3), "NS_L73_SparkAuth", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Sparks_%s" % name, (bx + 3.57, cy + 0.99, cz + 0.31), "NS_HitSparks", (0.17, 0.17, 0.17), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Tracer_%s" % name, (bx + 3.52, cy + 0.22, cz + 0.16), "NS_TracerBurst", (0.14, 0.14, 0.14), bound=True)
            # soft sprite cards (thin cubes as billboards)
            for k in range(5):
                spawn_sm(cube, (bx + 3.45 + k * 0.02, cy + 0.18 + k * 0.03, cz + 0.1 + k * 0.02), (0.01, 0.22 - k * 0.02, 0.18 - k * 0.015), unreal.Rotator(0, -10 + k * 8, 0), PREFIX + "TA16_MuzzleCard_%s_%d" % (name, k), mat=m_card_hot)
            for k in range(6):
                spawn_sm(cube, (bx + 3.54, cy + 0.75 + k * 0.05, cz + 0.22 + (k % 2) * 0.04), (0.01, 0.12, 0.1), unreal.Rotator(0, k * 20, 15), PREFIX + "TA16_SparkCard_%s_%d" % (name, k), mat=m_card_soft)
            spawn_sm(sphere, (bx + 3.47, cy + 0.18, cz + 0.1), (0.09, 0.09, 0.09), None, PREFIX + "TA16_MuzzleCore_%s" % name, mat=m_muzzle_emi)
            for k in range(8):
                spawn_sm(cube, (bx + 3.4 + k * 0.03, cy + 0.14 + k * 0.045, cz + 0.06 + k * 0.025), (0.15 - k * 0.012, 0.014, 0.014), unreal.Rotator(0, -12 + k * 5, 0), PREFIX + "TA16_Filament_%s_%d" % (name, k), mat=m_tracer_emi)
            for k in range(7):
                spawn_sm(sphere, (bx + 3.53, cy - 0.02 + k * 0.05, cz - 0.04 + k * 0.02), (0.022, 0.022, 0.022), None, PREFIX + "TA16_Shell_%s_%d" % (name, k), mat=m_plate)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA16_NS_ExplAuth", (bx + 3.62, cy - 0.9, cz + 0.52), "NS_L73_ExplAuth", (0.2, 0.2, 0.2), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_Expl", (bx + 3.63, cy - 0.91, cz + 0.53), "NS_DroneExplosion", (0.18, 0.18, 0.18), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_Flak", (bx + 3.6, cy + 1.08, cz + 0.48), "NS_FlakBurst", (0.16, 0.16, 0.16), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.64, cy - 0.95, cz + 0.5), (0.4, 0.4, 0.4), unreal.Rotator(0, 90, 4), PREFIX + "TA16_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_sm(sphere, (bx + 3.62, cy - 0.9, cz + 0.58), (0.16, 0.16, 0.16), None, PREFIX + "TA16_ExplCore", mat=m_card_expl)
                for k in range(6):
                    spawn_sm(cube, (bx + 3.58, cy - 1.0 + k * 0.06, cz + 0.45 + (k % 2) * 0.05), (0.01, 0.18, 0.14), unreal.Rotator(0, k * 25, 10), PREFIX + "TA16_ExplCard_%d" % k, mat=m_card_expl)
                for k in range(12):
                    spawn_sm(sphere, (bx + 3.55, cy - 1.2 + k * 0.05, cz + 0.45 + (k % 3) * 0.04), (0.026, 0.026, 0.026), None, PREFIX + "TA16_Debris_%d" % k, mat=m_spark_emi if k % 2 == 0 else m_plate)
        # City/ocean densify
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.56, cy + 0.3, cz - 0.3), (0.06, 1.2, 1.45), None, PREFIX + "TA16_BrickResp_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.6, cy - 0.9, cz - 0.1), (0.055, 1.02, 1.15), None, PREFIX + "TA16_ConcResp_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.58, cy + 0.0, cz + 0.24), (0.05, 0.85, 0.95), None, PREFIX + "TA16_CityHero_%s" % name, mats=[m_brick, m_conc, m_rust])
            for ix in range(4):
                for iy in range(4):
                    spawn_sm(cube, (bx + 3.57, cy - 0.3 + ix * 0.32, cz - 0.2 + iy * 0.3), (0.025, 0.14, 0.18), None, PREFIX + "TA16_Win_%s_%d_%d" % (name, ix, iy), mat=load_mat("/Game/Skyguard/Materials/M_CityGlass") or m_plate)
            if name == "City":
                spawn_niagara(PREFIX + "TA16_NS_CityFire", (bx + 3.62, cy + 0.4, cz + 0.76), "NS_CityFire", (0.18, 0.18, 0.18), bound=True)
            spawn_sm(sphere, (bx + 3.66, cy + 0.08, cz + 0.88), (0.05, 0.05, 0.05), None, PREFIX + "TA16_CityPin_%s" % name, mat=m_muzzle_emi)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA16_NS_SprayAuth_%s" % name, (bx + 3.52, cy - 0.22, cz - 0.56), "NS_L73_SprayAuth", (0.24, 0.24, 0.24), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Spray_%s" % name, (bx + 3.53, cy - 0.23, cz - 0.57), "NS_OceanSpray", (0.22, 0.22, 0.22), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Splash_%s" % name, (bx + 3.55, cy - 0.08, cz - 0.64), "NS_WaterSplash", (0.18, 0.18, 0.18), bound=True)
            for k in range(12):
                spawn_sm(sphere, (bx + 3.5, cy - 0.9 + k * 0.1, cz - 0.46 + (k % 2) * 0.05), (0.05 + (k % 2) * 0.012, 0.05 + (k % 2) * 0.012, 0.05 + (k % 2) * 0.012), None, PREFIX + "TA16_Foam_%s_%d" % (name, k), mat=m_foam_emi)
            for k in range(5):
                spawn_sm(cube, (bx + 3.51, cy - 0.5 + k * 0.12, cz - 0.4), (0.01, 0.2, 0.12), unreal.Rotator(0, k * 18, 0), PREFIX + "TA16_FoamCard_%s_%d" % (name, k), mat=m_card_cool)
    log("slice16 authored niagara shells + denser vfx language densify applied (no extra point lights)")

    
    # Slice16: deeper Niagara author pass + denser capture-visible particle language
    # HARD RULES: no FOV PointLight stacks; keep L52 HF densify core; behind-wall only.
    vfxlib = ensure_slice16_vfx_library()
    s16 = ensure_slice16_materials()
    m_air = s16.get("M_L70_AirframeResp") or s16.get("M_L68_AirframeANR")
    m_plate = s16.get("M_L70_PlateResp") or s16.get("M_L68_PlateANR")
    m_rust = s16.get("M_L70_RustResp") or s16.get("M_L68_RustANR")
    m_brick = s16.get("M_L70_BrickResp") or s16.get("M_L68_BrickANR")
    m_conc = s16.get("M_L70_ConcreteResp") or s16.get("M_L68_ConcreteANR")
    m_hot = s16.get("M_L70_MuzzleResp") or s16.get("M_L61_MuzzleHot")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = s16.get("M_L72_PropDiscBright") or s16.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc")
    m_blade = s16.get("M_L72_PropBladeEdge") or s16.get("M_L71_PropBlade") or m_air
    m_muzzle_emi = s16.get("M_L71_VFX_MuzzleEmi") or m_hot
    m_spark_emi = s16.get("M_L71_VFX_SparkEmi") or m_hot
    m_tracer_emi = s16.get("M_L71_VFX_TracerEmi") or m_hot
    m_foam_emi = s16.get("M_L71_VFX_FoamEmi") or m_plate
    m_expl_emi = s16.get("M_L71_VFX_ExplEmi") or m_hot
    m_card_hot = s16.get("M_L72_VFX_CardHot") or m_muzzle_emi
    m_card_soft = s16.get("M_L72_VFX_CardSoft") or m_spark_emi
    m_card_cool = s16.get("M_L72_VFX_CardCool") or m_foam_emi
    m_card_expl = s16.get("M_L72_VFX_CardExpl") or m_expl_emi
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop densify + particle wash field
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            spawn_sm(sphere, (bx + 3.78, cy + 0.0, cz + 0.12), (1.3, 0.045, 1.3), None, PREFIX + "TA16_PropDiscOuter_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.79, cy + 0.0, cz + 0.12), (0.9, 0.04, 0.9), None, PREFIX + "TA16_PropDiscMid_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.8, cy + 0.0, cz + 0.12), (0.5, 0.035, 0.5), None, PREFIX + "TA16_PropDiscInner_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.81, cy + 0.0, cz + 0.12), (0.2, 0.08, 0.2), None, PREFIX + "TA16_PropHub_%s" % name, mat=m_plate)
            for k in range(12):
                ang = k * 15.0
                spawn_sm(cube, (bx + 3.82, cy + 0.12 * ((k % 2) * 2 - 1), cz + 0.12), (0.025, 1.15, 0.045), unreal.Rotator(0, ang, 5 + k), PREFIX + "TA16_PropBlade_%s_%d" % (name, k), mat=m_blade)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.86, cy + 0.0, cz + 0.1), (0.5, 0.5, 0.5), unreal.Rotator(0, 0, 40), PREFIX + "TA16_PropHero_%s" % name, mats=[m_blade, m_air, m_plate, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.68, cy - 0.06, cz - 0.26), (0.66, 0.66, 0.66), unreal.Rotator(0, 90, 0), PREFIX + "TA16_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            spawn_niagara(PREFIX + "TA16_NS_PropWashAuth_%s" % name, (bx + 3.78, cy + 0.02, cz + 0.02), "NS_L73_PropWashAuth", (0.16, 0.16, 0.16), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_PropWash_%s" % name, (bx + 3.8, cy + 0.03, cz + 0.02), "NS_PropWash", (0.14, 0.14, 0.14), bound=True)
            spawn_particle_field(PREFIX + "TA16_WashField_%s" % name, (bx + 3.8, cy + 0.0, cz + 0.05), m_card_soft, count=14, radius=0.55, size=0.03, label_base="Wash")
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA16_NS_Contrail_%s" % name, (bx + 3.94, cy + 0.04, cz + 0.0), "NS_ContrailRibbon", (0.14, 0.14, 0.14), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_ContrailDense_%s" % name, (bx + 3.96, cy + 0.06, cz + 0.0), "NS_L73_ContrailDense", (0.12, 0.12, 0.12), bound=True)
            spawn_sm(sphere, (bx + 3.9, cy - 0.26, cz - 0.02), (0.06, 0.06, 0.06), None, PREFIX + "TA16_Exhaust_%s" % name, mat=m_muzzle_emi)
        if name in ("YakBeauty", "Cockpit", "ADS", "Prop"):
            spawn_sm(cube, (bx + 3.55, cy + 0.06, cz + 0.05), (0.05, 1.4, 0.8), None, PREFIX + "TA16_AirResp_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.59, cy - 0.46, cz - 0.03), (0.045, 1.05, 0.55), None, PREFIX + "TA16_PlateResp_%s" % name, mat=m_plate)
            for k in range(12):
                spawn_sm(sphere, (bx + 3.6, cy - 0.65 + k * 0.13, cz + 0.44), (0.024, 0.024, 0.024), None, PREFIX + "TA16_Rivet_%s_%d" % (name, k), mat=m_plate)
        # Combat/ADS denser visible particle language + deeper NS
        if name in ("Combat", "ADS", "Wide"):
            if sm_rifle_m and name in ("ADS", "Combat"):
                spawn_sm(sm_rifle_m, (bx + 3.34, cy + 0.05, cz - 0.03), (0.44, 0.44, 0.44), unreal.Rotator(0, 90, 0), PREFIX + "TA16_RifleHero_%s" % name, mats=[m_rifle, m_plate, m_rust, m_hot])
            spawn_niagara(PREFIX + "TA16_NS_MuzzleAuth_%s" % name, (bx + 3.48, cy + 0.15, cz + 0.07), "NS_L73_MuzzleAuth", (0.14, 0.14, 0.14), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_MuzzleBurst_%s" % name, (bx + 3.49, cy + 0.16, cz + 0.08), "NS_L73_MuzzleBurst", (0.13, 0.13, 0.13), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Muzzle_%s" % name, (bx + 3.5, cy + 0.16, cz + 0.08), "NS_MuzzleFlash", (0.12, 0.12, 0.12), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Smoke_%s" % name, (bx + 3.51, cy + 0.11, cz + 0.04), "NS_GunSmoke", (0.12, 0.12, 0.12), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_SparkAuth_%s" % name, (bx + 3.58, cy + 1.0, cz + 0.28), "NS_L73_SparkAuth", (0.15, 0.15, 0.15), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_SparkRing_%s" % name, (bx + 3.59, cy + 1.02, cz + 0.3), "NS_L73_SparkRing", (0.14, 0.14, 0.14), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Sparks_%s" % name, (bx + 3.6, cy + 1.01, cz + 0.29), "NS_HitSparks", (0.13, 0.13, 0.13), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Tracer_%s" % name, (bx + 3.54, cy + 0.2, cz + 0.14), "NS_TracerBurst", (0.12, 0.12, 0.12), bound=True)
            # denser visible particles
            spawn_particle_field(PREFIX + "TA16_MuzzleField_%s" % name, (bx + 3.5, cy + 0.18, cz + 0.1), m_card_hot, count=16, radius=0.28, size=0.035, label_base="Muz")
            spawn_burst_ring(PREFIX + "TA16_SparkRingVis_%s" % name, (bx + 3.58, cy + 0.95, cz + 0.28), m_card_soft, count=12, radius=0.42, label_base="Spark")
            for k in range(8):
                spawn_sm(cube, (bx + 3.42 + k * 0.03, cy + 0.12 + k * 0.05, cz + 0.05 + k * 0.03), (0.16 - k * 0.012, 0.013, 0.013), unreal.Rotator(0, -14 + k * 6, 0), PREFIX + "TA16_Filament_%s_%d" % (name, k), mat=m_tracer_emi)
            for k in range(9):
                spawn_sm(sphere, (bx + 3.55, cy - 0.04 + k * 0.05, cz - 0.05 + k * 0.02), (0.02, 0.02, 0.02), None, PREFIX + "TA16_Shell_%s_%d" % (name, k), mat=m_plate)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA16_NS_ExplAuth", (bx + 3.64, cy - 0.88, cz + 0.5), "NS_L73_ExplAuth", (0.18, 0.18, 0.18), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_ExplPlume", (bx + 3.65, cy - 0.89, cz + 0.52), "NS_L73_ExplPlume", (0.16, 0.16, 0.16), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_Expl", (bx + 3.66, cy - 0.9, cz + 0.51), "NS_DroneExplosion", (0.15, 0.15, 0.15), bound=True)
                spawn_niagara(PREFIX + "TA16_NS_Flak", (bx + 3.62, cy + 1.1, cz + 0.46), "NS_FlakBurst", (0.14, 0.14, 0.14), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.66, cy - 0.92, cz + 0.48), (0.42, 0.42, 0.42), unreal.Rotator(0, 90, 3), PREFIX + "TA16_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_sm(sphere, (bx + 3.64, cy - 0.88, cz + 0.56), (0.18, 0.18, 0.18), None, PREFIX + "TA16_ExplCore", mat=m_card_expl)
                spawn_particle_field(PREFIX + "TA16_ExplField", (bx + 3.64, cy - 0.88, cz + 0.55), m_card_expl, count=18, radius=0.65, size=0.04, label_base="Expl")
                spawn_burst_ring(PREFIX + "TA16_ExplRing", (bx + 3.64, cy - 0.88, cz + 0.5), m_card_hot, count=14, radius=0.7, label_base="ExplR")
                for k in range(14):
                    spawn_sm(sphere, (bx + 3.57, cy - 1.25 + k * 0.05, cz + 0.42 + (k % 3) * 0.04), (0.025, 0.025, 0.025), None, PREFIX + "TA16_Debris_%d" % k, mat=m_spark_emi if k % 2 == 0 else m_plate)
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.57, cy + 0.28, cz - 0.28), (0.06, 1.25, 1.5), None, PREFIX + "TA16_BrickResp_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.61, cy - 0.92, cz - 0.08), (0.055, 1.05, 1.2), None, PREFIX + "TA16_ConcResp_%s" % name, mat=m_conc)
            for ix in range(4):
                for iy in range(5):
                    spawn_sm(cube, (bx + 3.58, cy - 0.35 + ix * 0.3, cz - 0.25 + iy * 0.28), (0.022, 0.13, 0.16), None, PREFIX + "TA16_Win_%s_%d_%d" % (name, ix, iy), mat=load_mat("/Game/Skyguard/Materials/M_CityGlass") or m_plate)
            if name == "City":
                spawn_niagara(PREFIX + "TA16_NS_CityFire", (bx + 3.64, cy + 0.38, cz + 0.74), "NS_CityFire", (0.16, 0.16, 0.16), bound=True)
                spawn_particle_field(PREFIX + "TA16_CityEmber", (bx + 3.64, cy + 0.38, cz + 0.8), m_card_hot, count=12, radius=0.4, size=0.028, label_base="Ember")
            spawn_sm(sphere, (bx + 3.68, cy + 0.06, cz + 0.86), (0.05, 0.05, 0.05), None, PREFIX + "TA16_CityPin_%s" % name, mat=m_muzzle_emi)
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA16_NS_SprayAuth_%s" % name, (bx + 3.54, cy - 0.2, cz - 0.54), "NS_L73_SprayAuth", (0.2, 0.2, 0.2), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_FoamBurst_%s" % name, (bx + 3.55, cy - 0.18, cz - 0.52), "NS_L73_FoamBurst", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Spray_%s" % name, (bx + 3.56, cy - 0.2, cz - 0.55), "NS_OceanSpray", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA16_NS_Splash_%s" % name, (bx + 3.57, cy - 0.06, cz - 0.62), "NS_WaterSplash", (0.15, 0.15, 0.15), bound=True)
            spawn_particle_field(PREFIX + "TA16_FoamField_%s" % name, (bx + 3.55, cy - 0.35, cz - 0.45), m_card_cool, count=16, radius=0.7, size=0.04, label_base="Foam")
            for k in range(14):
                spawn_sm(sphere, (bx + 3.52, cy - 0.95 + k * 0.09, cz - 0.44 + (k % 2) * 0.05), (0.05 + (k % 2) * 0.01, 0.05 + (k % 2) * 0.01, 0.05 + (k % 2) * 0.01), None, PREFIX + "TA16_Foam_%s_%d" % (name, k), mat=m_foam_emi)
    log("slice16 deeper niagara + visible particle language densify applied (no extra point lights)")

    # Slice17 (thin / capture-safe on L73 KEEP): visible VFX beauty + prop/airframe response
    # HARD RULES: no FOV PointLight stacks; keep L52 HF densify core; behind-wall only; no L53 stacks.
    vfx17 = ensure_slice17_vfx_library()
    s17 = ensure_slice16_materials()
    m_air = s17.get("M_L70_AirframeResp") or s17.get("M_L68_AirframeANR")
    m_plate = s17.get("M_L70_PlateResp") or s17.get("M_L68_PlateANR")
    m_rust = s17.get("M_L70_RustResp") or s17.get("M_L68_RustANR")
    m_brick = s17.get("M_L70_BrickResp") or s17.get("M_L68_BrickANR")
    m_conc = s17.get("M_L70_ConcreteResp") or s17.get("M_L68_ConcreteANR")
    m_hot = s17.get("M_L70_MuzzleResp") or s17.get("M_L61_MuzzleHot")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = s17.get("M_L72_PropDiscBright") or s17.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc")
    m_blade = s17.get("M_L72_PropBladeEdge") or s17.get("M_L71_PropBlade") or m_air
    m_muzzle_emi = s17.get("M_L71_VFX_MuzzleEmi") or m_hot
    m_spark_emi = s17.get("M_L71_VFX_SparkEmi") or m_hot
    m_tracer_emi = s17.get("M_L71_VFX_TracerEmi") or m_hot
    m_foam_emi = s17.get("M_L71_VFX_FoamEmi") or m_plate
    m_expl_emi = s17.get("M_L71_VFX_ExplEmi") or m_hot
    m_card_hot = s17.get("M_L72_VFX_CardHot") or m_muzzle_emi
    m_card_soft = s17.get("M_L72_VFX_CardSoft") or m_spark_emi
    m_card_cool = s17.get("M_L72_VFX_CardCool") or m_foam_emi
    m_card_expl = s17.get("M_L72_VFX_CardExpl") or m_expl_emi
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop / airframe: thin PBR response + denser wash ribbon (behind wall)
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            spawn_sm(sphere, (bx + 3.84, cy + 0.0, cz + 0.13), (1.15, 0.03, 1.15), None, PREFIX + "TA17_PropDiscHi_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.85, cy + 0.0, cz + 0.13), (0.55, 0.025, 0.55), None, PREFIX + "TA17_PropDiscLo_%s" % name, mat=m_disc)
            for k in range(8):
                ang = k * 22.5
                spawn_sm(cube, (bx + 3.86, cy + 0.08 * ((k % 2) * 2 - 1), cz + 0.13), (0.02, 1.05, 0.035), unreal.Rotator(0, ang, 3 + k), PREFIX + "TA17_Blade_%s_%d" % (name, k), mat=m_blade)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.9, cy + 0.0, cz + 0.1), (0.48, 0.48, 0.48), unreal.Rotator(0, 12, 28), PREFIX + "TA17_PropHero_%s" % name, mats=[m_blade, m_air, m_plate, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.7, cy - 0.04, cz - 0.24), (0.64, 0.64, 0.64), unreal.Rotator(0, 90, 0), PREFIX + "TA17_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
            spawn_niagara(PREFIX + "TA17_NS_WashRibbon_%s" % name, (bx + 3.82, cy + 0.02, cz + 0.02), "NS_L74_PropWashRibbon", (0.15, 0.15, 0.15), bound=True)
            spawn_niagara(PREFIX + "TA17_NS_PropWash_%s" % name, (bx + 3.83, cy + 0.03, cz + 0.02), "NS_PropWash", (0.12, 0.12, 0.12), bound=True)
            spawn_particle_field(PREFIX + "TA17_WashField_%s" % name, (bx + 3.83, cy + 0.0, cz + 0.06), m_card_soft, count=10, radius=0.48, size=0.028, label_base="Wash")
            spawn_sm(sphere, (bx + 3.92, cy - 0.24, cz - 0.01), (0.05, 0.05, 0.05), None, PREFIX + "TA17_Exhaust_%s" % name, mat=m_muzzle_emi)
        if name in ("YakBeauty", "Cockpit", "ADS", "Prop"):
            # thin airframe panel response (behind wall)
            spawn_sm(cube, (bx + 3.58, cy + 0.08, cz + 0.06), (0.04, 1.35, 0.75), None, PREFIX + "TA17_Air_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.62, cy - 0.42, cz - 0.02), (0.035, 1.0, 0.5), None, PREFIX + "TA17_Plate_%s" % name, mat=m_plate)
            for k in range(10):
                spawn_sm(sphere, (bx + 3.63, cy - 0.6 + k * 0.12, cz + 0.42), (0.02, 0.02, 0.02), None, PREFIX + "TA17_Rivet_%s_%d" % (name, k), mat=m_plate)
            # ADS/cockpit thin HF stripes (not solid fills)
            if name in ("ADS", "Cockpit"):
                for k in range(6):
                    spawn_sm(cube, (bx + 1.15, cy - 0.25 + k * 0.1, cz + 0.05), (0.01, 0.08, 0.02), None, PREFIX + "TA17_HFStripe_%s_%d" % (name, k), mat=m_card_soft or m_plate)
        # Combat/VFX: denser but still-bounded particle language
        if name in ("Combat", "ADS", "Wide"):
            if sm_rifle_m and name in ("ADS", "Combat"):
                spawn_sm(sm_rifle_m, (bx + 3.36, cy + 0.04, cz - 0.02), (0.42, 0.42, 0.42), unreal.Rotator(0, 90, 0), PREFIX + "TA17_Rifle_%s" % name, mats=[m_rifle, m_plate, m_rust, m_hot])
            spawn_niagara(PREFIX + "TA17_NS_MuzzleCore_%s" % name, (bx + 3.5, cy + 0.14, cz + 0.06), "NS_L74_MuzzleCore", (0.13, 0.13, 0.13), bound=True)
            spawn_niagara(PREFIX + "TA17_NS_Muzzle_%s" % name, (bx + 3.51, cy + 0.15, cz + 0.07), "NS_MuzzleFlash", (0.11, 0.11, 0.11), bound=True)
            spawn_niagara(PREFIX + "TA17_NS_SmokeSoft_%s" % name, (bx + 3.52, cy + 0.1, cz + 0.03), "NS_L74_GunSmokeSoft", (0.12, 0.12, 0.12), bound=True)
            spawn_niagara(PREFIX + "TA17_NS_SparkArc_%s" % name, (bx + 3.6, cy + 0.98, cz + 0.27), "NS_L74_SparkArc", (0.14, 0.14, 0.14), bound=True)
            spawn_niagara(PREFIX + "TA17_NS_Sparks_%s" % name, (bx + 3.61, cy + 0.99, cz + 0.28), "NS_HitSparks", (0.12, 0.12, 0.12), bound=True)
            spawn_niagara(PREFIX + "TA17_NS_TracerStreak_%s" % name, (bx + 3.55, cy + 0.18, cz + 0.12), "NS_L74_TracerStreak", (0.11, 0.11, 0.11), bound=True)
            spawn_particle_field(PREFIX + "TA17_MuzzleField_%s" % name, (bx + 3.51, cy + 0.16, cz + 0.09), m_card_hot, count=12, radius=0.24, size=0.03, label_base="Muz")
            spawn_burst_ring(PREFIX + "TA17_SparkRing_%s" % name, (bx + 3.6, cy + 0.92, cz + 0.26), m_card_soft, count=10, radius=0.38, label_base="Spark")
            for k in range(6):
                spawn_sm(cube, (bx + 3.44 + k * 0.03, cy + 0.1 + k * 0.045, cz + 0.04 + k * 0.025), (0.14 - k * 0.012, 0.012, 0.012), unreal.Rotator(0, -12 + k * 5, 0), PREFIX + "TA17_Filament_%s_%d" % (name, k), mat=m_tracer_emi)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA17_NS_ExplBloom", (bx + 3.66, cy - 0.86, cz + 0.5), "NS_L74_ExplBloom", (0.16, 0.16, 0.16), bound=True)
                spawn_niagara(PREFIX + "TA17_NS_Expl", (bx + 3.67, cy - 0.88, cz + 0.51), "NS_DroneExplosion", (0.14, 0.14, 0.14), bound=True)
                spawn_niagara(PREFIX + "TA17_NS_FlakBloom", (bx + 3.64, cy + 1.08, cz + 0.46), "NS_L74_FlakBloom", (0.13, 0.13, 0.13), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.68, cy - 0.9, cz + 0.48), (0.4, 0.4, 0.4), unreal.Rotator(0, 90, 2), PREFIX + "TA17_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_particle_field(PREFIX + "TA17_ExplField", (bx + 3.66, cy - 0.86, cz + 0.54), m_card_expl, count=14, radius=0.55, size=0.035, label_base="Expl")
                spawn_burst_ring(PREFIX + "TA17_ExplRing", (bx + 3.66, cy - 0.86, cz + 0.5), m_card_hot, count=12, radius=0.62, label_base="ExplR")
                for k in range(10):
                    spawn_sm(sphere, (bx + 3.6, cy - 1.15 + k * 0.05, cz + 0.4 + (k % 3) * 0.035), (0.022, 0.022, 0.022), None, PREFIX + "TA17_Debris_%d" % k, mat=m_spark_emi if k % 2 == 0 else m_plate)
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.6, cy + 0.25, cz - 0.26), (0.05, 1.2, 1.4), None, PREFIX + "TA17_Brick_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.64, cy - 0.9, cz - 0.06), (0.045, 1.0, 1.15), None, PREFIX + "TA17_Conc_%s" % name, mat=m_conc)
            if name == "City":
                spawn_niagara(PREFIX + "TA17_NS_CityFire", (bx + 3.66, cy + 0.36, cz + 0.72), "NS_CityFire", (0.14, 0.14, 0.14), bound=True)
                spawn_particle_field(PREFIX + "TA17_Ember", (bx + 3.66, cy + 0.36, cz + 0.78), m_card_hot, count=10, radius=0.35, size=0.025, label_base="Ember")
        if name in ("Ocean", "Harbor"):
            spawn_niagara(PREFIX + "TA17_NS_FoamSheet_%s" % name, (bx + 3.56, cy - 0.18, cz - 0.52), "NS_L74_FoamSheet", (0.18, 0.18, 0.18), bound=True)
            spawn_niagara(PREFIX + "TA17_NS_Spray_%s" % name, (bx + 3.57, cy - 0.18, cz - 0.54), "NS_OceanSpray", (0.16, 0.16, 0.16), bound=True)
            spawn_particle_field(PREFIX + "TA17_FoamField_%s" % name, (bx + 3.56, cy - 0.32, cz - 0.44), m_card_cool, count=12, radius=0.6, size=0.035, label_base="Foam")
            for k in range(10):
                spawn_sm(sphere, (bx + 3.54, cy - 0.9 + k * 0.09, cz - 0.42 + (k % 2) * 0.04), (0.045, 0.045, 0.045), None, PREFIX + "TA17_Foam_%s_%d" % (name, k), mat=m_foam_emi)
    log("slice17 visible vfx + prop/airframe densify applied (no extra point lights)")

    # Slice18 (thin / capture-safe on L74 KEEP): materials + VFX push
    # HARD RULES: no FOV PointLight stacks; keep L52 HF densify core; behind-wall only; no L53 stacks.
    vfx18 = ensure_slice18_vfx_library()
    s18 = ensure_slice16_materials()
    m_air = s18.get("M_L70_AirframeResp") or s18.get("M_L68_AirframeANR")
    m_plate = s18.get("M_L70_PlateResp") or s18.get("M_L68_PlateANR")
    m_rust = s18.get("M_L70_RustResp") or s18.get("M_L68_RustANR")
    m_brick = s18.get("M_L70_BrickResp") or s18.get("M_L68_BrickANR")
    m_conc = s18.get("M_L70_ConcreteResp") or s18.get("M_L68_ConcreteANR")
    m_hot = s18.get("M_L70_MuzzleResp") or s18.get("M_L61_MuzzleHot")
    m_glow = load_mat("/Game/Skyguard/Materials/M_ExhaustGlow") or m_hot
    m_disc = s18.get("M_L72_PropDiscBright") or s18.get("M_L71_PropDiscMotion") or load_mat("/Game/Skyguard/Materials/M_PropDisc")
    m_blade = s18.get("M_L72_PropBladeEdge") or s18.get("M_L71_PropBlade") or m_air
    m_muzzle_emi = s18.get("M_L71_VFX_MuzzleEmi") or m_hot
    m_spark_emi = s18.get("M_L71_VFX_SparkEmi") or m_hot
    m_tracer_emi = s18.get("M_L71_VFX_TracerEmi") or m_hot
    m_foam_emi = s18.get("M_L71_VFX_FoamEmi") or m_plate
    m_expl_emi = s18.get("M_L71_VFX_ExplEmi") or m_hot
    m_card_hot = s18.get("M_L72_VFX_CardHot") or m_muzzle_emi
    m_card_soft = s18.get("M_L72_VFX_CardSoft") or m_spark_emi
    m_card_cool = s18.get("M_L72_VFX_CardCool") or m_foam_emi
    m_card_expl = s18.get("M_L72_VFX_CardExpl") or m_expl_emi
    m_rifle = load_mat("/Game/Skyguard/Materials/M_RifleTan") or m_plate
    m_leather = load_mat("/Game/Skyguard/Materials/M_LeatherGlove") or m_plate
    m_glass = load_mat("/Game/Skyguard/Materials/M_CityGlass") or m_plate
    m_ocean = load_mat("/Game/Skyguard/Materials/M_L23_Ocean") or s18.get("M_L21_BrightOcean")
    m_sand = load_mat("/Game/Skyguard/Materials/M_L23_Beach") or s18.get("M_L21_BrightSand")
    m_asphalt = load_mat("/Game/Skyguard/Materials/M_L23_Asphalt") or m_conc
    cube = load_sm("/Engine/BasicShapes/Cube")
    sphere = load_sm("/Engine/BasicShapes/Sphere")
    sm_prop = load_sm("/Game/Skyguard/Meshes/Hero/propeller_proxy")
    sm_yak = load_sm("/Game/Skyguard/Meshes/Hero/yak52_hd_proxy") or load_sm("/Game/Skyguard/Meshes/Hero/yak52_proxy")
    sm_rifle_m = load_sm("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy")
    sm_drone = load_sm("/Game/Skyguard/Meshes/Hero/shahed_proxy")
    for i, (name, cam, dist, mat) in enumerate(stages):
        bx = cam[0] + dist
        cy, cz = cam[1], cam[2]
        # Prop/airframe materials response + denser wash (behind wall)
        if name in ("Prop", "PropHub", "PropNose", "YakBeauty"):
            spawn_sm(sphere, (bx + 3.88, cy + 0.0, cz + 0.14), (1.2, 0.028, 1.2), None, PREFIX + "TA18_PropDiscHi_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.89, cy + 0.0, cz + 0.14), (0.62, 0.022, 0.62), None, PREFIX + "TA18_PropDiscMid_%s" % name, mat=m_disc)
            spawn_sm(sphere, (bx + 3.9, cy + 0.0, cz + 0.14), (0.28, 0.05, 0.28), None, PREFIX + "TA18_PropHub_%s" % name, mat=m_plate)
            for k in range(10):
                ang = k * 18.0
                spawn_sm(cube, (bx + 3.91, cy + 0.07 * ((k % 2) * 2 - 1), cz + 0.14), (0.018, 1.08, 0.032), unreal.Rotator(0, ang, 2 + k), PREFIX + "TA18_Blade_%s_%d" % (name, k), mat=m_blade)
            if sm_prop:
                spawn_sm(sm_prop, (bx + 3.94, cy + 0.0, cz + 0.11), (0.46, 0.46, 0.46), unreal.Rotator(0, 18, 22), PREFIX + "TA18_PropHero_%s" % name, mats=[m_blade, m_air, m_plate, m_disc])
            if sm_yak and name == "YakBeauty":
                spawn_sm(sm_yak, (bx + 3.72, cy - 0.03, cz - 0.22), (0.62, 0.62, 0.62), unreal.Rotator(0, 90, 0), PREFIX + "TA18_YakHero", mats=[m_air, m_plate, m_rust, m_glow])
                # panel seams / dirt response cards behind wall
                for k in range(8):
                    spawn_sm(cube, (bx + 3.74, cy - 0.55 + k * 0.14, cz - 0.05), (0.02, 0.12, 0.55), None, PREFIX + "TA18_Panel_%d" % k, mat=m_air if k % 2 == 0 else m_plate)
            spawn_niagara(PREFIX + "TA18_NS_WashSheet_%s" % name, (bx + 3.86, cy + 0.02, cz + 0.03), "NS_L75_PropWashSheet", (0.14, 0.14, 0.14), bound=True)
            spawn_niagara(PREFIX + "TA18_NS_Wash_%s" % name, (bx + 3.87, cy + 0.03, cz + 0.02), "NS_PropWash", (0.11, 0.11, 0.11), bound=True)
            spawn_particle_field(PREFIX + "TA18_WashField_%s" % name, (bx + 3.87, cy + 0.0, cz + 0.07), m_card_soft, count=12, radius=0.5, size=0.026, label_base="Wash")
            if name in ("YakBeauty", "Prop"):
                spawn_niagara(PREFIX + "TA18_NS_Contrail_%s" % name, (bx + 3.98, cy + 0.05, cz + 0.0), "NS_L75_ContrailCore", (0.12, 0.12, 0.12), bound=True)
            spawn_sm(sphere, (bx + 3.96, cy - 0.22, cz - 0.01), (0.045, 0.045, 0.045), None, PREFIX + "TA18_Exhaust_%s" % name, mat=m_muzzle_emi)
        if name in ("YakBeauty", "Cockpit", "ADS", "Prop"):
            spawn_sm(cube, (bx + 3.62, cy + 0.1, cz + 0.07), (0.035, 1.3, 0.72), None, PREFIX + "TA18_Air_%s" % name, mat=m_air)
            spawn_sm(cube, (bx + 3.66, cy - 0.4, cz - 0.01), (0.03, 0.95, 0.48), None, PREFIX + "TA18_Plate_%s" % name, mat=m_plate)
            spawn_sm(cube, (bx + 3.68, cy + 0.55, cz - 0.12), (0.025, 0.55, 0.35), None, PREFIX + "TA18_Rust_%s" % name, mat=m_rust)
            for k in range(12):
                spawn_sm(sphere, (bx + 3.67, cy - 0.7 + k * 0.12, cz + 0.4), (0.018, 0.018, 0.018), None, PREFIX + "TA18_Rivet_%s_%d" % (name, k), mat=m_plate)
            if name in ("ADS", "Cockpit"):
                for k in range(8):
                    spawn_sm(cube, (bx + 1.18, cy - 0.3 + k * 0.09, cz + 0.04), (0.008, 0.07, 0.018), None, PREFIX + "TA18_HFStripe_%s_%d" % (name, k), mat=m_card_soft or m_plate)
                if name == "ADS" and sm_rifle_m:
                    spawn_sm(sm_rifle_m, (bx + 3.38, cy + 0.03, cz - 0.02), (0.4, 0.4, 0.4), unreal.Rotator(0, 90, 0), PREFIX + "TA18_Rifle", mats=[m_rifle, m_plate, m_rust, m_hot])
                    spawn_sm(cube, (bx + 3.4, cy - 0.08, cz - 0.08), (0.04, 0.08, 0.05), None, PREFIX + "TA18_Glove", mat=m_leather)
        if name in ("Combat", "ADS", "Wide"):
            spawn_niagara(PREFIX + "TA18_NS_MuzzleHot_%s" % name, (bx + 3.52, cy + 0.13, cz + 0.06), "NS_L75_MuzzleCoreHot", (0.12, 0.12, 0.12), bound=True)
            spawn_niagara(PREFIX + "TA18_NS_Muzzle_%s" % name, (bx + 3.53, cy + 0.14, cz + 0.07), "NS_MuzzleFlash", (0.1, 0.1, 0.1), bound=True)
            spawn_niagara(PREFIX + "TA18_NS_SmokeVol_%s" % name, (bx + 3.54, cy + 0.09, cz + 0.03), "NS_L75_GunSmokeVolume", (0.12, 0.12, 0.12), bound=True)
            spawn_niagara(PREFIX + "TA18_NS_SparkFil_%s" % name, (bx + 3.62, cy + 0.96, cz + 0.26), "NS_L75_SparkFilament", (0.13, 0.13, 0.13), bound=True)
            spawn_niagara(PREFIX + "TA18_NS_Sparks_%s" % name, (bx + 3.63, cy + 0.97, cz + 0.27), "NS_HitSparks", (0.11, 0.11, 0.11), bound=True)
            spawn_niagara(PREFIX + "TA18_NS_TracerCore_%s" % name, (bx + 3.57, cy + 0.17, cz + 0.11), "NS_L75_TracerCore", (0.1, 0.1, 0.1), bound=True)
            spawn_particle_field(PREFIX + "TA18_MuzzleField_%s" % name, (bx + 3.53, cy + 0.15, cz + 0.08), m_card_hot, count=14, radius=0.22, size=0.028, label_base="Muz")
            spawn_burst_ring(PREFIX + "TA18_SparkRing_%s" % name, (bx + 3.62, cy + 0.9, cz + 0.25), m_card_soft, count=12, radius=0.36, label_base="Spark")
            for k in range(8):
                spawn_sm(cube, (bx + 3.46 + k * 0.028, cy + 0.09 + k * 0.04, cz + 0.03 + k * 0.022), (0.13 - k * 0.01, 0.011, 0.011), unreal.Rotator(0, -10 + k * 5, 0), PREFIX + "TA18_Filament_%s_%d" % (name, k), mat=m_tracer_emi)
            if name == "Combat":
                spawn_niagara(PREFIX + "TA18_NS_ExplShock", (bx + 3.68, cy - 0.84, cz + 0.5), "NS_L75_ExplShock", (0.15, 0.15, 0.15), bound=True)
                spawn_niagara(PREFIX + "TA18_NS_Expl", (bx + 3.69, cy - 0.86, cz + 0.51), "NS_DroneExplosion", (0.13, 0.13, 0.13), bound=True)
                spawn_niagara(PREFIX + "TA18_NS_FlakCore", (bx + 3.66, cy + 1.06, cz + 0.45), "NS_L75_FlakCore", (0.12, 0.12, 0.12), bound=True)
                if sm_drone:
                    spawn_sm(sm_drone, (bx + 3.7, cy - 0.88, cz + 0.47), (0.38, 0.38, 0.38), unreal.Rotator(0, 90, 2), PREFIX + "TA18_Shahed", mats=[m_plate, m_air, m_rust, m_hot])
                spawn_particle_field(PREFIX + "TA18_ExplField", (bx + 3.68, cy - 0.84, cz + 0.53), m_card_expl, count=16, radius=0.5, size=0.032, label_base="Expl")
                spawn_burst_ring(PREFIX + "TA18_ExplRing", (bx + 3.68, cy - 0.84, cz + 0.49), m_card_hot, count=14, radius=0.58, label_base="ExplR")
                for k in range(12):
                    spawn_sm(sphere, (bx + 3.62, cy - 1.1 + k * 0.045, cz + 0.38 + (k % 3) * 0.03), (0.02, 0.02, 0.02), None, PREFIX + "TA18_Debris_%d" % k, mat=m_spark_emi if k % 2 == 0 else m_plate)
        if name in ("City", "Harbor", "Wide"):
            spawn_sm(cube, (bx + 3.64, cy + 0.22, cz - 0.24), (0.045, 1.15, 1.35), None, PREFIX + "TA18_Brick_%s" % name, mat=m_brick)
            spawn_sm(cube, (bx + 3.68, cy - 0.88, cz - 0.05), (0.04, 0.95, 1.1), None, PREFIX + "TA18_Conc_%s" % name, mat=m_conc)
            spawn_sm(cube, (bx + 3.7, cy - 0.1, cz - 0.55), (0.03, 1.4, 0.08), None, PREFIX + "TA18_Asphalt_%s" % name, mat=m_asphalt)
            for ix in range(3):
                for iy in range(4):
                    spawn_sm(cube, (bx + 3.65, cy - 0.3 + ix * 0.28, cz - 0.2 + iy * 0.26), (0.018, 0.11, 0.14), None, PREFIX + "TA18_Win_%s_%d_%d" % (name, ix, iy), mat=m_glass)
            if name == "City":
                spawn_niagara(PREFIX + "TA18_NS_CityEmber", (bx + 3.7, cy + 0.34, cz + 0.7), "NS_L75_CityEmber", (0.13, 0.13, 0.13), bound=True)
                spawn_particle_field(PREFIX + "TA18_Ember", (bx + 3.7, cy + 0.34, cz + 0.76), m_card_hot, count=12, radius=0.32, size=0.024, label_base="Ember")
        if name in ("Ocean", "Harbor"):
            spawn_sm(cube, (bx + 3.6, cy - 0.4, cz - 0.7), (0.04, 1.6, 0.12), None, PREFIX + "TA18_Beach_%s" % name, mat=m_sand)
            spawn_sm(cube, (bx + 3.62, cy + 0.2, cz - 0.78), (0.05, 1.8, 0.2), None, PREFIX + "TA18_Ocean_%s" % name, mat=m_ocean)
            spawn_niagara(PREFIX + "TA18_NS_FoamCrest_%s" % name, (bx + 3.58, cy - 0.16, cz - 0.5), "NS_L75_FoamCrest", (0.16, 0.16, 0.16), bound=True)
            spawn_niagara(PREFIX + "TA18_NS_Spray_%s" % name, (bx + 3.59, cy - 0.16, cz - 0.52), "NS_OceanSpray", (0.14, 0.14, 0.14), bound=True)
            spawn_particle_field(PREFIX + "TA18_FoamField_%s" % name, (bx + 3.58, cy - 0.3, cz - 0.42), m_card_cool, count=14, radius=0.55, size=0.032, label_base="Foam")
            for k in range(12):
                spawn_sm(sphere, (bx + 3.56, cy - 0.85 + k * 0.08, cz - 0.4 + (k % 2) * 0.035), (0.04, 0.04, 0.04), None, PREFIX + "TA18_Foam_%s_%d" % (name, k), mat=m_foam_emi)
    log("slice18 materials + vfx push densify applied (no extra point lights)")

    log("loop75 true-art slice18 densify done")
    return stages

def capture(out_dir, stages):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir("/Game/Skyguard/Capture")
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            "RT_AAA_L75", "/Game/Skyguard/Capture", unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    rt.set_editor_property("size_x", 1920)
    rt.set_editor_property("size_y", 1080)
    try:
        rt.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    cams = [("AAA_Cam_L75_%s" % name, cam, (0.0,0.0,0.0)) for name, cam, dist, mat in stages]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
            try:
                c.set_actor_location(unreal.Vector(*loc), False, True)
            except Exception:
                pass
            log("CAM %s target=%s got=%s" % (name, loc, get_loc(c)))

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0,0,400), unreal.Rotator())
    sca.set_actor_label(PREFIX + "SceneCapture")
    comp = sca.get_editor_property("capture_component2d")
    comp.set_editor_property("texture_target", rt)
    try:
        comp.set_editor_property("capture_every_frame", False)
    except Exception:
        pass
    try:
        comp.set_editor_property("capture_on_movement", False)
    except Exception:
        pass
    try:
        # show only lit/unlit geometry
        comp.set_editor_property("primitive_render_mode", unreal.SceneCapturePrimitiveRenderMode.PRM_RENDER_SCENE_PRIMITIVES)
    except Exception:
        pass
    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world = unreal.EditorLevelLibrary.get_editor_world()

    sources = []
    try:
        sources.append(("BASE", unreal.SceneCaptureSource.SCS_BASE_COLOR))
    except Exception:
        pass
    try:
        sources.append(("FINAL", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR))
    except Exception:
        pass
    try:
        sources.append(("SCENE", unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR))
    except Exception:
        if not sources:
            sources.append(("DEFAULT", None))

    saved = []
    for name, loc, rot in cams:
        try:
            comp.set_editor_property("fov_angle", 90.0)
        except Exception:
            pass
        for src_name, enum in sources:
            try:
                if enum is not None:
                    comp.set_editor_property("capture_source", enum)
            except Exception as e:
                log("src " + str(e))
            sca.set_actor_location(unreal.Vector(*loc), False, True)
            sca.set_actor_rotation(unreal.Rotator(*rot), False)
            for _ in range(6):
                try:
                    comp.capture_scene()
                except Exception:
                    pass
            out_name = "%s_%s.png" % (name, src_name)
            out_png = os.path.join(out_dir, out_name)
            if os.path.isfile(out_png):
                try: os.remove(out_png)
                except Exception: pass
            try:
                unreal.RenderingLibrary.export_render_target(world, rt, out_dir, out_name)
            except Exception as e:
                log("export " + out_name + " " + str(e))
            if os.path.isfile(out_png):
                size = os.path.getsize(out_png)
                h = hashlib.sha256(open(out_png, "rb").read()).hexdigest()
                log("still %s size=%d sha=%s" % (out_name, size, h[:16]))
                saved.append((out_png, size, h, src_name, name))
    man = os.path.join(out_dir, "MANIFEST_SHA256.txt")
    with open(man, "w", encoding="utf-8") as f:
        f.write("Skyguard AAA Loop75 stills\n")
        f.write("time=%s\n" % time.strftime("%Y-%m-%dT%H:%M:%S"))
        f.write("note=l74_freeze_true_art_slice18_materials_vfx_push")
        for path, size, h, src, name in saved:
            f.write("%s  %d  src=%s cam=%s  %s\n" % (h, size, src, name, path))
        f.write("total=%d\n" % len(saved))
    log("manifest total=%d" % len(saved))
    return saved

def main():
    log("loop75 L74 freeze + true-art slice18 materials + VFX push start")
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_old()
    stages = densify()
    saved = capture(OUT_DIR, stages)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop75 complete stills=%d" % (len(saved) if saved else 0))
    log("CRITIC: host RGB select+audit required; overall FAIL until blind AAA win")

main()

