import { isIP } from "node:net";
import { resolve } from "node:path";
import type { BridgeConfig } from "./types.js";

const ALLOWED_REMOTE_FUNCTIONS = new Map<string, Set<string>>([
  ["/Script/EditorScriptingUtilities.Default__EditorAssetLibrary", new Set([
    "DoesAssetExist",
    "DoesDirectoryExist",
    "ListAssets",
    "FindAssetData",
    "GetPathNameForLoadedAsset",
    "GetMetadataTag",
  ])],
  ["/Script/EditorScriptingUtilities.Default__EditorLevelLibrary", new Set([
    "GetAllLevelActors",
    "GetEditorWorld",
  ])],
]);

export function assertLoopbackUrl(raw: string): URL {
  const url = new URL(raw);
  if (url.protocol !== "http:") throw new Error("Remote Control must use loopback HTTP");
  const host = url.hostname.toLowerCase();
  const allowed = host === "localhost" || host === "127.0.0.1" || host === "::1";
  if (!allowed || (isIP(host) === 0 && host !== "localhost")) {
    throw new Error(`Non-loopback Remote Control host rejected: ${host}`);
  }
  return url;
}

export function assertReadOnlyFunction(objectPath: string, functionName: string): void {
  const functions = ALLOWED_REMOTE_FUNCTIONS.get(objectPath);
  if (!functions?.has(functionName)) {
    throw new Error(`Remote function is not on the read-only allowlist: ${objectPath}.${functionName}`);
  }
}

export function assertMutationAuthorized(config: BridgeConfig, token: unknown): void {
  if (!config.mutationEnabled) throw new Error("Mutation tools are disabled at server startup");
  if (!config.mutationToken) throw new Error("Server mutation token is not configured");
  if (typeof token !== "string" || token.length < 16 || token !== config.mutationToken) {
    throw new Error("Explicit mutation authorization token rejected");
  }
}

export function defaultConfig(): BridgeConfig {
  const projectRoot = resolve(process.env.SKYGUARD_PROJECT_ROOT ?? "D:\\Skyguard52");
  return {
    projectRoot,
    remoteControlBaseUrl: process.env.SKYGUARD_UNREAL_REMOTE_URL ?? "http://127.0.0.1:30010",
    remoteTimeoutMs: Number.parseInt(process.env.SKYGUARD_UNREAL_TIMEOUT_MS ?? "3000", 10),
    mutationEnabled: process.argv.includes("--enable-receipt-writes"),
    mutationToken: process.env.SKYGUARD_MCP_MUTATION_TOKEN,
    receiptRoot: resolve(projectRoot, "Saved", "Reports", "Toolchain", "SkyguardUnrealMCP"),
  };
}
