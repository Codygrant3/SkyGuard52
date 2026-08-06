# Phase 6/7 Mission 1 Sortie-Flow Closure

Date: 2026-08-02

## Closed native seam

The campaign already had deterministic briefing, objectives, scoring, medals,
unlocks, and save-slot APIs. The playable sortie did not connect those systems
after victory: mission directors discarded the scored result, authored success
debrief text was unused, and no save or next-map travel contract was produced.

Mission 1 is now the native template for the complete non-visual lifecycle:

1. Briefing remains gated by authored reading time and asset readiness.
2. The campaign starts Mission 1 and owns its objective runtime.
3. Victory computes the authoritative score and medal.
4. The campaign builds `FSkyguardMissionDebrief` from the authored mission
   presentation and current result.
5. The debrief reports new personal bests, the next mission, its unlock state,
   and whether progression reached disk.
6. Mission 1 finalization saves to a configurable campaign slot.
7. Save failure stays visible and can be retried; it does not erase the
   completed in-memory result.
8. Next-map travel is fail-closed until the player acknowledges the debrief,
   progression is saved, the next mission is unlocked, and its playable map is
   assigned.
9. A fresh campaign runtime can reload the save and retain the unlock.

The campaign subsystem owns the reusable debrief/travel contract, so UI can
render it without duplicating scoring, unlock, or persistence logic. Mission 1
is wired first, matching the audit recommendation to freeze one complete
player-facing template before propagating it across Missions 2-10.

## Verification

Fast source-contract regression:

```powershell
python -m unittest Scripts.tests.test_campaign_sortie_flow_contract -v
```

Native Unreal automation:

```text
Skyguard52.Campaign.Sortie.BriefingToDebriefSaveAndTravelContract
```

The native scenario covers score, medal, authored debrief copy, new-best flags,
automatic disk persistence, next-mission selection/unlock, acknowledgment
gating, map-package resolution, fresh-runtime reload, and slot cleanup without
opening a map.

## Remaining acceptance

This provides the compile-testable native lifecycle required by the future UI.
It does not claim rendered briefing/debrief acceptance, voiced radio acceptance,
actual `OpenLevel` traversal, or a human-played packaged sortie. Those remain
visible/runtime acceptance gates under P6.6 and P7.12.
