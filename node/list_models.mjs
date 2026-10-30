// List COCO API models and summarize available group metadata.

const MODELS_URL = "https://api.cocoapi.top/v1/models";
const TIMEOUT_MS = 30_000;

function requiredApiKey() {
  const value = process.env.COCO_API_KEY?.trim();
  if (!value) {
    console.error("Missing COCO_API_KEY. Export it before running this example.");
    process.exit(2);
  }
  return value;
}

function groupLabel(model) {
  const value = model.group || model.groups || model.owned_by || "unknown";
  if (Array.isArray(value)) return value.map(String).join(", ") || "unknown";
  return String(value);
}

async function main() {
  const response = await fetch(MODELS_URL, {
    headers: { Authorization: `Bearer ${requiredApiKey()}` },
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
  const models = Array.isArray(payload.data) ? payload.data : [];
  models.sort((left, right) => String(left.id).localeCompare(String(right.id)));

  const counts = new Map();
  for (const model of models) {
    const group = groupLabel(model);
    console.log(`${model.id}\t${group}`);
    counts.set(group, (counts.get(group) ?? 0) + 1);
  }

  console.log(`\nTotal: ${models.length}`);
  console.log("Group metadata (falls back to owned_by when group is absent):");
  for (const [group, count] of [...counts].sort((a, b) => b[1] - a[1])) {
    console.log(`  ${group}: ${count}`);
  }
}

main().catch((error) => {
  if (error.name === "TimeoutError" || error.name === "AbortError") {
    console.error("Model listing timed out after 30 seconds. Check the network and retry.");
  } else if (error instanceof TypeError) {
    console.error(`Could not reach ${MODELS_URL}: ${error.message}`);
  } else {
    console.error(error.message);
  }
  process.exitCode = 1;
});
