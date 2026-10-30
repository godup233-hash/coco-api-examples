// Send one minimal OpenAI-compatible chat completion request to COCO API.

const CHAT_URL = "https://api.cocoapi.top/v1/chat/completions";
const TIMEOUT_MS = 30_000;

function requiredEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) {
    console.error(`Missing ${name}. Export it before running this example.`);
    process.exit(2);
  }
  return value;
}

async function responseError(response) {
  const requestId = response.headers.get("x-oneapi-request-id") ?? "not provided";
  const body = await response.text();
  if (response.status === 401) {
    return new Error("401 authentication failed. Check COCO_API_KEY and whether it is active.");
  }
  if (response.status === 429) {
    return new Error("429 rate limit reached. Reduce request frequency and retry later.");
  }
  return new Error(`API returned HTTP ${response.status}; request id: ${requestId}; body: ${body}`);
}

async function main() {
  const response = await fetch(CHAT_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${requiredEnv("COCO_API_KEY")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: requiredEnv("COCO_MODEL"),
      messages: [{ role: "user", content: "Reply with one short greeting." }],
      max_tokens: 128,
    }),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });

  if (!response.ok) {
    throw await responseError(response);
  }

  const payload = await response.json();
  console.log(payload.choices?.[0]?.message?.content ?? "");
}

main().catch((error) => {
  if (error.name === "TimeoutError" || error.name === "AbortError") {
    console.error("Request timed out after 30 seconds. Check the network and retry.");
  } else if (error instanceof TypeError) {
    console.error(`Could not reach ${CHAT_URL}: ${error.message}`);
  } else {
    console.error(error.message);
  }
  process.exitCode = 1;
});
