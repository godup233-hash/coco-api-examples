# coco-api-examples

Runnable examples for calling [COCO API](https://cocoapi.top) — a multi-model API gateway exposing an OpenAI-compatible `/v1` surface plus a native Anthropic `/v1/messages` endpoint. Python, Node (zero-dependency), and curl.

> **Disclosure:** this repository is maintained by the COCO API team as public developer documentation for the gateway at `https://cocoapi.top`. It is not an official SDK, and it is not affiliated with OpenAI, Anthropic, Google, or any upstream model provider. Treat everything below as reference code you read and adapt, not as a package you ship.

> **Snapshot notice:** model counts, groups, and prices referenced here were taken from the COCO API model hub on **2026-10-29**. Gateways change inventory frequently. Always confirm current IDs and pricing at https://cocoapi.top before you budget against them.

## Features

- **One key, one base URL.** Swap models by changing the `model` field, not the endpoint or SDK.
- **OpenAI-compatible.** Base URL `https://api.cocoapi.top/v1` works with the official `openai` Python/Node SDKs via `base_url`.
- **Native Anthropic Messages.** `/v1/messages` accepts `x-api-key` / `Authorization: Bearer` with `anthropic-version`.
- **SSE streaming.** Standard `stream: true` on Chat Completions; `stream: true` on Messages for Anthropic-style deltas.
- **Traceable errors.** Every response carries an `x-oneapi-request-id` header — quote it in support tickets.
- **CNY billing**, quoted per 1M tokens on the model hub.

## Quick Start

**1. Get a key.** Register at [cocoapi.top](https://cocoapi.top) and create an API key in the dashboard.

**2. Export your credentials.**

```bash
git clone <this-repo> && cd coco-api-examples
cp .env.example .env      # then fill in your key
export COCO_API_KEY='YOUR_COCO_API_KEY'
export COCO_MODEL='claude-fable-5.1'
```

**3. Make the first call.**

```bash
curl https://api.cocoapi.top/v1/chat/completions \
  -H "Authorization: Bearer ${COCO_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model": "'"${COCO_MODEL}"'", "messages": [{"role": "user", "content": "Say hi in one sentence."}]}'
```

Every example reads the key from `COCO_API_KEY`. No example contains a hardcoded credential.

## Examples

| Path | Language | What it shows |
|---|---|---|
| [`python/quickstart.py`](python/quickstart.py) | Python | Minimal chat call with classified error handling (401 / 429 / timeout) |
| [`python/streaming.py`](python/streaming.py) | Python | SSE streaming with incremental deltas |
| [`python/list_models.py`](python/list_models.py) | Python | `GET /v1/models`, grouped counts, family detection |
| [`python/claude_messages.py`](python/claude_messages.py) | Python | Native Anthropic Messages protocol, no OpenAI shim |
| [`python/async_batch.py`](python/async_batch.py) | Python | asyncio fan-out with a concurrency semaphore and per-task isolation |
| [`node/quickstart.mjs`](node/quickstart.mjs) | Node 20+ | Minimal chat call on built-in `fetch`, zero deps |
| [`node/streaming.mjs`](node/streaming.mjs) | Node 20+ | Hand-rolled SSE parser over `ReadableStream` |
| [`node/list_models.mjs`](node/list_models.mjs) | Node 20+ | Model listing and grouping |
| [`node/claude_messages.mjs`](node/claude_messages.mjs) | Node 20+ | Anthropic Messages call with SSE support |
| [`curl/`](curl/README.md) | Shell | Copy-paste curl recipes incl. troubleshooting |
| [`mcp/`](mcp/README.md) | JSON | Wiring the gateway into MCP / OpenAI-compatible clients |

See [`python/README.md`](python/README.md) and [`node/README.md`](node/README.md) for per-language setup.

## Endpoints

| Purpose | URL |
|---|---|
| Model list | `https://api.cocoapi.top/v1/models` |
| Chat Completions | `https://api.cocoapi.top/v1/chat/completions` |
| Anthropic Messages | `https://api.cocoapi.top/v1/messages` |
| Root / health | `https://api.cocoapi.top` |

**Base URL rule:** if your client appends `/v1` itself (most OpenAI SDK setups do), set `https://api.cocoapi.top`. Otherwise set `https://api.cocoapi.top/v1`. The `/v1` prefix appearing twice is the single most common mistake.

## Models

Counts below are the **2026-10-29 snapshot: 144 enabled models**. Model naming on a gateway may reflect upstream aliases — do not assume an ID maps to a specific vendor release, and always verify behaviour against the model hub.

| Family | Models (snapshot) | Example IDs |
|---|---|---|
| Claude | 27 | `claude-fable-5`, `claude-fable-5.1`, `claude-haiku-4-5-20251001`, `claude-haiku-5-5`, `claude-3-5-sonnet-20240620`, `claude-opus-4-1-20250805` |
| Gemini | 26 | see model hub |
| Domestic (CN) models | 31 | see model hub |
| GPT / Codex | 9 | see model hub |
| Grok | 4 | see model hub |
| Image | 13 | see model hub |
| Video | 4 | see model hub |
| Voice | 14 | see model hub |
| Other | 16 | `agnes-3.0-flash` |

Protocol coverage (snapshot): Chat Completions 144 · Gemini native 123 · Responses 116 · Anthropic Messages 116 · Image 11 · Embeddings 3.

## Notes

**Pricing.** Billed in CNY per 1M tokens. Each request bills across four components — input, cache creation, cache read, and output — and context-tiered pricing may apply. Multiplier groups (relative spend against a channel baseline) are published on the model hub; some groups are marked `x0`, meaning no charge at the time of the snapshot. Sample IDs from 2026-10-29, for reference only:

| Model ID | Input | Output |
|---|---|---|
| `claude-haiku-4-5-20251001` | <¥0.01 / 1M | <¥0.01 / 1M |
| `claude-fable-5.1` | ¥0.07 / 1M | ¥0.35 / 1M |
| `claude-haiku-5-5` | ¥0.20 / 1M | ¥1.00 / 1M |
| `claude-3-5-sonnet-20240620` | ¥1.72 / 1M | ¥8.58 / 1M |
| `claude-opus-4-1-20250805` | ¥8.58 / 1M | ¥42.90 / 1M |
| `agnes-3.0-flash` | ¥0.08 / 1M | ¥0.08 / 1M |

For anything not listed above, check the live price on the model hub — we would rather leave a blank than publish a number we cannot stand behind.

**Capability boundaries.** Image, video, voice, and Responses endpoints exist on the gateway, but those capabilities are not part of every model's verified behaviour and should not be assumed universally available. A model appearing under a protocol category does not imply support for that protocol's full parameter surface.

**Troubleshooting order.** address → credential → model → network → parameters.

- `401` means authentication failed, not that generation failed. Check the header name and whether your key's group allows the model.
- `429` means rate limiting. Back off and retry with jitter.
- Capture `x-oneapi-request-id` from the response headers; quote it when opening a support ticket.
- If the `model` field in the response differs from what you requested, note it and verify on the dashboard rather than assuming failure.
- Narrow any bug to the smallest request: same key, same model, same protocol.

## License

MIT. See [LICENSE](LICENSE). Trademarks and model names belong to their respective owners.
