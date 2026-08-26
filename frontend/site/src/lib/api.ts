/* Server-side API access.
 *
 * Astro renders on the server, so these run in Node and talk to the backends
 * over the internal network — never from the browser. Every secret stays
 * server-side, and a page arrives already populated rather than assembling
 * itself after load.
 *
 * Failure is expected and handled, not thrown: a block whose data could not be
 * fetched renders its designed absent state. One endpoint being down must not
 * blank the page.
 */
export const SITE_API = import.meta.env.SHRUTI_API_INTERNAL ?? "http://backend:8000";
const ASTRO_API = import.meta.env.SHRUTI_ASTRO_INTERNAL ?? "http://shruti-astro:8000";

async function get<T>(base: string, path: string, timeoutMs = 6000): Promise<T | null> {
  const control = new AbortController();
  const timer = setTimeout(() => control.abort(), timeoutMs);
  try {
    const response = await fetch(`${base}${path}`, { signal: control.signal });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    // Timeouts and network errors both land here. Returning null lets the
    // caller render its absent state; throwing would take the page with it.
    return null;
  } finally {
    clearTimeout(timer);
  }
}

/* Some daemon 4xx bodies ARE the answer: "the Sun did not rise at this
 * location on this date" is a fact about the sky, not a failure, and the page
 * has a designed state for it. Collapsing every non-200 to null threw that
 * sentence away and left the page unable to tell "no sunrise" from "the
 * ephemeris is down" — two states the design treats very differently.
 */
export interface Answer<T> {
  ok: boolean;
  data: T | null;
  /** The daemon's own explanation, where it gave one. */
  detail: string;
  status: number;
}

async function ask<T>(base: string, path: string, timeoutMs = 8000): Promise<Answer<T>> {
  const control = new AbortController();
  const timer = setTimeout(() => control.abort(), timeoutMs);
  try {
    const response = await fetch(`${base}${path}`, { signal: control.signal });
    const body = await response.json().catch(() => null);
    if (response.ok) return { ok: true, data: body as T, detail: "", status: response.status };
    return {
      ok: false,
      data: null,
      detail: typeof body?.detail === "string" ? body.detail : "",
      status: response.status,
    };
  } catch {
    return { ok: false, data: null, detail: "", status: 0 };
  } finally {
    clearTimeout(timer);
  }
}

export const askAstro = <T,>(path: string, timeoutMs = 8000) =>
  ask<T>(ASTRO_API, path, timeoutMs);

export const site = <T,>(path: string) => get<T>(SITE_API, path);
export const astro = <T,>(path: string) => get<T>(ASTRO_API, path);

/* The backend mounts its routers under /api, and the content router under
 * /api/content. Naming the paths here once stops every caller from having to
 * remember which of the two a given resource lives on — and stops the class of
 * bug this file shipped with, where every path was missing its prefix, every
 * fetch 404'd, and nothing looked broken because the designed absent states
 * look deliberate. That is precisely the failure the design brief warns about
 * with the press kit rendering nine zeroes.
 */
export const PATHS = {
  live: "/api/live",
  schedule: "/api/schedule",
  links: "/api/content/links",
  projects: "/api/content/projects",
  tools: "/api/content/tools",
  profile: "/api/content/profile",
  page: (name: string) => `/api/content/page/${name}`,
  products: "/api/shop/products",
  product: (slug: string) => `/api/shop/products/${slug}`,
} as const;

export interface LinkGroups {
  groups: Record<string, { platform: string; url: string; label: string }[]>;
}

export interface Project {
  slug: string;
  name: string;
  tagline: string;
  bodyMd: string;
  repoUrl: string;
  siteUrl: string;
  status: string;
  /** Chosen to lead the landing page. */
  featured: boolean;
  /* The API has always sent this. It was missing here, so the landing page —
     typed against this and not against the payload — had no screenshot to
     pass and passed null instead. A project's picture then appeared on /work
     and nowhere else. */
  /** The first photograph, kept for anything that only wants one. */
  media: { url: string; alt: string } | null;
  /** All of them, in order, the first being the one above. */
  photos: { url: string; alt: string }[];
}

export interface LiveStatus {
  anyLive: boolean;
  primary: { platform: string; title: string; watchUrl: string } | null;
  platforms: {
    platform: string;
    isLive: boolean;
    url: string;
    watchUrl: string;
    error: string | null;
  }[];
}

export interface ShopProduct {
  slug: string;
  name: string;
  kind: "physical" | "digital";
  tagline: string;
  bodyMd: string;
  priceCents: number;
  currency: string;
  /** A real state, and not the same as absent. */
  soldOut: boolean;
  /** The first photograph, for anything that only wants one. */
  media: { url: string; alt: string } | null;
  /** All of them, in order; the first is the one above. */
  photos: { url: string; alt: string }[];
}


/**
 * Where this site actually lives, for any URL that leaves the page.
 *
 * **Never build one of these from `Astro.url`.** Behind Caddy the Node adapter
 * reports `Astro.url.origin` as "http://localhost" whatever Host and
 * X-Forwarded-Host say — the same fact that forced Astro's own origin check
 * off in astro.config.mjs. A canonical tag or a sitemap built that way is
 * invisibly wrong until somebody opens it; a **share link** built that way is
 * worse, because it is handed to another person and simply does not work.
 *
 * That has now had to be remembered in five places, so it lives here once.
 */
export const SITE_URL =
  (import.meta.env.SHRUTI_SITE_URL ?? "https://shrutivtuber.com").replace(/\/$/, "");
