import unreal

def log(m):
    unreal.log('[SkyguardAAA] ' + str(m))

def clear_prefix(prefix):
    for a in list(unreal.EditorLevelLibrary.get_all_level_actors()):
        try:
            n = a.get_actor_label()
            if n and n.startswith(prefix):
                unreal.EditorLevelLibrary.destroy_actor(a)
        except Exception:
            pass

def mesh(path):
    return unreal.EditorAssetLibrary.load_asset(path)

def mat(path):
    return unreal.EditorAssetLibrary.load_asset(path)

def sm(mesh_asset, loc, scale=None, rot=None, label=None, material=None):
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc), rot or unreal.Rotator())
    if not a:
        return None
    c = a.static_mesh_component
    c.set_static_mesh(mesh_asset)
    if scale:
        a.set_actor_scale3d(unreal.Vector(*scale))
    if label:
        a.set_actor_label(label)
    if material:
        c.set_material(0, material)
    return a

def main():
    unreal.EditorLevelLibrary.load_level('/Game/Skyguard/Maps/Lvl_SkyguardCoast')
    clear_prefix('AAA_L3_')
    cube = mesh('/Engine/BasicShapes/Cube')
    sphere = mesh('/Engine/BasicShapes/Sphere')
    cyl = mesh('/Engine/BasicShapes/Cylinder')
    cone = mesh('/Engine/BasicShapes/Cone')
    air = mat('/Game/Skyguard/Materials/M_Tex_airframe_metal') or mat('/Game/Skyguard/Materials/M_YakAirframe')
    metal = mat('/Game/Skyguard/Materials/M_Tex_metal') or mat('/Game/Skyguard/Materials/M_Metal')
    leather = mat('/Game/Skyguard/Materials/M_Tex_leather') or mat('/Game/Skyguard/Materials/M_LeatherGlove')
    concrete = mat('/Game/Skyguard/Materials/M_Tex_concrete') or mat('/Game/Skyguard/Materials/M_CityConcrete')
    brick = mat('/Game/Skyguard/Materials/M_Tex_brick') or concrete
    plaster = mat('/Game/Skyguard/Materials/M_Tex_plaster') or concrete
    glass = mat('/Game/Skyguard/Materials/M_CityGlass')
    asphalt = mat('/Game/Skyguard/Materials/M_Asphalt') or mat('/Game/Skyguard/Materials/M_Road')
    sand = mat('/Game/Skyguard/Materials/M_Beach') or mat('/Game/Skyguard/Materials/M_Sand')
    wet = mat('/Game/Skyguard/Materials/M_WetSand') or sand
    wood = mat('/Game/Skyguard/Materials/M_PierWood')
    rust = mat('/Game/Skyguard/Materials/M_MetalRust') or metal
    prop = mat('/Game/Skyguard/Materials/M_PropDisc') or metal
    rifle = mat('/Game/Skyguard/Materials/M_RifleTan') or metal
    exhaust = mat('/Game/Skyguard/Materials/M_ExhaustGlow')
    canopy = mat('/Game/Skyguard/Materials/M_CockpitGlass') or glass
    foliage = mat('/Game/Skyguard/Materials/M_Foliage')
    cockpit = mat('/Game/Skyguard/Materials/M_CockpitInterior') or leather
    gauge = mat('/Game/Skyguard/Materials/M_GaugeGlass') or glass
    for i, y0 in enumerate(range(-2800, 2801, 118)):
        sm(cube, (-2100, y0, 20), (55, 5.9, 0.6), None, 'AAA_L3_TerrainDistrict_%d' % i, concrete)
        sm(cube, (-1900, y0, 34), (4.5, 5.8, 0.12), None, 'AAA_L3_Road_%d' % i, asphalt)
        sm(cube, (-1860, y0, 35), (0.5, 5.8, 0.08), None, 'AAA_L3_Sidewalk_%d' % i, plaster)
        for k in range(3):
            yy = y0 - 40 + k * 40
            sm(cyl, (-2000, yy, 55), (0.15, 0.15, 0.9), None, 'AAA_L3_Trunk_%d_%d' % (i, k), wood)
            sm(sphere, (-2000, yy, 95), (0.7, 0.7, 0.55), None, 'AAA_L3_Canopy_%d_%d' % (i, k), foliage)
            sm(cube, (-1830, yy, 40), (0.9, 0.45, 0.35), None, 'AAA_L3_Car_%d_%d' % (i, k), metal)
            sm(cube, (-1750, yy + 15, 70 + (k % 2) * 40), (1.2, 1.0, 2.4 + (k % 3)), None, 'AAA_L3_LowBld_%d_%d' % (i, k), brick if k % 2 else plaster)
            if k == 1:
                sm(cube, (-1750, yy + 15, 120 + (k % 3) * 20), (1.25, 1.05, 0.12), None, 'AAA_L3_Roof_%d_%d' % (i, k), rust)
    for i, y0 in enumerate(range(-3000, 3001, 200)):
        sm(cube, (-1050, y0, 16), (8, 10, 0.25), None, 'AAA_L3_Beach_%d' % i, sand)
        sm(cube, (-980, y0, 10), (3, 10, 0.15), None, 'AAA_L3_WetSand_%d' % i, wet)
        sm(cube, (-1120, y0, 22), (2, 10, 0.18), None, 'AAA_L3_Promenade_%d' % i, asphalt)
    for i, y in enumerate([-900, -300, 300, 900, 1500]):
        sm(cube, (-620, y, 28), (14, 1.6, 0.45), None, 'AAA_L3_Pier_%d' % i, wood)
        sm(cube, (-420, y, 90), (0.8, 0.8, 4.0), None, 'AAA_L3_CraneMast_%d' % i, rust)
        sm(cube, (-320, y, 175), (5.5, 0.55, 0.35), None, 'AAA_L3_CraneArm_%d' % i, rust)
        sm(cube, (-250, y, 40), (2.5, 1.8, 1.2), None, 'AAA_L3_Container_%d' % i, metal)
        if i == 2:
            sm(cyl, (1600, y + 400, 5), (1.2, 1.2, 8.0), unreal.Rotator(0, 0, 90), 'AAA_L3_SubBody', metal)
            sm(cube, (1500, y + 400, 35), (0.5, 1.2, 1.2), None, 'AAA_L3_SubSail', metal)
            sm(cyl, (1750, y + 400, 5), (0.5, 0.5, 1.2), unreal.Rotator(0, 0, 90), 'AAA_L3_SubNose', metal)
    sm(cyl, (0, 40, 320), (1.45, 1.45, 10.0), unreal.Rotator(0, 0, 90), 'AAA_L3_Yak_Fuselage', air)
    sm(sphere, (0, -450, 320), (1.35, 1.7, 1.35), None, 'AAA_L3_Yak_Nose', air)
    sm(cube, (0, 20, 305), (17, 2.2, 0.2), None, 'AAA_L3_Yak_Wing', air)
    sm(cube, (0, 480, 400), (0.2, 1.4, 2.8), None, 'AAA_L3_Yak_Fin', air)
    sm(cube, (0, 460, 335), (5.0, 1.3, 0.16), None, 'AAA_L3_Yak_Stab', air)
    for i, y in enumerate([-120, -40, 40, 120, 200, 260]):
        sm(cyl, (0, y, 372), (1.2, 0.07, 0.07), unreal.Rotator(0, 0, 90), 'AAA_L3_Yak_Bow_%d' % i, metal)
    sm(sphere, (0, -80, 375), (1.05, 1.5, 0.75), None, 'AAA_L3_Yak_CanopyFront', canopy)
    sm(cube, (0.95, 80, 375), (0.04, 2.2, 0.55), None, 'AAA_L3_Yak_CanopyRailR', metal)
    sm(cube, (-0.95, 80, 375), (0.04, 2.2, 0.55), None, 'AAA_L3_Yak_CanopyRailL', metal)
    sm(cube, (0, 70, 348), (1.55, 1.9, 0.08), None, 'AAA_L3_Yak_GunnerFloor', cockpit)
    sm(cube, (0, -25, 358), (1.35, 0.18, 0.6), None, 'AAA_L3_Yak_Panel', metal)
    for i, x in enumerate([-45, -15, 15, 45, -30, 30]):
        sm(cyl, (x, -18, 368), (0.09, 0.09, 0.03), None, 'AAA_L3_Yak_Gauge_%d' % i, gauge)
    sm(cyl, (0, -540, 320), (2.0, 2.0, 0.06), unreal.Rotator(0, 0, 90), 'AAA_L3_Yak_PropDisc', prop)
    for i in range(4):
        sm(cube, (0, -540, 320), (0.12, 2.3, 0.05), unreal.Rotator(0, 0, i * 45), 'AAA_L3_Yak_PropBlade_%d' % i, metal)
    sm(cyl, (-120, -40, 250), (0.12, 0.12, 1.0), None, 'AAA_L3_Yak_GearL', metal)
    sm(cyl, (120, -40, 250), (0.12, 0.12, 1.0), None, 'AAA_L3_Yak_GearR', metal)
    sm(sphere, (-120, -40, 210), (0.35, 0.15, 0.35), None, 'AAA_L3_Yak_WheelL', metal)
    sm(sphere, (120, -40, 210), (0.35, 0.15, 0.35), None, 'AAA_L3_Yak_WheelR', metal)
    sm(cyl, (18, 120, 360), (0.06, 0.06, 1.2), unreal.Rotator(0, 12, 0), 'AAA_L3_Rifle_Barrel', rifle)
    sm(cube, (18, 70, 358), (0.15, 0.42, 0.13), unreal.Rotator(0, 12, 0), 'AAA_L3_Rifle_Receiver', rifle)
    sm(cube, (18, 55, 352), (0.12, 0.25, 0.1), unreal.Rotator(0, 12, 8), 'AAA_L3_Rifle_Stock', rifle)
    sm(cube, (18, 95, 352), (0.05, 0.12, 0.2), unreal.Rotator(0, 12, 0), 'AAA_L3_Rifle_Mag', rifle)
    sm(cube, (18, 135, 368), (0.03, 0.03, 0.09), None, 'AAA_L3_Rifle_FrontSight', metal)
    sm(cube, (18, 78, 368), (0.05, 0.02, 0.1), None, 'AAA_L3_Rifle_RearSight', metal)
    sm(sphere, (22, 78, 352), (0.11, 0.14, 0.09), None, 'AAA_L3_Hand_Palm', leather)
    sm(cyl, (22, 78, 346), (0.03, 0.03, 0.12), unreal.Rotator(90, 0, 0), 'AAA_L3_Hand_Finger1', leather)
    sm(cyl, (26, 80, 346), (0.025, 0.025, 0.11), unreal.Rotator(90, 10, 0), 'AAA_L3_Hand_Finger2', leather)
    sm(cyl, (18, 80, 346), (0.025, 0.025, 0.11), unreal.Rotator(90, -10, 0), 'AAA_L3_Hand_Finger3', leather)
    sm(cyl, (22, 50, 340), (0.08, 0.08, 0.55), unreal.Rotator(80, 12, 0), 'AAA_L3_Arm_Forearm', leather)
    sm(cyl, (10, 20, 330), (0.11, 0.11, 0.45), unreal.Rotator(70, 20, 0), 'AAA_L3_Arm_Upper', leather)
    sm(cyl, (-30, 90, 355), (0.1, 0.1, 1.4), unreal.Rotator(0, -8, 5), 'AAA_L3_Igla_Tube', rust)
    sm(cube, (-30, 55, 355), (0.18, 0.25, 0.18), unreal.Rotator(0, -8, 5), 'AAA_L3_Igla_Grip', metal)
    sm(sphere, (-30, 40, 355), (0.12, 0.12, 0.12), None, 'AAA_L3_Igla_Optic', glass)
    sm(cyl, (-30, 150, 358), (0.05, 0.05, 0.7), unreal.Rotator(0, -8, 5), 'AAA_L3_Igla_Missile', metal)
    for lane, y in enumerate([-1800, -1000, -200, 600, 1400, 2200]):
        for n in range(5):
            x = 2400 + n * 520 + (lane % 2) * 160
            z = 380 + (n % 4) * 55
            sm(cone, (x, y, z), (1.25, 1.25, 3.4), unreal.Rotator(0, -90, 0), 'AAA_L3_Drone_%d_%d' % (lane, n), metal)
            sm(cube, (x - 40, y, z), (3.0, 0.16, 0.08), None, 'AAA_L3_DroneWing_%d_%d' % (lane, n), metal)
            sm(sphere, (x + 120, y, z), (0.2, 0.2, 0.2), None, 'AAA_L3_DroneEx_%d_%d' % (lane, n), exhaust)
    cams = [
        ('AAA_Cam_L3_Cockpit', (28, 95, 370), (-8, 8, 0)),
        ('AAA_Cam_L3_ADS', (18, 125, 364), (-2, 10, 0)),
        ('AAA_Cam_L3_City', (-1600, 0, 420), (-12, 0, 0)),
        ('AAA_Cam_L3_Harbor', (-500, -800, 260), (-8, 40, 0)),
        ('AAA_Cam_L3_Swarm', (2800, 200, 700), (-14, -180, 0)),
        ('AAA_Cam_L3_Exterior', (700, -1100, 560), (-12, 135, 0)),
    ]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory('/Game/Skyguard', False, True)
    log('Loop3 density pass complete')
    log('CRITIC EXPECTED: still FAIL vs AAA (proxy geometry)')

if __name__ == '__main__':
    main()
