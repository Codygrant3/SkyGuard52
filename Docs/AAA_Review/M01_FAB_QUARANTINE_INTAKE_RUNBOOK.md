# Mission 01 Fab/Quixel Quarantine Intake Gate

Status: `SOURCE_ONLY_FAIL_CLOSED`

This gate implements the coastal visual-review decision: retain
`BLD-M01-COAST-PROD-001` as the governed layout scaffold, but do not treat its
diagnostic terrain or midrise shells as final visible art. The first visible-art
inspection is limited to one Eastern European city kit and one beach/coast kit.

The initial template nominates:

- `Soviet Panels - Communist Eastern European Buildings Kit` for `CITY_KIT`;
- `Brushify - Beach Pack` for `BEACH_COAST_KIT`.

Nomination is not acceptance, ownership, purchase authorization, download
authorization, import authorization, runtime approval, or a license conclusion.

## Non-negotiable rules

- Do not purchase, download, or import automatically.
- Do not accept an asset because a matching folder or `.uasset` exists in
  `Content`.
- Do not inspect more than one city kit and one beach/coast kit in the first
  quarantine wave.
- Do not place quarantine assets in production `/Game/Skyguard/...` paths.
- Do not promote either kit to runtime use through this gate.
- Preserve the 100 m district dimensions, protected flight corridor, sockets,
  collision intent, and route composition defined by the coastal scaffold.

## Evidence staging

After the user manually chooses to acquire a nominated product, place immutable
evidence beneath:

```text
Saved/FabQuarantine/M01_FAB_QUARANTINE_INTAKE_001/
```

For each kit, capture and hash:

1. Product-page snapshot containing the exact URL, product ID, product name,
   seller, price, contents, and technical claims.
2. Exact license-tier text snapshot.
3. Receipt or free-acquisition confirmation.
4. Engine/platform compatibility evidence, including Unreal Engine 5.8 and
   cooked-Windows redistribution coverage.
5. Original download package or immutable package receipt with exact bytes.
6. Installed-file inventory with exact bytes and hashes.
7. Texture inventory grouped by width, height, count, format, and usage.
8. Evidence for Nanite, authored LODs, collision, and material instances,
   recording `supported: false` where a feature is genuinely absent.
9. Complete dependency inventory, using an empty list only when its evidence
   explicitly confirms no dependencies.
10. At least one additional immutable artifact record.

Every evidence object requires a relative path, positive byte count, and
lowercase SHA-256. Acquisition time must be ISO 8601 with a timezone. Paid
assets require a positive price; free assets require zero.

## Offline gate

From `D:\Skyguard52`:

```powershell
python .\Scripts\verify_m01_fab_quarantine_intake.py
```

The untouched template is expected to exit `3` with:

```text
gate_status: FAIL_CLOSED
disposition: HOLD_NO_PURCHASE_NO_IMPORT
```

This is the correct state before evidence exists.

Run source tests without launching Unreal, Blender, Fab, Bridge, a browser,
UBT, or UAT:

```powershell
python -m unittest .\Scripts\test_m01_fab_quarantine_intake.py
python -m py_compile .\Scripts\verify_m01_fab_quarantine_intake.py .\Scripts\test_m01_fab_quarantine_intake.py
```

## Manual inspection readiness

Only after both records are evidence-complete may the operator change:

```text
status = EVIDENCE_COMPLETE_READY_FOR_MANUAL_QUARANTINE_INSPECTION
quarantine_disposition = APPROVED_FOR_MANUAL_QUARANTINE_INSPECTION
final_disposition = QUARANTINE_ONLY_NOT_RUNTIME_APPROVED
```

Then run:

```powershell
python .\Scripts\verify_m01_fab_quarantine_intake.py --require-ready
```

A pass permits only a separately authorized, manual import into an isolated
quarantine project path. It does not permit purchase, import by this script,
production replacement, runtime promotion, or an AAA claim.

If either kit is unsuitable, retain complete evidence and set both records to
`REJECTED_BEFORE_IMPORT` / `REJECTED` with intake status
`EVIDENCE_COMPLETE_REJECTED`. A validated rejection remains non-importable.

## Subsequent gates

After a separately authorized quarantine import, require manual checks for:

- Ukrainian coastal facade language and non-repeating compositions;
- calibrated PBR sand, asphalt, concrete, plaster, metal, glass, salt, grime,
  wetness, and damage;
- Nanite/LOD, collision, shader complexity, texture memory, dependencies, and
  installed size;
- close, route-distance, and aerial views;
- daylight, overcast, night, wet, and storm conditions;
- matching performance evidence with unchanged snapping and corridor geometry.

Those checks belong to a later visual/runtime acceptance gate and cannot be
pre-approved here.
