# Phase 5 — Authentic Audio Unreal Import and Mix Runbook

This runbook begins only after an entry in
`PHASE5_AUTHENTIC_AUDIO_ACQUISITION_MANIFEST.json` reaches
`APPROVED_FOR_GOVERNED_IMPORT`. The current manifest is empty and blocked.

Before external acquisition, the offline contract set is:

- `PHASE5_AUDIO_RECORDING_SESSION_SCHEMA.json`
- `PHASE5_AUDIO_RECORDING_SESSION_MANIFEST.json`
- `PHASE5_AUDIO_SOURCE_SESSION_RECORDING_PLAN.md`
- `PHASE5_AUDIO_UNREAL_IMPORT_NAMING_LOUDNESS_CONTRACT.json`
- `Scripts/verify_phase5_audio_production_readiness.py`
- `Scripts/run_phase5_audio_offline_readiness_gate.ps1`
- `PHASE5_AUDIO_SHIPPING_BOUNDARY_POLICY.json`
- `PHASE5_AUDIO_SHIPPING_BOUNDARY.md`
- `Scripts/verify_phase5_audio_shipping_boundary.py`

The recording-session lane covers only project-owned Yak-52 and rear-open-canopy
identity recording. Rifle, missile, drone and explosion sources remain in the
licensed specialist-library lane.

## 1. Evidence freeze before touching Unreal

For every source:

1. Archive the governing license, invoice/grant, source page, vendor response
   and recorder metadata outside the Unreal `Content` tree.
2. Hash each document and immutable original with SHA-256.
3. Record licensed identity, users/seats, territory, term, permitted media,
   editing rights, cooked-distribution rights and standalone-file restrictions.
4. Verify recorder claims independently. Aircraft/state/perspective labels from
   a filename alone do not prove RPM, load, canopy state or microphone position.
5. Keep originals read-only. Every edit produces a separately named and hashed
   derivative plus an edit-decision log.
6. Run `verify_phase5_authentic_audio_acquisition.py`. Do not open Unreal if the
   selected entry is not importable.

## 2. Delivery and naming

- Delivery derivative: PCM WAV, 48 kHz, 24-bit.
- Preserve source channel layout when useful; author mono emitter derivatives
  separately from stereo cockpit/environmental perspectives.
- No MP3/AAC/transcoded preview may become a production master.
- Prefixes:
  - `SW_` SoundWave;
  - `MS_` MetaSound Source;
  - `SC_` Sound Cue where MetaSound is unnecessary;
  - `ATT_` Sound Attenuation;
  - `CON_` Sound Concurrency;
  - `SMX_` Sound Submix;
  - `MIX_` SoundMix.
- Variant suffixes use `_V01`, `_V02`; listener suffixes use `_Cockpit`,
  `_ExteriorClose`, `_ExteriorMedium`.
- Governed root: `/Game/Skyguard/Audio/Production/`.

Never import immutable originals directly. Import only the approved derivative
whose hash appears in the manifest.

Every governed SoundWave name begins with `SW_`; `S_` is not accepted. Record
LUFS-I, maximum LUFS-S, true peak, DC offset, clipped-sample count and duration
for each derivative. Offline derivatives must contain zero clipped samples and
remain at or below -3 dBTP. Do not normalize loops and transients to one shared
LUFS number. Interactive master acceptance remains a separate audible gate at
or below -1 dBTP.

## 3. Loop preparation

Engine, propeller, wind and drone propulsion loops require:

- stable logged state with transition material excluded;
- two candidate loop regions reviewed independently;
- sample-accurate start/end points;
- equal-power crossfade long enough to hide the seam without smearing blade
  passage or engine pulse;
- matching DC offset and zero-crossing review;
- phase/coherence review across synchronized microphones;
- no RPM wander, comb filtering, click, gain step or periodic pumping;
- at least ten seconds of handles retained in the edit archive;
- loop points and derivative hash recorded in provenance.

Do not create a cruise or power loop from a fly-by unless a stable, motion-free
region is demonstrated. Do not synthesize final open-canopy wind from white
noise.

## 4. MetaSounds and cues

### Yak-52 continuous identity

Author `MS_Yak52_IdentityBed` with separate parameters for normalized RPM,
engine load, true airspeed, rear-canopy opening and listener perspective.

- Idle, cruise and power layers crossfade by RPM/load; avoid abrupt state
  switches.
- Propeller blade-passage remains separately controllable and phase-checked
  against engine layers.
- Open-cockpit wind follows airspeed and canopy fraction, not camera yaw.
- Cockpit and exterior recordings remain distinct layers. Do not fake exterior
  solely by boosting an interior recording.
- Prime all continuous sources during briefing through existing soft references.
  Gameplay must not synchronously load them.

### Rifle

Author `MS_RifleShot` from separately approved muzzle, mechanical, casing and
reflection derivatives. Use non-repeating variation selection, small bounded
pitch/gain variation, animation-synchronized mechanics and distance-appropriate
reflection. Do not allow casing/mechanical layers to consume unbounded voices.

### Igla and missile

- `MS_IglaLaunch`: seeker/lock, launch transient and motor/tail are distinct.
- `MS_MissileFlight`: emitter flight/fly-by with Doppler handled by Unreal, not
  baked into a generic orbital-rocket recording.
- Launch must originate from the correct tube end and missile actor socket.

### Drone impact/explosion

Author `MS_DroneImpactExplosion` with crack, body, debris and environmental tail
layers, separate small/heavy variants and deterministic priority. Impact should
trigger hearing suppression through the existing director without a synchronous
asset load.

## 5. Routing

Use the governed seven-asset topology:

- `SMX_Master`
- `SMX_Cockpit`
- `SMX_Exterior`
- `SMX_Weapons`
- `SMX_Explosions`
- `SMX_Radio`
- `MIX_Cockpit`

Route engine/wind interior layers to Cockpit, external prop/engine to Exterior,
rifle/Igla/missile to Weapons, impact layers to Explosions, and mission voice to
Radio. Keep current authored starting values of 0.72 cockpit exterior
attenuation and 7200 Hz cockpit low-pass until calibrated listening supports a
change.

## 6. Concurrency and attenuation

- Continuous aircraft identity: one persistent instance per aircraft/layer.
- Rifle: bounded per-event concurrency with oldest/lowest-priority eviction.
- Igla launch: protect the launch transient; do not let seeker tones starve it.
- Missile flight: one emitter voice per live missile with distance culling.
- Debris/tails: lower priority than crack/body; aggressively limit repeated
  saturation events.
- Keep the director hard budget at 24 and packaged acceptance at no more than
  48 active voices.
- Use aircraft-attached interior/exterior attenuation for engine/propeller,
  non-spatial cockpit bed for local wind, and spatial emitter attenuation for
  weapons, missiles and impacts.
- Validate rear-cockpit and exterior listener transitions; no phase collapse,
  double playback or orientation pumping.

## 7. Gain, loudness and headroom

- Do not normalize every file independently.
- Preserve transient crest factor and category-relative dynamics.
- Raw capture should retain at least 12 dB of unclipped headroom.
- Final Master must remain at or below -1 dBTP during the densest boss
  destruction case.
- Choose LUFS targets only after calibrated monitoring and translation review;
  do not invent a numeric integrated target from offline inspection.
- Radio must remain intelligible without erasing aircraft identity.
- Weapon transients outrank the continuous engine bed; explosion crack/body are
  the strongest transient class, followed by deterministic suppression/recovery.

## 8. Import and binding transaction

1. Create an immutable import attempt receipt.
2. Import the approved derivative into its exact governed destination.
3. Verify SoundWave sample rate, channels, duration, looping and streaming
   settings against the manifest.
4. Create/update MetaSound or Sound Cue, attenuation and concurrency assets.
5. Bind output submix.
6. Update only the intended production-bank entry with Sound, provenance ID and
   immutable source hash.
7. Run fresh-process persistence audit. Never infer persistence from the
   builder's in-memory state.
8. If any check fails, leave the entry missing or quarantined; do not partially
   promote it.

## 9. Packaged performance acceptance

In a packaged audible Development build:

- meter at least 600 samples;
- audio thread maximum at or below 2 ms;
- zero underruns;
- no more than 48 active voices;
- Master true peak at or below -1 dBTP;
- no loop gaps, first-use synchronous-load hitch, missing route or voice
  starvation;
- test rear-cockpit, exterior, ADS rifle cadence, Igla flight and simultaneous
  heavy destruction;
- hash the exact executable, content containers and acceptance evidence.

## 10. Packaged anti-extraction and license checks

License compliance cannot rely on an assertion that cooked assets are
impossible to extract.

- Confirm no immutable original, source archive, vendor preview, edit session,
  source-page cache, license document or loose WAV exists in Staged, Saved,
  packaged directories or installer payload.
- Confirm production derivatives are cooked into Unreal IoStore containers and
  are not shipped as loose files.
- Search the packaged tree for original filenames, source hashes, vendor signed
  preview URLs and common audio extensions.
- If project policy later enables container encryption/signing, preserve key
  handling and build receipts separately; encryption is defense-in-depth, not
  permission to violate the license.
- Perform a reasonable extraction-risk review against the vendor's written
  requirements and record the reviewer/date/tooling.
- Verify credits/attribution and share-alike notices when a source requires them.
- Re-run the acquisition validator and packaged release supervisor against the
  exact build hash.

Passing this runbook authorizes a governed import attempt only. Full Phase 5
production readiness still requires all 25 production-bank categories, all
seven routing assets and audible packaged acceptance.

## Current external blockers

As of the empty governed manifests:

1. The Yak-52 session needs exact aircraft identity, a qualified operator,
   location/date, five approved and hashed rights/operations evidence records,
   a restrained microphone/recorder plan, and eleven completed logged shots.
2. A matching rifle library needs at least six muzzle variations and governed
   mechanical, casing and reflection layers.
3. An Igla-appropriate licensed set needs search, lock, launch, fly-by and
   impact components; unrelated rockets are not acceptable substitutes.
4. Light and heavy piston-UAV motor loops plus clean fly-bys are required;
   electric multirotors are not acceptable substitutes.
5. Small and heavy explosion systems each need crack, body, debris and
   environment-tail variations.
6. Ukrainian and English radio requires scripts, casting, performer releases
   and project-owned or expressly licensed recordings.
7. Every source needs immutable license/source evidence, SHA-256, semantic
   metadata review, a separately hashed edit log and derivative, and extraction
   risk review.
8. The seven routing and production-bank binaries are locally present, but
   still require a fresh serialized Unreal audit after sources are approved.
9. Existing C++ hard references to `/Game/Skyguard/Audio/Imported/` and the 14
   legacy OGG files under `Content/Skyguard/Audio/Source` remain unproven. They
   must be replaced by governed production-bank bindings or explicitly excluded
   from Shipping; their presence is not authentic-audio acceptance.

The release pipeline must run
`python Scripts/verify_phase5_audio_shipping_boundary.py` without
`--audit-only`. Exit code `3` is the expected current result and must stop a
Shipping cook. The audit-only form is for routine planning reports and does not
authorize release.
