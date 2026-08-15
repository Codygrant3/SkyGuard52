export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

export interface BridgeConfig {
  projectRoot: string;
  remoteControlBaseUrl: string;
  remoteTimeoutMs: number;
  mutationEnabled: boolean;
  mutationToken?: string;
  receiptRoot: string;
}

export interface ToolResult {
  [key: string]: JsonValue;
}

export interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, JsonValue>;
    required?: string[];
    additionalProperties: boolean;
  };
}

export interface HashRecord {
  path: string;
  bytes: number;
  sha256: string;
}
