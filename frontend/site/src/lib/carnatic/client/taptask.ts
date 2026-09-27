/* The tap task (FORMAT.md §4b, SELF_TEST.md §3; README_v2 §5): keep tala
 * against the app, format 2.
 *
 * - `segments` (avartanams at one speed and nadai, played without stopping
 *   the tala), or `speed`, `nadai` and `avartanams` for one segment.
 * - `targets`, one or more of claps, every_count, samam, syllables, entry,
 *   landing, nadai_change.
 * - `plays`: {abhyasa}, {line, raga}, {konnakol}, {example}; {recording}
 *   belongs to the Listening room's tap-along.
 * - `fade: [all, claps, samam, none]`, one step per equal share;
 *   `dropout: [1, 3]` silences one to three avartanams and scores the first
 *   samam after each gap; `variants` the learner chooses from; `tempo_range`;
 *   `window_ms`.
 *
 * The five counts (perfect ±30 ms, on time ±80 ms, early, late, missed; at
 * dense targets the window shrinks to 40 % of the gap), the personal best at
 * this step, and "Start by tapping". A tap on a count that isn't scored is
 * shown ("that count is a finger count"), never counted against anyone.
 */
import { blip, ctx, talaSound } from "./audio";
import { attempts, recordAttempt } from "./learner";
import { playLine } from "./phrase";
import { settings } from "./state";
import { pitchHz } from "../notation";
import { judge, type Gesture } from "../gestures";
import { attachPad, clapsOnly, clapsOnlyToggle } from "./tappad";

export interface Segment { avartanams: number; speed?: number; nadai?: number }
export interface TapSpec {
  id: string; title?: string; tala: string; tempo?: number; tempo_range?: number[]; speed?: number; nadai?: number;
  eduppu?: number; avartanams?: number; segments?: Segment[]; targets?: string[]; count_in?: number; fade?: string[];
  dropout?: number[]; variants?: Partial<TapSpec>[]; window_ms?: { perfect?: number; on_time?: number };
  plays?: { abhyasa?: string; line?: string; raga?: string; konnakol?: string; example?: string; recording?: string };
}

interface Count { n: number; action: "clap" | "finger" | "wave" | "silent"; samam?: boolean; anga?: number; angaName?: string; finger?: string }

const PHASES: Record<string, { title: string; sub: string }> = {
  all: { title: "All cues", sub: "clap, wave, fingers" },
  syllables: { title: "Syllables", sub: "what plays, no cues" },
  claps: { title: "Claps only", sub: "no finger counts" },
  samam: { title: "Samam only", sub: "one click a cycle" },
  none: { title: "Nothing", sub: "you keep it" },
};

const esc = (s: string) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;");

export interface TapData {
  counts: Count[]; talaName: string; defaultNadai: number;
  /** What plays: notes (a notation line's tokens) or syllables, one per unit. */
  melody?: string[]; syllables?: string[]; raga?: string;
  /** A konnakol example's events: the matra of each syllable and where it lands. */
  landingMatra?: number;
}

let talasP: Promise<any> | null = null;
let lessonsP: Promise<any> | null = null;
const talas = () => (talasP ??= fetch("/api/carnatic/data/talas.json").then((r) => (r.ok ? r.json() : null)).catch(() => null));
const abhyasa = () => (lessonsP ??= fetch("/api/carnatic/data/lessons.json").then((r) => (r.ok ? r.json() : null)).catch(() => null));

export async function tapData(spec: TapSpec): Promise<TapData> {
  const t = await talas();
  const tala = [...(t?.practical ?? []), ...(t?.suladi ?? [])].find((x: any) => x.id === spec.tala);
  const counts: Count[] = tala?.counts ?? Array.from({ length: 8 }, (_, i) => ({ n: i + 1, action: i === 0 || i === 4 || i === 6 ? "clap" : i === 5 || i === 7 ? "wave" : "finger", samam: i === 0 })) as Count[];
  const out: TapData = { counts, talaName: tala?.name ?? spec.tala.replace(/_/g, " "), defaultNadai: Number(tala?.grid?.default_gati ?? 4) };
  const p = spec.plays ?? {};
  if (p.abhyasa) {
    const l = await abhyasa();
    for (const set of l?.sets ?? []) for (const item of set.items ?? []) {
      if (item.id === p.abhyasa) out.melody = item.sections.flatMap((s: any) => s.lines.flatMap((ln: any) => ln.segments.flat()));
    }
  } else if (p.line) {
    out.melody = p.line.split(/\s+/).filter((x) => x && x !== "|" && x !== "||");
    out.raga = p.raga;
  } else if (p.konnakol) {
    out.syllables = p.konnakol.split(/\s+/).filter(Boolean);
  } else if (p.example) {
    const ex = (t?.konnakol?.examples ?? []).find((x: any) => x.id === p.example);
    if (ex) {
      out.syllables = ex.events.map((e: any) => e.syllable);
      out.landingMatra = Number(ex.matras_per_avartanam ?? 32) * Math.ceil(ex.events.length / Number(ex.matras_per_avartanam ?? 32));
    }
  }
  return out;
}

const UNITS: Record<number, number> = { 1: 1, 2: 2, 3: 4, 4: 8 };

export class TapTask {
  private tempo: number;
  private running = false;
  private targets: { at: number; kind: string; hit?: number; anga?: number; want: string }[] = [];
  private detach: (() => void) | null = null;
  private timer = 0;
  private t0 = 0;
  private started = "";

  constructor(private root: HTMLElement, private spec: TapSpec, private data: TapData, private onVariant?: (i: number) => void, private variant = 0) {
    this.tempo = Number(spec.tempo ?? (spec.tempo_range ? spec.tempo_range[0] + 10 : 60));
    this.draw();
  }

  private get fade(): string[] {
    const f = this.spec.fade;
    return f?.length ? f : ["all"];
  }
  private get countIn() { return Number(this.spec.count_in ?? 1); }
  private get targetKinds(): string[] { return this.spec.targets?.length ? this.spec.targets : ["claps"]; }
  private segments(): Segment[] {
    if (this.spec.segments?.length) return this.spec.segments;
    return [{ avartanams: Number(this.spec.avartanams ?? 4), speed: this.spec.speed, nadai: this.spec.nadai }];
  }
  private get avartanams() { return this.segments().reduce((n, s) => n + Number(s.avartanams || 1), 0); }

  private meta(): string {
    const segs = this.segments();
    const speeds = [...new Set(segs.map((s) => s.speed ?? 1))];
    const nadais = segs.map((s) => s.nadai ?? this.data.defaultNadai);
    return [this.data.talaName, `${this.tempo} a minute`, this.data.melody ? `speed ${speeds.join(", ")}` : "",
      `${this.avartanams} avartanam${this.avartanams === 1 ? "" : "s"}`, `count-in ${this.countIn}`,
      new Set(nadais).size > 1 ? `nadai ${nadais.join(" → ")}` : "", this.spec.eduppu ? `entry ${this.spec.eduppu} after samam` : "",
      this.spec.dropout ? `the audio drops out for ${this.spec.dropout.join(" to ")} avartanams` : ""].filter(Boolean).join(" · ");
  }

  private draw(result?: Record<string, number>, bestLine?: string, advice?: [string, string]) {
    const phases = this.fade.length > 1
      ? `<div class="tt-phases" role="list">${this.fade.map((id) => `<div class="tt-phase" role="listitem" data-phase="${id}"><b>${PHASES[id]?.title ?? id}</b><small>${PHASES[id]?.sub ?? ""}</small></div>`).join("")}</div>` : "";
    const variants = this.spec.variants?.length && !result
      ? `<div class="tt-variants" role="group" aria-label="Version">${this.spec.variants.map((v, i) => `<button type="button" class="ex-pad-s" data-variant="${i}" aria-pressed="${i === this.variant}">${esc(variantLabel(v, this.spec))}</button>`).join("")}</div>` : "";
    const range = this.spec.tempo_range;
    const tempo = range && !result ? `<div class="tt-tempo"><button type="button" class="ex-pad-s" data-tempo="-4" aria-label="Slower">−</button><span>${this.tempo} a minute</span><button type="button" class="ex-pad-s" data-tempo="4" aria-label="Faster">+</button><small>${range[0]}-${range[1]}</small></div>` : "";
    const scores = result ? `<div class="tt-scores">${[["perfect", "perfect"], ["onTime", "on time"], ["early", "early"], ["late", "late"], ["missed", "missed"]]
      .map(([k, l]) => `<div><b>${result[k] ?? 0}</b><small>${l}</small></div>`).join("")}</div>` : "";
    this.root.innerHTML = `<p class="tt-meta">${esc(this.meta())}</p>${variants}${tempo}${phases}`
      + (result ? `${scores}<p class="tt-best">${esc(bestLine ?? "")}</p>`
        + (advice ? `<div class="ex-explain"><p class="ex-verdict">${esc(advice[0])}</p><p>${esc(advice[1])}</p></div>` : "")
        : `<button type="button" class="tt-pad" data-pad>Start by tapping here, or press the space bar</button><p class="tt-note" data-note></p>`)
      + `<div class="ex-actions">${result ? `<button type="button" class="ex-btn ex-btn-s" data-again>Again</button><button type="button" class="ex-btn" data-step>Again, one step on</button>`
        : `<button type="button" class="ex-btn" data-go>Count me in</button>`}</div>`;
    this.root.querySelector("[data-go]")?.addEventListener("click", () => this.start());
    this.root.querySelector("[data-again]")?.addEventListener("click", () => this.draw());
    this.root.querySelectorAll<HTMLElement>("[data-variant]").forEach((b) => b.addEventListener("click", () => this.onVariant?.(Number(b.dataset.variant))));
    this.root.querySelectorAll<HTMLElement>("[data-tempo]").forEach((b) => b.addEventListener("click", () => {
      const r = this.spec.tempo_range ?? [40, 140];
      this.tempo = Math.max(r[0], Math.min(r[1], this.tempo + Number(b.dataset.tempo)));
      this.draw();
    }));
    this.root.querySelector("[data-step]")?.addEventListener("click", () => {
      const r = this.spec.tempo_range ?? [40, 140];
      this.tempo = Math.min(Number(r[1] ?? 140), this.tempo + 6);
      this.draw();
    });
    const pad = this.root.querySelector<HTMLElement>("[data-pad]");
    this.detach?.();
    this.detach = null;
    if (pad) {
      const hint = document.createElement("p");
      hint.className = "tt-hint";
      pad.insertAdjacentElement("afterend", hint);
      this.detach = attachPad(pad, { onTap: (kind, at) => this.tap(kind, at), hint });
      hint.insertAdjacentElement("afterend", clapsOnlyToggle(() => this.draw()));
    }
  }

  private start() {
    const ac = ctx();
    const counts = this.data.counts;
    const beat = 60 / this.tempo;
    const n = counts.length;
    this.t0 = ac.currentTime + 0.3;
    this.started = new Date().toISOString();
    this.targets = [];
    this.running = true;
    const total = this.countIn + this.avartanams;
    const fade = this.fade;
    const kinds = this.targetKinds;
    const s = settings();
    const saHz = pitchHz(s.sa || "C3");
    // dropout: gaps of 1 to 3 avartanams, never in the count-in or the first scored avartanam
    const silent = new Set<number>();
    const after = new Set<number>();
    if (this.spec.dropout) {
      const [lo, hi] = this.spec.dropout;
      let av = this.countIn + 1;
      while (av < total - 1) {
        const len = lo + Math.floor(Math.random() * (hi - lo + 1));
        if (av + len >= total) break;
        for (let k = 0; k < len; k++) silent.add(av + k);
        after.add(av + len);
        av += len + 2;
      }
    }
    // the segment of each avartanam
    const segOf: Segment[] = [];
    for (const seg of this.segments()) for (let k = 0; k < Number(seg.avartanams || 1); k++) segOf.push(seg);
    let mi = 0, si = 0;
    let prevNadai = segOf[0]?.nadai ?? this.data.defaultNadai;
    for (let av = 0; av < total; av++) {
      const scored = av >= this.countIn;
      const k = av - this.countIn;
      const seg = segOf[Math.max(0, k)] ?? segOf[segOf.length - 1] ?? { avartanams: 1 };
      const nadai = Number(seg.nadai ?? this.data.defaultNadai);
      const speed = Number(seg.speed ?? 1);
      const phase = !scored ? "all" : fade[Math.min(fade.length - 1, Math.floor((k * fade.length) / this.avartanams))];
      const quiet = silent.has(av);
      const avStart = this.t0 + av * n * beat;
      if (scored && nadai !== prevNadai && kinds.includes("nadai_change")) this.targets.push({ at: avStart, kind: "nadai_change", anga: 0, want: "any" });
      if (scored) prevNadai = nadai;
      for (let i = 0; i < n; i++) {
        const c = counts[i];
        const at = avStart + i * beat;
        if (!quiet) {
          if (phase === "all") talaSound(c.action, at, { samam: c.samam, finger: c.finger });
          else if (phase === "claps" && c.action === "clap") talaSound("clap", at, { samam: c.samam });
          else if (phase === "samam" && i === 0) talaSound("clap", at, { samam: true });
          // the nadai heard as subdivisions when it isn't the tala's default, or changes
          if (nadai !== this.data.defaultNadai && !this.data.syllables) for (let m = 0; m < nadai; m++) blip(m === 0 ? 1320 : 990, at + (m * beat) / nadai, 0.03, 0.03);
        }
        if (!scored) continue;
        // With whole-hand gestures each count of the hand is a target of its own kind; claps only keeps the claps.
        if (kinds.includes("claps") && c.action === "clap") this.targets.push({ at, kind: "clap", anga: c.anga, want: "clap" });
        else if (kinds.includes("claps") && !clapsOnly() && (c.action === "finger" || c.action === "wave")) this.targets.push({ at, kind: c.action, anga: c.anga, want: c.action });
        else if (kinds.includes("every_count") && c.action !== "silent") this.targets.push({ at, kind: "count", anga: c.anga, want: "any" });
        if (kinds.includes("samam") && i === 0 && (!this.spec.dropout || after.has(av))) this.targets.push({ at, kind: "samam", anga: 0, want: "any" });
      }
      if (quiet || !scored && !this.data.syllables && !this.data.melody) continue;
      const startAt = avStart + (av === this.countIn && this.spec.eduppu ? Number(this.spec.eduppu) * beat : 0);
      if (this.data.melody && scored) {
        const per = n * UNITS[speed];
        const unit = beat / UNITS[speed];
        const fromEduppu = av === this.countIn && this.spec.eduppu ? Math.round(Number(this.spec.eduppu) * UNITS[speed]) : 0;
        const line = Array.from({ length: per - fromEduppu }, () => this.data.melody![mi++ % this.data.melody!.length]).join(" ");
        playLine(line, { saHz, tuning: s.playbackTuning, unit, at: startAt, scale: undefined });
        if (av === this.countIn && kinds.includes("entry")) this.targets.push({ at: startAt, kind: "entry", anga: 0, want: "any" });
      }
      if (this.data.syllables && scored) {
        const per = n * nadai;
        for (let m = 0; m < per && si < this.data.syllables.length; m++, si++) {
          const syl = this.data.syllables[si];
          const at = avStart + (m * beat) / nadai;
          if (syl === "," || syl === "-") continue;
          if (phase !== "none") blip(m % nadai === 0 ? 1320 : 990, at, 0.04, 0.06);
          if (kinds.includes("syllables")) this.targets.push({ at, kind: "syllable", anga: 0, want: "any" });
        }
      }
    }
    if (kinds.includes("landing") && this.data.syllables) {
      const matras = this.data.landingMatra ?? this.data.syllables.length;
      const nadai = Number(segOf[0]?.nadai ?? this.data.defaultNadai);
      this.targets.push({ at: this.t0 + this.countIn * n * beat + (matras / nadai) * beat, kind: "landing", anga: 0, want: "any" });
    }
    this.targets.sort((a, b) => a.at - b.at);
    const end = this.t0 + total * n * beat + 0.4;
    const phaseEls = [...this.root.querySelectorAll<HTMLElement>("[data-phase]")];
    const pad = this.root.querySelector<HTMLElement>("[data-pad]");
    if (pad) pad.textContent = "Tap";
    const note = this.root.querySelector<HTMLElement>("[data-note]");
    const tick = () => {
      const now = ctx().currentTime;
      const av = Math.floor((now - this.t0) / (n * beat));
      const k = av - this.countIn;
      if (note && !note.dataset.keep) note.textContent = av < this.countIn ? "Counting in…" : silent.has(av) ? "The audio is out: keep going." : "";
      const p = k < 0 ? -1 : Math.min(fade.length - 1, Math.floor((k * fade.length) / this.avartanams));
      phaseEls.forEach((el, i) => el.classList.toggle("is-on", i === p));
      if (now >= end) { window.clearInterval(this.timer); this.finish(); }
    };
    this.timer = window.setInterval(tick, 60);
  }

  private tap(kind: Gesture = "clap", at?: number) {
    if (!this.running) { this.start(); return; }
    const now = at ?? ctx().currentTime;
    const beat = 60 / this.tempo;
    const gaps = this.targets.slice(1).map((t, i) => t.at - this.targets[i].at).filter((x) => x > 0.001);
    const dense = gaps.length ? Math.min(...gaps) : beat;
    const onTime = (this.spec.window_ms?.on_time ?? 80) / 1000;
    const win = Math.min(onTime, 0.4 * dense);
    let best: typeof this.targets[number] | null = null;
    for (const t of this.targets) if (t.hit === undefined && (!best || Math.abs(now - t.at) < Math.abs(now - best.at))) best = t;
    const note = this.root.querySelector<HTMLElement>("[data-note]");
    const reach = best?.kind === "nadai_change" ? beat / 2 : Math.max(0.25, dense / 2);
    const n = this.data.counts.length;
    const count = this.data.counts[((Math.round((now - this.t0) / beat) % n) + n) % n];
    if (!best || Math.abs(now - best.at) > reach) {
      // Nothing scored here: a silent count (or, claps only, a finger count or wave) is shown, not scored.
      if (note && count && this.targetKinds.includes("claps")) {
        note.textContent = count.action === "clap" ? "" : `That count is ${count.action === "finger" ? "a finger count" : count.action === "wave" ? "a wave" : "silent"}: shown, not scored.`;
      }
      return;
    }
    const verdict = judge(kind, { kind: best.want }, clapsOnly());
    if (!verdict.ok) { if (note) note.textContent = verdict.note; return; }
    if (note) note.textContent = "";
    best.hit = (now - best.at) * 1000;
    // A nadai change is right within half a count; the others use the timing windows.
    if (best.kind === "nadai_change") best.hit = Math.abs(best.hit) <= beat * 500 ? Math.sign(best.hit) * Math.min(Math.abs(best.hit), 80) : best.hit;
    else if (Math.abs(best.hit) > win * 1000 && Math.abs(best.hit) <= onTime * 1000) best.hit = Math.sign(best.hit) * (onTime * 1000 + 1);
  }

  private finish() {
    this.running = false;
    const perfectMs = this.spec.window_ms?.perfect ?? 30;
    const onTimeMs = this.spec.window_ms?.on_time ?? 80;
    const r = { perfect: 0, onTime: 0, early: 0, late: 0, missed: 0 };
    const earlyByAnga: Record<string, number> = {};
    for (const t of this.targets) {
      if (t.hit === undefined) { r.missed++; continue; }
      const a = Math.abs(t.hit);
      if (a <= perfectMs) r.perfect++;
      else if (a <= onTimeMs) r.onTime++;
      else if (t.hit < 0) { r.early++; earlyByAnga[String(t.anga ?? 0)] = (earlyByAnga[String(t.anga ?? 0)] ?? 0) + 1; }
      else r.late++;
    }
    const of = this.targets.length;
    const good = r.perfect + r.onTime;
    const itemId = this.spec.id;
    const prev = attempts({ itemId, kind: "tap" }).filter((a) => a.result.tempo === this.tempo && (a.result.variant ?? 0) === this.variant)
      .map((a) => (a.result.perfect ?? 0) + (a.result.onTime ?? 0));
    recordAttempt({ itemId, kind: "tap", startedAt: this.started, seconds: Math.round((60 / this.tempo) * this.data.counts.length * (this.countIn + this.avartanams)),
                    result: { tempo: this.tempo, variant: this.variant, ...r, of } });
    const best = prev.length ? Math.max(...prev) : null;
    const bestLine = best === null ? `First time at this step: ${good} perfect or on time out of ${of}.`
      : `Personal best at this step: ${best} perfect or on time out of ${of}. Today: ${good}.`;
    const drutamEarly = (earlyByAnga["1"] ?? 0) + (earlyByAnga["2"] ?? 0);
    const advice: [string, string] = r.early > r.late && r.early >= 2
      ? drutamEarly > r.early / 2
        ? ["Early in the drutams.", "Most early taps come in the drutams, where there's no finger count to lean on. Try counting \"one-and\" inside each drutam."]
        : ["A little early.", "The taps run ahead of the clap. Let the clap land before you move, and keep the hand's counts even."]
      : r.late > r.early && r.late >= 2
        ? ["A little late.", "The taps trail the clap. Count the finger counts aloud so the clap arrives when you expect it."]
        : r.missed > of / 4 ? ["Keep going.", "Some targets went by without a tap. Watch the hand in the trainer first, then try again with the cues on."]
          : ["Steady.", "Even taps all through. When it feels easy, try one step on: the tempo goes up a little."];
    this.draw(r, bestLine, advice);
    this.done?.({ ...r, of });
  }

  /** Called with the counts when a run ends (a checkpoint's tap part). */
  done?: (r: { perfect: number; onTime: number; early: number; late: number; missed: number; of: number }) => void;
}

function variantLabel(v: Partial<TapSpec>, base: TapSpec): string {
  const parts: string[] = [];
  if (v.tala) parts.push((v.tala ?? "").replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase()));
  if (v.eduppu !== undefined) parts.push(`entry ${v.eduppu} after samam`);
  if (v.nadai !== undefined) parts.push(`nadai ${v.nadai}`);
  if (v.plays?.abhyasa && !v.tala) parts.push(v.plays.abhyasa.replace(/_/g, " "));
  return parts.join(" · ") || "version";
}

/** Mount a tap task, with its variants (each gives only the keys that change). */
export async function mountTap(root: HTMLElement, spec: TapSpec, overrides: Partial<TapSpec> = {}): Promise<TapTask | null> {
  if (spec.plays?.recording) {
    root.innerHTML = `<p class="tt-meta">This one taps along with a real recording and its beat map.</p><div class="ex-actions"><a class="ex-btn" href="/carnatic/listen?tap=1">Open the Listening room</a></div>`;
    return null;
  }
  let task: TapTask | null = null;
  const run = async (i: number) => {
    const eff: TapSpec = { ...spec, ...(spec.variants?.[i] ?? {}), ...overrides, id: spec.id };
    task = new TapTask(root, eff, await tapData(eff), (j) => void run(j), i);
  };
  await run(0);
  return task;
}
