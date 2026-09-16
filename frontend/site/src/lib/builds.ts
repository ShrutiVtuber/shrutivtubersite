/* A build's page: set a target, tick a slot, count up, mint the overlay.
 * Every word drawn here arrives as data (`data-words`). */
const csrf = () => document.cookie.split("; ").find((c) => c.startsWith("shruti_csrf="))?.split("=")[1] ?? "";
async function api(method: string, path: string, body?: unknown): Promise<{ ok: boolean; status: number; body: any }> {
  const r = await fetch(path, { method, headers: { "content-type": "application/json", "x-csrf-token": csrf() }, body: body === undefined ? undefined : JSON.stringify(body) });
  let out: any = null; try { out = await r.json(); } catch { /* no body */ }
  return { ok: r.ok, status: r.status, body: out };
}
const esc = (s: unknown) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

export function mountBuild(root: HTMLElement): void {
  const words = JSON.parse(root.dataset.words || "{}");
  const id = root.dataset.build || "";
  let view: any = JSON.parse(root.dataset.view || "null");
  const $ = <T extends HTMLElement>(sel: string) => root.querySelector<T>(sel);
  const note = $("[data-note]");
  const tell = (t: string) => { if (note) { note.textContent = t; note.hidden = !t; } };
  const stateWord: Record<string, string> = { met: words.met, partial: words.partial, open: words.open };

  const drawHead = () => {
    const p = view.progress;
    const count = $("[data-count]"); if (count) count.textContent = `${p.met} ${words.of} ${p.total}`;
    const partlyEl = $("[data-partly]"); if (partlyEl) partlyEl.textContent = p.partly ? `· ${p.partly} ${words.partial}` : "";
    const done = $("[data-complete]"); if (done) done.hidden = !p.complete;
    const cats = $("[data-cats]");
    if (cats) cats.innerHTML = p.categories.map((c: any) => `<a href="#cat-${esc(c.id)}" class="cat ${c.total && c.met === c.total ? "met" : c.ratio > 0 ? "partial" : ""}"><span>${esc(c.name)}</span><span class="mono">${c.met}/${c.total}</span></a>`).join("");
    const ring = $("[data-ring]");
    if (ring) ring.querySelectorAll<SVGPathElement>(".fill:not(.partly)").forEach((f, i) => { const c = p.categories[i]; if (!c) return; const pct = c.total ? c.met / c.total : 0; f.style.strokeDasharray = `${(pct * 100).toFixed(1)} 100`; f.style.opacity = pct <= 0.004 ? "0" : "1"; });
    if (ring) ring.querySelectorAll<SVGPathElement>(".fill.partly").forEach((f, i) => { const c = p.categories[i]; if (!c) return; const pct = c.total ? (c.met + (c.partly || 0)) / c.total : 0; f.style.strokeDasharray = `${(pct * 100).toFixed(1)} 100`; f.style.opacity = pct <= 0.004 ? "0" : "1"; });
  };
  const drawItems = () => {
    for (const c of view.progress.categories) {
      for (const it of c.items) {
        const row = root.querySelector<HTMLElement>(`[data-item="${it.id}"]`); if (!row) continue;
        row.dataset.state = it.state;
        const st = row.querySelector<HTMLElement>("[data-state]"); if (st) st.textContent = stateWord[it.state] ?? it.state;
        const have = row.querySelector<HTMLElement>("[data-have]"); if (have) have.textContent = String(it.have ?? 0);
        const want = row.querySelector<HTMLInputElement>("[data-want]"); if (want && document.activeElement !== want) want.value = String(it.want ?? 0);
        const met = row.querySelector<HTMLInputElement>("[data-met]"); if (met) met.checked = it.state === "met";
        const partial = row.querySelector<HTMLInputElement>("[data-partial]"); if (partial) partial.checked = it.state === "partial";
      }
    }
  };
  const save = async (item: string, body: unknown) => {
    const r = await api("PUT", `/api/builds/${id}/goals/${encodeURIComponent(item)}`, body);
    if (!r.ok) { tell(words.failed); return; }
    view = r.body; drawHead(); drawItems();
  };
  root.addEventListener("change", (ev) => {
    const el = ev.target as HTMLInputElement; const row = el.closest<HTMLElement>("[data-item]"); if (!row) return;
    const item = row.dataset.item!;
    if (el.matches("[data-met]")) save(item, { met: el.checked, partial: false });
    else if (el.matches("[data-partial]")) save(item, { partial: el.checked, met: false });
    else if (el.matches("[data-target]")) save(item, { target: el.value.trim() });
    else if (el.matches("[data-want]")) save(item, { want: Math.max(0, Math.floor(Number(el.value) || 0)) });
    else if (el.matches("[data-note-field]")) save(item, { note: el.value.trim() });
  });
  root.addEventListener("click", (ev) => {
    const btn = (ev.target as HTMLElement).closest<HTMLButtonElement>("[data-step]"); if (!btn) return;
    const row = btn.closest<HTMLElement>("[data-item]")!; const item = row.dataset.item!;
    const current = Number(row.querySelector("[data-have]")?.textContent || 0);
    save(item, { have: Math.max(0, current + Number(btn.dataset.step)) });
  });

  /* The overlay: minted once, the URL shown once. */
  $("[data-mint]")?.addEventListener("click", async () => {
    const theme = $<HTMLSelectElement>("[data-theme]")?.value || "almanac";
    const motion = $<HTMLSelectElement>("[data-motion]")?.value || "reduced";
    const r = await api("POST", `/api/builds/${id}/overlays`, { theme, motion, label: "" });
    if (!r.ok) { tell(r.body?.detail || words.failed); return; }
    const url = $<HTMLInputElement>("[data-url]"); if (url) url.value = `${location.origin}/overlay/build?t=${encodeURIComponent(r.body.token)}`;
    const box = $("[data-minted]"); if (box) box.hidden = false;
    const list = $("[data-tokens]");
    if (list) { const row = document.createElement("div"); row.className = "bd-token"; row.innerHTML = `<span>${esc(words.overlay)} · ${esc(theme)}</span><button type="button" class="link" data-revoke="${r.body.id}">${esc(words.revoke)}</button>`; list.appendChild(row); list.hidden = false; }
  });
  $("[data-copy]")?.addEventListener("click", async () => { const url = $<HTMLInputElement>("[data-url]"); if (!url) return; try { await navigator.clipboard.writeText(url.value); tell(words.copied); } catch { url.select(); } });
  $("[data-have-it]")?.addEventListener("click", () => { const box = $("[data-minted]"); const url = $<HTMLInputElement>("[data-url]"); if (url) url.value = ""; if (box) box.hidden = true; });
  $<HTMLSelectElement>("[data-run]")?.addEventListener("change", async (ev) => {
    const r = await api("PUT", `/api/builds/${id}`, { run_id: Number((ev.currentTarget as HTMLSelectElement).value) || 0 });
    tell(r.ok ? words.saved : words.failed);
  });
  root.addEventListener("click", async (ev) => {
    const btn = (ev.target as HTMLElement).closest<HTMLButtonElement>("[data-revoke]"); if (!btn) return;
    const r = await fetch(`/api/builds/${id}/overlays/${btn.dataset.revoke}`, { method: "DELETE", headers: { "x-csrf-token": csrf() } });
    if (r.ok) btn.closest(".bd-token")?.remove(); else tell(words.failed);
  });
  $("[data-delete]")?.addEventListener("click", async () => {
    if (!confirm(words.confirmDelete)) return;
    const r = await api("DELETE", `/api/builds/${id}`);
    if (r.ok) location.href = "/builds"; else tell(words.failed);
  });
  drawHead(); drawItems();
}

export function mountBuilds(root: HTMLElement): void {
  const words = JSON.parse(root.dataset.words || "{}");
  const $ = <T extends HTMLElement>(sel: string) => root.querySelector<T>(sel);
  const note = $("[data-note]");
  const tell = (t: string) => { if (note) { note.textContent = t; note.hidden = !t; } };
  $("[data-new-form]")?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const body = { template_id: Number($<HTMLSelectElement>("[data-template]")?.value || 0), name: ($<HTMLInputElement>("[data-name]")?.value || "").trim(), variant: ($<HTMLInputElement>("[data-variant]")?.value || "").trim(), run_id: Number($<HTMLSelectElement>("[data-run]")?.value || 0) || null };
    if (!body.name) { tell(words.needsName); return; }
    if (!body.template_id) { tell(words.needsTemplate); return; }
    const r = await api("POST", "/api/builds", body);
    if (r.ok) location.href = `/builds/${r.body.id}`; else tell(r.body?.detail || words.failed);
  });
}
