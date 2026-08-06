Resume only the existing Unreal Engine/Blender AAA project at `D:\Skyguard52`.
Do not use the retired Three.js project, external models, or subagents.

Treat Recovery01 and Recovery02 as immutable and terminal. Treat the frozen
Recovery03 offline design as authority, but preserve its honest
`FAILED_WITH_EVIDENCE` classification: it is not yet authorized to launch
Unreal because its new editor plugin has not been built or rebound.

Authorize exactly one offline native plugin build/rebind gate for
`Plugins/SkyguardRecovery03`. Do not launch UnrealEditor, Blender, capture,
profiling, promotion, integration, or packaging.

Before the build, verify every Recovery03 freeze hash, confirm all governed
attempt/proof/launcher/preflight namespaces remain absent, confirm no heavy
process is active, and preserve all prior evidence. Build the plugin exactly
once with the installed UE 5.8 authority. Never retry automatically and never
reuse a failed build namespace.

If compilation fails, freeze stdout, stderr, command, PID, numeric exit code,
binary absence, source hashes, and process-tree evidence and classify
`FAILED_WITH_EVIDENCE`.

If compilation succeeds, run no Unreal proof. Verify the produced plugin
descriptor and binaries, freeze their byte counts and SHA-256 hashes, confirm
the plugin remains disabled by default and inert without the exact Recovery03
authorization triplet, run the lightweight exit-code and static lifecycle
tests, and create a new immutable build/readiness freeze.

Only if the compiled plugin and all offline checks pass may the result be
classified `PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY03_UNREAL_AUTHORIZATION`.
Then produce—but do not execute—the exact one-shot Recovery03 Unreal execution
prompt. Stop after the immutable native-build classification.
