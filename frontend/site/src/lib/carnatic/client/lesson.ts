/* The lesson reader in the browser (README_v2 §4): footnotes and glossary
 * terms that open like footnotes (a sticky margin panel on wide screens, an
 * inline card on narrow ones), the embeds (drone, sargam, recording, tala,
 * konnakol, tuner, quiz and tap tasks expanding in place), reading progress
 * and "your place is remembered on this device", and "Mark as complete",
 * which is the learner's own decision: nothing is marked for them.
 */
import { confidenceLine } from "../lesson";
import { genData, mountQuiz, prepare, type EngineOpts } from "./exercise";
import { loadPlayer } from "./embed";
import { ensureCard, lessonState, syncLessons, updateLesson } from "./learner";
import { playLine } from "./phrase";
import { Mic, readSwara } from "./pitch";
import { blip, ctx, talaSound } from "./audio";
import { boot, settings, startDrone, stopDrone, theDrone, onDrone } from "./state";
import { mountTap } from "./taptask";
import { inline, pitchHz } from "../notation";

interface PageData {
  id: string; slug: string; title: string; minutes: number; words: number; unitHref: string;
  sources: { key: string; n: number; cite: string; url?: string | null; research?: string | null; confidence?: string }[];
  glossary: { slug: string; term: string; definition: string; iso?: string; lesson?: string; lessonTitle?: string; lessonHref?: string }[];
  exercises: Record<string, any>;
  recordings: Record<string, { provider: string; url: string; label: string }>;
  lessonTitles: Record<string, { title: string; href: string }>;
  script: "lat" | "ta" | "te" | "kn"; tamil: "grantha" | "pure";
}

const esc = (s: string) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export function hydrateLesson(root: HTMLElement, data: PageData) {
  const wide = () => window.matchMedia("(min-width: 900px)").matches;
  const panel = document.querySelector<HTMLElement>("[data-fn-panel]");

  // ── footnotes and glossary terms ──────────────────────────────────────
  let openBtn: HTMLElement | null = null;
  let inlineCard: HTMLElement | null = null;
  const close = () => {
    openBtn?.classList.remove("is-open");
    openBtn = null;
    if (panel) panel.hidden = true;
    inlineCard?.remove();
    inlineCard = null;
  };
  const open = (btn: HTMLElement, html: string) => {
    const same = openBtn === btn;
    close();
    if (same) return;
    openBtn = btn;
    btn.classList.add("is-open");
    const body = `<div class="lr-fnp-head"><span>${html.split("\u0000")[0]}</span><button type="button" data-fn-close aria-label="Close">×</button></div>${html.split("\u0000")[1]}`;
    if (wide() && panel) {
      panel.innerHTML = body;
      panel.hidden = false;
      const top = btn.getBoundingClientRect().top + window.scrollY - (root.getBoundingClientRect().top + window.scrollY);
      panel.style.setProperty("--fn-top", `${Math.max(0, top - 24)}px`);
    } else {
      inlineCard = document.createElement("div");
      inlineCard.className = "lr-fnp lr-fnp-inline";
      inlineCard.innerHTML = body;
      (btn.closest("p, li, td, .lr-box") ?? btn).insertAdjacentElement("afterend", inlineCard);
    }
    document.querySelectorAll<HTMLElement>("[data-fn-close]").forEach((b) => b.addEventListener("click", close));
  };
  root.querySelectorAll<HTMLElement>("[data-fn]").forEach((b) => b.addEventListener("click", () => {
    const s = data.sources.find((x) => x.key === b.dataset.fn);
    if (!s) return;
    const conf = confidenceLine(s.confidence);
    const link = s.url ? `<a href="${esc(s.url)}" rel="noopener nofollow">${esc(s.url.replace(/^https?:\/\//, ""))}</a>`
      : s.research ? `<code>${esc(s.research)}</code>` : "";
    open(b, `Footnote ${s.n}\u0000<p>${esc(s.cite)}</p>${conf ? `<p class="lr-conf">${esc(conf)}</p>` : ""}${link ? `<p class="lr-fn-link">${link}</p>` : ""}`);
  }));
  root.querySelectorAll<HTMLElement>("[data-term]").forEach((b) => b.addEventListener("click", () => {
    const g = data.glossary.find((x) => x.slug === b.dataset.term);
    if (!g) return;
    open(b, `Glossary\u0000<p><b>${esc(g.term)}</b>${g.iso && g.iso !== g.term ? ` <span class="lr-iso">${esc(g.iso)}</span>` : ""}: ${esc(g.definition)}</p>${g.lessonHref ? `<p class="lr-fn-link">Taught in <a href="${esc(g.lessonHref)}">${esc(g.lessonTitle ?? g.lesson ?? "")}</a></p>` : ""}`);
  }));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });

  // ── embeds ────────────────────────────────────────────────────────────
  const s = settings();
  const saHz = () => pitchHz(settings().sa || "C3");

  root.querySelectorAll<HTMLElement>('[data-embed="drone"]').forEach((card) => {
    const btn = card.querySelector<HTMLElement>("[data-drone]")!;
    const name = card.querySelector<HTMLElement>("[data-drone-name]")!;
    const NAMES: Record<string, string> = { pa: "Pa–Sa–Sa–Sa", ma: "Ma–Sa–Sa–Sa", mute: "Sa–Sa–Sa, Pa muted", ni: "Ni–Sa–Sa–Sa" };
    let tuning = card.dataset.tuning || "pa";
    const paint = () => {
      const on = theDrone().playing && card.dataset.mine === "1";
      btn.setAttribute("aria-pressed", String(on));
      card.classList.toggle("is-on", on);
      card.querySelectorAll<HTMLElement>("[data-tuning]").forEach((x) => x.setAttribute("aria-pressed", String(x.dataset.tuning === tuning)));
      name.textContent = NAMES[tuning] ?? NAMES.pa;
    };
    btn.addEventListener("click", () => {
      const playing = theDrone().playing && card.dataset.mine === "1";
      root.querySelectorAll<HTMLElement>('[data-embed="drone"]').forEach((c) => { c.dataset.mine = ""; });
      if (playing) stopDrone();
      else { card.dataset.mine = "1"; startDrone(tuning as any); }
      root.querySelectorAll<HTMLElement>('[data-embed="drone"]').forEach((c) => c.dispatchEvent(new Event("paint")));
    });
    card.querySelectorAll<HTMLElement>("[data-tuning]").forEach((x) => x.addEventListener("click", () => {
      tuning = x.dataset.tuning!;
      if (theDrone().playing && card.dataset.mine === "1") startDrone(tuning as any);
      paint();
    }));
    card.addEventListener("paint", paint);
    onDrone(() => paint());
    paint();
  });

  genData().then((d) => {
    root.querySelectorAll<HTMLElement>('[data-embed="sargam"]').forEach((card) => {
      card.querySelector("[data-play]")?.addEventListener("click", () => {
        const speed = Number(card.dataset.speed || 1);
        const unit = 60 / Number(settings().tempo ?? 60) / ({ 1: 1, 2: 2, 3: 4 } as Record<number, number>)[speed];
        const notes = [...card.querySelectorAll<HTMLElement>(".sn:not(.sn-bar)")];
        playLine(card.dataset.line!, { saHz: saHz(), tuning: settings().playbackTuning, scale: d.scales[card.dataset.raga ?? ""],
          unit: Math.max(0.2, unit), onNote: (i, at) => {
            const el = notes[i];
            if (!el) return;
            setTimeout(() => { el.classList.add("is-now"); setTimeout(() => el.classList.remove("is-now"), unit * 900); }, Math.max(0, (at - ctx().currentTime) * 1000));
          } });
      });
    });
  });

  root.querySelectorAll<HTMLElement>('[data-embed="recording"]').forEach((card) => {
    card.querySelector("[data-load]")?.addEventListener("click", () => {
      const toS = (t?: string) => t ? t.split(":").reduce((a, x) => a * 60 + Number(x), 0) : undefined;
      loadPlayer(card.querySelector<HTMLElement>("[data-rec-box]")!, card.dataset.provider!, card.dataset.url!,
        { start: toS(card.dataset.start), end: toS(card.dataset.end) });
    });
  });

  // tala grids from talas.json
  const talasP = fetch("/api/carnatic/data/talas.json").then((r) => (r.ok ? r.json() : null)).catch(() => null);
  root.querySelectorAll<HTMLElement>('[data-embed="tala"]').forEach(async (card) => {
    const t = await talasP;
    const tala = [...(t?.practical ?? []), ...(t?.suladi ?? [])].find((x: any) => x.id === card.dataset.tala);
    const grid = card.querySelector<HTMLElement>("[data-tala-grid]")!;
    if (!tala) { grid.innerHTML = `<p class="lr-meta">This tala isn't in the data yet.</p>`; return; }
    const ACT: Record<string, string> = { clap: "clap", finger: "finger", wave: "wave", silent: "silent" };
    grid.innerHTML = tala.counts.map((c: any, i: number) => `<span class="lr-tc${c.samam ? " is-samam" : ""}${i && tala.counts[i - 1].anga !== c.anga ? " is-anga" : ""}"><b>${c.n}</b><small>${ACT[c.action] ?? c.action}</small></span>`).join("");
    const play = document.createElement("button");
    play.type = "button"; play.className = "lr-play"; play.setAttribute("aria-label", "Play one avartanam");
    play.innerHTML = `<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M5 3l8 5-8 5z" fill="currentColor"/></svg>`;
    card.querySelector(".lr-tala-foot")?.prepend(play);
    play.addEventListener("click", () => {
      const beat = 60 / Number(card.dataset.tempo || settings().tempo || 60);
      const t0 = ctx().currentTime + 0.2;
      const cells = [...grid.querySelectorAll<HTMLElement>(".lr-tc")];
      tala.counts.forEach((c: any, i: number) => {
        talaSound(c.action, t0 + i * beat, { samam: c.samam });
        setTimeout(() => { cells.forEach((x) => x.classList.remove("is-now")); cells[i]?.classList.add("is-now"); }, (i * beat + 0.2) * 1000);
      });
      setTimeout(() => cells.forEach((x) => x.classList.remove("is-now")), (tala.counts.length * beat + 0.3) * 1000);
    });
  });

  root.querySelectorAll<HTMLElement>('[data-embed="konnakol"]').forEach((card) => {
    card.querySelector("[data-konnakol]")?.addEventListener("click", () => {
      const syl = (card.dataset.pattern ?? "").split(/\s+/).filter(Boolean);
      const nadai = Number(card.dataset.nadai || 4);
      const beat = 60 / Number(settings().tempo || 60);
      const t0 = ctx().currentTime + 0.2;
      syl.forEach((x, i) => { if (x !== ",") blip(i % nadai === 0 ? 1320 : 990, t0 + (i * beat) / nadai, 0.05, 0.06); });
      for (let c = 0; c <= Math.ceil(syl.length / nadai); c++) talaSound(c === 0 ? "clap" : "finger", t0 + c * beat, { samam: c === 0 });
    });
  });

  root.querySelectorAll<HTMLElement>('[data-embed="tuner"]').forEach((card) => {
    const btn = card.querySelector<HTMLButtonElement>("[data-tuner]")!;
    const needle = card.querySelector<HTMLElement>("[data-tuner-needle]")!;
    const note = card.querySelector<HTMLElement>("[data-tuner-note]")!;
    let mic: Mic | null = null;
    let raf = 0;
    btn.addEventListener("click", async () => {
      if (mic) { mic.stop(); mic = null; cancelAnimationFrame(raf); btn.textContent = "Start tuner"; note.textContent = "Needs the microphone. Wear headphones if the drone is on."; return; }
      mic = new Mic();
      const st = await mic.start();
      if (st !== "working") { note.textContent = "The microphone isn't available: allow it in the browser to use the tuner."; mic = null; return; }
      btn.textContent = "Stop";
      const loop = () => {
        const hz = mic?.read();
        if (hz) {
          const r = readSwara(hz, saHz());
          needle.style.left = `${50 + Math.max(-50, Math.min(50, r.cents))}%`;
          note.textContent = `${inline(r.name, data.script, data.tamil)} · ${r.octaveWord} · ${r.cents > 0 ? "+" : ""}${r.cents} cents vs equal temperament`;
        }
        raf = requestAnimationFrame(loop);
      };
      loop();
    });
  });

  // exercises in place
  const engine = (ex: any): EngineOpts => ({
    script: data.script, tamil: data.tamil, cards: true, recordings: data.recordings,
    record: { itemId: ex.id, kind: ex.checkpoint ? "checkpoint" : "quiz" },
    from: () => ({ text: data.title, href: `#top` }),
  });
  root.querySelectorAll<HTMLElement>('[data-embed="quiz"], [data-embed="tap"]').forEach((card) => {
    const btn = card.querySelector<HTMLButtonElement>("[data-expand]");
    const body = card.querySelector<HTMLElement>("[data-ex-body]");
    const ex = data.exercises[card.dataset.ex!];
    if (!btn || !body || !ex) return;
    let mounted = false;
    btn.addEventListener("click", async () => {
      const opening = body.hidden;
      body.hidden = !opening;
      card.classList.toggle("is-open", opening);
      btn.textContent = opening ? "Close" : "Start";
      if (!opening || mounted) return;
      mounted = true;
      if (ex.kind === "tap" || card.dataset.embed === "tap") await mountTap(body, ex);
      else mountQuiz(body, ex, engine(ex));
    });
  });

  // ── progress, place, completion ───────────────────────────────────────
  const bar = document.querySelector<HTMLElement>("[data-progress]");
  const left = document.querySelector<HTMLElement>("[data-left]");
  const headings = [...root.querySelectorAll<HTMLElement>("[data-heading]")];
  const toc = [...document.querySelectorAll<HTMLElement>("[data-toc] a")];
  const state = lessonState(data.id);
  if (!state.openedAt) updateLesson(data.id, { openedAt: new Date().toISOString() });
  let saveT = 0;
  const onScroll = () => {
    const r = root.getBoundingClientRect();
    const total = r.height - window.innerHeight * 0.6;
    const frac = Math.max(0, Math.min(1, -r.top / Math.max(1, total)));
    if (bar) {
      bar.style.width = `${frac * 100}%`;
      const hdr = document.querySelector<HTMLElement>(".site-header");
      bar.style.top = `${Math.max(0, hdr ? hdr.getBoundingClientRect().bottom : 0)}px`;
    }
    if (left) left.textContent = `${Math.max(1, Math.round(data.minutes * (1 - frac)))} min left · ${data.words.toLocaleString("en")} words`;
    let current = headings[0];
    for (const h of headings) if (h.getBoundingClientRect().top < window.innerHeight * 0.3) current = h;
    toc.forEach((a) => a.setAttribute("aria-current", String(a.getAttribute("href") === `#${current?.id}`)));
    window.clearTimeout(saveT);
    saveT = window.setTimeout(() => { if (frac > 0.02) updateLesson(data.id, { position: { heading: current?.id, fraction: Math.round(frac * 100) / 100 } }); }, 1500);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  const resume = document.querySelector<HTMLElement>("[data-resume]");
  const showResume = (st: typeof state) => {
    const h = st.position?.heading ? headings.find((x) => x.id === st.position!.heading) : null;
    if (resume && h && (st.position?.fraction ?? 0) > 0.05 && !st.completedAt) {
      resume.innerHTML = `You were reading “${esc(h.textContent ?? "")}”. <a href="#${esc(h.id)}">Continue from there</a>`;
      resume.hidden = false;
    }
  };
  showResume(state);
  if (boot().signedIn) void syncLessons().then((all) => { if (all[data.id]) { showResume(all[data.id]); paintComplete(); } });

  const complete = document.querySelector<HTMLButtonElement>("[data-complete]");
  const paintComplete = () => {
    if (!complete) return;
    const done = !!lessonState(data.id).completedAt;
    complete.setAttribute("aria-pressed", String(done));
    complete.textContent = done ? "Completed ✓" : "Mark as complete";
  };
  complete?.addEventListener("click", () => {
    const done = !!lessonState(data.id).completedAt;
    updateLesson(data.id, { completedAt: done ? null : new Date().toISOString() });
    // SELF_TEST.md §6: a lesson's quiz items become review cards when the learner completes it (10 new a day at most).
    if (!done) for (const ex of Object.values(data.exercises)) if ((ex as any).kind === "quiz") for (const p of prepare(ex as any)) ensureCard(p.key);
    paintComplete();
  });
  paintComplete();
}
