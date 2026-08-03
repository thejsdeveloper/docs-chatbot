import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ChatHeader } from "@/components/chat/chat-header";

describe("ChatHeader", () => {
  // Nothing to reset on an empty thread, and the button would be the only
  // control competing with the suggestions for attention.
  it("hides new chat until there is a conversation to clear", () => {
    render(<ChatHeader onReset={vi.fn()} showReset={false} />);

    expect(screen.queryByRole("button", { name: "New chat" })).toBeNull();
  });

  it("clears the thread when new chat is pressed", async () => {
    const onReset = vi.fn();
    render(<ChatHeader onReset={onReset} showReset />);

    await userEvent.click(screen.getByRole("button", { name: "New chat" }));

    expect(onReset).toHaveBeenCalledTimes(1);
  });

  it("names the app in a single top-level heading", () => {
    render(<ChatHeader onReset={vi.fn()} showReset={false} />);

    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "React Docs Chatbot",
    );
  });
});
