// Parse and print an SSE chat stream from COCO API using built-in fetch.

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

function printEvent(dataLines) {
  if (dataLines.length === 0) return false;
  const data = dataLines.join("\n");
  if (data === "[DONE]") return true;
  const payload = JSON.parse(data);
  const content = payload.choices?.[0]?.delta?.content;
  if (content) process.stdout.write(content);
  return false;
}

async function main() {
  const response = await fetch(CHAT_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${requiredEnv("COCO_API_KEY")}`,
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({
      model: requiredEnv("COCO_MODEL"),
      messages: [{ role: "user", content: "Explain SSE streaming in three short points." }],
      max_tokens: 256,
      stream: true,
    }),
    signal: AbortSignal.timeout(TIMEOUT_MS),
  });

  if (!response.ok) throw await responseError(response);
  if (!response.body) throw new Error("The response did not contain a readable stream.");

  const decoder = new TextDecoder();
  let buffer = "";
  let dataLines = [];
  let finished = false;

  for await (const chunk of response.body) {
    buffer += decoder.decode(chunk, { stream: true });
    let newline;
    while (!finished && (newline = buffer.indexOf("\n")) !== -1) {
      let line = buffer.slice(0, newline);
      buffer = buffer.slice(newline + 1);
      if (line.endsWith("\r")) line = line.slice(0, -1);
      if (line === "") {
        finished = printEvent(dataLines);
        dataLines = [];
      } else if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trimStart());
      }
    }
    if (finished) break;
  }

  buffer += decoder.decode();
  const trailing = buffer.endsWith("\r") ? buffer.slice(0, -1) : buffer;
  if (!finished && trailing.startsWith("data:")) dataLines.push(trailing.slice(5).trimStart());
  if (!finished) printEvent(dataLines);
  process.stdout.write("\n");
}

main().catch((error) => {
  if (error.name === "TimeoutError" || error.name === "AbortError") {
    console.error("The stream timed out after 30 seconds. Check the network and retry.");
  } else if (error instanceof TypeError) {
    console.error(`Could not reach ${CHAT_URL}: ${error.message}`);
  } else if (error instanceof SyntaxError) {
    console.error(`The stream contained invalid JSON: ${error.message}`);
  } else {
    console.error(error.message);
  }
  process.exitCode = 1;
});
