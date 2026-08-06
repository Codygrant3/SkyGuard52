"""Skyguard AAA materials + master look pass: layered noise, roughness variance, emissive city windows."""
import unreal

def log(m):
    unreal.log(f"[SkyguardAAA] {m}")

def ensure_dir(p):
    if not unreal.EditorAssetLibrary.does_directory_exist(p):
        unreal.EditorAssetLibrary.make_directory(p)

def rebuild_master_material(name, base, roughness=0.7, metallic=0.0, emissive=None, roughness_var=0.05):
    path = f"/Game/Skyguard/Materials/{name}"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mat = unreal.EditorAssetLibrary.load_asset(path)
    else:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, "/Game/Skyguard/Materials", unreal.Material, unreal.MaterialFactoryNew()
        )
    if not mat:
        return None
    mel = unreal.MaterialEditingLibrary
    try:
        mel.delete_all_material_expressions(mat)
    except Exception:
        pass
    try:
        base_expr = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -600, -100)
        base_expr.set_editor_property("constant", unreal.LinearColor(base[0], base[1], base[2], 1.0))
        # cheap variation using noise if available
        try:
            noise = mel.create_material_expression(mat, unreal.MaterialExpressionNoise, -600, 40)
            noise.set_editor_property("scale", 2.5)
            one = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 100)
            one.set_editor_property("r", 1.0)
            add = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -250, 40)
            mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -100, -40)
            scale = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 160)
            scale.set_editor_property("r", roughness_var)
            # (1 + noise*var)
            mel.connect_material_expressions(noise, "", mul, "A")
            mel.connect_material_expressions(scale, "", mul, "B")
            mel.connect_material_expressions(one, "", add, "A")
            mel.connect_material_expressions(mul, "", add, "B")
            base_mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, 50, -80)
            mel.connect_material_expressions(base_expr, "", base_mul, "A")
            mel.connect_material_expressions(add, "", base_mul, "B")
            mel.connect_material_property(base_mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
        except Exception:
            mel.connect_material_property(base_expr, "", unreal.MaterialProperty.MP_BASE_COLOR)

        rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -600, 220)
        rough.set_editor_property("r", float(roughness))
        mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
        metal = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -600, 280)
        metal.set_editor_property("r", float(metallic))
        mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
        if emissive is not None:
            em = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -600, 340)
            em.set_editor_property("constant", unreal.LinearColor(emissive[0], emissive[1], emissive[2], 1.0))
            mel.connect_material_property(em, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.recompile_material(mat)
    except Exception as e:
        log(f"mat {name}: {e}")
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat


def spawn_sm(mesh, loc, scale=None, rot=None, label=None, material=None):
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a:
        return None
    c = a.static_mesh_component
    c.set_static_mesh(mesh)
    if scale:
        a.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        a.set_actor_label(label)
    if material:
        c.set_material(0, material)
    return a


def clear_prefix(prefix):
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            n = a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass


def main():
    log("materials+night windows pass start")
    ensure_dir("/Game/Skyguard/Materials")
    ensure_dir("/Game/Skyguard/VFX")
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")

    mats = {
        "ocean": rebuild_master_material("M_Ocean", (0.02, 0.12, 0.2), 0.15, 0.1, roughness_var=0.08),
        "ocean_deep": rebuild_master_material("M_OceanDeep", (0.01, 0.04, 0.08), 0.2, 0.05),
        "beach": rebuild_master_material("M_Beach", (0.74, 0.63, 0.42), 0.93, roughness_var=0.1),
        "city": rebuild_master_material("M_CityConcrete", (0.36, 0.35, 0.33), 0.84, roughness_var=0.12),
        "city_glass": rebuild_master_material("M_CityGlass", (0.12, 0.18, 0.24), 0.08, 0.05, emissive=(0.35, 0.28, 0.12), roughness_var=0.02),
        "airframe": rebuild_master_material("M_YakAirframe", (0.6, 0.62, 0.57), 0.4, 0.45, roughness_var=0.05),
        "drone": rebuild_master_material("M_ShahedDrone", (0.09, 0.11, 0.09), 0.5, 0.3),
        "rifle": rebuild_master_material("M_RifleTan", (0.4, 0.33, 0.18), 0.55, 0.25),
        "leather": rebuild_master_material("M_LeatherGlove", (0.11, 0.06, 0.03), 0.72),
        "exhaust": rebuild_master_material("M_ExhaustGlow", (0.5, 0.12, 0.01), 0.4, emissive=(4.0, 0.7, 0.05)),
    }

    # Lit windows scatter for dusk cinematic density
    clear_prefix("AAA_Window_")
    cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    glass = mats["city_glass"]
    for i in range(120):
        x = -1500 - (i % 6) * 240
        y = -2600 + (i * 47) % 5200
        z = 140 + (i * 37) % 900
        spawn_sm(cube, (x + 55, y, z), (0.05, 0.55, 0.4), None, f"AAA_Window_{i}", glass)

    # Extra sea spray proxies near beach
    clear_prefix("AAA_Foam_")
    sphere = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    beach = mats["beach"]
    for i in range(40):
        y = -2400 + i * 120
        spawn_sm(sphere, (-820, y, 18), (0.8, 1.6, 0.15), None, f"AAA_Foam_{i}", beach)

    # Niagara systems shells
    try:
        at = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.NiagaraSystemFactoryNew()
        for n in ["NS_MuzzleFlash", "NS_DroneTrail", "NS_OceanSpray", "NS_DroneExplosion"]:
            p = f"/Game/Skyguard/VFX/{n}"
            if not unreal.EditorAssetLibrary.does_asset_exist(p):
                ns = at.create_asset(n, "/Game/Skyguard/VFX", unreal.NiagaraSystem, factory)
                if ns:
                    unreal.EditorAssetLibrary.save_loaded_asset(ns)
                    log(f"created {n}")
    except Exception as e:
        log(f"niagara {e}")

    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("materials+windows+vfx shells complete")
    log("CRITIC EXPECTATION: still FAIL until Fab hero assets + compiled gameplay")

if __name__ == "__main__":
    main()
