# M08-M10 Playable Map Promotion

Status: `SOURCE_ONLY_DRY_RUN_DEFAULT`

This tool promotes Missions 8-10 from their assembly maps to their separate
playable-integration candidates in exactly two governed files:

- `Config/DefaultGame.ini`
- `Docs/AAA_Review/PHASE8_MISSION_SOAK_MATRIX.json`

It does not run Unreal, UBT or UAT. It does not modify either file unless the
operator explicitly supplies `--apply`.

## Required evidence

For each of M08, M09 and M10 the tool requires:

1. `Saved/Reports/M0X_PLAYABLE_INTEGRATION_GATE_LATEST.json`;
2. receipt `gate: PASS`;
3. passing persistence audit and non-failing automation evidence;
4. a parseable attempt timestamp no older than 72 hours by default;
5. an existing immutable attempt directory;
6. `Saved/Reports/M0X_PLAYABLE_INTEGRATION_BUILD.json` with `gate: PASS`;
7. the exact expected `target_map`;
8. an existing playable `.umap` whose SHA-256 matches the build report;
9. a receipt newer than both the `.umap` and build report.

The expected targets are:

- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M08_RescueCover_Playable_v1`
- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M09_SaturationAttack_Playable_v1`
- `/Game/Skyguard/Maps/Campaign_v1/Lvl_M10_EvacuationFinale_Playable_v1`

Missing, failing, stale, mismatched or unhashed evidence fails closed.

## Dry run

```powershell
python D:\Skyguard52\Scripts\promote_m08_m10_playable.py
```

Dry run prints:

- every receipt/map validation result;
- the exact `MapsToCook` substitutions;
- the exact soak-matrix map and status substitutions;
- unified diffs for both files;
- the resulting ordered ten-map list;
- all blockers.

If receipts or maps do not yet exist, exit code `3` and
`gate: FAIL_CLOSED` are expected. No file is changed.

The stale threshold can be tightened:

```powershell
python D:\Skyguard52\Scripts\promote_m08_m10_playable.py `
  --max-receipt-age-hours 24
```

## Source and mutation tests

```powershell
python -m unittest `
  D:\Skyguard52\Scripts\tests\test_promote_m08_m10_playable.py

python -m py_compile `
  D:\Skyguard52\Scripts\promote_m08_m10_playable.py `
  D:\Skyguard52\Scripts\tests\test_promote_m08_m10_playable.py
```

The tests use temporary projects. They prove dry-run immutability, exact
ordering, stale/failing/missing rejection, expected-map enforcement,
timestamped backups, verifier invocation and two-file rollback.

## Explicit apply

Only after reviewing a passing dry run:

```powershell
python D:\Skyguard52\Scripts\promote_m08_m10_playable.py --apply
```

Apply performs this bounded transaction:

1. Re-runs the fail-closed plan.
2. Creates timestamped backups beneath
   `Saved/Backups/M08_M10_Playable_Promotion/`.
3. Records original paths and SHA-256 values in `manifest.json`.
4. Atomically replaces each governed file using same-directory temporary files
   and `os.replace`.
5. Runs the existing
   `Scripts/verify_skyguard_phase8_cook_contract.py`.
6. Requires its JSON report to say `gate: PASS`.
7. Restores both backups atomically if writing or verification fails.

The resulting configuration must still contain ten unique maps in exact
M01-M10 order. Apply does not cook, package, launch an editor, alter map
assets, or claim runtime acceptance.
