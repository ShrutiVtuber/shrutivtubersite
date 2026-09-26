/* The Ledger's reckoning: what the game will do with a plan.
 *
 * Pure and deterministic. No DOM, no fetch, no Astro: it runs in the planner,
 * in the overlay, and under `node --test` from the same file. Contract 2 of
 * docs/LEDGER.md is its shape; the arithmetic is the research's, cited by
 * section at each step:
 *
 *   01  bigambitions/research/01-businesses-and-products.md
 *   03  bigambitions/research/03-real-estate-investments.md
 *   04  bigambitions/research/04-employees-operations-demand.md
 *
 * The design prototype's own reckoning (tread thresholds ×1.18/×1.35, a flat
 * $588 wage floor, 5 customers a shelf) was a stand-in and none of it is here.
 *
 * Every money figure is a Figure: its value, how far to trust it, and the
 * lines that add up to it (+ additions, − subtractions, × multipliers), which
 * the breakdown popover renders. "approximate" means it rests on something the
 * person assumed (satisfaction, demand) or the research could not pin down;
 * "not-counted" marks a cost the game charges that the Ledger cannot price.
 *
 * Words: the engine returns the design's sentences as {key, template, params}
 * so the page can pass the template through say() and fill it with fill().
 * Breakdown labels are English fallbacks keyed the same way.
 */
import type {
  BreakdownLine, Building, BusinessType, Campaign, CampaignAnswer, CampaignMix, ClassId, Ctx,
  Difficulty, Figure, Fix, Fixture, HeldBy, Honesty, LedgerData, Limit, LineOp, LineUnit,
  Missing, Neighbourhood, Plan, Product, ProductLine, RankFilters, RankRow, ReckonState,
  Reckoning, RentOrBuy, Say, StaffRole, Stair, StairEvents, StairOptions, Tread, Week,
} from "./types.ts";

// ── Constants the pack does not carry ────────────────────────────────────

/** The cheapest wholesalers (Hudson, NY Distro, Titans) sell at index 90 (01 §8,
 *  02). Goods are reckoned there: a plan buys where it is cheapest. */
export const WHOLESALE_INDEX = 0.9;
/** Default assumptions (handoff README: satisfaction 80, demand 80). */
export const DEFAULT_SATISFACTION = 80;
export const DEFAULT_DEMAND = 80;
/** Shortage raises the market price +25 %, backorder +50 % (01 §1.3, BiggerAmbitions; unverified). */
const SHORTAGE_PRICE = 1.25;
const BACKORDER_PRICE = 1.5;
/** Hype: +20 product demand for 14 days (04 §6). */
const HYPE_DEMAND = 20;

const DAYS = 7;
const HOURS = 24;
const CLASSES: ClassId[] = ["working", "middle", "upper"];
const EPS = 1e-9;

// ── Small helpers ────────────────────────────────────────────────────────

const alts = (req: string | null | undefined): string[] => (req ? req.split("|").filter(Boolean) : []);
/** Prices are set in cents; the game shows the edge rounded to the cent (01 §3.3 lists 45.57 for 32 × 1.424). */
export const cents = (x: number): number => Math.round(x * 100 + EPS) / 100;
const sum = (xs: number[]): number => xs.reduce((a, b) => a + b, 0);

const WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"];
const ORDINALS = ["zeroth", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth"];
const word = (n: number): string => WORDS[n] ?? String(n);
const ordinal = (n: number): string => ORDINALS[n] ?? `${n}th`;

/** $1,370 · −$1,820. Rounded to the dollar, as every headline figure is. */
export function money(n: number | null): string {
  if (n == null || !Number.isFinite(n)) return "—";
  const r = Math.round(n);
  return (r < 0 ? "−" : "") + "$" + Math.abs(r).toLocaleString("en-US");
}
const count = (n: number): string => Math.round(n).toLocaleString("en-US");

/** Fill a say() template: "Held at {cap}" + {cap: "20"}. Unknown names stay as written. */
export function fill(template: string, params: Record<string, string>): string {
  return template.replace(/\{(\w+)\}/g, (m, k: string) => (k in params ? params[k] : m));
}
const say = (key: string, template: string, params: Record<string, string> = {}): Say =>
  ({ key, template, params });

function line(key: string, label: string, op: LineOp, value: number | null, unit: LineUnit = "money",
  honesty: Honesty = "counted"): BreakdownLine {
  return { key, label, op, value, unit, honesty: value == null ? "not-counted" : honesty };
}
function figure(value: number | null, lines: BreakdownLine[], honesty?: Honesty): Figure {
  const h: Honesty = honesty
    ?? (value == null ? "not-counted" : lines.some((l) => l.honesty === "approximate") ? "approximate" : "counted");
  return { value, honesty: h, lines };
}
const none = (): Figure => ({ value: null, honesty: "not-counted", lines: [] });

// ── The pack, indexed once per pack ──────────────────────────────────────

interface Index {
  data: LedgerData;
  types: Map<string, BusinessType>;
  buildings: Map<string, Building>;
  products: Map<string, Product>;
  fixtures: Map<string, Fixture>;
  hoods: Map<string, Neighbourhood>;
  roles: Map<string, StaffRole>;
  courses: Map<string, { id: string; name: string }>;
  campaigns: Campaign[];
}
const INDEX = new WeakMap<LedgerData, Index>();
function index(data: LedgerData): Index {
  let ix = INDEX.get(data);
  if (!ix) {
    const by = <T extends { id: string }>(xs: T[] | undefined) => new Map((xs ?? []).map((x) => [x.id, x]));
    ix = {
      data,
      types: by(data.businessTypes), buildings: by(data.buildings), products: by(data.products),
      fixtures: by(data.fixtures), hoods: by(data.neighbourhoods), roles: by(data.staffRoles),
      courses: by(data.courses), campaigns: data.campaigns ?? [],
    };
    INDEX.set(data, ix);
  }
  return ix;
}

function difficultyOf(data: LedgerData, ctx: Ctx): Difficulty {
  const ds = data.difficulties ?? [];
  const base = ds.find((d) => d.id === ctx.difficulty) ?? ds.find((d) => d.id === "normal") ?? ds[0];
  return { ...base, ...(ctx.custom ?? {}) } as Difficulty;
}

// ── Promotion: traffic index + campaigns (04 §5, 03 §2.4) ────────────────

/**
 *   efficiency% = round(min(Σreach × buildingMult / m², 1) × 100)   buildingMult 2 for cinema/theatre
 *   gain        = round(efficiency% × neighbourhood marketingStrength)
 *   promotion   = min(100, trafficIndex + gain)
 * The difficulty promotion bonus a fan calculator adds (Normal +5) is unverified
 * and left out, as the pack leaves it out.
 */
function marketingGain(data: LedgerData, building: Building, hood: Neighbourhood | undefined, reach: number): number {
  const mult = data.rules.marketingReachMultiplier?.[building.use] ?? 1;
  const efficiency = Math.round(Math.min((reach * mult) / building.sqm, 1) * 100);
  return Math.round(efficiency * (hood?.marketingStrength ?? 1));
}
function promotionOf(data: LedgerData, building: Building, hood: Neighbourhood | undefined, reach: number) {
  const marketing = reach > 0 ? marketingGain(data, building, hood, reach) : 0;
  const promotion = Math.min(data.rules.promotion.max ?? 100, building.traffic + marketing);
  return { traffic: building.traffic, marketing, promotion };
}

// ── Price acceptance: the staircase (01 §1.3) ────────────────────────────

/**
 *   reference   = min(market price, lowest price in the neighbourhood)
 *   ceiling(c)  = reference × (max(classCeiling_c, priceIndex) + 0.30 with a monopoly)
 * A customer whose ceiling is below the shelf price refuses outright. The share
 * buying at a price is the class mix of those whose ceiling reaches it.
 */
interface PriceModel {
  reference: number;
  edges: Record<ClassId, number>;
  allBuy: number;
  steps: Tread[];
}
function priceModel(data: LedgerData, product: Product, hood: Neighbourhood,
  o: { competitor?: number; monopoly?: boolean; shortage?: boolean; backorder?: boolean } = {}): PriceModel {
  let market = product.marketPrice;
  if (o.backorder) market *= BACKORDER_PRICE;
  else if (o.shortage) market *= SHORTAGE_PRICE;
  const reference = o.competitor != null && o.competitor > 0 ? Math.min(market, o.competitor) : market;
  const bonus = o.monopoly ? data.rules.monopolyBonus : 0;
  const edges = {} as Record<ClassId, number>;
  for (const c of CLASSES) {
    edges[c] = cents(reference * (Math.max(data.rules.classCeilings[c], hood.priceIndex) + bonus));
  }
  const present = CLASSES.filter((c) => (hood.mix[c] ?? 0) > 0);
  const thresholds = [...new Set(present.map((c) => edges[c]))].sort((a, b) => a - b);
  const steps: Tread[] = [];
  let from = 0;
  thresholds.forEach((t, i) => {
    const buyers = present.filter((c) => edges[c] >= t - EPS);
    const share = Math.round(sum(buyers.map((c) => hood.mix[c])) * 1e6) / 1e6; // 0.06 + 0.82 + 0.12 is 1
    steps.push({ step: i, share, from, to: t, buyers });
    from = t;
  });
  return { reference, edges, allBuy: thresholds[0] ?? cents(reference * hood.priceIndex), steps };
}
function treadAt(pm: PriceModel, price: number): Tread | null {
  for (const s of pm.steps) if (price <= s.to + EPS) return s;
  return null; // above every edge: nobody buys
}

// ── Plan reading ─────────────────────────────────────────────────────────

function stocked(ix: Index, type: BusinessType, plan: Plan): string[] {
  const listed = plan.products ?? type.products.filter((p) => p.impact >= 1).map((p) => p.product);
  return listed.filter((id) => ix.products.has(id));
}
const fixtureCount = (plan: Plan, id: string): number => Math.max(0, Math.floor(plan.fixtures?.[id] ?? 0));
const hourAt = (plan: Plan, d: number, h: number): number => Math.max(0, Math.floor(plan.hours?.[d]?.[h] ?? 0));

/** The requirement group whose fixtures are staffed stations: registers, or a
 *  trainer's board, a DJ booth, a computer. The painted hours count these. */
function stationGroup(ix: Index, type: BusinessType): string[] | null {
  const groups = type.requires.map(alts);
  const pos = groups.find((g) => g.some((id) => ix.fixtures.get(id)?.kind === "pos"));
  if (pos) return pos;
  const stations = new Set(type.staff.filter((r) => r !== "security-guard")
    .flatMap((r) => alts(ix.roles.get(r)?.station)));
  return groups.find((g) => g.some((id) => stations.has(id))) ?? null;
}
function stationRole(ix: Index, type: BusinessType, group: string[] | null): StaffRole | null {
  if (!group) return null;
  for (const r of type.staff) {
    const role = ix.roles.get(r);
    if (role && alts(role.station).some((s) => group.includes(s))) return role;
  }
  return null;
}

/** What a plan lacks before the game lets it open. */
function missingOf(ix: Index, type: BusinessType, plan: Plan, ctx: Ctx, stock: string[]): Missing[] {
  const out: Missing[] = [];
  if (type.course && !(ctx.courses ?? []).includes(type.course)) {
    out.push({ path: "type", requirement: type.course, names: [ix.courses.get(type.course)?.name ?? type.course] });
  }
  for (const req of type.requires) {
    const ids = alts(req);
    if (!ids.some((id) => fixtureCount(plan, id) > 0)) {
      out.push({ path: "fixtures", requirement: req, names: ids.map((id) => ix.fixtures.get(id)?.name ?? id) });
    }
  }
  // A fixture that stands on another (a register on its cabinet): one each.
  const needs = new Map<string, { n: number; by: string }>();
  for (const [id, n] of Object.entries(plan.fixtures ?? {})) {
    const f = ix.fixtures.get(id);
    if (!f?.needs || !(n > 0)) continue;
    const cur = needs.get(f.needs);
    needs.set(f.needs, { n: (cur?.n ?? 0) + Math.floor(n), by: cur?.by ?? id });
  }
  for (const [req, { n, by }] of needs) {
    const have = sum(alts(req).map((id) => fixtureCount(plan, id)));
    if (have < n) {
      out.push({ path: "fixtures", requirement: req, names: alts(req).map((id) => ix.fixtures.get(id)?.name ?? id), neededBy: by });
    }
  }
  const conditions = type.conditions ?? [];
  if (conditions.includes("any-primary-product")) {
    const primaries = new Set(type.products.filter((p) => p.impact >= 1).map((p) => p.product));
    if (!stock.some((p) => primaries.has(p))) {
      out.push({ path: "products", requirement: "any-primary-product", names: [...primaries].map((id) => ix.products.get(id)?.name ?? id) });
    }
  }
  if (conditions.includes("hair-care-product-in-stock") && !stock.includes("hair-care-product")) {
    out.push({ path: "products", requirement: "hair-care-product-in-stock", names: [ix.products.get("hair-care-product")?.name ?? "Hair care product"] });
  }
  return out;
}

// ── Displays: capacity counts per product, not pooled (01 §1.1) ──────────

type DisplayKind = "none" | "shared" | "allocated";
interface DisplayCaps { kind: Map<string, DisplayKind>; cap: Map<string, number>; alloc: Map<string, Record<string, number>> }

function displayCaps(ix: Index, plan: Plan, stock: string[], fees: Set<string>): DisplayCaps {
  const kind = new Map<string, DisplayKind>();
  const cap = new Map<string, number>();
  const alloc = new Map<string, Record<string, number>>();
  const goods: string[] = [];
  for (const id of stock) {
    const p = ix.products.get(id)!;
    const shelves = p.displays.filter((d) => d.units != null && d.units > 0);
    if (shelves.length) { kind.set(id, "allocated"); cap.set(id, 0); alloc.set(id, {}); goods.push(id); continue; }
    const stations = p.displays.filter((d) => d.units == null);
    if (stations.length && !fees.has(id)) {
      // A service sold at its station (hair chairs, a coat check, a ticket kiosk):
      // the stations serve every service they list together.
      kind.set(id, "shared");
      let c = 0;
      const used: Record<string, number> = {};
      for (const s of stations) {
        const n = fixtureCount(plan, s.fixture);
        if (!n) continue;
        used[s.fixture] = n;
        c += n * (ix.fixtures.get(s.fixture)?.customersPerHour ?? Infinity);
      }
      cap.set(id, c);
      alloc.set(id, used);
      continue;
    }
    kind.set(id, "none"); // charged at the door or at a desk: no display
    alloc.set(id, {});
  }
  if (plan.displays) {
    for (const id of goods) {
      let c = 0;
      const mine = plan.displays[id] ?? {};
      for (const [f, n] of Object.entries(mine)) {
        const holds = ix.products.get(id)!.displays.some((d) => d.fixture === f && (d.units ?? 0) > 0);
        if (!holds || !(n > 0)) continue;
        c += Math.floor(n) * (ix.fixtures.get(f)?.customersPerHour ?? 0);
        alloc.get(id)![f] = Math.floor(n);
      }
      cap.set(id, c);
    }
    return { kind, cap, alloc };
  }
  // Share the plan's display fixtures out: always to the product with the
  // least display so far, from the fixture serving most customers an hour
  // (ties: the one fewest stocked products can use, then by id).
  const holders = new Map<string, string[]>();
  for (const id of goods) {
    for (const d of ix.products.get(id)!.displays) {
      if ((d.units ?? 0) <= 0) continue;
      if (!holders.has(d.fixture)) holders.set(d.fixture, []);
      holders.get(d.fixture)!.push(id);
    }
  }
  const left = new Map<string, number>();
  for (const f of [...holders.keys()].sort()) {
    const n = fixtureCount(plan, f);
    if (n > 0 && (ix.fixtures.get(f)?.customersPerHour ?? 0) > 0) left.set(f, n);
  }
  for (;;) {
    let pick: string | null = null;
    for (const id of goods) {
      const can = [...left.keys()].some((f) => left.get(f)! > 0 && holders.get(f)!.includes(id));
      if (can && (pick == null || cap.get(id)! < cap.get(pick)! - EPS)) pick = id;
    }
    if (pick == null) break;
    let best: string | null = null;
    for (const f of left.keys()) {
      if (left.get(f)! <= 0 || !holders.get(f)!.includes(pick)) continue;
      if (best == null) { best = f; continue; }
      const a = ix.fixtures.get(f)!.customersPerHour!, b = ix.fixtures.get(best)!.customersPerHour!;
      if (a > b || (a === b && holders.get(f)!.length < holders.get(best)!.length)) best = f;
    }
    left.set(best!, left.get(best!)! - 1);
    cap.set(pick, cap.get(pick)! + ix.fixtures.get(best!)!.customersPerHour!);
    const a = alloc.get(pick)!;
    a[best!] = (a[best!] ?? 0) + 1;
  }
  return { kind, cap, alloc };
}

// ── The core: one week, hour by hour (01 §1.1–1.2, 04 §4) ────────────────

interface ProductCore {
  id: string;
  price: number;
  typed: boolean;
  pm: PriceModel;
  tread: Tread | null;
  perCustomer: number;       // units a buying customer takes, before price refusal
  factors: { salesRatio: number; demand: number; satisfaction: number; impact: number; maxAmount: number } | null;
  buyers: number;            // customers a week who reached it (after displays, fee days)
  units: number;
  unitCost: number;
  imported: boolean;
  displayCap: number | null;
  displays: Record<string, number>;
}

interface Core {
  state: ReckonState;
  type: BusinessType | null;
  building: Building | null;
  hood: Neighbourhood | null;
  diff: Difficulty;
  would: number[][];
  served: number[][];
  heldBy: HeldBy[][];
  heldHours: { registers: number; displays: number; fixtures: number; building: number };
  heldPeak: { registers: number; displays: number; fixtures: number; building: number };
  heldCap: { registers: number; displays: number; fixtures: number; building: number };
  displayProduct: Map<string, number>;
  storeFixture: Map<string, number>;
  customers: number;
  wouldWeek: number;
  openHours: number;
  stationHours: number;
  stationCount: number;
  station: string[] | null;
  role: StaffRole | null;
  promo: { traffic: number; marketing: number; promotion: number; multiplier: number } | null;
  satisfaction: number;
  products: ProductCore[];
  moneyIn: number;
  goods: number;
  wages: number;
  wageLines: BreakdownLine[];
  rent: number;
  ads: number;
  deliveries: number;
  contracts: number;
  week: number;
  missing: Missing[];
  stock: string[];
}

const grid = <T>(v: T): T[][] => Array.from({ length: DAYS }, () => Array<T>(HOURS).fill(v));

function simulate(ix: Index, plan: Plan, ctx: Ctx): Core {
  const data = ix.data;
  const diff = difficultyOf(data, ctx);
  const type = plan.typeId ? ix.types.get(plan.typeId) ?? null : null;
  const building = plan.buildingId ? ix.buildings.get(plan.buildingId) ?? null : null;
  const hood = building ? ix.hoods.get(building.neighbourhood) ?? null : null;
  const satisfaction = clamp(plan.satisfaction ?? DEFAULT_SATISFACTION, 0, 100);
  const core: Core = {
    state: "ok", type, building, hood, diff,
    would: grid(0), served: grid(0), heldBy: grid<HeldBy>(null),
    heldHours: { registers: 0, displays: 0, fixtures: 0, building: 0 },
    heldPeak: { registers: 0, displays: 0, fixtures: 0, building: 0 },
    heldCap: { registers: 0, displays: 0, fixtures: 0, building: 0 },
    displayProduct: new Map(), storeFixture: new Map(),
    customers: 0, wouldWeek: 0, openHours: 0, stationHours: 0, stationCount: 0, station: null, role: null,
    promo: null, satisfaction, products: [], moneyIn: 0, goods: 0, wages: 0, wageLines: [],
    rent: 0, ads: 0, deliveries: 0, contracts: 0, week: 0, missing: [], stock: [],
  };
  if (!type) { core.state = "no-type"; return core; }
  if (!building) { core.state = "no-building"; return core; }
  if (!type.uses.includes(building.use)) { core.state = "not-a-shop"; return core; }
  if (!type.hourMult || !type.dayMult || building.capacity == null || !hood) { core.state = "no-customers"; return core; }

  const stock = stocked(ix, type, plan);
  core.stock = stock;
  core.missing = missingOf(ix, type, plan, ctx, stock);

  // Would come: ceil(min(CC × promotionMultiplier × day × hour, CC)) (01 §1.1).
  const reach = sum(ix.campaigns.filter((c) => plan.campaigns?.[c.id]).map((c) => c.reach));
  const p = promotionOf(data, building, hood, reach);
  const multiplier = diff.baseCustomerPromotionMultiplier + data.rules.promotion.gainPerMultiplier * (p.promotion / 100);
  core.promo = { ...p, multiplier };
  const CC = building.capacity;
  const atCapacity = grid(false);
  for (let d = 0; d < DAYS; d++) {
    for (let h = 0; h < HOURS; h++) {
      const raw = CC * multiplier * (type.dayMult[d] ?? 0) * (type.hourMult[h] ?? 0);
      // The epsilon keeps a product that is whole in exact arithmetic from
      // rounding up a customer on floating-point dust.
      core.would[d][h] = Math.ceil(Math.min(raw, CC) - EPS);
      atCapacity[d][h] = raw >= CC - EPS;
    }
  }

  // Ceilings (04 §4): the building, the staffed stations, store-wide required
  // fixtures (baskets, a changing room, gym equipment), and each product's displays.
  const station = stationGroup(ix, type);
  core.station = station;
  core.role = stationRole(ix, type, station);
  const stationCaps = (station ?? []).flatMap((id) =>
    Array<number>(fixtureCount(plan, id)).fill(ix.fixtures.get(id)?.customersPerHour ?? Infinity))
    .sort((a, b) => b - a);
  core.stationCount = stationCaps.length;
  const stationCap = (n: number) => sum(stationCaps.slice(0, Math.min(n, stationCaps.length)));
  const storeCaps: { id: string; cap: number }[] = [];
  for (const req of type.requires) {
    const ids = alts(req);
    if (station && ids.every((id) => station.includes(id))) continue;
    const fx = ids.map((id) => ix.fixtures.get(id)).filter((f): f is Fixture => !!f);
    if (!fx.length || fx.some((f) => f.displays.length) || fx.every((f) => f.customersPerHour == null)) continue;
    const c = sum(fx.map((f) => fixtureCount(plan, f.id) * (f.customersPerHour ?? 0)));
    const present = fx.find((f) => fixtureCount(plan, f.id) > 0) ?? fx[0];
    storeCaps.push({ id: present.id, cap: c });
  }
  const storeMin = storeCaps.reduce<{ id: string; cap: number } | null>((m, s) => (m == null || s.cap < m.cap ? s : m), null);

  const fees = new Set<string>((type.entranceFee ?? []).map((e) => e.product));
  if (type.perCustomerProduct) fees.add(type.perCustomerProduct);
  const dc = displayCaps(ix, plan, stock, fees);
  const feeDays = new Map<string, Set<number>>();
  for (const e of type.entranceFee ?? []) feeDays.set(e.product, new Set(e.days));

  const cannotOpen = core.missing.length > 0;
  const buyers = new Map<string, number>(stock.map((id) => [id, 0]));
  for (let d = 0; d < DAYS; d++) {
    for (let h = 0; h < HOURS; h++) {
      const n = hourAt(plan, d, h);
      if (n <= 0 || cannotOpen) continue;
      core.openHours++;
      const staffed = Math.min(n, stationCaps.length);
      core.stationHours += staffed;
      const would = core.would[d][h];
      core.wouldWeek += would;
      const sCap = station ? stationCap(staffed) : Infinity;
      const fCap = storeMin ? storeMin.cap : Infinity;
      const served = Math.min(would, sCap, fCap);
      core.served[d][h] = served;
      core.customers += served;
      let dMin = Infinity, dProduct: string | null = null;
      for (const id of stock) {
        if (fees.has(id) && feeDays.has(id) && !feeDays.get(id)!.has(d)) continue;
        const c = dc.kind.get(id) === "none" ? Infinity : dc.cap.get(id)!;
        buyers.set(id, buyers.get(id)! + Math.min(served, c));
        if (c < dMin) { dMin = c; dProduct = id; }
      }
      let by: HeldBy = null;
      if (would > Math.min(sCap, fCap)) by = sCap <= fCap ? "registers" : "fixtures";
      else if (dMin < served) by = "displays";
      else if (atCapacity[d][h]) by = "building";
      core.heldBy[d][h] = by;
      if (by) {
        core.heldHours[by]++;
        const cap = by === "registers" ? sCap : by === "fixtures" ? fCap : by === "displays" ? dMin : CC;
        const peak = by === "displays" ? served : would;
        if (peak > core.heldPeak[by]) { core.heldPeak[by] = peak; core.heldCap[by] = cap; }
        if (by === "displays" && dProduct) core.displayProduct.set(dProduct, (core.displayProduct.get(dProduct) ?? 0) + 1);
        if (by === "fixtures" && storeMin) core.storeFixture.set(storeMin.id, (core.storeFixture.get(storeMin.id) ?? 0) + 1);
      }
    }
  }
  if (cannotOpen) { core.state = "cannot-open"; }

  // Units (01 §1.2):
  //   units = customers × salesRatio × demand/100 × satisfactionMult × impact × maxAmountFactor
  //   satisfactionMult = 0.5 + satisfaction/100;  maxAmountFactor: max ≤ 1 ? max : primary ? (1+max)/2 : 1
  // then × the share of the class mix whose ceiling reaches the price (01 §1.3).
  // Entrance fees and tickets are one per customer.
  const sat = data.rules.satisfaction;
  const satMult = sat.at0 + (sat.at100 - sat.at0) * (satisfaction / 100);
  const maxAmt = data.rules.maxAmountPerProduct?.[type.id] ?? type.maxAmountPerProduct ?? 1;
  const importIndex = ctx.importIndex ?? WHOLESALE_INDEX;
  for (const id of stock) {
    const prod = ix.products.get(id)!;
    const typed = plan.prices?.[id] != null && Number.isFinite(plan.prices[id]);
    const pm = priceModel(data, prod, hood, { competitor: plan.competitorPrice?.[id] });
    const price = typed ? Math.max(0, plan.prices[id]) : pm.allBuy;
    const tread = treadAt(pm, price);
    const listed = type.products.find((x) => x.product === id);
    const impact = listed?.impact ?? data.rules.unlistedProductImpact ?? 0.025;
    const primary = impact >= 1;
    let perCustomer: number;
    let factors: ProductCore["factors"] = null;
    if (fees.has(id)) perCustomer = 1;
    else {
      const demand = clamp(plan.demand?.[id] ?? DEFAULT_DEMAND, 0, 100);
      const salesRatio = prod.salesRatio > 0 ? prod.salesRatio : 1;
      const maxAmount = maxAmt <= 1 ? maxAmt : primary ? (1 + maxAmt) / 2 : 1;
      factors = { salesRatio, demand: demand / 100, satisfaction: satMult, impact, maxAmount };
      perCustomer = salesRatio * (demand / 100) * satMult * impact * maxAmount;
    }
    const b = buyers.get(id) ?? 0;
    const units = b * perCustomer * (tread?.share ?? 0);
    const wholesale = prod.sources.includes("wholesaler");
    const imported = !wholesale && prod.sources.includes("importer");
    const unitCost = prod.kind === "service" || !prod.wholesale ? 0 : prod.wholesale * (imported ? importIndex : WHOLESALE_INDEX);
    const kind = dc.kind.get(id);
    core.products.push({
      id, price, typed, pm, tread, perCustomer, factors, buyers: b, units, unitCost, imported,
      displayCap: kind === "none" ? null : dc.cap.get(id) ?? 0, displays: dc.alloc.get(id) ?? {},
    });
  }
  core.moneyIn = sum(core.products.map((x) => x.units * x.price));
  core.goods = sum(core.products.map((x) => x.units * x.unitCost));

  // Wages (04 §1, 01 §6). A role's hourly wage is the plan's own figure when it
  // gives one, else the role's base wage × the difficulty's salary multiplier
  // (Normal 0.7). That default is the floor a skill-0 hire asks; the asking wage
  // by skill is not published (04 §8), so a defaulted wage is approximate. The
  // role that staffs the stations works every staffed station-hour painted.
  const wageOf = (role: StaffRole) => {
    const typedWage = plan.staff?.[role.id]?.wage;
    return typedWage != null && Number.isFinite(typedWage)
      ? { wage: typedWage, honesty: "counted" as Honesty }
      : { wage: role.baseWage * diff.salaryMultiplier, honesty: "approximate" as Honesty };
  };
  const roleIds = new Set<string>([...type.staff, ...Object.keys(plan.staff ?? {})]);
  for (const rid of [...type.staff, ...[...roleIds].filter((r) => !type.staff.includes(r)).sort()]) {
    const role = ix.roles.get(rid);
    if (!role) continue;
    const { wage, honesty } = wageOf(role);
    const hours = role === core.role ? core.stationHours : Math.max(0, plan.staff?.[rid]?.hours ?? 0);
    if (hours > 0) {
      core.wages += hours * wage;
      core.wageLines.push(line(`wages.${rid}`, `${role.name} · ${count(hours)} h × $${wage.toFixed(2)}`, "+", hours * wage, "money", honesty));
    } else if (type.staff.includes(rid) && role !== core.role) {
      core.wageLines.push(line(`wages.${rid}.unplanned`, `${role.name}: no hours planned`, "+", null));
    }
  }

  core.rent = (building.rentDay ?? 0) * 7;
  core.ads = sum(ix.campaigns.filter((c) => plan.campaigns?.[c.id]).map((c) => c.costDay * 7)); // billed daily, open or not (04 §5)
  // One wholesale delivery contract a week per wholesaler, $400 each (01 §8);
  // a product past one contract's weekly limit needs a second wholesaler.
  const bought = core.products.filter((x) => x.units > 0 && x.unitCost > 0 && !x.imported);
  core.contracts = bought.length
    ? Math.max(1, ...bought.map((x) => {
      const lim = ix.products.get(x.id)!.weeklyLimit;
      return lim ? Math.ceil(x.units / lim - EPS) : 1;
    }))
    : 0;
  core.deliveries = core.contracts * data.rules.wholesaleDeliveryFee;
  const licensing = (type.conditions ?? []).includes("licensing-fees") && type.licensingFeeDay != null ? type.licensingFeeDay * 7 : 0;
  core.week = core.moneyIn - core.goods - core.wages - core.rent - core.ads - core.deliveries - licensing;
  if (core.state === "ok" && core.openHours === 0) core.state = "closed";
  return core;
}

function clamp(x: number, lo: number, hi: number): number {
  return Number.isFinite(x) ? Math.min(hi, Math.max(lo, x)) : lo;
}

// ── Figures from the core ────────────────────────────────────────────────

function productFigures(ix: Index, core: Core): ProductLine[] {
  return core.products.map((x) => {
    const prod = ix.products.get(x.id)!;
    const f = x.factors;
    const share = x.tread?.share ?? 0;
    const unitsLines: BreakdownLine[] = [
      line(`products.${x.id}.buyers`, "Customers who reach it", "+", x.buyers, "count", "counted"),
      ...(f ? [
        line(`products.${x.id}.salesRatio`, "Sales ratio", "×", f.salesRatio, "factor"),
        line(`products.${x.id}.demand`, "Demand", "×", f.demand, "factor", "approximate"),
        line(`products.${x.id}.satisfaction`, "Satisfaction", "×", f.satisfaction, "factor", "approximate"),
        line(`products.${x.id}.impact`, "How strongly it sells here", "×", f.impact, "factor"),
        ...(f.maxAmount !== 1 ? [line(`products.${x.id}.maxAmount`, "Amount a customer takes", "×", f.maxAmount, "factor")] : []),
      ] : [line(`products.${x.id}.perCustomer`, "One for each customer", "×", 1, "factor")]),
      line(`products.${x.id}.share`, "Customers who accept the price", "×", share, "factor"),
      line(`products.${x.id}.units`, "Units a week", "=", x.units, "count", f ? "approximate" : "counted"),
    ];
    const moneyIn = figure(x.units * x.price, [
      ...unitsLines,
      line(`products.${x.id}.price`, `Price $${x.price.toFixed(2)}`, "×", x.price, "price"),
      line(`products.${x.id}.moneyIn`, "Money in", "=", x.units * x.price, "money", f ? "approximate" : "counted"),
    ]);
    const costLabel = x.unitCost === 0
      ? "Nothing to buy in"
      : x.imported
        ? `Imported: $${prod.wholesale.toFixed(2)} × import index`
        : `Wholesale $${prod.wholesale.toFixed(2)} × ${WHOLESALE_INDEX.toFixed(2)}, the cheapest wholesaler`;
    const goods = figure(x.units * x.unitCost, [
      line(`products.${x.id}.units`, "Units a week", "+", x.units, "count", f ? "approximate" : "counted"),
      line(`products.${x.id}.unitCost`, costLabel, "×", x.unitCost, "price", x.imported ? "approximate" : "counted"),
      line(`products.${x.id}.goods`, "Goods", "=", x.units * x.unitCost, "money", "approximate"),
    ]);
    return {
      id: x.id, name: prod.name, price: x.price, typed: x.typed, edge: x.pm.allBuy, tread: x.tread,
      buyers: x.buyers, units: x.units, displayCap: x.displayCap, displays: x.displays, moneyIn, goods,
    };
  });
}

function weekFigures(ix: Index, core: Core, products: ProductLine[], plan: Plan): Week {
  const type = core.type!;
  const moneyIn = figure(core.moneyIn, products.map((p) =>
    line(`week.moneyIn.${p.id}`, `${p.name} · ${count(p.units)} × $${p.price.toFixed(2)}`, "+", p.moneyIn.value, "money",
      p.moneyIn.honesty === "counted" ? "counted" : "approximate")));
  const goodsLines = products.map((p) =>
    line(`week.goods.${p.id}`, `${p.name} · ${count(p.units)} × $${(core.products.find((x) => x.id === p.id)!.unitCost).toFixed(2)}`,
      "+", p.goods.value, "money", "approximate"));
  if (core.products.some((x) => x.imported && x.units > 0)) {
    goodsLines.push(line("week.goods.importIndex", "Imported goods at the import index you gave, else 0.90; each save sets its own (0.5–1.3)", "×", null, "factor"));
  }
  const goods = figure(core.goods, goodsLines, "approximate");
  const wages = figure(core.wages, core.wageLines);
  const b = core.building!;
  const rent = figure(core.rent, [line("week.rent", `$${b.rentDay} a day × 7`, "+", core.rent)]);
  const adLines = ix.campaigns.filter((c) => plan.campaigns?.[c.id])
    .map((c) => line(`week.ads.${c.id}`, `${c.name} · $${c.costDay} a day × 7`, "+", c.costDay * 7));
  const ads = figure(core.ads, adLines);
  const delLines = [line("week.deliveries", `${core.contracts} wholesale contract${core.contracts === 1 ? "" : "s"} × $${ix.data.rules.wholesaleDeliveryFee}`, "+", core.deliveries)];
  if (core.products.some((x) => x.imported && x.units > 0)) {
    delLines.push(line("week.deliveries.imports", "Imports: the warehouse, its drivers and the importer's fees", "+", null));
  }
  const deliveries = figure(core.deliveries, delLines);
  const licensingCond = (type.conditions ?? []).includes("licensing-fees");
  const totalLines: BreakdownLine[] = [
    line("week.moneyIn", "Money in", "+", core.moneyIn, "money", "approximate"),
    line("week.goods", "Goods", "−", core.goods, "money", "approximate"),
    line("week.wages", "Wages", "−", core.wages, "money", wages.honesty === "counted" ? "counted" : "approximate"),
    line("week.rent", "Rent", "−", core.rent),
    line("week.ads", "Advertising", "−", core.ads),
    line("week.deliveries", "Deliveries", "−", core.deliveries),
  ];
  if (licensingCond) {
    totalLines.push(type.licensingFeeDay != null
      ? line("week.licensing", `Licensing · $${type.licensingFeeDay} a day × 7`, "−", type.licensingFeeDay * 7)
      : line("week.licensing", "Licensing fees: no 1.0 figure is known", "−", null));
  }
  if (type.theft) totalLines.push(line("week.theft", "Theft: no formula is known", "−", null));
  totalLines.push(line("week.tax", "Tax, taken at the year's end", "−", null));
  totalLines.push(line("week.total", "The week", "=", core.week, "money", "approximate"));
  const total = figure(core.week, totalLines, "approximate");
  return { moneyIn: { ...moneyIn, honesty: "approximate" }, goods, wages, rent, ads, deliveries, total, loss: core.week < 0 };
}

function setupFigures(ix: Index, plan: Plan, building: Building | null) {
  const fl: BreakdownLine[] = [];
  let total = 0;
  for (const [id, n] of Object.entries(plan.fixtures ?? {})) {
    const f = ix.fixtures.get(id);
    const k = Math.max(0, Math.floor(n));
    if (!f || !k) continue;
    total += k * f.price;
    fl.push(line(`setup.fixtures.${id}`, `${f.name} × ${k} · $${f.price.toLocaleString("en-US")}`, "+", k * f.price,
      "money", f.confidence === "community" ? "approximate" : "counted"));
  }
  const fd = ix.data.rules.furnitureDelivery;
  if (fd) fl.push(line("setup.fixtures.delivery", `Delivery: $${fd.fee} on orders of $${fd.minimumOrder.toLocaleString("en-US")} or more, or carry it yourself`, "+", null));
  const fixtures = figure(total, fl, "counted");
  const deposit = building?.deposit != null
    ? figure(building.deposit, [line("setup.deposit", `Rent deposit · $${building.rentDay} × ${Math.round(building.deposit / (building.rentDay || 1))} days`, "+", building.deposit)])
    : none();
  const t = total + (deposit.value ?? 0);
  const all = figure(building ? t : null, [
    line("setup.fixtures", "Fixtures", "+", total),
    line("setup.deposit", "Rent deposit", "+", deposit.value),
    line("setup.stock", "Stock for the first day", "+", null),
    line("setup.total", "Setup", "=", building ? t : null),
  ], "counted");
  return { fixtures, deposit, total: all };
}

// ── What limits it ───────────────────────────────────────────────────────

const USE_A: Record<string, string> = {
  shop: "a shop unit", office: "an office", warehouse: "a warehouse", home: "a home",
  cinema: "a cinema building", theatre: "a theatre building", special: "a special building",
};
const USE_NOUN: Record<string, string> = {
  shop: "a shop", office: "an office", warehouse: "a warehouse", home: "a home",
  cinema: "a cinema", theatre: "a theatre", special: "open to businesses",
};
const an = (s: string) => (/^[aeiou]/i.test(s) ? "an " : "a ") + s;
/** Short names the sentences use: "register", "cabinet". */
const SHORT: Record<string, string> = { "cash-register": "register", "cabinet-with-drawers": "cabinet" };
const stationWord = (f: Fixture | undefined) =>
  !f ? "station" : SHORT[f.id] ?? f.name.replace(/\s*\(.*\)$/, "").toLowerCase();
const plural = (w: string, n: number) => (n === 1 ? w : w.endsWith("s") ? w : `${w}s`);
const staffNoun = (role: StaffRole | null) =>
  !role ? "someone to staff it" : role.id === "customer-service" ? "a cashier" : an(role.name.toLowerCase());

function unknownLimit(state: ReckonState, heldHours: Limit["heldHours"], s: Say, kind: Limit["state"] = "unknown"): Limit {
  return { state: kind, reason: state, heldHours, say: s };
}

/** The cheapest fixture that is one of `ids`, with whatever it stands on. */
function cheapestOf(ix: Index, ids: string[], plan: Plan) {
  let best: { id: string; adds: Record<string, number>; cost: number; lines: BreakdownLine[] } | null = null;
  for (const id of ids) {
    const f = ix.fixtures.get(id);
    if (!f) continue;
    const adds: Record<string, number> = { [id]: 1 };
    const lines = [line(`fix.${id}`, f.name, "+", f.price)];
    let cost = f.price;
    if (f.needs) {
      const under = alts(f.needs).map((x) => ix.fixtures.get(x)).filter((x): x is Fixture => !!x)
        .sort((a, b) => a.price - b.price || a.id.localeCompare(b.id))[0];
      // Stands on another fixture: count what the plan already has spare.
      const needers = sum(Object.entries(plan.fixtures ?? {}).filter(([k]) => ix.fixtures.get(k)?.needs === f.needs).map(([, n]) => Math.floor(n)));
      const have = sum(alts(f.needs).map((x) => fixtureCount(plan, x)));
      if (under && have < needers + 1) {
        adds[under.id] = 1;
        cost += under.price;
        lines.push(line(`fix.${under.id}`, `${under.name}, which it stands on`, "+", under.price));
      }
    }
    if (!best || cost < best.cost) best = { id, adds, cost, lines };
  }
  return best;
}

function withFixtures(plan: Plan, adds: Record<string, number>, productId?: string): Plan {
  const fixtures = { ...plan.fixtures };
  for (const [k, n] of Object.entries(adds)) fixtures[k] = (fixtures[k] ?? 0) + n;
  let displays = plan.displays;
  if (displays && productId) {
    displays = { ...displays, [productId]: { ...(displays[productId] ?? {}) } };
    for (const [k, n] of Object.entries(adds)) displays[productId][k] = (displays[productId][k] ?? 0) + n;
  }
  return { ...plan, fixtures, ...(displays ? { displays } : {}) };
}

function limitOf(ix: Index, plan: Plan, ctx: Ctx, core: Core): Limit {
  const hh = core.heldHours;
  const type = core.type;
  switch (core.state) {
    case "no-type":
      return unknownLimit(core.state, hh, say("limit.noType", "Nothing to limit yet. Choose a business type and a building, and the Ledger works out what holds it back."));
    case "no-building":
      return unknownLimit(core.state, hh, say("limit.unknown", "Nothing to limit yet. Choose a building and the Ledger works out what holds this business back."));
    case "not-a-shop": {
      const use = type!.uses[0];
      const b = core.building!;
      return unknownLimit(core.state, hh, use === "shop"
        ? say("limit.notAShop", "This building is not a shop. {typeA} needs a shop unit; the finder lists them.", { typeA: capital(an(type!.name.toLowerCase())) })
        : say("limit.notItsUse", "This building is not {useNoun}. {typeA} needs {useA}; the finder lists them.",
          { useNoun: USE_NOUN[use] ?? use, typeA: capital(an(type!.name.toLowerCase())), useA: USE_A[use] ?? use, building: b.address }), "not-a-shop");
    }
    case "no-customers":
      return unknownLimit(core.state, hh, say("limit.noCustomers", "{typeA} serves no customers, so nothing holds its customers back.", { typeA: capital(an(type!.name.toLowerCase())) }));
    case "cannot-open": {
      const first = core.missing[0];
      const need = first.path === "type"
        ? `the ${first.names[0]} course`
        : first.path === "products" ? "a product it sells first-hand" : an(first.names[0].toLowerCase());
      return unknownLimit(core.state, hh, say("limit.cannotOpen", "Nothing to limit until it can open. It needs {need} first.", { need }), "cannot-open");
    }
    case "closed":
      return unknownLimit(core.state, hh, say("limit.closed", "Nothing to limit while it never opens. Paint the hours it opens under Hours and staff."));
    default: break;
  }
  const kinds: (keyof Limit["heldHours"])[] = ["registers", "displays", "fixtures", "building"];
  const by = kinds.reduce<keyof Limit["heldHours"] | null>((m, k) => (hh[k] > 0 && (m == null || hh[k] > hh[m]) ? k : m), null);
  if (!by) return { state: "free", heldHours: hh, say: say("limit.free", "Nothing binds. Every customer who would come is served, every open hour.") };

  const cap = core.heldCap[by];
  const hours = hh[by];
  const would = by === "building" ? null : core.heldPeak[by];
  const base: Limit = { state: "held", by, cap, hours, would, heldHours: hh, say: say("", "") };
  const week = core.week;
  const worthOf = (fixed: Plan) => simulate(ix, fixed, ctx);

  if (by === "building") {
    base.fix = {
      kind: "building", adds: {}, cost: none(), weeklyCost: none(),
      worth: figure(null, [line("fix.worth", "How many more would come is not known: the game stops counting at the building's capacity", "+", null)]),
      plan: null,
    };
    base.say = say("limit.held.building",
      "Held at {cap} customers an hour by the building, for {hours} hours of the week. How many more would come is not known: the game stops counting at the building's capacity. A building with a larger capacity is the change that lifts it.",
      { cap: count(cap), hours: count(hours) });
    return base;
  }

  if (by === "registers") {
    const group = core.station ?? [];
    const owned = core.stationCount;
    base.count = owned;
    const ownedIds = group.filter((id) => fixtureCount(plan, id) > 0);
    const noun = stationWord(ix.fixtures.get(ownedIds[0] ?? group[0]));
    // Painted fewer staff than stations somewhere it binds? Then staffing is the fix.
    let understaffed = false;
    for (let d = 0; d < DAYS; d++) for (let h = 0; h < HOURS; h++) {
      if (core.heldBy[d][h] === "registers" && hourAt(plan, d, h) < owned) understaffed = true;
    }
    const n = understaffed ? owned : owned + 1;
    const hoursPlus = plan.hours.map((row) => row.map((v) => (v > 0 ? Math.min(Math.floor(v) + 1, n) : 0)));
    let adds: Record<string, number> = {};
    let costLines: BreakdownLine[] = [];
    let cost = 0;
    if (!understaffed) {
      const c = cheapestOf(ix, group, plan)!;
      adds = c.adds; costLines = c.lines; cost = c.cost;
    }
    const fixed: Plan = { ...withFixtures(plan, adds), hours: hoursPlus };
    const after = worthOf(fixed);
    const wageDelta = after.wages - core.wages;
    const role = core.role;
    const newHours = after.stationHours - core.stationHours;
    const wage = newHours > 0 ? wageDelta / newHours : 0;
    const wageHonesty: Honesty = role && plan.staff?.[role.id]?.wage != null ? "counted" : "approximate";
    const fix: Fix = {
      kind: understaffed ? "staff" : "register", adds,
      cost: figure(cost, [...costLines, line("fix.cost", "Cost", "=", cost)], "counted"),
      weeklyCost: figure(wageDelta, [
        line("fix.weekly.hours", `${role?.name ?? "Staff"}: every open hour, one more`, "+", newHours, "hours"),
        line("fix.weekly.wage", `$${wage.toFixed(2)} an hour`, "×", wage, "price", wageHonesty),
        line("fix.weekly", "A week", "=", wageDelta, "money", wageHonesty),
      ]),
      worth: figure(after.week - week, [
        line("fix.worth.after", "The week with it", "+", after.week, "money", "approximate"),
        line("fix.worth.now", "The week now", "−", week, "money", "approximate"),
        line("fix.worth", "Worth a week, its wages paid", "=", after.week - week, "money", "approximate"),
      ], "approximate"),
      plan: fixed,
    };
    base.fix = fix;
    const f = ix.fixtures.get(Object.keys(adds)[0] ?? ownedIds[0] ?? group[0]);
    const under = Object.keys(adds)[1] ? ix.fixtures.get(Object.keys(adds)[1]) : undefined;
    const params = {
      cap: count(cap), count: word(owned), station: plural(noun, owned), hours: count(hours), would: count(would ?? 0),
      ordinal: ordinal(n), stationOne: stationWord(f), cost: money(cost),
      withNeeds: under ? ` with its ${stationWord(under)}` : "", staffA: staffNoun(role),
      weeklyCost: money(wageDelta), worth: money(fix.worth.value),
    };
    base.say = understaffed
      ? say("limit.held.staff", "Held at {cap} customers an hour by {count} staffed {station}, for {hours} hours of the week. {would} would come. Staffing the {ordinal} {stationOne} every open hour ({weeklyCost} a week) is worth {worth} a week.", params)
      : say("limit.held.registers", "Held at {cap} customers an hour by {count} {station}, for {hours} hours of the week. {would} would come. A {ordinal} {stationOne} ({cost}{withNeeds}) and {staffA} ({weeklyCost} a week) are worth {worth} a week.", params);
    return base;
  }

  if (by === "displays") {
    const productId = [...core.displayProduct.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? core.stock[0];
    const prod = ix.products.get(productId)!;
    base.productId = productId;
    const pc = core.products.find((x) => x.id === productId)!;
    const shelves = prod.displays.filter((d) => (d.units ?? 0) > 0).map((d) => d.fixture);
    const stations = prod.displays.filter((d) => d.units == null).map((d) => d.fixture);
    const c = cheapestOf(ix, shelves.length ? shelves : stations, plan);
    const nOwned = sum(Object.values(pc.displays));
    base.count = nOwned;
    if (!c) {
      base.say = say("limit.held.displays.none", "Held for {product} by its displays, for {hours} hours of the week. Nothing in the game's catalogue displays it.", { product: prod.name.toLowerCase(), hours: count(hours) });
      return base;
    }
    base.fixtureId = c.id;
    const fixed = withFixtures(plan, c.adds, productId);
    const after = worthOf(fixed);
    base.fix = {
      kind: "display", adds: c.adds, productId,
      cost: figure(c.cost, [...c.lines, line("fix.cost", "Cost", "=", c.cost)], "counted"),
      weeklyCost: figure(0, [line("fix.weekly", "No wage", "+", 0)]),
      worth: figure(after.week - week, [
        line("fix.worth.after", "The week with it", "+", after.week, "money", "approximate"),
        line("fix.worth.now", "The week now", "−", week, "money", "approximate"),
        line("fix.worth", "Worth a week", "=", after.week - week, "money", "approximate"),
      ], "approximate"),
      plan: fixed,
    };
    base.say = say("limit.held.displays",
      "Held at {cap} customers an hour for {product} by its displays, for {hours} hours of the week. {would} would come. {fixtureA} ({cost}) is worth {worth} a week.",
      { cap: count(cap), product: prod.name.toLowerCase(), hours: count(hours), would: count(would ?? 0),
        fixtureA: capital(an(ix.fixtures.get(c.id)!.name.toLowerCase())), cost: money(c.cost), worth: money(after.week - week) });
    return base;
  }

  // by === "fixtures": a store-wide fixture (shopping baskets, a changing room).
  const fid = [...core.storeFixture.entries()].sort((a, b) => b[1] - a[1])[0]?.[0];
  const group = type!.requires.map(alts).find((g) => fid != null && g.includes(fid)) ?? [];
  base.fixtureId = fid;
  const c = cheapestOf(ix, group, plan);
  if (c) {
    const fixed = withFixtures(plan, c.adds);
    const after = worthOf(fixed);
    base.fix = {
      kind: "fixture", adds: c.adds,
      cost: figure(c.cost, [...c.lines, line("fix.cost", "Cost", "=", c.cost)], "counted"),
      weeklyCost: figure(0, [line("fix.weekly", "No wage", "+", 0)]),
      worth: figure(after.week - week, [
        line("fix.worth.after", "The week with it", "+", after.week, "money", "approximate"),
        line("fix.worth.now", "The week now", "−", week, "money", "approximate"),
        line("fix.worth", "Worth a week", "=", after.week - week, "money", "approximate"),
      ], "approximate"),
      plan: fixed,
    };
  }
  const fx = fid ? ix.fixtures.get(fid) : undefined;
  base.say = say("limit.held.fixtures",
    "Held at {cap} customers an hour by the {fixture}, for {hours} hours of the week. {would} would come. Another ({cost}) is worth {worth} a week.",
    { cap: count(cap), fixture: (fx?.name ?? "fixtures").toLowerCase(), hours: count(hours), would: count(would ?? 0),
      cost: money(base.fix?.cost.value ?? null), worth: money(base.fix?.worth.value ?? null) });
  return base;
}
const capital = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

// ── reckon ───────────────────────────────────────────────────────────────

/** The whole reckoning of one plan: grids, products, the week, setup, payback, the limit. */
export function reckon(data: LedgerData, plan: Plan, ctx: Ctx): Reckoning {
  const ix = index(data);
  const core = simulate(ix, plan, ctx);
  const limit = limitOf(ix, plan, ctx, core);
  const setup = setupFigures(ix, plan, core.building);
  const counted = core.state === "ok" || core.state === "closed";
  const products = counted ? productFigures(ix, core) : [];
  const nullWeek: Week = { moneyIn: none(), goods: none(), wages: none(), rent: none(), ads: none(), deliveries: none(), total: none(), loss: false };
  const week = counted ? weekFigures(ix, core, products, plan) : nullWeek;
  if (core.state === "cannot-open" && core.building) {
    week.rent = figure(core.rent, [line("week.rent", `$${core.building.rentDay} a day × 7`, "+", core.rent)]);
  }
  const perDay = (week.total.value ?? 0) / 7;
  const payable = counted && setup.total.value != null && perDay > 0;
  const paybackDays = payable
    ? figure(setup.total.value! / perDay, [
      line("payback.setup", "Setup", "+", setup.total.value),
      line("payback.day", "The week ÷ 7", "÷", perDay, "money", "approximate"),
      line("payback.days", "Days", "=", setup.total.value! / perDay, "days", "approximate"),
    ], "approximate")
    : figure(null, counted ? [line("payback.never", "A week that makes nothing never pays it back", "=", null, "days")] : []);
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const customers = counted
    ? figure(core.customers, [
      ...days.map((d, i) => line(`customers.${i}`, d, "+", sum(core.served[i]), "count", "approximate")),
      line("customers.would", "Would come", "=", core.wouldWeek, "count", "approximate"),
      line("customers.promotion", `Promotion ${core.promo!.promotion} % (traffic ${core.promo!.traffic} + campaigns ${core.promo!.marketing})`, "×", core.promo!.multiplier, "factor", core.promo!.marketing > 0 ? "approximate" : "counted"),
      line("customers.bonus", "The difficulty's promotion bonus, unverified", "+", null, "percent"),
      line("customers.heldBack", "Held back by a ceiling", "−", core.wouldWeek - core.customers, "count", "approximate"),
    ], "approximate")
    : none();
  return {
    state: core.state, would: core.would, served: core.served, heldBy: core.heldBy, customers,
    promotion: core.promo, products, week, setup, paybackDays, limit, missing: core.missing,
  };
}

// ── priceStair ───────────────────────────────────────────────────────────

/** The staircase for one product in one neighbourhood: its treads, and the
 *  market / every-customer-buys / best / competitor markers (01 §1.3). */
export function priceStair(data: LedgerData, productId: string, neighbourhoodId: string,
  events: StairEvents = {}, opts: StairOptions = {}): Stair | null {
  const ix = index(data);
  const product = ix.products.get(productId);
  const hood = ix.hoods.get(neighbourhoodId);
  if (!product || !hood) return null;
  const pm = priceModel(data, product, hood, {
    competitor: opts.competitorPrice, monopoly: events.monopoly, shortage: events.shortage, backorder: events.backorder,
  });
  // Best: the tread whose top price × share of buyers is largest. Below the
  // all-buy edge nobody more buys, so a lower price only earns less.
  let best = pm.steps[0] ?? { to: pm.allBuy, share: 1 } as Tread;
  for (const s of pm.steps) if (s.to * s.share > best.to * best.share + EPS) best = s;
  const nothing = !!events.backorder;
  const moneyWeek = opts.unitsAtEdge != null ? (nothing ? 0 : opts.unitsAtEdge * best.share * best.to) : null;
  return {
    productId, neighbourhoodId, reference: pm.reference, market: product.marketPrice, edges: pm.edges, steps: pm.steps,
    markers: { market: product.marketPrice, allBuy: pm.allBuy, best: best.to, competitor: opts.competitorPrice ?? null },
    best: { price: best.to, share: best.share, moneyWeek },
    demandAdd: events.hype ? HYPE_DEMAND : 0,
    nothingToSell: nothing,
    honesty: events.shortage || events.backorder || events.hype ? "approximate" : "counted",
  };
}

// ── cheapestCampaigns ────────────────────────────────────────────────────

/** Tries all 63 mixes of the six campaigns for a building; the cheapest whose
 *  marketing gain reaches `target` points of promotion, and the most any mix
 *  reaches (04 §5). Ties go to the higher gain, then to the fewer campaigns. */
export function cheapestCampaigns(data: LedgerData, buildingId: string, target: number): CampaignAnswer | null {
  const ix = index(data);
  const b = ix.buildings.get(buildingId);
  if (!b) return null;
  const hood = ix.hoods.get(b.neighbourhood);
  const cs = ix.campaigns;
  const n = cs.length;
  let hit: CampaignMix | null = null;
  let max: CampaignMix | null = null;
  const better = (a: CampaignMix, m: CampaignMix | null, byGain: boolean) => {
    if (!m) return true;
    if (byGain && a.gain !== m.gain) return a.gain > m.gain;
    if (a.costDay !== m.costDay) return a.costDay < m.costDay;
    if (a.gain !== m.gain) return a.gain > m.gain;
    return a.campaigns.length < m.campaigns.length;
  };
  let tried = 0;
  for (let mask = 1; mask < 1 << n; mask++) {
    tried++;
    const chosen = cs.filter((_, i) => mask & (1 << i));
    const reach = sum(chosen.map((c) => c.reach));
    const gain = marketingGain(data, b, hood, reach);
    const costDay = sum(chosen.map((c) => c.costDay));
    const mix: CampaignMix = {
      campaigns: chosen.map((c) => c.id), gain, costDay, costWeek: costDay * 7,
      promotion: Math.min(data.rules.promotion.max ?? 100, b.traffic + gain),
    };
    if (gain >= target && better(mix, hit, false)) hit = mix;
    if (better(mix, max, true)) max = mix;
  }
  return { buildingId, target, tried, reached: !!hit, mix: hit, max: max! };
}

// ── rentOrBuy ────────────────────────────────────────────────────────────

/** Rent against the price of the whole building (03 §2.3, §3). A game year is
 *  60 days. Tenant income and property tax are not counted: their 1.0 formulas
 *  are unknown. */
export function rentOrBuy(data: LedgerData, buildingId: string, years: number): RentOrBuy | null {
  const ix = index(data);
  const b = ix.buildings.get(buildingId);
  if (!b) return null;
  const daysPerYear = data.difficulties?.[0]?.daysPerYear ?? 60;
  const y = Math.max(0, years);
  if (b.rentDay == null || b.price == null) {
    return {
      buildingId, state: "not-for-rent", years: y, daysPerYear, rentYear: none(), rentOver: none(), price: none(),
      yearsToRepay: none(), verdict: null, difference: null,
      say: say("rob.notForRent", "This building is not for rent or sale."),
    };
  }
  const rentYear = b.rentDay * daysPerYear;
  const rentOver = rentYear * y;
  const repay = b.price / rentYear;
  const verdict = rentOver > b.price ? "buy" : "rent";
  const difference = verdict === "buy" ? rentOver - b.price : b.price - rentOver;
  const notCounted = [
    line("rob.tenants", "Rent from tenants in the rest of the building", "+", null),
    line("rob.tax", "Property tax", "−", null),
  ];
  const params = { years: count(y), rentOver: money(rentOver), difference: money(difference), repay: count(Math.ceil(repay - EPS)) };
  return {
    buildingId, state: "ok", years: y, daysPerYear,
    rentYear: figure(rentYear, [line("rob.rentDay", `$${b.rentDay} a day`, "+", b.rentDay), line("rob.days", `${daysPerYear} days a game year`, "×", daysPerYear, "days")]),
    rentOver: figure(rentOver, [line("rob.rentYear", "Rent a game year", "+", rentYear), line("rob.years", `${count(y)} game years`, "×", y, "years")]),
    price: figure(b.price, [line("rob.price", `The whole building, ${count(b.buildingSqm ?? b.sqm)} m²`, "+", b.price), ...notCounted]),
    yearsToRepay: figure(repay, [line("rob.price", "Price", "+", b.price), line("rob.rentYear", "Rent a game year", "÷", rentYear), line("rob.repay", "Game years", "=", repay, "years")]),
    verdict, difference,
    say: verdict === "buy"
      ? say("rob.buy", "Buy. Over {years} game years renting would cost {difference} more than the price.", params)
      : say("rob.rent", "Rent. Over {years} game years rent comes to {rentOver}; buying costs {difference} more than that, and only pays back after {repay} game years.", params),
  };
}

// ── rankBuildings ────────────────────────────────────────────────────────

const RANK_MEMO = new WeakMap<LedgerData, Map<string, RankRow[]>>();
const MEMO_SIZE = 16;

function stable(v: unknown): string {
  if (v == null || typeof v !== "object") return JSON.stringify(v ?? null);
  if (Array.isArray(v)) return `[${v.map(stable).join(",")}]`;
  const o = v as Record<string, unknown>;
  return `{${Object.keys(o).sort().filter((k) => o[k] !== undefined).map((k) => `${JSON.stringify(k)}:${stable(o[k])}`).join(",")}}`;
}

/** Every building that passes the filters, each with the week this plan would
 *  make there (null where the type cannot trade), sorted. Memoised by plan,
 *  context and filters; the rows are shared, so treat them as read-only. */
export function rankBuildings(data: LedgerData, plan: Plan, ctx: Ctx, filters: RankFilters = {}): RankRow[] {
  const key = stable({ plan, ctx, filters });
  let memo = RANK_MEMO.get(data);
  if (!memo) { memo = new Map(); RANK_MEMO.set(data, memo); }
  const hit = memo.get(key);
  if (hit) return hit;
  const ix = index(data);
  const rank = filters.rank ?? true;
  const use = filters.use && filters.use !== "any" ? filters.use : null;
  const rows: RankRow[] = [];
  for (const b of data.buildings) {
    if (filters.neighbourhood && b.neighbourhood !== filters.neighbourhood) continue;
    if (use && b.use !== use) continue;
    if (filters.capacity != null && b.capacity !== filters.capacity) continue;
    if (!rank || !plan.typeId) { rows.push({ id: b.id, week: null, customers: null, state: null }); continue; }
    const core = simulate(ix, { ...plan, buildingId: b.id }, ctx);
    const ok = core.state === "ok" || core.state === "closed";
    rows.push({ id: b.id, week: ok ? core.week : null, customers: ok ? core.customers : null, state: core.state });
  }
  const sort = filters.sort ?? (rank ? "week" : "rent");
  const dir = filters.dir ?? (sort === "address" ? 1 : -1);
  const val = (r: RankRow): number | string | null => {
    const b = ix.buildings.get(r.id)!;
    if (sort === "week") return r.week;
    if (sort === "rent") return b.rentDay;
    if (sort === "capacity") return b.capacity;
    if (sort === "traffic") return b.traffic;
    return b.address;
  };
  rows.sort((a, b) => {
    const x = val(a), y = val(b);
    if (x == null && y == null) return a.id.localeCompare(b.id);
    if (x == null) return 1; // nothing to rank sits at the end, either way
    if (y == null) return -1;
    const c = typeof x === "string" ? x.localeCompare(y as string) : (x as number) - (y as number);
    return c !== 0 ? c * dir : a.id.localeCompare(b.id);
  });
  if (memo.size >= MEMO_SIZE) memo.delete(memo.keys().next().value!);
  memo.set(key, rows);
  return rows;
}
