/* One record whole (README-planners §2.6, §4.9).
 *
 * It goes as far as the data does, in almanac tables: a unique's every line
 * with its range, an affix's full tier table with the top tier marked, a
 * skill's ranks and its upgrade pairs, a node's stats and its neighbours.
 * Then what it points at and what points at it, then where it came from.
 *
 * ⚠ It stays ours because it is a table in our type with our hairlines. No
 * art slot, no icon, no frame, no rarity colour, nothing shaped like the
 * game's own tooltip.
 */
const escape = (t: unknown) =>
  String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c] as string));

const num = (v: unknown) => (typeof v === "number" ? v.toLocaleString("en-GB") : String(v ?? ""));

/** A range as the data holds it: one number, or two with a dash between. */
export function range(low: unknown, high: unknown): string {
  const a = typeof low === "number" ? low : null;
  const b = typeof high === "number" ? high : null;
  if (a === null && b === null) return "";
  if (a === null || b === null) return num(a ?? b);
  return a === b ? num(a) : `${num(a)}–${num(b)}`;
}

const row = (label: string, value: string, mark = "") => `
  <div class="rc-row${mark ? ` rc-${mark}` : ""}">
    <span>${escape(label)}</span><span class="rc-lead" aria-hidden="true"></span><span class="rc-val">${escape(value)}</span>
  </div>`;

const table = (head: string, rows: string) => rows ? `<div class="rc-part"><p class="gd-eyebrow">${escape(head)}</p>${rows}</div>` : "";

/** Every line a unique or a runeword grants, with its range. */
function lines(rec: any): string {
  const all = (rec.affixes || rec.stats || rec.effects || []).filter((l: any) => l && typeof l === "object");
  if (!Array.isArray(all) || !all.length) return "";
  return table("Its lines", all.map((l: any) =>
    row(l.text || l.stat || l.name || "", range(l.min, l.max) || num(l.value))).join(""));
}

/** An affix's tiers, the top one marked — the only mark this drawer gives. */
function tiers(rec: any): string {
  const all = (rec.tiers || []).filter((t: any) => t && typeof t === "object");
  if (!all.length) return "";
  const rank = (t: any) => Number(t.item_level ?? t.level ?? t.item_power ?? t.tier ?? 0);
  const top = all.reduce((a: any, b: any) => (rank(b) >= rank(a) ? b : a), all[0]);
  return table("Tiers", all.map((t: any) => {
    const at = t.item_level ?? t.level ?? t.item_power;
    const label = [t.name, at != null ? `item level ${num(at)}` : ""].filter(Boolean).join(" · ") || `tier ${num(t.tier)}`;
    return row(label, range(t.min, t.max), t === top ? "top" : "");
  }).join(""));
}

/** A skill's per-rank values — the numbers a planner actually reads. */
function ranks(rec: any): string {
  const all = (rec.ranks_or_levels || []).filter((r: any) => r && typeof r === "object");
  if (!all.length) return "";
  const shown = all.length > 12 ? [all[0], all[Math.floor(all.length / 2)], all[all.length - 1]] : all;
  return table(all.length > 12 ? `Rank values · ${all.length} rows, three of them` : "Rank values",
    shown.map((r: any) => {
      const values = r.values && typeof r.values === "object" ? r.values : r;
      const said = Object.entries(values)
        .filter(([k, v]) => k !== "rank" && k !== "level" && (typeof v === "number" || Array.isArray(v)))
        .slice(0, 3)
        .map(([k, v]) => `${k.replace(/_/g, " ")} ${Array.isArray(v) ? range(v[0], v[1]) : num(v)}`)
        .join(" · ");
      return row(`rank ${num(r.rank ?? r.level)}`, said);
    }).join(""));
}

/** The upgrade pairs a Diablo IV skill carries: choose one of each. */
function upgrades(rec: any): string {
  const all = (rec.upgrades || []).filter((u: any) => u && typeof u === "object");
  if (!all.length) return "";
  return table("Upgrade pairs · choose one of each",
    all.map((u: any) => row(u.name || u.id, u.summary || "")).join(""));
}

function statsOf(rec: any): string {
  const all = (rec.stats || []).filter((s: any) => s && typeof s === "object");
  if (!Array.isArray(all) || !all.length) return "";
  return table("Stats", all.map((s: any) => row(s.stat || s.text || "", s.display || range(s.min, s.max) || num(s.value))).join(""));
}

const chips = (head: string, links: any[]) => links.length
  ? `<div class="rc-part"><p class="gd-eyebrow">${escape(head)}</p><p class="rc-chips">${links.slice(0, 24)
      .map((l) => `<span class="rc-chip">${escape(l.name || l.id)}</span>`).join("")}</p></div>`
  : "";

export function drawRecord(rec: any, pack: { researched_at?: string } | null): string {
  const facts = [
    rec.level_req != null ? row("Level", num(rec.level_req)) : "",
    rec.slot_id ? row("Slot", String(rec.slot_id).replace(/-/g, " ")) : "",
    rec.group ? row("Cluster", rec.group) : "",
    rec.cost ? row("Cost", typeof rec.cost === "object" ? `${num(rec.cost.amount)} ${rec.cost.resource || ""}`.trim() : String(rec.cost)) : "",
    rec.cooldown ? row("Cooldown", String(typeof rec.cooldown === "object" ? JSON.stringify(rec.cooldown) : rec.cooldown)) : "",
    rec.max_rank ? row("Ranks", num(rec.max_rank)) : "",
  ].join("");
  const out = (rec.links || []).filter((l: any) => l.rel !== "of");
  const into = (rec.linked_from || []).filter((l: any) => l.rel !== "of");
  return `
    <div class="rc-head">
      <span class="gd-eyebrow">${escape([rec.sub || rec.kind, rec.slot_id].filter(Boolean).join(" · "))}</span>
      <h3 class="gd-h3">${escape(rec.name || rec.id)}</h3>
      ${rec.summary ? `<p class="gd-soft">${escape(rec.summary)}</p>` : ""}
    </div>
    ${facts ? `<div class="rc-part">${facts}</div>` : ""}
    ${lines(rec)}${statsOf(rec)}${tiers(rec)}${ranks(rec)}${upgrades(rec)}
    ${chips("Points at", out)}${chips("Pointed at by", into)}
    <p class="gd-hint">from the game's data files${pack?.researched_at ? ` · gathered ${escape(pack.researched_at)}` : ""}</p>`;
}
