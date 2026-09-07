# syntax=docker/dockerfile:1
# Built from the workspace root so the shared token package resolves.
FROM node:22-alpine AS base
RUN corepack enable && corepack prepare pnpm@9.15.0 --activate
WORKDIR /app

FROM base AS deps
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY frontend/shared/package.json ./frontend/shared/
COPY frontend/site/package.json ./frontend/site/
RUN pnpm install --frozen-lockfile

FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/frontend/site/node_modules ./frontend/site/node_modules
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY frontend/shared ./frontend/shared
COPY frontend/site ./frontend/site
RUN pnpm --filter @shruti/site build
# The one dependency that cannot be bundled.
#
# Astro bundles everything it can, so this image's runtime node_modules is
# under a megabyte. `@resvg/resvg-js` loads a compiled .node binary, so Vite
# leaves the import alone and the package has to genuinely be on disk when the
# server runs.
#
# Installed on its own, with npm rather than pnpm, into a scratch directory:
#
#   * `pnpm deploy --prod` was the obvious tool and was wrong. It faithfully
#     installs everything under `dependencies`, and this package.json keeps
#     astro, typescript and tailwind there — so it produced a correct, working
#     281MB node_modules and took the image from 232MB to 659MB.
#   * copying the site's own node_modules is not enough either: pnpm fills it
#     with symlinks into the workspace store, which arrive dangling.
#
#   * npm writes plain directories, so what lands here is exactly the
#     rasteriser and its platform binary and nothing else.
#
# The version is pinned to package.json's; bump both together.
# The package.json is not optional: without one npm walks UP looking for the
# nearest manifest, finds the workspace root, and installs into /app instead —
# leaving /app/runtime/node_modules absent and the COPY below failing.
RUN mkdir -p /app/runtime \
 && echo '{"name":"site-runtime","private":true}' > /app/runtime/package.json \
 && cd /app/runtime \
 && npm install --omit=dev --no-package-lock --no-audit --no-fund \
      @resvg/resvg-js@2.6.2

FROM base AS prod
ENV NODE_ENV=production HOST=0.0.0.0 PORT=4321
COPY --from=build /app/frontend/site/dist ./dist
COPY --from=build /app/frontend/site/node_modules ./node_modules
COPY --from=build /app/runtime/node_modules ./node_modules
COPY --from=build /app/frontend/site/package.json ./package.json
# The fonts the OG card is rasterised with. Not in public/ on purpose: these
# are for the SERVER to draw with, and serving them to browsers would ship a
# second copy of two faces the site already delivers as woff2. Built by
# scripts/build-render-fonts.py — see the header there for why the shipped
# woff2 cannot be used directly.
COPY --from=build /app/frontend/site/fonts-render ./fonts-render
RUN addgroup -S site && adduser -S site -G site && chown -R site:site /app
USER site
EXPOSE 4321
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:4321/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "./dist/server/entry.mjs"]
