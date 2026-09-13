/* One drawing per element, shared by the single-element sources' twins in a
 * layout. The Done moment on the now card keeps its timings: ignite 0–300,
 * collapse 260–340, unfold 300–400. Under the overlay's own reduced setting
 * it is an instant swap and one line.
 */
const esc = (s: unknown) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
const wait = (ms: number) => new Promise((r) => window.setTimeout(r, ms));

const arcD = (r: number, a0: number, a1: number) => {
  const R = (d: number) => ((d - 90) * Math.PI) / 180;
  const x0 = 50 + r * Math.cos(R(a0)), y0 = 50 + r * Math.sin(R(a0)), x1 = 50 + r * Math.cos(R(a1)), y1 = 50 + r * Math.sin(R(a1));
  return `M ${x0.toFixed(2)} ${y0.toFixed(2)} A ${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`;
};

export function sigilSvg(parts: any[], stroke = 12, size = 200): string {
  const n = Math.max(1, parts.length), gap = Math.max(2, Math.min(8, 24 / n)), span = 360 / n, w = stroke * 0.5, r = 50 - w / 2 - 1;
  let out = "";
  parts.forEach((p, i) => {
    const a0 = i * span + gap / 2, a1 = (i + 1) * span - gap / 2;
    out += `<path d="${arcD(r, a0, a1)}" fill="none" stroke="var(--gt-faint)" stroke-opacity=".35" stroke-width="${w}"/>`;
    const pct = Math.max(0, Math.min(1, p.pct || 0));
    out += `<path class="fill" pathLength="100" d="${arcD(r, a0, a1)}" fill="none" stroke="${p.state === "done" ? "var(--st-done)" : "var(--st-now)"}" stroke-width="${w}" style="stroke-dasharray:${(pct * 100).toFixed(1)} 100${pct <= 0.004 ? ";opacity:0" : ""}"/>`;
  });
  return `<svg viewBox="0 0 100 100" width="${size}" height="${size}" aria-hidden="true">${out}</svg>`;
}

interface Opts { still: boolean; reduced: boolean; line?: HTMLElement | null }

export async function drawElement(slot: HTMLElement, kind: string, prev: any, next: any, o: Opts): Promise<void> {
  if (kind === "guide-now") {
    let card = slot.querySelector<HTMLElement>(".gov-now");
    if (!card) { slot.innerHTML = `<div class="gov-plate gov-now"><div class="swap" data-swap><span class="gov-eyebrow" data-phase></span><span class="title" data-title></span><span class="line" data-line></span><span class="horizon"></span></div></div>`; card = slot.querySelector<HTMLElement>(".gov-now")!; }
    const swap = card.querySelector<HTMLElement>("[data-swap]")!;
    const paint = (el: any) => { card!.querySelector("[data-phase]")!.textContent = el?.phase ?? ""; card!.querySelector("[data-title]")!.textContent = el?.title ?? ""; card!.querySelector("[data-line]")!.textContent = el?.line ?? ""; card!.hidden = !el || !el.id; };
    const stepChanged = prev?.id && next?.id !== prev.id;
    if (!stepChanged || o.still || o.reduced) {
      paint(next);
      if (stepChanged && o.reduced && o.line) { o.line.textContent = `Done · ${prev.id}`; o.line.hidden = false; window.setTimeout(() => { o.line!.hidden = true; }, 2000); }
      return;
    }
    card.classList.add("ignite"); await wait(260); swap.classList.add("collapse"); await wait(80); paint(next); swap.classList.remove("collapse"); swap.classList.add("unfold");
    requestAnimationFrame(() => requestAnimationFrame(() => swap.classList.remove("unfold"))); await wait(100); card.classList.remove("ignite");
    return;
  }
  if (kind === "guide-sigil") {
    let holder = slot.querySelector<HTMLElement>(".gov-sigil");
    if (!holder) { slot.innerHTML = `<div class="gov-sigil"><div class="ring" data-ring></div><span class="count" data-count></span></div>`; holder = slot.querySelector<HTMLElement>(".gov-sigil")!; }
    const ring = holder.querySelector<HTMLElement>("[data-ring]")!;
    const stroke = Number(getComputedStyle(slot.closest(".gov")!).getPropertyValue("--gt-stroke")) || 12;
    holder.hidden = !next;
    if (!next) return;
    const fills = ring.querySelectorAll<SVGPathElement>(".fill");
    if (fills.length === (next.parts ?? []).length && fills.length) {
      next.parts.forEach((p: any, i: number) => { const f = fills[i]; const pct = Math.max(0, Math.min(1, p.pct || 0)); f.setAttribute("stroke", p.state === "done" ? "var(--st-done)" : "var(--st-now)"); f.style.strokeDasharray = `${(pct * 100).toFixed(1)} 100`; f.style.opacity = pct <= 0.004 ? "0" : "1"; });
    } else ring.innerHTML = sigilSvg(next.parts ?? [], stroke);
    holder.querySelector("[data-count]")!.textContent = next.count ?? "";
    const finished = prev && (prev.parts ?? []).filter((p: any) => p.state === "done").length < (next.parts ?? []).filter((p: any) => p.state === "done").length;
    if (finished && !o.still && !o.reduced) { holder.classList.add("phase-done"); await wait(600); holder.classList.remove("phase-done"); }
    return;
  }
  if (kind === "guide-path") {
    slot.innerHTML = next ? `<div class="gov-plate gov-path">${(next.strip ?? []).map((it: any) => `<span class="it ${esc(it.state)}"><span class="dot ${esc(it.state)}"></span><span>${esc(it.title)}</span></span>`).join("")}</div>` : "";
    return;
  }
  if (kind === "guide-goal") {
    /* A group's goal: the title, the count, one bar per tier, the crew by
     * size with "and N others" — no ranks and no medals, by design. */
    const g = next && next.parts ? next : null;
    if (!g) { slot.innerHTML = ""; return; }
    const crew = [...(g.contributors ?? [])];
    const others = Number(g.others || 0);
    const line = crew.join(" · ") + (others > 0 ? `${crew.length ? " · " : ""}and ${others} ${others === 1 ? "other" : "others"}` : "");
    slot.innerHTML = `<div class="gov-plate gov-goal"><span class="gov-eyebrow">${esc(g.name)}</span><span class="title">${esc(g.goal)}</span><span class="gov-mono count">${esc(g.count)}${g.tiers ? ` · tier ${esc(g.tier)} of ${esc(g.tiers)}` : ""}</span><div class="tiers">${(g.parts ?? []).map((p: any) => `<span class="tier ${esc(p.state)}"><span class="fill" style="width:${(Math.max(0, Math.min(1, p.pct || 0)) * 100).toFixed(1)}%"></span></span>`).join("")}</div><span class="crew">${esc(line)}</span></div>`;
    return;
  }
  if (kind === "counter") {
    /* The site's counter as an element: label 22px eyebrow, number 72px mono
     * tabular. The host formats the numbers; this only places them. */
    const c = next && next.text != null ? next : null;
    slot.innerHTML = c ? `<div class="gov-plate gov-counter"><span class="gov-eyebrow">${esc(c.name)}</span><span class="gov-mono number">${esc(c.text)}</span>${c.target_text ? `<span class="of">${esc(c.target_text)}</span>` : ""}</div>` : "";
    return;
  }
  if (kind === "text") {
    slot.innerHTML = next && next.text ? `<div class="gov-plate gov-text"><span class="line">${esc(next.text)}</span></div>` : "";
    return;
  }
  if (kind === "image") {
    const url = String(next?.url || "");
    slot.innerHTML = /^https:\/\//i.test(url) ? `<img class="gov-image" src="${esc(url)}" alt="" />` : "";
    return;
  }
  if (kind === "ticker") {
    /* Names, most recent first, and nothing else — never amounts. Empty
     * carries her standing line rather than advertising emptiness. */
    const t = next && Array.isArray(next.names) ? next : null;
    if (!t) { slot.innerHTML = ""; return; }
    const row = t.names.length
      ? t.names.map((n: any) => `<span class="${n.anonymous ? "anon" : ""}">${esc(n.who)}</span>`).join(`<span class="sep">·</span>`)
      : (t.standing ? `<span class="standing">${esc(t.standing)}</span>` : "");
    slot.innerHTML = row ? `<div class="gov-plate gov-ticker"><span class="gov-eyebrow">${esc(t.label || "supporters")}</span><div class="names">${row}</div></div>` : "";
    return;
  }
  if (kind === "sky") {
    /* Finished numbers from the server; this only lays them out. */
    const bodies: any[] = next && Array.isArray(next.bodies) ? next.bodies : [];
    if (!bodies.length) { slot.innerHTML = ""; return; }
    const deg = (d: number) => { const whole = Math.floor(d), min = Math.round((d - whole) * 60); return `${whole}°${String(min).padStart(2, "0")}′`; };
    slot.innerHTML = `<div class="gov-plate gov-sky"><span class="gov-eyebrow">the sky now</span>${bodies.map((b: any) =>
      `<div class="body"><span class="name">${esc(b.name)}</span><span class="gov-mono where">${esc(b.sign)} ${deg(Number(b.degree) || 0)}${b.retrograde ? `<span class="retro">retro</span>` : ""}</span><span class="gov-mono rate">${(Number(b.perHour) || 0) >= 0 ? "+" : ""}${(Number(b.perHour) || 0).toFixed(2)}°/h</span></div>`).join("")}</div>`;
    return;
  }
  if (kind === "hours") {
    const h = next && next.current ? next : null;
    if (!h) { slot.innerHTML = ""; return; }
    const ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"];
    const cell = (c: any, now: boolean) => c ? `<div class="cell ${now ? "now" : ""}"><span class="who">${esc(c.ruler)}</span><span class="gov-mono ord">${ROMAN[c.index] ?? c.index} · ${c.isNight ? "night" : "day"}</span></div>` : `<div class="cell"><span class="who">—</span></div>`;
    slot.innerHTML = `<div class="gov-plate gov-hours"><span class="gov-eyebrow">planetary hours</span><div class="cells">${cell(h.past, false)}${cell(h.current, true)}${cell(h.next, false)}</div><span class="gov-mono day">the day belongs to ${esc(h.dayRuler || "")}</span></div>`;
    return;
  }
  if (kind === "countdown") {
    /* The server sends the deadline and its own clock; the offset is measured
     * once and the count is right afterwards. A closed window says so and
     * never counts upward into negatives. */
    const c = next && next.name != null ? next : null;
    const anySlot = slot as any;
    if (anySlot._tick) { window.clearInterval(anySlot._tick); anySlot._tick = 0; }
    if (!c) { slot.innerHTML = ""; return; }
    slot.innerHTML = `<div class="gov-plate gov-countdown"><span class="gov-eyebrow">${esc(c.name)}</span><span class="gov-mono figure" data-figure></span><span class="say" data-say></span></div>`;
    const figure = slot.querySelector<HTMLElement>("[data-figure]")!, say = slot.querySelector<HTMLElement>("[data-say]")!;
    if (!c.endsAt) { say.textContent = "Open · no closing date"; return; }
    const offset = Date.now() - new Date(c.now || Date.now()).getTime();
    const ends = new Date(c.endsAt).getTime();
    const paint = () => {
      const left = ends - (Date.now() - offset);
      if (left <= 0) { figure.textContent = ""; say.textContent = "Window closed"; if (anySlot._tick) { window.clearInterval(anySlot._tick); anySlot._tick = 0; } return; }
      const s = Math.floor(left / 1000), d = Math.floor(s / 86400), hh = Math.floor((s % 86400) / 3600), mm = Math.floor((s % 3600) / 60), ss = s % 60;
      figure.textContent = d > 0 ? `${d}d ${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}` : `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`;
      say.textContent = "left";
    };
    paint();
    anySlot._tick = window.setInterval(paint, 1000);
    return;
  }
  if (kind === "alerts") {
    /* Whatever has not been shown yet, one plate at a time. History is not
     * replayed: the first frame marks everything seen. Silent, by design. */
    const events: any[] = next && Array.isArray(next.events) ? next.events : [];
    const anySlot = slot as any;
    if (!anySlot._seen) {
      anySlot._seen = new Set(events.map((e) => e.id));
      anySlot._queue = [];
      if (!slot.querySelector(".gov-alerts")) slot.innerHTML = `<div class="gov-alerts" data-alerts></div>`;
      return;
    }
    const fresh = events.filter((e) => !anySlot._seen.has(e.id));
    fresh.forEach((e) => anySlot._seen.add(e.id));
    anySlot._queue.push(...fresh);
    const box = slot.querySelector<HTMLElement>("[data-alerts]") ?? (() => { slot.innerHTML = `<div class="gov-alerts" data-alerts></div>`; return slot.querySelector<HTMLElement>("[data-alerts]")!; })();
    const money = (e: any) => e.amountMinor ? `${(e.currency || "").toUpperCase() === "EUR" ? "€" : (e.currency || "") + " "}${(e.amountMinor / 100).toFixed(2)}` : (e.quantity ? `× ${e.quantity}` : "");
    const showNext = async () => {
      if (anySlot._showing) return;
      const e = anySlot._queue.shift(); if (!e) return;
      anySlot._showing = true;
      box.innerHTML = `<div class="gov-plate gov-alert ${o.still || o.reduced ? "" : "enter"}"><span class="who">${esc(e.who || "Someone")}</span>${money(e) ? `<span class="gov-mono amount">${esc(money(e))}</span>` : ""}${e.message ? `<span class="message">${esc(e.message)}</span>` : ""}</div>`;
      await wait(6000);
      box.innerHTML = "";
      anySlot._showing = false;
      if (anySlot._queue.length) showNext();
    };
    showNext();
    return;
  }
  if (kind === "wheel") {
    /* The transit wheel is its own source; a layout embeds it where it sits. */
    const src = String(next?.src || "");
    slot.innerHTML = src.startsWith("/overlay/wheel") ? `<iframe class="gov-wheel" src="${esc(src)}" title="transit wheel" loading="eager"></iframe>` : "";
    return;
  }
  if (kind === "guide-routine") {
    const r = next?.routine;
    slot.innerHTML = r ? `<div class="gov-plate gov-routine"><div class="head"><span class="name">${esc(r.name)}</span><span class="gov-mono count">${esc(r.count)}</span></div><div>${(r.items ?? []).map((i: any) => `<div class="item ${i.done ? "done" : ""}"><span class="dot ${i.done ? "done" : "available"}"></span><span>${esc(i.text)}</span></div>`).join("")}</div></div>` : "";
    return;
  }
}
