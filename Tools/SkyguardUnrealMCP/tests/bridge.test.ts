import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { assertWithinRoot, hashFile, sha256Json } from "../src/hash.js";
import { assertLoopbackUrl, assertMutationAuthorized } from "../src/policy.js";
import { buildReceipt } from "../src/receipts.js";
import { TOOL_DEFINITIONS } from "../src/tools.js";
import type { BridgeConfig } from "../src/types.js";

test("loopback policy rejects remote hosts", () => {
  assert.equal(assertLoopbackUrl("http://127.0.0.1:30010").hostname, "127.0.0.1");
  assert.throws(() => assertLoopbackUrl("https://127.0.0.1:30010"));
  assert.throws(() => assertLoopbackUrl("http://192.168.1.20:30010"));
});

test("governed path rejects traversal", () => {
  const root = mkdtempSync(join(tmpdir(), "sg52-root-"));
  assert.equal(assertWithinRoot(join(root, "Saved", "a.json"), root), join(root, "Saved", "a.json"));
  assert.throws(() => assertWithinRoot(join(root, "..", "escape.txt"), root));
});

test("hash-bound in-memory receipt is deterministic for evidence", async () => {
  const root = mkdtempSync(join(tmpdir(), "sg52-receipt-"));
  mkdirSync(join(root, "Saved"));
  const path = join(root, "Saved", "sample.txt");
  writeFileSync(path, "evidence\n", "utf8");
  const hash = await hashFile(path);
  assert.equal(hash.bytes, 9);
  assert.equal(hash.sha256.length, 64);
  const receipt = await buildReceipt("test", [path], root, { passed: true });
  assert.equal(typeof receipt.receiptSha256, "string");
  assert.equal(String(receipt.receiptSha256).length, 64);
  assert.equal(sha256Json({ b: 2, a: 1 }), sha256Json({ a: 1, b: 2 }));
});

test("mutation requires startup and per-call authorization", () => {
  const config: BridgeConfig = { projectRoot: "D:\\Skyguard52", remoteControlBaseUrl: "http://127.0.0.1:30010", remoteTimeoutMs: 1000, mutationEnabled: true, mutationToken: "1234567890abcdef", receiptRoot: "D:\\Skyguard52\\Saved\\Reports\\Toolchain" };
  assert.doesNotThrow(() => assertMutationAuthorized(config, "1234567890abcdef"));
  assert.throws(() => assertMutationAuthorized({ ...config, mutationEnabled: false }, "1234567890abcdef"));
  assert.throws(() => assertMutationAuthorized(config, "wrong-token-value"));
});

test("tool surface is unique and read-only-first", () => {
  const names = TOOL_DEFINITIONS.map((tool) => tool.name);
  assert.equal(new Set(names).size, names.length);
  assert.ok(names.includes("skyguard_health"));
  assert.ok(names.includes("unreal_shader_compilation_state"));
  assert.ok(names.includes("design_automation_test_launch"));
  assert.ok(names.includes("performance_collect_receipt"));
  assert.equal(names.filter((name) => name.includes("write")).length, 1);
});
