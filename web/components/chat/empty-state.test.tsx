import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { EmptyState } from "@/components/chat/empty-state";

describe("EmptyState", () => {
  it("offers a starting point for a user who has no question yet", () => {
    render(<EmptyState onSelectPrompt={vi.fn()} />);

    expect(screen.getAllByRole("button").length).toBeGreaterThan(0);
  });

  // The label is short ("Effects running twice"); the prompt is the real
  // question. Sending the label instead would degrade retrieval silently.
  it("sends the full prompt, not the button label", async () => {
    const onSelectPrompt = vi.fn();
    render(<EmptyState onSelectPrompt={onSelectPrompt} />);

    await userEvent.click(
      screen.getByRole("button", { name: /Effects running twice/ }),
    );

    expect(onSelectPrompt).toHaveBeenCalledWith(
      "Why does my Effect run twice on mount?",
    );
  });

  it("fires once per click", async () => {
    const onSelectPrompt = vi.fn();
    render(<EmptyState onSelectPrompt={onSelectPrompt} />);

    await userEvent.click(screen.getByRole("button", { name: /useRef/ }));

    expect(onSelectPrompt).toHaveBeenCalledTimes(1);
  });
});
