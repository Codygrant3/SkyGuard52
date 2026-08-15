# Skyguard Unreal MCP

Local, read-only-first Model Context Protocol bridge for the canonical Unreal Engine 5.8 project at `D:\Skyguard52`.

It does **not** launch Unreal, save worlds, import assets, edit project content, run builds, or expose arbitrary Python/C++ execution. Remote Control calls are loopback-only and restricted to a fixed read-only function allowlist.

## Capabilities

- Canonical manifest health and production-state summaries.
- Loopback Unreal Remote Control health.
- Bounded asset existence/listing and loaded-level actor inspection.
- Bounded `/Game` or `/Engine` object/material property reads.
- Recent log and process inspection for shader/asset compilation signals.
- Non-executing automation, viewport capture, and Unreal Insights trace plans.
- Hash-bound in-memory evidence receipts.
- Optional atomic receipt publication with dual authorization.

## Build and test

```powershell
cd D:\Skyguard52\Tools\SkyguardUnrealMCP
npm install
npm test
```

The package has no runtime dependencies. TypeScript and Node type declarations are development-only.

## Run read-only

```powershell
$env:SKYGUARD_PROJECT_ROOT = 'D:\Skyguard52'
$env:SKYGUARD_UNREAL_REMOTE_URL = 'http://127.0.0.1:30010'
node D:\Skyguard52\Tools\SkyguardUnrealMCP\dist\src\server.js
```

Unreal Remote Control must already be enabled and listening on loopback. The bridge will never start Unreal itself.

Example Codex configuration:

```toml
[mcp_servers.skyguard_unreal]
command = "node"
args = ["D:\\Skyguard52\\Tools\\SkyguardUnrealMCP\\dist\\src\\server.js"]
env = { SKYGUARD_PROJECT_ROOT = "D:\\Skyguard52", SKYGUARD_UNREAL_REMOTE_URL = "http://127.0.0.1:30010" }
```

Registering it in a user configuration is intentionally a separate, explicit action. This package does not modify Codex, Unreal, project, firewall, or user settings.

## Receipt-write authorization

Receipt writes are disabled by default. They require all three conditions:

1. Start with `--enable-receipt-writes`.
2. Set a high-entropy `SKYGUARD_MCP_MUTATION_TOKEN` environment variable.
3. Supply the same token to `receipt_write_authorized`.

The tool can write only a new JSON file below `Saved\Reports\Toolchain\SkyguardUnrealMCP`; traversal and overwrite are rejected. No Unreal mutation tool exists in this version.

## Operational boundaries

- Respect the production manifest's one-heavy-process and zero-auto-retry rules.
- Generated launch plans are designs, not authorization to execute them.
- Remote Control remains an experimental/editor-facing Unreal capability; inspect the exact installed UE version before expanding the allowlist.
- Actor and object responses depend on the loaded editor map and enabled Editor Scripting/Remote Control plugins.
- Store no secrets in the repository or MCP configuration file.
