export interface SourceHit {
  text: string;
  source: string;
  position: number;
  distance: number;
}

export type ChatStreamEvent =
  | { event: "sources"; data: SourceHit[] }
  | { event: "token"; data: string }
  | { event: "error"; data: string }
  | { event: "done" };

/** Splits a raw SSE byte stream into { event, data } frames per the spec's blank-line delimiter. */
async function* parseSseStream(
  body: ReadableStream<Uint8Array>
): AsyncGenerator<{ event: string; data: string }> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let boundary: number;
      while ((boundary = buffer.indexOf("\n\n")) !== -1) {
        const rawFrame = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);

        let event = "message";
        const dataLines: string[] = [];
        for (const line of rawFrame.split("\n")) {
          if (line.startsWith("event:")) {
            event = line.slice("event:".length).trim();
          } else if (line.startsWith("data:")) {
            dataLines.push(line.slice("data:".length).trim());
          }
        }
        if (dataLines.length > 0) {
          yield { event, data: dataLines.join("\n") };
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export interface ChatStreamRequest {
  apiBaseUrl: string;
  question: string;
  k?: number;
  signal?: AbortSignal;
}

/** Streams POST /chat/stream, yielding typed events as they arrive off the wire. */
export async function* streamChat({
  apiBaseUrl,
  question,
  k = 4,
  signal,
}: ChatStreamRequest): AsyncGenerator<ChatStreamEvent> {
  const res = await fetch(`${apiBaseUrl}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, k }),
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed: ${res.status} ${res.statusText}`);
  }

  for await (const frame of parseSseStream(res.body)) {
    switch (frame.event) {
      case "sources":
        yield { event: "sources", data: JSON.parse(frame.data) as SourceHit[] };
        break;
      case "token":
        yield { event: "token", data: JSON.parse(frame.data) as string };
        break;
      case "error":
        yield { event: "error", data: JSON.parse(frame.data) as string };
        break;
      case "done":
        yield { event: "done" };
        break;
    }
  }
}
