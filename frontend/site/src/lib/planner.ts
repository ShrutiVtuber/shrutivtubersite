/* The build planner's data layer.
 *
 * Everything the planner draws comes from two places: the game database
 * (`/api/gamedata`, facts about games and nothing about anybody) and the
 * person's own plan (`/api/builds`). This module holds the shapes both
 * speak and the small amount of reading that is the same on every surface.
 *
 * ⚠ A plan is never computed here. The server cleans it, bounds it, refuses
 * what the data does not know and says why — see `shrutisguides.gamedata`.
 * The page's job is to show what came back, refusals included.
 */

export type GamePack = {
  id: string;
  name: string;
  patch: string;
  season: string;
  researched_at: string;
  level_cap: number | null;
  counts: Record<string, number>;
  problems: number;
  planner: boolean;
};

export type Field =
  | { type: "id"; kind: string; sub?: string | string[]; by_class?: boolean }
  | { type: "ids"; kind: string; sub?: string | string[]; max?: number; by_class?: boolean }
  | { type: "int"; min?: number; max?: number; unit?: string }
  | { type: "choice"; options: string[] }
  | { type: "text" }
  | { type: "within"; list: string; max?: number };

export type Section = {
  id: string;
  name: string;
  type: "pick" | "picks" | "gear" | "targets";
  kind?: string;
  sub?: string | string[];
  by_class?: boolean;
  max?: number;
  grid?: boolean;
  track?: string;
  slots?: string[] | Record<string, string>;
  exclude?: string[];
  fields?: Record<string, Field>;
  points?: { id: string; name: string; field?: string; unit?: string };
  entries?: { id: string; name: string; max?: number; unit?: string }[];
};

export type Recipe = { game: string; sections: Section[] };

/** A record as a chooser row shows it. The whole record comes from `/{kind}/{id}`. */
export type Row = {
  kind: string;
  id: string;
  name: string;
  sub: string;
  group: string;
  class_ids: string[];
  slot_id: string;
  tags: string[];
  level_req: number | null;
  summary: string;
};

export type Line = { value: number; form: string; text: string; where: string; kind: string; name: string; state: string; condition?: string };
export type Step = { kind: string; label: string; value: number; running: number; lines: Line[] };
export type StatRow = {
  stat: string; name: string; unit: string; group: string; integer: boolean;
  value: number; state: string; why?: string; cap?: string;
  steps: Step[]; uncounted: Line[]; inactive: Line[];
};
export type Hit = {
  skill: string; name: string; element: string;
  low: number; high: number; average: number; rank: number; state: string; why: string;
  steps: { kind: string; label: string; value: number; running: number }[];
};
export type Assumption = { id: string; name: string; held: boolean; lines: number; stats: string[] };
export type Sheet = {
  game: string; level: number; supported: boolean; state: string;
  groups: { group: string; rows: StatRow[] }[];
  damage: Hit[];
  conditions: Assumption[];
  uncounted: { lines: number; things: number; from: { kind: string; id: string; name: string; where: string; lines: number }[] };
};

export type PlanSummary = {
  game: string; gameName: string; patch: string; season: string;
  classId: string; className: string; level: number | null; choices: number;
  sections: { id: string; name: string; type: string; lines: { id: string; label: string; detail: string }[] }[];
};

/** The person's choices, exactly as the server reads them back. */
export type Plan = {
  game: string;
  class_id: string;
  level: number | null;
  notes: string;
  conditions: string[];
  sections: Record<string, unknown>;
};

/* ── the words a planner page always needs ───────────────────────────────── */

/** `Diablo IV 3.2.1 · Season 15 · gathered 21 Sep 2026` — on every planner page. */
export function dataLine(pack: Pick<GamePack, "name" | "patch" | "season" | "researched_at"> | null): string {
  if (!pack) return "";
  const gathered = pack.researched_at ? `gathered ${asDate(pack.researched_at)}` : "";
  return [pack.name, short(pack.patch), short(pack.season), gathered].filter(Boolean).join(" · ");
}

/** A pack states its patch and season at length; a line wants the front of it. */
function short(value: string): string {
  return String(value || "").split(" (")[0].split(";")[0].trim();
}

function asDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return `${d.getUTCDate()} ${["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

/* ── marks ───────────────────────────────────────────────────────────────── */

/** A slot's mark. One drawing serves all three games: a helm is a helm. */
const SLOT_MARKS: [RegExp, string][] = [
  [/(helm|head|circlet)/, "slot-head"],
  [/(chest|torso|body)/, "slot-body"],
  [/(glove|hand)/, "slot-hands"],
  [/(pants|legs|greave)/, "slot-legs"],
  [/(boot|feet)/, "slot-feet"],
  [/(amulet|neck)/, "slot-neck"],
  [/ring/, "slot-ring"],
  [/belt/, "slot-belt"],
  [/(quiver)/, "slot-quiver"],
  [/(focus|grimoire|orb|totem|book)/, "slot-focus"],
  [/(shield|off-hand|offhand)/, "slot-shield"],
  [/(ranged|bow|crossbow)/, "slot-ranged"],
  [/(two-hand|2h|two handed)/, "slot-weapon-2h"],
  [/(weapon|main-hand|mainhand|dual-wield)/, "slot-weapon-1h"],
  [/flask/, "slot-flask"],
  [/charm/, "slot-charm"],
  [/jewel/, "slot-jewel"],
  [/(socket|gem)/, "slot-socket"],
  [/rune/, "slot-rune"],
  [/merc/, "slot-mercenary"],
];

export function slotMark(slotId: string): string {
  const id = String(slotId || "").toLowerCase();
  for (const [pattern, mark] of SLOT_MARKS) if (pattern.test(id)) return mark;
  return "slot-socket";
}

/** What kind of record a chooser row is. */
const KIND_MARKS: Record<string, string> = {
  skill: "kind-active", specialization: "kind-support", board: "kind-board", node: "kind-node",
  glyph: "kind-glyph", unique: "kind-unique", set: "kind-set", runeword: "kind-runeword",
  affix: "kind-affix", aspect: "kind-aspect", tempering: "kind-manual", progression: "kind-progression",
};

export function kindMark(row: Pick<Row, "kind" | "sub">): string {
  if (row.kind === "skill" && (row.sub === "support" || row.sub === "passive")) return "kind-support";
  return KIND_MARKS[row.kind] || "kind-node";
}

/** An element's mark, for a damage row or an affix that names one. */
export function statMark(stat: string): string {
  const id = String(stat || "").toLowerCase();
  for (const e of ["fire", "cold", "lightning", "poison", "shadow", "physical", "holy", "life", "mana", "armour"]) {
    if (id.includes(e)) return `stat-${e === "shadow" ? "shadow" : e}`;
  }
  return "";
}

/* ── reading a sheet ─────────────────────────────────────────────────────── */

/** A number as the panel writes it: tabular, with its unit, never rounded away. */
export function figure(row: Pick<StatRow, "value" | "unit" | "integer">): string {
  const n = row.integer ? Math.round(row.value) : Math.round(row.value * 10) / 10;
  return `${n.toLocaleString("en-GB")}${row.unit || ""}`;
}

/** Whether a row is at or past the cap the game sets for it. */
export function atCap(row: StatRow, rows: Record<string, StatRow>): boolean {
  const cap = row.cap ? rows[row.cap] : undefined;
  return !!cap && row.value >= cap.value;
}

export const STATE_WORDS: Record<string, string> = {
  counted: "counted",
  approximate: "approximate",
  "not-counted": "not counted",
};
