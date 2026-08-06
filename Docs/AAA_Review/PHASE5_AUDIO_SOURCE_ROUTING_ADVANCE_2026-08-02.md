# Phase 5 Audio Source-Routing Advance — 2026-08-02

## Result

The native audio path is materially closer to final authoring, while the
Shipping and friend-facing boundary remains fail closed.

After the offline work, a bounded UE 5.8 NullRHI automation run loaded the
current native module and passed all five `Skyguard52.Audio` tests. No packaged
game was launched. No audio was downloaded, imported, promoted, deleted, or
claimed audible.

## Runtime advances

- The native audio director now has a governed soft reference to
  `DA_P5A_ProductionAudioBank` and requests that bank asynchronously.
- The resolved bank is applied before its dependent Sound, attenuation,
  concurrency, submix, and cockpit-mix references are asynchronously primed.
- All five continuous Yak-52 identity routes preserve their four required
  bindings: Sound, attenuation, concurrency, and output submix.
- The cockpit SoundMix is primed and pushed/popped with rear-cockpit/exterior
  listener perspective.
- A per-world registered director provides one governed dispatch boundary for
  gameplay audio.
- Rifle muzzle/mechanical, Igla search/lock/launch/impact, and light/heavy
  drone-destruction events now route through that boundary.
- Direct synchronous loads of legacy Imported propeller, rifle, and explosion
  sounds were removed from native gameplay.
- `/Game/Skyguard/Audio/Imported` was removed from `DirectoriesToAlwaysCook`.
- A bank with approved sources but missing attenuation, concurrency, or
  output-submix bindings can no longer report production ready.

## Authoring handoff

`PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json` now governs:

- 15 exact attenuation recipes;
- 14 exact concurrency recipes;
- six exact MetaSound interface/category compositions;
- the fail-closed rule that missing sources remain null and
  `MISSING_SOURCE`, even when routing primitives are authored.

The recipes have now been used to serialize and independently reopen the
attenuation and concurrency assets. The current on-disk counts are:

- MetaSounds: 0 of 6;
- attenuation assets: 15 of 15;
- concurrency assets: 14 of 14;
- authentic approved categories: 0 of 25.

Fresh serialized evidence is recorded in
`PHASE5_ROUTING_PRIMITIVES_SERIALIZED_2026-08-02.md` and
`Saved/Reports/Phase5RoutingPrimitives/attempt_20260802T131336693Z_fa835612/fresh_audit.json`.
All 25 bank routing bindings reopen successfully, while every source remains
explicitly null/`MISSING_SOURCE`. Empty filename-only MetaSound shells were not
created because they would not prove governed interfaces or topology.

## Host audio attribution boundary

`collect_phase5_host_audio_diagnostics.ps1` performed a read-only 24-hour
Application event-log scan. Its current receipt reports:

- status: `HOST_AUDIO_MIDDLEWARE_FAULTS_DETECTED`;
- Nahimic / `DeviceRoutingDaemonModule.dll` faults: 89;
- Skyguard faults in the same query: 0;
- Unreal launched: false;
- service state modified: false.

This does not clear Skyguard audio. It prevents a host middleware crash from
being mislabeled as a game defect, and it prevents a clean host log from being
treated as audible acceptance.

## Verification evidence

- `PHASE5_AUDIO_OFFLINE_READINESS_GATE.json`:
  `PASS_CONTRACT_VALID_EXTERNAL_AUTHORING_AND_ACQUISITION_REQUIRED`;
- offline gate mutation suite: 50 tests passed;
- runtime routing report:
  `CONTRACT_VALID_AUTHORING_BLOCKED`, structural contract valid;
- runtime source markers: 0 missing, 0 forbidden, 11 event bindings,
  10 of 10 mission briefing prime hooks;
- primitive recipe validation: 15 attenuation, 14 concurrency, six
  MetaSound interfaces, zero errors;
- Shipping audit: zero forbidden runtime Imported references and zero
  forbidden Imported always-cook directives.
- Native UE 5.8 automation:
  `Saved/Logs/Phase5AudioRoutingPostAdvance.log`, five tests discovered and
  five completed with `Result={Success}`, command-line exit code 0, zero
  failure signatures, and zero fatal/assert/ensure/GPU-timeout signatures.
  The durable log SHA-256 is
  `7b9c2d1e4431f55b7c713508cf63e407c79fc3462b278792340258632db98759`.
- Post-serialization native regression:
  `Saved/BuildAttempts/PHASE5_ROUTING_PRIMITIVES_NATIVE_REGRESSION/attempt_20260802T135100Z`,
  five of five tests successful, exit code 0, and zero
  fatal/assert/ensure/GPU-timeout signatures. Log SHA-256:
  `c3c6b43576b60eef40d7bca7716e7bf96fbdb7aedf23f52ccaa7482c3ff2f108`.

## Remaining fail-closed blocks

- record or license authentic sources and approve all provenance;
- author and serialize six governed MetaSound graphs;
- bind all 25 production-bank categories;
- quarantine or remove 14 legacy Imported `.uasset`s and 14 loose source-media
  files from the Shipping boundary without destroying evidence;
- run a fresh Unreal serialized topology audit;
- run packaged audible combat soaks on a stable host audio path;
- complete independent listening acceptance.

Until every item above is proven, this phase is not production-audio ready and
friend-facing Shipping remains blocked.
