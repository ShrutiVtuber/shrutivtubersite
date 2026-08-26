/* The service worker, and it does exactly two things.
 *
 * It is NOT an offline cache. Caching a server-rendered site whose whole point
 * is that content changes without a deploy would mean serving yesterday's sky
 * from disk, and a stale ephemeris is worse than no ephemeris. Every request
 * goes to the network, as it would with no worker at all.
 *
 * What it does:
 *   1. Wakes on a push and asks the site what the notice says. The push itself
 *      carries no payload — see backend/shruti/core/push.py for why — so this
 *      fetch is how the words arrive.
 *   2. Focuses an already-open tab when the notification is clicked, rather
 *      than opening a fourth copy of the same site.
 */

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

self.addEventListener("push", (event) => {
  event.waitUntil(
    (async () => {
      let notice = null;
      try {
        const r = await fetch("/api/community/push/notice", { cache: "no-store" });
        if (r.ok) notice = await r.json();
      } catch {
        /* Nothing to say and no way to find out. */
      }
      /* No notice, or a stale one, means show NOTHING. A browser waking an
         hour after a stream ended should not announce it. Some platforms
         insist a push shows something; on those this is the honest minimum. */
      if (!notice || !notice.title) return;

      await self.registration.showNotification(notice.title, {
        body: notice.body || "",
        icon: "/favicon-192.png",
        badge: "/favicon-32.png",
        tag: notice.kind || "shruti",
        renotify: false,
        data: { url: notice.url || "/" },
      });
    })(),
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = (event.notification.data && event.notification.data.url) || "/";
  event.waitUntil(
    (async () => {
      const open = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
      for (const client of open) {
        if (new URL(client.url).origin === self.location.origin) {
          await client.focus();
          if ("navigate" in client) await client.navigate(target);
          return;
        }
      }
      await self.clients.openWindow(target);
    })(),
  );
});
