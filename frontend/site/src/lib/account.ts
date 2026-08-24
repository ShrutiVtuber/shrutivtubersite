/* Reader-account access from the server side of a page render.
 *
 * The reader's session cookie has to be forwarded deliberately: the site
 * fetches the backend over the internal network, so nothing is carried unless
 * it is passed on. Forwarding only this one cookie, rather than the whole
 * header, keeps the CSRF cookie out of the backend's sight — it has no
 * business there.
 */
import { SITE_API } from "./api";

export const READER_COOKIE = "shruti_reader";

export interface Account {
  email: string;
  displayName: string;
  timezone: string;
  readingLanguage: string;
  preferredTradition: string;
  houseSystem: string;
  ayanamsa: string;
  nativity: {
    label: string; birthDate: string; birthTime: string | null;
    timeUnknown: boolean; placeName: string; lat: number; lon: number;
    elevation: number; timezone: string; utcOffsetMinutes: number | null;
  } | null;
  consents: {
    kind: string; granted: boolean; version: string;
    givenAt: string | null; lawfulBasis: string; source: string;
  }[];
  newsletter: { subscribed: boolean; pending: boolean; cadence: string | null };
}

function headers(astro: any) {
  const out: Record<string, string> = {};
  const token = astro.cookies?.get(READER_COOKIE)?.value;
  if (token) out.cookie = `${READER_COOKIE}=${token}`;

  /* Forward the BROWSER'S origin, not this server's.
   *
   * These calls run in Node, so without this the backend sees a request with
   * no Origin at all and falls back to the configured site. Everything that
   * only reads was fine with that; the moment one of these calls decided
   * where to send somebody AFTER a payment, it stopped being fine — a
   * checkout started on a laptop handed Stripe a cancel URL pointing at
   * shrutivtuber.com, which before cutover is the old WordPress site.
   *
   * The backend still only ever matches this against its own allowlist, so
   * forwarding it hands over nothing a header could abuse. */
  const origin = astro.request?.headers?.get("origin");
  if (origin) out.origin = origin;
  const referer = astro.request?.headers?.get("referer");
  if (referer) out.referer = referer;

  return out;
}

export async function account(astro: any): Promise<Account | null> {
  try {
    const r = await fetch(`${SITE_API}/api/account/me`, { headers: headers(astro) });
    if (!r.ok) return null;
    return (await r.json()) as Account;
  } catch {
    return null;
  }
}

/** Call a signed-in endpoint, forwarding the reader's session. */
export async function asReader(
  astro: any, path: string, init: RequestInit = {},
): Promise<{ ok: boolean; status: number; body: any }> {
  try {
    const r = await fetch(`${SITE_API}${path}`, {
      ...init,
      headers: { ...(init.headers ?? {}), ...headers(astro) },
    });
    const body = await r.json().catch(() => null);
    return { ok: r.ok, status: r.status, body };
  } catch {
    return { ok: false, status: 0, body: null };
  }
}
