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

FROM base AS prod
ENV NODE_ENV=production HOST=0.0.0.0 PORT=4321
COPY --from=build /app/frontend/site/dist ./dist
COPY --from=build /app/frontend/site/node_modules ./node_modules
COPY --from=build /app/frontend/site/package.json ./package.json
RUN addgroup -S site && adduser -S site -G site && chown -R site:site /app
USER site
EXPOSE 4321
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:4321/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "./dist/server/entry.mjs"]
