# Skyguard52 Luna Proposal Farm — Prompt Pack + Ranking Schema
Updated: 2026-07-31
Goal: farm capture-safe AAA art proposals under L52 freeze. Luna discovers. Host audit + harsh critic accept.

## Authority order
1. Host Pillow RGB audit (usable/partial/fail per camera)
2. Harsh critic blind A/B vs MSFS / BF-COD class refs
3. Capture freeze recipe (L52)
4. Luna proposals (cheap discovery only)

Luna is never final acceptance.

## Freeze law (paste into every Luna prompt)

CAPTURE FREEZE = Loop52
- Project: D:\Skyguard52
- Map: /Game/Skyguard/Maps/Lvl_SkyguardCoast
- Recipe script: Scripts/build_skyguard_aaa_loop52_cockpit_combat_hf_capture.py
- Result: 11/11 cameras usable
- Cameras (yaw0 look +X): Prop, PropHub, PropNose, YakBeauty, Cockpit, ADS, City, Combat, Harbor, Ocean, Wide

HARD RULES
1. Keep L52 unlit high-frequency densify in FOV (wall plane x ~= bx+1/+2).
2. NO dark PBR / dark metal as sole FOV material.
3. NO extreme sun/sky boosts that wash uniqueness.
4. Hero/authored content only BEHIND wall (x >= bx+3) OR additive small emissive proxies.
5. One proposal = one implementable change.
6. Must improve at least one AAA pillar without dropping any camera below Usable.

PILLARS STILL FAILING (harsh critic)
- Materials / weathering
- Aircraft panel fidelity
- City / Ocean beauty
- Weapon / ADS beauty
- Niagara VFX beauty

---

## Shared JSON schema (required output)

Return ONLY valid JSON array of proposals. No markdown. No prose before/after.

```json
[
  {
    "id": "MAT-001",
    "pillar": "materials|aircraft|city_ocean|weapon_ads|vfx",
    "title": "short title <= 80 chars",
    "change": "one concrete change",
    "stage_targets": ["Prop","YakBeauty"],
    "placement": "behind_wall|additive_emissive|unlit_hf_only",
    "assets": {
      "meshes": ["/Game/Skyguard/Meshes/Hero/..."],
      "materials": ["/Game/Skyguard/Materials/..."],
      "textures": ["/Game/Skyguard/Textures/..."],
      "niagara": ["/Game/Skyguard/VFX/..."]
    },
    "implementation_notes": "exact densify/spawn/material steps",
    "expected_metric_effect": {
      "uniq_delta": "up|flat|down",
      "edge_delta": "up|flat|down",
      "black_delta": "up|flat|down",
      "cameras_helped": ["YakBeauty"],
      "cameras_risk": ["Prop"]
    },
    "capture_safe_reason": "why this cannot repeat L46/L48 failures",
    "acceptance_test": "what host audit + visual check must show",
    "effort": "S|M|L",
    "priority_guess": 1,
    "risk": "low|med|high"
  }
]
```

Field constraints:
- stage_targets ⊆ known cameras
- placement must be one of the 3 enums
- effort S = one loop, M = 1-2 loops, L = multi-loop (prefer S/M)
- priority_guess 1 = highest
- risk high almost always rejected unless unique breakthrough

---

## Master system prompt (common header)

```
You are Luna, a high-volume proposal generator for Skyguard52 AAA Unreal densify loops.
You do not implement. You do not re-open capture recipe debates.
You output only JSON proposals that obey CAPTURE FREEZE L52 and HARD RULES.
Prefer small, verifiable, capture-safe improvements with high visual ROI.
Reject any idea that places dark PBR in FOV, replaces HF densify boards, or needs extreme lighting.
If unsure, choose behind_wall + bright albedo materials or additive_emissive.
```

---

## Prompt pack (5 pillar farms)

### 1) Materials / weathering — `P01_materials.md` body

```
[MASTER SYSTEM PROMPT]
[FREEZE LAW]

TASK: Produce 20 proposals for materials/weathering only.
Focus:
- airframe metal normal/roughness/AO/dirt (bright enough for capture)
- prop disc motion readability without FOV washout
- rifle/tan polymer + worn metal accents
- rust/dirt breakup tiles BEHIND wall
Use existing assets under:
- /Game/Skyguard/Materials (M_L21_*, M_L23_*, M_Tex_*, M_YakAirframe, M_AirframeMetal, M_PropDisc, M_RifleTan)
- /Game/Skyguard/Textures/Imported (T_airframe_metal_*, T_*_A/N/R)

Return 20 JSON objects in one array.
IDs: MAT-001 ... MAT-020
pillar must be "materials"
effort prefer S or M
```

### 2) Aircraft / cockpit fidelity — `P02_aircraft.md` body

```
[MASTER SYSTEM PROMPT]
[FREEZE LAW]

TASK: Produce 20 proposals for aircraft/cockpit fidelity only.
Focus:
- Yak beauty silhouette + panel breakup behind wall
- cockpit tub / instruments / glove / arm with bright readable mats
- canopy edge cues without black glass FOV collapse
- prop hub/blades as capture-safe bright shells
Meshes preferred:
- yak52_hd_proxy, propeller_proxy, cockpit_tub_proxy, gunner_station_proxy,
  instrument_cluster_proxy, glove_hand_proxy, glove_arm_proxy

Return 20 JSON objects.
IDs: AIR-001 ... AIR-020
pillar must be "aircraft"
placement mostly behind_wall
```

### 3) City / Ocean beauty — `P03_city_ocean.md` body

```
[MASTER SYSTEM PROMPT]
[FREEZE LAW]

TASK: Produce 20 proposals for city/ocean beauty only.
Focus:
- facade towers/apartments with bright brick/plaster/corrugated
- harbor crane/ship/pier/seawall readable from air
- ocean foam caps + wet sand coastal band
- avoid pure black ocean finals
Meshes:
- facade_tower_proxy, apartment_midrise_proxy, harbor_crane_proxy,
  container_ship_proxy/freighter_proxy, pier_section_proxy, seawall_proxy,
  submarine_proxy, coast_block_proxy

Return 20 JSON objects.
IDs: CO-001 ... CO-020
pillar must be "city_ocean"
```

### 4) Weapon / ADS beauty — `P04_weapon_ads.md` body

```
[MASTER SYSTEM PROMPT]
[FREEZE LAW]

TASK: Produce 20 proposals for weapon/ADS beauty only.
Focus:
- rifle ADS proxy + glove contact readability
- Igla shape readability behind wall
- iron-sight / barrel cues without dark FOV slab
- keep ADS HF unlit checkers/stripes intact
Meshes:
- rifle_ads_proxy, rifle_irons_proxy, igla_proxy, glove_hand_proxy

Return 20 JSON objects.
IDs: WPN-001 ... WPN-020
pillar must be "weapon_ads"
Important: do not replace ADS HF densify with solid dark materials.
```

### 5) Niagara / VFX beauty — `P05_vfx.md` body

```
[MASTER SYSTEM PROMPT]
[FREEZE LAW]

TASK: Produce 20 proposals for VFX beauty only.
Focus:
- muzzle flash, gun smoke, hit sparks
- drone explosion / flak burst
- prop wash / tracer
- ocean spray
Use additive emissive proxies first if Niagara systems are shells.
Niagara paths under /Game/Skyguard/VFX:
NS_MuzzleFlash, NS_GunSmoke, NS_HitSparks, NS_DroneExplosion, NS_FlakBurst,
NS_PropWash, NS_TracerBurst, NS_OceanSpray, NS_WaterSplash, NS_MissileTrail

Return 20 JSON objects.
IDs: VFX-001 ... VFX-020
pillar must be "vfx"
placement must be additive_emissive unless proven safe behind_wall
No dark smoke walls in FOV.
```

---

## Batching / volume strategy

For weekend Luna farming:
- Run each pillar prompt in many short threads (temperature medium/high for diversity).
- Target per wave: 20 proposals x 5 pillars = 100 proposals/wave.
- Run many waves. Example weekend goal: 1,000–5,000 ranked candidates, not 100k unfiltered dumps.
- Deduplicate by title+change+stage_targets similarity before ranking.

Recommended wave cadence:
1. Wave A: pure discovery (open variants)
2. Wave B: constrained to failed critic pillars with evidence from latest CRITIC_FAIL_loopXX.md
3. Wave C: recovery-only if capture usable < 11

---

## Ranking schema

### Hard filters (auto reject)
Reject if any true:
- placement missing/invalid
- uses dark PBR in FOV / mid-FOV hero masses
- proposes extreme lighting
- proposes removing L52 HF densify boards
- stage_targets empty or unknown camera
- no acceptance_test
- effort = L AND risk = high
- change is vague ("make better", "more realistic") without concrete asset/step

### Score model (0-100)

```
score =
  25 * pillar_need
+ 20 * visual_roi
+ 20 * capture_safety
+ 15 * implementability
+ 10 * asset_readiness
+ 10 * metric_upside
- 25 * regression_risk
- 10 * complexity_penalty
```

#### pillar_need (0-1)
- materials 1.0
- aircraft 1.0
- city_ocean 0.9
- weapon_ads 0.9
- vfx 1.0

#### visual_roi (0-1)
- 1.0 clearly changes beauty of hero subject
- 0.6 moderate local improvement
- 0.3 minor/noisy

#### capture_safety (0-1)
- 1.0 behind_wall or tiny additive_emissive
- 0.5 unlit_hf_only tweaks
- 0.0 FOV dark PBR / board replacement

#### implementability (0-1)
- 1.0 existing mesh/mat paths + S effort
- 0.6 needs minor mat setup
- 0.3 needs new content pipeline

#### asset_readiness (0-1)
- 1.0 paths exist in Content/Skyguard
- 0.5 plausible existing family
- 0.0 needs external marketplace first

#### metric_upside (0-1)
- 1.0 expects uniq/edge up, black flat/down on target cams
- 0.5 mixed
- 0.0 likely black up or uniq down

#### regression_risk (0-1)
- 0.0 low isolated behind-wall
- 0.5 touches multiple stages
- 1.0 global lighting / FOV material rewrite

#### complexity_penalty (0-1)
- 0.0 S
- 0.5 M
- 1.0 L

### Rank bands
- A (implement now): score >= 75 and risk low/med and capture_safety >= 0.8
- B (next queue): 60-74
- C (park): 45-59
- D (reject): < 45 or hard-filter fail

### Selection policy per densify loop
From A-band only:
- pick 3-7 proposals
- max 2 per pillar
- max 1 high-risk exception (none preferred)
- prefer proposals whose stage_targets intersect current weak/partial cams
- package into one Unreal densify script delta under L52 freeze
- run capture + host audit
- keep only if usable stays 11/11 (or improves) and no pillar regresses

---

## Ranking CSV schema

`proposals_ranked.csv` columns:

```
id,pillar,title,score,band,risk,effort,placement,stage_targets,capture_safety,visual_roi,implementability,asset_readiness,metric_upside,regression_risk,complexity_penalty,source_wave,status
```

status enum:
- candidate
- selected_for_loop
- implemented
- accepted
- rejected_capture
- rejected_critic
- duplicate

---

## Post-L53 start command pattern

When L53 audit completes:
1. If usable >= 11: set BASE_FREEZE = L53 if art improved, else L52
2. Launch 5 Luna waves (P01..P05)
3. Validate JSON
4. Hard-filter + score
5. Export top A-band to `Docs/AAA_Review/luna_farm/selected_next_loop.md`
6. Implement selected only
7. Capture/audit
8. Update CONTROL_BOARD.md with accepted/rejected counts

---

## selected_next_loop.md template

```
# Selected Luna proposals for Loop NN
Base freeze: L52/L53
Usable gate required: 11/11

## Keep rules
- behind wall / additive emissive only
- preserve HF densify

## Implement list
1. ID — title — stages — why
2. ...

## Explicit non-goals
- no FOV dark PBR
- no global light overhaul

## Acceptance
- host usable 11/11
- no camera falls to Partial/No
- critic notes any pillar movement
```

---

## Minimal validator checklist (manual or script)

For each proposal JSON object:
- [ ] valid enums
- [ ] known cameras
- [ ] non-empty change + acceptance_test
- [ ] capture_safe_reason mentions freeze rule
- [ ] assets paths look local (`/Game/Skyguard/...`)
- [ ] not a duplicate of prior accepted ID family

---

## What success looks like this weekend

Not 100k chats. Success is:
- hundreds of valid JSON proposals
- dozens of A-band items
- several implemented loops that keep 11/11 usable
- harsh critic still FAIL until blind A/B truly flips pillars
- CONTROL_BOARD tracks accepted art gains separately from capture gate

Capture gate is met (L52). Luna farm exists to force art pillars upward without reopening densify regressions.
