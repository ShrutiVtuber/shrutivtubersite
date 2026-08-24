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
const SITE_API = import.meta.env.SHRUTI_API_INTERNAL ?? "http://backend:8000";
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

export const site = <T,>(path: string) => get<T>(SITE_API, path);
export const astro = <T,>(path: string) => get<T>(ASTRO_API, path);

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
