"""Stream an OpenAI-compatible chat response from COCO API over SSE."""

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

    try:
        stream = client.chat.completions.create(
            model=required_env("COCO_MODEL"),
            messages=[{"role": "user", "content": "Explain SSE streaming in three short points."}],
            max_tokens=256,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content if chunk.choices else None
            if content:
                print(content, end="", flush=True)
        print()
    except AuthenticationError:
        print("401 authentication failed. Check COCO_API_KEY and whether it is active.", file=sys.stderr)
        raise SystemExit(1)
    except RateLimitError:
        print("429 rate limit reached. Reduce request frequency and retry later.", file=sys.stderr)
        raise SystemExit(1)
    except APITimeoutError:
        print("The stream timed out after 30 seconds. Check the network and retry.", file=sys.stderr)
        raise SystemExit(1)
    except APIConnectionError as exc:
        print(f"Streaming connection failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except APIStatusError as exc:
        request_id = exc.response.headers.get("x-oneapi-request-id", "not provided")
        print(f"API returned HTTP {exc.status_code}; request id: {request_id}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
