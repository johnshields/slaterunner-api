import { defineConfig } from "vite";

/**
 * Vite config
 * Served by FastAPI via app.frontend() at root, so base is "/".
 */
export default defineConfig({
  base: "/",
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
