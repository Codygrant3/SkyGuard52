# Skyguard — our own thing

Updated: 2026-08-14

The BF6/COD photoreal bar is retired as the live product goal.

We are making a **tactical arcade gunship campaign**. You are the Apache
front-seat gunner. An AI pilot flies. You feel enormously powerful, but
you must keep picking the threat that can kill the helicopter or the
objective first. Military action-movie picture from helicopter distance,
not a Megascans close-up.

Read `Docs/SKYGUARD_APACHE_GUNSHIP_PIVOT.md` before changing weapons,
missions, or the player aircraft.

## What we keep

- Canonical project: `D:\Skyguard52` (Unreal Engine 5.8).
- Gunner look, zoom, combat VFX, audio, campaign directors, briefing/HUD.
- Playable coastal/harbor maps, starting with
  `/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1`.
- Historical `Docs/AAA_Review` and `Saved/` evidence. Do not rewrite or delete it.

## What we stop doing

- Yak-52 rear rifle + Igla as the live fantasy.
- Shahed-only missions.
- Photoreal ground / vegetation / skyline acceptance loops.
- Treating names like AAA, accepted, or production as quality.
- Using the retired Three.js tree as source or deployment authority.

## Live weapons

30 mm chin gun. Rocket pods. Guided missiles. No Igla on the player.

## What “good” means now

1. You sit in the Apache CPG seat and the chin gun follows your look.
2. Cannon, rockets, and missiles feel different and useful.
3. Mixed threats — boats, armor, air — not one drone type forever.
4. Mood and readable silhouettes beat close-up material science.

## Lane

**A — keep Unreal, drop the COD bar.** Locked 2026-08-14.
**Apache gunship campaign.** Locked 2026-08-14.

## Next build slice

**Ten-mission campaign** runs on the playable coastal map via
`ASkyguardGunshipSortieDirector`. First Contact through Fortress Dawn,
auto-advancing after a win. Harbor Breaker is mission 2.

## How to play

Editor: open `Lvl_M01_CoastalIntercept_Playable_v1` and press Play.  
W climb and speed up, S descend and slow down, A/D pivot, arrows point the nose.  
Mouse look, RMB sensor, T thermal, Space fire, 1/2/3 stations, R reload, C flares.  
After a sortie: 1–4 pick loadout, N or Enter continues.
