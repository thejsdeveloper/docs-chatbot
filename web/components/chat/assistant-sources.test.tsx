import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { AssistantSources } from "@/components/chat/assistant-sources";
import type { SourceHit } from "@/lib/chat-stream";

function hit(source: string, position: number): SourceHit {
  return { text: `chunk ${position}`, source, position, distance: 0.1 };
}

/** The list is collapsed behind a trigger, so every assertion needs it open. */
async function renderOpen(sources: SourceHit[]) {
  render(<AssistantSources sources={sources} />);
  await userEvent.click(screen.getByRole("button"));
}

describe("AssistantSources", () => {
  it("renders nothing without sources", () => {
    const { container } = render(<AssistantSources sources={[]} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing when sources are absent entirely", () => {
    const { container } = render(<AssistantSources sources={undefined} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("links each source to its react.dev page", async () => {
    await renderOpen([hit("reference/react/useRef.md", 0)]);

    expect(
      screen.getByRole("link", { name: /reference\/react\/useRef/ }),
    ).toHaveAttribute("href", "https://react.dev/reference/react/useRef");
  });

  // Retrieval matches chunks, not documents: four passages of one page used to
  // render the same link four times.
  it("collapses repeated chunks of one document into a single link", async () => {
    await renderOpen([
      hit("reference/react/useState.md", 0),
      hit("reference/react/useState.md", 3),
      hit("reference/react/useState.md", 7),
    ]);

    expect(screen.getAllByRole("link")).toHaveLength(1);
    expect(screen.getByRole("link")).toHaveTextContent("3 passages");
  });

  it("counts documents, not passages, in the trigger", async () => {
    render(
      <AssistantSources
        sources={[hit("a.md", 0), hit("a.md", 1), hit("b.md", 0)]}
      />,
    );

    expect(screen.getByRole("button")).toHaveTextContent("2");
  });

  it("leaves a single-passage document uncounted", async () => {
    await renderOpen([hit("learn/index.md", 0)]);

    expect(screen.getByRole("link")).toHaveTextContent("learn/index");
    expect(screen.getByRole("link")).not.toHaveTextContent("passage");
  });

  // Hits arrive best-first, so first-seen order is strongest-first and the
  // dedupe must not reshuffle it.
  it("keeps documents in retrieval order", async () => {
    await renderOpen([hit("b.md", 0), hit("a.md", 0), hit("b.md", 1)]);

    expect(screen.getAllByRole("link").map((a) => a.textContent)).toEqual([
      expect.stringContaining("b"),
      expect.stringContaining("a"),
    ]);
  });
});
