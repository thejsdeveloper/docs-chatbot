"use client";

import { useCallback, useRef, useState } from "react";
import { streamChat, type SourceHit } from "@/lib/chat-stream";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceHit[];
  status?: "streaming" | "error";
  error?: string;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

let nextId = 0;
const makeId = () => `msg-${++nextId}`;

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const lastQuestionRef = useRef<string | null>(null);

  const updateAssistant = useCallback(
    (id: string, patch: Partial<ChatMessage>) => {
      setMessages((prev) =>
        prev.map((m) => (m.id === id ? { ...m, ...patch } : m))
      );
    },
    []
  );

  const run = useCallback(
    async (question: string) => {
      lastQuestionRef.current = question;
      const controller = new AbortController();
      abortRef.current = controller;

      const assistantId = makeId();
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: "assistant", content: "", status: "streaming" },
      ]);
      setIsStreaming(true);

      try {
        for await (const evt of streamChat({
          apiBaseUrl: API_BASE_URL,
          question,
          signal: controller.signal,
        })) {
          if (evt.event === "sources") {
            updateAssistant(assistantId, { sources: evt.data });
          } else if (evt.event === "token") {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: m.content + evt.data }
                  : m
              )
            );
          } else if (evt.event === "error") {
            updateAssistant(assistantId, { status: "error", error: evt.data });
          } else if (evt.event === "done") {
            updateAssistant(assistantId, { status: undefined });
          }
        }
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") {
          // Stopping is the user's own choice, so it is not an error -- but
          // `done` never arrives either, and leaving the status set would
          // animate the bubble forever. Settle on the text that did land.
          updateAssistant(assistantId, { status: undefined });
        } else {
          updateAssistant(assistantId, {
            status: "error",
            error: err instanceof Error ? err.message : "Something went wrong.",
          });
        }
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [updateAssistant]
  );

  const sendMessage = useCallback(
    (question: string) => {
      const trimmed = question.trim();
      if (!trimmed || isStreaming) return;
      setMessages((prev) => [
        ...prev,
        { id: makeId(), role: "user", content: trimmed },
      ]);
      void run(trimmed);
    },
    [isStreaming, run]
  );

  const retry = useCallback(() => {
    if (!lastQuestionRef.current || isStreaming) return;
    void run(lastQuestionRef.current);
  }, [isStreaming, run]);

  const stop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    lastQuestionRef.current = null;
    setMessages([]);
  }, []);

  return { messages, isStreaming, sendMessage, retry, stop, reset };
}
