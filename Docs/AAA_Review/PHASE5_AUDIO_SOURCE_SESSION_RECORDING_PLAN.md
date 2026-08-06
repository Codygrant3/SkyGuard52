# Phase 5 — Yak-52 Source Session and Recording Plan

## Outcome

The project-owned session is a governed capture of the Yak-52 identity bed:
engine idle, cruise and power; propeller blade passage; and rear-cockpit wind
with the rear canopy open. It does **not** include live rifle, missile,
pyrotechnic, or improvised-effects recording.

The authoritative machine-readable packet is:

- `PHASE5_AUDIO_RECORDING_SESSION_SCHEMA.json`
- `PHASE5_AUDIO_RECORDING_SESSION_MANIFEST.json`

The manifest is intentionally `PLANNING`. Empty evidence fields are blockers,
not placeholders that may be interpreted as approval.

## Go/no-go sequence

1. Identify the exact aircraft by model, serial/registration, engine and
   propeller configuration.
2. Obtain the operator, location, recordist-rights, performer/privacy, and
   operational/insurance evidence listed in the manifest.
3. Have a named rights reviewer hash and approve every evidence document.
4. Have the qualified aircraft operator approve all engine states, flight
   states, canopy openings, equipment positions and abort criteria.
5. Complete the microphone, recorder, restraint, hearing-protection and slate
   plans.
6. Run the offline session validator. `CLEARED_TO_RECORD` is invalid unless all
   evidence and setup fields are complete.
7. Record lossless isolated tracks without AGC, limiting, denoising,
   normalization or lossy transmission.
8. Hash originals at ingestion and move them into the non-shipping archive.
9. Verify metadata before any semantic claim such as “Yak-52 cruise” or
   “open rear cockpit.”
10. Create, meter, document and hash separate 48 kHz/24-bit PCM WAV
    derivatives. Only governed derivatives may reach Unreal.

## Shot design

The manifest carries eleven required shots:

- paired rear-cockpit and exterior warm idle;
- rear-cockpit taxi;
- rear-cockpit stabilized cruise and matched exterior passes;
- rear-cockpit sustained high power and matched exterior passes;
- slow power sweeps for transition authoring;
- low and high safe-airspeed rear-open-canopy wind;
- engine-off cockpit room tone/noise floor.

Every take must log the parameters named in `required_metadata`. RPM, manifold
pressure, airspeed or canopy opening may not be inferred later from filenames.
Exterior fly-bys supplement static/attached beds; they cannot be looped and
misrepresented as stable engine states.

## Suggested rig, subject to operator approval

- isolated multitrack recorder capable of 96 kHz/24-bit PCM;
- secured rear-cockpit binaural or spaced stereo pair with wind protection;
- vibration-isolated airframe/contact channel where safe;
- exterior close and medium microphones for ground runs;
- synchronized exterior pass recorder;
- redundant slate/time reference;
- independent wind/weather logging.

All equipment must be positively restrained and placed so it cannot interfere
with controls, visibility, emergency egress, canopy travel, pilot movement or
aircraft systems. The aircraft operator has final authority.

## Capture notes

- Target at least 12 dB of clean headroom; a clipped “hero” take is rejected.
- Keep at least ten seconds of stable handles around candidate loop regions.
- Capture multiple takes after any microphone or gain change.
- Log contaminating aircraft, voices, vehicles, wind gusts and handling noise.
- Do not ask for unsafe RPM, manifold pressure, airspeed, maneuver, canopy
  position or flight path for sound.
- No identifiable voice becomes production radio without a performer release
  and a separate approved dialogue session.

## External acquisition lane

The following remain specialist licensed-library or professionally supervised
sources and are not part of this aircraft session:

- matching rifle muzzle, mechanism, casing and reflection variations;
- Igla-appropriate search, lock, launch, fly-by and impact layers;
- piston-UAV light/heavy propulsion and fly-bys;
- small/heavy explosion crack, body, debris and environmental tails;
- Ukrainian and English radio performances.

Each license must allow commercial interactive-game use, modification, cooked
embedding, end-user distribution and promotional synchronization while
prohibiting standalone raw-source redistribution.

## Acceptance boundary

A completed session is still quarantined. It becomes production eligible only
after rights review, immutable hashing, metadata verification, edit logging,
audio QA, derivative metering, governed Unreal import and packaged audible mix
acceptance. No document in this plan asserts that any recording currently
exists or is licensed.
