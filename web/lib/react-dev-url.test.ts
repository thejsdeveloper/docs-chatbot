import { describe, expect, it } from "vitest";
import { reactDevUrl, sourceLabel } from "@/lib/react-dev-url";

describe("reactDevUrl", () => {
  it("maps a corpus path to its react.dev route", () => {
    expect(reactDevUrl("reference/react/useState.md")).toBe(
      "https://react.dev/reference/react/useState",
    );
  });

  // react.dev serves /learn, not /learn/index -- an index.md that kept its
  // basename would produce a 404 in the sources list.
  it("drops a trailing index segment", () => {
    expect(reactDevUrl("learn/index.md")).toBe("https://react.dev/learn");
  });

  it("maps the root index to the bare origin, with no trailing slash", () => {
    expect(reactDevUrl("index.md")).toBe("https://react.dev");
  });

  it("only strips index as a whole segment", () => {
    expect(reactDevUrl("learn/indexing.md")).toBe(
      "https://react.dev/learn/indexing",
    );
  });
});

describe("sourceLabel", () => {
  it("shows the path without the extension", () => {
    expect(sourceLabel("reference/react/useRef.md")).toBe(
      "reference/react/useRef",
    );
  });

  it("keeps index visible, since the label names the file", () => {
    expect(sourceLabel("learn/index.md")).toBe("learn/index");
  });
});
