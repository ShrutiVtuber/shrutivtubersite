/* The tap task (README_v2 §5, SELF_TEST.md §3): keep tala against the app.
 *
 * Fading audio: all cues → claps only → samam only → nothing. The five
 * counts (perfect ±30 ms, on time ±80 ms, early, late, missed; at dense
 * targets the window shrinks to 40 % of the gap), the personal best at this
 * step, and "Start by tapping". A tap on a count that isn't scored is shown
 * ("that count is a finger count"), never counted against anyone.
 */
import { blip, ctx, talaSound } from "./audio";
import { attempts, recordAttempt } from "./learner";
import { playLine } from "./phrase";
import { settings } from "./state";
import { pitchHz } from "../notation";

export interface TapSpec {
  id: string; title?: string; tala: string; tempo?: number; tempoRange?: number[]; tempo_range?: number[];
  speed?: number | number[]; nadai?: number | number[]; nadai_sequence?: number[]; avartanams?: number;
  targets?: string; count_in?: number; countIn?: number; fade?: string[]; eduppu?: number | number[];
  plays?: string; gap?: number[]; line?: string; raga?: string;
}

interface Count { n: number; action: "clap" | "finger" | "wave" | "silent"; samam?: boolean; anga?: number; angaName?: string }

const PHASES = [
  { id: "all", title: "All cues", sub: "clap, wave, fingers" },
  { id: "claps", title: "Claps only", sub: "no finger counts" },
  { id: "samam", title: "Samam only", sub: "one click a cycle" },
  { id: "none", title: "Nothing", sub: "you keep it" },
];

const esc = (s: string) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;");

export interface TapData { counts: Count[]; talaName: string; melody?: string[] }

export class TapTask {
  private tempo: number;
  private running = false;
  private targets: { at: number; kind: string; hit?: number; anga?: number }[] = [];
  private shown: string[] = [];
  private timer = 0;
  private t0 = 0;
  private started = "";

  constructor(private root: HTMLElement, private spec: TapSpec, private data: TapData) {
    const range = spec.tempoRange ?? spec.tempo_range;
    this.tempo = Number(spec.tempo ?? (range ? range[0] + 10 : 60));
    this.draw();
  }

  private get fade(): string[] {
    const f = this.spec.fade;
    if (!f?.length) return ["all"];
    return f[0] === "all" ? f : ["all", ...f];
  }
  private get avartanams() { return Number(this.spec.avartanams ?? 4); }
  private get countIn() { return Number(this.spec.count_in ?? this.spec.countIn ?? 1); }
  private speeds(): number[] { const s = this.spec.speed; return Array.isArray(s) ? s : [Number(s ?? 1)]; }
  private nadais(): number[] {
    const n = this.spec.nadai_sequence ?? this.spec.nadai;
    return Array.isArray(n) ? n : [Number(n ?? 4)];
  }

  private meta(): string {
    const sp = this.speeds();
    return [this.data.talaName, `${this.tempo} a minute`, `speed ${sp.join(", ")}`, `${this.avartanams} avartanam${this.avartanams === 1 ? "" : "s"}`,
      `count-in ${this.countIn}`, this.nadais().length > 1 ? `nadai ${this.nadais().join(" → ")}` : ""].filter(Boolean).join(" · ");
  }

  private draw(result?: Record<string, number>, bestLine?: string, advice?: [string, string]) {
    const phases = this.fade.length > 1
      ? `<div class="tt-phases" role="list">${PHASES.filter((p) => this.fade.includes(p.id)).map((p) => `<div class="tt-phase" role="listitem" data-phase="${p.id}"><b>${p.title}</b><small>${p.sub}</small></div>`).join("")}</div>` : "";
    const scores = result ? `<div class="tt-scores">${[["perfect", "perfect"], ["onTime", "on time"], ["early", "early"], ["late", "late"], ["missed", "missed"]]
      .map(([k, l]) => `<div><b>${result[k] ?? 0}</b><small>${l}</small></div>`).join("")}</div>` : "";
    this.root.innerHTML = `<p class="tt-meta">${esc(this.meta())}</p>${phases}`
      + (result ? `${scores}<p class="tt-best">${esc(bestLine ?? "")}</p>`
        + (advice ? `<div class="ex-explain"><p class="ex-verdict">${esc(advice[0])}</p><p>${esc(advice[1])}</p></div>` : "")
        : `<button type="button" class="tt-pad" data-pad>Start by tapping here, or press the space bar</button><p class="tt-note" data-note></p>`)
      + `<div class="ex-actions">${result ? `<button type="button" class="ex-btn ex-btn-s" data-again>Again</button><button type="button" class="ex-btn" data-step>Again, one step on</button>`
        : `<button type="button" class="ex-btn" data-go>Count me in</button>`}</div>`;
    this.root.querySelector("[data-go]")?.addEventListener("click", () => this.start());
    this.root.querySelector("[data-again]")?.addEventListener("click", () => this.draw());
    this.root.querySelector("[data-step]")?.addEventListener("click", () => {
      const range = this.spec.tempoRange ?? this.spec.tempo_range ?? [40, 140];
      this.tempo = Math.min(Number(range[1] ?? 140), this.tempo + 6);
      this.draw();
    });
    const pad = this.root.querySelector<HTMLElement>("[data-pad]");
    pad?.addEventListener("pointerdown", (e) => { e.preventDefault(); this.tap(); });
    const key = (e: KeyboardEvent) => {
      if (e.code !== "Space" || (e.target as HTMLElement)?.closest("input, textarea, select")) return;
      if (!this.root.isConnected) { document.removeEventListener("keydown", key); return; }
      if (!this.root.querySelector("[data-pad]")) return;
      e.preventDefault();
      this.tap();
    };
    document.addEventListener("keydown", key);
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
    const gap = this.spec.targets === "samam-after-gap" ? Math.min(3, Math.max(1, Math.round(1 + Math.random() * 2))) : 0;
    const speeds = this.speeds();
    const nadais = this.nadais();
    const s = settings();
    const melody = this.data.melody ?? [];
    let mi = 0;
    for (let av = 0; av < total; av++) {
      const scored = av >= this.countIn;
      const k = av - this.countIn;
      const phase = !scored ? "all" : fade[Math.min(fade.length - 1, Math.floor((k * fade.length) / this.avartanams))];
      const silentGap = gap > 0 && scored && k >= 1 && k < 1 + gap;
      const speed = speeds[Math.min(speeds.length - 1, Math.floor((Math.max(0, k) * speeds.length) / this.avartanams))];
      const nadai = nadais[Math.min(nadais.length - 1, Math.floor((Math.max(0, k) * nadais.length) / this.avartanams))];
      for (let i = 0; i < n; i++) {
        const c = counts[i];
        const at = this.t0 + (av * n + i) * beat;
        if (!silentGap) {
          if (phase === "all") talaSound(c.action, at, { samam: c.samam });
          else if (phase === "claps" && c.action === "clap") talaSound("clap", at, { samam: c.samam });
          else if (phase === "samam" && i === 0) talaSound("clap", at, { samam: true });
          if (nadais.length > 1 && scored) for (let m = 0; m < nadai; m++) blip(m === 0 ? 1320 : 990, at + (m * beat) / nadai, 0.03, 0.03);
        }
        if (!scored) continue;
        const t = this.spec.targets ?? "claps";
        if (t === "claps" && c.action === "clap") this.targets.push({ at, kind: "clap", anga: c.anga });
        else if (t === "every-count") this.targets.push({ at, kind: "count", anga: c.anga });
        else if (t === "samam" && i === 0) this.targets.push({ at, kind: "samam", anga: 0 });
        else if (t === "samam-after-gap" && i === 0 && k === 1 + gap) this.targets.push({ at, kind: "samam", anga: 0 });
        else if (t === "claps-and-landing" && c.action === "clap") this.targets.push({ at, kind: "clap", anga: c.anga });
      }
      if (melody.length && scored) {
        const per = n * ({ 1: 1, 2: 2, 3: 4 } as Record<number, number>)[speed];
        const line = Array.from({ length: per }, () => melody[mi++ % melody.length]).join(" ");
        playLine(line, { saHz: pitchHz(s.sa || "C3"), tuning: s.playbackTuning, unit: beat / (per / n), at: this.t0 + av * n * beat });
      }
    }
    if (this.spec.targets === "entry") {
      const ed = Array.isArray(this.spec.eduppu) ? this.spec.eduppu[Math.floor(Math.random() * this.spec.eduppu.length)] : Number(this.spec.eduppu ?? 1.5);
      this.targets.push({ at: this.t0 + (this.countIn * n + ed) * beat, kind: "entry", anga: 0 });
    }
    const end = this.t0 + total * n * beat + 0.4;
    const phaseEls = [...this.root.querySelectorAll<HTMLElement>("[data-phase]")];
    const pad = this.root.querySelector<HTMLElement>("[data-pad]");
    if (pad) pad.textContent = "Tap";
    const note = this.root.querySelector<HTMLElement>("[data-note]");
    const tick = () => {
      const now = ctx().currentTime;
      const av = Math.floor((now - this.t0) / (n * beat));
      const k = av - this.countIn;
      if (note) note.textContent = av < this.countIn ? "Counting in…" : "";
      const p = k < 0 ? -1 : Math.min(fade.length - 1, Math.floor((k * fade.length) / this.avartanams));
      phaseEls.forEach((el, i) => el.classList.toggle("is-on", i === p));
      if (now >= end) { window.clearInterval(this.timer); this.finish(); }
    };
    this.timer = window.setInterval(tick, 60);
  }

  private tap() {
    if (!this.running) { this.start(); return; }
    const now = ctx().currentTime;
    const beat = 60 / this.tempo;
    const dense = this.targets.length > 1 ? Math.min(...this.targets.slice(1).map((t, i) => t.at - this.targets[i].at).filter((x) => x > 0)) : beat;
    const win = Math.min(0.08, 0.4 * dense);
    let best: typeof this.targets[number] | null = null;
    for (const t of this.targets) if (t.hit === undefined && (!best || Math.abs(now - t.at) < Math.abs(now - best.at))) best = t;
    const note = this.root.querySelector<HTMLElement>("[data-note]");
    if (!best || Math.abs(now - best.at) > Math.max(0.25, dense / 2)) {
      const n = this.data.counts.length;
      const idx = Math.floor((((now - this.t0) / beat) % n + n) % n);
      const c = this.data.counts[Math.round(((now - this.t0) / beat)) % n] ?? this.data.counts[idx];
      if (note && c) note.textContent = c.action === "clap" ? "" : `That count is ${c.action === "finger" ? "a finger count" : c.action === "wave" ? "a wave" : "silent"}: shown, not scored.`;
      return;
    }
    best.hit = (now - best.at) * 1000;
    if (Math.abs(best.hit) > win * 1000 && Math.abs(best.hit) <= 80) best.hit = Math.sign(best.hit) * 81;
  }

  private finish() {
    this.running = false;
    const r = { perfect: 0, onTime: 0, early: 0, late: 0, missed: 0 };
    const earlyByAnga: Record<string, number> = {};
    for (const t of this.targets) {
      if (t.hit === undefined) { r.missed++; continue; }
      const a = Math.abs(t.hit);
      if (a <= 30) r.perfect++;
      else if (a <= 80) r.onTime++;
      else if (t.hit < 0) { r.early++; earlyByAnga[String(t.anga ?? 0)] = (earlyByAnga[String(t.anga ?? 0)] ?? 0) + 1; }
      else r.late++;
    }
    const of = this.targets.length;
    const good = r.perfect + r.onTime;
    const prev = attempts({ itemId: this.spec.id, kind: "tap" }).filter((a) => a.result.tempo === this.tempo)
      .map((a) => (a.result.perfect ?? 0) + (a.result.onTime ?? 0));
    recordAttempt({ itemId: this.spec.id, kind: "tap", startedAt: this.started, seconds: Math.round((60 / this.tempo) * this.data.counts.length * (this.countIn + this.avartanams)),
                    result: { tempo: this.tempo, ...r, of } });
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
        : r.missed > of / 4 ? ["Keep going.", "Some claps went by without a tap. Watch the hand in the trainer first, then try again with the cues on."]
          : ["Steady.", "Even taps all through. When it feels easy, try one step on: the tempo goes up a little."];
    this.draw(r, bestLine, advice);
  }
}

export async function tapData(spec: TapSpec): Promise<TapData> {
  const talas = await fetch("/api/carnatic/data/talas.json").then((r) => (r.ok ? r.json() : null)).catch(() => null);
  const practical = (talas?.practical ?? []).find((t: any) => t.id === spec.tala || t.id === ({ rupaka: "rupaka_3count" } as Record<string, string>)[spec.tala]);
  const suladi = (talas?.suladi ?? []).find((t: any) => t.id === spec.tala);
  const counts: Count[] = (practical ?? suladi)?.counts ?? Array.from({ length: 8 }, (_, i) => ({ n: i + 1, action: i === 0 || i === 4 || i === 6 ? "clap" : i === 5 || i === 7 ? "wave" : "finger", samam: i === 0 }));
  let melody: string[] | undefined;
  if (spec.plays) {
    const lessons = await fetch("/api/carnatic/data/lessons.json").then((r) => (r.ok ? r.json() : null)).catch(() => null);
    for (const set of lessons?.sets ?? []) for (const item of set.items ?? []) {
      if (item.id === spec.plays || item.id === spec.plays.replace(/_1$/, "_01")) melody = item.sections.flatMap((s: any) => s.lines.flatMap((l: any) => l.segments.flat()));
    }
  }
  return { counts, talaName: practical?.name ?? suladi?.name ?? spec.tala.replace(/_/g, " "), melody };
}
