/* A group's page: join, contribute one number, mint the goal overlay.
 *
 * Every word drawn here arrives as data (`data-words`), so the page's copy
 * stays editable from the admin. Nothing here ranks anyone: the server
 * lists the crew by size with "and N others" and this script only draws it.
 */
const csrf = () => document.cookie.split("; ").find((c) => c.startsWith("shruti_csrf="))?.split("=")[1] ?? "";

async function api(method: string, path: string, body?: unknown): Promise<{ ok: boolean; status: number; body: any }> {
  const r = await fetch(path, {
    method,
    headers: { "content-type": "application/json", "x-csrf-token": csrf() },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  let out: any = null;
  try { out = await r.json(); } catch { /* no body */ }
  return { ok: r.ok, status: r.status, body: out };
}

import { plate } from "./plate";
const esc = (v: string) => String(v).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

/** The chosen theme: a tile radio on the new pages, a select on older ones. */
export function chosenTheme(root: HTMLElement): string {
  return root.querySelector<HTMLInputElement>("input[data-theme]:checked")?.value || root.querySelector<HTMLSelectElement>("select[data-theme]")?.value || "almanac";
}

export function mountGroup(root: HTMLElement): void {
  const words = JSON.parse(root.dataset.words || "{}");
  const code = root.dataset.code || "";
  const $ = <T extends HTMLElement>(sel: string) => root.querySelector<T>(sel);
  const note = $("[data-note]");
  const tell = (text: string) => { if (note) { note.textContent = text; note.hidden = !text; } };

  $("[data-join]")?.addEventListener("click", async () => {
    const r = await api("POST", `/api/groups/${code}/join`);
    if (r.ok) window.location.reload(); else tell(r.status === 409 ? words.closed : words.failed);
  });
  $("[data-leave]")?.addEventListener("click", async () => {
    const r = await api("POST", `/api/groups/${code}/leave`);
    if (r.ok) window.location.reload(); else tell(words.failed);
  });
  $("[data-close]")?.addEventListener("click", async (ev) => {
    const btn = ev.currentTarget as HTMLButtonElement;
    const r = await api("POST", `/api/groups/${code}/close`, { closed: btn.dataset.close === "1" });
    if (r.ok) window.location.reload(); else tell(words.failed);
  });

  const amount = $<HTMLInputElement>("[data-amount]");
  const step = (d: number) => { if (!amount) return; amount.value = String(Math.max(1, (Number(amount.value) || 0) + d)); };
  $("[data-less]")?.addEventListener("click", () => step(-1));
  $("[data-more]")?.addEventListener("click", () => step(1));
  $("[data-contribute]")?.addEventListener("click", async () => {
    const n = Math.floor(Number(amount?.value || 0));
    if (!n || n < 1) { tell(words.oneNumber); return; }
    const r = await api("POST", `/api/groups/${code}/contribute`, { amount: n });
    if (r.ok) window.location.reload(); else tell(r.status === 409 ? words.closed : words.failed);
  });

  /* The goal overlay: minted once, the URL shown once. */
  const minted = $("[data-minted]");
  const url = $<HTMLInputElement>("[data-url]");
  $("[data-mint]")?.addEventListener("click", async () => {
    const theme = chosenTheme(root);
    const motion = ($<HTMLSelectElement>("[data-motion]")?.value) || "reduced";
    const r = await api("POST", `/api/groups/${code}/overlays`, { theme, motion, label: "" });
    if (!r.ok) { tell(r.status === 403 ? words.joinFirst : words.failed); return; }
    if (url) url.value = `${window.location.origin}/overlay/guide-goal?t=${encodeURIComponent(r.body.token)}`;
    if (minted) minted.hidden = false;
    const list = $("[data-tokens]");
    if (list) {
      /* A new token row, in the same shape as the server-rendered ones. */
      const row = document.createElement("li");
      row.className = "gd-token"; row.setAttribute("data-token-row", "");
      const themeName = words.themes?.[theme] ?? theme; const motionName = words.motions?.[motion] ?? motion;
      row.innerHTML = `${plate({ theme, elements: [{ kind: "guide-sigil", x: 860, y: 300, w: 200, h: 200 }, { kind: "guide-goal", x: 560, y: 560, w: 800, h: 120 }], width: 56, aria: themeName })}<span class="gd-token-text"><span class="gd-token-label">${esc(words.goalOverlay)}</span><span class="gd-note">${esc(themeName)} · ${esc(motionName)} · ${esc(words.idle)}</span></span><button type="button" class="sh-btn" data-variant="ghost" data-size="sm" data-revoke="${r.body.id}"><span>${esc(words.revoke)}</span></button>`;
      list.appendChild(row);
      list.hidden = false;
    }
  });
  $("[data-have-it]")?.addEventListener("click", () => { if (url) url.value = ""; if (minted) minted.hidden = true; });
  $("[data-copy]")?.addEventListener("click", async () => {
    if (!url) return;
    try { await navigator.clipboard.writeText(url.value); tell(words.copied); } catch { url.select(); }
  });
  root.addEventListener("click", async (ev) => {
    const btn = (ev.target as HTMLElement).closest<HTMLButtonElement>("[data-revoke]");
    if (!btn) return;
    const r = await fetch(`/api/groups/${code}/overlays/${btn.dataset.revoke}`, { method: "DELETE", headers: { "x-csrf-token": csrf() } });
    if (r.ok) { btn.closest("[data-token-row]")?.remove(); const list = $("[data-tokens]"); if (list && !list.querySelector("[data-token-row]")) list.hidden = true; } else tell(words.failed);
  });
}

export function mountGroups(root: HTMLElement): void {
  const words = JSON.parse(root.dataset.words || "{}");
  const $ = <T extends HTMLElement>(sel: string) => root.querySelector<T>(sel);
  const note = $("[data-note]");
  const tell = (text: string) => { if (note) { note.textContent = text; note.hidden = !text; } };

  $("[data-join-form]")?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const code = ($<HTMLInputElement>("[data-join-code]")?.value || "").trim().toUpperCase();
    if (!/^[A-Z]{6}$/.test(code)) { tell(words.sixLetters); return; }
    const r = await api("POST", `/api/groups/${code}/join`);
    if (r.ok) window.location.href = `/groups/${code}`;
    else tell(r.status === 404 ? words.noSuchGroup : r.status === 409 ? words.closed : words.failed);
  });
  $("[data-start-form]")?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const body = {
      name: ($<HTMLInputElement>("[data-name]")?.value || "").trim(),
      goal: ($<HTMLInputElement>("[data-goal]")?.value || "").trim(),
      target: Math.max(0, Math.floor(Number($<HTMLInputElement>("[data-target]")?.value || 0))),
      tiers: Math.max(1, Math.min(12, Math.floor(Number($<HTMLInputElement>("[data-tiers]")?.value || 5)))),
    };
    if (!body.name) { tell(words.needsName); return; }
    const r = await api("POST", "/api/groups", body);
    if (r.ok) window.location.href = `/groups/${r.body.code}`; else tell(words.failed);
  });
}
