# Phase 5 authentic-source acquisition readiness

## Outcome

The accepted six-graph MetaSound topology is now protected by an immutable,
offline source-acquisition contract:

- Contract:
  `Docs/AAA_Review/PHASE5_AUTHENTIC_SOURCE_ACQUISITION_CONTRACT.json`
- Verifier:
  `Scripts/verify_phase5_authentic_source_acquisition_contract.py`
- Mutation tests:
  `Scripts/test_phase5_authentic_source_acquisition_contract.py`
- Accepted topology attempt:
  `Saved/Reports/Phase5MetaSoundTopology/attempt_20260802T151943423Z_7fd745f0`

The contract is intentionally not an asset-acquisition receipt. It authorizes no
purchase, license acceptance, download, media processing, Unreal import,
MetaSound mutation, production-readiness claim, shipping claim, or audible
acceptance claim.

## Current truth

- Governed MetaSound graphs: **6**
- Exact WaveAsset source slots: **25**
- Slots still using accepted null defaults: **25**
- Authentic approved sources: **0**
- Downloaded sources: **0**
- Hashed source files: **0**
- Imported production SoundWaves: **0**
- Research candidate leads: **14**
- Slots with at least one research or rejected candidate reference: **20**
- Slots with no candidate reference: **5**
- Production ready: **false**
- Shipping allowed: **false**
- Packaged audible acceptance: **false**

The five slots without any research candidate are:

1. `RifleCasing`
2. `IglaSearch`
3. `IglaLock`
4. `IglaFlyby`
5. `IglaImpact`

Candidate presence is not readiness. The current candidates are retained only
to prevent duplicate research and accidental promotion:

- Generic C-47, biplane, and aircraft fly-past material cannot establish
  Yak-52 identity.
- Synthetic white-noise wind cannot establish open Yak-52 rear-cockpit airflow.
- Rifle candidates have not been acquired or checked against the final rifle,
  exact file, transient integrity, perspective, or animation.
- The orbital-rocket launch candidate is rejected for Igla scale and system
  mismatch.
- The electric toy-drone candidate is rejected for piston-UAV identity mismatch.
- Explosion candidates have researched source pages but no acquired, hashed,
  technically inspected, or accepted files.
- The radio lead is outside the accepted 25 slots and remains blocked by
  underlying-recording, performer, privacy, language, and mission-fit evidence.

## Allowed acquisition routes

### Project-owned recording

Required for:

- `EngineIdle`
- `EngineCruise`
- `EnginePower`
- `Propeller`
- `OpenCockpitWind`

These sources need an authorized Yak-52 recording session with exact aircraft,
operating-state, listener-perspective, canopy, RPM/load, recorder, microphone,
placement, safety, ownership, and rights evidence. Generic aircraft libraries
may inform reference but cannot satisfy these identity slots.

### Licensed library

Allowed for the rifle, Igla, drone, and explosion slots only when the exact
downloaded file is covered by independently reviewed evidence for commercial
interactive-game use, modification, cooked embedding/distribution, and any
required marketing use. Source-page labels or uploader assertions alone are
insufficient.

## Required promotion evidence

Before a slot can advance to a separately governed import attempt, it needs:

1. Exact source identity, publisher/owner, product or recording identifier,
   original filename, URL or session reference, acquisition UTC, byte size, and
   SHA-256.
2. Immutable license, grant, assignment, releases, and reviewer receipt that
   apply to the exact source file.
3. Independently reviewed subject, event/state, listener perspective, technical
   quality, and slot-specific semantic fit.
4. Immutable original plus a complete edit chain and hashed production
   derivative.
5. PCM WAV derivative at 48 kHz/24-bit, mono or stereo as specified, with
   documented metering, no clipped samples, and true peak at or below -3 dBTP
   before the in-engine mix.
6. Raw-source exclusion from Unreal Content, cooked builds, and standalone
   redistribution.
7. Identified rights, semantic, and audio-QA reviewers with UTC acceptance
   records.
8. A separate fresh Unreal import audit followed by packaged audible acceptance.

## Offline verification behavior

The verifier fails closed if:

- the accepted topology attempt, topology contract, fresh audit, category briefs,
  acquisition schema/manifest, or candidate ledger changes hash;
- any of the six MetaSound binaries drifts from the accepted audit;
- any graph, WaveAsset input, category, source route, or Unreal destination
  differs from the accepted topology and category briefs;
- the 25 slots are missing, duplicated, added, or promoted inside the immutable
  contract;
- a candidate identifier is invented or omitted from the exact inventory;
- the current ledgers claim a download, hash, import, production-ready state,
  shipping permission, or packaged audible acceptance without evidence.

Each normal verifier run writes a new attempt directory under
`Saved/Reports/Phase5AuthenticSourceAcquisition`. Tests and the aggregate offline
gate use `--no-write` so they do not create misleading acceptance artifacts.
