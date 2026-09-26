/* The lesson reader's renderer: a lesson's markdown, exactly as FORMAT.md §3
 * (and the writers' tolerated extensions) defines it, to HTML.
 *
 * Isomorphic: the reader renders on the server and the Studio admin's live
 * preview runs the same function in the browser, so the preview is what
 * the reader sees.
 *
 * - `{{kind k=v}}` lines and ```` ```sargam ```` blocks become embeds: a
 *   card with a compact state, hydrated in the browser (client/lesson.ts).
 * - `> [!listen]`, `> [!schools]`, `> [!sources]` become the three quiet boxes.
 * - `[^key]` markers are numbered in order of first use.
 * - `<!-- -->` editor notes are never rendered.
 * - Glossary terms get a dotted underline at their first use only.
 * - An embed the page can't draw becomes a quiet grey box saying what's
 *   missing; it never breaks the page and never hides text.
 */
import { type Script, type TamilStyle, tokenize } from "./notation";
import { phraseHtml } from "./render";

export interface LessonSource { key: string; n: number; cite: string; url?: string | null; research?: string | null; confidence?: string }
export interface GlossaryTerm { term: string; slug: string; definition: string; lesson?: string; aliases?: string[] }
export interface RecordingInfo {
  id: string; available: boolean; label: string; why?: string; provider?: string; url?: string;
  raga?: string | null; clips?: { id: string; start: string; end: string; label: string }[];
}
export interface ExerciseInfo { id: string; kind: string; title?: string; items?: unknown[]; minutes?: number; lesson?: string; [k: string]: unknown }

export interface LessonCtx {
  script: Script;
  tamil?: TamilStyle;
  sources: LessonSource[];
  glossary?: GlossaryTerm[];
  exercises?: Record<string, ExerciseInfo>;
  recordings?: Record<string, RecordingInfo>;
  /** Raga ids → names and scales, for raga and mela cards and embed captions. */
  ragas?: Record<string, { name: string; arohana?: string; avarohana?: string; parent?: string; number?: number }>;
  melas?: Record<number, { name: string; arohana: string; avarohana: string; chakra?: string }>;
  talaNames?: Record<string, string>;
  drillTitles?: Record<string, string>;
  lessonTitles?: Record<string, { title: string; slug: string }>;
  /** Language-aware link builder. */
  href?: (path: string) => string;
  saLabel?: string;
  slug?: string;
}

export interface Rendered {
  html: string;
  toc: { id: string; text: string; level: number }[];
  glossaryUsed: string[];
  embeds: { kind: string; id?: string }[];
}

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const slugify = (s: string) => s.toLowerCase().replace(/<[^>]+>/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

const ATTR = /([a-z_]+)=("([^"]*)"|[^\s}]+)/g;

export function parseAttrs(text: string): Record<string, string> {
  const out: Record<string, string> = {};
  for (const m of text.matchAll(ATTR)) out[m[1]] = m[3] !== undefined ? m[3] : m[2];
  return out;
}

export function stripNotes(body: string): string {
  return body.replace(/<!--[\s\S]*?-->\s*\n?/g, "");
}

export function editorNotes(body: string): string[] {
  return [...body.matchAll(/<!--([\s\S]*?)-->/g)].map((m) => m[1].trim());
}

export function footnoteOrder(body: string): string[] {
  const out: string[] = [];
  for (const m of stripNotes(body).matchAll(/\[\^([A-Za-z0-9_.:-]+)\]/g)) if (!out.includes(m[1])) out.push(m[1]);
  return out;
}

/** Words of prose, for "N min left · words". */
export function countWords(body: string): number {
  const text = stripNotes(body).replace(/```[\s\S]*?```/g, " ").replace(/^\{\{.*\}\}$/gm, " ");
  return (text.match(/[A-Za-z][A-Za-z'’-]*/g) ?? []).length;
}

// ── inline ────────────────────────────────────────────────────────────────

class Inline {
  seen = new Set<string>();
  used: string[] = [];
  private terms: { re: RegExp; t: GlossaryTerm }[];

  constructor(private ctx: LessonCtx) {
    const list: { re: RegExp; t: GlossaryTerm; len: number }[] = [];
    for (const t of ctx.glossary ?? []) {
      for (const w of [t.term, ...(t.aliases ?? [])]) {
        if (!w) continue;
        const src = w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        list.push({ re: new RegExp(`(^|[^A-Za-z])(${src})(?![A-Za-z])`, "i"), t, len: w.length });
      }
    }
    // Longer terms first: "vakra raga" before "raga".
    this.terms = list.sort((a, b) => b.len - a.len);
  }

  /** Plain text: escaped, with the first use of each glossary term marked. */
  plain(text: string, glossary: boolean): string {
    if (!glossary || !this.terms.length) return esc(text);
    let out = "";
    let rest = text;
    // Repeatedly find the earliest unseen term in the remaining text.
    for (;;) {
      let best: { at: number; len: number; t: GlossaryTerm; word: string } | null = null;
      for (const { re, t } of this.terms) {
        if (this.seen.has(t.slug)) continue;
        const m = re.exec(rest);
        if (!m) continue;
        const at = m.index + m[1].length;
        if (!best || at < best.at) best = { at, len: m[2].length, t, word: m[2] };
      }
      if (!best) break;
      out += esc(rest.slice(0, best.at));
      this.seen.add(best.t.slug);
      this.used.push(best.t.slug);
      out += `<button type="button" class="lr-term" data-term="${esc(best.t.slug)}">${esc(best.word)}</button>`;
      rest = rest.slice(best.at + best.len);
    }
    return out + esc(rest);
  }

  render(text: string, glossary = true): string {
    const ctx = this.ctx;
    let out = "";
    let i = 0;
    const re = /(`[^`]+`)|(!\[[^\]]*\]\([^)\s]+\))|(\[\^[A-Za-z0-9_.:-]+\])|(\[[^\]]+\]\([^)\s]+\))|(\*\*[^*]+\*\*)|(\*[^*\s][^*]*\*)|(\b_[^_]+_\b)/g;
    for (const m of text.matchAll(re)) {
      out += this.plain(text.slice(i, m.index), glossary);
      const tok = m[0];
      if (m[1]) out += `<code>${esc(tok.slice(1, -1))}</code>`;
      else if (m[2]) {
        const mm = /^!\[([^\]]*)\]\(([^)]+)\)$/.exec(tok)!;
        out += `<img class="lr-img" src="${esc(mm[2])}" alt="${esc(mm[1])}" loading="lazy">`;
      } else if (m[3]) {
        const key = tok.slice(2, -1);
        const s = ctx.sources.find((x) => x.key === key);
        out += s
          ? `<sup class="lr-fn"><button type="button" data-fn="${esc(key)}" aria-label="Footnote ${s.n}">${s.n}</button></sup>`
          : `<sup class="lr-fn lr-fn-missing" title="Footnote ${esc(key)} has no source">?</sup>`;
      } else if (m[4]) {
        const mm = /^\[([^\]]+)\]\(([^)]+)\)$/.exec(tok)!;
        const url = mm[2];
        const ext = /^https?:/.test(url);
        out += `<a href="${esc(url)}"${ext ? ' rel="noopener nofollow"' : ""}>${this.render(mm[1], false)}</a>`;
      } else if (m[5]) out += `<strong>${this.render(tok.slice(2, -2), glossary)}</strong>`;
      else if (m[6]) out += `<em>${this.render(tok.slice(1, -1), glossary)}</em>`;
      else if (m[7]) out += `<em>${this.render(tok.slice(1, -1), glossary)}</em>`;
      i = (m.index ?? 0) + tok.length;
    }
    return out + this.plain(text.slice(i), glossary);
  }
}

// ── embeds ────────────────────────────────────────────────────────────────

function grey(what: string): string {
  return `<div class="lr-embed lr-fail" role="note"><span class="lr-fail-h">${esc(what)}</span></div>`;
}

const SYNTH = `<span class="lr-synth">synthesised approximation</span>`;

function sargamHtml(lines: string[], attrs: Record<string, string>, ctx: LessonCtx): string {
  const o = { script: ctx.script, tamil: ctx.tamil, subs: true };
  const rows: string[] = [];
  let lastSwaras: string | null = null;
  const pairs: { swaras: string; sahitya: string | null }[] = [];
  for (const raw of lines) {
    const l = raw.trim();
    if (!l) continue;
    if (l.startsWith("~")) {
      if (pairs.length) pairs[pairs.length - 1].sahitya = l.slice(1).trim();
      continue;
    }
    lastSwaras = l;
    pairs.push({ swaras: l, sahitya: null });
  }
  for (const p of pairs) {
    if (p.sahitya) {
      // One syllable or "-" per note or hold; bars in the sahitya line are skipped.
      const syl = p.sahitya.split(/\s+/).filter((x) => x && x !== "|" && x !== "||");
      let k = 0;
      const cells = tokenize(p.swaras).map((t) => {
        if (t.kind === "text" && (t.raw === "|" || t.raw === "||")) return phraseHtml(t.raw, o);
        const s = syl[k++];
        return `<span class="lr-sy-cell">${phraseHtml(t.raw, o)}<span class="lr-sy">${s && s !== "-" ? esc(s) : "&nbsp;"}</span></span>`;
      });
      rows.push(`<div class="lr-sg-row lr-sg-sahitya">${cells.join("")}</div>`);
    } else {
      rows.push(`<div class="lr-sg-row">${phraseHtml(p.swaras, o)}</div>`);
    }
  }
  if (!lastSwaras) return grey("This notation block is empty.");
  const raga = attrs.raga ? ctx.ragas?.[attrs.raga]?.name ?? attrs.raga : "";
  const tala = attrs.tala && attrs.tala !== "none" ? ctx.talaNames?.[attrs.tala] ?? attrs.tala.replace(/_/g, " ") : "no tala";
  const meta = [raga.toLowerCase(), tala].filter(Boolean).join(" · ");
  const all = pairs.map((p) => p.swaras).join(" ");
  const composer = ctx.href ? ctx.href(`/carnatic/compose?line=${encodeURIComponent(all)}${attrs.raga ? `&raga=${attrs.raga}` : ""}${attrs.tala && attrs.tala !== "none" ? `&tala=${attrs.tala}` : ""}`) : "#";
  return `<div class="lr-embed lr-sargam" data-embed="sargam" data-line="${esc(all)}" data-raga="${esc(attrs.raga ?? "")}" data-tala="${esc(attrs.tala ?? "")}" data-speed="${esc(attrs.speed ?? "1")}">`
    + `<div class="lr-sg-top"><button type="button" class="lr-play" data-play aria-label="Play this line">${playIcon}</button><div class="lr-sg-lines">${rows.join("")}</div></div>`
    + `<div class="lr-sg-foot">${attrs.caption ? `<span class="lr-caption">${esc(attrs.caption)}</span>` : ""}${SYNTH}<span class="lr-meta">${esc(meta)}</span>`
    + `<a class="lr-compose" href="${esc(composer)}">Open in composer</a></div></div>`;
}

const playIcon = `<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M5 3l8 5-8 5z" fill="currentColor"/></svg>`;

function droneHtml(attrs: Record<string, string>, ctx: LessonCtx): string {
  const tuning = (attrs.tuning ?? "pa").toLowerCase();
  const name = { pa: "Pa–Sa–Sa–Sa", ma: "Ma–Sa–Sa–Sa", ni: "Ni–Sa–Sa–Sa", mute: "Sa–Sa–Sa, Pa muted" }[tuning] ?? "Pa–Sa–Sa–Sa";
  const seg = (v: string, label: string) => `<button type="button" data-tuning="${v}" aria-pressed="${tuning === v}">${label}</button>`;
  return `<div class="lr-embed lr-drone" data-embed="drone" data-tuning="${esc(tuning)}">`
    + `<button type="button" class="lr-play lr-play-lg" data-drone aria-label="Play the drone">${playIcon}</button>`
    + `<div class="lr-drone-t"><b>Drone · <span data-drone-name>${name}</span></b><span>Sa = ${esc(ctx.saLabel ?? "your Sa")} · synthesised approximation</span></div>`
    + `<div class="lr-seg" role="group" aria-label="Drone tuning">${seg("pa", "Pa")}${seg("ma", "Ma")}${seg("mute", "Mute Pa")}</div></div>`;
}

function recordingHtml(attrs: Record<string, string>, ctx: LessonCtx): string {
  const r = ctx.recordings?.[attrs.id];
  const room = ctx.href ? ctx.href(`/carnatic/listen/recording/${encodeURIComponent(attrs.id)}`) : "#";
  if (!r || !r.available || !r.url) {
    return `<div class="lr-embed lr-rec lr-rec-off" data-embed="recording" data-id="${esc(attrs.id)}">`
      + `<div class="lr-rec-box"><p>This recording isn't available here yet.</p><small>Shruti hasn't approved it for the Listening room, or its link has stopped working. The lesson reads fine without it.</small></div>`
      + `<div class="lr-rec-foot"><b>${esc(attrs.hide_raga === "true" ? "A recording" : r?.label ?? attrs.id)}</b></div></div>`;
  }
  const label = attrs.hide_raga === "true" ? "A recording (the raga is hidden until you guess)" : r.label;
  return `<div class="lr-embed lr-rec" data-embed="recording" data-id="${esc(r.id)}" data-provider="${esc(r.provider ?? "")}" data-url="${esc(r.url)}" data-start="${esc(attrs.start ?? "")}" data-end="${esc(attrs.end ?? "")}" data-hide-raga="${attrs.hide_raga === "true"}">`
    + `<div class="lr-rec-box" data-rec-box><button type="button" class="lr-btn" data-load>Load the recording</button><small>Nothing loads from the provider until you press this.</small></div>`
    + `<div class="lr-rec-foot"><b>${esc(label)}</b>${r.why && attrs.hide_raga !== "true" ? `<span>${esc(r.why)}</span>` : ""}`
    + (attrs.start ? `<span class="lr-meta">${esc(attrs.start)}${attrs.end ? `–${esc(attrs.end)}` : ""}</span>` : "")
    + `<a href="${esc(room)}">Listening room ›</a></div></div>`;
}

function exerciseCard(kind: string, id: string, ctx: LessonCtx): string {
  const ex = ctx.exercises?.[id];
  const href = ctx.href ?? ((p: string) => p);
  if (!ex) return grey(`Exercise ${id} isn't in the course yet.`);
  const title = String(ex.title ?? id);
  if (ex.kind === "tap" || kind === "tap") {
    return `<div class="lr-embed lr-ex" data-embed="tap" data-ex="${esc(id)}"><div class="lr-ex-t"><span class="lr-eyebrow">Tala keeping · ${esc(id)}</span>`
      + `<b>${esc(title)}</b><small>Tap along; perfect, on time, early, late and missed are counted for you only</small></div>`
      + `<button type="button" class="lr-btn" data-expand>Start</button><div class="lr-ex-body" data-ex-body hidden></div></div>`;
  }
  if (ex.kind === "practice") {
    return `<div class="lr-embed lr-ex lr-ex-piece" data-embed="practice" data-ex="${esc(id)}"><div class="lr-ex-t"><span class="lr-eyebrow lr-rose">Practice piece</span>`
      + `<b>${esc(title)}</b><small>Others can read it and reply. Nobody gets a grade.</small></div>`
      + `<a class="lr-link" href="${esc(href(`/carnatic/learn/${ctx.slug}/room/${id}`))}">Read what others wrote</a>`
      + `<a class="lr-btn lr-btn-s" href="${esc(href(`/carnatic/learn/${ctx.slug}/room/${id}/write`))}">Write yours</a></div>`;
  }
  if (ex.kind === "listening") {
    return `<div class="lr-embed lr-ex lr-ex-piece" data-embed="listen" data-ex="${esc(id)}"><div class="lr-ex-t"><span class="lr-eyebrow">Listening analysis</span>`
      + `<b>${esc(title)}</b><small>Timestamped notes on a recording; others reply with a short rubric.</small></div>`
      + `<a class="lr-link" href="${esc(href(`/carnatic/learn/${ctx.slug}/room/${id}`))}">Read analyses</a>`
      + `<a class="lr-btn lr-btn-s" href="${esc(href(`/carnatic/learn/${ctx.slug}/room/${id}/write`))}">Write yours</a></div>`;
  }
  const n = Array.isArray(ex.items) ? ex.items.length : 0;
  const mins = ex.minutes ? `About ${ex.minutes} minutes · ` : "";
  return `<div class="lr-embed lr-ex" data-embed="quiz" data-ex="${esc(id)}"><div class="lr-ex-t"><span class="lr-eyebrow">Test yourself</span>`
    + `<b>${esc(title)}: ${n} question${n === 1 ? "" : "s"}</b><small>${mins}explained after every answer</small></div>`
    + `<button type="button" class="lr-btn" data-expand>Start</button><div class="lr-ex-body" data-ex-body hidden></div></div>`;
}

function drillCard(id: string, ctx: LessonCtx): string {
  const href = ctx.href ?? ((p: string) => p);
  const title = ctx.drillTitles?.[id];
  if (!title) return grey(`Drill ${id} isn't in the ear trainer.`);
  return `<div class="lr-embed lr-ex" data-embed="drill"><div class="lr-ex-t"><span class="lr-eyebrow">Ear training · ${esc(id)}</span>`
    + `<b>${esc(title)}</b><small>Synthesised approximation · about 5 minutes</small></div>`
    + `<a class="lr-btn lr-btn-s" href="${esc(href(`/carnatic/practice/ear/${id}`))}">Start the drill</a></div>`;
}

function ragaCard(attrs: Record<string, string>, ctx: LessonCtx): string {
  const r = ctx.ragas?.[attrs.slug];
  const href = ctx.href ?? ((p: string) => p);
  if (!r) return grey(`The raga ${attrs.slug ?? "?"} isn't in the explorer yet.`);
  const o = { script: ctx.script, tamil: ctx.tamil, subs: true };
  return `<a class="lr-embed lr-card-link" data-embed="raga" href="${esc(href(`/carnatic/ragas/${attrs.slug}`))}"><span class="lr-eyebrow">Raga${r.parent ? ` · ${esc(r.parent)}` : ""}</span>`
    + `<b class="lr-card-h">${esc(r.name)}</b>`
    + (r.arohana ? `<span class="lr-card-sc">${phraseHtml(r.arohana, o)}<span class="lr-meta">arohana</span></span>` : "")
    + (r.avarohana ? `<span class="lr-card-sc">${phraseHtml(r.avarohana, o)}<span class="lr-meta">avarohana</span></span>` : "")
    + `<span class="lr-link">Open the raga page ›</span></a>`;
}

function melaCard(attrs: Record<string, string>, ctx: LessonCtx): string {
  const href = ctx.href ?? ((p: string) => p);
  if (attrs.grid === "true") {
    const hl = new Set((attrs.highlight ?? "").split(",").map((x) => Number(x.trim())).filter(Boolean));
    const cells = Array.from({ length: 72 }, (_, i) => i + 1).map((n) =>
      `<a href="${esc(href(`/carnatic/ragas/melakarta/${n}`))}" class="${hl.has(n) ? "on" : ""}" title="${esc(ctx.melas?.[n]?.name ?? String(n))}">${n}</a>`);
    return `<div class="lr-embed lr-mela-grid" data-embed="mela"><span class="lr-eyebrow">The 72 melakartas</span><div class="lr-grid72">${cells.join("")}</div></div>`;
  }
  const n = Number(attrs.n);
  const m = ctx.melas?.[n];
  if (!m) return grey(`Melakarta ${attrs.n ?? "?"} isn't in the data.`);
  const o = { script: ctx.script, tamil: ctx.tamil, subs: true };
  return `<a class="lr-embed lr-card-link" data-embed="mela" href="${esc(href(`/carnatic/ragas/melakarta/${n}`))}"><span class="lr-eyebrow">Melakarta ${n}${m.chakra ? ` · ${esc(m.chakra)} chakra` : ""} · a scale, not a raga</span>`
    + `<b class="lr-card-h">${esc(m.name)}</b><span class="lr-card-sc">${phraseHtml(m.arohana, o)}</span><span class="lr-card-sc">${phraseHtml(m.avarohana, o)}</span></a>`;
}

function talaCard(attrs: Record<string, string>, ctx: LessonCtx): string {
  const href = ctx.href ?? ((p: string) => p);
  const name = ctx.talaNames?.[attrs.id] ?? (attrs.id ?? "").replace(/_/g, " ");
  if (!attrs.id) return grey("A tala tag needs id=.");
  const bits = [attrs.nadai && `nadai ${attrs.nadai}`, attrs.kalai && `${attrs.kalai} kalai`, attrs.speed && `speed ${attrs.speed}`,
    attrs.eduppu && `starts ${attrs.eduppu} after samam`, attrs.tempo && `${attrs.tempo} a minute`].filter(Boolean).join(" · ");
  const q = new URLSearchParams({ tala: attrs.id, ...(attrs.mode ? { mode: attrs.mode } : {}), ...(attrs.nadai ? { nadai: attrs.nadai } : {}) });
  return `<div class="lr-embed lr-tala" data-embed="tala" data-tala="${esc(attrs.id)}" data-nadai="${esc(attrs.nadai ?? "")}" data-tempo="${esc(attrs.tempo ?? "")}">`
    + `<div class="lr-tala-grid" data-tala-grid></div><div class="lr-tala-foot"><b>${esc(name)}</b>${bits ? `<span class="lr-meta">${esc(bits)}</span>` : ""}`
    + `<a class="lr-btn lr-btn-s" href="${esc(href(`/carnatic/practice/tala?${q}`))}">Open the trainer</a></div></div>`;
}

function gamakaCard(attrs: Record<string, string>, ctx: LessonCtx): string {
  const href = ctx.href ?? ((p: string) => p);
  if (!attrs.name) return grey("A gamaka tag needs name=.");
  const on = attrs.on ? ` on ${attrs.on}` : "";
  const line = attrs.on ? `${attrs.name}:${attrs.on}` : `${attrs.name}:G3`;
  return `<div class="lr-embed lr-sargam" data-embed="sargam" data-line="${esc(line)}" data-raga="${esc(attrs.raga ?? "")}">`
    + `<div class="lr-sg-top"><button type="button" class="lr-play" data-play aria-label="Play the gamaka">${playIcon}</button>`
    + `<div class="lr-sg-lines"><div class="lr-sg-row">${phraseHtml(line, { script: ctx.script, tamil: ctx.tamil, subs: true })}</div></div></div>`
    + `<div class="lr-sg-foot"><span class="lr-caption">${esc(attrs.name)}${esc(on)}</span>${SYNTH}<a class="lr-compose" href="${esc(href(`/carnatic/gamakas#${attrs.name}`))}">In the gamaka library</a></div></div>`;
}

function konnakolCard(attrs: Record<string, string>, ctx: LessonCtx): string {
  const pattern = attrs.pattern ?? "";
  if (!pattern && !attrs.example) return grey("A konnakol tag needs pattern= or example=.");
  const syl = pattern.split(/\s+/).filter(Boolean);
  const tala = attrs.tala ? ctx.talaNames?.[attrs.tala] ?? attrs.tala.replace(/_/g, " ") : "";
  return `<div class="lr-embed lr-konnakol" data-embed="konnakol" data-pattern="${esc(pattern)}" data-tala="${esc(attrs.tala ?? "")}" data-nadai="${esc(attrs.nadai ?? "4")}">`
    + `<div class="lr-kn-row">${syl.length ? syl.map((s) => `<span class="${s === "," ? "gap" : ""}">${s === "," ? "·" : esc(s)}</span>`).join("") : `<span>${esc(attrs.example ?? "")}</span>`}</div>`
    + `<div class="lr-sg-foot"><button type="button" class="lr-play" data-konnakol aria-label="Play the syllables">${playIcon}</button><span class="lr-caption">Konnakol${tala ? ` · ${esc(tala)}` : ""}${attrs.nadai ? ` · nadai ${esc(attrs.nadai)}` : ""}${attrs.start ? ` · from matra ${esc(attrs.start)}` : ""}</span><span class="lr-synth">click and pitch cues</span></div></div>`;
}

function tunerCard(attrs: Record<string, string>, ctx: LessonCtx): string {
  const href = ctx.href ?? ((p: string) => p);
  return `<div class="lr-embed lr-tuner" data-embed="tuner" data-raga="${esc(attrs.raga ?? "")}">`
    + `<div class="lr-tuner-t"><b>Tuner</b><div class="lr-tuner-bar" data-tuner-bar><i data-tuner-needle></i></div><small data-tuner-note>Needs the microphone. Wear headphones if the drone is on.</small></div>`
    + `<button type="button" class="lr-btn lr-btn-s" data-tuner>Start tuner</button><a class="lr-link lr-tuner-more" href="${esc(href("/carnatic/practice/tuner"))}">Full tuner ›</a></div>`;
}

function composerCard(attrs: Record<string, string>, ctx: LessonCtx): string {
  const href = ctx.href ?? ((p: string) => p);
  const q = new URLSearchParams(Object.fromEntries(Object.entries({ line: attrs.line, raga: attrs.raga, tala: attrs.tala }).filter(([, v]) => v)) as Record<string, string>);
  return `<div class="lr-embed lr-ex" data-embed="composer"><div class="lr-ex-t"><span class="lr-eyebrow">Composer</span><b>Try it in the composer</b>`
    + (attrs.line ? `<span class="lr-card-sc">${phraseHtml(attrs.line, { script: ctx.script, tamil: ctx.tamil, subs: true })}</span>` : "")
    + `</div><a class="lr-btn lr-btn-s" href="${esc(href(`/carnatic/compose?${q}`))}">Open in composer</a></div>`;
}

export function embedHtml(kind: string, attrs: Record<string, string>, ctx: LessonCtx): string {
  switch (kind) {
    case "drone": return droneHtml(attrs, ctx);
    case "sargam": return attrs.line ? sargamHtml([attrs.line, ...(attrs.sahitya ? [`~ ${attrs.sahitya}`] : [])], attrs, ctx) : grey("A sargam tag needs line=\"…\".");
    case "recording": return attrs.id ? recordingHtml(attrs, ctx) : grey("A recording tag needs id=.");
    case "quiz": case "tap": return attrs.id ? exerciseCard(kind, attrs.id, ctx) : grey(`A ${kind} tag needs id=.`);
    case "practice": case "listen": return attrs.id ? exerciseCard(kind, attrs.id, ctx) : grey(`A ${kind} tag needs id=.`);
    case "drill": return attrs.id ? drillCard(attrs.id, ctx) : grey("A drill tag needs id=.");
    case "raga": return ragaCard(attrs, ctx);
    case "mela": return melaCard(attrs, ctx);
    case "tala": return talaCard(attrs, ctx);
    case "gamaka": return gamakaCard(attrs, ctx);
    case "konnakol": return konnakolCard(attrs, ctx);
    case "tuner": return tunerCard(attrs, ctx);
    case "composer": return composerCard(attrs, ctx);
    default: return grey(`{{${kind}}} isn't something this page can show yet.`);
  }
}

// ── blocks ────────────────────────────────────────────────────────────────

const BOX = { listen: "What to listen for", schools: "Some schools", sources: "Sources differ" } as const;

export function renderLesson(body: string, ctx: LessonCtx): Rendered {
  const inl = new Inline(ctx);
  const lines = stripNotes(body).replace(/\r\n/g, "\n").split("\n");
  const out: string[] = [];
  const toc: Rendered["toc"] = [];
  const embeds: Rendered["embeds"] = [];
  const ids = new Set<string>();
  let para: string[] = [];

  const flush = () => {
    if (para.length) out.push(`<p>${inl.render(para.join(" "))}</p>`);
    para = [];
  };
  const isBlockStart = (l: string) => /^(#{2,4} |> |[-*] |\d+\. |\|.*\||```|\{\{)/.test(l.trim());

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const t = line.trim();
    if (!t) { flush(); continue; }

    // Fenced blocks: ```sargam … ``` is an embed; others are plain code.
    if (t.startsWith("```")) {
      flush();
      const info = t.slice(3).trim();
      const inner: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith("```")) inner.push(lines[i++]);
      if (info.startsWith("sargam")) {
        embeds.push({ kind: "sargam" });
        out.push(sargamHtml(inner, parseAttrs(info.slice(6)), ctx));
      } else out.push(`<pre class="lr-pre"><code>${esc(inner.join("\n"))}</code></pre>`);
      continue;
    }

    // An embed tag alone on its line.
    const em = /^\{\{\s*([a-z]+)([^}]*)\}\}$/.exec(t);
    if (em) {
      flush();
      const attrs = parseAttrs(em[2] ?? "");
      embeds.push({ kind: em[1], id: attrs.id });
      out.push(embedHtml(em[1], attrs, ctx));
      continue;
    }

    const h = /^(#{2,4})\s+(.+)$/.exec(t);
    if (h) {
      flush();
      const level = h[1].length;
      let id = slugify(h[2]) || "section";
      while (ids.has(id)) id += "-2";
      ids.add(id);
      if (level <= 3) toc.push({ id, text: h[2].replace(/\*|`/g, ""), level });
      out.push(`<h${level} id="${id}" data-heading>${inl.render(h[2], false)}</h${level}>`);
      continue;
    }

    if (t.startsWith(">")) {
      flush();
      const quote: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith(">")) quote.push(lines[i++].trim().replace(/^>\s?/, ""));
      i--;
      const box = /^\[!(listen|schools|sources)\]\s*(.*)$/.exec(quote[0] ?? "");
      if (box) {
        const kind = box[1] as keyof typeof BOX;
        const rest = [box[2], ...quote.slice(1)].join("\n").trim();
        const paras = rest.split(/\n\s*\n/).map((p) => `<p>${inl.render(p.replace(/\n/g, " "))}</p>`).join("");
        out.push(`<aside class="lr-box lr-box-${kind}"><span class="lr-box-h">${BOX[kind]}</span>${paras}</aside>`);
      } else {
        out.push(`<blockquote>${quote.join("\n").split(/\n\s*\n/).map((p) => `<p>${inl.render(p.replace(/\n/g, " "))}</p>`).join("")}</blockquote>`);
      }
      continue;
    }

    if (/^([-*]|\d+\.)\s+/.test(t)) {
      flush();
      const ordered = /^\d+\./.test(t);
      const items: string[] = [];
      while (i < lines.length) {
        const l = lines[i];
        const lt = l.trim();
        if (/^([-*]|\d+\.)\s+/.test(lt) && (ordered ? /^\d+\./.test(lt) : /^[-*]/.test(lt)) && !/^\s{2,}/.test(l)) {
          items.push(lt.replace(/^([-*]|\d+\.)\s+/, ""));
        } else if (lt && /^\s{2,}/.test(l) && items.length) {
          items[items.length - 1] += " " + lt.replace(/^([-*]|\d+\.)\s+/, "");
        } else break;
        i++;
      }
      i--;
      const tag = ordered ? "ol" : "ul";
      out.push(`<${tag}>${items.map((x) => `<li>${inl.render(x)}</li>`).join("")}</${tag}>`);
      continue;
    }

    if (t.startsWith("|") && i + 1 < lines.length && /^\|?\s*:?-{3,}/.test(lines[i + 1].trim())) {
      flush();
      const row = (l: string) => l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
      const head = row(t);
      i += 2;
      const body: string[][] = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) body.push(row(lines[i++]));
      i--;
      out.push(`<div class="lr-table"><table><thead><tr>${head.map((c) => `<th>${inl.render(c, false)}</th>`).join("")}</tr></thead>`
        + `<tbody>${body.map((r) => `<tr>${r.map((c) => `<td>${inl.render(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
      continue;
    }

    if (para.length && isBlockStart(t)) flush();
    para.push(t);
  }
  flush();
  return { html: out.join("\n"), toc, glossaryUsed: inl.used, embeds };
}

/** The confidence line under a footnote (README_v2 §4). High shows nothing. */
export function confidenceLine(c?: string | null): string {
  if (!c || c === "high") return "";
  return c === "low" ? "One source, or our own reasoning" : "Sources differ, or rest on a single discussion";
}
