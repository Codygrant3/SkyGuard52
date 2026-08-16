# Skyguard Apache Gunship — formal pivot

Updated: 2026-08-14

Lane A still holds: keep Unreal, drop the COD/photoreal bar, do not delete
`Docs/AAA_Review` or `Saved/` evidence, do not use the retired Three.js tree.

## North star

A cinematic tactical gunship game where the player feels enormously
powerful, but must constantly identify the most dangerous threat before it
can kill the helicopter or destroy the objective.

This is **not** “replace the Yak-52 with an Apache.” The game is the
relationship between **pilot, gunner, sensors, weapons, and battlefield
prioritization**. Authentic presentation, simplified operation, meaningful
decisions, explosive action. Distinct enough to have an identity. Scoped
enough to finish.

Positioning: **tactical arcade gunship campaign.**

## Product lock

- Vehicle: Apache gunship. Player is the front-seat CPG. AI pilot flies.
- Live weapons: 30 mm, rockets, guided missiles. No Igla. No rifle.
- Two sights: helmet-sight for immediate threats; targeting-sensor for hunting.
- Pilot: player issues engagement geometry (orbit, hold, run, break, pop-up).
  The pilot flies it. The player does not fly a sim.
- Enemies form networks, not a shooting gallery. Shahed-style attackers are
  one archetype, not the campaign.
- Quality: high-fidelity **feedback**, selective hero assets, consistent
  gameplay-distance presentation. Five shipping checks only.

## Eleven design pillars

1. **Guided freedom** — AI handles flight and terrain; player commands how
   we engage. Terrain is cover for pop-up attacks.
2. **Two complementary sights** — helmet for spectacle and near threats;
   sensor for precision. Zoom is power and vulnerability.
3. **Weapons are decisions** — each station has a job and a cost.
   “Is this worth a missile?”
4. **Battlefield ecosystem** — radar, command, ADA, armor, artillery,
   drones, and helicopters support one another. Kill one node, change the map.
5. **Readable escalation** — search → detect → track → lock → fire.
   Deaths should be understandable.
6. **Action-movie mission rhythm** — approach, contact, complication,
   choice, reversal, climax, extraction. Reuse modular kits, not the same
   flight path.
7. **Bosses are systems** — destroy radar, engines, launchers, magazines.
   Not a single health bar.
8. **The pilot is a character** — calls, confirms, warns, gets urgent.
9. **Damage is drama** — sensors, heat, jams, cracked glass, not only a bar.
10. **Progression unlocks playstyles** — loadouts and maneuvers, not +3% damage.
11. **Spend pixels where the player feels them** — cockpit, weapons, death,
    sensors, light, landmarks, silhouettes, atmosphere.

## What we reuse vs archive

Reuse: UE 5.8, gunner pawn, arcade mood, combat VFX, audio/radio, mission
directors, campaign/briefing/HUD, pilot-command enum, boss weak points,
generic threat body, coastal/harbor maps.

Archive (do not delete): Yak as live mount, rifle + Igla presentation,
Shahed-only roster, rear-seat safety arc, photoreal AAA gates.
`ASkyguardIglaMissile` is guided-missile physics only.

## Live CPG controls

| Input | Meaning |
| --- | --- |
| Mouse | Helmet / sensor look. Chin gun slaves in helmet-sight. |
| Space | Fire selected station |
| RMB | Hold **targeting-sensor** (TV/thermal grade, tight FOV) |
| 1 / 2 / 3 | Cannon / rockets / guided missile |
| R | Reload the selected station |
| T | Toggle thermal inside the sensor |
| X | Pop flares (defeat inbound missiles) |
| F | Launch guided missile if lock is complete |
| W | Ascend and accelerate |
| S | Descend and slow down |
| A / D | Pivot the airframe left / right |
| Arrow keys | Point the nose the way you want to go |

## Harbor Breaker — proof of the thesis

Reuse existing coastal/harbor playables. Do not author a new photoreal kit.

| Time | Beat |
| --- | --- |
| 0–2 | Low approach. Pilot introduces helmet cannon and sensor. |
| 2–4 | Fast attack boats on the cargo ships. |
| 4–6 | Technicals and armor on the shoreline. |
| 6–8 | Mobile radar comes up and starts coordinating ADA. |
| 8–10 | Choice: kill the radar, or save a damaged friendly ship. |
| 10–13 | Patrol-ship boss: radar, cannon, launcher, engines, drone deck. |
| 13–15 | Extraction helo. Forced back into helmet-sight. |

That one sortie must prove: land/sea/air, prioritization, pilot commands,
three weapons, two sights, a component boss, cinematic pacing.

## Implementation order

1. Apache seat, three stations, mixed threats (done).
2. Direct flight + helmet vs sensor (done).
3. Thermal, flares, inbound warnings (done).
4. Ten-mission roster, weather identity, patrol-ship systems, debrief, loadouts (this pass).
5. Unique maps and a VO bank still later.

A pillar is not shipped because it is named. It is shipped when a player
can feel the decision.
