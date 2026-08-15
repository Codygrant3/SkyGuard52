import { assertLoopbackUrl, assertReadOnlyFunction } from "./policy.js";
import type { BridgeConfig, JsonValue } from "./types.js";

export class UnrealRemoteClient {
  private readonly base: URL;

  constructor(private readonly config: BridgeConfig) {
    this.base = assertLoopbackUrl(config.remoteControlBaseUrl);
  }

  async info(): Promise<JsonValue> {
    return this.request("GET", "/remote/info");
  }

  async callReadOnly(objectPath: string, functionName: string, parameters: Record<string, JsonValue>): Promise<JsonValue> {
    assertReadOnlyFunction(objectPath, functionName);
    return this.request("PUT", "/remote/object/call", {
      objectPath,
      functionName,
      parameters,
      generateTransaction: false,
    });
  }

  async readProperty(objectPath: string, propertyName: string): Promise<JsonValue> {
    if (!objectPath.startsWith("/Game/") && !objectPath.startsWith("/Engine/")) {
      throw new Error("Property reads are restricted to /Game and /Engine objects");
    }
    if (!/^[A-Za-z_][A-Za-z0-9_.]*$/.test(propertyName)) throw new Error("Invalid property name");
    return this.request("PUT", "/remote/object/property", {
      objectPath,
      propertyName,
      access: "READ_ACCESS",
    });
  }

  private async request(method: "GET" | "PUT", path: string, body?: Record<string, JsonValue>): Promise<JsonValue> {
    const url = new URL(path, this.base);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.config.remoteTimeoutMs);
    try {
      const response = await fetch(url, {
        method,
        headers: body ? { "content-type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });
      const text = await response.text();
      let payload: JsonValue = text;
      try { payload = text ? JSON.parse(text) as JsonValue : null; } catch { /* retain text */ }
      if (!response.ok) throw new Error(`Unreal Remote Control ${response.status}: ${text.slice(0, 1000)}`);
      return payload;
    } finally {
      clearTimeout(timer);
    }
  }
}
