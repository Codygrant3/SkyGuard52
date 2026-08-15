import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { basename, join, resolve } from "node:path";
import { execFileSync } from "node:child_process";
import { hashFile } from "./hash.js";
import { UnrealRemoteClient } from "./remote.js";
import { buildReceipt, writeReceipt } from "./receipts.js";
import type { BridgeConfig, JsonValue, ToolDefinition, ToolResult } from "./types.js";

const objectSchema = (properties: Record<string, JsonValue>, required: string[] = []): ToolDefinition["inputSchema"] => ({
  type: "object", properties, required, additionalProperties: false,
});

export const TOOL_DEFINITIONS: ToolDefinition[] = [
  { name: "skyguard_health", description: "Read-only bridge, project, policy and Unreal Remote Control health.", inputSchema: objectSchema({ probeUnreal: { type: "boolean", default: true } }) },
  { name: "skyguard_project_state", description: "Read the canonical production manifest and summarize asset states without mutation.", inputSchema: objectSchema({ includeAssets: { type: "boolean", default: false } }) },
  { name: "unreal_remote_info", description: "Read Unreal Remote Control API information from the loopback endpoint.", inputSchema: objectSchema({}) },
  { name: "unreal_asset_exists", description: "Check whether a /Game asset exists using the fixed read-only EditorAssetLibrary allowlist.", inputSchema: objectSchema({ assetPath: { type: "string", pattern: "^/Game/" } }, ["assetPath"]) },
  { name: "unreal_asset_list", description: "List assets under a /Game directory with a fixed read-only Unreal function.", inputSchema: objectSchema({ directoryPath: { type: "string", pattern: "^/Game(/|$)" }, recursive: { type: "boolean", default: true } }, ["directoryPath"]) },
  { name: "unreal_actor_list", description: "List actors in the currently loaded editor level through the read-only allowlist.", inputSchema: objectSchema({}) },
  { name: "unreal_object_read_properties", description: "Read selected properties from a /Game or /Engine object; no write access is exposed.", inputSchema: objectSchema({ objectPath: { type: "string" }, propertyNames: { type: "array", items: { type: "string" }, maxItems: 32 } }, ["objectPath", "propertyNames"]) },
  { name: "unreal_material_inspect", description: "Read bounded material properties from an existing Unreal object.", inputSchema: objectSchema({ objectPath: { type: "string" }, propertyNames: { type: "array", items: { type: "string" }, maxItems: 24 } }, ["objectPath"]) },
  { name: "unreal_shader_compilation_state", description: "Inspect process state and recent Unreal logs for shader/asset compilation signals.", inputSchema: objectSchema({ maxLogLines: { type: "integer", minimum: 20, maximum: 2000, default: 300 } }) },
  { name: "design_automation_test_launch", description: "Generate but do not execute a one-shot Unreal automation test launch plan.", inputSchema: objectSchema({ testFilter: { type: "string", minLength: 1 }, timeoutSeconds: { type: "integer", minimum: 30, maximum: 7200, default: 1200 } }, ["testFilter"]) },
  { name: "design_viewport_capture", description: "Generate but do not execute a governed camera/viewport capture contract.", inputSchema: objectSchema({ map: { type: "string", pattern: "^/Game/" }, cameras: { type: "array", items: { type: "string" }, minItems: 1, maxItems: 16 }, width: { type: "integer", minimum: 640, maximum: 7680 }, height: { type: "integer", minimum: 360, maximum: 4320 } }, ["map", "cameras", "width", "height"]) },
  { name: "design_trace_capture", description: "Generate but do not execute a bounded Unreal Insights trace/performance plan.", inputSchema: objectSchema({ durationSeconds: { type: "integer", minimum: 5, maximum: 1800, default: 60 }, channels: { type: "array", items: { type: "string" }, maxItems: 16 } }) },
  { name: "performance_collect_receipt", description: "Hash existing performance evidence and return an in-memory receipt; does not write files.", inputSchema: objectSchema({ kind: { type: "string" }, evidencePaths: { type: "array", items: { type: "string" }, maxItems: 128 }, payload: {} }, ["kind", "evidencePaths"]) },
  { name: "receipt_write_authorized", description: "Atomically write a receipt inside the governed report root. Disabled unless server startup and per-call token authorization both pass.", inputSchema: objectSchema({ fileName: { type: "string" }, receipt: {}, authorizationToken: { type: "string" } }, ["fileName", "receipt", "authorizationToken"]) },
];

function asRecord(args: unknown): Record<string, unknown> {
  if (!args || typeof args !== "object" || Array.isArray(args)) return {};
  return args as Record<string, unknown>;
}

function requiredString(args: Record<string, unknown>, key: string): string {
  const value = args[key];
  if (typeof value !== "string" || !value) throw new Error(`${key} must be a nonempty string`);
  return value;
}

function stringArray(args: Record<string, unknown>, key: string, maximum = 128): string[] {
  const value = args[key];
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string") || value.length > maximum) {
    throw new Error(`${key} must be a string array with at most ${maximum} items`);
  }
  return value as string[];
}

function latestLog(projectRoot: string): string | null {
  const logDir = join(projectRoot, "Saved", "Logs");
  if (!existsSync(logDir)) return null;
  const logs = readdirSync(logDir).filter((file) => file.endsWith(".log"))
    .map((file) => join(logDir, file)).sort((a, b) => statSync(b).mtimeMs - statSync(a).mtimeMs);
  return logs[0] ?? null;
}

function processSnapshot(): JsonValue {
  try {
    const script = "Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match 'Unreal|ShaderCompileWorker|AutomationTool|UnrealBuildTool|Blender' } | Select-Object Id,ProcessName,StartTime | ConvertTo-Json -Compress";
    const output = execFileSync("powershell.exe", ["-NoProfile", "-Command", script], { encoding: "utf8", timeout: 3000 }).trim();
    return output ? JSON.parse(output) as JsonValue : [];
  } catch (error) {
    return { unavailable: true, reason: String(error) };
  }
}

export async function callTool(config: BridgeConfig, name: string, rawArgs: unknown): Promise<ToolResult> {
  const args = asRecord(rawArgs);
  const remote = new UnrealRemoteClient(config);
  const manifestPath = join(config.projectRoot, "Production", "production_manifest.json");
  switch (name) {
    case "skyguard_health": {
      const manifest = existsSync(manifestPath) ? await hashFile(manifestPath) : null;
      let unreal: JsonValue = { probed: false };
      if (args.probeUnreal !== false) {
        try { unreal = { reachable: true, info: await remote.info() }; }
        catch (error) { unreal = { reachable: false, reason: String(error) }; }
      }
      return { ok: true, mode: config.mutationEnabled ? "receipt-write-gated" : "read-only", loopbackRemote: config.remoteControlBaseUrl, manifest: manifest as unknown as JsonValue, unreal, processSnapshot: processSnapshot() };
    }
    case "skyguard_project_state": {
      const manifest = JSON.parse(readFileSync(manifestPath, "utf8")) as Record<string, unknown>;
      const assets = Array.isArray(manifest.assets) ? manifest.assets as Array<Record<string, unknown>> : [];
      const states: Record<string, number> = {};
      for (const asset of assets) { const state = String(asset.status ?? "unknown"); states[state] = (states[state] ?? 0) + 1; }
      return { project: manifest.project as JsonValue, baseline: manifest.baseline as JsonValue, executionOrder: manifest.execution_order as JsonValue, assetStateCounts: states as JsonValue, assets: args.includeAssets === true ? assets as JsonValue : null, manifestAuthority: await hashFile(manifestPath) as unknown as JsonValue };
    }
    case "unreal_remote_info": return { info: await remote.info() };
    case "unreal_asset_exists": {
      const assetPath = requiredString(args, "assetPath");
      if (!assetPath.startsWith("/Game/")) throw new Error("assetPath must start with /Game/");
      return { result: await remote.callReadOnly("/Script/EditorScriptingUtilities.Default__EditorAssetLibrary", "DoesAssetExist", { AssetPath: assetPath }) };
    }
    case "unreal_asset_list": {
      const directoryPath = requiredString(args, "directoryPath");
      if (directoryPath !== "/Game" && !directoryPath.startsWith("/Game/")) throw new Error("directoryPath must be /Game or a child");
      return { result: await remote.callReadOnly("/Script/EditorScriptingUtilities.Default__EditorAssetLibrary", "ListAssets", { DirectoryPath: directoryPath, bRecursive: args.recursive !== false, bIncludeFolder: false }) };
    }
    case "unreal_actor_list": return { result: await remote.callReadOnly("/Script/EditorScriptingUtilities.Default__EditorLevelLibrary", "GetAllLevelActors", {}) };
    case "unreal_object_read_properties": {
      const objectPath = requiredString(args, "objectPath");
      const names = stringArray(args, "propertyNames", 32);
      const properties: Record<string, JsonValue> = {};
      for (const property of names) properties[property] = await remote.readProperty(objectPath, property);
      return { objectPath, properties };
    }
    case "unreal_material_inspect": {
      const objectPath = requiredString(args, "objectPath");
      const names = args.propertyNames ? stringArray(args, "propertyNames", 24) : ["BlendMode", "ShadingModel", "TwoSided", "OpacityMaskClipValue", "MaterialDomain"];
      const properties: Record<string, JsonValue> = {};
      for (const property of names) properties[property] = await remote.readProperty(objectPath, property);
      return { objectPath, properties };
    }
    case "unreal_shader_compilation_state": {
      const path = latestLog(config.projectRoot);
      if (!path) return { logAvailable: false, processSnapshot: processSnapshot() };
      const maxLines = Math.max(20, Math.min(2000, Number(args.maxLogLines ?? 300)));
      const lines = readFileSync(path, "utf8").split(/\r?\n/).slice(-maxLines);
      const signals = lines.filter((line) => /ShaderCompile|shaders? left|asset compil|DerivedData|PSO/i.test(line)).slice(-100);
      return { logAvailable: true, log: path, logAuthority: await hashFile(path) as unknown as JsonValue, signalCount: signals.length, signals, processSnapshot: processSnapshot() };
    }
    case "design_automation_test_launch": {
      const filter = requiredString(args, "testFilter");
      if (!/^[A-Za-z0-9_. *-]+$/.test(filter)) throw new Error("Unsafe automation test filter");
      const executable = join("D:\\UE_5.8", "Engine", "Binaries", "Win64", "UnrealEditor-Cmd.exe");
      return { executed: false, plan: { executable, arguments: [join(config.projectRoot, "Skyguard52.uproject"), "-unattended", "-nop4", "-nosplash", `-ExecCmds=Automation RunTests ${filter};Quit`, "-ReportOutputPath=<fresh-governed-attempt>"], timeoutSeconds: Number(args.timeoutSeconds ?? 1200), oneHeavyProcess: true, automaticRetries: 0 } as unknown as JsonValue };
    }
    case "design_viewport_capture": return { executed: false, contract: { map: requiredString(args, "map"), cameras: stringArray(args, "cameras", 16), width: Number(args.width), height: Number(args.height), colorFormat: "PNG", worldSaveAllowed: false, diskAssetMutationAllowed: false, freshNamespaceRequired: true, directVisualReviewRequired: true } as unknown as JsonValue };
    case "design_trace_capture": {
      const allowed = new Set(["cpu", "gpu", "frame", "bookmark", "loadtime", "file", "assetloadtime", "memory", "task"]);
      const channels = args.channels ? stringArray(args, "channels", 16) : ["cpu", "gpu", "frame", "bookmark", "loadtime"];
      if (channels.some((channel) => !allowed.has(channel))) throw new Error("Unsupported trace channel");
      return { executed: false, plan: { channels, durationSeconds: Number(args.durationSeconds ?? 60), traceArgument: `-trace=${channels.join(",")}`, output: "<fresh-governed-attempt>/trace.utrace", requiredEvidence: ["trace.utrace", "frame_samples.csv", "process_snapshot.json", "terminal_receipt.json"] } as unknown as JsonValue };
    }
    case "performance_collect_receipt": return buildReceipt(requiredString(args, "kind"), stringArray(args, "evidencePaths"), config.projectRoot, (args.payload ?? null) as JsonValue);
    case "receipt_write_authorized": return writeReceipt(config, requiredString(args, "fileName"), (args.receipt ?? null) as JsonValue, args.authorizationToken);
    default: throw new Error(`Unknown tool: ${name}`);
  }
}
