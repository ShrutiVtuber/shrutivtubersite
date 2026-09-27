/* The exercise engine (README_v2 §5): every item type in one visual
 * language, inside a lesson, in Test yourself, in review and in the admin
 * preview.
 *
 * The card, in order: eyebrow (position · type), id in mono, prompt in
 * display type, controls, the explanation after ANY answer with a link to the
 * lesson it comes from, then the action. Right: accent outline and wash.
 * Wrong pick: faint ink, strikethrough, "your answer". Missed: dashed accent
 * outline. Never red, never a score or a percentage; a wrong answer is
 * "Not quite. We'll come back to this one." and becomes a review card.
 */
import { checkNumber, checkSargam, checkText, clock, seconds, type SargamRule } from "../answers";
import { check as constructCheck, eduppuUnits, perAvartanam, type ConstructSpec } from "../construct";
import { generate, type GenData, type GenItem } from "../generators";
import { inline, type Script, type TamilStyle } from "../notation";
import { phraseHtml } from "../render";
import { recordAttempt, review } from "./learner";
import { playLine } from "./phrase";
import { settings, startDrone, theDrone } from "./state";
import { pitchHz } from "../notation";
import { loadPlayer, type Player } from "./embed";
import { blip, ctx as audioCtx, talaSound } from "./audio";

export interface Item { type: string; [k: string]: any }
export interface Exercise { id: string; kind: string; title?: string; lesson?: string; items?: Item[]; [k: string]: any }

export interface EngineOpts {
  script: Script;
  tamil?: TamilStyle;
  /** "From “…”" link for an item's explanation. */
  from?: (item: PreparedItem) => { text: string; href: string } | null;
  /** Ids of the questions as the eyebrow shows them. */
  eyebrow?: (item: PreparedItem, index: number, total: number) => string;
  /** Record the attempt (quiz or checkpoint) when the set ends. */
  record?: { itemId: string; kind: "quiz" | "checkpoint" | "review"; skills?: Record<string, string> } | null;
  /** Turn wrong answers into review cards (and right ones into reviews of existing cards). */
  cards?: boolean;
  onDone?: (summary: Summary) => void;
  /** Recordings the page knows, for ear items with a recording and timestamps. */
  recordings?: Record<string, { provider: string; url: string; label: string }>;
  singleItem?: boolean;
  /** The page draws its own result screen (Test yourself): skip the runner's. */
  ownEnd?: boolean;
}

export interface PreparedItem { key: string; label: string; exId: string; lesson?: string; item: Item; gen?: GenItem; skill?: string }
export interface Summary { right: number; of: number; items: { key: string; right: boolean; skill?: string; text?: string; card?: string; share?: number }[] }

const esc = (s: string) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// ── data for generators and raga scales ────────────────────────────────────

let dataPromise: Promise<GenData & { scales: Record<string, string>; ragaNames: string[] }> | null = null;

export function genData() {
  if (!dataPromise) {
    const get = (n: string) => fetch(`/api/carnatic/data/${n}`).then((r) => (r.ok ? r.json() : null)).catch(() => null);
    dataPromise = Promise.all([get("ragas.json"), get("talas.json"), get("lessons.json")]).then(([ragas, talas, lessons]) => {
      const scales: Record<string, string> = {};
      const names: string[] = [];
      for (const r of [...(ragas?.janyas ?? []), ...(ragas?.performed ?? [])]) {
        scales[r.id] = `${r.arohana} ${r.avarohana}`;
        names.push(r.name);
      }
      for (const m of ragas?.melakartas ?? []) { scales[m.id] = `${m.arohana} ${m.avarohana}`; if (!names.includes(m.name)) names.push(m.name); }
      return {
        melas: ragas?.melakartas ?? [], janyas: [...(ragas?.janyas ?? [])], suladi: talas?.suladi ?? [],
        practical: talas?.practical ?? [], lessonSets: lessons?.sets ?? [], scales, ragaNames: names.sort(),
      };
    });
  }
  return dataPromise;
}

// ── preparing items ────────────────────────────────────────────────────────

const TYPE_LABEL: Record<string, string> = {
  choice: "Choose one", multi: "Choose all that apply", order: "Drag to order", number: "A number", text: "Type the answer",
  sargam: "Write it in notation", fill: "Fill the gaps", ear: "Listen", timestamp: "Mark a moment", tap: "Tap the moment", generated: "Generated",
  construct: "Construction task",
};

export function prepare(ex: Exercise): PreparedItem[] {
  return (ex.items ?? []).flatMap((item, i) => {
    const t = item.type === "choice" && (item.select === "many" || Array.isArray(item.answer)) ? "multi" : item.type;
    const one = (k = 0): PreparedItem => ({ key: `${ex.id}#${i + 1}${k ? `.${k + 1}` : ""}`, label: TYPE_LABEL[t] ?? item.type,
      exId: `${ex.id}.${i + 1}`, lesson: ex.lesson, item, skill: item.skill });
    // match: one choice card per pair, the options being all the rights (FORMAT.md §4a).
    if (item.type === "match" && Array.isArray(item.pairs)) {
      const rights = item.pairs.map((p: any, k: number) => ({ id: `r${k}`, text: String(p.right) }));
      return item.pairs.map((p: any, k: number): PreparedItem => ({
        key: `${ex.id}#${i + 1}.${k + 1}`, label: "Match", exId: `${ex.id}.${i + 1}`, lesson: ex.lesson, skill: item.skill,
        item: { type: "choice", text: `${item.text}: ${p.left}`, options: rights, answer: `r${k}`, explain: item.explain } }));
    }
    // A generator with `count` asks that many fresh questions (FORMAT.md §4d).
    const n = item.type === "generated" ? Math.max(1, Math.min(8, Number(item.settings?.count ?? 1) || 1)) : 1;
    return Array.from({ length: n }, (_, k) => one(k));
  });
}

// ── the runner ─────────────────────────────────────────────────────────────

export class QuizRunner {
  private at = 0;
  private results: Summary["items"] = [];
  private started = new Date().toISOString();
  private t0 = Date.now();

  constructor(private root: HTMLElement, private items: PreparedItem[], private o: EngineOpts) {
    this.root.classList.add("ex-runner");
    void this.show();
  }

  private async show() {
    if (this.at >= this.items.length) return this.finish();
    const p = this.items[this.at];
    const card = document.createElement("div");
    card.className = "ex-card";
    const eyebrow = this.o.eyebrow?.(p, this.at, this.items.length)
      ?? `Question ${this.at + 1} of ${this.items.length} · ${p.label}`;
    card.innerHTML = `<div class="ex-head"><span class="ex-eyebrow">${esc(eyebrow)}</span><span class="ex-id">${esc(p.exId)}</span></div><div class="ex-body"></div>`;
    this.root.replaceChildren(card);
    const body = card.querySelector<HTMLElement>(".ex-body")!;
    await renderItem(body, p, this.o, (right, share) => {
      this.results.push({ key: p.key, right, skill: p.skill, text: String((p.gen as any)?.text ?? p.item.text ?? ""), card: p.gen?.card ?? p.key,
                          ...(share !== undefined ? { share } : {}) });
      if (this.o.cards && share === undefined) review(p.gen?.card ?? p.key, right);
    }, () => { this.at += 1; void this.show(); }, this.at === this.items.length - 1);
  }

  private finish() {
    const right = this.results.filter((r) => r.right).length;
    const summary: Summary = { right, of: this.results.length, items: this.results };
    if (this.o.record) {
      const skills: Record<string, { right: number; of: number }> = {};
      for (const r of this.results) {
        const sk = r.skill ?? this.o.record.skills?.[r.key];
        if (!sk) continue;
        skills[sk] = skills[sk] ?? { right: 0, of: 0 };
        skills[sk].of += 1;
        skills[sk].right += r.share !== undefined ? r.share : r.right ? 1 : 0;
      }
      recordAttempt({ itemId: this.o.record.itemId, kind: this.o.record.kind, startedAt: this.started,
                      seconds: Math.round((Date.now() - this.t0) / 1000),
                      result: { items: this.results.map((r) => ({ key: r.key, right: r.right })), right, of: summary.of,
                                ...(Object.keys(skills).length ? { skills } : {}) } });
    }
    if (this.o.ownEnd) { this.o.onDone?.(summary); return; }
    const back = summary.of - right;
    const wrap = document.createElement("div");
    wrap.className = "ex-card ex-end";
    wrap.innerHTML = `<p class="ex-end-h">${right} of ${summary.of} ${right === 1 ? "was" : "were"} right the first time.</p>`
      + `<p class="ex-end-p">${back ? `${back === 1 ? "The other one comes" : `The other ${back} come`} back later in review. ` : ""}Results are for you only.</p>`
      + `<div class="ex-actions"><button type="button" class="ex-btn ex-btn-s" data-again>Try again</button></div>`;
    this.root.replaceChildren(wrap);
    wrap.querySelector("[data-again]")?.addEventListener("click", () => {
      this.at = 0; this.results = []; this.started = new Date().toISOString(); this.t0 = Date.now(); void this.show();
    });
    this.o.onDone?.(summary);
  }
}

// ── one item ───────────────────────────────────────────────────────────────

function explainBox(right: boolean | "close" | null, text: string, from: { text: string; href: string } | null, extra = ""): string {
  const h = right === null ? "Noted." : right === "close" ? "Close." : right ? "Yes." : "Not quite. We'll come back to this one.";
  return `<div class="ex-explain"><p class="ex-verdict">${h}</p>${extra}<p>${esc(text)}</p>`
    + (from ? `<a class="ex-from" href="${esc(from.href)}">From “${esc(from.text)}” ›</a>` : "") + `</div>`;
}

function actions(check: string, next: string): string {
  return `<div class="ex-actions">${check}${next}</div>`;
}

export async function renderItem(el: HTMLElement, p: PreparedItem, o: EngineOpts, onAnswer: (right: boolean, share?: number) => void,
                                 onNext: () => void, last = false): Promise<void> {
  let item = p.item;
  // A checkpoint's tap and drill parts (FORMAT.md §5): they count in the share of targets or items right.
  if (item.type === "_tap" || item.type === "_drill") {
    const next = `<div class="ex-actions"><button type="button" class="ex-btn" data-next hidden>${last ? "Finish" : "Next"}</button></div>`;
    el.innerHTML = `<p class="ex-prompt">${esc(item.text ?? "")}</p><div data-part></div>${next}`;
    const host = el.querySelector<HTMLElement>("[data-part]")!;
    const nextBtn = el.querySelector<HTMLButtonElement>("[data-next]")!;
    nextBtn.addEventListener("click", onNext);
    let reported = false;
    const report = (share: number) => {
      if (reported) return;
      reported = true;
      if (share >= 0) onAnswer(share >= 0.8, share); // below zero: nothing could be asked, so the profile says nothing

      nextBtn.hidden = false;
    };
    if (item.type === "_tap") {
      const { mountTap } = await import("./taptask");
      const task = await mountTap(host, item.spec, item.overrides ?? {});
      if (task) task.done = (r) => report(r.of ? (r.perfect + r.onTime) / r.of : 0);
      else report(0);
    } else {
      const { runSession } = await import("./ear");
      await runSession(host, [item.level], item.drills, { script: o.script, tamil: o.tamil, size: item.count, set: item.set,
        done: () => true, backHref: "", lessonHref: () => null, embedded: (right, of) => report(of ? right / of : -1) });
    }
    return;
  }
  const data = await genData();
  if (item.type === "generated") {
    const g = generate(item.generator, data, item.settings ?? {});
    if (!g) {
      el.innerHTML = `<p class="ex-prompt">This generator (${esc(item.generator)}) can't make a question here.</p>`
        + actions("", `<button type="button" class="ex-btn" data-next>${last ? "Finish" : "Next"}</button>`);
      el.querySelector("[data-next]")?.addEventListener("click", onNext);
      return;
    }
    p.gen = g;
    item = { ...g, type: g.type, explain: g.explain, generated: true, ...(g.rule ? g.rule : {}) };
  }
  const from = o.from?.(p) ?? null;
  const nextLabel = o.singleItem ? "" : last ? "Finish" : "Next";
  const prompt = `<p class="ex-prompt">${esc(item.text ?? "")}</p>${p.gen?.note ? `<p class="ex-note">${esc(p.gen.note)}</p>` : ""}`;
  const answered = (right: boolean | "close" | null, extra = "") => {
    el.querySelector(".ex-actions")?.remove();
    el.querySelectorAll<HTMLElement>("input, button[data-opt], [data-pad] button, select").forEach((x) => { (x as HTMLInputElement).disabled = true; });
    el.insertAdjacentHTML("beforeend", explainBox(right, String(item.explain ?? ""), from, extra));
    const another = p.gen ? `<button type="button" class="ex-btn ex-btn-s" data-another>Another one</button>` : "";
    el.insertAdjacentHTML("beforeend", actions(another, nextLabel ? `<button type="button" class="ex-btn" data-next>${nextLabel}</button>` : ""));
    el.querySelector("[data-next]")?.addEventListener("click", onNext);
    el.querySelector("[data-another]")?.addEventListener("click", () => void renderItem(el, { ...p, gen: undefined }, o, onAnswer, onNext, last));
    if (right !== null) onAnswer(right === true);
  };
  const type = item.type === "choice" && (item.select === "many" || Array.isArray(item.answer)) ? "multi" : item.type;
  switch (type) {
    case "choice": case "multi": return choiceItem(el, item, type === "multi", prompt, answered, !!p.gen);
    case "order": return orderItem(el, item, prompt, answered);
    case "number": return numberItem(el, item, prompt, answered, !!p.gen);
    case "text": return textItem(el, item, prompt, answered, data.ragaNames, !!p.gen);
    case "sargam": return sargamItem(el, item, prompt, answered, o, data.scales, !!p.gen);
    case "fill": return fillItem(el, item, prompt, answered, o, data.scales);
    case "ear": return earItem(el, item, prompt, answered, o, data.scales);
    case "timestamp": case "tap": return timestampItem(el, item, prompt, answered, o);
    case "construct": return constructItem(el, item, prompt, answered, o, data);
    default:
      el.innerHTML = `${prompt}<p class="ex-note">This kind of question (${esc(item.type)}) can't be shown here yet.</p>`
        + actions("", `<button type="button" class="ex-btn" data-next>${nextLabel || "Close"}</button>`);
      el.querySelector("[data-next]")?.addEventListener("click", onNext);
  }
}

type Answered = (right: boolean | "close" | null, extra?: string) => void;

function checkBtn(label = "Check"): string {
  return actions("", `<button type="button" class="ex-btn" data-check>${label}</button>`);
}

// choice and multi-select
function choiceItem(el: HTMLElement, item: Item, many: boolean, prompt: string, answered: Answered, gen = false) {
  const opts: { id: string; text: string }[] = item.options ?? [];
  const answer = new Set<string>((Array.isArray(item.answer) ? item.answer : [item.answer]).map(String));
  el.innerHTML = `${prompt}<div class="ex-opts" role="${many ? "group" : "radiogroup"}">${opts.map((op) =>
    `<button type="button" class="ex-opt${many ? " ex-multi" : ""}" data-opt="${esc(op.id)}" aria-pressed="false"><span class="ex-mark" aria-hidden="true"></span><span class="ex-opt-t">${esc(op.text)}</span><span class="ex-tag"></span></button>`).join("")}</div>${checkBtn()}`;
  const buttons = [...el.querySelectorAll<HTMLButtonElement>("[data-opt]")];
  buttons.forEach((b) => b.addEventListener("click", () => {
    if (!many) buttons.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
    else b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true"));
  }));
  el.querySelector("[data-check]")!.addEventListener("click", () => {
    const chosen = new Set(buttons.filter((b) => b.getAttribute("aria-pressed") === "true").map((b) => b.dataset.opt!));
    if (!chosen.size) return;
    const right = chosen.size === answer.size && [...chosen].every((c) => answer.has(c));
    buttons.forEach((b) => {
      const id = b.dataset.opt!;
      const tag = b.querySelector(".ex-tag")!;
      if (chosen.has(id) && answer.has(id)) { b.classList.add("is-right"); tag.textContent = "your answer ✓"; }
      else if (chosen.has(id)) { b.classList.add("is-wrong"); tag.textContent = "your answer"; }
      else if (answer.has(id)) { b.classList.add("is-missed"); tag.textContent = many ? "missed" : "answer"; }
    });
    const why = [...chosen].map((c) => item.why?.[c]).filter(Boolean).map((w: string) => `<p class="ex-why">${esc(w)}</p>`).join("");
    answered(right, why);
  });
}

// order
function orderItem(el: HTMLElement, item: Item, prompt: string, answered: Answered) {
  const opts: { id: string; text: string }[] = item.options ?? [];
  // Start from a shuffled order that isn't already the answer.
  let order = [...opts];
  for (let k = 0; k < 6 && order.map((o) => o.id).join() === (item.answer ?? []).join(); k++) order = [...opts].sort(() => Math.random() - 0.5);
  el.innerHTML = `${prompt}<ol class="ex-order" data-list></ol>${checkBtn()}`;
  const list = el.querySelector<HTMLOListElement>("[data-list]")!;
  let dragging: HTMLElement | null = null;
  const draw = () => {
    list.innerHTML = order.map((op, i) => `<li class="ex-row" draggable="true" data-id="${esc(op.id)}"><span class="ex-grip" aria-hidden="true">⋮⋮</span><span class="ex-n">${i + 1}</span><span class="ex-opt-t">${esc(op.text)}</span><span class="ex-tag"></span>`
      + `<span class="ex-move"><button type="button" data-up aria-label="Move up">↑</button><button type="button" data-down aria-label="Move down">↓</button></span></li>`).join("");
    list.querySelectorAll<HTMLElement>("li").forEach((li, i) => {
      li.querySelector("[data-up]")?.addEventListener("click", () => { if (i > 0) { [order[i - 1], order[i]] = [order[i], order[i - 1]]; draw(); } });
      li.querySelector("[data-down]")?.addEventListener("click", () => { if (i < order.length - 1) { [order[i + 1], order[i]] = [order[i], order[i + 1]]; draw(); } });
      li.addEventListener("dragstart", () => { dragging = li; li.classList.add("is-drag"); });
      li.addEventListener("dragend", () => { li.classList.remove("is-drag"); dragging = null; });
      li.addEventListener("dragover", (e) => {
        e.preventDefault();
        if (!dragging || dragging === li) return;
        const from = order.findIndex((x) => x.id === dragging!.dataset.id);
        const to = order.findIndex((x) => x.id === li.dataset.id);
        const [moved] = order.splice(from, 1);
        order.splice(to, 0, moved);
        draw();
        dragging = list.querySelector(`[data-id="${CSS.escape(moved.id)}"]`);
      });
    });
  };
  draw();
  el.querySelector("[data-check]")!.addEventListener("click", () => {
    const want: string[] = item.answer ?? [];
    const right = order.map((o) => o.id).join() === want.join();
    list.querySelectorAll<HTMLElement>("li").forEach((li, i) => {
      const ok = want[i] === li.dataset.id;
      li.classList.add(ok ? "is-right" : "is-wrong");
      li.draggable = false;
      li.querySelector(".ex-move")?.remove();
      li.querySelector(".ex-tag")!.textContent = ok ? "✓" : `goes ${want.indexOf(li.dataset.id!) + 1}${["st", "nd", "rd"][want.indexOf(li.dataset.id!)] ?? "th"}`;
    });
    answered(right);
  });
}

// number
function numberItem(el: HTMLElement, item: Item, prompt: string, answered: Answered, gen = false) {
  const unit = item.unit ?? item.rule?.unit ?? "";
  el.innerHTML = `${prompt}<label class="ex-num"><input type="text" inputmode="decimal" autocomplete="off" aria-label="Your answer">${unit ? `<span>${esc(unit)}</span>` : ""}</label>${checkBtn()}`;
  const input = el.querySelector<HTMLInputElement>("input")!;
  const go = () => {
    if (!input.value.trim()) return;
    const accept = [Number(item.answer), ...((item.accept ?? []) as string[]).map(Number)];
    let verdict: "right" | "close" | "wrong" = "wrong";
    for (const a of accept) {
      const v = checkNumber(input.value, a, Number(item.tolerance ?? 0), item.close !== undefined ? Number(item.close) : undefined);
      if (v === "right") { verdict = "right"; break; }
      if (v === "close") verdict = "close";
    }
    const box = input.closest(".ex-num")!;
    box.classList.add(verdict === "right" ? "is-right" : "is-wrong");
    if (verdict !== "right") box.insertAdjacentHTML("afterend", `<span class="ex-correct">${esc(item.answer)} <small>${esc(unit)}</small></span>`);
    answered(verdict === "right" ? true : verdict === "close" ? "close" : false);
  };
  el.querySelector("[data-check]")!.addEventListener("click", go);
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
  input.focus({ preventScroll: true });
}

// text (with raga-name suggestions)
function textItem(el: HTMLElement, item: Item, prompt: string, answered: Answered, ragaNames: string[], gen = false) {
  const accept: string[] = item.accept ?? (item.choices ?? []);
  const ragaLike = /raga/i.test(item.text ?? "") || !!item.choices || item.accept_from;
  const listId = `ex-dl-${Math.random().toString(36).slice(2)}`;
  const names = item.choices ? (item.choices as string[]).map((c) => c[0].toUpperCase() + c.slice(1)) : ragaNames;
  el.innerHTML = `${prompt}<div class="ex-text"><input type="text" autocomplete="off" aria-label="Your answer" ${ragaLike ? `list="${listId}"` : ""}>`
    + (ragaLike ? `<datalist id="${listId}">${names.map((n) => `<option value="${esc(n)}">`).join("")}</datalist><small class="ex-note">Spelling variants are accepted.</small>` : "")
    + `</div>${checkBtn()}`;
  const input = el.querySelector<HTMLInputElement>("input")!;
  const go = () => {
    if (!input.value.trim()) return;
    if (!accept.length) {
      input.classList.add("is-wrong");
      answered(null);
      return;
    }
    const right = checkText(input.value, accept);
    input.classList.add(right ? "is-right" : "is-wrong");
    if (!right) input.insertAdjacentHTML("afterend", `<p class="ex-correct">Answer: ${esc(accept[0])}</p>`);
    answered(right);
  };
  el.querySelector("[data-check]")!.addEventListener("click", go);
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
}

// the sargam input pad (swara buttons, variants, octave, hold, backspace)
export function sargamPad(host: HTMLElement, o: { script: Script; tamil?: TamilStyle }, initial = ""): { value: () => string; set: (v: string) => void } {
  let tokens: string[] = initial ? initial.split(/\s+/).filter(Boolean) : [];
  let variant: number | null = null;
  let octave = 0;
  host.innerHTML = `<div class="ex-sg-input" tabindex="0" aria-label="Your notation. Type letters, or use the buttons."><div class="ex-sg-line" data-line></div></div>`
    + `<div class="ex-pad" data-pad>${"SRGMPDN".split("").map((s) => `<button type="button" data-sw="${s}">${inline(s, o.script, o.tamil)}</button>`).join("")}`
    + `<span class="ex-pad-row">${[1, 2, 3].map((n) => `<button type="button" class="ex-pad-s" data-var="${n}" aria-pressed="false">${n}</button>`).join("")}`
    + `<button type="button" class="ex-pad-s" data-oct="1" aria-pressed="false">Upper ˙</button><button type="button" class="ex-pad-s" data-oct="-1" aria-pressed="false">Lower .</button>`
    + `<button type="button" class="ex-pad-s" data-hold>, hold</button><button type="button" class="ex-pad-s" data-back aria-label="Delete">⌫</button></span></div>`;
  const line = host.querySelector<HTMLElement>("[data-line]")!;
  const draw = () => { line.innerHTML = tokens.length ? phraseHtml(tokens.join(" "), { script: o.script, tamil: o.tamil, subs: true }) + `<span class="ex-caret"></span>` : `<span class="ex-caret"></span>`; };
  const add = (s: string) => {
    const v = s === "S" || s === "P" ? "" : variant ?? "";
    tokens.push(`${octave < 0 ? "." : ""}${s}${v}${octave > 0 ? "'" : ""}`);
    draw();
  };
  host.querySelectorAll<HTMLButtonElement>("[data-sw]").forEach((b) => b.addEventListener("click", () => add(b.dataset.sw!)));
  host.querySelectorAll<HTMLButtonElement>("[data-var]").forEach((b) => b.addEventListener("click", () => {
    const n = Number(b.dataset.var);
    variant = variant === n ? null : n;
    host.querySelectorAll("[data-var]").forEach((x) => x.setAttribute("aria-pressed", String(Number((x as HTMLElement).dataset.var) === variant)));
  }));
  host.querySelectorAll<HTMLButtonElement>("[data-oct]").forEach((b) => b.addEventListener("click", () => {
    const n = Number(b.dataset.oct);
    octave = octave === n ? 0 : n;
    host.querySelectorAll("[data-oct]").forEach((x) => x.setAttribute("aria-pressed", String(Number((x as HTMLElement).dataset.oct) === octave)));
  }));
  host.querySelector("[data-hold]")!.addEventListener("click", () => { tokens.push(","); draw(); });
  host.querySelector("[data-back]")!.addEventListener("click", () => { tokens.pop(); draw(); });
  const box = host.querySelector<HTMLElement>(".ex-sg-input")!;
  box.addEventListener("keydown", (e) => {
    const k = e.key;
    if (/^[srgmpdnSRGMPDN]$/.test(k)) { add(k.toUpperCase()); e.preventDefault(); }
    else if (/^[123]$/.test(k) && tokens.length) {
      const last = tokens[tokens.length - 1];
      if (/^[.]*[RGMDN]'*$/.test(last)) tokens[tokens.length - 1] = last.replace(/([RGMDN])/, `$1${k}`);
      draw(); e.preventDefault();
    } else if (k === "'" && tokens.length) { tokens[tokens.length - 1] += "'"; draw(); e.preventDefault(); }
    else if (k === "." ) { octave = octave === -1 ? 0 : -1; e.preventDefault(); }
    else if (k === "," || k === ";") { tokens.push(k); draw(); e.preventDefault(); }
    else if (k === "Backspace") { tokens.pop(); draw(); e.preventDefault(); }
  });
  draw();
  return { value: () => tokens.join(" "), set: (v: string) => { tokens = v.split(/\s+/).filter(Boolean); draw(); } };
}

function ruleOf(item: Item, scales: Record<string, string>): SargamRule {
  return {
    raga: item.raga, scale: item.raga ? scales[item.raga] : undefined,
    checkHolds: item.check_holds ?? item.checkHolds ?? false, checkOctaves: item.check_octaves ?? item.checkOctaves ?? true,
    checkBars: item.check_bars ?? false, enharmonic: item.enharmonic ?? "reject",
    variantsRequired: item.variantsRequired ?? !item.raga,
  };
}

export function sargamResultHtml(res: ReturnType<typeof checkSargam>, o: EngineOpts): string {
  const draw = (k: string) => {
    const [name, oct] = k.split("@");
    const n = Number(oct);
    return phraseHtml(`${n < 0 ? ".".repeat(-n) : ""}${name}${n > 0 ? "'".repeat(n) : ""}`, { script: o.script, tamil: o.tamil, subs: true });
  };
  return `<div class="ex-sg-result">${res.cells.map((c) => {
    if (c.ok) return `<span class="ex-sg-cell">${draw(c.given)}</span>`;
    if (c.missing) return `<span class="ex-sg-cell is-missing"><span class="ex-sg-want">${draw(c.want!)}</span><span class="ex-sg-gap"></span></span>`;
    if (c.extra) return `<span class="ex-sg-cell is-extra">${draw(c.given)}</span>`;
    return `<span class="ex-sg-cell is-wrong"><span class="ex-sg-want">${draw(c.want!)}</span>${draw(c.given)}</span>`;
  }).join("")}</div><p class="ex-partial">${esc(res.sentence)}</p>`;
}

function sargamItem(el: HTMLElement, item: Item, prompt: string, answered: Answered, o: EngineOpts, scales: Record<string, string>, gen = false) {
  el.innerHTML = `${prompt}<div data-pad-host></div>${checkBtn()}`;
  const pad = sargamPad(el.querySelector<HTMLElement>("[data-pad-host]")!, o);
  el.querySelector("[data-check]")!.addEventListener("click", () => {
    const v = pad.value();
    if (!v) return;
    const res = checkSargam(v, String(item.answer ?? ""), ruleOf(item, scales));
    const host = el.querySelector<HTMLElement>("[data-pad-host]")!;
    host.classList.add(res.right ? "is-right" : "is-wrong");
    host.innerHTML = sargamResultHtml(res, o);
    answered(res.right);
  });
}

// fill the gaps
function fillItem(el: HTMLElement, item: Item, prompt: string, answered: Answered, o: EngineOpts, scales: Record<string, string>) {
  const toks = String(item.line ?? "").split(/\s+/).filter(Boolean);
  const answers: string[] = (Array.isArray(item.answer) ? item.answer : String(item.answer ?? "").split(/\s+/)).map(String);
  let g = 0;
  const cells = toks.map((t) => t === "_" ? `<input class="ex-gap" data-gap="${g++}" size="3" aria-label="Gap ${g}" autocomplete="off">`
    : t === "|" || t === "||" ? phraseHtml(t, { script: o.script, tamil: o.tamil }) : phraseHtml(t, { script: o.script, tamil: o.tamil, subs: true }));
  el.innerHTML = `${prompt}<div class="ex-fill">${cells.join("")}</div><p class="ex-note">Type a swara in each gap (for example G3, S' or ,).</p>${checkBtn()}`;
  el.querySelector("[data-check]")!.addEventListener("click", () => {
    const inputs = [...el.querySelectorAll<HTMLInputElement>("[data-gap]")];
    if (inputs.some((i) => !i.value.trim())) return;
    const rule = { ...ruleOf(item, scales), checkHolds: item.check_holds ?? true };
    let allRight = true;
    inputs.forEach((inp, i) => {
      const res = checkSargam(inp.value, answers[i] ?? "", rule);
      const box = document.createElement("span");
      box.className = `ex-gap-done ${res.right ? "is-right" : "is-wrong"}`;
      box.innerHTML = res.right ? phraseHtml(answers[i], { script: o.script, tamil: o.tamil, subs: true })
        : `<span class="ex-sg-want">${phraseHtml(answers[i], { script: o.script, tamil: o.tamil, subs: true })}</span><s>${esc(inp.value)}</s>`;
      inp.replaceWith(box);
      if (!res.right) allRight = false;
    });
    answered(allRight);
  });
}

// ear
async function playAudio(audio: any, o: EngineOpts, scales: Record<string, string>, box?: HTMLElement): Promise<void> {
  if (!audio) return;
  if (audio.kind === "recording") {
    const r = o.recordings?.[audio.id];
    if (r && box) loadPlayer(box, r.provider, r.url, { start: seconds(audio.start ?? null) ?? undefined });
    return;
  }
  const s = settings();
  if (audio.drone !== false && !theDrone().playing) startDrone(audio.raga && scales[audio.raga] && !/\bP\b/.test(scales[audio.raga]) ? "ma" : undefined);
  const unit = 60 / Number(audio.tempo ?? 60) / ({ 1: 1, 2: 2, 3: 4 } as Record<number, number>)[Number(audio.speed ?? 1)];
  playLine(String(audio.line ?? audio.note ?? "S"), { saHz: pitchHz(s.sa || "C3"), tuning: s.playbackTuning,
    scale: audio.raga ? scales[audio.raga] : undefined, unit: Math.max(0.2, unit), at: audioCtx().currentTime + 0.25 });
}

function earItem(el: HTMLElement, item: Item, prompt: string, answered: Answered, o: EngineOpts, scales: Record<string, string>) {
  const audio = item.audio ?? {};
  const synth = audio.kind !== "recording";
  const player = `<div class="ex-ear"><button type="button" class="lr-play lr-play-lg" data-listen aria-label="Play">${`<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M5 3l8 5-8 5z" fill="currentColor"/></svg>`}</button>`
    + `<div><p>Play again as often as you like</p><small>${synth ? "Synthesised approximation · drone on Sa" : "A recording · loads when you press play"}</small></div></div>`
    + (synth ? "" : `<div class="ex-rec" data-rec></div>`);
  const inner = document.createElement("div");
  el.innerHTML = prompt + player;
  el.appendChild(inner);
  el.querySelector("[data-listen]")!.addEventListener("click", () => void playAudio(audio, o, scales, el.querySelector<HTMLElement>("[data-rec]") ?? undefined));
  const sub = { ...item, type: item.options ? "choice" : "sargam" };
  if (sub.type === "choice") choiceItem(inner, sub, Array.isArray(item.answer), "", (r, x) => { el.querySelectorAll<HTMLElement>(":scope > .ex-actions").forEach((a) => a.remove()); answered(r, x); });
  else sargamItem(inner, sub, "", (r, x) => answered(r, x), o, scales);
  // The child's own check button sits inside `inner`; lift it to the card's foot.
  const act = inner.querySelector(".ex-actions");
  if (act) el.appendChild(act);
}

// timestamp (mark a moment in a recording)
function timestampItem(el: HTMLElement, item: Item, prompt: string, answered: Answered, o: EngineOpts) {
  const rid = item.recording ?? item.audio?.id;
  const rec = rid ? o.recordings?.[rid] : undefined;
  el.innerHTML = `${prompt}<div class="ex-stamp-player" data-box>${rec ? `<button type="button" class="ex-btn ex-btn-s" data-load>Load the recording</button><small>Nothing loads from the provider until you press this.</small>`
    : `<small>The recording for this one isn't available here yet.</small>`}</div>`
    + `<div class="ex-stamp"><span class="ex-stamp-t" data-t>0:00</span><div class="ex-stamp-row"><button type="button" class="ex-btn ex-btn-s" data-minus>−1 s</button>`
    + `<button type="button" class="ex-btn ex-btn-s ex-btn-on" data-mark>Mark this moment</button><button type="button" class="ex-btn ex-btn-s" data-plus>+1 s</button>`
    + `<input type="text" class="ex-stamp-in" data-typed placeholder="m:ss" aria-label="Or type the time" size="6"></div></div>${checkBtn()}`;
  let marked: number | null = null;
  let player: Player | null = null;
  const show = () => { el.querySelector<HTMLElement>("[data-t]")!.textContent = marked === null ? "0:00" : clock(marked); };
  el.querySelector("[data-load]")?.addEventListener("click", () => {
    player = loadPlayer(el.querySelector<HTMLElement>("[data-box]")!, rec!.provider, rec!.url, { start: seconds(item.start ?? null) ?? undefined });
  });
  el.querySelector("[data-mark]")!.addEventListener("click", () => {
    const t = player?.time();
    marked = t ?? marked ?? 0;
    if (t === null || t === undefined) (el.querySelector<HTMLInputElement>("[data-typed]")!).focus();
    show();
  });
  el.querySelector("[data-minus]")!.addEventListener("click", () => { marked = Math.max(0, (marked ?? 0) - 1); show(); });
  el.querySelector("[data-plus]")!.addEventListener("click", () => { marked = (marked ?? 0) + 1; show(); });
  el.querySelector<HTMLInputElement>("[data-typed]")!.addEventListener("change", (e) => { const v = seconds((e.target as HTMLInputElement).value); if (v !== null) { marked = v; show(); } });
  el.querySelector("[data-check]")!.addEventListener("click", () => {
    if (marked === null) return;
    const want = seconds(item.answer);
    if (want === null) {
      answered(null, `<p class="ex-why">Shruti hasn't marked this moment yet, so there's nothing to compare with. You marked ${clock(marked)}.</p>`);
      return;
    }
    const tol = item.type === "tap" ? Number(item.tolerance_ms ?? 150) / 1000 : Number(item.tolerance ?? 6);
    const right = Math.abs(marked - want) <= tol;
    answered(right, `<p class="ex-why">Accepted between ${clock(Math.max(0, want - tol))} and ${clock(want + tol)}. You marked ${clock(marked)}.</p>`);
  });
}

// construction tasks: the builder on the tala grid
const KONNAKOL = ["ta", "ka", "di", "mi", "gi", "na", "thom", "ki", "ta ka", "jo", "nu"];

function constructItem(el: HTMLElement, item: Item, prompt: string, answered: Answered, o: EngineOpts, data: Awaited<ReturnType<typeof genData>>) {
  const counts = data.practical.find((t: any) => t.id === item.tala)?.counts.length
    ?? data.suladi.find((t: any) => t.id === item.tala)?.aksharas ?? 8;
  const spec: ConstructSpec = { input: item.input === "konnakol" ? "konnakol" : "sargam", tala: item.tala, counts,
    nadai: item.input === "konnakol" ? Number(item.nadai ?? 4) : undefined, speed: Number(item.speed ?? 1),
    eduppu: item.eduppu !== undefined ? Number(item.eduppu) : undefined, raga: item.raga };
  if (item.raga && data.scales[item.raga]) spec.allowed = new Set(data.scales[item.raga].match(/[SRGMPDN][123]?/g) ?? []);
  const per = perAvartanam(spec);
  const talaName = data.practical.find((t: any) => t.id === item.tala)?.name ?? String(item.tala ?? "").replace(/_/g, " ");
  const head = `<p class="ex-meta">${esc(talaName)} tala · ${spec.input === "konnakol" ? `nadai ${spec.nadai}` : `speed ${spec.speed}`} · target: ${esc(typeof item.target === "string" ? item.target : "land on samam")}</p>`;
  const chips = spec.input === "konnakol"
    ? `<div class="ex-chips">${KONNAKOL.map((k) => `<button type="button" data-syl="${k}">${k}</button>`).join("")}<button type="button" class="ex-chip-gap" data-syl=",">, (gap)</button><button type="button" class="ex-chip-gap" data-back>⌫</button></div>`
    : `<div data-pad-host></div>`;
  el.innerHTML = `${prompt}${head}<div class="ex-grid" data-grid style="--cols:${Math.min(counts, 8)}"></div>`
    + (item.ask_start ? `<label class="ex-start">It starts <input type="number" min="0" max="${counts}" step="0.5" value="0" data-start> counts after samam</label>` : "")
    + `${chips}<div class="ex-live" data-live></div>`
    + actions(`<button type="button" class="ex-btn ex-btn-s" data-play>Play it over the tala</button>`, `<button type="button" class="ex-btn" data-check>Check it</button>`);
  let syl: string[] = [];
  let pad: ReturnType<typeof sargamPad> | null = null;
  if (spec.input !== "konnakol") pad = sargamPad(el.querySelector<HTMLElement>("[data-pad-host]")!, o);
  const value = () => (pad ? pad.value() : syl.join(" "));
  const drawGrid = () => {
    const v = value().split(/\s+/).filter(Boolean);
    const start = eduppuUnits(spec);
    const perCount = per / counts;
    const avs = Math.max(1, Math.ceil((start + v.length) / per));
    const cells: string[] = [];
    for (let c = 0; c < counts * avs; c++) {
      const slots = Array.from({ length: perCount }, (_, j) => {
        const idx = c * perCount + j - start;
        const t = idx >= 0 ? v[idx] : undefined;
        return `<span class="ex-slot${t === undefined ? " is-empty" : t === "," ? " is-gap" : ""}">${t === undefined ? "" : t === "," ? "·" : esc(t)}</span>`;
      }).join("");
      cells.push(`<div class="ex-beat"><span class="ex-beat-n">${(c % counts) + 1}</span><div class="ex-slots">${slots}</div></div>`);
    }
    el.querySelector<HTMLElement>("[data-grid]")!.innerHTML = cells.join("");
    const res = constructCheck(value(), item.checks ?? [], spec);
    el.querySelector<HTMLElement>("[data-live]")!.innerHTML = `<p class="ex-live-h">${esc(res.status)}</p>${res.notes.map((n) => `<p>${esc(n)}</p>`).join("")}`;
  };
  el.querySelectorAll<HTMLButtonElement>("[data-syl]").forEach((b) => b.addEventListener("click", () => { syl.push(...b.dataset.syl!.split(" ")); drawGrid(); }));
  el.querySelector("[data-back]")?.addEventListener("click", () => { syl.pop(); drawGrid(); });
  el.querySelector("[data-pad-host]")?.addEventListener("click", () => setTimeout(drawGrid));
  el.querySelector("[data-pad-host]")?.addEventListener("keydown", () => setTimeout(drawGrid));
  el.querySelector<HTMLInputElement>("[data-start]")?.addEventListener("input", (e) => { spec.eduppu = Number((e.target as HTMLInputElement).value) || 0; drawGrid(); });
  el.querySelector("[data-play]")!.addEventListener("click", () => {
    const v = value().split(/\s+/).filter(Boolean);
    const tempo = 60;
    const beat = 60 / tempo;
    const perCount = per / counts;
    const t0 = audioCtx().currentTime + 0.3;
    const avs = Math.max(1, Math.ceil((eduppuUnits(spec) + v.length) / per));
    for (let c = 0; c <= counts * avs; c++) talaSound(c % counts === 0 ? "clap" : "finger", t0 + c * beat, { samam: c % counts === 0 });
    v.forEach((t, i) => {
      if (t !== ",") blip(880, t0 + ((eduppuUnits(spec) + i) / perCount) * beat, 0.05, 0.06);
    });
  });
  el.querySelector("[data-check]")!.addEventListener("click", () => {
    if (!value()) return;
    const res = constructCheck(value(), item.checks ?? [], spec);
    el.querySelector<HTMLElement>("[data-live]")!.classList.add(res.ok ? "is-right" : "is-wrong");
    answered(res.ok);
  });
  drawGrid();
}

/** Mount a whole exercise (a quiz or a checkpoint) into an element. */
export function mountQuiz(root: HTMLElement, ex: Exercise, o: EngineOpts): QuizRunner {
  return new QuizRunner(root, prepare(ex), o);
}
