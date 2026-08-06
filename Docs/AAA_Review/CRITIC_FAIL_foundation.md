# AAA Critic Report — Pass Foundation+Lighting

Date: 2026-07-31
Project: D:\Skyguard52
Map: /Game/Skyguard/Maps/Lvl_SkyguardCoast
Engine: UE 5.8.1

## Verdict: **FAIL — not AAA**

Blind A/B mental comparison against:
- MSFS 2024 cockpit/atmosphere
- Battlefield 2042 coastal urban materials/density
- COD modern weapon ADS fidelity

### Side-by-side (harsh)

| Domain | Skyguard now | AAA reference | Better |
|---|---|---|---|
| Ocean | Flat plane + solid color material | FFT/Gerstner water, foam, caustics, SSR/Lumen reflections | **Reference** |
| City | Repeated scaled cubes | Nanite modular kits, unique rooftops, interiors, decals, dirt | **Reference** |
| Aircraft | Primitive fuselage/wings | Authored Yak CAD, rivets, chipped paint, canopy refraction | **Reference** |
| Rifle/ADS | Proxy blocks | High-poly weapon, authentic irons, hand/cloth, recoil cams | **Reference** |
| Lighting | Basic sun/sky/fog (improving) | Guided exposure, volumetrics, godrays, local lights | **Reference** (still ahead) |
| Gameplay systems | Empty BP shells mostly | Full combat loop, AI, audio, destruction | **Reference** |
| Overall | Graybox cinematic intent | Shipping AAA | **Reference** |

### Would a harsh critic be wowed?
**No.** Current state is an improved graybox / previsualization, not triple-A.

### Must-fix before re-review
1. Replace BasicShapes with authored/Fab hero meshes (Yak, rifle, drone, buildings)
2. Water plugin ocean with foam/coastal transition
3. Layered master materials with normal/ORM/dirt/macro variation
4. Fully wired gunner ADS/fire + drone AI + VFX
5. Niagara muzzle/explosion/smoke at cinematic quality
6. Capture high-res screenshots from AAA_Cam_* and re-run blind compare

### What improved this pass
- Project moved to clean path `D:\Skyguard52` (OneDrive path crashed UE)
- AAA plugins enabled (Water, Niagara, PCG, etc.)
- Renderer defaults set for Lumen + VSM + SM6
- Dense city/coast dressing generated
- Expanded material library
- Review cameras placed

### Next loop owners
- World/Water agent
- Cockpit/Weapon agent
- Drone/VFX agent
- Critic agent (reject until wowed)
