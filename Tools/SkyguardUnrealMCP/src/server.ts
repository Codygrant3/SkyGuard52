import { callTool, TOOL_DEFINITIONS } from "./tools.js";
import { defaultConfig } from "./policy.js";

interface JsonRpcRequest { jsonrpc: "2.0"; id?: string | number | null; method: string; params?: Record<string, unknown>; }

const config = defaultConfig();
let buffer = Buffer.alloc(0);

function send(payload: unknown): void {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
}

async function handle(request: JsonRpcRequest): Promise<void> {
  if (request.id === undefined) return;
  try {
    let result: unknown;
    switch (request.method) {
      case "initialize":
        result = { protocolVersion: String(request.params?.protocolVersion ?? "2025-06-18"), capabilities: { tools: { listChanged: false } }, serverInfo: { name: "skyguard-unreal-mcp", version: "0.1.0" }, instructions: "Read-only-first Unreal inspection bridge. Unreal mutations are not exposed; receipt writes require dual authorization." };
        break;
      case "ping": result = {}; break;
      case "tools/list": result = { tools: TOOL_DEFINITIONS }; break;
      case "tools/call": {
        const name = String(request.params?.name ?? "");
        const args = request.params?.arguments;
        try {
          const value = await callTool(config, name, args);
          result = { content: [{ type: "text", text: JSON.stringify(value, null, 2) }], structuredContent: value, isError: false };
        } catch (error) {
          result = { content: [{ type: "text", text: String(error) }], isError: true };
        }
        break;
      }
      default: throw Object.assign(new Error(`Method not found: ${request.method}`), { code: -32601 });
    }
    send({ jsonrpc: "2.0", id: request.id, result });
  } catch (error) {
    const code = typeof error === "object" && error && "code" in error ? Number((error as { code: unknown }).code) : -32603;
    send({ jsonrpc: "2.0", id: request.id, error: { code, message: String(error) } });
  }
}

function consume(): void {
  while (buffer.length > 0) {
    const headerEnd = buffer.indexOf("\r\n\r\n");
    if (headerEnd >= 0 && buffer.subarray(0, headerEnd).toString("utf8").toLowerCase().includes("content-length:")) {
      const header = buffer.subarray(0, headerEnd).toString("utf8");
      const match = /content-length:\s*(\d+)/i.exec(header);
      if (!match) throw new Error("Invalid Content-Length frame");
      const length = Number(match[1]);
      const bodyStart = headerEnd + 4;
      if (buffer.length < bodyStart + length) return;
      const body = buffer.subarray(bodyStart, bodyStart + length).toString("utf8");
      buffer = buffer.subarray(bodyStart + length);
      void handle(JSON.parse(body) as JsonRpcRequest);
      continue;
    }
    const newline = buffer.indexOf(10);
    if (newline < 0) return;
    const line = buffer.subarray(0, newline).toString("utf8").trim();
    buffer = buffer.subarray(newline + 1);
    if (line) void handle(JSON.parse(line) as JsonRpcRequest);
  }
}

process.stdin.on("data", (chunk: Buffer) => { buffer = Buffer.concat([buffer, chunk]); consume(); });
process.stdin.on("error", (error) => { process.stderr.write(`stdin error: ${String(error)}\n`); process.exitCode = 1; });
