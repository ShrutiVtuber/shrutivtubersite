// @ts-check
import node from "@astrojs/node";
import { defineConfig } from "astro/config";

// SSR, not static. Content lives in Postgres and is edited through the admin,
// so a page must render from the database on request — the whole point of the
// content model is that unhiding a block from Athens takes effect immediately,
// without a rebuild or a deploy.
//
// Tailwind is wired through PostCSS rather than the @astrojs/tailwind
// integration, matching how theourgia does it.
export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  server: { host: "127.0.0.1", port: 4321 },
  vite: {
    ssr: {
      // The production image ships `dist/` and almost no node_modules — Astro
      // bundles what it needs into the server entry. markdown-remark is left
      // external by default and then cannot be resolved at runtime, so it has
      // to be bundled in explicitly. It renders the section bodies the admin
      // writes, which are markdown in the database.
      noExternal: ["@astrojs/markdown-remark"],
    },
    // The API is same-origin in production (Caddy routes /api/*), so there is
    // no CORS surface. In dev, proxy to the running stack so the site behaves
    // the same way.
    server: {
      proxy: {
        "/api": { target: "http://127.0.0.1:8200", changeOrigin: true },
      },
    },
  },
});
