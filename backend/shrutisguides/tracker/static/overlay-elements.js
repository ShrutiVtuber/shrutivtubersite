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
  var overlay_elements_exports = {};
  __export(overlay_elements_exports, {
    drawElement: () => drawElement,
    sigilSvg: () => sigilSvg
  });
  const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  const wait = (ms) => new Promise((r) => window.setTimeout(r, ms));
  const arcD = (r, a0, a1) => {
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
    if (kind === "guide-routine") {
      const r = next?.routine;
      slot.innerHTML = r ? `<div class="gov-plate gov-routine"><div class="head"><span class="name">${esc(r.name)}</span><span class="gov-mono count">${esc(r.count)}</span></div><div>${(r.items ?? []).map((i) => `<div class="item ${i.done ? "done" : ""}"><span class="dot ${i.done ? "done" : "available"}"></span><span>${esc(i.text)}</span></div>`).join("")}</div></div>` : "";
      return;
    }
  }
  return __toCommonJS(overlay_elements_exports);
})();
