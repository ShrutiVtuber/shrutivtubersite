/* Path of Exile 2's passive tree (README-planners §5.2).
 *
 * Four thousand nodes on one canvas, zoomed and panned. The positions and
 * the edges come out of the data; nothing of the game's art, palette or
 * layout does.
 *
 * ⚠ Detail follows the zoom, because four thousand names at once is not a
 * tree, it is a wall: far draws dots only, mid names the keystones and the
 * class starts, near names the notables too. Small nodes are counted in the
 * chooser, not listed — and here they are drawn but never labelled.
 */
export type Node = {
  id: string; name: string; sub?: string; kind?: string;
  position?: { x: number; y: number }; connections?: string[]; summary?: string;
};

const escape = (t: unknown) =>
  String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c] as string));

export const PRESETS = { far: 0.42, mid: 0.85, near: 1.55 } as const;
export const ZOOM_MIN = 0.28;
export const ZOOM_MAX = 3.2;
export const ZOOM_STEP = 1.35;

/** What kind of node it is: `sub` where the database has it, else `kind`. */
export const nodeKind = (n: Node) => String(n.sub || (n.kind !== "node" ? n.kind : "") || "small");

const R: Record<string, number> = { keystone: 26, notable: 18, mastery: 14, "jewel-socket": 15, ascendancy: 12, start: 22, attribute: 8, small: 7 };

/**
 * How far in we are, as a multiple of the scale that would show the whole
 * tree. ⚠ The spec's presets are numbers for a normalised space; a real tree
 * spans tens of thousands of units, so an absolute scale would put nearly
 * all of it off the canvas. Everything below reads this, not the raw scale.
 */
export const depth = (k: number, fit: number) => (fit > 0 ? k / fit : k);

/**
 * ⚠ The thresholds are just below the presets on purpose. Stepping from mid
 * by the zoom step lands on 1.549…, and a threshold of exactly `near` would
 * never be crossed by the control a person actually uses.
 */
const named = (kind: string, d: number) =>
  d >= PRESETS.near - 0.01
    ? kind !== "small" && kind !== "attribute"
    : d >= PRESETS.mid - 0.01
      ? kind === "keystone" || kind === "start"
      : false;

export function bounds(nodes: Node[]) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const n of nodes) {
    const p = n.position;
    if (!p) continue;
    minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x);
    minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y);
  }
  return Number.isFinite(minX) ? { minX, minY, maxX, maxY } : { minX: 0, minY: 0, maxX: 1, maxY: 1 };
}

/** Every edge as ONE path — four thousand line elements is a page that scrolls badly. */
function edges(nodes: Node[]): string {
  const at = new Map(nodes.map((n) => [n.id, n]));
  const seen = new Set<string>();
  const parts: string[] = [];
  for (const n of nodes) {
    const a = n.position;
    if (!a) continue;
    for (const other of n.connections || []) {
      const key = n.id < other ? `${n.id}|${other}` : `${other}|${n.id}`;
      if (seen.has(key)) continue;
      seen.add(key);
      const b = at.get(other)?.position;
      if (b) parts.push(`M${a.x} ${a.y}L${b.x} ${b.y}`);
    }
  }
  return parts.join("");
}

/** The scale at which the whole tree fits the canvas. */
export function fitFor(nodes: Node[], width = 1240, height = 720): number {
  const b = bounds(nodes);
  const w = Math.max(1, b.maxX - b.minX), h = Math.max(1, b.maxY - b.minY);
  return Math.min(width / w, height / h);
}

export function drawTree(nodes: Node[], taken: Set<string>, looking: string, k: number, fit = 1): string {
  const drawn = nodes.filter((n) => n.position);
  const marks = drawn.map((n) => {
    const kind = nodeKind(n);
    const r = R[kind] ?? 7;
    const got = taken.has(n.id);
    const me = n.id === looking;
    const fill = me ? "var(--state-now)" : got ? "var(--state-done)" : "var(--surface-card)";
    const line = me ? "var(--state-now)" : got ? "var(--state-done)" : kind === "keystone" || kind === "start" ? "var(--state-open)" : "var(--state-locked)";
    return `<circle cx="${n.position!.x}" cy="${n.position!.y}" r="${r}" fill="${fill}" stroke="${line}"
      stroke-width="${me ? 5 : got ? 4 : 2}" class="pt-node" data-node="${escape(n.id)}"><title>${escape(n.name)}</title></circle>`;
  }).join("");

  const d = depth(k, fit);
  const labels = drawn.filter((n) => named(nodeKind(n), d)).map((n) =>
    `<text x="${n.position!.x}" y="${n.position!.y - (R[nodeKind(n)] ?? 7) - 8}" text-anchor="middle"
      class="pt-label" font-size="${Math.round(26 / Math.max(d, 0.5))}">${escape(n.name)}</text>`).join("");

  return `<path d="${edges(drawn)}" class="pt-edges" fill="none"/>${marks}${labels}`;
}
