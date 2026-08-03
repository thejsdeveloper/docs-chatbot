import { defineConfig } from "vitest/config";

export default defineConfig({
  // @vitejs/plugin-react is deliberately absent: it drags in a Babel 8 RC that
  // conflicts with shadcn's Babel 7. Vite's own transform handles the JSX.
  resolve: { tsconfigPaths: true },
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    globals: true,
    include: ["{app,components,lib}/**/*.test.{ts,tsx}"],
  },
});
