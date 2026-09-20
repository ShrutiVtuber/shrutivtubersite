// SPDX-License-Identifier: AGPL-3.0-only
/**
 * The builds pages, as the 20 September boards draw them: the list, and the
 * editor with its sticky category chips, the pinned next goal, one category
 * open at a time and rows that expand when tapped. Every save comes back with
 * the whole build, and everything on the page redraws from it — the head's
 * sigil, the chips, the counts, the pinned goal, the rows.
 */
import { sigil, buildStates } from "./guides-sigil";
import { plate, PRESETS } from "./plate";

const esc = (v: unknown) => String(v ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
const csrf = () => document.cookie.split("; ").find((c) => c.startsWith("shruti_csrf="))?.split("=")[1] ?? "";
async function api(method: string, path: string, body?: unknown): Promise<{ ok: boolean; status: number; body: any }> {
  const r = await fetch(path, { method, headers: { "content-type": "application/json", "x-csrf-token": csrf() }, body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await r.text();
  let parsed: any = null;
  try { parsed = text ? JSON.parse(text) : null; } catch { parsed = text; }
  return { ok: r.ok, status: r.status, body: parsed };
}

/** The chosen theme: a tile radio on the new pages, a select on older ones. */
function chosenTheme(root: HTMLElement): string {
  return root.querySelector<HTMLInputElement>("input[data-theme]:checked")?.value || root.querySelector<HTMLSelectElement>("select[data-theme]")?.value || "almanac";
}

type Item = { id: string; label: string; kind: string; state: string; target: string; have?: number; want?: number; unit?: string };
type Cat = { id: string; name: string; met: number; total: number; ratio: number; partly?: number; items: Item[] };

export function mountBuild(root: HTMLElement): void {
  const words = JSON.parse(root.dataset.words || "{}");
  const hints: Record<string, string> = JSON.parse(root.dataset.hints || "{}");
  const id = root.dataset.build || "";
  let view: any = JSON.parse(root.dataset.view || "null");
  const $ = <T extends HTMLElement>(sel: string) => root.querySelector<T>(sel);
  const $$ = <T extends HTMLElement>(sel: string) => Array.from(root.querySelectorAll<T>(sel));
  const note = $("[data-note]");
  const tell = (t: string) => { if (note) { note.textContent = t; note.hidden = !t; } };
  const stateWord: Record<string, string> = { met: words.met, partial: words.partial, open: words.open };
  const dotState = (s: string) => (s === "met" ? "met" : s === "partial" ? "partly" : "notyet");
  const itemStates = (c: Cat) => c.items.map((it) => (it.state === "met" ? "d" : it.state === "partial" ? "n" : "o")).join("");
  const catState = (c: Cat) => (c.total > 0 && c.met === c.total ? "met" : c.met > 0 || (c.partly ?? 0) > 0 ? "partly" : "notyet");
  const fill = (t: string, vars: Record<string, string | number>) => Object.entries(vars).reduce((s, [k, v]) => s.replace(`{${k}}`, String(v)), t);

  /* The head: sigil, counts, the complete line, the chips. */
  const drawHead = () => {
    const p = view.progress; const cats: Cat[] = p.categories;
    const ring = $("[data-ring]");
    if (ring) ring.innerHTML = sigil({ n: Math.max(1, cats.length), states: buildStates(cats), size: 160, ring: true, label: `${p.met} / ${p.total}`, animate: false, aria: words.ringAria });
    const count = $("[data-count]"); if (count) count.textContent = fill(words.metOf, { met: p.met, total: p.total });
    const done = cats.filter((c) => c.total > 0 && c.met === c.total).length;
    const cc = $("[data-cats-complete]"); if (cc) cc.textContent = fill(words.catsComplete, { n: done, m: cats.length });
    const complete = $("[data-complete]"); if (complete) complete.hidden = !p.complete;
    const beside = $("[data-beside]"); if (beside) beside.hidden = p.complete || !view.runId;
    const total = $("[data-total]"); if (total) total.innerHTML = `${p.met} <span class="gd-faint">/ ${p.total}</span>`;
    for (const c of cats) {
      const chip = $(`[data-chip="${CSS.escape(c.id)}"]`); if (!chip) continue;
      chip.querySelector<HTMLElement>("[data-chip-count]")!.textContent = `${c.met}/${c.total}`;
      chip.querySelector<HTMLElement>(".gd-dot")?.setAttribute("data-state", catState(c));
      const section = $(`[data-cat="${CSS.escape(c.id)}"]`); if (!section) continue;
      const sg = section.querySelector<HTMLElement>("[data-cat-sigil]");
      if (sg) sg.innerHTML = sigil({ n: Math.max(1, c.items.length), states: itemStates(c), size: 28, ring: false, showCount: false, animate: false, aria: c.name });
      const cnt = section.querySelector<HTMLElement>("[data-cat-count]"); if (cnt) cnt.textContent = fill(words.catMet, { met: c.met, total: c.total });
    }
  };
  /* Every row (and the pinned card) from the view. */
  const drawItems = () => {
    for (const c of view.progress.categories as Cat[]) {
      for (const it of c.items) {
        for (const row of $$(`[data-item="${CSS.escape(it.id)}"]`)) {
          row.dataset.state = it.state;
          row.querySelector<HTMLElement>(".item-dot")?.setAttribute("data-state", dotState(it.state));
          const st = row.querySelector<HTMLElement>("[data-state-word]"); if (st) st.textContent = stateWord[it.state] ?? it.state;
          const have = row.querySelector<HTMLElement>("[data-have]"); if (have) have.textContent = String(it.have ?? 0);
          const wantText = row.querySelector<HTMLElement>("[data-want-text]"); if (wantText) wantText.textContent = String(it.want ?? 0);
          const want = row.querySelector<HTMLInputElement>("[data-want]"); if (want && document.activeElement !== want) want.value = String(it.want ?? 0);
          const target = row.querySelector<HTMLInputElement>("[data-target]"); if (target && document.activeElement !== target) target.value = it.target ?? "";
          const line = row.querySelector<HTMLElement>("[data-target-line]"); if (line) { line.textContent = it.target ?? ""; line.hidden = !it.target; }
          const met = row.querySelector<HTMLInputElement>("[data-met]"); if (met) met.checked = it.state === "met";
          const partial = row.querySelector<HTMLInputElement>("[data-partial]"); if (partial) partial.checked = it.state === "partial";
        }
      }
    }
  };
  /* The pinned card: the first goal not met, with its own controls. */
  const drawNext = () => {
    const card = $("[data-next]"); if (!card) return;
    let found: { c: Cat; it: Item } | null = null;
    for (const c of view.progress.categories as Cat[]) { const it = c.items.find((i) => i.state !== "met"); if (it) { found = { c, it }; break; } }
    if (!found) { card.innerHTML = view.progress.complete ? "" : `<span class="gd-eyebrow">${esc(words.next)}</span><h2>${esc(words.allMet)}</h2>`; return; }
    const { c, it } = found;
    const kind = words.kinds?.[it.kind] ?? it.kind;
    let controls = "";
    if (it.kind === "slot") {
      const hint = hints[it.id] ? fill(words.targetHint, { hint: hints[it.id] }) : "";
      controls = `<div class="sh-field"><label class="sh-f-label" for="next-target">${esc(words.target)}</label><input class="sh-f-ctrl" id="next-target" type="text" maxlength="120" value="${esc(it.target)}" placeholder="${esc(hints[it.id] || "")}" data-target />${hint ? `<span class="sh-f-hint">${esc(hint)}</span>` : ""}</div>` +
        `<div class="gd-ticks"><label class="gd-tick"><input type="checkbox" data-partial ${it.state === "partial" ? "checked" : ""}/> ${esc(words.partly)}</label><label class="gd-tick"><input type="checkbox" data-met ${it.state === "met" ? "checked" : ""}/> ${esc(words.onChar)}</label></div>`;
    } else if (it.kind === "counter") {
      controls = `<span class="gd-stepper"><button type="button" class="gd-step" data-step="-1" aria-label="${esc(words.less)}">−</button><span class="gd-have" data-have>${it.have ?? 0}</span><button type="button" class="gd-step" data-step="1" aria-label="${esc(words.more)}">+</button><span class="gd-faint">${esc(words.of)} <span data-want-text>${it.want ?? 0}</span> ${esc(it.unit ?? "")}</span></span>`;
    } else {
      controls = `<label class="gd-tick"><input type="checkbox" data-met ${it.state === "met" ? "checked" : ""}/> ${esc(words.done)}</label>`;
    }
    card.innerHTML = `<span class="gd-eyebrow">${esc(words.next)} · ${esc(c.name)} · ${esc(kind)}</span><h2>${esc(it.label)}</h2><div class="controls" data-item="${esc(it.id)}" data-item-state="${esc(it.state)}">${controls}</div>`;
  };
  const drawAll = () => { drawHead(); drawItems(); drawNext(); };

  const save = async (item: string, body: unknown) => {
    const r = await api("PUT", `/api/builds/${id}/goals/${encodeURIComponent(item)}`, body);
    if (!r.ok) { tell(words.failed); return; }
    view = r.body; tell(""); drawAll();
  };
  root.addEventListener("change", (ev) => {
    const el = ev.target as HTMLInputElement; const row = el.closest<HTMLElement>("[data-item]"); if (!row) return;
    const item = row.dataset.item!;
    if (el.matches("[data-met]")) save(item, { met: el.checked, partial: false });
    else if (el.matches("[data-partial]")) save(item, { partial: el.checked, met: false });
    else if (el.matches("[data-target]")) save(item, { target: el.value.trim() });
    else if (el.matches("[data-want]")) save(item, { want: Math.max(0, Math.floor(Number(el.value) || 0)) });
  });
  root.addEventListener("click", (ev) => {
    const t = ev.target as HTMLElement;
    const step = t.closest<HTMLButtonElement>("[data-step]");
    if (step) {
      const row = step.closest<HTMLElement>("[data-item]")!; const item = row.dataset.item!;
      const current = Number(row.querySelector("[data-have]")?.textContent || 0);
      save(item, { have: Math.max(0, current + Number(step.dataset.step)) });
      return;
    }
    /* One category open at a time; a chip opens its category and scrolls to it. */
    const chip = t.closest<HTMLButtonElement>("[data-chip]");
    const toggle = t.closest<HTMLButtonElement>("[data-cat-toggle]");
    if (chip || toggle) {
      const wanted = chip ? chip.dataset.chip! : toggle!.closest<HTMLElement>("[data-cat]")!.dataset.cat!;
      const section = $(`[data-cat="${CSS.escape(wanted)}"]`)!;
      const opening = chip ? true : section.dataset.open !== "true";
      for (const s of $$("[data-cat]")) { const on = opening && s.dataset.cat === wanted; s.dataset.open = String(on); s.querySelector("[data-cat-toggle]")?.setAttribute("aria-expanded", String(on)); }
      for (const c of $$("[data-chip]")) { const on = opening && c.dataset.chip === wanted; c.dataset.open = String(on); c.setAttribute("aria-selected", String(on)); }
      if (chip) section.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    /* A slot or counter row expands to its fields when tapped. */
    const expand = t.closest<HTMLButtonElement>("[data-expand]");
    if (expand) {
      const box = expand.closest<HTMLElement>("[data-item]")?.querySelector<HTMLElement>("[data-expanded]");
      if (box) { box.hidden = !box.hidden; expand.setAttribute("aria-expanded", String(!box.hidden)); if (!box.hidden) box.querySelector<HTMLInputElement>("input")?.focus(); }
    }
  });

  /* The overlay: minted once, the URL shown once. */
  $("[data-mint]")?.addEventListener("click", async () => {
    const theme = chosenTheme(root);
    const motion = $<HTMLSelectElement>("[data-motion]")?.value || "full";
    const r = await api("POST", `/api/builds/${id}/overlays`, { theme, motion, label: "" });
    if (!r.ok) { tell(r.body?.detail || words.failed); return; }
    const url = $<HTMLInputElement>("[data-url]"); if (url) url.value = `${location.origin}/overlay/build?t=${encodeURIComponent(r.body.token)}`;
    const box = $("[data-minted]"); if (box) box.hidden = false;
    const list = $("[data-tokens]");
    if (list) {
      const themeName = words.themes?.[theme] ?? theme; const motionName = words.motions?.[motion] ?? motion;
      const row = document.createElement("li"); row.className = "gd-token"; row.setAttribute("data-token-row", "");
      row.innerHTML = `${plate({ theme, elements: PRESETS.grid, width: 56, aria: themeName })}<span class="gd-token-text"><span class="gd-token-label">${esc(words.overlay)}</span><span class="gd-note">${esc(themeName)} · ${esc(motionName)} · ${esc(words.idle)}</span></span><button type="button" class="sh-btn" data-variant="ghost" data-size="sm" data-revoke="${r.body.id}"><span>${esc(words.revoke)}</span></button>`;
      list.appendChild(row); list.hidden = false;
    }
  });
  $("[data-copy]")?.addEventListener("click", async () => { const url = $<HTMLInputElement>("[data-url]"); if (!url) return; try { await navigator.clipboard.writeText(url.value); tell(words.copied); } catch { url.select(); } });
  $("[data-have-it]")?.addEventListener("click", () => { const box = $("[data-minted]"); const url = $<HTMLInputElement>("[data-url]"); if (url) url.value = ""; if (box) box.hidden = true; });
  $<HTMLSelectElement>("[data-run]")?.addEventListener("change", async (ev) => {
    const r = await api("PUT", `/api/builds/${id}`, { run_id: Number((ev.currentTarget as HTMLSelectElement).value) || 0 });
    if (r.ok) { view.runId = Number((ev.currentTarget as HTMLSelectElement).value) || null; drawHead(); }
    tell(r.ok ? words.saved : words.failed);
  });
  root.addEventListener("click", async (ev) => {
    const btn = (ev.target as HTMLElement).closest<HTMLButtonElement>("[data-revoke]"); if (!btn) return;
    const r = await fetch(`/api/builds/${id}/overlays/${btn.dataset.revoke}`, { method: "DELETE", headers: { "x-csrf-token": csrf() } });
    if (r.ok) { btn.closest("[data-token-row]")?.remove(); const list = $("[data-tokens]"); if (list && !list.querySelector("[data-token-row]")) list.hidden = true; } else tell(words.failed);
  });
  $("[data-delete]")?.addEventListener("click", async () => {
    if (!confirm(words.confirmDelete)) return;
    const r = await api("DELETE", `/api/builds/${id}`);
    if (r.ok) location.href = "/builds"; else tell(words.failed);
  });
  drawAll();
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
