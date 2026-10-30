// Call COCO API through the native Anthropic Messages-compatible endpoint.

const MESSAGES_URL = "https://api.cocoapi.top/v1/messages";
const TIMEOUT_MS = 30_000;

function requiredEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) {
    console.error(`Missing ${name}. Export it before running this example.`);
    process.exit(2);
  }
  return value;
}

async function main() {
  const response = await fetch(MESSAGES_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${requiredEnv("COCO_API_KEY")}`,
      "Content-Type": "application/json",
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: requiredEnv("COCO_MODEL"),
      max_tokens: 128,
      messages: [{ role: "user", content: "Reply with one short greeting." }],
    }),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });

  if (!response.ok) {
    const requestId = response.headers.get("x-oneapi-request-id") ?? "not provided";
    const body = await response.text();
    if (response.status === 401) {
      throw new Error("401 authentication failed. Check COCO_API_KEY and whether it is active.");
    }
    if (response.status === 429) {
      throw new Error("429 rate limit reached. Reduce request frequency and retry later.");
    }
    throw new Error(`API returned HTTP ${response.status}; request id: ${requestId}; body: ${body}`);
  }

  const payload = await response.json();
  const text = (payload.content ?? [])
    .filter((block) => block.type === "text")
    .map((block) => block.text ?? "")
    .join("");
  console.log(text);
}

main().catch((error) => {
  if (error.name === "TimeoutError" || error.name === "AbortError") {
    console.error("Request timed out after 30 seconds. Check the network and retry.");
  } else if (error instanceof TypeError) {
    console.error(`Could not reach ${MESSAGES_URL}: ${error.message}`);
  } else {
    console.error(error.message);
  }
  process.exitCode = 1;
});
