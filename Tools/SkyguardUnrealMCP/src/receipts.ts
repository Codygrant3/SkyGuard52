import { mkdirSync, renameSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { assertWithinRoot, hashFile, sha256Json } from "./hash.js";
import type { BridgeConfig, JsonValue, ToolResult } from "./types.js";
import { assertMutationAuthorized } from "./policy.js";

export async function buildReceipt(kind: string, evidencePaths: string[], projectRoot: string, payload: JsonValue = null): Promise<ToolResult> {
  const evidence = [];
  for (const rawPath of evidencePaths) {
    const path = assertWithinRoot(rawPath, projectRoot);
    evidence.push(await hashFile(path));
  }
  const receipt = {
    schema: "skyguard.unreal-mcp-receipt.v1",
    kind,
    createdAtUtc: new Date().toISOString(),
    projectRoot,
    evidence,
    payload,
  };
  return { receipt: receipt as unknown as JsonValue, receiptSha256: sha256Json(receipt) };
}

export function writeReceipt(config: BridgeConfig, fileName: string, receipt: JsonValue, token: unknown): ToolResult {
  assertMutationAuthorized(config, token);
  if (!/^[A-Za-z0-9][A-Za-z0-9_.-]*\.json$/.test(fileName)) throw new Error("Invalid receipt filename");
  const destination = assertWithinRoot(join(config.receiptRoot, fileName), config.receiptRoot);
  mkdirSync(dirname(destination), { recursive: true });
  const temp = `${destination}.tmp-${process.pid}`;
  const serialized = `${JSON.stringify(receipt, null, 2)}\n`;
  writeFileSync(temp, serialized, { encoding: "utf8", flag: "wx" });
  renameSync(temp, destination);
  return { written: true, path: destination, bytes: Buffer.byteLength(serialized) };
}
