# M01 UMG Sortie Presentation Contract

Date: 2026-08-02

## Outcome

Mission 1 now owns a reusable `USkyguardSortiePresentationComponent`. The
component is a UMG-compatible presentation model, not a hard-coded widget. It
keeps layout and visual art in Blueprint/UMG while ensuring widgets bind to
governed mission and campaign state instead of duplicating gameplay rules.

## Briefing model

The component derives mission-specific content directly from the active
`USkyguardMissionDefinition`:

- mission directive and title;
- route-point count, route length, and planned speed;
- aggregate attack-drone, formation, and wave counts;
- one primary/secondary card per objective;
- protected-objective, boss, route, threat, weapon, weather, and radio
  pictogram semantics;
- boss callsign, weak-point count, and required weapon set;
- weather profile, wind, cloud, and precipitation;
- all authored radio lines with stable IDs and channel labels;
- rear-arc scanning, iron-sight ADS, rifle fire, pilot-safety, Igla, and
  protected-objective guidance derived from mission requirements.

Pictograms are semantic enum values rather than texture paths. This lets the UI
team replace icon art without changing campaign logic or DataAssets.

## Debrief model

The presentation component mirrors the authoritative campaign debrief:

- current score and medal;
- authored success copy;
- new-best score and medal flags;
- explicit save-success or save-failure state;
- retry-save action;
- one-shot debrief acknowledgment;
- next-mission identity, unlock, and map state;
- guarded travel-ready, travel-blocked, and campaign-complete states.

State changes emit a Blueprint-assignable event so UMG can transition panels
without ticking or polling every frame.

## Verification

Fast source-contract suite:

```powershell
python -m unittest Scripts.tests.test_sortie_presentation_contract -v
```

Native headless automation:

```text
Skyguard52.Presentation.Sortie.DenseMissionSpecificBriefing
Skyguard52.Presentation.Sortie.DebriefSaveRetryAckAndTravelStates
```

The tests intentionally stop before calling `OpenLevel`; they validate the
travel guard but do not initiate visible rendering.

Verified headlessly on 2026-08-02 with `-NullRHI`: two tests discovered, two
successful, zero failures, process exit code `0`. Evidence:

```text
Saved/BuildAttempts/SORTIE_PRESENTATION/attempt_20260802T115315Z/
```

## Honest boundary

This closes the reusable C++ data-binding and state-machine layer. It does not
claim a final UMG layout, accepted pictogram artwork, typography, animation,
controller navigation, localization review, or human visual acceptance.
