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
    const theme = ($<HTMLSelectElement>("[data-theme]")?.value) || "almanac";
    const motion = ($<HTMLSelectElement>("[data-motion]")?.value) || "reduced";
    const r = await api("POST", `/api/groups/${code}/overlays`, { theme, motion, label: "" });
    if (!r.ok) { tell(r.status === 403 ? words.joinFirst : words.failed); return; }
    if (url) url.value = `${window.location.origin}/overlay/guide-goal?t=${encodeURIComponent(r.body.token)}`;
    if (minted) minted.hidden = false;
    const list = $("[data-tokens]");
    if (list) {
      const row = document.createElement("div");
      row.className = "gp-token";
      row.innerHTML = `<span>${words.goalOverlay} · ${theme}</span><button type="button" class="link" data-revoke="${r.body.id}">${words.revoke}</button>`;
      list.appendChild(row);
      list.hidden = false;
    }
  });
  $("[data-copy]")?.addEventListener("click", async () => {
    if (!url) return;
    try { await navigator.clipboard.writeText(url.value); tell(words.copied); } catch { url.select(); }
  });
  root.addEventListener("click", async (ev) => {
    const btn = (ev.target as HTMLElement).closest<HTMLButtonElement>("[data-revoke]");
    if (!btn) return;
    const r = await fetch(`/api/groups/${code}/overlays/${btn.dataset.revoke}`, { method: "DELETE", headers: { "x-csrf-token": csrf() } });
    if (r.ok) btn.closest(".gp-token")?.remove(); else tell(words.failed);
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
