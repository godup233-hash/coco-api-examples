# Using COCO API from an MCP Client

COCO API exposes model API protocols; it is not itself an MCP transport endpoint. To use it in an MCP-capable client, run an MCP server/bridge that supports an OpenAI-compatible upstream, then point that bridge at COCO API.

## Prerequisites

1. A COCO API key exported as `COCO_API_KEY`.
2. An exact live model ID exported as `COCO_MODEL`.
3. An MCP bridge you trust that accepts an OpenAI-compatible base URL, key, and model.
4. An MCP client that can start local stdio servers.

## Configuration Shape

The following is an **illustrative configuration**, not a directly runnable package reference. Replace the command and arguments with those required by your chosen bridge. Environment-variable interpolation syntax also varies by client.

```json
{
  "mcpServers": {
    "coco-api": {
      "command": "<path-to-your-mcp-bridge>",
      "args": [],
      "env": {
        "OPENAI_API_KEY": "${COCO_API_KEY}",
        "OPENAI_BASE_URL": "https://api.cocoapi.top/v1",
        "OPENAI_MODEL": "${COCO_MODEL}"
      }
    }
  }
}
```

Adjust variable names to the bridge's documentation. Some bridges use `OPENAI_API_BASE`, `BASE_URL`, or command-line flags instead of `OPENAI_BASE_URL`. If the bridge appends `/v1` automatically, configure `https://api.cocoapi.top` instead.

## Safe Setup

1. Verify the key and model independently with the [curl model-list and chat requests](../curl/README.md).
2. Install and audit the selected MCP bridge.
3. Put the JSON in the location documented by your MCP client.
4. Prefer the client's secret/environment support. Do not paste a real key into a configuration committed to Git.
5. Restart the client and run the smallest tool or prompt request first.

## Diagnostics

- **Bridge does not start:** run its configured `command` manually and inspect stderr.
- **401:** confirm the client passed `COCO_API_KEY` into the bridge process and that the bridge sends bearer authentication.
- **429:** lower the bridge's concurrency or request rate and retry later.
- **Timeout:** test `https://api.cocoapi.top/v1/models` from the same environment and check the bridge timeout.
- **Unsupported parameter/tool behavior:** simplify the request. Gateway routing does not guarantee every model or group supports every protocol parameter, and not every programming tool is one-click compatible.

Client schemas, bridge flags, and secret-substitution rules differ. Treat the JSON above as a shape to adapt, and follow the actual client and bridge documentation.
