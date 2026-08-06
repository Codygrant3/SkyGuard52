import unreal

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
    unreal.EditorLevelLibrary.load_level("/Game/Skyguard/Maps/Lvl_SkyguardCoast")
    clear_prefix("AAA_L4_")
    cube = mesh("/Engine/BasicShapes/Cube")
    sphere = mesh("/Engine/BasicShapes/Sphere")
    cyl = mesh("/Engine/BasicShapes/Cylinder")
    cone = mesh("/Engine/BasicShapes/Cone")
    plane = mesh("/Engine/BasicShapes/Plane")
    concrete = mat("/Game/Skyguard/Materials/M_Tex_L3_rock") or mat("/Game/Skyguard/Materials/M_Tex_concrete")
    brick = mat("/Game/Skyguard/Materials/M_Tex_brick") or concrete
    plaster = mat("/Game/Skyguard/Materials/M_Tex_plaster") or concrete
    glass = mat("/Game/Skyguard/Materials/M_CityGlass")
    asphalt = mat("/Game/Skyguard/Materials/M_Tex_L3_asphalt2") or mat("/Game/Skyguard/Materials/M_Asphalt")
    sand = mat("/Game/Skyguard/Materials/M_Tex_L3_sand") or mat("/Game/Skyguard/Materials/M_Beach")
    wet = mat("/Game/Skyguard/Materials/M_WetSand") or sand
    wood = mat("/Game/Skyguard/Materials/M_Tex_L3_wood2") or mat("/Game/Skyguard/Materials/M_PierWood")
    plate = mat("/Game/Skyguard/Materials/M_Tex_L3_plate") or mat("/Game/Skyguard/Materials/M_Tex_metal")
    roof = mat("/Game/Skyguard/Materials/M_Tex_L3_roof") or plate
    leather = mat("/Game/Skyguard/Materials/M_Tex_leather") or mat("/Game/Skyguard/Materials/M_LeatherGlove")
    rifle = mat("/Game/Skyguard/Materials/M_RifleTan") or plate
    canopy = mat("/Game/Skyguard/Materials/M_CockpitGlass") or glass
    ocean = mat("/Game/Skyguard/Materials/M_Ocean")
    deep = mat("/Game/Skyguard/Materials/M_OceanDeep")
    exhaust = mat("/Game/Skyguard/Materials/M_ExhaustGlow")
    foliage = mat("/Game/Skyguard/Materials/M_Foliage")
    cockpit = mat("/Game/Skyguard/Materials/M_CockpitInterior") or leather
    air = mat("/Game/Skyguard/Materials/M_Tex_airframe_metal") or plate
    prop = mat("/Game/Skyguard/Materials/M_PropDisc") or plate

    sm(plane, (2800, 0, -18), (700, 700, 1), None, "AAA_L4_OceanDeep", deep)
    sm(plane, (900, 0, -8), (420, 520, 1), None, "AAA_L4_OceanNear", ocean)
    for i, y in enumerate(range(-3200, 3201, 180)):
        sm(cube, (-760, y, 2), (2.2, 8.5, 0.08), None, "AAA_L4_FoamLine_%d" % i, wet)
        sm(sphere, (-720, y + 40, 4), (0.8, 1.6, 0.25), None, "AAA_L4_WaveCrest_%d" % i, ocean)
        if i % 3 == 0:
            sm(sphere, (-680, y, 6), (0.4, 0.9, 0.2), None, "AAA_L4_Spray_%d" % i, exhaust)
    idx = 0
    for district, x0 in enumerate([-2400, -2050, -1700]):
        for i in range(14):
            for j in range(10):
                y = -2400 + i * 360 + (district % 2) * 80
                x = x0 - j * 95
                h = 4 + ((i * 3 + j * 5 + district * 7) % 18)
                z = 40 + h * 18
                m = glass if h > 12 else (brick if (i + j) % 2 == 0 else plaster)
                sm(cube, (x, y, z * 0.5), (3.2, 3.0, h), None, "AAA_L4_Tower_%d" % idx, m)
                sm(cube, (x, y, z + 8), (3.3, 3.1, 0.25), None, "AAA_L4_RoofDeck_%d" % idx, roof)
                sm(cube, (x + 16, y, z * 0.55), (0.12, 2.7, h * 0.85), None, "AAA_L4_WindowStrip_%d" % idx, glass)
                if idx % 4 == 0:
                    sm(cyl, (x, y, z + 30), (0.08, 0.08, 1.4), None, "AAA_L4_Antenna_%d" % idx, plate)
                if idx % 5 == 0:
                    sm(cube, (x + 10, y + 10, z + 18), (0.5, 0.5, 0.4), None, "AAA_L4_HVAC_%d" % idx, plate)
                idx += 1
    for i, y in enumerate(range(-2500, 2501, 160)):
        sm(cube, (-1880, y, 38), (1.6, 0.7, 0.55), None, "AAA_L4_Vehicle_%d" % i, plate if i % 2 else brick)
        sm(cyl, (-1850, y + 40, 55), (0.08, 0.08, 1.5), None, "AAA_L4_Lamp_%d" % i, plate)
        sm(sphere, (-1850, y + 40, 85), (0.18, 0.18, 0.18), None, "AAA_L4_LampHead_%d" % i, exhaust)
        if i % 2 == 0:
            sm(cube, (-1905, y, 34.5), (2.0, 0.15, 0.03), None, "AAA_L4_Crosswalk_%d" % i, plaster)
        if i % 4 == 0:
            sm(cyl, (-1960, y, 50), (0.18, 0.18, 1.0), None, "AAA_L4_TreeTrunk_%d" % i, wood)
            sm(sphere, (-1960, y, 90), (0.9, 0.9, 0.7), None, "AAA_L4_TreeCanopy_%d" % i, foliage)

    sm(sphere, (-1550, -1200, 160), (3.5, 3.5, 2.2), None, "AAA_L4_Landmark_Radar", plate)
    sm(cube, (-1500, 900, 90), (2.5, 4.0, 4.0), None, "AAA_L4_Landmark_ChurchBody", plaster)
    sm(cone, (-1500, 900, 190), (1.2, 1.2, 2.2), None, "AAA_L4_Landmark_Spire", roof)
    sm(cyl, (-2100, 0, 70), (8.0, 8.0, 0.35), None, "AAA_L4_Landmark_Stadium", concrete)
    for k in range(8):
        sm(cube, (-2300, -400 + k * 90, 90), (1.5, 1.5, 3.5 + k * 0.2), None, "AAA_L4_Landmark_Stacks_%d" % k, plate)
    for i, y in enumerate([-1400, -700, 0, 700, 1400, 2100]):
        sm(cube, (-540, y, 26), (16, 1.8, 0.5), None, "AAA_L4_Pier_%d" % i, wood)
        sm(cube, (-300, y, 110), (0.9, 0.9, 5.0), None, "AAA_L4_CraneMast_%d" % i, plate)
        sm(cube, (-180, y, 210), (6.5, 0.6, 0.4), None, "AAA_L4_CraneArm_%d" % i, plate)
        for c in range(4):
            sm(cube, (-420 + c * 35, y + 40, 35 + (c % 2) * 20), (1.4, 2.2, 1.1), None, "AAA_L4_Container_%d_%d" % (i, c), plate if c % 2 else brick)
        sm(cube, (-250, y - 60, 40), (3.0, 1.2, 1.5), None, "AAA_L4_Warehouse_%d" % i, concrete)
    sm(cyl, (1750, 600, 4), (1.3, 1.3, 10.0), unreal.Rotator(0, 0, 90), "AAA_L4_SubBody", plate)
    sm(cube, (1650, 600, 40), (0.6, 1.4, 1.5), None, "AAA_L4_SubSail", plate)
    sm(cyl, (1920, 600, 4), (0.55, 0.55, 1.5), unreal.Rotator(0, 0, 90), "AAA_L4_SubNose", plate)
    sm(cube, (1650, 600, 70), (0.15, 0.15, 1.2), None, "AAA_L4_SubPeriscope", plate)

    sm(cyl, (0, 40, 320), (1.5, 1.5, 10.5), unreal.Rotator(0, 0, 90), "AAA_L4_Yak_Fuselage", air)
    sm(sphere, (0, -470, 320), (1.4, 1.8, 1.4), None, "AAA_L4_Yak_Nose", air)
    sm(cube, (0, 10, 302), (18, 2.4, 0.22), None, "AAA_L4_Yak_Wing", air)
    sm(cube, (0, 500, 405), (0.22, 1.5, 3.0), None, "AAA_L4_Yak_Fin", air)
    sm(cube, (0, 480, 338), (5.4, 1.4, 0.18), None, "AAA_L4_Yak_Stab", air)
    for i, y in enumerate([-300, -150, 0, 150, 300]):
        sm(cube, (0, y, 335), (1.52, 0.05, 0.02), None, "AAA_L4_Yak_PanelLine_%d" % i, plate)
    for i, y in enumerate([-140, -60, 20, 100, 180, 250, 300]):
        sm(cyl, (0, y, 374), (1.22, 0.07, 0.07), unreal.Rotator(0, 0, 90), "AAA_L4_Yak_Bow_%d" % i, plate)
    sm(sphere, (0, -90, 376), (1.08, 1.55, 0.78), None, "AAA_L4_Yak_CanopyFront", canopy)
    sm(cube, (1.0, 90, 376), (0.05, 2.4, 0.58), None, "AAA_L4_Yak_CanopyRailR", plate)
    sm(cube, (-1.0, 90, 376), (0.05, 2.4, 0.58), None, "AAA_L4_Yak_CanopyRailL", plate)
    sm(cube, (0, 75, 348), (1.6, 2.0, 0.09), None, "AAA_L4_Yak_GunnerFloor", cockpit)
    sm(cube, (0, -28, 360), (1.4, 0.2, 0.65), None, "AAA_L4_Yak_Panel", plate)
    for i, x in enumerate([-50, -30, -10, 10, 30, 50, -20, 20]):
        sm(cyl, (x, -20, 370), (0.09, 0.09, 0.03), None, "AAA_L4_Yak_Gauge_%d" % i, glass)
    sm(cube, (0, 55, 355), (0.7, 0.7, 0.55), None, "AAA_L4_Yak_Seat", leather)
    sm(cyl, (0, 35, 360), (0.05, 0.05, 0.45), None, "AAA_L4_Yak_Stick", plate)
    sm(cube, (-15, 25, 350), (0.25, 0.08, 0.05), None, "AAA_L4_Yak_PedalL", plate)
    sm(cube, (15, 25, 350), (0.25, 0.08, 0.05), None, "AAA_L4_Yak_PedalR", plate)
    sm(cyl, (0, -560, 320), (2.1, 2.1, 0.07), unreal.Rotator(0, 0, 90), "AAA_L4_Yak_PropDisc", prop)
    for i in range(6):
        sm(cube, (0, -560, 320), (0.1, 2.4, 0.05), unreal.Rotator(0, 0, i * 30), "AAA_L4_Yak_PropBlade_%d" % i, plate)
    sm(cyl, (-130, -30, 245), (0.13, 0.13, 1.1), None, "AAA_L4_Yak_GearL", plate)
    sm(cyl, (130, -30, 245), (0.13, 0.13, 1.1), None, "AAA_L4_Yak_GearR", plate)
    sm(sphere, (-130, -30, 205), (0.38, 0.16, 0.38), None, "AAA_L4_Yak_WheelL", plate)
    sm(sphere, (130, -30, 205), (0.38, 0.16, 0.38), None, "AAA_L4_Yak_WheelR", plate)

    sm(cyl, (18, 125, 360), (0.055, 0.055, 1.25), unreal.Rotator(0, 10, 0), "AAA_L4_Rifle_Barrel", rifle)
    sm(cube, (18, 72, 358), (0.16, 0.45, 0.14), unreal.Rotator(0, 10, 0), "AAA_L4_Rifle_Receiver", rifle)
    sm(cube, (18, 52, 352), (0.13, 0.28, 0.11), unreal.Rotator(0, 10, 8), "AAA_L4_Rifle_Stock", rifle)
    sm(cube, (18, 98, 351), (0.05, 0.14, 0.22), unreal.Rotator(0, 10, 0), "AAA_L4_Rifle_Mag", rifle)
    sm(cube, (18, 145, 370), (0.03, 0.03, 0.12), None, "AAA_L4_Rifle_FrontSightPost", plate)
    sm(cube, (18, 145, 365), (0.08, 0.02, 0.03), None, "AAA_L4_Rifle_FrontSightBase", plate)
    sm(cube, (18, 78, 370), (0.07, 0.02, 0.12), None, "AAA_L4_Rifle_RearSightAperture", plate)
    sm(cube, (18, 78, 366), (0.1, 0.03, 0.04), None, "AAA_L4_Rifle_RearSightBase", plate)
    sm(sphere, (22, 82, 352), (0.12, 0.15, 0.1), None, "AAA_L4_Hand_Palm", leather)
    for fi, off in enumerate([(-4, 0), (0, 2), (4, 1), (7, -1)]):
        sm(cyl, (22 + off[0], 84 + off[1], 345), (0.025, 0.025, 0.12), unreal.Rotator(90, 8, 0), "AAA_L4_Hand_Finger_%d" % fi, leather)
    sm(cyl, (20, 55, 340), (0.09, 0.09, 0.6), unreal.Rotator(78, 12, 0), "AAA_L4_Arm_Forearm", leather)
    sm(cyl, (8, 25, 328), (0.12, 0.12, 0.5), unreal.Rotator(68, 18, 0), "AAA_L4_Arm_Upper", leather)
    sm(sphere, (4, 8, 320), (0.16, 0.14, 0.14), None, "AAA_L4_Arm_Shoulder", leather)
    sm(cyl, (-32, 95, 355), (0.11, 0.11, 1.5), unreal.Rotator(0, -8, 5), "AAA_L4_Igla_Tube", plate)
    sm(cube, (-32, 55, 355), (0.2, 0.28, 0.2), unreal.Rotator(0, -8, 5), "AAA_L4_Igla_Grip", plate)
    sm(sphere, (-32, 40, 355), (0.13, 0.13, 0.13), None, "AAA_L4_Igla_Optic", glass)
    sm(cyl, (-32, 165, 358), (0.05, 0.05, 0.75), unreal.Rotator(0, -8, 5), "AAA_L4_Igla_MissileNose", plate)
    sm(cone, (-32, 185, 358), (0.08, 0.08, 0.2), unreal.Rotator(0, -8, 5), "AAA_L4_Igla_MissileTip", exhaust)
    for lane, y in enumerate([-2200, -1400, -600, 200, 1000, 1800, 2600]):
        for n in range(7):
            x = 2500 + n * 480 + (lane % 2) * 150
            z = 370 + (n % 5) * 48
            heavy = (n % 4 == 0)
            scale = (1.55, 1.55, 4.0) if heavy else (1.2, 1.2, 3.3)
            sm(cone, (x, y, z), scale, unreal.Rotator(0, -90, 0), "AAA_L4_Drone_%d_%d" % (lane, n), plate)
            sm(cube, (x - 45, y, z), (3.3 if heavy else 2.8, 0.18, 0.09), None, "AAA_L4_DroneWing_%d_%d" % (lane, n), plate)
            sm(sphere, (x + 130, y, z), (0.25, 0.25, 0.25), None, "AAA_L4_DroneEx_%d_%d" % (lane, n), exhaust)
    for i in range(20):
        sm(sphere, (80 + i * 15, 130 + i * 3, 365), (0.08, 0.08, 0.08), None, "AAA_L4_VFX_Muzzle_%d" % i, exhaust)
    for i in range(12):
        sm(sphere, (-1400, -900 + i * 160, 120 + (i % 3) * 40), (1.2, 1.2, 1.0), None, "AAA_L4_VFX_Flak_%d" % i, exhaust)
    for i in range(15):
        sm(cyl, (1800 + i * 40, -300 + i * 50, 420), (0.05, 0.05, 2.5), unreal.Rotator(0, 90, 10), "AAA_L4_VFX_Contrail_%d" % i, glass)
    cams = [
        ("AAA_Cam_L4_Cockpit", (30, 100, 372), (-8, 8, 0)),
        ("AAA_Cam_L4_ADS_Iron", (18, 132, 366), (-1, 8, 0)),
        ("AAA_Cam_L4_CityCanyon", (-1900, 0, 180), (-8, 0, 0)),
        ("AAA_Cam_L4_Harbor", (-400, -1000, 240), (-10, 35, 0)),
        ("AAA_Cam_L4_Ocean", (1200, -1500, 300), (-12, 40, 0)),
        ("AAA_Cam_L4_Swarm", (3000, 0, 750), (-15, -180, 0)),
        ("AAA_Cam_L4_ExteriorYak", (650, -1200, 520), (-10, 140, 0)),
    ]
    for name, loc, rot in cams:
        c = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), unreal.Rotator(*rot))
        if c:
            c.set_actor_label(name)
    unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard", False, True)
    log("Loop4 megacity densification complete")
    log("CRITIC EXPECTED: still FAIL vs AAA (proxy geometry remains)")

if __name__ == "__main__":
    main()
