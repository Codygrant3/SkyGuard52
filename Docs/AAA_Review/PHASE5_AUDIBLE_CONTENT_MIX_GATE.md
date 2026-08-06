# Phase 5 — Audible Content and Mix Gate

## Lawful development path

`USkyguardAudioProceduralBankComponent` generates six deterministic,
project-owned mono PCM signals:

- rifle impulse;
- Igla lock tone;
- Igla launch impulse;
- small explosion;
- heavy explosion;
- radio beep.

These signals exist only to exercise the audio device, routing, cooldown,
ducking and packaging path before source-recorded or licensed production audio
arrives. They are deliberately marked **audition**, are compile-time blocked in
Shipping, use a hard one-megabyte PCM budget, and are not wired into the combat
sound director.

They must never be represented as realistic weapon, aircraft, missile or
explosion recordings. They are sequential QA signals, not concurrency-safe
combat content.

## Mix acceptance targets

The production mix must be evaluated from a packaged Development build with the
rear-cockpit and exterior listener perspectives:

| Bus | Relative target | Required checks |
|---|---:|---|
| Master | ceiling at or below -1 dBTP | no clipping during boss destruction |
| Dialogue/radio | intelligible above engine | subtitles remain independent |
| Weapons | transient priority over engine | no repeated-shot voice starvation |
| Explosions | strongest transient class | suppression recovers deterministically |
| Engine/propeller | continuous bed | no loop gaps or RPM phasing |
| Wind | speed/canopy dependent | no camera-orientation pumping |
| Drones | range/direction legible | distinct light/heavy signatures |

Final numeric LUFS targets must be chosen by the sound designer after calibrated
monitoring; they are not fabricated here.

## Required source-content ledger

Every production file requires:

- source owner or marketplace publisher;
- license identifier and permitted redistribution;
- original filename and immutable hash;
- recording/sample rate, channels and bit depth;
- edit/master derivation;
- in-project asset path;
- assigned Sound Cue/MetaSound, attenuation and concurrency asset;
- mission/category usage.

Missing provenance is a release blocker.

## Remaining blockers

- Source-recorded or properly licensed Yak-52 radial engine and propeller loops.
- Open-canopy wind recordings at representative airspeeds.
- Layered rifle muzzle, mechanism, casing and distant reflection.
- Igla seeker, launch motor, fly-by and impact.
- Distinct Shahed and heavy-drone signatures.
- Layered small/heavy explosions and debris tails.
- Cockpit/exterior submixes, attenuation and convolution/impulse-response policy.
- Ukrainian and English performances for all mission radio lines.
- Audible packaged-build playback evidence.
- Voice count, decode/streaming cost, underrun and game-thread telemetry.
- Calibrated loudness, true-peak and translation review.

Until these exist, Phase 5 has a verified structural contract and a lawful
audition path—not final audible acceptance.

## Verification — 2026-08-01 CDT

- `Skyguard52Editor Win64 Development`: UHT, compile and link **PASS**.
- Focused `Skyguard52.Audio` automation: **3/3 Success**.
- Procedural audition generation: six cues, 573,120 bytes against a 1,048,576-byte hard budget.
- Deterministic checksums matched across two independent bank builds.
- Disabling development audition cleared the bank and prevented playback.
- Zero failed tests, fatal errors or ensure failures.

Evidence:

`D:\Skyguard52\Saved\Logs\Phase5AudioAutomation04.stdout.log`

This NullRHI run validates signal construction and control flow. It does not
produce audible playback evidence and does not validate sound quality,
spatialization, streaming, device underruns or a packaged mix.

The production source bank, routing contract and refusal-based packaged
acceptance harness are defined in
`D:\Skyguard52\Docs\AAA_Review\PHASE5_PRODUCTION_AUDIO_INTEGRATION.md`.
Until its 25 source entries and seven routing assets are complete, the
authoritative result remains `BLOCKED_MISSING_SOURCE`.
