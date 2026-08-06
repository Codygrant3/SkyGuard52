# Skyguard 52 — Mission 1 Fab/Bridge Provenance Reconciliation

Classification: `AWAITING_MANUAL_ACQUISITION_EVIDENCE`

## Current result

Fab and Bridge are enabled in `Skyguard52.uproject`, but no governed evidence
proves that the nominated city or beach kit—or any Quixel/Megascans asset—has
been acquired, staged, imported, or accepted.

The governed quarantine root does not exist:

`D:\Skyguard52\Saved\FabQuarantine\M01_FAB_QUARANTINE_INTAKE_001`

A read-only scan covered 1,417 `.uasset` files. It found:

- zero exact product-ID, seller, product-name, Megascans, Quixel, or canonical
  Megascans-package markers;
- zero matching imported-content directories;
- one broad occurrence of the word `bridge` in the Mission 9 Saturation Attack
  data asset, which is mission vocabulary rather than acquisition evidence.

No content is promoted or rejected from a filename scan alone. The result is
simply that acquisition and import remain unproven and therefore fail closed.

## Existing intake gate

The untouched quarantine template correctly reports:

- exit code `3`;
- `gate_status = FAIL_CLOSED`;
- `disposition = HOLD_NO_PURCHASE_NO_IMPORT`;
- 50 explicit missing-evidence findings.

All 13 existing focused tests pass.

## New downstream control

The final-use contract now binds a third-party source to:

- exact entitlement, license, and acquisition evidence;
- source inventory;
- exact `/Game/Skyguard/...` packages and on-disk hashes;
- Mission 1 use;
- dependency closure;
- technical, visual, and performance acceptance;
- shipping constraints and notice obligations;
- an exact build or package candidate.

It rejects quarantine package references and never treats a successful receipt
as release acceptance.

## Remaining action

Acquisition is a deliberate account/UI action and has not been performed.
Before any import:

1. choose at most one city kit and one coast kit;
2. preserve the exact product page, license tier, receipt, compatibility
   evidence, package, and installed inventory;
3. make the existing quarantine intake verifier pass;
4. complete technical evaluation;
5. request a separate one-shot quarantine-import authorization.

Gate 2—the Mission 1 native project build—remains the next executable heavy
gate and still requires its existing explicit one-shot authorization.

