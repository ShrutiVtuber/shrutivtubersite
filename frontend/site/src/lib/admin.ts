/* Admin access from a page render.
 *
 * The admin session cookie has to be forwarded deliberately, like the reader
 * one: the site talks to the backend over the internal network and carries
 * nothing it is not told to. Only this cookie goes — the CSRF cookie has no
 * business at the backend.
 */
import { SITE_API } from "./api";

export const ADMIN_COOKIE = "shruti_session";

export interface AdminCall {
  ok: boolean;
  status: number;
  body: any;
  /** The raw response, for when a Set-Cookie needs forwarding. */
  raw: Response | null;
}

function headers(astro: any): Record<string, string> {
  const token = astro.cookies.get(ADMIN_COOKIE)?.value;
  return token ? { cookie: `${ADMIN_COOKIE}=${token}` } : {};
}

export async function asAdmin(
  astro: any, path: string, init: RequestInit = {},
): Promise<AdminCall> {
  try {
    const r = await fetch(`${SITE_API}${path}`, {
      ...init,
      headers: { ...(init.headers ?? {}), ...headers(astro) },
    });
    const body = await r.json().catch(() => null);
    return { ok: r.ok, status: r.status, body, raw: r };
  } catch {
    return { ok: false, status: 0, body: null, raw: null };
  }
}

/** True when the request carries a valid admin session. */
export async function signedIn(astro: any): Promise<boolean> {
  const r = await asAdmin(astro, "/api/admin/me");
  return r.ok;
}

/** Every table the admin may edit, and how to talk about it. */
export const KINDS = [
  { kind: "sections", label: "Page blocks", singular: "block" },
  { kind: "projects", label: "Projects", singular: "project" },
  { kind: "links", label: "Links", singular: "link" },
  { kind: "profile-fields", label: "Profile fields", singular: "field" },
  { kind: "credits", label: "Credits", singular: "credit" },
  { kind: "schedule", label: "Schedule", singular: "stream" },
  { kind: "fan-art", label: "Fan works", singular: "piece" },
  { kind: "tools", label: "Tools", singular: "tool" },
] as const;
