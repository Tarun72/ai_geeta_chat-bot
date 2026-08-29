import type { ChatRequest, Source, StreamEvent } from "../types";

function parseSseBlock(block: string): StreamEvent | null {
  const lines = block.split("\n");
  let event = "message";
  const dataLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith("event:")) {
      event = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trimStart());
    }
  }

  const data = dataLines.join("\n");

  switch (event) {
    case "sources":
      return { type: "sources", sources: JSON.parse(data) as Source[] };
    case "token":
      return { type: "token", token: JSON.parse(data) as string };
    case "done":
      return { type: "done" };
    case "error":
      return { type: "error", message: JSON.parse(data) as string };
    default:
      return null;
  }
}

export async function* streamChat(
  request: ChatRequest,
  signal?: AbortSignal,
): AsyncGenerator<StreamEvent> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question: request.question,
      top_k: request.top_k ?? 5,
    }),
    signal,
  });

  if (!response.ok) {
    const text = await response.text();
    yield { type: "error", message: text || `Request failed (${response.status})` };
    return;
  }

  if (!response.body) {
    yield { type: "error", message: "No response body received from server." };
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const blocks = buffer.split("\n\n");
    buffer = blocks.pop() ?? "";

    for (const block of blocks) {
      if (!block.trim()) {
        continue;
      }
      const event = parseSseBlock(block);
      if (event) {
        yield event;
      }
    }
  }

  if (buffer.trim()) {
    const event = parseSseBlock(buffer);
    if (event) {
      yield event;
    }
  }
}
