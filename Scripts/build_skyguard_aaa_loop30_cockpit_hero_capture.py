import unreal
import os
import hashlib
import time

PREFIX = 'AAA_L30_'
OUT_DIR = r'D:\Skyguard52\Saved\Screenshots\AAA_L30'
RT_PATH = '/Game/Skyguard/Capture/RT_AAA_L30'
MAP_PATH = '/Game/Skyguard/Maps/Lvl_SkyguardCoast'

def log(m):
    unreal.log('[SkyguardAAA] ' + str(m))

def clear_old():
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and (n.startswith('AAA_L') or n.startswith('AAA_Cam_L')):
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

def list_static_meshes(folder):
    out = []
    try:
        for a in unreal.EditorAssetLibrary.list_assets(folder, True, False):
            asset = unreal.EditorAssetLibrary.load_asset(a)
            if isinstance(asset, unreal.StaticMesh):
                out.append((a, asset))
    except Exception as e:
        log('list ' + str(e))
    return out

def bounds_max(mesh):
    try:
        e = mesh.get_bounds().box_extent
        return max(abs(e.x) * 2, abs(e.y) * 2, abs(e.z) * 2, 0.001)
    except Exception:
        return 100.0

def spawn_sm(mesh, loc, scale=(1, 1, 1), rot=None, label=None, mat=None):
    if not mesh:
        return None
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor, unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), rot or unreal.Rotator()
    )
    if not a:
        return None
    a.static_mesh_component.set_static_mesh(mesh)
    a.set_actor_scale3d(unreal.Vector(float(scale[0]), float(scale[1]), float(scale[2])))
    try:
        a.set_actor_location(unreal.Vector(float(loc[0]), float(loc[1]), float(loc[2])), False, True)
    except Exception:
        pass
    if mat:
        try:
            a.static_mesh_component.set_material(0, mat)
        except Exception:
            pass
    if label:
        a.set_actor_label(label)
    return a

def densify():
    cube = load_sm('/Engine/BasicShapes/Cube')
    sphere = load_sm('/Engine/BasicShapes/Sphere')
    plane = load_sm('/Engine/BasicShapes/Plane')
    cyl = load_sm('/Engine/BasicShapes/Cylinder')
    cone = load_sm('/Engine/BasicShapes/Cone')

    air = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Airframe') or load_mat('/Game/Skyguard/Materials/Generated/M_AirframeMetal')
    panel = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Panel') or air
    leather = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Leather') or panel
    canopy = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Canopy')
    brick = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Brick') or load_mat('/Game/Skyguard/Materials/Generated/M_BrickFacade')
    plaster = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Plaster')
    asphalt = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Asphalt')
    ocean = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Ocean')
    beach = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Beach')
    foam = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Foam')
    glass = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Glass')
    muzzle = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Muzzle') or load_mat('/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot')
    boom = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Boom') or load_mat('/Game/Skyguard/Materials/Generated/MI_ExplosionCore')
    white = load_mat('/Game/Skyguard/Materials/Generated/M_L21_BrightWhite') or plaster
    bright_metal = load_mat('/Game/Skyguard/Materials/Generated/M_L21_BrightMetal') or air
    bright_brick = load_mat('/Game/Skyguard/Materials/Generated/M_L21_BrightBrick') or brick
    bright_ocean = load_mat('/Game/Skyguard/Materials/Generated/M_L21_BrightOcean') or ocean
    unlit_w = load_mat('/Game/Skyguard/Materials/Generated/M_L18_UnlitWhite')
    unlit_y = load_mat('/Game/Skyguard/Materials/Generated/M_L18_UnlitYellow')
    unlit_c = load_mat('/Game/Skyguard/Materials/Generated/M_L18_UnlitCyan')
    unlit_r = load_mat('/Game/Skyguard/Materials/Generated/M_L18_UnlitRed')
    unlit_g = load_mat('/Game/Skyguard/Materials/Generated/M_L18_UnlitGreen')
    needle = load_mat('/Game/Skyguard/Materials/Generated/M_L23_Needle') or unlit_y
    hi_pool = [m for m in [unlit_w, unlit_y, unlit_c, unlit_r, unlit_g, white, bright_metal, panel, boom, muzzle, bright_brick, air] if m]
    metal_pool = [m for m in [bright_metal, air, panel, unlit_w, unlit_y, white] if m]

    def hi(i):
        return hi_pool[i % len(hi_pool)] if hi_pool else panel
    def hero(i):
        return metal_pool[i % len(metal_pool)] if metal_pool else panel

    stages = [
        ('Prop', (0.0, 0.0, 500.0), 100.0, 12, 9),
        ('PropHub', (0.0, 240.0, 500.0), 95.0, 11, 8),
        ('PropNose', (0.0, -240.0, 500.0), 95.0, 11, 8),
        ('YakBeauty', (220.0, -180.0, 430.0), 140.0, 14, 9),
        ('Cockpit', (40.0, 110.0, 380.0), 55.0, 14, 10),
        ('ADS', (20.0, 150.0, 370.0), 50.0, 10, 7),
        ('City', (-850.0, -220.0, 280.0), 160.0, 14, 9),
        ('Combat', (720.0, 10.0, 450.0), 130.0, 11, 8),
        ('Harbor', (-220.0, -160.0, 160.0), 130.0, 11, 7),
        ('Ocean', (680.0, -20.0, 120.0), 150.0, 12, 7),
        ('Wide', (160.0, -400.0, 400.0), 180.0, 13, 9),
    ]

    for name, cam, dist, ny, nz in stages:
        cx, cy, cz = cam
        bx = cx + dist
        for iy in range(-ny, ny + 1):
            for iz in range(-nz, nz + 1):
                mat = hi(iy + iz * 3) if name in ('Cockpit', 'ADS', 'City') else hero(iy + iz)
                spawn_sm(cube, (bx, cy + iy * 4.8, cz + iz * 4.8), (0.28, 0.45, 0.45), None, PREFIX + 'Board_%s_%d_%d' % (name, iy, iz), mat)

        if name.startswith('Prop'):
            for i, ang in enumerate(range(0, 180, 8)):
                spawn_sm(cube, (bx - 3, cy, cz), (0.16, 8.2, 0.14), unreal.Rotator(0, ang, 0), PREFIX + 'Blade_%s_%d' % (name, i), hero(i))
            spawn_sm(sphere, (bx - 7, cy, cz), (1.7, 1.7, 1.7), None, PREFIX + 'Hub_%s' % name, bright_metal or hi(1))
            spawn_sm(cone, (bx - 15, cy, cz), (1.15, 1.15, 2.4), unreal.Rotator(0, 0, -90), PREFIX + 'Spinner_%s' % name, unlit_y or white)
            for i in range(6):
                spawn_sm(plane, (bx - 5, cy, cz), (2.2 + i * 0.35, 2.2 + i * 0.35, 1), unreal.Rotator(0, i * 15, 90), PREFIX + 'Disc_%s_%d' % (name, i), unlit_c if i % 2 == 0 else (bright_metal or hi(i)))
            for i in range(5):
                spawn_sm(cyl, (bx + 6 + i * 6, cy, cz), (0.4 + i * 0.12, 0.4 + i * 0.12, 0.65), unreal.Rotator(0, 0, 90), PREFIX + 'Cowling_%s_%d' % (name, i), air if i % 2 == 0 else panel)
            for i in range(16):
                spawn_sm(cube, (bx + 2, cy - 6 + i * 0.8, cz - 3 + (i % 5) * 1.2), (0.05, 0.9, 0.05), None, PREFIX + 'Streak_%s_%d' % (name, i), panel if i % 2 == 0 else unlit_w)

        if name == 'YakBeauty':
            for i in range(40):
                spawn_sm(cube, (bx - 2, cy - 40 + i * 2.0, cz), (0.06, 0.12, 3.8), None, PREFIX + 'PanelV_%d' % i, hero(i))
                spawn_sm(cube, (bx - 2, cy, cz - 28 + i * 1.4), (0.06, 4.8, 0.09), None, PREFIX + 'PanelH_%d' % i, hero(i + 1))
            for i in range(90):
                spawn_sm(sphere, (bx - 1, cy - 42 + (i % 18) * 4.6, cz - 24 + (i // 18) * 7.5), (0.12, 0.12, 0.12), None, PREFIX + 'Rivet_%d' % i, unlit_w if i % 3 == 0 else bright_metal)
            spawn_sm(cube, (bx + 6, cy + 18, cz + 8), (1.1, 0.08, 1.1), None, PREFIX + 'Star', unlit_r or boom)
            for i in range(18):
                spawn_sm(cyl, (bx + 10 + i * 1.5, cy + 8, cz + 12), (0.05, 0.05, 1.0), unreal.Rotator(0, 0, 90), PREFIX + 'CanopyRail_%d' % i, bright_metal or panel)
                spawn_sm(plane, (bx + 12 + i * 1.2, cy + 10, cz + 14), (0.45, 0.35, 1), unreal.Rotator(55, 0, 0), PREFIX + 'CanopyGlass_%d' % i, canopy or glass)

        if name == 'Cockpit':
            for i in range(18):
                spawn_sm(cyl, (bx - 3, cy - 20 + i * 2.2, cz - 2), (0.38, 0.38, 0.08), unreal.Rotator(90, 0, 0), PREFIX + 'Gauge_%d' % i, unlit_y if i % 2 == 0 else (unlit_c or glass))
                spawn_sm(cube, (bx - 2.2, cy - 20 + i * 2.2, cz - 1.5), (0.04, 0.22, 0.03), None, PREFIX + 'Needle_%d' % i, unlit_r or needle)
                spawn_sm(cube, (bx - 5, cy - 20 + i * 2.2, cz - 4), (0.3, 0.9, 0.08), None, PREFIX + 'Dash_%d' % i, panel)
            spawn_sm(cube, (bx - 10, cy, cz - 14), (1.3, 1.1, 0.65), None, PREFIX + 'Seat', leather or hi(0))
            spawn_sm(cube, (bx - 18, cy, cz - 14), (1.3, 1.1, 0.65), None, PREFIX + 'SeatF', leather or hi(1))
            for i in range(16):
                spawn_sm(cyl, (bx - 1, cy, cz + 2), (0.06, 0.06, 1.3), unreal.Rotator(0, i * 11.25, 90), PREFIX + 'Bow_%d' % i, unlit_w if i % 2 == 0 else bright_metal)
            for i in range(40):
                spawn_sm(sphere, (bx - 8 + (i % 8) * 1.3, cy - 12 + (i // 8) * 3.5, cz + 1 + (i % 5) * 0.8), (0.18, 0.18, 0.18), None, PREFIX + 'Fill_%d' % i, hi(i))
            spawn_sm(cube, (bx - 6, cy - 14, cz), (1.0, 0.1, 0.7), None, PREFIX + 'RailL', panel)
            spawn_sm(cube, (bx - 6, cy + 14, cz), (1.0, 0.1, 0.7), None, PREFIX + 'RailR', panel)
            spawn_sm(cyl, (bx - 8, cy, cz - 6), (0.07, 0.07, 0.7), unreal.Rotator(30, 0, 0), PREFIX + 'Stick', panel)
            spawn_sm(cube, (bx + 8, cy, cz + 10), (1.8, 1.1, 0.1), None, PREFIX + 'CanopySlide', canopy or glass)

        if name == 'ADS':
            rifle_parts = list_static_meshes('/Game/Skyguard/Meshes/WebGame/skyguard-rifle')
            for i, (path, mesh) in enumerate(rifle_parts[:10]):
                scv = 80.0 / bounds_max(mesh)
                if scv > 40:
                    scv = 1.0
                spawn_sm(mesh, (bx - 12, cy, cz), (scv, scv, scv), unreal.Rotator(0, 90, 0), PREFIX + 'Rifle_%d' % i)
            spawn_sm(cyl, (bx - 6, cy, cz), (0.08, 0.08, 1.3), unreal.Rotator(0, 0, 90), PREFIX + 'Barrel', bright_metal or air)
            spawn_sm(cube, (bx, cy, cz + 1.2), (0.03, 0.08, 0.2), None, PREFIX + 'FrontSight', unlit_w or white)
            spawn_sm(cube, (bx - 12, cy, cz + 0.5), (0.05, 0.18, 0.12), None, PREFIX + 'RearSight', panel)
            spawn_sm(sphere, (bx - 15, cy - 1.4, cz - 0.9), (0.24, 0.17, 0.13), None, PREFIX + 'Glove', leather)
            for fi in range(4):
                spawn_sm(cyl, (bx - 12, cy - 1.2 + fi * 0.24, cz - 0.5), (0.04, 0.04, 0.18), unreal.Rotator(70, 0, 0), PREFIX + 'Finger_%d' % fi, leather)
            for i in range(18):
                spawn_sm(sphere, (bx + 4 + i * 3.2, cy, cz + 0.9), (0.1, 0.1, 0.1), None, PREFIX + 'Muzzle_%d' % i, muzzle or hi(i))

        if name == 'City':
            for i in range(36):
                h = 3 + (i % 8)
                spawn_sm(cube, (bx + 10, cy - 50 + i * 2.8, cz - 8 + h * 2), (1.3, 1.1, h), None, PREFIX + 'MiniBldg_%d' % i, bright_brick if i % 2 == 0 else plaster)
                spawn_sm(cube, (bx + 17, cy - 50 + i * 2.8, cz + 2), (0.08, 0.7, 0.35), None, PREFIX + 'Win_%d' % i, unlit_y if i % 2 == 0 else panel)
            for i in range(20):
                spawn_sm(cube, (bx + 2, cy - 40 + i * 4, cz - 16), (0.25, 2.2, 0.08), None, PREFIX + 'Road_%d' % i, asphalt)
                spawn_sm(cube, (bx + 2, cy - 40 + i * 4, cz - 15.5), (0.08, 0.9, 0.04), None, PREFIX + 'Lane_%d' % i, unlit_w or white)

        if name == 'Combat':
            drone_parts = list_static_meshes('/Game/Skyguard/Meshes/WebGame/skyguard-drone')
            for i, (path, mesh) in enumerate(drone_parts[:8]):
                scd = 180.0 / bounds_max(mesh)
                if scd > 40:
                    scd = 1.0
                spawn_sm(mesh, (bx + i * 8, cy - 8 + (i % 3) * 6, cz + (i % 4) * 4), (scd, scd, scd), unreal.Rotator(0, 180, 0), PREFIX + 'Drone_%d' % i)
            for i in range(16):
                spawn_sm(sphere, (bx + i * 5, cy - 8 + (i % 4) * 5, cz + (i % 3) * 4), (0.95, 0.95, 0.95), None, PREFIX + 'Burst_%d' % i, boom or hi(i))
                spawn_sm(cube, (bx + 15 + i * 2.5, cy, cz), (0.12, 0.12, 1.8), None, PREFIX + 'Tracer_%d' % i, unlit_y or muzzle)

        if name in ('Harbor', 'Ocean'):
            for i in range(24):
                spawn_sm(plane, (bx + 4, cy - 45 + i * 3.8, cz - 18), (3.2, 3.2, 1), unreal.Rotator(90, 0, 0), PREFIX + 'Wave_%s_%d' % (name, i), bright_ocean or ocean)
                spawn_sm(cube, (bx + 7, cy - 45 + i * 3.8, cz - 16), (0.7, 1.4, 0.1), None, PREFIX + 'Foam_%s_%d' % (name, i), foam or unlit_w)
            if name == 'Harbor':
                for i in range(6):
                    spawn_sm(cube, (bx + 14, cy - 25 + i * 9, cz + 2), (0.9, 0.9, 6.5), None, PREFIX + 'Crane_%d' % i, air)
                    spawn_sm(cube, (bx + 28, cy - 25 + i * 9, cz + 10), (8.5, 0.4, 0.4), None, PREFIX + 'Boom_%d' % i, panel)

    meshes = list_static_meshes('/Game/Skyguard/Meshes/WebGame/yak52-detail-kit')
    prod = []
    for path, mesh in meshes:
        n = path.split('/')[-1].split('.')[0]
        low = n.lower()
        if low.startswith('production-') or 'yak52' in low:
            prod.append((path, mesh, n, low))
    ref = None
    for path, mesh, n, low in prod:
        if 'wings-tail' in low or 'exterior' in low or 'fuselage' in low:
            ref = mesh
            break
    sc = 1.0
    if ref:
        sc = 950.0 / bounds_max(ref)
        if sc > 20:
            sc = 1.0
        if sc < 0.02:
            sc = 0.25
    s = (sc, sc, sc)
    log('yak prod=%d scale=%s' % (len(prod), s))
    origin = (360.0, -180.0, 410.0)
    for path, mesh, n, low in prod:
        mat = air
        if any(k in low for k in ['panel', 'instrument', 'gauge', 'annunciator', 'bezel', 'needle']):
            mat = panel
        if 'glass' in low or 'canopy' in low:
            mat = canopy or glass or panel
        if 'upholstery' in low or 'quilt' in low:
            mat = leather
        spawn_sm(mesh, origin, s, None, PREFIX + 'Yak_%s' % n[:40], mat)

    for i in range(55):
        x = -1900 - (i % 8) * 120
        y = -2600 + (i // 8) * 280
        h = 7 + (i * 5) % 10
        spawn_sm(cube, (x, y, 35 + h * 14), (2.4, 2.0, h), None, PREFIX + 'Bldg_%d' % i, bright_brick if i % 2 == 0 else plaster)
        for w in range(min(h, 6)):
            spawn_sm(cube, (x + 25, y, 55 + w * 28), (0.08, 0.75, 0.26), None, PREFIX + 'W_%d_%d' % (i, w), unlit_y if w % 2 == 0 else panel)
    for i, y in enumerate(range(-2600, 2601, 170)):
        spawn_sm(cube, (-1500, y, 32), (12, 5, 0.12), None, PREFIX + 'RoadW_%d' % i, asphalt)
    for i, x in enumerate([600, 1800, 3000]):
        for j, y in enumerate(range(-2800, 2801, 1100)):
            spawn_sm(plane, (x, y, 0.4), (120, 120, 1), None, PREFIX + 'OceanW_%d_%d' % (i, j), ocean)

    sun = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 5200), unreal.Rotator(-26, 38, 0))
    if sun:
        sun.set_actor_label(PREFIX + 'Sun')
        try:
            c = sun.get_component_by_class(unreal.DirectionalLightComponent)
            if c:
                c.set_intensity(19.0)
                c.set_mobility(unreal.ComponentMobility.MOVABLE)
        except Exception as e:
            log('sun ' + str(e))
    sky = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 1500), unreal.Rotator())
    if sky:
        sky.set_actor_label(PREFIX + 'Sky')
        try:
            c = sky.get_component_by_class(unreal.SkyLightComponent)
            if c:
                c.set_intensity(3.5)
                c.set_editor_property('real_time_capture', True)
        except Exception:
            pass
    for i, (loc, intens) in enumerate([
        ((100, 0, 500), 200000.0), ((95, 240, 500), 180000.0), ((95, -240, 500), 180000.0),
        ((360, -180, 430), 170000.0), ((95, 110, 380), 190000.0), ((70, 150, 370), 150000.0),
        ((-690, -220, 280), 170000.0), ((850, 10, 450), 150000.0), ((-90, -160, 160), 140000.0),
        ((830, -20, 120), 140000.0), ((340, -400, 400), 150000.0),
    ]):
        pl = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*loc), unreal.Rotator())
        if pl:
            pl.set_actor_label(PREFIX + 'Pt_%d' % i)
            try:
                c = pl.get_component_by_class(unreal.PointLightComponent)
                if c:
                    c.set_intensity(intens)
                    c.set_editor_property('attenuation_radius', 4200.0)
            except Exception:
                pass
    try:
        unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SkyAtmosphere, unreal.Vector(0, 0, 0), unreal.Rotator()).set_actor_label(PREFIX + 'Atmo')
    except Exception:
        pass
    pp = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0, 0, 200), unreal.Rotator())
    if pp:
        pp.set_actor_label(PREFIX + 'PP')
        try:
            pp.set_editor_property('unbound', True)
        except Exception:
            pass
    try:
        for cls_path, loc, label in [
            ('/Script/Skyguard52.SkyguardGunner', (40, 110, 370), PREFIX + 'CPP_Gunner'),
            ('/Script/Skyguard52.SkyguardDroneSpawner', (2200, 0, 520), PREFIX + 'CPP_Spawner'),
            ('/Script/Skyguard52.SkyguardPropSpinner', (95, 0, 500), PREFIX + 'PropSpinner'),
        ]:
            cls = unreal.load_class(None, cls_path)
            if cls:
                a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator())
                if a:
                    a.set_actor_label(label)
                    try:
                        a.set_actor_location(unreal.Vector(*loc), False, True)
                    except Exception:
                        pass
    except Exception as e:
        log('cpp ' + str(e))
    log('loop30 densify done')
    return stages

def capture(out_dir, stages):
    os.makedirs(out_dir, exist_ok=True)
    ensure_dir('/Game/Skyguard/Capture')
    if unreal.EditorAssetLibrary.does_asset_exist(RT_PATH):
        rt = unreal.EditorAssetLibrary.load_asset(RT_PATH)
    else:
        rt = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            'RT_AAA_L30', '/Game/Skyguard/Capture', unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew()
        )
    rt.set_editor_property('size_x', 1920)
    rt.set_editor_property('size_y', 1080)
    try:
        rt.set_editor_property('render_target_format', unreal.TextureRenderTargetFormat.RTF_RGBA8)
    except Exception:
        pass
    unreal.EditorAssetLibrary.save_loaded_asset(rt)

    cams = [('AAA_Cam_L30_%s' % name, cam, (0.0, 0.0, 0.0)) for name, cam, dist, ny, nz in stages]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
            try:
                c.set_actor_location(unreal.Vector(*loc), False, True)
            except Exception:
                pass

    sca = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, 0, 400), unreal.Rotator())
    sca.set_actor_label(PREFIX + 'SceneCapture')
    comp = sca.get_editor_property('capture_component2d')
    comp.set_editor_property('texture_target', rt)
    try:
        comp.set_editor_property('capture_every_frame', False)
    except Exception:
        pass
    try:
        comp.set_editor_property('capture_on_movement', False)
    except Exception:
        pass
    try:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    except Exception:
        world = unreal.EditorLevelLibrary.get_editor_world()

    sources = []
    try:
        sources.append(('BASE', unreal.SceneCaptureSource.SCS_BASE_COLOR))
    except Exception:
        pass
    try:
        sources.append(('FINAL', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR))
    except Exception:
        pass
    try:
        sources.append(('SCENE', unreal.SceneCaptureSource.SCS_SCENE_COLOR_HDR))
    except Exception:
        if not sources:
            sources.append(('DEFAULT', None))

    saved = []
    for name, loc, rot in cams:
        try:
            comp.set_editor_property('fov_angle', 92.0)
        except Exception:
            pass
        for src_name, enum in sources:
            try:
                if enum is not None:
                    comp.set_editor_property('capture_source', enum)
            except Exception as e:
                log('src ' + str(e))
            sca.set_actor_location(unreal.Vector(*loc), False, True)
            sca.set_actor_rotation(unreal.Rotator(*rot), False)
            for _ in range(5):
                try:
                    comp.capture_scene()
                except Exception:
                    pass
            out_name = '%s_%s.png' % (name, src_name)
            out_png = os.path.join(out_dir, out_name)
            if os.path.isfile(out_png):
                try:
                    os.remove(out_png)
                except Exception:
                    pass
            try:
                unreal.RenderingLibrary.export_render_target(world, rt, out_dir, out_name)
            except Exception as e:
                log('export ' + out_name + ' ' + str(e))
            if os.path.isfile(out_png):
                size = os.path.getsize(out_png)
                h = hashlib.sha256(open(out_png, 'rb').read()).hexdigest()
                log('still %s size=%d sha=%s' % (out_name, size, h[:16]))
                saved.append((out_png, size, h, src_name, name))
    man = os.path.join(out_dir, 'MANIFEST_SHA256.txt')
    with open(man, 'w', encoding='utf-8') as f:
        f.write('Skyguard AAA Loop30 stills\n')
        f.write('time=%s\n' % time.strftime('%Y-%m-%dT%H:%M:%S'))
        f.write('note=host_pillow_selects_best; cockpit HF + prop hero metal; yaw0 boards\n')
        for path, size, h, src, name in saved:
            f.write('%s  %d  src=%s cam=%s  %s\n' % (h, size, src, name, path))
        f.write('total=%d\n' % len(saved))
    log('manifest total=%d' % len(saved))
    return saved

def main():
    log('loop30 cockpit HF + prop hero metal densify start')
    unreal.EditorLevelLibrary.load_level(MAP_PATH)
    clear_old()
    stages = densify()
    saved = capture(OUT_DIR, stages)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory('/Game/Skyguard', False, True)
    log('Loop30 complete stills=%d' % (len(saved) if saved else 0))
    log('CRITIC: host RGB select+audit required; overall FAIL until blind AAA win')

main()
