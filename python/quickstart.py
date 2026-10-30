"""Send one minimal OpenAI-compatible chat completion request to COCO API."""

import os
import sys

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

BASE_URL = "https://api.cocoapi.top/v1"


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Missing {name}. Export it before running this example.", file=sys.stderr)
        raise SystemExit(2)
    return value


def main() -> None:
    client = OpenAI(
        api_key=required_env("COCO_API_KEY"),
        base_url=BASE_URL,
        timeout=30.0,
        max_retries=0,
    )
    model = required_env("COCO_MODEL")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Reply with one short greeting."}],
            max_tokens=128,
        )
        print(response.choices[0].message.content or "")
    except AuthenticationError:
        print("401 authentication failed. Check COCO_API_KEY and whether it is active.", file=sys.stderr)
        raise SystemExit(1)
    except RateLimitError:
        print("429 rate limit reached. Reduce request frequency and retry later.", file=sys.stderr)
        raise SystemExit(1)
    except APITimeoutError:
        print("Request timed out after 30 seconds. Check the network and retry.", file=sys.stderr)
        raise SystemExit(1)
    except APIConnectionError as exc:
        print(f"Could not reach {BASE_URL}: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except APIStatusError as exc:
        request_id = exc.response.headers.get("x-oneapi-request-id", "not provided")
        print(f"API returned HTTP {exc.status_code}; request id: {request_id}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
