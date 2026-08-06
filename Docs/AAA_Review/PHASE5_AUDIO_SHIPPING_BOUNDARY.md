# Phase 5 — Fail-Closed Audio Shipping Boundary

## Purpose

The development project still contains unverified legacy audio. This boundary
prevents that material from being mistaken for authenticated production audio
or promoted into a Shipping build.

Policy:

`D:\Skyguard52\Docs\AAA_Review\PHASE5_AUDIO_SHIPPING_BOUNDARY_POLICY.json`

Gate:

`D:\Skyguard52\Scripts\verify_phase5_audio_shipping_boundary.py`

Latest evidence:

`D:\Skyguard52\Saved\Reports\PHASE5_AUDIO_SHIPPING_BOUNDARY_AUDIT.json`

## Two invocation modes

Routine planning audit:

```powershell
python D:\Skyguard52\Scripts\verify_phase5_audio_shipping_boundary.py --audit-only
```

This returns zero when the policy is valid, while the report continues to say
`BLOCK_SHIPPING_UNVERIFIED_AUDIO`.

Actual Shipping/release gate:

```powershell
python D:\Skyguard52\Scripts\verify_phase5_audio_shipping_boundary.py
```

This is fail-closed. It returns exit code `3` while any Shipping blocker
remains. Invalid policy or malformed contracts return exit code `2`.

Build or release automation must call the second form before any Shipping cook,
package, installer, upload, or public release. It must treat every nonzero exit
as a hard stop.

## Current blocked evidence

The offline scanner currently finds:

- 13 C++ runtime references to `/Game/Skyguard/Audio/Imported/`;
- one `DirectoriesToAlwaysCook` directive for the legacy Imported directory;
- 14 legacy imported `.uasset` files;
- 14 loose OGG source files under the Unreal Content tree;
- ten authentic source bundles still `MISSING_LICENSE_AND_SOURCE`;
- no accepted Phase 5 production-readiness state;
- no fresh serialized Unreal routing/import audit;
- no packaged audible acceptance.

This does not assert that the legacy files infringe anyone’s rights. It asserts
that their origin, license, semantic identity, derivatives, and Shipping terms
have not passed the governed Phase 5 evidence boundary.

## Safe closure order

1. Acquire and approve the authentic sources described in the recording and
   licensed-library plans.
2. Bind approved governed derivatives through the production bank.
3. Replace every gameplay hard reference to `/Audio/Imported/`.
4. Remove the Imported directory from `DirectoriesToAlwaysCook`.
5. Move immutable originals and loose source media outside the Unreal Content
   tree into the non-shipping evidence archive.
6. Remove legacy imported assets only after their production replacements are
   verified and no runtime reference remains.
7. Run the fresh serialized Unreal routing/import persistence audit.
8. Run packaged audible and anti-extraction acceptance.
9. Run the Shipping gate without `--audit-only`; only exit zero permits release.

Do not silence the gate by adding allowlists, renaming legacy directories, or
changing states without the required evidence. Development quarantine is not
Shipping acceptance.
