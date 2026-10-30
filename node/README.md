# Node.js Examples

These examples require Node.js 20+ and use only built-in `fetch`, `AbortSignal`, and Web Streams APIs. There are no runtime dependencies to install.

## Setup

```bash
cd node
export COCO_API_KEY='YOUR_COCO_API_KEY'
export COCO_MODEL='YOUR_MODEL_ID'
```

Select an exact `COCO_MODEL` value from the current model list:

```bash
node list_models.mjs
```

The scripts do not load `.env` automatically. Export the variables or supply them through your shell, container, or process manager.

## Run

```bash
node quickstart.mjs
node streaming.mjs
node list_models.mjs
node claude_messages.mjs
```

The equivalent npm scripts are `npm run quickstart`, `npm run streaming`, `npm run models`, and `npm run messages`.

| Script | Purpose |
|---|---|
| `quickstart.mjs` | Minimal OpenAI-compatible chat completion |
| `streaming.mjs` | Line-safe SSE parsing and incremental output |
| `list_models.mjs` | Model listing and group/owner metadata counts |
| `claude_messages.mjs` | Native `/v1/messages` request |

## Errors

- **401:** verify `COCO_API_KEY`, its status, and the API address.
- **429:** lower request frequency and retry later.
- **Timeout:** the examples abort after 30 seconds; verify network reachability and retry a minimal request.
- **Other API errors:** save the displayed `x-oneapi-request-id` when requesting support.

Model identifiers can be upstream mappings or aliases. A response model name that differs from the request should be recorded and checked, not automatically treated as a fault.
