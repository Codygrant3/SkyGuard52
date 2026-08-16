# Skyguard 52 Production Control

This directory is the mutable, canonical production queue for the Unreal 5.8
and Blender 5.2 build.

Historical `Docs\AAA_Review`, `Saved\Reports`, and `Saved\BuildAttempts`
artifacts remain immutable evidence. They are not the day-to-day scheduler.

## Live P0 — Apache CPG hero slice (2026-08-16)

The live art queue is Apache front-seat CPG. Yak-52 / rifle / Igla /
Shahed-as-P0 hero loops are archived, not deleted.

`python .\Scripts\skyguard_production.py next --limit 15` should surface these
first:

1. `core-apache-cockpit` — CPG front-seat cockpit
2. `core-apache-cockpit-station-detail01` — CPG station detail01 with eyepoint review (additional queued method; does not supersede cockpit until accepted)
3. `core-apache-cockpit-station-model01` — CPG station model01 with formed bmesh geometry and eyepoint review (additional queued method; does not supersede station-detail01 until accepted)
4. `core-apache-cockpit-station-model02` — CPG station model02 with clear greenhouse and explicit TEDAC hood (additional queued method; does not supersede station-model01 until accepted)
5. `core-apache-cockpit-station-model03` — CPG station model03 with formed seat, canopy frame, and knobs (additional queued method; does not supersede station-model02 until accepted)
6. `core-apache-30mm` — 30 mm chin gun
7. `core-apache-hydra` — Hydra / rocket pods
8. `core-apache-hellfire` — Hellfire / guided missile and launch rail
9. `core-apache-airframe` — exterior airframe

Lane `P0-apache-cpg-hero-slice` is first in `execution_order`. Archived items
remain in `P0-cockpit-combat-vertical-slice` as `deferred`, so `next` skips
them. Do not flip any of these Apache assets to `ready` or `accepted` without
a real worker, one `production_cycle` run, and Human + Codex full-resolution
review. No ready→accepted skip.

`core-apache-cockpit` has a registered governed worker at
`Scripts\Workers\worker_core_apache_cockpit.py` and stays `queued`.
`core-apache-cockpit-station-detail01`,
`core-apache-cockpit-station-model01`,
`core-apache-cockpit-station-model02`, and
`core-apache-cockpit-station-model03` are additional queued Apache P0
methods with their own workers and output contracts. Do not launch
Blender, do not accept art, and do not invent workers for the remaining
Apache P0 weapons/airframe assets from Cloud. No ready→accepted skip.

## Standing Blender and Unreal authorization

The user's standing authorization is recorded in
`Production\standing_heavy_process_authorization.json`. Governed Blender,
UnrealEditor, UnrealEditor-Cmd, build, render, capture, profiling, integration,
and Development-package gates no longer stop for a new conversational approval.
Existing `-AuthorizeSingle*` parameters remain mechanical one-shot guards and
the controller may supply them after preflight passes.

Standing authorization does not weaken the production controls: one heavy
process at a time, a fresh namespace, zero automatic retries, immutable attempt
evidence, mandatory contracted postflight, direct visual review, and reversible
integration remain required. Windows UAC or third-party license/purchase prompts
are operating-system or vendor boundaries and are not bypassed by this policy.

## Commands

Run from `D:\Skyguard52`:

```powershell
python .\Scripts\skyguard_production.py audit
python .\Scripts\skyguard_production.py preflight
python .\Scripts\skyguard_production.py next --limit 15
python .\Scripts\validate_skyguard_production.py
```

To move an Apache P0 asset after a real worker and contract are registered:

```powershell
python .\Scripts\skyguard_production.py set-state core-apache-cockpit ready `
  --reason "Reference-backed worker and output contract validated."
```

Do not run that `set-state` or a `production_cycle` launch until the user
asks. `core-apache-cockpit`, `core-apache-cockpit-station-detail01`,
`core-apache-cockpit-station-model01`,
`core-apache-cockpit-station-model02`, and
`core-apache-cockpit-station-model03` have registered workers and stay
`queued`. The remaining Apache P0 weapon and airframe assets still have
no worker.

Archived Yak / rifle / Igla / Shahed-as-P0 lanes stay `deferred`. Historical
cycle examples such as `core-shahed136` are evidence only and are not the
next art action.

To audit and run the registered cockpit worker together with its mandatory
automatic postflight (only when the user asks for a Blender launch):

```powershell
python .\Scripts\skyguard_production_cycle.py audit core-apache-cockpit
python .\Scripts\skyguard_production_cycle.py run core-apache-cockpit
```

This cycle command is the preferred production entry point. It leaves a passing
asset in `awaiting_review`, because direct full-resolution visual review still
cannot be automated into acceptance. If the registered postflight rejects the
outputs, it fails the lane and preserves both the Blender attempt and postflight
evidence without retrying.

Hero lanes may also define a `quality_gate` in
`Production\ready_blender_output_contracts.json`. This inexpensive triage checks
renderable topology density, UV coverage, material diversity, and unreadable
review frames. It exists to reject obvious proxy output early; it never replaces
direct full-resolution review and never authorizes Unreal import.

New hero workers should also call `Scripts\blender_pre_render_quality_gate.py`
after geometry/material construction and before final rendering. The worker must
preserve the receipt even on failure. This prevents a known proxy mesh from
consuming the full final-render budget.

## Durable visual-feedback guard

`Production\visual_feedback_memory.json` converts repeated full-resolution
visual failures into a strategy constraint. The controller validates guarded
assets against it before a heavy launch. Once a lane reaches `PIVOT_REQUIRED`,
lighting-only, cosmetic-only, same-namespace, full-corridor-first, and
whole-scene procedural-primitive retries are refused.

Inspect or test a proposed strategy with:

```powershell
python .\Scripts\skyguard_visual_feedback.py evaluate --lane m01_environment
python .\Scripts\skyguard_visual_feedback.py guard --lane m01_environment `
  --strategy-tag asset_specific `
  --strategy-tag authored_geometry `
  --strategy-tag checkpointed_visual_review `
  --strategy-tag governed_local_pbr `
  --strategy-tag small_hero_cell
```

This guard does not choose art automatically and never grants visual
acceptance. It prevents a rejected production method from being renamed and
repeated without a substantive strategy change.

The lower-level worker-only command remains available for diagnostics:

```powershell
python .\Scripts\skyguard_production.py run support-rail-coupon
```

The controller:

- refuses a second heavy process;
- verifies tool hashes and machine headroom;
- creates a new attempt namespace;
- launches Blender once;
- records stdout, stderr, PID, exit code, outputs, and hashes;
- never retries automatically;
- leaves successful outputs in `awaiting_review`.

Asset-specific Blender workers should derive from:

- `Scripts\skyguard_blender_worker_sdk.py`
- `Scripts\skyguard_blender_worker_template.py`

The SDK centralizes Blender 5.2 metric units, `PLAIN_AXES` sockets, fixed review
cameras, renders, `.blend` save, GLB export, validation, and artifact receipts.
Its exact-host smoke test also proved why output validation is mandatory:
Blender may return process exit code `0` after a Python traceback.

After directly inspecting the governed renders:

```powershell
python .\Scripts\skyguard_production.py review support-rail-coupon `
  --decision accept `
  --reviewer "Codex plus user" `
  --notes "Dimensions and fixed-camera renders passed the registered rubric."
```

No asset may move directly from `ready` to `accepted`.

## State model

`queued` → ordinary work not yet executable  
`blocked_reference` → more authority is genuinely required  
`source_candidate` → geometry exists but is not accepted  
`provisional_blockout` → accepted only as a blockout  
`ready` → worker and contract are executable  
`running` → one governed process owns the heavy lock  
`awaiting_review` → outputs exist and require direct inspection  
`accepted` → approved for Unreal candidate import  
`failed` → attempt preserved; no automatic retry  
`deferred` → intentionally postponed

## Evidence model

The mutable manifest is written atomically and never hashes itself.
Each attempt gets one terminal receipt and hashes only its immutable inputs and
outputs. Release snapshots may hash a finalized manifest after it stops
changing.

This one-way evidence graph replaces the prior circular freeze pattern.
