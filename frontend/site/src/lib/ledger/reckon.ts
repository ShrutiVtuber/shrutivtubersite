/* The Ledger reckoned for the app: POST /ledger/reckon.json (docs/LEDGER.md
 * Contract 5).
 *
 * The Squirrel Guides app is native, and the engine is TypeScript. So the
 * app sends a plan here and gets back the figures the planner, the ledger's
 * pages and the overlays would draw for it, worked out by the SAME engine
 * with the SAME words:
 *
 *   the week       engine.ts reckon(), the stats bar's own figures
 *   What limits it limit.ts limitSentence / limitNote / limitHead / fixLabel,
 *                  in the words of copy("component:WhatLimitsIt")
 *   the first      kept.ts firstSentence (a company's rows, phase 2)
 *   It cannot open limit.ts missingRows, in copy("ledger/plan")'s words
 *   what changed   stream.ts changeLabel + changeLine, the planner's switch
 *                  exactly (component:StreamSwitch's stream.ch* labels)
 *
 * Pure apart from the Request it reads: no DOM, no fetch, no session. The
 * route file wires in loadPack() and copy(); a test passes its own, so
 * `node --test` calls the very handler the route exports.
 *
 * ⚠ It reads nothing about anybody and writes nothing: the plan arrives in
 *   the body and the answer is arithmetic on it. That is why it needs no
 *   session and no CSRF token (see the route file).
 */
import type { Ctx, Figure, Honesty, LedgerData, Plan, Reckoning, ReckonState } from "./types.ts";
import { reckon } from "./engine.ts";
import { fullPlan, changeLabel, changeLine, WORDS as STREAM_WORDS } from "./stream.ts";
import { fixLabel, fixNote, limitHead, limitNote, limitSentence, missingRows, LIMIT_SENTENCES, LIMIT_WORDS, MISSING_WORDS } from "./limit.ts";
import { firstSentence } from "./kept.ts";
import { days, money } from "./format.ts";

// ── limits (the backend's, routes/ledger.py) ────────────────────────────────

export const PLAN_BYTES = 64 * 1024;
export const CUSTOM_BYTES = 4 * 1024;
export const MAX_BATCH = 50;
export const MAX_COURSES = 64;
/** The whole body: fifty rows of a company at a few KB each fit many times over. */
export const BODY_BYTES = 1024 * 1024;

export const NOT_LOADED = "The game's data is not loaded yet, so there is nothing honest to reckon with.";

// ── the words ──────────────────────────────────────────────────────────────

export type Say = (key: string, fallback: string) => string;
export interface ReckonWords {
  /** component:WhatLimitsIt: the limit's sentences, notes, heads and fix labels. */
  limit: Record<string, string>;
  /** ledger/plan: the rows of "It cannot open yet". */
  missing: Record<string, string>;
  /** stream.ts WORDS with component:StreamSwitch's stream.ch* labels over them, as the planner's switch sends. */
  stream: typeof STREAM_WORDS;
  /** component:LedgerStats: the figures bar's unit and loss words. */
  days: string;
  loss: string;
}

const noSay: Say = (_k, v) => v;

/**
 * The words, from each scope's say(), keyed exactly as the pages key them:
 * [id].astro and [business].astro build the limit words this way, plan.astro
 * the missing rows, StreamSwitch.astro the change labels, LedgerStats.astro
 * the unit. So a sentence she edits once reads the same on the site, on
 * stream and in the app.
 */
export function wordsFrom(says: { limit?: Say; plan?: Say; stream?: Say; stats?: Say } = {}): ReckonWords {
  const limit: Record<string, string> = {};
  for (const [k, v] of Object.entries({ ...LIMIT_SENTENCES, ...LIMIT_WORDS })) limit[k] = (says.limit ?? noSay)(k, v);
  const missing: Record<string, string> = {};
  for (const [k, v] of Object.entries(MISSING_WORDS)) missing[k] = (says.plan ?? noSay)(k, v);
  const stream = { ...STREAM_WORDS };
  for (const k of Object.keys(STREAM_WORDS) as (keyof typeof STREAM_WORDS)[]) {
    if (k.startsWith("ch")) stream[k] = (says.stream ?? noSay)(`stream.${k}`, STREAM_WORDS[k]);
  }
  const stats = says.stats ?? noSay;
  return { limit, missing, stream, days: stats("unit.days", "days"), loss: stats("loss", "loss") };
}

// ── checking what arrives ──────────────────────────────────────────────────

export class Refusal extends Error {
  status: number;
  constructor(status: number, detail: string) { super(detail); this.status = status; }
}

const isObject = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);
const byteLength = (v: unknown): number => new TextEncoder().encode(JSON.stringify(v)).length;

/** A plan's shape, as the backend checks it (`_plan`): an object, 64 KB at most, and the hours grid right. */
export function checkPlan(value: unknown, what = "plan"): Partial<Plan> {
  if (!isObject(value)) throw new Refusal(422, `a ${what} is an object`);
  const size = byteLength(value);
  if (size > PLAN_BYTES) throw new Refusal(413, `the ${what} is ${Math.floor(size / 1024)} KB; ${PLAN_BYTES / 1024} KB is the most reckoned`);
  const hours = value.hours;
  if (hours != null) {
    const ok = Array.isArray(hours) && hours.length === 7 && hours.every((day) =>
      Array.isArray(day) && day.length === 24 && day.every((h) => Number.isInteger(h) && h >= 0 && h <= 9));
    if (!ok) throw new Refusal(422, "a plan's hours are seven days of 24 hours, each 0 to 9 registers");
  }
  return value as Partial<Plan>;
}

/** The ledger's context, as the backend checks a ledger's difficulty, courses and custom values. */
export function checkCtx(value: unknown): Ctx {
  if (value == null) value = {};
  if (!isObject(value)) throw new Refusal(422, "ctx is an object: {difficulty, courses, custom?, importIndex?}");
  const d = value.difficulty == null ? "normal" : value.difficulty;
  if (typeof d !== "string" || !/^[a-z0-9-]{1,40}$/.test(d.trim().toLowerCase())) {
    throw new Refusal(422, "a difficulty is its id from the game's data, like normal or custom");
  }
  const courses = value.courses == null ? [] : value.courses;
  if (!Array.isArray(courses) || courses.length > MAX_COURSES || !courses.every((c) => typeof c === "string" && c.length > 0 && c.length <= 80)) {
    throw new Refusal(422, "courses are the ids of the courses taken");
  }
  const ctx: Ctx = { difficulty: d.trim().toLowerCase(), courses: [...new Set(courses as string[])] };
  if (value.custom != null) {
    if (!isObject(value.custom)) throw new Refusal(422, "a custom difficulty is an object of values");
    if (byteLength(value.custom) > CUSTOM_BYTES) throw new Refusal(413, `a custom difficulty is ${CUSTOM_BYTES / 1024} KB at most`);
    ctx.custom = value.custom as Ctx["custom"];
  }
  if (value.importIndex != null) {
    const i = value.importIndex;
    if (typeof i !== "number" || !Number.isFinite(i) || i < 0.5 || i > 1.3) {
      throw new Refusal(422, "an import index is a number from 0.5 to 1.3");
    }
    ctx.importIndex = i;
  }
  return ctx;
}

export type ReckonRequest =
  | { kind: "one"; plan: Partial<Plan>; previous: Partial<Plan> | null; ctx: Ctx }
  | { kind: "batch"; plans: { id: string | number; plan: Partial<Plan> }[]; ctx: Ctx };

/** The body, read and checked. Throws a Refusal with the status to answer. */
export function checkBody(body: unknown): ReckonRequest {
  if (!isObject(body)) throw new Refusal(422, "the body is an object: {plan, ctx, previous?} or {plans: [{id, plan}], ctx}");
  const ctx = checkCtx(body.ctx);
  if ("plans" in body) {
    const rows = body.plans;
    if (!Array.isArray(rows) || rows.length === 0) throw new Refusal(422, "plans is a list of {id, plan}");
    if (rows.length > MAX_BATCH) throw new Refusal(413, `${MAX_BATCH} plans at most in one batch`);
    const plans = rows.map((row, i) => {
      if (!isObject(row)) throw new Refusal(422, `plans[${i}] is {id, plan}`);
      const id = row.id;
      const idOk = (typeof id === "string" && id.length > 0 && id.length <= 64) || (typeof id === "number" && Number.isSafeInteger(id));
      if (!idOk) throw new Refusal(422, `plans[${i}] needs an id: a business's id, or a string of 64 characters at most`);
      return { id: id as string | number, plan: checkPlan(row.plan, `plan (plans[${i}])`) };
    });
    return { kind: "batch", plans, ctx };
  }
  if (!("plan" in body)) throw new Refusal(422, "the body needs a plan, or plans for a batch");
  const plan = checkPlan(body.plan);
  const previous = body.previous == null ? null : checkPlan(body.previous, "previous plan");
  return { kind: "one", plan, previous, ctx };
}

/** The body as text, refused past `limit` bytes whatever Content-Length claims. */
export async function readCapped(request: Request, limit = BODY_BYTES): Promise<string> {
  const said = Number(request.headers.get("content-length") ?? "");
  if (Number.isFinite(said) && said > limit) throw new Refusal(413, `the body is more than ${limit / 1024} KB`);
  if (!request.body) return "";
  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > limit) {
      await reader.cancel().catch(() => {});
      throw new Refusal(413, `the body is more than ${limit / 1024} KB`);
    }
    chunks.push(value);
  }
  const all = new Uint8Array(size);
  let at = 0;
  for (const c of chunks) { all.set(c, at); at += c.byteLength; }
  return new TextDecoder("utf-8", { fatal: true }).decode(all);
}

// ── the answer ─────────────────────────────────────────────────────────────

export interface Amount { value: number | null; honesty: Honesty }

export interface ReckonResult {
  state: ReckonState;
  week: {
    moneyIn: Amount; goods: Amount; wages: Amount; rent: Amount; ads: Amount; deliveries: Amount;
    total: Amount & { loss: boolean };
  };
  setup: Amount;
  /** Days to pay the setup back, to a tenth. */
  paybackDays: Amount;
  /** Customers a week, whole. */
  customers: Amount;
  limit: {
    state: string;
    reason: string | null;
    by: string | null;
    hours: number | null;
    cap: number | null;
    would: number | null;
    fix: { kind: string; label: string | null; note: string; cost: Amount; weeklyCost: Amount; worth: Amount } | null;
    /** The whole sentence, as the planner's What limits it reads. */
    sentence: string;
    /** Its first sentence, as a company's rows read. */
    first: string;
    /** "held · 47 h" · "free" · "not known yet". */
    note: string;
    /** The figures bar's one word: "Registers" · "Nothing" · "—". */
    head: string;
  };
  /** What it needs before it can open, one sentence each (the planner's "It cannot open yet"). */
  missing: { path: string; text: string }[];
  /** The figures bar at a phone's width, written as the website's stats bar writes it. */
  bar: { week: string; loss: string | null; payback: string; limit: string };
  /** With `previous`: what just changed, as the overlay prints it. Null when nothing did. */
  change?: { label: string; delta: number | null; sentence: string; caret: string } | null;
}

const dollars = (f: Figure | undefined): Amount => ({
  value: f?.value == null || !Number.isFinite(f.value) ? null : Math.round(f.value),
  honesty: f?.honesty ?? "not-counted",
});
const tenths = (f: Figure | undefined): Amount => ({
  value: f?.value == null || !Number.isFinite(f.value) ? null : Math.round(f.value * 10) / 10,
  honesty: f?.honesty ?? "not-counted",
});

/** Reckon, or null when the engine cannot read the plan at all (never a stale or made-up figure). */
export function reckonPlan(data: LedgerData, plan: Partial<Plan>, ctx: Ctx): Reckoning | null {
  try {
    return reckon(data, fullPlan(plan), ctx);
  } catch {
    return null;
  }
}

const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);

/** One plan's answer. `previous` adds the change line, as the planner's Plan on stream switch builds it. */
export function reckonResult(data: LedgerData, plan: Partial<Plan>, ctx: Ctx, words: ReckonWords,
  previous: Partial<Plan> | null = null): ReckonResult | null {
  const rk = reckonPlan(data, plan, ctx);
  if (!rk) return null;
  const limit = rk.limit;
  const sentence = limitSentence(limit, words.limit);
  const w = rk.week;
  const total = dollars(w.total);
  const fix = limit.fix ?? null;
  const out: ReckonResult = {
    state: rk.state,
    week: {
      moneyIn: dollars(w.moneyIn), goods: dollars(w.goods), wages: dollars(w.wages), rent: dollars(w.rent),
      ads: dollars(w.ads), deliveries: dollars(w.deliveries),
      total: { ...total, loss: !!w.loss },
    },
    setup: dollars(rk.setup.total),
    paybackDays: tenths(rk.paybackDays),
    customers: dollars(rk.customers),
    limit: {
      state: limit.state,
      reason: limit.reason ?? null,
      by: limit.by ?? null,
      hours: limit.hours ?? null,
      cap: limit.cap ?? null,
      would: limit.would == null ? null : Math.round(limit.would),
      fix: fix ? {
        kind: fix.kind,
        label: fixLabel(limit, words.limit),
        note: fixNote(limit, words.limit),
        cost: dollars(fix.cost), weeklyCost: dollars(fix.weeklyCost), worth: dollars(fix.worth),
      } : null,
      sentence,
      first: firstSentence(sentence),
      note: limitNote(limit, words.limit),
      head: limitHead(limit, words.limit),
    },
    missing: rk.state === "cannot-open" || rk.missing.length ? missingRows(rk.missing, data, fullPlan(plan), words.missing) : [],
    bar: {
      week: money(w.total.value),
      loss: w.loss ? words.loss : null,
      payback: days(rk.paybackDays.value, words.days),
      limit: limitHead(limit, words.limit),
    },
  };
  if (previous) {
    if (same(fullPlan(previous), fullPlan(plan))) {
      out.change = null;
    } else {
      /* stream-switch.ts liveBody: the label from changeLabel against the plan
         before, the delta the two weeks' difference to the dollar, and the
         line around it the overlay's own (stream.ts WORDS). */
      const before = reckonPlan(data, previous, ctx)?.week.total.value;
      const after = w.total.value;
      const delta = before != null && after != null && Number.isFinite(before) && Number.isFinite(after) ? Math.round(after - before) : null;
      const label = changeLabel(data, previous, plan, rk, words.stream);
      const line = changeLine({ label, delta }, STREAM_WORDS);
      out.change = { label, delta, sentence: line?.text ?? label, caret: line?.caret ?? "" };
    }
  }
  return out;
}

// ── the handler ────────────────────────────────────────────────────────────

export interface ReckonDeps {
  /** The pack, or null when it is not loaded (lib/ledger/data.ts loadPack). */
  pack: () => Promise<LedgerData | null>;
  /** The words, from copy() (see wordsFrom). */
  words: () => Promise<ReckonWords>;
}

const HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
};

const answer = (status: number, body: unknown, extra: Record<string, string> = {}) =>
  new Response(JSON.stringify(body), { status, headers: { ...HEADERS, ...extra } });

/** The POST handler. `reckonRoute(deps)` is what pages/ledger/reckon.json.ts exports. */
export function reckonRoute(deps: ReckonDeps) {
  return async ({ request }: { request: Request }): Promise<Response> => {
    try {
      const type = (request.headers.get("content-type") ?? "").split(";")[0].trim().toLowerCase();
      if (type !== "application/json") throw new Refusal(415, "the body is JSON, sent as application/json");
      const text = await readCapped(request).catch((e) => {
        if (e instanceof Refusal) throw e;
        throw new Refusal(400, "the body is not UTF-8 JSON");
      });
      let body: unknown;
      try { body = JSON.parse(text); } catch { throw new Refusal(400, "the body is not JSON"); }
      const asked = checkBody(body);

      const [data, words] = await Promise.all([deps.pack(), deps.words()]);
      if (!data) return answer(503, { detail: NOT_LOADED }, { "retry-after": "60" });
      const game = { version: data.game?.version ?? "", build: data.game?.build ?? "" };

      if (asked.kind === "batch") {
        const results = asked.plans.map(({ id, plan }) => ({ id, ...(reckonResult(data, plan, asked.ctx, words) ?? { state: null, unreadable: true }) }));
        return answer(200, { game, results });
      }
      const result = reckonResult(data, asked.plan, asked.ctx, words, asked.previous);
      if (!result) throw new Refusal(422, "the plan could not be reckoned: its fields are not the engine's");
      return answer(200, { game, ...result });
    } catch (e) {
      if (e instanceof Refusal) return answer(e.status, { detail: e.message });
      return answer(500, { detail: "the reckoning failed" });
    }
  };
}

/** Any other method. */
export const notAllowed = () => answer(405, { detail: "POST a plan here" }, { allow: "POST" });
