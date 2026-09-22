/* Diablo II's skill tabs (README-planners §5.4).
 *
 * Three tabs of ten skills on a 3 × 6 grid, over an arrows-only SVG. The
 * arrows are the tab's whole shape: parent bottom to child top, heavy where
 * the parent has points and light where it does not.
 *
 * ⚠ The synergies are NOT drawn across the page. A skill raises, and is
 * raised by, skills that are often on another tab, and lines between tabs
 * make a hairball. Only the selected skill's own-tab synergies are curved on
 * the canvas; everything else is legible as TYPE in the panel beside, where a
 * different tab is named in mono and marked in accent.
 */
export type TabNode = {
  id: string; name: string; kind?: string; level_req?: number;
  position?: { row: number; column: number }; requires?: string[]; connections?: string[];
};
export type Tab = { id: string; name: string; nodes?: TabNode[] };
export type Synergy = { skill_id: string; per_point?: number; effect?: string; stat?: string };

const escape = (t: unknown) =>
  String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c] as string));

/* 100 units a column, 100 a row, so a cell's centre is (c·100+50, r·100+50). */
const CX = (n: TabNode) => ((n.position?.column ?? 1) - 1) * 100 + 50;
const CY = (n: TabNode) => ((n.position?.row ?? 1) - 1) * 100 + 50;

export function drawArrows(tab: Tab, points: Record<string, number>, selected: string, synergies: Synergy[]): string {
  const nodes = tab.nodes || [];
  const at = new Map(nodes.map((n) => [n.id, n]));
  const arrows = nodes.flatMap((child) =>
    (child.requires || []).map((parentId) => {
      const parent = at.get(parentId);
      if (!parent) return "";
      const met = (points[parentId] || 0) > 0;
      return `<line x1="${CX(parent)}" y1="${CY(parent) + 34}" x2="${CX(child)}" y2="${CY(child) - 40}"
        stroke="var(${met ? "--state-done" : "--line-strong"})" stroke-width="${met ? 2 : 1.2}" marker-end="url(#tt-tip)"/>`;
    })).join("");

  /* only the selected skill's synergies, and only inside its own tab */
  const here = new Set(nodes.map((n) => n.id));
  const bows = selected && here.has(selected)
    ? synergies.filter((s) => here.has(s.skill_id) && s.skill_id !== selected).map((s) => {
        const a = at.get(selected)!, b = at.get(s.skill_id)!;
        const mx = (CX(a) + CX(b)) / 2 + 76, my = (CY(a) + CY(b)) / 2;
        return `<path d="M ${CX(a)} ${CY(a)} Q ${mx} ${my} ${CX(b)} ${CY(b)}" fill="none"
          stroke="var(--accent)" stroke-width="1.6" stroke-dasharray="5 4"/>`;
      }).join("")
    : "";

  return `<svg class="tt-arrows" viewBox="0 0 300 600" preserveAspectRatio="none" aria-hidden="true">
    <defs><marker id="tt-tip" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M0 0 L8 4 L0 8 z" fill="currentColor"/></marker></defs>
    ${arrows}${bows}</svg>`;
}

export function drawTab(tab: Tab, points: Record<string, number>, selected: string, synergies: Synergy[]): string {
  const nodes = (tab.nodes || []).slice().sort((a, b) => (a.position?.row ?? 0) - (b.position?.row ?? 0));
  const raised = new Set(synergies.map((s) => s.skill_id));
  const cells = nodes.map((n) => {
    const spent = points[n.id] || 0;
    const state = spent ? "in" : "none";
    const look = n.id === selected ? "looking" : raised.has(n.id) ? "raises" : state;
    return `<button type="button" class="tt-cell" data-skill="${escape(n.id)}" data-look="${look}"
      style="grid-row:${n.position?.row ?? 1};grid-column:${n.position?.column ?? 1}"
      aria-pressed="${n.id === selected}">
      <span class="tt-name">${escape(n.name)}</span>
      <span class="tt-points">${spent || "·"}</span>
    </button>`;
  }).join("");
  const spentHere = nodes.reduce((sum, n) => sum + (points[n.id] || 0), 0);
  return `<div class="tt-tab" data-tab="${escape(tab.id)}">
    <div class="tt-head"><span class="gd-eyebrow">${escape(tab.name)}</span><span class="gd-mono tt-spent">${spentHere}</span></div>
    <div class="tt-grid">${drawArrows(tab, points, selected, synergies)}${cells}</div>
  </div>`;
}

/** It raises · It is raised by — two indices, so a cross-tab link reads as type. */
export function drawSynergyPanel(
  skill: { id: string; name: string; synergies?: Synergy[] } | null,
  tabOf: (id: string) => string,
  nameOf: (id: string) => string,
  points: Record<string, number>,
  raisedBy: { id: string; name: string; per_point?: number }[],
): string {
  if (!skill) return `<p class="gd-hint">Take a skill to see what raises it, and what it raises.</p>`;
  const here = tabOf(skill.id);
  const row = (id: string, per: number | undefined) => {
    const tab = tabOf(id);
    const taken = (points[id] || 0) > 0;
    return `<div class="tt-syn" data-taken="${taken ? "yes" : "no"}">
      <span>${escape(nameOf(id))}</span>
      <span class="gd-mono tt-tab-name" data-elsewhere="${tab !== here ? "yes" : "no"}">${escape(tab || "")}</span>
      <span class="gd-mono">${per != null ? `${per}%` : ""}</span>
      <span class="tt-rule">${taken ? `${points[id]} points at ${per ?? "?"}% a point` : "nothing taken"}</span>
    </div>`;
  };
  const raises = (skill.synergies || []).map((s) => row(s.skill_id, s.per_point)).join("");
  const by = raisedBy.map((s) => row(s.id, s.per_point)).join("");
  return `
    ${raises ? `<div class="tt-part"><p class="gd-eyebrow">It is raised by</p>${raises}</div>` : ""}
    ${by ? `<div class="tt-part"><p class="gd-eyebrow">It raises</p>${by}</div>` : ""}
    ${raises || by ? "" : `<p class="gd-hint">${escape(skill.name)} has no synergies.</p>`}`;
}
