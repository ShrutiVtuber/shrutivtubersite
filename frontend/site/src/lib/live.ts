/* Map the site backend's /live payload onto the LiveBadge contract.
 *
 * The badge has three states and the third one matters: 'unknown' is what the
 * design demands when the platform APIs could not be reached. It must never
 * claim live, and — the part that is easy to get wrong — it must never claim
 * OFFLINE either. A visitor told "offline" while she is streaming is a worse
 * failure than a visitor told the status could not be fetched.
 *
 * So this is fail-closed in both directions: no data at all, or every platform
 * erroring, both resolve to 'unknown'.
 */
import type { LiveStatus } from "./api";

export interface BadgeState {
  status: "live" | "offline" | "unknown";
  title?: string;
  href?: string;
}

export function badgeFrom(live: LiveStatus | null): BadgeState {
  if (!live || !Array.isArray(live.platforms) || live.platforms.length === 0) {
    return { status: "unknown" };
  }
  if (live.anyLive && live.primary) {
    return { status: "live", title: live.primary.title, href: live.primary.watchUrl };
  }
  // Every platform failed: we do not actually know she is offline.
  if (live.platforms.every((p) => p.error)) return { status: "unknown" };
  return { status: "offline" };
}
