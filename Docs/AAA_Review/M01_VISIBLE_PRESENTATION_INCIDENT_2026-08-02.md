# M01 Visible Presentation Incident — 2026-08-02

## Status

**Blocked before the input-combat performance gate.** The packaged runtime can
load M01 and complete the same timed smoke path when rendered offscreen, but a
visible swap chain repeatedly stops making forward progress. The evidence
supports a **scene-independent swap-chain/driver presentation deadlock** on this
machine. It does not support attributing the incident to M01 content, the
possession change, resolution, window mode, a specific Unreal RHI, or a single
high-end rendering feature.

## Exact package lineage

### Accepted baseline

The accepted release baseline remains:

- Attempt:
  `D:\Skyguard52\Saved\Releases\Phase8\attempt_20260802T092516016Z`
- Gate:
  `gate_report.json` reports `PASS` and `EXECUTION_COMPLETE`; all fourteen
  release checks are true.
- Development launcher SHA-256:
  `a6cf9ae22fe1c065d9f1daf4d6cd7aa2b1c1299e200f7e7cefea6dd66413c059`
- Development runtime SHA-256:
  `5fb0f2f0ee2299174949a34fffd0852a357e7311a5dacc8e7aeb072b2ecb29cf`
- Shipping launcher SHA-256:
  `449927bc515e6b096f6840d0b9720e145b715a311aa03f6b66e295c85e0b46f7`
- Cooked registry SHA-256, both configurations:
  `765cfcc6c144f42d8aa443bf561a6ec3993431cb12151226b20d9c7f78e58145`

Evidence:
`D:\Skyguard52\Saved\Releases\Phase8\attempt_20260802T092516016Z\run_manifest.json`
and
`D:\Skyguard52\Saved\Releases\Phase8\attempt_20260802T092516016Z\gate_report.json`.

### Fresh possession package

The possession correction was built successfully and both focused M01
automation tests passed:

- Build:
  `D:\Skyguard52\Saved\BuildAttempts\M01_POSSESSION_FIX\attempt_20260802T104109221Z`
- Tests:
  `BriefingGateAndGovernedContract` and
  `PlayableRuntimeCompositionAndProgression`, 2/2 successful, 0 warnings,
  0 failures.
- Test report:
  `D:\Skyguard52\Saved\BuildAttempts\M01_POSSESSION_AUTOMATION\attempt_20260802T104221542Z\report\index.json`

The fresh Development package is:

- Attempt:
  `D:\Skyguard52\Saved\Releases\Phase8\attempt_20260802T104313425Z`
- Development launcher SHA-256:
  `a6cf9ae22fe1c065d9f1daf4d6cd7aa2b1c1299e200f7e7cefea6dd66413c059`
- Development runtime SHA-256:
  `41a1aaf42e9c328eef8d7abea276010d1ea0aef4d270082f2e3b650f7a2f394e`
- Cooked registry SHA-256:
  `14b6c27ab9a5c7869cfc07d863eed67b391a163e03c0bff9c32a63492c79e3fd`
- Its two-phase unattended runtime validation passed with clean exit codes and
  no critical signatures:
  `D:\Skyguard52\Saved\Releases\Phase8\attempt_20260802T104313425Z\artifacts\runtime_validation_20260802T104440118Z\runtime_validation_verification.json`.

This attempt is a valid fresh Development possession candidate, not a new
accepted release baseline. Its overall release gate is `FAIL` because the
targeted run did not produce Shipping, ten-mission soak, or Shipping startup
smoke evidence.

## Isolation evidence

| Attempt | Isolation | Receipt/result |
|---|---|---|
| `M01_VISIBLE_RENDER_ISOLATION\attempt_20260802T103322973Z` | M01, visible, 1920×1080, D3D12/SM6 | Reached `MAP_READY`; visible run then produced repeated 5-second 3D/compute GPU timeouts and did not complete. |
| `M01_RENDER_OFFSCREEN_ISOLATION\attempt_20260802T103505707Z` | M01, `-RenderOffscreen`, 1920×1080, D3D12/SM6 | Receipt reached `COMPLETE`; engine requested exit and shut down normally. |
| `M01_VISIBLE_720P_ISOLATION\attempt_20260802T103551418Z` | M01, visible window, 1280×720, D3D12/SM6 | `MAP_READY`, followed by repeated 3D/compute GPU timeouts; no completion. |
| `M01_FULLSCREEN_D3D12_ISOLATION\attempt_20260802T103708003Z` | M01, fullscreen 1280×720, D3D12/SM6 | `MAP_READY`, followed by 3D/compute GPU timeouts; no completion. |
| `M01_VISIBLE_D3D11_ISOLATION\attempt_20260802T103808489Z` | M01, visible window, D3D11/SM5 | Reached `MAP_READY` but did not reach `COMPLETE`; changing RHI did not restore visible forward progress. |
| `M01_VISIBLE_POST_POSSESSION\attempt_20260802T104529005Z` | Fresh possession package, M01 visible, D3D12 | `MAP_READY`, followed by 3D/compute GPU timeouts; the possession change did not cause or cure the incident. |
| `M01_VISIBLE_MIN_RENDERER\attempt_20260802T104634965Z` | M01 visible with Nanite, Lumen diffuse/reflections, VSM, volumetric clouds, and HZB disabled | `MAP_READY`, followed by 3D/compute GPU timeouts; broad scene-feature reduction did not cure it. |
| `ENTRY_VISIBLE_D3D12_ISOLATION\attempt_20260802T104738127Z` | Empty Engine Entry map, visible, D3D12 | `MAP_READY`, followed by 3D/compute GPU timeouts; reproduces without M01 scene content. |
| `ENTRY_VISIBLE_D3D11_ISOLATION\attempt_20260802T104815835Z` | Empty Engine Entry map, visible, D3D11 | `MAP_READY` but no `COMPLETE`; reproduces across RHIs. |
| `ENTRY_VISIBLE_VSYNC60_ISOLATION\attempt_20260802T105050130Z` | Empty Entry map, D3D12, VSync on and 60 FPS cap | `MAP_READY`, followed by 3D/compute GPU timeouts. |
| `ENTRY_VISIBLE_SINGLE_RHI_ISOLATION\attempt_20260802T105410092Z` | Empty Entry map, D3D12, RHI thread and async compute disabled | `MAP_READY`, followed by 3D/compute GPU timeouts. |

The receipt files and stdout logs are retained beneath each listed attempt
directory. `MAP_READY` proves the runtime and requested map initialized; it is
not evidence that the timed visible smoke completed.

## Conclusion and scope

The decisive comparison is visible versus offscreen:

1. The offscreen D3D12 M01 run reached `COMPLETE` and shut down normally.
2. Visible runs stalled at 720p and 1080p, windowed and fullscreen.
3. The failure survived D3D12-to-D3D11, major renderer-feature removal, VSync
   and frame limiting, and single-RHI/no-async-compute isolation.
4. The empty Engine Entry map reproduced the visible stall.
5. The fresh possession package reproduced the same behavior.

Therefore the bounded working diagnosis is a **scene-independent
swap-chain/driver presentation deadlock**. This is a diagnosis of the current
evidence, not proof of a specific NVIDIA component defect.

## NVIDIA observation and restoration

`nvspcap64.dll` was observed injected/loaded during the diagnostic session.
That is recorded as correlation only. **No causal claim is made against
nvspcap, ShadowPlay, or the NVIDIA overlay.**

The temporary ShadowPlay registry experiment did not produce a completed
visible smoke receipt. The original ShadowPlay values were restored afterward;
the current restored values include:

- `HKCU\Software\NVIDIA Corporation\Global\ShadowPlay\NVSPCAPS\IsShadowPlayEnabled`
  = `01000000`
- `HKCU\Software\NVIDIA Corporation\Global\ShadowPlay\NVSPCAPS\IsShadowPlayEnabledUser`
  = `01000000`

The incomplete receipts from the bounded experiment remain at:

- `D:\Skyguard52\Saved\BuildAttempts\ENTRY_SHADOWPLAY_DISABLED\attempt_20260802T105257907Z`
- `D:\Skyguard52\Saved\BuildAttempts\ENTRY_NO_OVERLAY_RACE_TEST\attempt_20260802T105459772Z`

Neither attempt establishes overlay causality.

## Required next action

Do **not** start the M01 input-combat performance gate yet. It requires a
stable visible presentation path.

The next diagnostic must be user-side and one variable at a time:

1. Disable the NVIDIA in-game overlay/Instant Replay from the NVIDIA
   application UI, then reboot or otherwise confirm the overlay capture module
   is not loaded into the game process.
2. Re-run the bounded visible Engine Entry smoke first, followed by the bounded
   visible M01 smoke only if Entry reaches `COMPLETE`.
3. If the stall remains, perform a controlled NVIDIA driver A/B test (current
   driver versus a known-stable clean-installed driver), preserving the same
   package, map, resolution, command line, and receipt timeout.
4. Proceed to the input-combat performance gate only after a visible Entry and
   visible M01 run both produce `COMPLETE` receipts without GPU-timeout
   signatures.

## Post-network-approval retest

After the user approved the Skyguard network-access prompt, the repaired
Development package was tested again with the empty Engine Entry map:

- Package:
  `D:\Skyguard52\Saved\Releases\Phase8\attempt_20260802T110201576Z`
- Attempt:
  `D:\Skyguard52\Saved\BuildAttempts\ENTRY_VISIBLE_POST_NETWORK_APPROVAL\attempt_20260802T110528214Z`
- Window:
  1280 x 720, windowed, D3D12/SM6, no VSync
- Intended startup-smoke duration:
  10 seconds
- Supervisor limit:
  35 seconds
- Result:
  the process did not exit within the supervisor limit, the receipt remained at
  `MAP_READY`, and the log contained two GPU-timeout signatures.

This confirms that firewall approval did not resolve the visible presentation
deadlock. M01 was intentionally not launched because the scene-independent
Entry prerequisite did not reach `COMPLETE`.

The active firewall policy was also inspected for the exact repaired packaged
runtime. Two enabled inbound rules for that executable still reported `Block`
(TCP and UDP, Private and Public profiles). An attempted exact-rule correction
to `Allow` was rejected by Windows with `Access is denied`; no firewall rule
was changed by the automation. This policy mismatch should be corrected from an
elevated Windows Firewall UI or administrator PowerShell session, but it is
independent of the renderer diagnosis: the empty offline Entry map still
reproduced the visible GPU stall.
