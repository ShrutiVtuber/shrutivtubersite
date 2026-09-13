/* The track view: app screens 10–21 as one web page (board W4).
 *
 * One step is the page; Done is the largest thing on it; Too much replaces
 * the whole page. The path sits beside Now — and, her decision, the person
 * can fold it away; the choice is remembered in this browser.
 *
 * Everything a person does goes to the runs API and the answer redraws the
 * page: the server computes states with the shared engine, so nothing here
 * decides what is current. This file only draws, and plays the one motion
 * the product has.
 *
 * ⚠ No English lives here. Every word comes from the page's copy() as W.
 * ⚠ Nothing measures absence: no streaks, no counts of days, no "you missed".
 */
import {
  type Gate, type GuideDoc, type Step, fill, gateWords, optionLabel, phasesOf, safeUrl, stepsOf,
} from "./guides";

type View = any;
type Words = any;

export function mountTrack(root: HTMLElement) {
  const W: Words = JSON.parse(root.dataset.words || "{}");
  const doc: GuideDoc = JSON.parse(root.dataset.doc || "{}");
  let view: View = JSON.parse(root.dataset.run || "null");
  const gateShort = W.gate.short;
  const gateLong = W.gate.words;
  const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const esc = (s: unknown) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  const $ = <T extends HTMLElement>(sel: string) => root.querySelector<T>(sel);
  const token = () => document.cookie.split("; ").find((c) => c.startsWith("shruti_csrf="))?.split("=")[1] ?? "";
  const lowered = (): GuideDoc => ({ ...doc, checkin: (doc.checkin ?? []).map((f) => ({ ...f, label: (f.label || f.id).toLowerCase() })) });
  const words = (g: Gate | undefined, vocab: any) => gateWords(g, lowered(), vocab);

  /* ── the API ─────────────────────────────────────────────────────────── */
  let busy = false;
  const errorBar = $("[data-error]")!;
  let lastAction: (() => Promise<void>) | null = null;
  const call = async (method: string, path: string, body?: unknown): Promise<View | null> => {
    try {
      const r = await fetch(path, { method, headers: { "content-type": "application/json", "x-csrf-token": token() }, body: body === undefined ? undefined : JSON.stringify(body) });
      if (r.status === 401) { errorBar.hidden = false; errorBar.querySelector("[data-error-text]")!.textContent = W.error.signedOut; return null; }
      if (!r.ok) { errorBar.hidden = false; errorBar.querySelector("[data-error-text]")!.textContent = W.error.noAnswer; return null; }
      errorBar.hidden = true;
      return await r.json();
    } catch {
      errorBar.hidden = false; errorBar.querySelector("[data-error-text]")!.textContent = W.error.noAnswer;
      return null;
    }
  };
  const act = async (fn: () => Promise<View | null>) => {
    if (busy) return; busy = true;
    lastAction = async () => { const v = await fn(); if (v) { view = v; draw(); } };
    try { await lastAction(); } finally { busy = false; }
  };
  $("[data-retry]")?.addEventListener("click", () => { if (lastAction) act(async () => { await lastAction!(); return null; }); });

  /* ── the guide, indexed ──────────────────────────────────────────────── */
  const phases = phasesOf(doc);
  const pathPhases = phases.filter((p) => !p.track);
  const stepsById = new Map((doc.steps ?? []).map((s) => [s.id, s]));
  const phaseOf = (s: Step) => phases.find((p) => p.id === s.phase);
  const pathOrder = pathPhases.flatMap((p) => stepsOf(doc, p));
  const applies = (s: { applies_to?: string[] }) => !s.applies_to || s.applies_to.length === 0 || s.applies_to.includes(view.variant);
  const state = (id: string): string => view.progress.states[id] ?? "locked";
  const isVideo = (l: any) => l.type === "video" || /youtube\.com|youtu\.be|twitch\.tv|vimeo\.com/i.test(String(l.url ?? ""));
  const linksOf = (s: Step) => (view.linkOverrides?.[s.id] ?? s.links ?? []) as any[];
  const codexById = new Map((doc.codex ?? []).map((c) => [c.id, c]));
  const checkinSummary = () => (doc.checkin ?? []).filter((f) => view.checkinShown?.[f.id] && view.checkin[f.id] !== undefined)
    .map((f) => f.type === "number" ? `${(f.label || f.id).toLowerCase()} ${view.checkin[f.id]}` : optionLabel(f, String(view.checkin[f.id])))
    .concat(view.variant ? [doc.game.variants?.find((v) => v.id === view.variant)?.name ?? view.variant] : []).join(", ");

  /* ── the sigil ───────────────────────────────────────────────────────── */
  const arcD = (r: number, a0: number, a1: number) => {
    const R = (d: number) => ((d - 90) * Math.PI) / 180;
    const x0 = 50 + r * Math.cos(R(a0)), y0 = 50 + r * Math.sin(R(a0)), x1 = 50 + r * Math.cos(R(a1)), y1 = 50 + r * Math.sin(R(a1));
    return `M ${x0.toFixed(2)} ${y0.toFixed(2)} A ${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`;
  };
  const sigil = (parts: { pct: number; state: string }[], size: number, label: string) => {
    const n = Math.max(1, parts.length), gap = Math.max(2, Math.min(8, 24 / n)), span = 360 / n;
    const w = size < 48 ? 9 : 6, r = 50 - w / 2 - 1;
    let out = "";
    parts.forEach((p, i) => {
      const a0 = i * span + gap / 2, a1 = (i + 1) * span - gap / 2;
      out += `<path d="${arcD(r, a0, a1)}" fill="none" stroke="var(--ink-faint)" stroke-opacity=".3" stroke-width="${w}"/>`;
      const pct = Math.max(0, Math.min(1, p.pct || 0));
      out += `<path class="sg-fill" pathLength="100" d="${arcD(r, a0, a1)}" fill="none" stroke="${p.state === "done" ? "var(--rose)" : "var(--accent)"}" stroke-width="${w}" style="stroke-dasharray:${(pct * 100).toFixed(1)} 100${pct <= 0.004 ? ";opacity:0" : ""}"/>`;
    });
    return `<div class="sg" style="width:${size}px;height:${size}px"><svg viewBox="0 0 100 100" width="${size}" height="${size}" aria-hidden="true">${out}</svg>${label && size >= 48 ? `<span class="sg-label" style="font-size:${Math.round(size * 0.17)}px">${esc(label)}</span>` : ""}</div>`;
  };

  /* ── drawing ─────────────────────────────────────────────────────────── */
  const collapsedKey = "shruti.guides.path";
  let collapsed = false;
  try { collapsed = localStorage.getItem(collapsedKey) === "1"; } catch { collapsed = false; }

  const drawHead = () => {
    const cur = view.progress.current ? stepsById.get(view.progress.current) : null;
    const phase = cur ? phaseOf(cur) : null;
    const parts = view.progress.sigil ?? [];
    const idx = phase ? pathPhases.indexOf(phase) : -1;
    const [d, n] = phase ? (view.progress.phaseCounts[phase.id] ?? [0, 0]) : [0, 0];
    $("[data-sigil]")!.innerHTML = sigil(parts, 104, idx >= 0 ? `${idx + 1}/${pathPhases.length}` : "");
    $("[data-phase-eyebrow]")!.textContent = phase ? fill(W.head.phase, { n: String(idx + 1), of: String(pathPhases.length) }) : "";
    $("[data-phase-name]")!.textContent = phase ? phase.name : W.head.finished;
    $("[data-phase-meta]")!.textContent = phase ? [fill(W.head.steps, { d: String(d), n: String(n) }), phase.band ? phase.band : "", checkinSummary()].filter(Boolean).join(" · ") : "";
    const re = $("[data-reentry]")!;
    if (view.reentry && !reentryDismissed) {
      re.hidden = false;
      re.innerHTML = `<span class="tk-eyebrow rose">${esc(W.reentry.last)} · ${esc(view.reentry.when)}</span>` +
        `<p class="tk-re-line">${esc(W.reentry.finished)} <b>${esc(view.reentry.lastDone.title)}</b>.</p>` +
        (view.reentry.note ? `<p class="tk-re-note">${esc(view.reentry.note)}</p>` : "") +
        (view.reentry.next ? `<p class="tk-mono">${esc(W.reentry.next)} ${esc(view.reentry.next.title)}</p>` : "");
    } else re.hidden = true;
    const stale = $("[data-stale]")!; stale.hidden = !view.stale;
  };
  let reentryDismissed = false;

  const nowHtml = (s: Step | null) => {
    if (!s) {
      const total = pathOrder.length, done = pathOrder.filter((x) => state(x.id) === "done").length;
      const allGated = pathOrder.some((x) => ["locked"].includes(state(x.id))) && done < total;
      return `<div class="tk-now empty"><p class="tk-empty">${esc(allGated ? fill(W.now.allGated, { summary: checkinSummary() || W.now.noCheckin }) : W.now.finished)}</p></div>`;
    }
    const phase = phaseOf(s)!; const here = stepsOf(doc, phase); const pos = here.indexOf(s) + 1;
    const links = linksOf(s); const video = links.find(isVideo);
    const entry = s.codex ? codexById.get(s.codex) : undefined;
    return `<div class="tk-now" data-now-card data-step="${esc(s.id)}">
      <span class="tk-eyebrow">${esc(phase.name)} · ${esc(fill(W.now.stepOf, { n: String(pos), of: String(here.length) }))}</span>
      <h2 class="tk-now-title">${esc(s.title)}</h2>
      ${s.do ? `<p class="tk-now-do">${esc(s.do)}</p>` : ""}
      <div class="tk-now-meta">${s.ongoing ? `<span class="tk-mono">${esc(W.step.ongoing)}</span>` : s.minutes ? `<span class="tk-mono">${esc(s.minutes)} ${esc(W.step.min)}</span>` : ""}${video && safeUrl(video.url) ? `<a class="tk-pill" href="${esc(safeUrl(video.url))}" target="_blank" rel="nofollow noopener"><span class="tk-play"><span></span></span><span class="tk-mono accent">${esc(video.label || W.step.video)}</span></a>` : ""}</div>
      <div class="tk-now-more" hidden>
        ${s.done_when ? `<p class="tk-line"><b>${esc(W.step.done)} · </b>${esc(s.done_when)}</p>` : ""}
        ${s.why ? `<p class="tk-why">${esc(s.why)}</p>` : ""}
        ${links.length ? `<div class="tk-links">${links.map((l: any) => safeUrl(l.url) ? `<a class="tk-pill" href="${esc(safeUrl(l.url))}" target="_blank" rel="nofollow noopener">${isVideo(l) ? `<span class="tk-play"><span></span></span>` : `<span class="tk-mono">↗</span>`}<span>${esc(l.label || l.url)}</span></a>` : "").join("")}</div>` : ""}
        ${entry ? `<div class="tk-codex-rule"><span class="tk-eyebrow rose">${esc(W.step.codex)}</span><span>${esc(entry.name)}${entry.what ? " — " + esc(entry.what) : ""}</span></div>` : ""}
        <div class="tk-now-more-acts"><button type="button" class="tk-ghost" data-skip>${esc(W.now.skip)}</button></div>
      </div>
      <div class="tk-now-acts">
        <button type="button" class="tk-done" data-done>${esc(W.now.done)}</button>
        <button type="button" class="tk-secondary" data-later>${esc(W.now.later)}</button>
        <button type="button" class="tk-ghost" data-more aria-expanded="false">${esc(W.now.more)}</button>
      </div>
    </div>`;
  };
  const drawNow = () => { const cur = view.progress.current ? stepsById.get(view.progress.current) ?? null : null; $("[data-now]")!.innerHTML = nowHtml(cur); };

  const drawLater = () => {
    const el = $("[data-later]")!; const items: any[] = view.later ?? [];
    el.innerHTML = `<div class="tk-sec-head"><span class="tk-eyebrow">${esc(W.later.title)}</span><span class="tk-mono">${items.length ? fill(W.later.parked, { n: String(items.length) }) : ""}</span></div>` +
      (items.length ? items.map((it, i) => `<div class="tk-row"><span class="tk-row-text">${esc(it.text)}</span><span class="tk-leader"></span><span class="tk-mono ${it.step ? "accent" : ""}">${esc(it.step ? fill(W.later.from, { id: it.step }) : dayWord(it.at))}</span><button type="button" class="tk-x" data-unpark="${i}" aria-label="${esc(W.later.remove)}">✕</button></div>`).join("")
        : `<p class="tk-quiet">${esc(W.later.empty)}</p>`) +
      `<form class="tk-park" data-park><input type="text" name="text" maxlength="280" placeholder="${esc(W.later.hint)}" /><button type="submit" class="tk-secondary sm">${esc(W.later.add)}</button></form>`;
  };
  const dayWord = (iso: string) => { try { return new Date(iso).toLocaleDateString(undefined, { weekday: "long" }); } catch { return ""; } };

  const dot = (st: string) => st === "done" ? `<span class="dot dash rose"></span>` : st === "skipped" || st === "later" ? `<span class="dot dash faint"></span>`
    : st === "current" ? `<span class="dot disc"></span>` : st === "available" ? `<span class="dot ring"></span>` : `<span class="dot hollow"></span>`;
  const rowRight = (s: Step, st: string) => {
    if (st === "skipped") return W.path.skipped;
    if (st === "later") return W.path.later;
    if (st === "locked") { const g = words(s.gate, gateShort); return g.length ? g.join(" · ") : (applies(s) ? "" : W.path.notThisRun); }
    if (s.kind === "optional") return W.path.optional;
    return "";
  };
  const drawPath = () => {
    const el = $("[data-path]")!;
    const done = pathOrder.filter((x) => state(x.id) === "done").length;
    let html = `<div class="tk-sec-head"><span class="tk-eyebrow">${esc(W.path.title)}</span><span class="tk-mono">${done} / ${pathOrder.length}</span><button type="button" class="tk-fold" data-fold>${esc(collapsed ? W.path.show : W.path.hide)}</button></div>`;
    if (!collapsed) {
      html += `<div class="tk-path">` + pathPhases.map((p) => {
        const [d, n] = view.progress.phaseCounts[p.id] ?? [0, 0];
        const cur = view.progress.current ? phaseOf(stepsById.get(view.progress.current)!)?.id === p.id : false;
        return `<div class="tk-ph ${cur ? "now" : d === n && n > 0 ? "done" : ""}"><span class="tk-ph-name">${esc(p.name)}</span><span class="tk-mono">${d} / ${n}</span></div>` +
          stepsOf(doc, p).map((s) => { const st = state(s.id); return `<div class="tk-step ${st}" data-row="${esc(s.id)}">${dot(st)}<span class="tk-step-title">${esc(s.title)}</span><span class="tk-mono">${esc(rowRight(s, st))}</span></div><div class="tk-row-menu" data-menu="${esc(s.id)}" hidden></div>`; }).join("");
      }).join("") + `</div>`;
      const orphaned = Object.entries(view.progress.orphaned ?? {});
      if (orphaned.length) html += `<div class="tk-ph faint"><span class="tk-ph-name">${esc(W.path.gone)}</span></div>` + orphaned.map(([id, st]) => `<div class="tk-step ${st} faint"><span class="dot dash faint"></span><span class="tk-step-title">${esc(id)}</span><span class="tk-mono">${esc(st === "done" ? W.path.done : String(st))}</span></div>`).join("");
    }
    el.innerHTML = html;
  };

  const drawAlso = () => {
    const el = $("[data-also]")!;
    const routinesOpen = Object.values(view.progress.routines ?? {}).filter(Boolean).length;
    const codexActive = Object.values(view.progress.codex ?? {}).filter((s) => s === "active").length;
    const rows = [
      (doc.routines ?? []).length ? [W.also.routines, "#routines", fill(W.also.open, { n: String(routinesOpen) })] : null,
      (doc.codex ?? []).length ? [W.also.codex, "#codex", `${codexActive} ${W.also.of} ${(doc.codex ?? []).length}`] : null,
      ...(doc.tracks ?? []).map((t) => [t.name, `#track-${t.id}`, fill(W.also.rank, { n: String(view.tracks?.[t.id]?.rank ?? 0) })]),
      [W.also.note, "#note", view.note ? W.also.written : W.also.empty],
    ].filter(Boolean) as string[][];
    el.innerHTML = `<div class="tk-sec-head"><span class="tk-eyebrow">${esc(W.also.title)}</span></div>` + rows.map(([label, href, right]) => `<a class="tk-row" href="${href}"><span class="tk-row-text accent">${esc(label)}</span><span class="tk-leader"></span><span class="tk-mono">${esc(right)}</span></a>`).join("");
  };

  const drawRoutines = () => {
    const el = $("[data-routines]"); if (!el) return;
    const rs = (doc.routines ?? []).filter((r) => applies(r));
    if (!rs.length) { el.innerHTML = `<p class="tk-quiet">${esc(W.routines.empty)}</p>`; return; }
    el.innerHTML = rs.map((r) => {
      const open = !!view.progress.routines?.[r.id]; const st = view.routines?.[r.id] ?? {}; const ticked: string[] = st.ticked ?? [];
      const all = r.items.length && ticked.length === r.items.length; const some = ticked.length > 0 && !all;
      return `<details class="tk-routine" ${open && !all ? "open" : ""}><summary>${all ? `<span class="dot dash rose"></span>` : some ? `<span class="dot ring"></span>` : open ? `<span class="dot ring"></span>` : `<span class="dot hollow"></span>`}<span class="tk-step-title">${esc(r.name)}</span><span class="tk-mono">${esc(W.resets[r.resets] ?? r.resets)}${st.reset_at ? ` · ${esc(fill(W.routines.lastReset, { when: dayWord(st.reset_at) }))}` : ""}${!open ? ` · ${esc(W.routines.gated)} ${esc(words(r.gate, gateShort).join(" · "))}` : ""}</span></summary>
        <div class="tk-routine-items">${r.items.map((i) => `<label class="tk-check"><input type="checkbox" data-tick="${esc(r.id)}" value="${esc(i.id)}" ${ticked.includes(i.id) ? "checked" : ""} ${open ? "" : "disabled"}/> <span class="${ticked.includes(i.id) ? "struck" : ""}">${esc(i.text)}</span></label>`).join("")}
        ${r.resets === "manual" ? `<button type="button" class="tk-ghost sm" data-reset="${esc(r.id)}">${esc(W.routines.reset)}</button>` : ""}</div></details>`;
    }).join("");
  };

  const drawCodex = () => {
    const el = $("[data-codex]"); if (!el) return;
    const entries = doc.codex ?? []; const notes = doc.codex_notes ?? [];
    const st = (id: string) => view.progress.codex?.[id] ?? "hidden";
    const active = entries.filter((c) => st(c.id) === "active"), soon = entries.filter((c) => st(c.id) === "soon"), hidden = entries.filter((c) => st(c.id) === "hidden");
    let html = notes.map((n) => `<div class="tk-notes"><span class="tk-eyebrow rose">${esc(n.title)}</span><ul>${n.items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul></div>`).join("");
    if (!active.length && !soon.length) {
      const first = hidden[0];
      html += `<p class="tk-quiet">${esc(first ? fill(W.codex.nothingFirst, { name: first.name, when: words(first.show_when, gateLong).join(", ") }) : W.codex.nothing)}</p>`;
    }
    html += active.map((c) => `<details class="tk-entry" ${view.lastDone && stepsById.get(view.lastDone.id)?.codex === c.id ? "open" : ""}><summary><span class="dot ring"></span><span class="tk-step-title">${esc(c.name)}</span></summary><div class="tk-entry-body">${["what", "when", "how"].filter((k) => (c as any)[k]).map((k) => `<p class="tk-line"><b>${esc(W.codex[k])} · </b>${esc((c as any)[k])}</p>`).join("")}${(c.links ?? []).length ? `<div class="tk-links">${c.links!.map((l) => safeUrl(l.url) ? `<a class="tk-pill" href="${esc(safeUrl(l.url))}" target="_blank" rel="nofollow noopener">${isVideo(l) ? `<span class="tk-play"><span></span></span>` : `<span class="tk-mono">↗</span>`}<span>${esc(l.label || l.url)}</span></a>` : "").join("")}</div>` : ""}</div></details>`).join("");
    html += soon.map((c) => `<div class="tk-entry soon"><span class="dot hollow"></span><span class="tk-step-title">${esc(c.name)}</span><span class="tk-mono">${esc(W.codex.ignore)} ${esc(c.ignore_until ?? "")}</span></div>`).join("");
    if (hidden.length && (active.length || soon.length)) html += `<p class="tk-quiet">${esc(fill(W.codex.moreLater, { n: String(hidden.length) }))}${hidden[0]?.show_when ? ` ${esc(fill(W.codex.firstAt, { name: hidden[0].name, when: words(hidden[0].show_when, gateLong).join(", ") }))}` : ""}</p>`;
    el.innerHTML = html;
  };

  const drawTracks = () => {
    for (const t of doc.tracks ?? []) {
      const el = $(`[data-track="${CSS.escape(t.id)}"]`); if (!el) continue;
      if (!applies(t)) { el.innerHTML = `<p class="tk-quiet">${esc(fill(W.track.notThisRun, { names: (t.applies_to ?? []).join(", ") }))}</p>`; continue; }
      const st = view.tracks?.[t.id] ?? {}; const rank = Number(st.rank ?? 0); const dayOne: string[] = st.day_one ?? []; const counters = st.counters ?? {};
      const ranks = t.ranks ?? [];
      let html = ranks.length ? `<div class="tk-sec-head"><span class="tk-eyebrow">${esc(W.track.ranks)}</span><span class="tk-mono">${esc(fill(W.track.rankOf, { n: String(rank), of: String(ranks.length) }))}</span></div>` +
        `<div class="tk-ranks">${ranks.map((r) => `<label class="tk-check"><input type="checkbox" data-rank="${esc(t.id)}" value="${r.n}" ${rank >= r.n ? "checked" : ""}/> <span class="${rank >= r.n ? "struck" : ""}"><b>${esc(W.track.rank)} ${r.n}</b> · ${esc(r.capstone)}${r.when ? ` <span class="tk-mono">— ${esc(r.when)}</span>` : ""}</span></label>`).join("")}</div>` : "";
      if ((t.day_one ?? []).length) html += `<div class="tk-sec-head"><span class="tk-eyebrow">${esc(W.track.dayOne)}</span><span class="tk-mono">${dayOne.length} / ${t.day_one!.length}</span></div><div class="tk-ranks">${t.day_one!.map((id) => `<label class="tk-check"><input type="checkbox" data-dayone="${esc(t.id)}" value="${esc(id)}" ${dayOne.includes(id) ? "checked" : ""}/> <span class="${dayOne.includes(id) ? "struck" : ""}">${esc(stepsById.get(id)?.title ?? id)} <span class="tk-mono">${esc(id)}</span></span></label>`).join("")}</div>`;
      for (const c of t.counters ?? []) {
        const n = Number(counters[c.id] ?? 0); const nudge = c.nudge_at !== undefined && n >= c.nudge_at;
        html += `<div class="tk-counter"><span class="tk-eyebrow">${esc(c.label)}</span><div class="tk-stepper"><button type="button" data-count="${esc(t.id)}:${esc(c.id)}:-1">−</button><span class="tk-count">${n}</span><button type="button" data-count="${esc(t.id)}:${esc(c.id)}:1">+</button>${c.max !== undefined ? `<span class="tk-mono">/ ${c.max}</span>` : ""}</div>${nudge && c.nudge ? `<p class="tk-nudge">${esc(c.nudge)}</p>` : ""}</div>`;
      }
      html += (t.sections ?? []).map((s) => `<details class="tk-entry"><summary><span class="tk-step-title">${esc(s.title)}</span></summary><div class="tk-entry-body"><p class="tk-line pre">${esc(s.body)}</p></div></details>`).join("");
      el.innerHTML = html;
    }
  };

  const drawNote = () => { const el = $<HTMLTextAreaElement>("[data-note]"); if (el && document.activeElement !== el) el.value = view.note ?? ""; };

  const draw = () => { drawHead(); drawNow(); drawLater(); drawPath(); drawAlso(); drawRoutines(); drawCodex(); drawTracks(); drawNote(); };

  /* ── the Done moment ─────────────────────────────────────────────────── */
  const done = async (stepId: string) => {
    const card = $("[data-now-card]");
    if (reduced() || !card) {
      await act(async () => call("POST", `/api/runs/${view.id}/steps/${encodeURIComponent(stepId)}`, { state: "done" }));
      const line = $("[data-done-line]")!; line.textContent = `${W.now.doneWord} · ${stepId}`; line.hidden = false;
      window.setTimeout(() => { line.hidden = true; }, 2000);
      return;
    }
    card.classList.add("ignite");
    const request = call("POST", `/api/runs/${view.id}/steps/${encodeURIComponent(stepId)}`, { state: "done" });
    window.setTimeout(() => card.classList.add("collapse"), 260);
    const answer = await request;
    const wait = (ms: number) => new Promise((r) => window.setTimeout(r, ms));
    await wait(340);
    if (answer) { view = answer; reentryDismissed = true; draw(); const next = $("[data-now-card]"); if (next) { next.classList.add("unfold"); requestAnimationFrame(() => requestAnimationFrame(() => next.classList.remove("unfold"))); } }
    else { card.classList.remove("ignite", "collapse"); }
  };

  /* ── events ──────────────────────────────────────────────────────────── */
  root.addEventListener("click", async (event) => {
    const t = event.target as HTMLElement;
    const btn = t.closest<HTMLElement>("button, a");
    if (btn?.matches("[data-done]")) { const id = $("[data-now-card]")?.dataset.step; if (id) { reentryDismissed = true; await done(id); } return; }
    if (btn?.matches("[data-later]")) { const id = $("[data-now-card]")?.dataset.step; if (id) { reentryDismissed = true; await act(() => call("POST", `/api/runs/${view.id}/steps/${encodeURIComponent(id)}`, { state: "later" })); } return; }
    if (btn?.matches("[data-skip]")) { const id = $("[data-now-card]")?.dataset.step; if (id) await act(() => call("POST", `/api/runs/${view.id}/steps/${encodeURIComponent(id)}`, { state: "skipped" })); return; }
    if (btn?.matches("[data-more]")) { const more = $("[data-now-card] .tk-now-more"); if (more) { more.hidden = !more.hidden; btn.setAttribute("aria-expanded", String(!more.hidden)); } return; }
    if (btn?.matches("[data-fold]")) { collapsed = !collapsed; try { localStorage.setItem(collapsedKey, collapsed ? "1" : "0"); } catch {} root.dataset.folded = collapsed ? "1" : "0"; drawPath(); return; }
    if (btn?.matches("[data-unpark]")) { await act(() => call("DELETE", `/api/runs/${view.id}/later/${btn.dataset.unpark}`)); return; }
    if (btn?.matches("[data-reset]")) { await act(() => call("POST", `/api/runs/${view.id}/routines/${encodeURIComponent(btn.dataset.reset!)}/reset`)); return; }
    if (btn?.matches("[data-count]")) { const [tid, cid, d] = btn.dataset.count!.split(":"); const cur = Number(view.tracks?.[tid]?.counters?.[cid] ?? 0); const counters = { ...(view.tracks?.[tid]?.counters ?? {}), [cid]: Math.max(0, cur + Number(d)) }; await act(() => call("PUT", `/api/runs/${view.id}/track/${encodeURIComponent(tid)}`, { counters })); return; }
    if (btn?.matches("[data-row-state]")) { const [id, st] = btn.dataset.rowState!.split(":"); await act(() => call("POST", `/api/runs/${view.id}/steps/${encodeURIComponent(id)}`, { state: st })); return; }
    if (btn?.matches("[data-checkin]")) { openCheckin(); return; }
    if (btn?.matches("[data-much]")) { openMuch(); return; }
    if (btn?.matches("[data-sheet-close]")) { closeSheet(); return; }
    if (btn?.matches("[data-much-close]")) { closeMuch(); return; }
    if (btn?.matches("[data-timer]")) { startTimer(); return; }
    if (btn?.matches("[data-timer-stop]")) { stopTimer(); return; }
    if (btn?.matches("[data-save-note]")) { const text = $<HTMLTextAreaElement>("[data-note]")?.value ?? ""; await act(() => call("PUT", `/api/runs/${view.id}/note`, { text })); const s = $("[data-note-status]"); if (s) s.textContent = W.note.saved; return; }
    const row = t.closest<HTMLElement>("[data-row]");
    if (row) {
      const id = row.dataset.row!; const st = state(id); const menu = $(`[data-menu="${CSS.escape(id)}"]`)!;
      for (const m of root.querySelectorAll<HTMLElement>("[data-menu]")) if (m !== menu) m.hidden = true;
      if (!menu.hidden) { menu.hidden = true; return; }
      const s = stepsById.get(id)!;
      const buttons = st === "done" ? [["open", W.path.undo]] : st === "skipped" || st === "later" ? [["open", W.path.back]]
        : st === "locked" ? [] : [["done", W.now.done], ["skipped", W.now.skip], ["later", W.now.later]];
      const gate = st === "locked" ? words(s.gate, gateLong) : [];
      menu.innerHTML = (st === "locked" ? `<span class="tk-mono">${esc(gate.length ? fill(W.path.locked, { when: gate.join(", ") }) : W.path.notThisRun)}</span>` : "") +
        buttons.map(([v, label]) => `<button type="button" class="tk-ghost sm" data-row-state="${esc(id)}:${v}">${esc(label)}</button>`).join("");
      menu.hidden = false;
    }
  });
  root.addEventListener("change", async (event) => {
    const el = event.target as HTMLInputElement;
    if (el.dataset.tick) { const rid = el.dataset.tick; const ticked = Array.from(root.querySelectorAll<HTMLInputElement>(`[data-tick="${CSS.escape(rid)}"]:checked`)).map((x) => x.value); await act(() => call("POST", `/api/runs/${view.id}/routines/${encodeURIComponent(rid)}`, { ticked })); }
    if (el.dataset.rank) { const tid = el.dataset.rank; const n = Number(el.value); const rank = el.checked ? Math.max(n, Number(view.tracks?.[tid]?.rank ?? 0)) : n - 1; await act(() => call("PUT", `/api/runs/${view.id}/track/${encodeURIComponent(tid)}`, { rank })); }
    if (el.dataset.dayone) { const tid = el.dataset.dayone; const day_one = Array.from(root.querySelectorAll<HTMLInputElement>(`[data-dayone="${CSS.escape(tid)}"]:checked`)).map((x) => x.value); await act(() => call("PUT", `/api/runs/${view.id}/track/${encodeURIComponent(tid)}`, { day_one })); }
  });
  root.addEventListener("submit", async (event) => {
    const form = event.target as HTMLFormElement;
    if (form.matches("[data-park]")) { event.preventDefault(); const text = String(new FormData(form).get("text") ?? "").trim(); if (text) await act(() => call("POST", `/api/runs/${view.id}/later`, { text })); return; }
    if (form.matches("[data-checkin-form]")) { event.preventDefault(); await saveCheckin(form); return; }
    if (form.matches("[data-proposal-form]")) { event.preventDefault(); const ids = Array.from(form.querySelectorAll<HTMLInputElement>("input[name=step]:checked")).map((x) => x.value); closeSheet(); if (ids.length) await act(() => call("POST", `/api/runs/${view.id}/accept`, { steps: ids })); return; }
  });
  root.addEventListener("input", (event) => {
    const el = event.target as HTMLInputElement;
    if (el.name === "step" && el.form?.matches("[data-proposal-form]")) { const n = el.form.querySelectorAll("input[name=step]:checked").length; const b = el.form.querySelector<HTMLButtonElement>("[data-mark]"); if (b) b.textContent = fill(W.proposal.mark, { n: String(n) }); }
    if (el.matches("[data-step-value]")) { const v = el.closest(".tk-stepper")?.querySelector<HTMLElement>(".tk-count"); }
  });

  /* ── sheets ──────────────────────────────────────────────────────────── */
  const sheet = $("[data-sheet]")!;
  const openSheet = (html: string) => { sheet.querySelector("[data-sheet-body]")!.innerHTML = html; sheet.hidden = false; document.body.style.overflow = "hidden"; };
  const closeSheet = () => { sheet.hidden = true; document.body.style.overflow = ""; };
  const openCheckin = () => {
    const fields = (doc.checkin ?? []);
    const shown = fields.filter((f) => view.checkinShown?.[f.id]);
    const hiddenLine = fields.filter((f) => !view.checkinShown?.[f.id] && applies(f)).map((f) => fill(W.checkin.appears, { label: f.label || f.id, when: words(f.show_when, gateLong).join(", ") })).join(" ");
    const html = `<form data-checkin-form><h3 class="tk-sheet-title">${esc(W.checkin.title)}</h3><p class="tk-quiet">${esc(view.lastSeenAt ? fill(W.checkin.last, { when: dayWord(view.lastSeenAt) }) : W.checkin.first)}</p>` +
      shown.map((f) => {
        const v = view.checkin[f.id];
        if (f.type === "number") return `<div class="tk-field"><span class="tk-eyebrow">${esc(f.label || f.id)}</span><div class="tk-stepper big"><button type="button" data-num="${esc(f.id)}:-1">−</button><input type="number" name="${esc(f.id)}" value="${esc(v ?? f.min ?? 0)}" min="${esc(f.min ?? "")}" max="${esc(f.max ?? "")}" data-step-value /><button type="button" data-num="${esc(f.id)}:1">+</button></div></div>`;
        const opts = f.options ?? [];
        if (opts.length <= 6) return `<div class="tk-field"><span class="tk-eyebrow">${esc(f.label || f.id)}</span><div class="tk-seg">${opts.map((o) => `<label><input type="radio" name="${esc(f.id)}" value="${esc(o)}" ${o === v ? "checked" : ""}/><span>${esc(optionLabel(f, o))}</span></label>`).join("")}</div></div>`;
        return `<label class="tk-field"><span class="tk-eyebrow">${esc(f.label || f.id)}</span><select name="${esc(f.id)}"><option value="">—</option>${opts.map((o) => `<option value="${esc(o)}" ${o === v ? "selected" : ""}>${esc(optionLabel(f, o))}</option>`).join("")}</select></label>`;
      }).join("") +
      (hiddenLine ? `<p class="tk-mono">${esc(hiddenLine)}</p>` : "") +
      `<div class="tk-sheet-acts"><button type="button" class="tk-ghost" data-sheet-close>${esc(W.checkin.cancel)}</button><button type="submit" class="tk-primary">${esc(W.checkin.save)}</button></div></form>`;
    openSheet(html);
  };
  sheet.addEventListener("click", (event) => {
    const b = (event.target as HTMLElement).closest<HTMLElement>("[data-num]"); if (!b) return;
    const [fid, d] = b.dataset.num!.split(":"); const input = sheet.querySelector<HTMLInputElement>(`input[name="${CSS.escape(fid)}"]`); if (!input) return;
    const min = input.min === "" ? -Infinity : Number(input.min), max = input.max === "" ? Infinity : Number(input.max);
    input.value = String(Math.min(max, Math.max(min, (Number(input.value) || 0) + Number(d))));
  });
  const saveCheckin = async (form: HTMLFormElement) => {
    const values: Record<string, unknown> = {};
    for (const f of doc.checkin ?? []) { const raw = new FormData(form).get(f.id); if (raw !== null && raw !== "") values[f.id] = f.type === "number" ? Number(raw) : String(raw); }
    closeSheet();
    const answer = await call("POST", `/api/runs/${view.id}/checkin`, { values });
    if (!answer) return;
    view = answer; reentryDismissed = true; draw();
    const proposals: any[] = view.progress.proposals ?? [];
    if (proposals.length) openProposal(proposals);
  };
  const openProposal = (proposals: any[]) => {
    const summary = checkinSummary().split(", ")[0] || "";
    openSheet(`<form data-proposal-form><h3 class="tk-sheet-title">${esc(fill(W.proposal.title, { summary, n: String(proposals.length) }))}</h3><p class="tk-quiet">${esc(W.proposal.sub)}</p>` +
      proposals.map((p) => `<label class="tk-check big"><input type="checkbox" name="step" value="${esc(p.id)}" checked /><span><span class="tk-step-title">${esc(p.title)}</span><span class="tk-mono">${esc(p.id)} · ${esc(p.evidence)}</span></span></label>`).join("") +
      `<p class="tk-mono">${esc(W.proposal.footer)}</p><div class="tk-sheet-acts"><button type="button" class="tk-ghost" data-sheet-close>${esc(W.proposal.nothing)}</button><button type="submit" class="tk-primary" data-mark>${esc(fill(W.proposal.mark, { n: String(proposals.length) }))}</button></div></form>`);
  };

  /* ── Too much ────────────────────────────────────────────────────────── */
  const much = $("[data-much-panel]")!;
  let timerHandle = 0; let remaining = 0;
  const openMuch = () => {
    const cur = view.progress.current ? stepsById.get(view.progress.current) : null;
    much.querySelector("[data-much-line]")!.textContent = cur ? (cur.oneliner || cur.title) : W.now.finished;
    much.hidden = false; document.body.style.overflow = "hidden";
  };
  const closeMuch = () => { stopTimer(); much.hidden = true; document.body.style.overflow = ""; };
  const fmt = (s: number) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  const startTimer = () => {
    remaining = 15 * 60; much.dataset.timer = "1";
    const clock = much.querySelector<HTMLElement>("[data-clock]")!; clock.textContent = fmt(remaining);
    const said = much.querySelector<HTMLElement>("[data-timer-said]")!; said.textContent = W.much.playing;
    timerHandle = window.setInterval(() => {
      remaining -= 1; clock.textContent = fmt(Math.max(0, remaining));
      if (remaining <= 0) { window.clearInterval(timerHandle); said.textContent = W.much.finished; }
    }, 1000);
  };
  const stopTimer = () => { window.clearInterval(timerHandle); delete much.dataset.timer; };

  /* ── run switcher ────────────────────────────────────────────────────── */
  $<HTMLSelectElement>("[data-switch]")?.addEventListener("change", (event) => {
    const v = (event.target as HTMLSelectElement).value;
    location.href = v === "new" ? `${location.pathname}?new=1` : `${location.pathname}?run=${v}`;
  });

  root.dataset.folded = collapsed ? "1" : "0";
  draw();
}

/* Starting a run: a form, then the bulk-skip PROPOSAL, then the run. */
export function mountNewRun(root: HTMLElement) {
  const W: Words = JSON.parse(root.dataset.words || "{}");
  const guideId = Number(root.dataset.guide || 0);
  const esc = (s: unknown) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  const token = () => document.cookie.split("; ").find((c) => c.startsWith("shruti_csrf="))?.split("=")[1] ?? "";
  const form = root.querySelector<HTMLFormElement>("[data-new-run]")!;
  const sheet = root.querySelector<HTMLElement>("[data-sheet]")!;
  const status = root.querySelector<HTMLElement>("[data-new-status]")!;
  const create = async (name: string, variant: string, skip: string[]) => {
    status.textContent = W.newRun.starting;
    const r = await fetch("/api/runs", { method: "POST", headers: { "content-type": "application/json", "x-csrf-token": token() }, body: JSON.stringify({ guide_id: guideId, name, variant, skip_steps: skip }) });
    if (!r.ok) { status.textContent = W.error.noAnswer; return; }
    const run = await r.json();
    location.href = `${location.pathname}?run=${run.id}`;
  };
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const name = String(data.get("name") ?? "").trim();
    const variant = String(data.get("variant") ?? "");
    const groups = data.getAll("skip").map(String).filter(Boolean);
    if (!groups.length) { await create(name, variant, []); return; }
    const r = await fetch(`/api/runs/skip-proposal?guide=${guideId}&groups=${encodeURIComponent(groups.join(","))}`);
    const proposal: { phase: string; name: string; steps: string[] }[] = r.ok ? await r.json() : [];
    const total = proposal.reduce((n, p) => n + p.steps.length, 0);
    if (!total) { await create(name, variant, []); return; }
    sheet.querySelector("[data-sheet-body]")!.innerHTML = `<form data-skip-form><h3 class="tk-sheet-title">${esc(W.newRun.skipTitle)}</h3><p class="tk-quiet">${esc(W.proposal.sub)}</p>` +
      proposal.map((p) => `<label class="tk-check big"><input type="checkbox" name="phase" value="${esc(p.phase)}" checked data-steps="${esc(p.steps.join(","))}" /><span><span class="tk-step-title">${esc(p.name)}</span><span class="tk-mono">${p.steps.length} ${esc(W.newRun.steps)}</span></span></label>`).join("") +
      `<p class="tk-mono">${esc(W.newRun.skipFooter)}</p><div class="tk-sheet-acts"><button type="button" class="tk-ghost" data-skip-nothing>${esc(W.proposal.nothing)}</button><button type="submit" class="tk-primary" data-skip-n>${esc(fill(W.newRun.skipN, { n: String(total) }))}</button></div></form>`;
    sheet.hidden = false;
    const skipForm = sheet.querySelector<HTMLFormElement>("[data-skip-form]")!;
    const recount = () => { const n = Array.from(skipForm.querySelectorAll<HTMLInputElement>("input[name=phase]:checked")).reduce((k, x) => k + x.dataset.steps!.split(",").filter(Boolean).length, 0); skipForm.querySelector("[data-skip-n]")!.textContent = fill(W.newRun.skipN, { n: String(n) }); };
    skipForm.addEventListener("change", recount);
    skipForm.querySelector("[data-skip-nothing]")!.addEventListener("click", async () => { sheet.hidden = true; await create(name, variant, []); });
    skipForm.addEventListener("submit", async (e) => { e.preventDefault(); const skip = Array.from(skipForm.querySelectorAll<HTMLInputElement>("input[name=phase]:checked")).flatMap((x) => x.dataset.steps!.split(",").filter(Boolean)); sheet.hidden = true; await create(name, variant, skip); });
  });
}
