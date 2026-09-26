/* The Ledger's shapes: the data pack it reads (Contract 1 of docs/LEDGER.md)
 * and the plan, context and results of the engine (Contract 2).
 *
 * Types only. Nothing here runs, so `node --test` can load engine.ts (which
 * imports this file with `import type`) by stripping types, with no build.
 */

// ── Contract 1: the data pack ────────────────────────────────────────────

export type ClassId = "working" | "middle" | "upper";
export type Confidence = "datamined" | "community" | "estimated";
export type BuildingUse = "shop" | "office" | "warehouse" | "home" | "cinema" | "theatre" | "special";
export type FixtureKind = "pos" | "display" | "required" | "comfort" | "security" | "storage";

export interface Difficulty {
  id: string;
  name: string;
  startMoney: number;
  taxPct: number;
  daysPerYear?: number;
  baseCustomerPromotionMultiplier: number;
  salaryMultiplier: number;
  marketPriceMultiplier: number;
  [k: string]: unknown;
}

export interface Neighbourhood {
  id: string;
  name: string;
  mix: Record<ClassId, number>;
  priceIndex: number;
  marketingStrength: number;
  demandsWeight: number;
  minInterior: number;
  rival: string | null;
  realEstateMultiplier?: number;
}

export interface Building {
  id: string;
  address: string;
  neighbourhood: string;
  use: BuildingUse;
  layout: string | null;
  sqm: number;
  buildingSqm?: number;
  capacity: number | null;
  traffic: number;
  vehicleSlots: number;
  rentDay: number | null;
  deposit: number | null;
  price: number | null;
}

export interface EntranceFee { product: string; days: number[] }

export interface BusinessType {
  id: string;
  name: string;
  category: string;
  simulator: string | null;
  course: string | null;
  uses: BuildingUse[];
  staff: string[];
  stock: string[];
  theft: boolean;
  maxAmountPerProduct: number;
  dayMult: number[] | null;
  hourMult: number[] | null;
  products: { product: string; impact: number }[];
  requires: string[];               // "a|b" = either
  conditions?: string[];            // any-primary-product · licensing-fees · hair-care-product-in-stock
  demands: Record<string, number>;
  entranceFee: EntranceFee[] | null;
  perCustomerProduct?: string | null;
  licensingFeeDay?: number | null;
  estimated?: string[];
}

export interface Product {
  id: string;
  name: string;
  kind?: "product" | "service";
  marketPrice: number;
  wholesale: number;
  box: number;
  salesRatio: number;
  optimalProviders: number | null;
  sources: string[];
  weeklyLimit: number | null;
  importerWeeklyLimit?: number | null;
  displays: { fixture: string; units: number | null; confidence?: Confidence }[];
}

export interface Fixture {
  id: string;
  name: string;
  price: number;
  store: string;
  customersPerHour: number | null;
  kind: FixtureKind;
  needs: string | null;             // "a|b" = either
  displays: { product: string; units: number | null }[];
  confidence?: Confidence;
}

export interface StaffRole {
  id: string;
  name: string;
  baseWage: number;
  station: string | null;           // "a|b" = either
  agency?: string;
  trainingMultiplier?: number;
}

export interface Campaign { id: string; name: string; kind: string; costDay: number; reach: number; agency?: string }
export interface Course { id: string; name: string; price?: number | null; unlocks?: string[] }

export interface LedgerRules {
  classCeilings: Record<ClassId, number>;
  monopolyBonus: number;
  satisfaction: { at0: number; at100: number };
  promotion: { gainPerMultiplier: number; max?: number };
  wholesaleDeliveryFee: number;
  unlistedProductImpact?: number;
  marketingReachMultiplier?: Record<string, number>;
  furnitureDelivery?: { fee: number; minimumOrder: number };
  depositDays?: Record<string, number>;
  maxAmountPerProduct?: Record<string, number>;
}

export interface LedgerData {
  game: { id: string; name: string; version: string; build: string; gathered: string };
  rules: LedgerRules;
  difficulties: Difficulty[];
  neighbourhoods: Neighbourhood[];
  buildings: Building[];
  businessTypes: BusinessType[];
  products: Product[];
  fixtures: Fixture[];
  staffRoles: StaffRole[];
  campaigns: Campaign[];
  courses: Course[];
}

// ── Contract 2: plan and context ─────────────────────────────────────────

export interface StaffLine {
  /** Hours a week. Ignored for the role that staffs the registers (its hours come from the painted grid). */
  hours?: number;
  /** Dollars an hour, as the game's MyEmployees shows it. Absent = base wage × the difficulty's salary multiplier. */
  wage?: number;
}

export interface Plan {
  typeId: string | null;
  buildingId: string | null;
  /** productId → shelf price; absent = the all-buy edge. */
  prices: Record<string, number>;
  /** fixtureId → count. */
  fixtures: Record<string, number>;
  /** [7][24], Monday first: 0 closed, n = n registers (stations) staffed. */
  hours: number[][];
  campaigns: Record<string, boolean>;
  /** 0–100, default 80. */
  satisfaction: number;
  satisfactionTyped: boolean;
  /** productId → 0–100, default 80. */
  demand?: Record<string, number>;
  /** productId → the lowest price a rival asks in the neighbourhood. */
  competitorPrice?: Record<string, number>;
  // Additions to Contract 2 (see docs/LEDGER.md):
  /** The products stocked. Absent = the type's primary products (impact 1). */
  products?: string[];
  /** productId → fixtureId → count: which displays hold which product. Absent = shared out by the engine. */
  displays?: Record<string, Record<string, number>>;
  /** roleId → hours a week and/or wage. */
  staff?: Record<string, StaffLine>;
}

export interface Ctx {
  difficulty: string;
  courses: string[];
  /** A Custom difficulty's own values, over the named difficulty's. */
  custom?: Partial<Difficulty>;
  /** The save's import price index (0.5–1.3, MarketInsider). Absent = 0.9, the cheapest wholesalers' index. */
  importIndex?: number;
}

// ── Results ──────────────────────────────────────────────────────────────

export type Honesty = "counted" | "approximate" | "not-counted";
export type LineOp = "+" | "−" | "×" | "÷" | "=";
export type LineUnit = "money" | "count" | "factor" | "hours" | "days" | "percent" | "years" | "price";

/** One line of a breakdown. `value` null = not counted (the popover strikes it through). */
export interface BreakdownLine {
  key: string;
  label: string;
  op: LineOp;
  value: number | null;
  unit: LineUnit;
  honesty: Honesty;
}

export interface Figure {
  value: number | null;
  honesty: Honesty;
  lines: BreakdownLine[];
}

export type HeldBy = "building" | "registers" | "displays" | "fixtures" | null;

export type ReckonState =
  | "ok" | "no-type" | "no-building" | "not-a-shop" | "cannot-open" | "closed" | "no-customers";

export interface Missing {
  path: "type" | "fixtures" | "products";
  /** A course id, a requirement group ("a|b"), a fixture a fixture needs, or a condition. */
  requirement: string;
  /** Plain names for the sentence: the course, or each fixture that would do. */
  names: string[];
  /** For a `needs`: the fixture that needs it. */
  neededBy?: string;
}

export interface Tread {
  /** 0 = every customer buys; each step up loses a class. */
  step: number;
  share: number;
  from: number;
  to: number;
  buyers: ClassId[];
}

export interface ProductLine {
  id: string;
  name: string;
  price: number;
  typed: boolean;
  edge: number;
  tread: Tread | null;
  /** Customers a week who reached this product (after its displays). */
  buyers: number;
  units: number;
  displayCap: number | null;
  displays: Record<string, number>;
  moneyIn: Figure;
  goods: Figure;
}

export interface Say {
  key: string;
  template: string;
  params: Record<string, string>;
}

export interface Fix {
  kind: "register" | "staff" | "display" | "fixture" | "building";
  /** fixtureId → count added. */
  adds: Record<string, number>;
  productId?: string;
  cost: Figure;
  weeklyCost: Figure;
  worth: Figure;
  /** The plan with the fix applied; the UI's "Add a second register" sets it. */
  plan: Plan | null;
}

export interface Limit {
  state: "held" | "free" | "unknown" | "cannot-open" | "not-a-shop";
  reason?: ReckonState;
  by?: Exclude<HeldBy, null>;
  cap?: number;
  hours?: number;
  would?: number | null;
  /** Stations (registers) owned, for "one register". */
  count?: number;
  productId?: string;
  fixtureId?: string;
  heldHours: { registers: number; displays: number; fixtures: number; building: number };
  fix?: Fix;
  say: Say;
}

export interface Week {
  moneyIn: Figure;
  goods: Figure;
  wages: Figure;
  rent: Figure;
  ads: Figure;
  deliveries: Figure;
  total: Figure;
  loss: boolean;
}

export interface Reckoning {
  state: ReckonState;
  would: number[][];
  served: number[][];
  heldBy: HeldBy[][];
  customers: Figure;
  promotion: { traffic: number; marketing: number; promotion: number; multiplier: number } | null;
  products: ProductLine[];
  week: Week;
  setup: { fixtures: Figure; deposit: Figure; total: Figure };
  paybackDays: Figure;
  limit: Limit;
  missing: Missing[];
}

export interface StairEvents { monopoly?: boolean; hype?: boolean; shortage?: boolean; backorder?: boolean }

export interface StairOptions {
  competitorPrice?: number;
  /** Units a week if every customer bought (the plan's units at the all-buy edge); gives money a week. */
  unitsAtEdge?: number;
}

export interface Stair {
  productId: string;
  neighbourhoodId: string;
  reference: number;
  market: number;
  edges: Record<ClassId, number>;
  steps: Tread[];
  markers: { market: number; allBuy: number; best: number; competitor: number | null };
  best: { price: number; share: number; moneyWeek: number | null };
  /** Hype adds this much product demand (points of 100). */
  demandAdd: number;
  nothingToSell: boolean;
  honesty: Honesty;
}

export interface CampaignMix {
  campaigns: string[];
  gain: number;
  promotion: number;
  costDay: number;
  costWeek: number;
}

export interface CampaignAnswer {
  buildingId: string;
  target: number;
  tried: number;
  reached: boolean;
  /** The cheapest mix reaching the target, or null. */
  mix: CampaignMix | null;
  /** The most any mix reaches, at its cheapest. */
  max: CampaignMix;
}

export interface RentOrBuy {
  buildingId: string;
  state: "ok" | "not-for-rent";
  years: number;
  daysPerYear: number;
  rentYear: Figure;
  rentOver: Figure;
  price: Figure;
  yearsToRepay: Figure;
  verdict: "rent" | "buy" | null;
  /** Buy: how much more renting would cost. Rent: how much more buying costs. */
  difference: number | null;
  say: Say;
}

export interface RankFilters {
  neighbourhood?: string | null;
  use?: BuildingUse | "any" | null;
  capacity?: number | null;
  rank?: boolean;
  sort?: "week" | "rent" | "capacity" | "traffic" | "address";
  dir?: 1 | -1;
}

export interface RankRow {
  id: string;
  week: number | null;
  customers: number | null;
  state: ReckonState | null;
}
