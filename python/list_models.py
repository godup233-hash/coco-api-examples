"""List COCO API models and summarize available group metadata."""

from collections import Counter
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


def required_api_key() -> str:
    value = os.environ.get("COCO_API_KEY", "").strip()
    if not value:
        print("Missing COCO_API_KEY. Export it before running this example.", file=sys.stderr)
        raise SystemExit(2)
    return value


def group_label(model: object) -> str:
    payload = model.model_dump()  # type: ignore[attr-defined]
    value = payload.get("group") or payload.get("groups") or payload.get("owned_by") or "unknown"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "unknown"
    return str(value)


def main() -> None:
    client = OpenAI(
        api_key=required_api_key(),
        base_url=BASE_URL,
        timeout=30.0,
        max_retries=0,
    )

    try:
        models = list(client.models.list().data)
        for model in sorted(models, key=lambda item: item.id):
            print(f"{model.id}\t{group_label(model)}")

        counts = Counter(group_label(model) for model in models)
        print(f"\nTotal: {len(models)}")
        print("Group metadata (falls back to owned_by when group is absent):")
        for group, count in counts.most_common():
            print(f"  {group}: {count}")
    except AuthenticationError:
        print("401 authentication failed. Check COCO_API_KEY and whether it is active.", file=sys.stderr)
        raise SystemExit(1)
    except RateLimitError:
        print("429 rate limit reached. Reduce request frequency and retry later.", file=sys.stderr)
        raise SystemExit(1)
    except APITimeoutError:
        print("Model listing timed out after 30 seconds. Check the network and retry.", file=sys.stderr)
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
