"use strict";
var OverlayElements = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // ../../../../../../home/sophia/Documents/development/shurtiwebsite/frontend/site/src/lib/overlay-elements.ts
  var overlay_elements_exports = {};
  __export(overlay_elements_exports, {
    drawElement: () => drawElement,
    sigilSvg: () => sigilSvg
  });
  var esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  var wait = (ms) => new Promise((r) => window.setTimeout(r, ms));
  var arcD = (r, a0, a1) => {
    const R = (d) => (d - 90) * Math.PI / 180;
    const x0 = 50 + r * Math.cos(R(a0)), y0 = 50 + r * Math.sin(R(a0)), x1 = 50 + r * Math.cos(R(a1)), y1 = 50 + r * Math.sin(R(a1));
    return `M ${x0.toFixed(2)} ${y0.toFixed(2)} A ${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`;
  };
  function sigilSvg(parts, stroke = 12, size = 200) {
    const n = Math.max(1, parts.length), gap = Math.max(2, Math.min(8, 24 / n)), span = 360 / n, w = stroke * 0.5, r = 50 - w / 2 - 1;
    let out = "";
    parts.forEach((p, i) => {
      const a0 = i * span + gap / 2, a1 = (i + 1) * span - gap / 2;
      out += `<path d="${arcD(r, a0, a1)}" fill="none" stroke="var(--gt-faint)" stroke-opacity=".35" stroke-width="${w}"/>`;
      const pct = Math.max(0, Math.min(1, p.pct || 0));
      if (p.partly !== void 0) {
        const partly = Math.max(pct, Math.min(1, Number(p.partly) || 0));
        out += `<path class="fill partly" pathLength="100" d="${arcD(r, a0, a1)}" fill="none" stroke="var(--st-now)" stroke-width="${w}" style="stroke-dasharray:${(partly * 100).toFixed(1)} 100${partly <= 4e-3 ? ";opacity:0" : ""}"/>`;
        out += `<path class="fill" pathLength="100" d="${arcD(r, a0, a1)}" fill="none" stroke="var(--st-done)" stroke-width="${w}" style="stroke-dasharray:${(pct * 100).toFixed(1)} 100${pct <= 4e-3 ? ";opacity:0" : ""}"/>`;
        return;
      }
      out += `<path class="fill" pathLength="100" d="${arcD(r, a0, a1)}" fill="none" stroke="${p.state === "done" ? "var(--st-done)" : "var(--st-now)"}" stroke-width="${w}" style="stroke-dasharray:${(pct * 100).toFixed(1)} 100${pct <= 4e-3 ? ";opacity:0" : ""}"/>`;
    });
    return `<svg viewBox="0 0 100 100" width="${size}" height="${size}" aria-hidden="true">${out}</svg>`;
  }
  async function drawElement(slot, kind, prev, next, o) {
    if (kind === "guide-now") {
      let card = slot.querySelector(".gov-now");
      if (!card) {
        slot.innerHTML = `<div class="gov-plate gov-now"><div class="swap" data-swap><span class="gov-eyebrow" data-phase></span><span class="title" data-title></span><span class="line" data-line></span><span class="horizon"></span></div></div>`;
        card = slot.querySelector(".gov-now");
      }
      const swap = card.querySelector("[data-swap]");
      const paint = (el) => {
        card.querySelector("[data-phase]").textContent = el?.phase ?? "";
        card.querySelector("[data-title]").textContent = el?.title ?? "";
        card.querySelector("[data-line]").textContent = el?.line ?? "";
        card.hidden = !el || !el.id;
      };
      const stepChanged = prev?.id && next?.id !== prev.id;
      if (!stepChanged || o.still || o.reduced) {
        paint(next);
        if (stepChanged && o.reduced && o.line) {
          o.line.textContent = `Done \xB7 ${prev.id}`;
          o.line.hidden = false;
          window.setTimeout(() => {
            o.line.hidden = true;
          }, 2e3);
        }
        return;
      }
      card.classList.add("ignite");
      await wait(260);
      swap.classList.add("collapse");
      await wait(80);
      paint(next);
      swap.classList.remove("collapse");
      swap.classList.add("unfold");
      requestAnimationFrame(() => requestAnimationFrame(() => swap.classList.remove("unfold")));
      await wait(100);
      card.classList.remove("ignite");
      return;
    }
    if (kind === "guide-sigil") {
      let holder = slot.querySelector(".gov-sigil");
      if (!holder) {
        slot.innerHTML = `<div class="gov-sigil"><div class="ring" data-ring></div><span class="count" data-count></span></div>`;
        holder = slot.querySelector(".gov-sigil");
      }
      const ring = holder.querySelector("[data-ring]");
      const stroke = Number(getComputedStyle(slot.closest(".gov")).getPropertyValue("--gt-stroke")) || 12;
      holder.hidden = !next;
      if (!next) return;
      const fills = ring.querySelectorAll(".fill");
      if (fills.length === (next.parts ?? []).length && fills.length) {
        next.parts.forEach((p, i) => {
          const f = fills[i];
          const pct = Math.max(0, Math.min(1, p.pct || 0));
          f.setAttribute("stroke", p.state === "done" ? "var(--st-done)" : "var(--st-now)");
          f.style.strokeDasharray = `${(pct * 100).toFixed(1)} 100`;
          f.style.opacity = pct <= 4e-3 ? "0" : "1";
        });
      } else ring.innerHTML = sigilSvg(next.parts ?? [], stroke);
      holder.querySelector("[data-count]").textContent = next.count ?? "";
      const finished = prev && (prev.parts ?? []).filter((p) => p.state === "done").length < (next.parts ?? []).filter((p) => p.state === "done").length;
      if (finished && !o.still && !o.reduced) {
        holder.classList.add("phase-done");
        await wait(600);
        holder.classList.remove("phase-done");
      }
      return;
    }
    if (kind === "guide-path") {
      slot.innerHTML = next ? `<div class="gov-plate gov-path">${(next.strip ?? []).map((it) => `<span class="it ${esc(it.state)}"><span class="dot ${esc(it.state)}"></span><span>${esc(it.title)}</span></span>`).join("")}</div>` : "";
      return;
    }
    if (kind === "guide-goal") {
      const g = next && next.parts ? next : null;
      if (!g) {
        slot.innerHTML = "";
        return;
      }
      const crew = [...g.contributors ?? []];
      const others = Number(g.others || 0);
      const line = crew.join(" \xB7 ") + (others > 0 ? `${crew.length ? " \xB7 " : ""}and ${others} ${others === 1 ? "other" : "others"}` : "");
      slot.innerHTML = `<div class="gov-plate gov-goal"><span class="gov-eyebrow">${esc(g.name)}</span><span class="title">${esc(g.goal)}</span><span class="gov-mono count">${esc(g.count)}${g.tiers ? ` \xB7 tier ${esc(g.tier)} of ${esc(g.tiers)}` : ""}</span><div class="tiers">${(g.parts ?? []).map((p) => `<span class="tier ${esc(p.state)}"><span class="fill" style="width:${(Math.max(0, Math.min(1, p.pct || 0)) * 100).toFixed(1)}%"></span></span>`).join("")}</div><span class="crew">${esc(line)}</span></div>`;
      return;
    }
    if (kind === "counter") {
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
      const t = next && Array.isArray(next.names) ? next : null;
      if (!t) {
        slot.innerHTML = "";
        return;
      }
      const row = t.names.length ? t.names.map((n) => `<span class="${n.anonymous ? "anon" : ""}">${esc(n.who)}</span>`).join(`<span class="sep">\xB7</span>`) : t.standing ? `<span class="standing">${esc(t.standing)}</span>` : "";
      slot.innerHTML = row ? `<div class="gov-plate gov-ticker"><span class="gov-eyebrow">${esc(t.label || "supporters")}</span><div class="names">${row}</div></div>` : "";
      return;
    }
    if (kind === "sky") {
      const bodies = next && Array.isArray(next.bodies) ? next.bodies : [];
      if (!bodies.length) {
        slot.innerHTML = "";
        return;
      }
      const deg = (d) => {
        const whole = Math.floor(d), min = Math.round((d - whole) * 60);
        return `${whole}\xB0${String(min).padStart(2, "0")}\u2032`;
      };
      slot.innerHTML = `<div class="gov-plate gov-sky"><span class="gov-eyebrow">the sky now</span>${bodies.map((b) => `<div class="body"><span class="name">${esc(b.name)}</span><span class="gov-mono where">${esc(b.sign)} ${deg(Number(b.degree) || 0)}${b.retrograde ? `<span class="retro">retro</span>` : ""}</span><span class="gov-mono rate">${(Number(b.perHour) || 0) >= 0 ? "+" : ""}${(Number(b.perHour) || 0).toFixed(2)}\xB0/h</span></div>`).join("")}</div>`;
      return;
    }
    if (kind === "hours") {
      const h = next && next.current ? next : null;
      if (!h) {
        slot.innerHTML = "";
        return;
      }
      const ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"];
      const cell = (c, now) => c ? `<div class="cell ${now ? "now" : ""}"><span class="who">${esc(c.ruler)}</span><span class="gov-mono ord">${ROMAN[c.index] ?? c.index} \xB7 ${c.isNight ? "night" : "day"}</span></div>` : `<div class="cell"><span class="who">\u2014</span></div>`;
      slot.innerHTML = `<div class="gov-plate gov-hours"><span class="gov-eyebrow">planetary hours</span><div class="cells">${cell(h.past, false)}${cell(h.current, true)}${cell(h.next, false)}</div><span class="gov-mono day">the day belongs to ${esc(h.dayRuler || "")}</span></div>`;
      return;
    }
    if (kind === "countdown") {
      const c = next && next.name != null ? next : null;
      const anySlot = slot;
      if (anySlot._tick) {
        window.clearInterval(anySlot._tick);
        anySlot._tick = 0;
      }
      if (!c) {
        slot.innerHTML = "";
        return;
      }
      slot.innerHTML = `<div class="gov-plate gov-countdown"><span class="gov-eyebrow">${esc(c.name)}</span><span class="gov-mono figure" data-figure></span><span class="say" data-say></span></div>`;
      const figure = slot.querySelector("[data-figure]"), say = slot.querySelector("[data-say]");
      if (!c.endsAt) {
        say.textContent = "Open \xB7 no closing date";
        return;
      }
      const offset = Date.now() - new Date(c.now || Date.now()).getTime();
      const ends = new Date(c.endsAt).getTime();
      const paint = () => {
        const left = ends - (Date.now() - offset);
        if (left <= 0) {
          figure.textContent = "";
          say.textContent = "Window closed";
          if (anySlot._tick) {
            window.clearInterval(anySlot._tick);
            anySlot._tick = 0;
          }
          return;
        }
        const s = Math.floor(left / 1e3), d = Math.floor(s / 86400), hh = Math.floor(s % 86400 / 3600), mm = Math.floor(s % 3600 / 60), ss = s % 60;
        figure.textContent = d > 0 ? `${d}d ${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}` : `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`;
        say.textContent = "left";
      };
      paint();
      anySlot._tick = window.setInterval(paint, 1e3);
      return;
    }
    if (kind === "alerts") {
      const events = next && Array.isArray(next.events) ? next.events : [];
      const anySlot = slot;
      if (!anySlot._seen) {
        anySlot._seen = new Set(events.map((e) => e.id));
        anySlot._queue = [];
        if (!slot.querySelector(".gov-alerts")) slot.innerHTML = `<div class="gov-alerts" data-alerts></div>`;
        return;
      }
      const fresh = events.filter((e) => !anySlot._seen.has(e.id));
      fresh.forEach((e) => anySlot._seen.add(e.id));
      anySlot._queue.push(...fresh);
      const box = slot.querySelector("[data-alerts]") ?? (() => {
        slot.innerHTML = `<div class="gov-alerts" data-alerts></div>`;
        return slot.querySelector("[data-alerts]");
      })();
      const money = (e) => e.amountMinor ? `${(e.currency || "").toUpperCase() === "EUR" ? "\u20AC" : (e.currency || "") + " "}${(e.amountMinor / 100).toFixed(2)}` : e.quantity ? `\xD7 ${e.quantity}` : "";
      const showNext = async () => {
        if (anySlot._showing) return;
        const e = anySlot._queue.shift();
        if (!e) return;
        anySlot._showing = true;
        box.innerHTML = `<div class="gov-plate gov-alert ${o.still || o.reduced ? "" : "enter"}"><span class="who">${esc(e.who || "Someone")}</span>${money(e) ? `<span class="gov-mono amount">${esc(money(e))}</span>` : ""}${e.message ? `<span class="message">${esc(e.message)}</span>` : ""}</div>`;
        await wait(6e3);
        box.innerHTML = "";
        anySlot._showing = false;
        if (anySlot._queue.length) showNext();
      };
      showNext();
      return;
    }
    if (kind === "wheel") {
      const src = String(next?.src || "");
      slot.innerHTML = src.startsWith("/overlay/wheel") ? `<iframe class="gov-wheel" src="${esc(src)}" title="transit wheel" loading="eager"></iframe>` : "";
      return;
    }
    if (kind === "build") {
      const b = next && Array.isArray(next.parts) ? next : null;
      if (!b) {
        slot.innerHTML = "";
        return;
      }
      const stroke = Number(getComputedStyle(slot.closest(".gov")).getPropertyValue("--gt-stroke")) || 12;
      const prevPlate = slot.querySelector(".gov-build");
      const wasMet = prevPlate ? Number(prevPlate.dataset.met || 0) : null;
      const metBefore = new Set((prevPlate?.dataset.metSlots || "").split("|").filter(Boolean));
      const flip = prevPlate?.dataset.flip === "a" ? "b" : "a";
      const compact = slot.dataset.shows === "compact";
      const narrow = !compact && slot.clientWidth > 0 && slot.clientWidth < 560;
      const wordOf = (st) => st === "met" ? "met" : st === "partial" ? "partly" : "not yet";
      const ring = (size, count, of) => `<div class="ring" style="width:${size}px;height:${size}px">${sigilSvg(b.parts, stroke, size)}<div class="ring-count"><span class="gov-mono met" style="font-size:${count}px">${esc(b.met)}</span><span class="gov-mono of" style="font-size:${of}px">of ${esc(b.total)}</span></div></div>`;
      if (compact) {
        slot.innerHTML = `<div class="gov-plate gov-build compact" data-met="${esc(b.met)}" data-flip="${flip}"><span class="title">${esc(b.name)}</span>${ring(64, 0, 0)}<span class="gov-mono count">${esc(b.met)} <span class="of">/ ${esc(b.total)}</span></span></div>`;
      } else {
        const chips = narrow ? "" : `<div class="chips">${b.parts.map((p) => `<span class="chip ${esc(p.state === "done" ? "met" : p.state === "now" ? "partly" : "open")}">${esc(p.name)}<span class="gov-mono">${esc(p.met)}/${esc(p.total)}</span></span>`).join("")}</div>`;
        const grid = narrow || !b.gridName || !(b.slots ?? []).length ? "" : `<div class="grid-block"><p class="gov-eyebrow">${esc(b.gridName)}</p><div class="grid">${b.slots.map((sl) => `<span class="cell ${esc(sl.state)}${sl.state === "met" && !metBefore.has(sl.label) && metBefore.size + wasMet > 0 ? ` lit-${flip}` : ""}">${esc(sl.label)}</span>`).join("")}</div></div>`;
        const goals = (b.next ?? []).slice(0, narrow ? 1 : 3);
        const nextBlock = b.complete || !goals.length ? "" : `<div class="next-block">${narrow ? "" : `<p class="gov-eyebrow">Next open goals</p>`}${goals.map((n) => `<div class="goal"><span class="cat">${narrow ? "Next \xB7 " : ""}${esc(n.category)}</span><span class="label">${esc(n.label)}</span>${n.detail ? `<span class="detail">${esc(n.detail)}</span>` : ""}<span class="leader"></span><span class="word ${n.word === "partly" ? "partly" : "open"}">${esc(n.word)}</span></div>`).join("")}</div>`;
        const complete = b.complete ? `<div class="complete-block"><span class="gov-eyebrow rose">Complete</span><span class="sentence">The build is on the character.</span></div>` : "";
        slot.innerHTML = `<div class="gov-plate gov-build${narrow ? " narrow" : ""}" data-met="${esc(b.met)}" data-flip="${flip}" data-met-slots="${esc((b.slots ?? []).filter((x) => x.state === "met").map((x) => x.label).join("|"))}"><div class="head">${ring(narrow ? 120 : 168, narrow ? 34 : 46, narrow ? 14 : 17)}<div class="titles"><p class="gov-eyebrow">${esc(b.eyebrow || "Build")}</p><h2 class="title">${esc(b.name)}</h2>${chips}</div></div>${grid}${nextBlock}${complete}</div>`;
      }
      if (wasMet !== null && Number(b.met) > wasMet && !o.still && !o.reduced) {
        const card = slot.querySelector(".gov-build");
        card.classList.add(`ignite-${flip}`);
      }
      return;
    }
    if (kind === "guide-routine") {
      const r = next?.routine;
      slot.innerHTML = r ? `<div class="gov-plate gov-routine"><div class="head"><span class="name">${esc(r.name)}</span><span class="gov-mono count">${esc(r.count)}</span></div><div>${(r.items ?? []).map((i) => `<div class="item ${i.done ? "done" : ""}"><span class="dot ${i.done ? "done" : "available"}"></span><span>${esc(i.text)}</span></div>`).join("")}</div></div>` : "";
      return;
    }
  }
  return __toCommonJS(overlay_elements_exports);
})();
