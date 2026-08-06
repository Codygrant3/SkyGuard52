# Phase 5 Runtime Audio Routing Readiness

## Current determination

The Unreal/C++ runtime scaffold is source-valid, but the final audio graph is
not production-ready. This is an intentional fail-closed result.

The project currently contains the production bank, six submixes, cockpit
SoundMix, all 15 governed `ATT_` attenuation assets, and all 14 governed `CON_`
concurrency assets. A separate NullRHI process fresh-audited those 29 serialized
assets plus all 25 routing-only bank bindings. It contains no authored
production `MS_` MetaSound. All 25 governed authentic-audio categories remain
unapproved or missing. Legacy `/Game/Skyguard/Audio/Imported` assets also remain
inside Content and are forbidden at the Shipping boundary.

## What is verified offline

- The exact 25-category C++ enum, acquisition briefs, authentic-source
  manifest, and Unreal import contract agree.
- All 25 categories have an explicit final MetaSound composition destination.
- The ten direct runtime event bindings match the declared bank categories.
- The audio director asynchronously primes Sound, attenuation, concurrency,
  and submix soft references.
- Gameplay event dispatch uses already-resolved soft references and has no
  synchronous load call in the director.
- Cooldowns, per-event concurrency limits, priority eviction, and the global
  voice limit are present in current source.
- Mission integration directors 01–10 prime configured audio during briefing.
- The seven P5-A routing scaffold files and production bank are present.
- The governed production bank is now requested asynchronously by the native
  audio director; a native mission no longer depends on an unassigned Blueprint
  property to discover it.
- All five Yak-52/wind loop routes now retain their Sound, attenuation,
  concurrency, and output-submix references after the bank is applied.
- Rifle fire, Igla search/lock/launch/impact, and light/heavy drone destruction
  dispatch through the registered mission audio director. The former direct,
  synchronous `/Audio/Imported` explosion load was removed from drone death.
- The exact authoring recipes for 15 attenuation assets, 14 concurrency assets,
  and six MetaSound interfaces are governed by
  `PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json`.
- All 29 attenuation/concurrency primitives have now been serialized and
  reopened in an independent NullRHI process. The fresh receipt proves 25 of
  25 route-only bank bindings while preserving 25 null/MISSING_SOURCE entries.
- The offline gate emits a read-only Windows host-audio receipt. Nahimic or
  `DeviceRoutingDaemonModule.dll` faults are reported separately and are not
  misattributed to Skyguard.

## What is not verified offline

A `.uasset` filename cannot prove its class, serialized references, submix
parentage, attenuation curve, concurrency rule, MetaSound graph, parameter
binding, or cook behavior. Those facts require a fresh Unreal-side audit.

An editor audit cannot prove that the mix is audible, glitch-free, performant,
or correctly spatialized in the packaged game. That requires packaged combat
soak telemetry and independent listening.

## Required authoring sequence

1. Acquire or record authentic sources and complete provenance without
   importing unapproved media.
2. Preserve and hash-bind the 29 routing primitives during the final graph
   audit.
3. Author six MetaSound graphs: Yak-52 identity bed, rifle shot, Igla weapon,
   drone propulsion, small explosion, and heavy explosion.
4. Bind every bank entry to approved SoundWave, attenuation, concurrency, and
   output-submix assets.
5. Run the fresh Unreal serialized-routing verifier.
6. Remove legacy Imported audio from every Shipping dependency and cook rule.
7. Run packaged audible acceptance across briefing, ADS fire, Igla, drone
   destruction, boss destruction, radio-over-combat, and cockpit/exterior
   translation.

Before packaged listening, collect the host boundary:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  .\Scripts\collect_phase5_host_audio_diagnostics.ps1
```

This command is read-only. It does not stop Nahimic, change drivers, alter
services, or launch Unreal.

Run the offline audit:

```powershell
python .\Scripts\verify_phase5_audio_runtime_routing_readiness.py
```

Require final runtime readiness (expected to exit 3 until external authoring and
acceptance are complete):

```powershell
python .\Scripts\verify_phase5_audio_runtime_routing_readiness.py --require-runtime-ready
```
