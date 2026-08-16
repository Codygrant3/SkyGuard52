# Skyguard production phases

Updated: 2026-08-16

This is the **coordination plan of record** for remaining production work.

It does not invent a product. Live fantasy stays the tactical arcade Apache
CPG campaign in `Docs/SKYGUARD_OWN_THING.md` and
`Docs/SKYGUARD_APACHE_GUNSHIP_PIVOT.md`. Read those first. Historical AAA
evidence stays immutable. Do not reopen Stage 7B / hero photoreal acceptance
loops unless the user explicitly restores that bar.

## Product lock (do not reopen)

- Player is the Apache front-seat CPG. An AI pilot flies.
- Live weapons: 30 mm, Hydra, Hellfire. No player Igla. No rifle.
- Harbor Breaker is the 15-minute proof of the thesis (mission 2).
- Ten-mission campaign already runs on
  `/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1` via
  `ASkyguardGunshipSortieDirector`.
- Harbor Breaker `BeatSeconds` stay
  `{120, 240, 360, 480, 600, 780, 900}`. Do not shrink them.

## Coordination

Code Reviewer merges. Workers never merge.

Workers never touch a dirty `D:\Skyguard52`. One worktree and one branch per
job. Branch prefixes: `cursor/*` and `grok/*`.

File locks before launch. Do not start a second job on a locked path.

Stack onto `cursor/harbor-proof-play` until Harbor Play is signed off, then
stack onto `main`.

C++ tests are required on every gameplay or engine change. Cloud agents
cannot compile Unreal or hit Play; they still add or update the tests.

No art or map rebuilds in phases 0–4.

gh may be logged out; push branches anyway.

## Phase 0 — Land Harbor Breaker proof (15 min)

Land the Harbor Play stack so the user can Play and extract.

Stack: feel #5 + lock #1 + ship #7 + debrief #8 + weather + inbound.

That stack is the existing Harbor Breaker thesis, not a new mission:

| Stack item | Pivot pillar / existing beat |
| --- | --- |
| feel #5 | Readable escalation: search → detect → track → lock → fire |
| lock #1 | Guided freedom: AI flies; player commands engagement geometry |
| ship #7 | Bosses are systems: patrol-ship radar, cannon, launcher, engines, deck |
| debrief #8 | Pilot is a character: calls, confirms, win/fail, loadout prompt |
| weather | Mission weather identity already on the ten-mission roster |
| inbound | Inbound missile warning, flares, extract pressure |

Phase 0 control and HUD changes:

- Remap flares from `C` to `X`.
- Show inbound warning and flare count on the CPG HUD.

User Play is the extract. Fail the Play if any of these fire:

| Fail code | Meaning |
| --- | --- |
| boats at 0:30 | Fast boats appear on the 0–2 approach, not the 2–4 contact beat |
| hull splash kills ship | Splash / stray hull hits sink the cargo ship |
| Space in SRCH | Space fires the guided station while the lock is still in search |
| C still flares | `C` still pops flares after the remap to `X` |
| night without thermal | Night identity plays without a working thermal path |

Do not shrink Harbor Breaker `BeatSeconds` to make the Play shorter.

## Phase 1 — Harden from Play notes, split by file lock

Harden only what the Phase 0 Play actually called out.

Split by file lock. One lock, one worktree, one branch. Do not bundle
unrelated Play notes into one dirty tree.

Still no art or map rebuilds.

## Phase 2 — Unfelt pillars

A pillar is not shipped because it is named. It is shipped when a player can
feel the decision. These are the unfelt pillars from the pivot, not a new
fantasy.

| Slice | Work | Stay inside |
| --- | --- | --- |
| 2A | Apache own-ship systems damage. Not one bar. | Sensors, heat, jams, cracked glass — pillar 9 |
| 2B | Pilot commands as decisions | Orbit, hold, run, break, pop-up — pillar 1 |
| 2C | Text pilot calls | `SkyguardPilotVoice` + radio. No VO bank |
| 2D | Radar-down lengthens inbound | Killing the net changes the inbound clock |
| 2E | Weapon cost only if a station feels free | Do not add cost theater if the station already costs |

Do not restore Yak, Igla, or rifle as live player fantasy while doing this.

## Phase 3 — Ten-mission beat kits

Author beat kits for the existing ten-mission roster on the existing coastal
map. No new maps.

Roster (already in `SkyguardCampaignRoster`): First Contact, Harbor Breaker,
Broken Highway, Night Eyes, River Hammer, Dust Offensive, Downed Bird, Iron
Rain, Hunter-Killer, Fortress Dawn.

Reuse modular kits. Do not author a new photoreal kit. Do not shrink Harbor
Breaker `BeatSeconds`.

## Phase 4 — Eng packaging / five shipping checks

Encode Eng packaging and the five shipping checks from
`Docs/SKYGUARD_APACHE_GUNSHIP_PIVOT.md` as tests.

Do not reopen photoreal acceptance. Do not treat the words AAA, accepted, or
production as quality.

## Phase 5 — Unique maps + VO after proof

Unique maps and a VO bank stay later. They start only after Harbor Play is
signed off and phases 0–4 have proof.

Phase 2C text calls (`SkyguardPilotVoice` + radio) remain the live voice
until a VO bank is actually scheduled here.

## Phase 6 — Art RC (human gate)

Art RC is a human gate. Cloud cannot accept art.

Apache cockpit first. Spend pixels where the CPG feels them.

Yak / Igla / rifle art is archived. Do not delete the archive. Do not put it
back in the live player fantasy.

## Banned

- Yak, Igla, or rifle as live player fantasy.
- Shrinking Harbor Breaker `BeatSeconds`.
- New maps or art rebuilds in phases 0–4.
- Cloud art acceptance.
- Touching a dirty `D:\Skyguard52`.
- Merging without the Code Reviewer.
- Inventing a new product, aircraft, or weapon set.
