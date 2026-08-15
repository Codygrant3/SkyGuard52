import { createHash } from "node:crypto";
import { createReadStream, statSync } from "node:fs";
import { resolve, relative, isAbsolute } from "node:path";
import type { HashRecord } from "./types.js";

export function assertWithinRoot(candidate: string, root: string): string {
  const absolute = resolve(candidate);
  const absoluteRoot = resolve(root);
  const rel = relative(absoluteRoot, absolute);
  if (rel === "" || (!rel.startsWith("..") && !isAbsolute(rel))) return absolute;
  throw new Error(`Path escapes governed root: ${candidate}`);
}

export async function hashFile(path: string): Promise<HashRecord> {
  const bytes = statSync(path).size;
  const hash = createHash("sha256");
  await new Promise<void>((resolvePromise, reject) => {
    const stream = createReadStream(path);
    stream.on("data", (chunk) => hash.update(chunk));
    stream.on("error", reject);
    stream.on("end", resolvePromise);
  });
  return { path, bytes, sha256: hash.digest("hex") };
}

export function sha256Json(value: unknown): string {
  return createHash("sha256").update(stableStringify(value)).digest("hex");
}

export function stableStringify(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(",")}]`;
  if (value && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, item]) => `${JSON.stringify(key)}:${stableStringify(item)}`);
    return `{${entries.join(",")}}`;
  }
  return JSON.stringify(value);
}
