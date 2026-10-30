"""Call COCO API through the native Anthropic Messages-compatible endpoint."""

import json
import os
import socket
import sys
from urllib import error, request

MESSAGES_URL = "https://api.cocoapi.top/v1/messages"
TIMEOUT_SECONDS = 30


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Missing {name}. Export it before running this example.", file=sys.stderr)
        raise SystemExit(2)
    return value


def main() -> None:
    api_key = required_env("COCO_API_KEY")
    payload = {
        "model": required_env("COCO_MODEL"),
        "max_tokens": 128,
        "messages": [{"role": "user", "content": "Reply with one short greeting."}],
    }
    api_request = request.Request(
        MESSAGES_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with request.urlopen(api_request, timeout=TIMEOUT_SECONDS) as response:
            body = json.load(response)
        text_blocks = [
            block.get("text", "")
            for block in body.get("content", [])
            if block.get("type") == "text"
        ]
        print("".join(text_blocks))
    except error.HTTPError as exc:
        request_id = exc.headers.get("x-oneapi-request-id", "not provided")
        if exc.code == 401:
            message = "401 authentication failed. Check COCO_API_KEY and whether it is active."
        elif exc.code == 429:
            message = "429 rate limit reached. Reduce request frequency and retry later."
        else:
            detail = exc.read().decode("utf-8", errors="replace")
            message = f"API returned HTTP {exc.code}; request id: {request_id}; body: {detail}"
        print(message, file=sys.stderr)
        raise SystemExit(1)
    except (TimeoutError, socket.timeout):
        print(f"Request timed out after {TIMEOUT_SECONDS} seconds. Check the network and retry.", file=sys.stderr)
        raise SystemExit(1)
    except error.URLError as exc:
        if isinstance(exc.reason, (TimeoutError, socket.timeout)):
            print(f"Request timed out after {TIMEOUT_SECONDS} seconds. Check the network and retry.", file=sys.stderr)
        else:
            print(f"Could not reach {MESSAGES_URL}: {exc.reason}", file=sys.stderr)
        raise SystemExit(1)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"The API returned an unexpected response: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
