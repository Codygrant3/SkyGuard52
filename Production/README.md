# Skyguard 52 Production Control

This directory is the mutable, canonical production queue for the Unreal 5.8
and Blender 5.2 build.

Historical `Docs\AAA_Review`, `Saved\Reports`, and `Saved\BuildAttempts`
artifacts remain immutable evidence. They are not the day-to-day scheduler.

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

To move an asset after its references and worker are ready:

```powershell
python .\Scripts\skyguard_production.py set-state core-hand-forearm ready `
  --reason "Reference-backed worker and output contract validated."
```

To audit and run exactly one registered Blender worker together with its
mandatory automatic postflight:

```powershell
python .\Scripts\skyguard_production_cycle.py audit core-shahed136
python .\Scripts\skyguard_production_cycle.py run core-shahed136
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
