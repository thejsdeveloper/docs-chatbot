import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ChatStreamEvent } from "@/lib/chat-stream";
import { useChat } from "@/lib/use-chat";

const streamChat = vi.hoisted(() => vi.fn());
vi.mock("@/lib/chat-stream", () => ({ streamChat }));

/** Emits `events`, then ends -- the happy path for a completed answer. */
function emits(...events: ChatStreamEvent[]) {
  streamChat.mockImplementation(async function* () {
    for (const evt of events) yield evt;
  });
}

/** A stream that yields nothing and stays open until `release()` is called,
 * which is what lets a test observe the in-flight state. */
function stallingStream() {
  let release!: () => void;
  const open = new Promise<void>((resolve) => {
    release = resolve;
  });
  streamChat.mockImplementation(async function* () {
    await open;
  });
  return () => release();
}

const token = (data: string): ChatStreamEvent => ({ event: "token", data });
const hit = (source: string) => ({
  text: "t",
  source,
  position: 0,
  distance: 0.1,
});

afterEach(() => vi.clearAllMocks());

describe("useChat", () => {
  it("appends the question, then the answer it streams back", async () => {
    emits(token("Because "), token("StrictMode."), { event: "done" });
    const { result } = renderHook(() => useChat());

    act(() => result.current.sendMessage("Why twice?"));

    await waitFor(() => expect(result.current.isStreaming).toBe(false));
    expect(result.current.messages).toMatchObject([
      { role: "user", content: "Why twice?" },
      { role: "assistant", content: "Because StrictMode.", status: undefined },
    ]);
  });

  it("attaches sources to the answer they belong to", async () => {
    emits(
      { event: "sources", data: [hit("a.md")] },
      token("hi"),
      { event: "done" },
    );
    const { result } = renderHook(() => useChat());

    act(() => result.current.sendMessage("q"));

    await waitFor(() =>
      expect(result.current.messages[1].sources).toHaveLength(1),
    );
  });

  it("trims the question before sending it", async () => {
    emits({ event: "done" });
    const { result } = renderHook(() => useChat());

    act(() => result.current.sendMessage("  spaced  "));

    await waitFor(() => expect(result.current.isStreaming).toBe(false));
    expect(result.current.messages[0].content).toBe("spaced");
    expect(streamChat).toHaveBeenCalledWith(
      expect.objectContaining({ question: "spaced" }),
    );
  });

  it("ignores a blank submission", () => {
    const { result } = renderHook(() => useChat());

    act(() => result.current.sendMessage("   "));

    expect(result.current.messages).toEqual([]);
    expect(streamChat).not.toHaveBeenCalled();
  });

  // Two concurrent streams would interleave tokens into one bubble.
  it("refuses a second question while one is in flight", async () => {
    const release = stallingStream();
    const { result } = renderHook(() => useChat());

    act(() => result.current.sendMessage("first"));
    await waitFor(() => expect(result.current.isStreaming).toBe(true));
    act(() => result.current.sendMessage("second"));

    expect(streamChat).toHaveBeenCalledTimes(1);
    expect(result.current.messages).toHaveLength(2);
    act(release);
  });

  it("marks the answer as errored when the stream reports a failure", async () => {
    emits({ event: "error", data: "Sorry, the answer stream failed." });
    const { result } = renderHook(() => useChat());

    act(() => result.current.sendMessage("q"));

    await waitFor(() =>
      expect(result.current.messages[1]).toMatchObject({
        status: "error",
        error: "Sorry, the answer stream failed.",
      }),
    );
  });

  it("reports a transport failure with the thrown message", async () => {
    streamChat.mockImplementation(async function* () {
      throw new Error("Chat request failed: 500 Server Error");
    });
    const { result } = renderHook(() => useChat());

    act(() => result.current.sendMessage("q"));

    await waitFor(() =>
      expect(result.current.messages[1].error).toMatch(/500/),
    );
  });

  // Stopping is the user's own choice, so it must not look like a failure.
  it("does not mark a user-aborted stream as an error", async () => {
    streamChat.mockImplementation(async function* () {
      throw new DOMException("aborted", "AbortError");
    });
    const { result } = renderHook(() => useChat());

    act(() => result.current.sendMessage("q"));

    await waitFor(() => expect(result.current.isStreaming).toBe(false));
    expect(result.current.messages[1].status).toBeUndefined();
    expect(result.current.messages[1].error).toBeUndefined();
  });

  it("aborts the request when stopped", async () => {
    const release = stallingStream();
    const { result } = renderHook(() => useChat());
    act(() => result.current.sendMessage("q"));
    await waitFor(() => expect(result.current.isStreaming).toBe(true));

    act(() => result.current.stop());

    const { signal } = streamChat.mock.calls[0][0];
    expect(signal.aborted).toBe(true);
    act(release);
  });

  // Retry re-asks the last *question*; it must not resend a stale answer or
  // append a duplicate user bubble.
  it("re-asks the last question without repeating the user message", async () => {
    emits({ event: "error", data: "boom" });
    const { result } = renderHook(() => useChat());
    act(() => result.current.sendMessage("Why twice?"));
    await waitFor(() => expect(result.current.isStreaming).toBe(false));

    emits(token("ok"), { event: "done" });
    act(() => result.current.retry());
    await waitFor(() => expect(result.current.isStreaming).toBe(false));

    expect(streamChat).toHaveBeenLastCalledWith(
      expect.objectContaining({ question: "Why twice?" }),
    );
    expect(result.current.messages.filter((m) => m.role === "user")).toHaveLength(1);
  });

  it("does nothing on retry before anything has been asked", () => {
    const { result } = renderHook(() => useChat());

    act(() => result.current.retry());

    expect(streamChat).not.toHaveBeenCalled();
  });

  it("clears the thread on reset", async () => {
    emits(token("hi"), { event: "done" });
    const { result } = renderHook(() => useChat());
    act(() => result.current.sendMessage("q"));
    await waitFor(() => expect(result.current.isStreaming).toBe(false));

    act(() => result.current.reset());

    expect(result.current.messages).toEqual([]);
  });

  it("forgets the last question on reset, so retry cannot resurrect it", async () => {
    emits(token("hi"), { event: "done" });
    const { result } = renderHook(() => useChat());
    act(() => result.current.sendMessage("q"));
    await waitFor(() => expect(result.current.isStreaming).toBe(false));

    act(() => result.current.reset());
    act(() => result.current.retry());

    expect(streamChat).toHaveBeenCalledTimes(1);
  });

  it("gives every message a distinct id", async () => {
    emits(token("hi"), { event: "done" });
    const { result } = renderHook(() => useChat());

    act(() => result.current.sendMessage("one"));
    await waitFor(() => expect(result.current.isStreaming).toBe(false));
    act(() => result.current.sendMessage("two"));
    await waitFor(() => expect(result.current.isStreaming).toBe(false));

    const ids = result.current.messages.map((m) => m.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
