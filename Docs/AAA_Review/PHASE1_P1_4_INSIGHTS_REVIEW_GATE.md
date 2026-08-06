# Phase 1 P1.4 — Unreal Insights review/export gate

## Purpose

This gate converts the accepted Phase 1 `.utrace` into reproducible,
hash-bound Unreal Insights exports without launching a visible Unreal window or
changing system settings. It does **not** promote a readable trace into P1.4
acceptance.

The installed UE 5.8 source is the command contract:

- `ExportTimerStatisticsFromUtrace.cs` demonstrates `-Unattended -AutoQuit
  -NoUI -NullRHI` and `TimingInsights.ExportTimerStatistics`.
- `ExportCommandsTests.cpp` proves `ExportThreads`, `ExportTimers`,
  `ExportTimingEvents`, and response-file execution.

## Run

```powershell
Set-Location D:\Skyguard52
.\Scripts\run_skyguard_phase1_insights_review_gate.ps1
```

The supervisor creates an immutable attempt under
`Saved/Profiling/Phase1InsightsReview/`, binds the trace, performance report,
Unreal Insights executable, engine source contracts, and command file by
SHA-256, then launches only headless `UnrealInsights.exe`.

The independent verifier writes:

- attempt-local `review_report.json`;
- `Saved/Reports/PHASE1_INSIGHTS_REVIEW_LATEST.json`;
- threads, timers, aggregate timer statistics, and domain-filtered events.

`headless_export_gate=PASS` means the trace was analyzed, exports are parseable,
the bound inputs still match, AutoQuit completed, and no critical analysis
signature was found.

## Fail-closed P1.4 disposition

The accepted trace requested:

`cpu,gpu,frame,bookmark,loadtime,file,assetload`

It omitted `memory` and contains no explicit VRAM residency/budget telemetry.
Therefore the report must retain:

`p1_4_disposition=INSUFFICIENT_EVIDENCE`

Timer-name matches are triage. Aggregate startup loading, shader, PSO, or
Niagara time is not automatically a user-visible hitch and absence of a match
is not proof of absence.

## Exact remaining review

1. Open the hash-bound trace in Unreal Insights 5.8.
2. In Timing Insights, select the post-warmup combat interval.
3. Review the exported loading/streaming, shader/PSO, and Niagara candidates in
   timeline context.
4. Save dated screenshots and explicit pass/fail findings.
5. Capture a new input-driven trace with `memory` plus explicit GPU-memory/VRAM
   budget telemetry. The measured interval must include ADS+rifle, Igla launch,
   drone breakup, boss destruction, weather transition, and fast camera motion.

Until both the contextual review and the new memory/VRAM capture are accepted,
P1.4 remains insufficiently evidenced.
