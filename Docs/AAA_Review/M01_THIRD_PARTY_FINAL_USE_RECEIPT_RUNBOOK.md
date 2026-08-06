# Mission 1 Third-Party Final-Use Receipt

Status: `SOURCE_ONLY_FAIL_CLOSED`

This contract closes the gap between acquisition evidence and the exact
third-party Unreal packages used by a Mission 1 candidate. It does not acquire,
download, import, promote, build, launch, package, or accept any asset.

## Pipeline position

Every third-party asset must pass these distinct gates:

1. Catalog research — nomination only.
2. Account acquisition and immutable license/receipt capture.
3. Quarantine intake.
4. Technical evaluation.
5. Separate quarantine import authorization.
6. Visual and performance acceptance.
7. Final-use receipt bound to exact `/Game/Skyguard/...` packages.
8. Separate release audit.

Passing an earlier stage never substitutes for a later stage. Folder presence,
catalog metadata, plugin enablement, quarantine acceptance, or an Unreal
reference alone does not prove license coverage or production acceptance.

## Template

Use:

`Docs/AAA_Review/M01_THIRD_PARTY_FINAL_USE_RECEIPT_TEMPLATE.json`

Copy it to a new immutable, candidate-specific namespace. Do not edit the
template in place.

The completed record must bind:

- candidate identifier and exact build/package artifact;
- provider, product or asset ID, name, creator, source URL, and version;
- exact license tier, acquisition record, and license snapshot;
- cooked-Windows redistribution coverage;
- source-file inventory;
- every final `/Game/Skyguard/...` package and matching project-file hash;
- Mission 1 map use and purpose;
- modifications and dependency closure;
- intake, technical, visual, and performance acceptance artifacts;
- release constraints and any required notice;
- all receipt-level completeness assertions.

Quarantine paths and `/Engine/...` content references are rejected.

## Verification

The untouched template must fail closed:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python .\Scripts\verify_m01_third_party_final_use_receipt.py
```

Expected:

- exit code `3`;
- `gate_status = FAIL_CLOSED`;
- `disposition = HOLD_NO_RUNTIME_PROMOTION`.

Verify a candidate-specific record with:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python .\Scripts\verify_m01_third_party_final_use_receipt.py `
  --record .\Saved\AssetProvenance\M01\<candidate>\final_use_receipt.json `
  --project-root D:\Skyguard52
```

A pass means only:

`READY_FOR_SEPARATE_RELEASE_AUDIT`

It is not release acceptance and does not authorize a build, Unreal execution,
integration, promotion, or packaging.

## Focused tests

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m unittest .\Scripts\test_m01_third_party_final_use_receipt.py
```

The tests cover a valid record, template-state failure, file-hash mismatch,
quarantine references, missing Mission 1 use, missing visual evidence, and
duplicate asset identifiers.

