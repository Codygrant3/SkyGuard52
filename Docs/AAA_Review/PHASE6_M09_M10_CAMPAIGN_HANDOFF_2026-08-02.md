# Phase 6 Mission 9 to Mission 10 Campaign Handoff

Date: 2026-08-02

## Outcome

Mission 9 now participates in the governed campaign runtime instead of completing
only inside its level-local objective runtime.

Before this closure, defeating Iron Rain and preserving two city targets changed
the Mission 9 wave state to `Completed`, but did not call
`USkyguardCampaignSubsystem::CompleteActiveMission`. Campaign V1 places
`M10_EvacuationFinale` directly behind `M09_SaturationAttack`, so that missing
record could leave the finale locked after a successful Mission 9 sortie.

## Implemented boundary

- Mission 9 loads and validates the Campaign V1 definition.
- It starts or binds the active Mission 9 campaign runtime when progression
  permits the sortie.
- Objective progress and protected-target failure route through the active
  campaign runtime.
- Direct editor launches retain the local objective-runtime fallback.
- Successful completion is fail-closed on required-objective completion and
  terminal failure.
- Campaign-backed success records Mission 9 through
  `CompleteActiveMission` before setting the level wave state to `Completed`.
- A native automation scenario restores completed Missions 1-8, starts Mission
  9, executes its governed three-wave and Iron Rain defeat route, verifies the
  Mission 9 save record, and verifies Mission 10 becomes unlocked.

## Verification

Fast source-contract regression:

```powershell
python -m unittest Scripts.tests.test_m09_campaign_handoff_contract -v
```

Result on 2026-08-02: `PASS` (5 tests).

Native Unreal automation added:

```text
Skyguard52.Mission09.Campaign.CompletionRecordsAndUnlocksFinale
```

The native test is authored but was not executed in this lightweight pass
because the machine-stability constraint prohibited launching heavyweight
Unreal processes. It must be included in the next editor automation run before
this handoff is treated as runtime-proven.

## Scope note

This closes the specific M09-to-M10 progression seam. It does not by itself
close the broader Phase 6 player-facing briefing, debrief, map-travel, and full
campaign-flow evidence gap.
