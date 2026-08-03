import { afterEach, describe, expect, it, vi } from "vitest";
import { streamChat, type ChatStreamEvent } from "@/lib/chat-stream";

/** Serve `body` as a response whose stream is chopped at the given boundaries,
 * so a frame can be split across reads the way it is on a real socket. */
function respondWith(...packets: string[]) {
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const encoder = new TextEncoder();
      for (const packet of packets) controller.enqueue(encoder.encode(packet));
      controller.close();
    },
  });
  return new Response(stream, { status: 200 });
}

function frame(event: string, data?: unknown) {
  const lines = [`event: ${event}`];
  if (data !== undefined) lines.push(`data: ${JSON.stringify(data)}`);
  return `${lines.join("\n")}\n\n`;
}

async function collect(): Promise<ChatStreamEvent[]> {
  const events: ChatStreamEvent[] = [];
  for await (const evt of streamChat({ apiBaseUrl: "http://api", question: "q" })) {
    events.push(evt);
  }
  return events;
}

afterEach(() => vi.unstubAllGlobals());

function stubFetch(response: Response | (() => Response)) {
  const fetchMock = vi.fn(async () =>
    typeof response === "function" ? response() : response,
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("streamChat", () => {
  it("posts the question and k to the chat endpoint", async () => {
    const fetchMock = stubFetch(respondWith(frame("done", "[DONE]")));

    await collect();

    const [url, init] = fetchMock.mock.calls[0] as unknown as [
      string,
      RequestInit,
    ];
    expect(url).toBe("http://api/chat/stream");
    expect(JSON.parse(init.body as string)).toEqual({ question: "q", k: 4 });
  });

  it("yields sources, tokens and done in wire order", async () => {
    const hits = [{ text: "t", source: "a.md", position: 0, distance: 0.1 }];
    stubFetch(
      respondWith(
        frame("sources", hits),
        frame("token", "Hello"),
        frame("token", " world"),
        frame("done", "[DONE]"),
      ),
    );

    expect(await collect()).toEqual([
      { event: "sources", data: hits },
      { event: "token", data: "Hello" },
      { event: "token", data: " world" },
      { event: "done" },
    ]);
  });

  // The parser buffers because TCP does not respect frame boundaries: a token
  // arriving in two reads must not surface as two half-decoded events.
  it("reassembles a frame split across reads", async () => {
    stubFetch(
      respondWith('event: token\nda', 'ta: "Hel', 'lo"\n\n', frame("done", "x")),
    );

    expect(await collect()).toEqual([
      { event: "token", data: "Hello" },
      { event: "done" },
    ]);
  });

  it("surfaces a server error frame as an event rather than throwing", async () => {
    stubFetch(
      respondWith(frame("error", "Sorry, the answer stream failed."), frame("done", "x")),
    );

    expect(await collect()).toEqual([
      { event: "error", data: "Sorry, the answer stream failed." },
      { event: "done" },
    ]);
  });

  it("ignores frames it has no case for", async () => {
    stubFetch(respondWith(frame("ping", "keepalive"), frame("done", "x")));

    expect(await collect()).toEqual([{ event: "done" }]);
  });

  it("throws when the request fails", async () => {
    stubFetch(new Response(null, { status: 500, statusText: "Server Error" }));

    await expect(collect()).rejects.toThrow(/500/);
  });
});
