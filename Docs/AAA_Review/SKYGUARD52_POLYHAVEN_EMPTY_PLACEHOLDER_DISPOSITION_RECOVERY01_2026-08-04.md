# Skyguard 52 — Empty Poly Haven Placeholder Disposition Recovery01

Classification: `PASSED_OFFLINE_EXCLUDED_FROM_CURRENT_CANDIDATE`

The empty families:

- `metal_walkway_01`
- `painted_metal_02`
- `ship_hull`

remain empty directories. They are not runtime assets and are explicitly
excluded by the frozen Mission 1 landscape review contract.

Recovery01 scanned 2,001 files across `Source`, `Config`, `Plugins`, and
`Content`, including 1,417 `.uasset` files. It found zero exact family markers.

## Original verifier failure

The first new verifier returned `FAILED_WITH_EVIDENCE` because it looked for
the exclusions at `source_controls.excluded`. The frozen contract stores them
at `provenance.excluded`.

That original verifier and its tests remain unchanged. Recovery01 uses a fresh
filename and changes only the contract lookup path. Its four tests pass and the
full-project verification exits `0`.

## Disposition

The directories were not deleted, populated, renamed, or promoted. Their
current-candidate disposition is:

`EXCLUDED_FROM_CURRENT_CANDIDATE_NOT_DELETED`

This removes the need to acquire replacement files for the current candidate,
but it does not prove final Shipping absence. The packaged dependency graph and
Asset Registry must reconfirm the exclusion before release. Any future proposal
to use one of these families requires a new source, license, file manifest,
import, visual, performance, and final-use acceptance chain.

