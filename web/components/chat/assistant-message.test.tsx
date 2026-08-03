import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { AssistantMessage } from "@/components/chat/assistant-message";
import type { ChatMessage } from "@/lib/use-chat";

function message(patch: Partial<ChatMessage> = {}): ChatMessage {
  return { id: "m1", role: "assistant", content: "An answer.", ...patch };
}

describe("AssistantMessage", () => {
  it("shows the answer text", () => {
    render(<AssistantMessage message={message()} onRetry={vi.fn()} />);

    expect(screen.getByText("An answer.")).toBeInTheDocument();
  });

  // A stream that has opened but produced no token yet must not render an
  // empty response block, or the bubble flickers on every send.
  it("renders no body while the answer is still empty", () => {
    render(
      <AssistantMessage
        message={message({ content: "", status: "streaming" })}
        onRetry={vi.fn()}
      />,
    );

    expect(screen.queryByRole("button", { name: "Retry" })).toBeNull();
    expect(screen.queryByText("An answer.")).toBeNull();
  });

  it("surfaces the server's reason when the stream fails", () => {
    render(
      <AssistantMessage
        message={message({
          status: "error",
          error: "Sorry, the answer stream failed.",
        })}
        onRetry={vi.fn()}
      />,
    );

    expect(
      screen.getByText("Sorry, the answer stream failed."),
    ).toBeInTheDocument();
  });

  it("falls back to a generic message when the error has no text", () => {
    render(
      <AssistantMessage message={message({ status: "error" })} onRetry={vi.fn()} />,
    );

    expect(screen.getByText("Something went wrong.")).toBeInTheDocument();
  });

  it("re-asks the question when retry is pressed", async () => {
    const onRetry = vi.fn();
    render(
      <AssistantMessage
        message={message({ status: "error", error: "boom" })}
        onRetry={onRetry}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: "Retry" }));

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  // Partial answers are kept: the user can read what arrived before the break.
  it("keeps the partial answer alongside the error", () => {
    render(
      <AssistantMessage
        message={message({ content: "Half an ans", status: "error", error: "boom" })}
        onRetry={vi.fn()}
      />,
    );

    expect(screen.getByText("Half an ans")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("offers no retry on a healthy answer", () => {
    render(<AssistantMessage message={message()} onRetry={vi.fn()} />);

    expect(screen.queryByRole("button", { name: "Retry" })).toBeNull();
  });
});
