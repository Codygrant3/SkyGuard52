# Recovery03 lifecycle decision

Gate: `P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03`

## Decision

Use a Recovery03-only Unreal Editor plugin whose editor module owns an `FTSTicker`
state machine. The module is inert unless all three frozen command-line values
match: contract ID, authorization token, and exact absent output namespace.
It must not use `-ExecutePythonScript`.

The ticker owns authorization, immutable-input checks, editor/world readiness,
two distinct stable shader-ready polls, 30 seconds of warmup, 30 seconds and at
least 900 measurement samples, eight viewport captures, transient material
restoration, terminal receipts, and the final explicit editor exit request.

## Evidence

The quarantined Recovery05 source demonstrates that a native Unreal tickable can
survive beyond its initiating stack and can write a receipt before
`FPlatformMisc::RequestExitWithStatus`. It is evidence only and remains
unchanged:

- `Saved/Quarantine/Phase3FailedCaptureSources/Recovery12Retirement/SkyguardM01GroupedTopologyRecovery05Capture.h`
- `Saved/Quarantine/Phase3FailedCaptureSources/Recovery12Retirement/SkyguardM01GroupedTopologyRecovery05Capture.cpp`

Recovery02 proves that `-ExecutePythonScript` is not a valid lifecycle owner for
deferred callbacks: the editor emitted `QUIT_EDITOR` before any governed proof
artifact was produced.

## Telemetry decision

Local UE 5.8 source proves:

- command-line INI overrides use
  `-ini:IniName:[Section]:Key=Value`;
- `UAnalyticsPrivacySettings` is `config=EditorSettings`;
- editor analytics initialization consults `bSendUsageData`;
- the plugin manager parses `-DisablePlugins=`.

The future launch therefore requires:

`-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False`

and:

`-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared`

Postflight still fails on any HTTP, EOS, analytics, telemetry, datarouter,
Fab, Bridge, source-control, login, update, DNS, socket, or network-attempt
evidence. Suppression is not inferred merely from blocked or failed requests.

## Blocking prerequisite

The Recovery03 plugin is new native code. This offline gate does not authorize a
native build, and the current editor module cannot contain code that has not
been compiled and rebound. Therefore the design cannot honestly be classified
as ready for a single Unreal execution. A separate one-shot native plugin build
and binary hash-freeze gate is required first.

Classification: `FAILED_WITH_EVIDENCE`

