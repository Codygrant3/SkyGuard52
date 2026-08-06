# Phase 8 — Release Tier and Audio Prepackage Contract

## Outcome

Phase 8 now evaluates authentic production audio before UAT, cook, stage,
package, archive, mission soak, or Shipping smoke begins.

Contract:

`D:\Skyguard52\Docs\AAA_Review\PHASE8_RELEASE_TIER_CONTRACT.json`

Preflight:

`D:\Skyguard52\Scripts\verify_skyguard_phase8_release_tier.py`

Supervisor:

`D:\Skyguard52\Scripts\run_skyguard_phase8_release_gate.ps1`

## Tiers

### Engineering

Purpose: internal reproducibility, performance baselines and developer testing.

Engineering may package while authentic audio is blocked only when its receipt
records:

- `engineering_audio_exception_requested=true`;
- `engineering_audio_exception_applied=true`;
- the exact current audio blockers;
- `external_distribution_allowed=false`;
- `shipping_promotion_allowed=false`.

This exception does not change any acquisition state and does not claim
production audio.

The supervisor’s backward-compatible defaults are `Engineering` and an enabled
Engineering audio exception. The preferred explicit command is:

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_phase8_release_gate.ps1 `
  -ReleaseTier Engineering `
  -EngineeringAudioException $true
```

### AAA

Purpose: final AAA acceptance candidate. Authentic production audio is
mandatory. No Engineering exception is accepted.

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_phase8_release_gate.ps1 `
  -ReleaseTier AAA
```

### FriendFacing

Purpose: any package intended for friends or another external recipient.
Authentic production audio and every Phase 5 Shipping boundary are mandatory.

```powershell
powershell -ExecutionPolicy Bypass -File `
  D:\Skyguard52\Scripts\run_skyguard_phase8_release_gate.ps1 `
  -ReleaseTier FriendFacing
```

With the current blocked audio evidence, AAA and FriendFacing both return exit
code `3` before packaging.

## Execution ordering

For every new Phase 8 attempt:

1. Create the immutable attempt manifest and artifact directory.
2. Run harness self-checks.
3. Run the release-tier audio preflight and persist its receipt.
4. Stop immediately with `RELEASE_TIER_PREFLIGHT_FAILED` if the tier is not
   allowed.
5. Only then run cook-contract checks, process-lane checks and optional UAT.

The independent Phase 8 verifier requires the receipt to match the manifest’s
tier and effective exception flag. Engineering receipts must forbid external
distribution and Shipping promotion. AAA/FriendFacing receipts must show
`PASS_SHIPPING_AUDIO_BOUNDARY`, no exception, and production-audio acceptance.

## Historical evidence

Immutable Phase 8 manifests created before this contract are preserved as
Engineering-only baselines with
`historical_implicit_engineering_exception=true`. This compatibility rule does
not authorize rerunning them as AAA or FriendFacing and cannot upgrade the
audio state.

Every new supervisor attempt writes an explicit tier receipt.
