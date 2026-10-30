# Python Examples

These examples target Python 3.10+ and use the OpenAI Python SDK for OpenAI-compatible routes. The Anthropic Messages example uses only the Python standard library so the native request is visible end to end.

## Setup

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export COCO_API_KEY='YOUR_COCO_API_KEY'
export COCO_MODEL='YOUR_MODEL_ID'
```

Choose `COCO_MODEL` from the live model list:

```bash
python list_models.py
```

The scripts do not load `.env` files automatically. Export variables in the shell, use your shell's environment loader, or configure them in your process manager.

## Run

```bash
python quickstart.py
python streaming.py
python list_models.py
python claude_messages.py
python async_batch.py
```

| Script | Purpose |
|---|---|
| `quickstart.py` | Minimal OpenAI-compatible chat completion |
| `streaming.py` | Incremental SSE output |
| `list_models.py` | Model listing and group/owner metadata counts |
| `claude_messages.py` | Native `/v1/messages` request |
| `async_batch.py` | Concurrent calls with a semaphore and per-request error isolation |

## Errors

Each script reports actionable cases:

- **401:** verify `COCO_API_KEY`, its status, and the configured API address.
- **429:** reduce request frequency or batch concurrency, then retry later.
- **Timeout:** verify network reachability and retry the smallest request first.
- **Other API errors:** record the `x-oneapi-request-id` shown by the script when asking for support.

If a response's `model` differs from the requested name, record it for verification rather than treating it as an automatic failure; identifiers can be upstream mappings or aliases.
