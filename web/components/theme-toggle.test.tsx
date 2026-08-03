import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ThemeToggle } from "@/components/theme-toggle";

const setTheme = vi.fn();
const useTheme = vi.hoisted(() => vi.fn());
vi.mock("next-themes", () => ({ useTheme }));

beforeEach(() => {
  vi.clearAllMocks();
  useTheme.mockReturnValue({ resolvedTheme: "light", setTheme });
});

describe("ThemeToggle", () => {
  it("switches to dark when the resolved theme is light", async () => {
    render(<ThemeToggle />);

    await userEvent.click(
      screen.getByRole("button", { name: "Switch to dark mode" }),
    );

    expect(setTheme).toHaveBeenCalledWith("dark");
  });

  it("switches back to light when the resolved theme is dark", async () => {
    useTheme.mockReturnValue({ resolvedTheme: "dark", setTheme });
    render(<ThemeToggle />);

    await userEvent.click(
      screen.getByRole("button", { name: "Switch to light mode" }),
    );

    expect(setTheme).toHaveBeenCalledWith("light");
  });

  // The server cannot know the theme, so it must emit a blank slot of the same
  // size: an icon there would hydrate to the wrong one and shift the header.
  // This asserts the *server* snapshot, which is the half that regressed most
  // easily when the mounted flag moved out of an effect.
  it("renders no icon on the server", () => {
    useTheme.mockReturnValue({ resolvedTheme: "dark", setTheme });

    const html = renderToStaticMarkup(<ThemeToggle />);

    expect(html).not.toContain("<svg");
    expect(html).toContain("size-9");
  });
});
