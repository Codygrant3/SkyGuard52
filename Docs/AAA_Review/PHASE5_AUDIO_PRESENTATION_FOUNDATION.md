# Phase 5 — Audio and Presentation Foundation

## Implemented native contract

`USkyguardAudioDirectorComponent` is the aircraft-level runtime sound authority. It provides:

- normalized idle, cruise, power, propeller and open-cockpit wind layers;
- rear-cockpit versus exterior listener filtering;
- rifle, Igla, drone, explosion and debris event categories;
- per-event cooldown, concurrency, duration and priority policy;
- a hard global voice budget with higher-priority eviction;
- temporary hearing suppression and mix ducking;
- asynchronous briefing-time priming through soft asset references;
- request, rejection, eviction and peak-voice telemetry;
- graceful silence when final recordings are absent or not resident.

`USkyguardRadioChatterComponent` provides:

- priority-ordered mission chatter;
- bounded queue length;
- lower-priority displacement by urgent calls;
- per-line cooldowns and deterministic timing;
- subtitle and speaker metadata independent of audio availability;
- UI-facing line-start and line-finish delegates for subtitles and speaker cards;
- asynchronous briefing-time voice-line priming through soft references;
- dropped-line and played-line telemetry.

## Integration contract

Add both components to the final Yak-52 actor. Call `PrimeConfiguredAssets` while the player reads the mission briefing. Drive `SetEngineState` from normalized radial-engine RPM/load, true airspeed, and rear-canopy opening. Route combat events through `TriggerEvent`; the game systems do not load WAV assets synchronously.

Close explosions should call `ApplyHearingSuppression`. Camera changes should call `SetListenerPerspective`. Mission logic should enqueue semantic radio lines rather than directly playing files.

## Acceptance automation

- `Skyguard52.Audio.Director.DeterministicStateAndBudgets`
- `Skyguard52.Audio.Radio.BoundedPriorityQueue`

The tests prove deterministic engine blending, timed suppression, bounded voices, priority eviction, bounded radio queues, priority order and cooldown behavior without requiring final sound assets.

## Content gaps before final mix

- Yak-52 radial engine recordings at idle, cruise and high load.
- Propeller blade-passage loop and open-canopy wind at several airspeeds.
- Rifle muzzle, mechanism, casing and distant-reflection layers.
- Igla search, lock, launch motor, fly-by and impact layers.
- Separate Shahed and heavy-drone motor/fly-by signatures.
- Small and heavy explosion crack/body/debris/tail layers.
- Cockpit impulse responses or authored submix treatment.
- Ukrainian/English radio performances and subtitles for all ten missions.
- Sound cues/MetaSounds, attenuation assets, concurrency assets and final loudness pass.

Final WAVs should be imported only after provenance and license records exist. Runtime audio profiling must validate voice count, game-thread cost and streaming behavior in a packaged combat soak.

## Verification — 2026-08-01 CDT

The native `Skyguard52Editor Win64 Development` target completed UHT, compilation and linking successfully against Unreal Engine 5.8. No additional module dependency was required.

Focused NullRHI automation evidence is preserved at:

`D:\Skyguard52\Saved\Logs\Phase5AudioAutomation04.stdout.log`

Results:

- three tests discovered from `Skyguard52.Audio`;
- `Skyguard52.Audio.Director.DeterministicStateAndBudgets`: **Success**;
- `Skyguard52.Audio.ProceduralAudition.DeterministicBoundedSignals`: **Success**;
- `Skyguard52.Audio.Radio.BoundedPriorityQueue`: **Success**;
- zero failed tests;
- zero fatal errors;
- zero ensure failures.

This is a structural and deterministic runtime-foundation pass. It does not claim final audible quality because the licensed recordings, MetaSounds/Sound Cues, attenuation, acoustic routing, localized voice performances and packaged-build mix/profile pass remain content work.

The lawful native audition path and its strict non-shipping boundary are
specified separately in
`D:\Skyguard52\Docs\AAA_Review\PHASE5_AUDIBLE_CONTENT_MIX_GATE.md`.
