"""Run several COCO API chat requests concurrently with isolated failures."""

import asyncio
import os
import sys

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)

BASE_URL = "https://api.cocoapi.top/v1"
CONCURRENCY = 3
PROMPTS = [
    "Define idempotency in one sentence.",
    "Define exponential backoff in one sentence.",
    "Define an API gateway in one sentence.",
    "Define server-sent events in one sentence.",
    "Define a rate limit in one sentence.",
]


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Missing {name}. Export it before running this example.", file=sys.stderr)
        raise SystemExit(2)
    return value


async def run_one(
    client: AsyncOpenAI,
    semaphore: asyncio.Semaphore,
    model: str,
    index: int,
    prompt: str,
) -> tuple[int, bool, str]:
    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=128,
            )
            return index, True, response.choices[0].message.content or ""
        except AuthenticationError:
            return index, False, "401 authentication failed; check COCO_API_KEY."
        except RateLimitError:
            return index, False, "429 rate limit reached; lower concurrency and retry later."
        except APITimeoutError:
            return index, False, "Timed out after 30 seconds; check the network and retry."
        except APIConnectionError as exc:
            return index, False, f"Connection failed: {exc}"
        except APIStatusError as exc:
            request_id = exc.response.headers.get("x-oneapi-request-id", "not provided")
            return index, False, f"HTTP {exc.status_code}; request id: {request_id}"
        except Exception as exc:  # Isolate one malformed response without cancelling the batch.
            return index, False, f"Unexpected error: {type(exc).__name__}: {exc}"


async def main() -> None:
    client = AsyncOpenAI(
        api_key=required_env("COCO_API_KEY"),
        base_url=BASE_URL,
        timeout=30.0,
        max_retries=0,
    )
    model = required_env("COCO_MODEL")
    semaphore = asyncio.Semaphore(CONCURRENCY)

    results = await asyncio.gather(
        *(run_one(client, semaphore, model, index, prompt) for index, prompt in enumerate(PROMPTS, 1))
    )
    await client.close()

    failed = False
    for index, ok, output in sorted(results):
        label = "ok" if ok else "error"
        print(f"[{index}] {label}: {output}")
        failed = failed or not ok
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
