# Phase 5 P5-A — Yak-52 Identity Source Evidence

The production identity bed still has **zero approved source candidates**.
This is intentional. The researched CC0 references have useful license records,
but none proves Yak-52 semantic identity:

- the C-47 interior is a different, multi-engine aircraft;
- the radial biplane and generic propeller clips are fly-bys rather than
  controlled RPM/load recordings;
- synthesized white noise is not authentic rear-cockpit airflow.

They are formally rejected as production identity sources in:

`D:\Skyguard52\Docs\AAA_Review\PHASE5_P5A_IDENTITY_SOURCE_EVIDENCE_CONTRACT.json`

## Governed next acquisition

The preferred route is a controlled, project-owned Yak-52 recording session.
That route is not itself a source candidate. It becomes one only after a
specific aircraft, operator, session, signed agreement, embedded-game
redistribution rights, recording log and immutable captures exist.

Rights evidence must explicitly cover commercial interactive-game use,
derivative editing, cooked-build distribution, marketing use, worldwide scope
and continued use by already-distributed builds. Raw recordings stay outside
the shipped product and may not be redistributed as a sound library.

Semantic evidence must bind every recording to the actual aircraft, engine and
propeller configuration, operating state, RPM/load, listener position and—for
open-cockpit wind—airspeed and rear-canopy opening. Generic aircraft,
uncontrolled fly-bys and synthetic wind cannot pass.

Until all three independent approvals—rights, semantic match and technical
ingest—exist, the files must not be downloaded into the governed source
archive, auditioned as candidates, imported into Unreal, or bound in the
production bank. Audible QA is a later gate and audition never equals binding.

## Offline audit

Run:

`python D:\Skyguard52\Scripts\verify_phase5_p5a_identity_source_evidence.py`

The normal command validates the blocked contract and exits zero.
`--require-candidate` must exit 3 while no evidence-complete source exists.
`--require-ready` must exit 4 while the five categories remain missing.
