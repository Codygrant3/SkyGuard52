# Phase 5 — Production Audio Integration

## Production bank

`USkyguardAudioProductionBank` is the authoritative `UPrimaryDataAsset` schema
for final audio. It declares 25 required categories:

- five Yak-52 engine, propeller and wind layers;
- four rifle layers;
- five Igla layers;
- three drone layers;
- four small-explosion layers;
- four heavy-explosion layers.

Each entry binds:

- a `USoundBase` soft reference;
- attenuation;
- concurrency;
- output submix;
- source status;
- provenance identifier;
- immutable source SHA-256.

The accepted production source statuses are project-owned recording and
licensed third-party source. `ProceduralQATestOnly` can exercise development
routing but can never satisfy production readiness.

`InitializeRequiredEntries` creates exactly one entry per category with
`MISSING_SOURCE`. `EvaluateReadiness` reports:

- missing category entries and duplicates;
- explicit missing sources;
- invalid source/status/provenance combinations;
- QA-only signals;
- missing routing assets;
- structural contract completeness;
- final production readiness.

Missing content therefore stays visible rather than silently becoming an empty
or misleading Sound asset.

## Routing and listener integration

The bank requires master, cockpit, exterior, weapons, explosions and radio
submixes plus a cockpit SoundMix. The production director copies its
RPM/load-loop references, event references, attenuation, concurrency, submix
sends, cockpit attenuation and cockpit low-pass setting from the bank.

Soft references are primed during the briefing. Gameplay event dispatch does
not synchronously load final audio.

## Acceptance harness

`USkyguardAudioAcceptanceHarness` records bounded evidence from a packaged
Development run. It refuses acceptance unless all of the following are true:

- valid build and evidence SHA-256 values;
- packaged Development build;
- audible device actually observed;
- calibrated metering used;
- production bank ready;
- at least 600 measured samples;
- voice count within the authored limit;
- zero underruns;
- audio-thread cost within budget;
- true peak at or below the authored ceiling.

Native automation tests this refusal logic with synthetic values. Those tests
validate the gate contract only; they are not audible evidence.

## Current honest state

All 25 categories remain `MISSING_SOURCE`. The seven routing binaries and the
production-bank binary are present locally, but no fresh serialized Unreal
audit receipt exists for this checkout. Their provenance state therefore reads
`LOCAL_BINARY_PRESENT_FRESH_UNREAL_AUDIT_MISSING`, not accepted or
production-ready. Final audible acceptance is blocked.

Use
`D:\Skyguard52\Docs\AAA_Review\PHASE5_AUDIO_PRODUCTION_PROVENANCE_TEMPLATE.json`
as the import ledger boundary. Never replace `MISSING_SOURCE` until the
recording/license, hash and Unreal assignments are verified.

## Structural verification — 2026-08-01 CDT

- Global Unreal Engine 5.8 editor target: UHT, compile and link **PASS**.
- `Skyguard52.Audio.Acceptance.RefusesUnprovenAudibleClaims`: **Success**.
- `Skyguard52.Audio.Director.DeterministicStateAndBudgets`: **Success**.
- `Skyguard52.Audio.ProceduralAudition.DeterministicBoundedSignals`: **Success**.
- `Skyguard52.Audio.ProductionBank.ExplicitMissingSourceContract`: **Success**.
- `Skyguard52.Audio.Radio.BoundedPriorityQueue`: **Success**.
- Audio namespace: **5/5 passed** with zero audio-test failures.

Evidence:

`D:\Skyguard52\Saved\Logs\GlobalAutomation_Wave1.stdout.log`

The broader 21-test wave contained one unrelated Mission 1 integration failure
at that moment; it does not alter the five successful audio results. This is
still structural automation, not audible or packaged acceptance.

Authoritative present state:

- 25 of 25 production categories explicitly `MISSING_SOURCE`;
- seven of seven routing binaries locally present, fresh Unreal audit missing;
- category contract complete;
- production readiness false;
- audible acceptance blocked.

Source research and the lawful closure sequence are recorded in:

- `D:\Skyguard52\Docs\AAA_Review\PHASE5_AUDIO_SOURCE_ACQUISITION_LEDGER.json`
- `D:\Skyguard52\Docs\AAA_Review\PHASE5_AUDIO_SOURCE_GAP_CLOSURE_PLAN.md`

The research ledger contains direct, HTTP-verified CC0 candidate pages but no
downloads or hashes. Legal clarity alone does not clear semantic or audio-quality
review. Yak-specific loops, authentic open-cockpit wind, Igla, piston UAVs and
mission radio remain blocked.

All 25 category briefs and the offline readiness guard are defined in:

- `D:\Skyguard52\Docs\AAA_Review\PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json`
- `D:\Skyguard52\Docs\AAA_Review\PHASE5_AUDIO_CATEGORY_BRIEFS.md`
- `D:\Skyguard52\Scripts\verify_phase5_audio_acquisition_contract.py`

Current offline audit:

- exact category coverage: 25/25;
- all states: `MISSING_SOURCE`;
- routing binary paths present: 7/7; runtime audit receipt missing;
- acquisition downloads and hashes: 0/0;
- contract validation: pass;
- production readiness: false;
- release-mode verifier: correctly exits 3.

Audit receipt:

`D:\Skyguard52\Saved\Reports\PHASE5_AUDIO_ACQUISITION_CONTRACT_AUDIT.json`

## P5-A source-independent routing scaffold

The smallest executable routing wave is governed by:

- `D:\Skyguard52\Docs\AAA_Review\PHASE5_P5A_IDENTITY_BED_ROUTING_CONTRACT.json`
- `D:\Skyguard52\Scripts\build_skyguard_phase5_p5a_audio_routing.py`
- `D:\Skyguard52\Scripts\verify_phase5_p5a_audio_routing_contract.py`
- `D:\Skyguard52\Scripts\test_phase5_p5a_audio_routing_contract.py`

The Unreal Python builder is idempotent. It creates or reuses the six required
submixes, cockpit SoundMix and production-bank Data Asset, but creates no
SoundWave and performs no import or download. It initializes the full
25-category bank only when that bank is first created and preserves every
existing entry on later runs.

Engine idle, cruise, power, propeller and open-cockpit wind remain explicit
`MISSING_SOURCE` placeholders with null Sound, provenance and hash values.
Creating the routing scaffold can clear the seven routing gaps; it cannot
advance production-source count or claim P5-A identity-bed acceptance.

Offline validation:

`python D:\Skyguard52\Scripts\verify_phase5_p5a_audio_routing_contract.py`

Mutation tests:

`python D:\Skyguard52\Scripts\test_phase5_p5a_audio_routing_contract.py`

Before an Unreal execution receipt exists, `--require-built` must exit 3.
Until lawful recordings and complete provenance exist,
`--require-production-ready` must remain nonzero.

The serialized build-and-fresh-audit supervisor is:

`powershell -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\run_skyguard_phase5_p5a_audio_routing_gate.ps1`

It refuses an occupied Unreal lane, creates an immutable attempt directory,
redirects every process to attempt-specific logs, leaves a timed-out process
authoritative instead of duplicating it, builds in one Unreal process, and
audits persisted assets in a new process. Its only successful state is
`PASS_ROUTING_ONLY`; its status receipt always keeps `production_ready=false`
and the five Yak-52 identity sources explicitly missing.

UE 5.8.1 source compatibility was checked against the installed engine headers:
`USoundSubmixFactory`, `USoundMixFactory`, `UDataAssetFactory.DataAssetClass`
and `USoundSubmixBase.ChildSubmixes` exist in `D:\UE_5.8`. Runtime compatibility
still requires the serialized Unreal execution and fresh-process receipt.
