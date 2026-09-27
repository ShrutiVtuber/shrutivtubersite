/* Test yourself (SELF_TEST.md §2, §4, §6; artboards P1-P3): assembling a
 * set, running it with the exercise engine, and the result screens.
 *
 * - lesson   the lesson's own quiz items
 * - unit     all the unit's quiz items, 12-20 of them
 * - mixed    10, 20 or 40: due cards first, then items from lessons the
 *            learner completed (opened, when nothing is completed yet),
 *            leaning towards older lessons
 * - topic    one strand across units
 * - review   the due quiz cards
 * - checkpoint  the unit's quiz items balanced across its lessons; the
 *            result is a profile in three words per lesson (the skill),
 *            with the best so far and a small chart of every attempt
 *
 * Nothing here says pass, fail, score or percent, and nothing is red.
 */
import { attempts, allLessons, cards, dueCards, wordFor } from "./learner";
import { prepare, QuizRunner, type EngineOpts, type Exercise, type PreparedItem, type Summary } from "./exercise";

const esc = (s: string) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

interface UnitRow { n: number; title: string; lessons: { id: string; slug: string; title: string; available: boolean; order: number }[] }
export interface TestPage {
  units: UnitRow[];
  drills?: any;
  topics: Record<string, number[]>;
  script: EngineOpts["script"];
  tamil: EngineOpts["tamil"];
  href: (p: string) => string;
}

const exCache = new Map<number, Promise<Exercise[]>>();
function unitExercises(n: number): Promise<Exercise[]> {
  if (!exCache.has(n)) {
    exCache.set(n, fetch(`/api/carnatic/course/exercises?unit=${n}`).then((r) => (r.ok ? r.json() : { items: [] }))
      .then((b) => (b.items as Exercise[]).filter((e) => e.kind === "quiz" || e.kind === "checkpoint")).catch(() => []));
  }
  return exCache.get(n)!;
}

function shuffle<T>(a: T[]): T[] {
  const x = [...a];
  for (let i = x.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [x[i], x[j]] = [x[j], x[i]];
  }
  return x;
}

const unitOf = (id: string) => Number(id.slice(1, 3));

export interface BuiltSet {
  kind: "lesson" | "unit" | "mixed" | "topic" | "review" | "checkpoint";
  eyebrow: string; title: string; items: PreparedItem[]; itemId: string; recordKind: "quiz" | "checkpoint" | "review";
  unit?: UnitRow; empty?: string; again?: string;
  /** Checkpoints: the lesson that teaches each skill, for "Suggested next". */
  skillLesson?: Record<string, string>;
}

/** The item for a generator card ("gen:name:category") asked afresh. */
function fromCard(key: string, pool: Map<string, PreparedItem>): PreparedItem | null {
  if (pool.has(key)) return pool.get(key)!;
  const m = /^gen:([a-z_]+)/.exec(key);
  if (!m) return null;
  return { key, label: "Generated", exId: key, item: { type: "generated", generator: m[1], settings: {} } };
}

export async function buildSet(q: URLSearchParams, page: TestPage): Promise<BuiltSet> {
  const lessons = allLessons();
  const titleOf = new Map(page.units.flatMap((u) => u.lessons.map((l) => [l.id, l.title] as const)));
  const lessonsIn = (units: number[]) => page.units.filter((u) => units.includes(u.n)).flatMap((u) => u.lessons);
  const itemsOf = async (units: number[]) => (await Promise.all(units.map(unitExercises))).flat();
  const quizOf = async (units: number[]) => (await itemsOf(units)).filter((e) => e.kind === "quiz");
  const touched = (ids: string[]) => {
    const done = ids.filter((id) => lessons[id]?.completedAt);
    return done.length ? done : ids.filter((id) => lessons[id]?.openedAt);
  };

  if (q.get("lesson")) {
    const id = q.get("lesson")!;
    const exs = (await quizOf([unitOf(id)])).filter((e) => e.lesson === id);
    return { kind: "lesson", eyebrow: `Lesson quiz · ${id}`, title: titleOf.get(id) ?? id, items: exs.flatMap(prepare),
             itemId: exs[0]?.id ?? id, recordKind: "quiz", empty: "This lesson has no quiz yet." };
  }
  if (q.get("unit")) {
    const n = Number(q.get("unit"));
    const u = page.units.find((x) => x.n === n);
    const all = shuffle((await quizOf([n])).flatMap(prepare)).slice(0, 20);
    return { kind: "unit", eyebrow: `Unit quiz · unit ${n}`, title: u ? `Unit ${n} quiz: ${u.title}` : `Unit ${n} quiz`, items: all,
             itemId: `U${String(n).padStart(2, "0")}`, recordKind: "quiz", unit: u };
  }
  if (q.get("checkpoint")) {
    const n = Number(q.get("checkpoint"));
    const u = page.units.find((x) => x.n === n);
    const cpId = `CP.U${String(n).padStart(2, "0")}`;
    const unitExs = await itemsOf([n]);
    const cp = unitExs.find((e) => e.id === cpId && e.kind === "checkpoint");
    const tries = attempts({ itemId: cpId, kind: "checkpoint" }).length;
    const nth = ["first", "second", "third", "fourth", "fifth"][tries] ?? `attempt ${tries + 1}`;
    const head = { kind: "checkpoint" as const, eyebrow: `Unit ${n} checkpoint · ${u?.title ?? ""} · ${nth} attempt`,
      title: `Where you are with ${u ? u.title.charAt(0).toLowerCase() + u.title.slice(1) : `unit ${n}`}`, itemId: cpId,
      recordKind: "checkpoint" as const, unit: u };
    if (cp) {
      // FORMAT.md §5: parts drawn at run time, in order, each under a skill; written items by {items: n}.
      const skillName = new Map<string, string>((cp.skills ?? []).map((k: any) => [k.id, k.name]));
      const name = (id: string) => skillName.get(id) ?? id;
      const written = prepare({ ...cp, items: cp.items ?? [] });
      let wi = 0;
      const items: PreparedItem[] = [];
      const skillLesson: Record<string, string> = {};
      const byId = new Map(unitExs.map((e) => [e.id, e] as const));
      const K = new Map<string, any>((page.drills?.talaKeeping ?? []).map((k: any) => [k.id, k] as const));
      const levels = new Map<string, any>((page.drills?.levels ?? []).map((l: any) => [l.id, l] as const));
      for (const part of cp.parts ?? []) {
        const skill = name(part.skill);
        if (part.quiz) {
          const ex = byId.get(part.quiz) ?? (await quizOf([unitOf(part.quiz)])).find((e) => e.id === part.quiz);
          if (!ex) continue;
          const pool = shuffle(prepare(ex));
          items.push(...pool.slice(0, part.count ?? pool.length).map((p) => ({ ...p, skill })));
          if (ex.lesson && !skillLesson[skill]) skillLesson[skill] = ex.lesson;
        } else if (part.tap) {
          const spec = K.get(part.tap) ?? byId.get(part.tap);
          if (!spec) continue;
          items.push({ key: `${cpId}#${part.tap}`, label: "Tala keeping", exId: part.tap, skill,
            item: { type: "_tap", text: `${spec.title}. Tap along; this part counts in the share of taps perfect or on time.`, spec,
                    overrides: part.avartanams ? { avartanams: part.avartanams, segments: undefined } : {} } });
        } else if (part.drill) {
          const level = levels.get(part.drill);
          if (!level || !page.drills) continue;
          items.push({ key: `${cpId}#${part.drill}`, label: "Ear training", exId: part.drill, skill,
            item: { type: "_drill", text: `${level.title}: ${part.count ?? 4} items.`, level, drills: page.drills, count: part.count ?? 4, set: part.set ?? null } });
        } else if (part.items) {
          for (let k = 0; k < Number(part.items) && wi < written.length; k++, wi++) items.push({ ...written[wi], skill });
        }
      }
      const first = cp.skills?.[0]?.id ? name(cp.skills[0].id) : u?.title ?? "";
      for (; wi < written.length; wi++) items.push({ ...written[wi], skill: first });
      return { ...head, items, skillLesson };
    }
    const byLesson = new Map<string, PreparedItem[]>();
    for (const p of unitExs.filter((e) => e.kind === "quiz").flatMap(prepare)) {
      const k = p.lesson ?? "";
      byLesson.set(k, [...(byLesson.get(k) ?? []), { ...p, skill: titleOf.get(k) ?? k }]);
    }
    // Balanced: up to 3 from each lesson, 14 at most (10-15 minutes).
    const per = Math.max(2, Math.min(3, Math.ceil(14 / Math.max(1, byLesson.size))));
    const items = shuffle([...byLesson.values()].flatMap((xs) => shuffle(xs).slice(0, per))).slice(0, 14);
    return { ...head, items };
  }
  if (q.get("topic")) {
    const t = q.get("topic")!;
    const units = page.topics[t] ?? [];
    const ids = lessonsIn(units).map((l) => l.id);
    const mine = new Set(touched(ids));
    const pool = (await quizOf(units)).filter((e) => !mine.size || mine.has(e.lesson ?? "")).flatMap(prepare);
    return { kind: "topic", eyebrow: `Topic review · ${t}`, title: `${t.charAt(0).toUpperCase() + t.slice(1)}, across the units`,
             items: shuffle(pool).slice(0, 15), itemId: `topic:${t}`, recordKind: "review", again: "Another round" };
  }
  if (q.get("review")) {
    const due = dueCards().filter((c) => c.key.includes("#") || c.key.startsWith("gen:"));
    const units = [...new Set(due.map((c) => c.key.includes("#") ? unitOf(c.key) : 0).filter(Boolean))];
    const pool = new Map((await quizOf(units)).flatMap(prepare).map((p) => [p.key, p] as const));
    const items = due.map((c) => fromCard(c.key, pool)).filter((x): x is PreparedItem => !!x).slice(0, 30);
    return { kind: "review", eyebrow: `Review · ${items.length} cards`, title: "Ready to review", items, itemId: "review",
             recordKind: "review", empty: "Nothing is due. Cards come back on their own schedule." };
  }
  // mixed
  const size = [10, 20, 40].includes(Number(q.get("mixed"))) ? Number(q.get("mixed")) : 20;
  const all = page.units.flatMap((u) => u.lessons.map((l) => l.id));
  const mine = touched(all);
  const units = [...new Set(mine.map(unitOf))];
  const pool = (await quizOf(units)).filter((e) => mine.includes(e.lesson ?? "")).flatMap(prepare);
  const poolMap = new Map(pool.map((p) => [p.key, p] as const));
  const due = dueCards().map((c) => fromCard(c.key, poolMap)).filter((x): x is PreparedItem => !!x);
  // Older lessons weigh more: a lesson's weight is its place from the newest.
  const order = mine.slice().sort((a, b) => String(lessons[a]?.completedAt ?? lessons[a]?.openedAt).localeCompare(String(lessons[b]?.completedAt ?? lessons[b]?.openedAt)));
  const weight = (p: PreparedItem) => 1 + (order.length - order.indexOf(p.lesson ?? "")) / Math.max(1, order.length);
  const rest = pool.filter((p) => !due.some((d) => d.key === p.key)).map((p) => ({ p, r: Math.random() * weight(p) }))
    .sort((a, b) => b.r - a.r).map((x) => x.p);
  return { kind: "mixed", eyebrow: `Mixed review · ${size} items`, title: "A little of everything you've opened",
           items: [...due, ...rest].slice(0, size), itemId: `mixed:${size}`, recordKind: "review",
           empty: "Open a lesson first: mixed review draws on the lessons you've read.", again: `Another ${size}` };
}

// ── result screens ─────────────────────────────────────────────────────────

const DAY = 86400000;
function when(key: string): string {
  const c = cards().find((x) => x.key === key);
  if (!c?.nextDue) return "coming back later";
  const d = Math.round((new Date(c.nextDue).getTime() - Date.now()) / DAY);
  return d <= 0 ? "coming back today" : d === 1 ? "coming back tomorrow" : `coming back in ${d} days`;
}

export function resultList(root: HTMLElement, set: BuiltSet, s: Summary, page: TestPage, again: () => void) {
  const wrong = s.items.filter((x) => !x.right).length;
  const skills = new Map<string, { right: number; of: number }>();
  for (const it of s.items) {
    const k = it.key.includes("#") ? `Unit ${unitOf(it.key)}` : "generated items";
    const v = skills.get(k) ?? { right: 0, of: 0 };
    v.of += 1; if (it.right) v.right += 1;
    skills.set(k, v);
  }
  const smooth = [...skills].filter(([, v]) => v.right === v.of).map(([k]) => k);
  const lede = !s.of ? "" : wrong === 0 ? "Everything came up right the first time." :
    `${smooth.length ? `${smooth.join(" and ")} went smoothly. ` : ""}${wrong === 1 ? "One item is" : `${wrong} items are`} coming back in review.`;
  root.innerHTML = `<p class="lr-eyebrow-top">${esc(set.eyebrow)} · done</p><h1 class="lr-title">What came up</h1>`
    + (lede ? `<p class="st-lede">${esc(lede)}</p>` : "")
    + `<ol class="st-list">${s.items.map((it, i) => `<li><span class="st-n">${i + 1}</span><span class="st-q">${esc(it.text || it.key)}</span>`
      + `<span class="st-r${it.right ? " yes" : ""}">${it.right ? "yes" : esc(when(it.card ?? it.key))}</span></li>`).join("")}</ol>`
    + `<p class="st-note">Results are for you only. Nobody else sees them.</p>`
    + `<div class="st-actions"><button type="button" class="lr-btn" data-again>${esc(set.again ?? "Try again")}</button>`
    + `<a class="lr-link" href="${esc(page.href("/carnatic/practice"))}">Back to Test yourself</a></div>`;
  root.querySelector("[data-again]")?.addEventListener("click", again);
}

const WORD_Y: Record<string, number> = { comfortable: 0, "getting there": 1, new: 2 };

function chart(words: string[]): string {
  const w = 140, h = 36, step = words.length > 1 ? (w - 16) / (words.length - 1) : 0;
  const pts = words.map((x, i) => [8 + i * step, 6 + WORD_Y[x] * 12] as const);
  return `<svg class="st-chart" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true">`
    + [0, 1, 2].map((r) => `<line x1="0" x2="${w}" y1="${6 + r * 12}" y2="${6 + r * 12}" />`).join("")
    + (pts.length > 1 ? `<polyline points="${pts.map((p) => p.join(",")).join(" ")}" />` : "")
    + pts.map((p) => `<circle cx="${p[0]}" cy="${p[1]}" r="2.5" />`).join("") + `</svg>`;
}

export function checkpointProfile(root: HTMLElement, set: BuiltSet, s: Summary, page: TestPage, again: () => void) {
  const now = new Map<string, { right: number; of: number }>();
  for (const it of s.items) {
    const k = it.skill ?? "other";
    const v = now.get(k) ?? { right: 0, of: 0 };
    v.of += 1; v.right += it.share !== undefined ? it.share : it.right ? 1 : 0;
    now.set(k, v);
  }
  // Earlier attempts (the one just recorded is the last).
  const history = attempts({ itemId: set.itemId, kind: "checkpoint" });
  const rank = (w: string) => 2 - WORD_Y[w];
  const order = (k: string) => set.unit?.lessons.find((l) => l.title === k)?.order ?? 99;
  const rows = [...now].sort((a, b) => order(a[0]) - order(b[0])).map(([skill, v]) => {
    const word = wordFor(v.right, v.of);
    const past = history.map((a) => a.result?.skills?.[skill]).filter(Boolean).map((x: any) => wordFor(x.right, x.of));
    const best = past.reduce((b, x) => (rank(x) > rank(b) ? x : b), word);
    const lesson = set.unit?.lessons.find((l) => l.title === skill || l.id === set.skillLesson?.[skill]);
    return `<li><span class="st-skill"><b>${esc(skill)}</b><small>${Math.round(v.right * 10) / 10} of ${v.of}${lesson ? ` · <a href="${esc(page.href(`/carnatic/learn/${lesson.slug}`))}">lesson ${set.unit!.n}.${String(lesson.order).padStart(2, "0")}</a>` : ""}</small></span>`
      + `<span class="st-wb"><span class="st-word${word === "comfortable" ? " is-top" : ""}">${word}</span><span class="st-best">best: ${best}</span></span>`
      + `${chart(past.length ? past : [word])}</li>`;
  }).join("");
  const weakest = [...now].map(([k, v]) => ({ k, share: v.of ? v.right / v.of : 0 })).sort((a, b) => a.share - b.share)[0];
  const lesson = weakest && set.unit?.lessons.find((l) => l.title === weakest.k || l.id === set.skillLesson?.[weakest.k]);
  root.innerHTML = `<p class="lr-eyebrow-top">${esc(set.eyebrow)}</p><h1 class="lr-title">${esc(set.title)}</h1>`
    + `<ul class="st-profile">${rows}</ul>`
    + `<p class="st-note">Three words only: new · getting there · comfortable. <span>Chart rows, top to bottom: comfortable, getting there, new.</span></p>`
    + (lesson && weakest.share < 0.8 ? `<div class="st-next"><b>Suggested next</b><p>Lesson ${set.unit!.n}.${String(lesson.order).padStart(2, "0")}, <a href="${esc(page.href(`/carnatic/learn/${lesson.slug}`))}">“${esc(lesson.title)}”</a>, then this checkpoint again when you like.</p></div>` : "")
    + `<div class="st-actions"><button type="button" class="lr-btn" data-again>Take it again</button><a class="lr-link" href="${esc(page.href("/carnatic/practice"))}">Back to Test yourself</a></div>`;
  root.querySelector("[data-again]")?.addEventListener("click", again);
}

export async function runTest(root: HTMLElement, q: URLSearchParams, page: TestPage) {
  root.innerHTML = `<p class="st-note">Getting the questions…</p>`;
  const set = await buildSet(q, page);
  const start = () => {
    if (!set.items.length) {
      root.innerHTML = `<p class="lr-eyebrow-top">${esc(set.eyebrow)}</p><h1 class="lr-title">${esc(set.title)}</h1><p class="ch-empty">${esc(set.empty ?? "There's nothing to ask here yet.")}</p>`
        + `<div class="st-actions"><a class="lr-link" href="${esc(page.href("/carnatic/practice"))}">Back to Test yourself</a></div>`;
      return;
    }
    root.innerHTML = `<p class="lr-eyebrow-top">${esc(set.eyebrow)}</p><h1 class="lr-title st-title">${esc(set.title)}</h1><div class="st-run" data-run></div>`;
    const lessonHref = new Map(page.units.flatMap((u) => u.lessons.map((l) => [l.id, { title: l.title, href: page.href(`/carnatic/learn/${l.slug}`) }] as const)));
    new QuizRunner(root.querySelector<HTMLElement>("[data-run]")!, set.items, {
      script: page.script, tamil: page.tamil, cards: true, ownEnd: true,
      record: { itemId: set.itemId, kind: set.recordKind },
      from: (p) => { const l = p.lesson ? lessonHref.get(p.lesson) : null; return l ? { text: l.title, href: l.href } : null; },
      onDone: (s) => (set.kind === "checkpoint" ? checkpointProfile : resultList)(root, set, s, page, async () => {
        const fresh = await buildSet(q, page);
        Object.assign(set, fresh);
        start();
      }),
    });
  };
  start();
}
