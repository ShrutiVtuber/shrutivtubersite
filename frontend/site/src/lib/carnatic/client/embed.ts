/* Third-party players, loaded only when the visitor presses the button (hard
 * rule 7): YouTube (privacy-enhanced domain), Vimeo, SoundCloud; Bandcamp
 * opens on its own site. Nothing from a provider loads before the press.
 *
 * For YouTube the player is also driven over postMessage (no script from
 * YouTube is loaded into the page): seek to a time, and read the current
 * time for timestamps and tapping along with a beat map.
 */

export interface PlayerOpts { start?: number | null; end?: number | null; autoplay?: boolean }

export function embedUrl(provider: string, url: string, o: PlayerOpts = {}): string | null {
  try {
    const u = new URL(url);
    const start = o.start ? Math.floor(o.start) : null;
    if (provider === "youtube") {
      const id = u.hostname === "youtu.be" ? u.pathname.slice(1) : u.searchParams.get("v") ?? u.pathname.split("/").pop();
      if (!id) return null;
      const q = new URLSearchParams({ autoplay: o.autoplay === false ? "0" : "1", enablejsapi: "1", rel: "0",
        origin: location.origin, ...(start ? { start: String(start) } : {}), ...(o.end ? { end: String(Math.floor(o.end)) } : {}) });
      return `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}?${q}`;
    }
    if (provider === "vimeo") {
      const id = u.pathname.split("/").filter(Boolean).pop();
      return id ? `https://player.vimeo.com/video/${encodeURIComponent(id)}?autoplay=${o.autoplay === false ? 0 : 1}${start ? `#t=${start}s` : ""}` : null;
    }
    if (provider === "soundcloud") return `https://w.soundcloud.com/player/?url=${encodeURIComponent(url)}&auto_play=${o.autoplay === false ? "false" : "true"}`;
  } catch {
    /* not a URL */
  }
  return null;
}

export interface Player {
  frame: HTMLIFrameElement | null;
  /** Seconds, or null when the provider doesn't tell us. */
  time(): number | null;
  seek(seconds: number): void;
  onTime(fn: (t: number) => void): void;
}

/** Replace `box`'s contents with the player. Bandcamp and unknown links open in a new tab. */
export function loadPlayer(box: HTMLElement, provider: string, url: string, o: PlayerOpts = {}): Player {
  const src = embedUrl(provider, url, o);
  let current: number | null = null;
  const listeners = new Set<(t: number) => void>();
  if (!src) {
    window.open(url, "_blank", "noopener");
    return { frame: null, time: () => null, seek: () => window.open(url, "_blank", "noopener"), onTime: () => {} };
  }
  const f = document.createElement("iframe");
  f.src = src;
  f.allow = "autoplay; encrypted-media; fullscreen";
  f.title = "Player";
  f.className = "lr-frame";
  box.replaceChildren(f);
  if (provider === "youtube") {
    const hello = () => f.contentWindow?.postMessage(JSON.stringify({ event: "listening", id: 1 }), "*");
    f.addEventListener("load", () => { hello(); setTimeout(hello, 800); });
    window.addEventListener("message", (e) => {
      if (e.source !== f.contentWindow) return;
      try {
        const d = typeof e.data === "string" ? JSON.parse(e.data) : e.data;
        const t = d?.info?.currentTime;
        if (typeof t === "number") {
          current = t;
          listeners.forEach((fn) => fn(t));
        }
      } catch {
        /* not ours */
      }
    });
  }
  return {
    frame: f,
    time: () => current,
    seek(seconds: number) {
      if (provider === "youtube") {
        f.contentWindow?.postMessage(JSON.stringify({ event: "command", func: "seekTo", args: [seconds, true] }), "*");
        f.contentWindow?.postMessage(JSON.stringify({ event: "command", func: "playVideo", args: [] }), "*");
      } else {
        f.src = embedUrl(provider, url, { ...o, start: seconds }) ?? f.src;
      }
    },
    onTime(fn) { listeners.add(fn); },
  };
}

export const PROVIDER_NAME: Record<string, string> = {
  youtube: "YouTube", vimeo: "Vimeo", soundcloud: "SoundCloud", bandcamp: "Bandcamp", archive: "the Internet Archive",
};
