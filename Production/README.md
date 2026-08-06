# Skyguard 52 Production Control

This directory is the mutable, canonical production queue for the Unreal 5.8
and Blender 5.2 build.

Historical `Docs\AAA_Review`, `Saved\Reports`, and `Saved\BuildAttempts`
artifacts remain immutable evidence. They are not the day-to-day scheduler.

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

To run exactly one registered Blender worker:

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
