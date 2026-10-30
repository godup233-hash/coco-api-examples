# curl Examples

Set credentials and choose an exact model ID from the live list before copying the requests:

```bash
export COCO_API_KEY='YOUR_COCO_API_KEY'
export COCO_MODEL='YOUR_MODEL_ID'
```

Never paste a real key into a committed script or shell history shared with others.

## List Models

```bash
curl --fail-with-body --silent --show-error \
  --max-time 30 \
  'https://api.cocoapi.top/v1/models' \
  -H "Authorization: Bearer ${COCO_API_KEY}"
```

Use the returned model ID as `COCO_MODEL`. The available catalog and group access can change.

## Chat Completion

```bash
curl --fail-with-body --silent --show-error \
  --max-time 30 \
  'https://api.cocoapi.top/v1/chat/completions' \
  -H "Authorization: Bearer ${COCO_API_KEY}" \
  -H 'Content-Type: application/json' \
  --data-binary '{
    "model": "'"${COCO_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with one short greeting."}
    ],
    "max_tokens": 128
  }'
```

## Streaming Chat Completion

`--no-buffer` prints SSE chunks as they arrive.

```bash
curl --fail-with-body --silent --show-error --no-buffer \
  --max-time 30 \
  'https://api.cocoapi.top/v1/chat/completions' \
  -H "Authorization: Bearer ${COCO_API_KEY}" \
  -H 'Content-Type: application/json' \
  -H 'Accept: text/event-stream' \
  --data-binary '{
    "model": "'"${COCO_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Explain SSE streaming in three short points."}
    ],
    "max_tokens": 256,
    "stream": true
  }'
```

## Anthropic Messages

This calls the native Messages-compatible endpoint with bearer authentication.

```bash
curl --fail-with-body --silent --show-error \
  --max-time 30 \
  'https://api.cocoapi.top/v1/messages' \
  -H "Authorization: Bearer ${COCO_API_KEY}" \
  -H 'Content-Type: application/json' \
  -H 'anthropic-version: 2023-06-01' \
  --data-binary '{
    "model": "'"${COCO_MODEL}"'",
    "max_tokens": 128,
    "messages": [
      {"role": "user", "content": "Reply with one short greeting."}
    ]
  }'
```

## Inspect Status and Request ID

Remove `--fail-with-body` temporarily and add `--include` to inspect response headers:

```bash
curl --include --silent --show-error \
  --max-time 30 \
  'https://api.cocoapi.top/v1/models' \
  -H "Authorization: Bearer ${COCO_API_KEY}"
```

Record the `x-oneapi-request-id` header when reporting an API error.

## Troubleshooting

Check in this order: **address → credential → model → network → parameters**.

| Symptom | Action |
|---|---|
| HTTP 401 | Confirm `COCO_API_KEY` is present, active, and sent as `Authorization: Bearer ...`. |
| HTTP 429 | Reduce request rate/concurrency and retry later. |
| curl timeout (exit 28) | Check network reachability; increase `--max-time` only after a minimal request works. |
| Model error | Run the model-list request and copy an exact ID available to the key's group. |
| Unexpected output model | Record the request and response names for verification; aliases or upstream mappings may differ. |
| Parameter error | Retry the smallest request. Protocol routing does not guarantee every model/group supports every parameter. |

The API root is `https://api.cocoapi.top`. Clients that append `/v1` should receive that root; clients that do not should receive `https://api.cocoapi.top/v1`.
