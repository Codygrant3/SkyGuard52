# Phase 5 — Category Recording and Acquisition Briefs

The authoritative machine-readable briefs are:

`D:\Skyguard52\Docs\AAA_Review\PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json`

They cover all 25 production-bank categories and bind each category to:

- project-owned recording or licensed-library acquisition;
- an identity/semantic requirement;
- capture or library-delivery specifications;
- cockpit/exterior listener perspectives;
- rights and provenance requirements;
- Unreal destination, submix, attenuation and concurrency contracts;
- category-specific acceptance tests;
- an explicit source state.

## Production groups

| Group | Categories | Current state | Closure owner |
|---|---:|---|---|
| Yak-52 and airflow | 5 | `MISSING_SOURCE` | project-owned recording agreement |
| Rifle | 4 | `MISSING_SOURCE` | final weapon decision plus licensed library |
| Igla | 5 | `MISSING_SOURCE` | specialist licensed library |
| Drones | 3 | `MISSING_SOURCE` | verified piston-UAV library |
| Explosions | 8 | `MISSING_SOURCE` | layered licensed/project-owned effects |

## Offline guard

Run:

`python D:\Skyguard52\Scripts\verify_phase5_audio_acquisition_contract.py`

This validates structure and writes:

`D:\Skyguard52\Saved\Reports\PHASE5_AUDIO_ACQUISITION_CONTRACT_AUDIT.json`

The normal validation command can pass while reporting
`CONTRACT_VALID_BLOCKED_MISSING_SOURCE`; this means the plan is complete and
honest, not that audio is ready.

Release automation must use:

`python D:\Skyguard52\Scripts\verify_phase5_audio_acquisition_contract.py --require-ready`

That mode exits nonzero until:

- all 25 categories are `PRODUCTION_BOUND`;
- every bound entry has source and derivative SHA-256, rights approval, audio-QA
  approval, and Unreal routing assignments;
- all seven routing assets are present;
- the provenance gate advances to `READY_FOR_AUDIBLE_ACCEPTANCE`.

No source may advance merely because its webpage displays a permissible
license. Semantic fit, technical quality, provenance and listening review are
separate gates.

