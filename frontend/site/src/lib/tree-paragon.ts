/* Diablo IV's paragon boards (README-planners §5.3).
 *
 * A board is a 21 × 21 grid with its corners cut — that is the board's own
 * shape, and it comes out of the data, not out of a drawing. Reaching a far
 * node means paying for every cell on the way, so the ROUTE is the choice
 * and a proposal states the whole cost.
 *
 * ⚠ Nothing here is taken from the game's art or palette. The structure is a
 * fact about the game; every colour is the section's, and gold marks only an
 * untaken legendary — the one thing in the section that uses it besides the
 * compass ring.
 */
export type Cell = {
  id: string; name: string; kind?: string; sub?: string; row?: number; col?: number;
  connections?: string[]; stats?: unknown[]; summary?: string;
};

/* ⚠ A record's `kind` is what the database files it under — every cell here
 * is a "node". What KIND of node it is (normal · magic · rare · legendary ·
 * glyph-socket · gate · start) is its `sub`. Reading the wrong one draws
 * every cell the same size and loses the board's whole shape. */
export const cellKind = (c: Cell) => String(c.sub || (c.kind !== "node" ? c.kind : "") || "normal");
export type Board = {
  id: string; name: string; grid?: { width: number; height: number };
  glyph_socket?: { node_id?: string; row?: number; col?: number };
  gates?: { row?: number; col?: number }[];
};

const escape = (t: unknown) =>
  String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c] as string));

/** The size of a cell, in units of one cell, by what kind of node it is. */
const SIZE: Record<string, number> = { legendary: 0.86, start: 0.86, rare: 0.74, "glyph-socket": 0.74, magic: 0.56, normal: 0.44, gate: 0.5 };

/**
 * ⚠ The board's shape. A 21 × 21 grid with its corners cut: no cell further
 * than fifteen steps from the middle counting both ways, and none where both
 * ways exceed eight. Drawing the full square would draw a board the game
 * does not have.
 */
export function onBoard(row: number, col: number, size = 21): boolean {
  const middle = (size - 1) / 2;
  const dr = Math.abs(row - middle), dc = Math.abs(col - middle);
  return dr + dc <= 15 && !(dr > 8 && dc > 8);
}

const fill = (kind: string, taken: boolean, looking: boolean) =>
  looking ? "var(--state-now)" : taken ? "var(--state-done)" : kind === "start" ? "var(--state-open)" : "var(--surface-card)";

const stroke = (kind: string, taken: boolean) =>
  taken ? "var(--state-done)" : kind === "legendary" ? "var(--guide-gold)" : kind === "rare" ? "var(--state-open)" : "var(--state-locked)";

export function drawBoard(board: Board, cells: Cell[], taken: Set<string>, looking: string, mini = false): string {
  const size = board.grid?.width || 21;
  const on = cells.filter((c) => typeof c.row === "number" && typeof c.col === "number" && onBoard(c.row!, c.col!, size));

  /* the allocated route: one path through the cells a person has paid for */
  const route = on.filter((c) => taken.has(c.id)).map((c) => `M ${c.col! + 0.5} ${c.row! + 0.5} l 0.001 0`).join(" ");

  const socket = board.glyph_socket;
  const radius = socket && typeof socket.row === "number"
    ? `<rect x="${socket.col! + 0.5 - 4.5}" y="${socket.row! + 0.5 - 4.5}" width="9" height="9" rx="0.3"
        fill="var(--accent-wash)" stroke="var(--accent)" stroke-width="0.08" stroke-dasharray="0.4 0.3"/>`
    : "";

  const gates = (board.gates || []).filter((g) => typeof g.row === "number").map((g) =>
    `<rect x="${g.col! + 0.5 - 0.25}" y="${g.row! + 0.5 - 1.3}" width="0.5" height="2.6" fill="var(--rose)" opacity=".8"/>`).join("");

  const marks = on.map((c) => {
    const kind = cellKind(c);
    const s = SIZE[kind] ?? 0.44;
    const got = taken.has(c.id);
    const me = c.id === looking;
    return `<rect x="${c.col! + 0.5 - s / 2}" y="${c.row! + 0.5 - s / 2}" width="${s}" height="${s}" rx="${s / 6}"
      fill="${fill(kind, got, me)}" stroke="${me ? "var(--state-now)" : stroke(kind, got)}" stroke-width="${me ? 0.12 : 0.07}"
      ${mini ? "" : `data-cell="${escape(c.id)}" class="pg-cell"`}><title>${escape(c.name)}</title></rect>`;
  }).join("");

  const socketRing = socket && typeof socket.row === "number"
    ? `<circle cx="${socket.col! + 0.5}" cy="${socket.row! + 0.5}" r="0.37" fill="none" stroke="var(--accent)" stroke-width="0.1"/>`
    : "";

  return `<svg class="${mini ? "pg-mini" : "pg-board"}" viewBox="-1 -1 ${size + 2} ${size + 2}" role="img"
    aria-label="${escape(board.name)}">
    ${radius}${gates}
    ${route ? `<path d="${route}" stroke="var(--state-done)" stroke-width="0.34" stroke-linecap="round" fill="none"/>` : ""}
    ${marks}${socketRing}
  </svg>`;
}

/** The chain: the boards a plan equips, with the gate between each. */
export function drawChain(boards: Board[], cellsOf: (id: string) => Cell[], taken: Set<string>, open: string): string {
  const most = 5;
  const strip = boards.slice(0, most).map((b, i) => `
    ${i ? `<span class="pg-gate" aria-hidden="true"></span>` : ""}
    <button type="button" class="pg-link" data-board="${escape(b.id)}" aria-current="${b.id === open}">
      ${drawBoard(b, cellsOf(b.id), taken, "", true)}
      <span class="pg-link-name">${escape(b.name)}</span>
    </button>`).join("");
  const room = boards.length < most
    ? `<span class="pg-room">five boards is the most a character may equip</span>` : "";
  return `<div class="pg-chain">${strip}${room}</div>`;
}
