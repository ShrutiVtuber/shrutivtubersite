/* The Play hub's data: which games the wing covers, and where a signed-in
 * reader left off in each room (handoff 26 Sep 2026, README §2–4).
 *
 * Nothing here is sample data. The index is assembled from what each room
 * already serves — the games with a published guide, the planner packs that
 * are loaded, the Ledger's pack — and "where you left off" is the reader's own
 * most recently touched item, read through the same endpoints the rooms read.
 *
 * ⚠ Server only: it imports lib/api.ts, which reads the environment.
 */
import { site } from "./api";
import { asReader } from "./account";
import { loadPack } from "./ledger/data";

/* The games a build planner is written for. Mirrors RECIPES in
 * backend/shrutisguides/gamedata/recipes.py (checked by
 * backend/tests/test_the_play_hub_reads_real_data.py). Listed here rather than
 * read, because a planner whose data is not loaded is absent from
 * /api/gamedata/games — and the hub has to say "data not loaded yet" for it,
 * which it can only do if it knows the planner exists. The names are
 * fallbacks: a loaded pack's own name wins. */
export const PLANNER_GAMES: { id: string; name: string }[] = [
  { id: "diablo-iv", name: "Diablo IV" },
  { id: "path-of-exile-2", name: "Path of Exile 2" },
  { id: "diablo-ii-resurrected", name: "Diablo II: Resurrected" },
];

/* The Ledger is for one game. Its slug is the one the guide tracker already
 * maps to the Ledger theme (pages/guides/[game]/[slug]/track.astro). */
export const LEDGER_GAME = { id: "big-ambitions", name: "Big Ambitions" };

/* The overlay theme a game wears by default, and which room it belongs to.
 * Grimoire is the Diablo IV theme (admin overlays, the Ledger's theme notes);
 * Ledger is Big Ambitions'. A game with no entry wears the house theme and the
 * index says nothing about it. */
export const GAME_THEMES: Record<string, { theme: "grimoire" | "ledger"; room: "builds" | "ledger" }> = {
  "diablo-iv": { theme: "grimoire", room: "builds" },
  "big-ambitions": { theme: "ledger", room: "ledger" },
};

/* An editorial order, never a popular one: the games the rooms were built
 * for, as the handoff lists them. Any other game with a guide follows by name. */
export const GAME_ORDER = ["diablo-iv", "big-ambitions", "path-of-exile-2", "diablo-ii-resurrected"];

export interface GuideGame { slug: string; name: string; guides: number }
export interface PlannerPack { id: string; name: string; planner: boolean }

export interface WingData {
  guideGames: GuideGame[];
  packs: PlannerPack[];
  ledgerLoaded: boolean;
  ledgerName: string | null;
}

/** What the index is built from. Every read degrades to "nothing" rather than throwing. */
export async function wingData(): Promise<WingData> {
  const [guideGames, packs, pack] = await Promise.all([
    site<GuideGame[]>("/api/guides/games"),
    site<PlannerPack[]>("/api/gamedata/games"),
    /* Kept a minute in-process by loadPack, so the hub does not pull the
       385 KB pack on every render. */
    loadPack(),
  ]);
  return {
    guideGames: (Array.isArray(guideGames) ? guideGames : []).filter((g) => g && g.slug && g.guides > 0),
    packs: Array.isArray(packs) ? packs.filter((p) => p && p.id) : [],
    ledgerLoaded: !!pack,
    ledgerName: pack?.game?.name ?? null,
  };
}

export interface LeftOff { name: string; href: string }

const list = (r: { ok: boolean; body: any } | null): any[] => (r?.ok && Array.isArray(r.body) ? r.body : []);
const newest = <T extends { updatedAt?: string | null }>(rows: T[]): T | undefined =>
  [...rows].sort((a, b) => String(b.updatedAt ?? "").localeCompare(String(a.updatedAt ?? "")))[0];

/**
 * The reader's most recently touched item in each room: a name and a link,
 * nothing else — no count, no date, no progress. A room with nothing to return
 * to is absent from the answer. Asked only for rooms that are on the page.
 */
export async function leftOff(astro: any, rooms: { guides: boolean; ledger: boolean; builds: boolean; groups: boolean }): Promise<Record<string, LeftOff>> {
  const none = Promise.resolve(null);
  const [runs, ledgers, builds, groups] = await Promise.all([
    rooms.guides ? asReader(astro, "/api/runs") : none,       // newest first (updated_at desc)
    rooms.ledger ? asReader(astro, "/api/ledger/ledgers") : none, // by position; recency picked below
    rooms.builds ? asReader(astro, "/api/builds") : none,     // newest first (updated_at desc)
    rooms.groups ? asReader(astro, "/api/groups/mine") : none, // newest first (updated_at desc)
  ]);
  const out: Record<string, LeftOff> = {};

  const run = newest(list(runs));
  if (run?.guide?.slug && run.guide.game?.slug) {
    const title = String(run.guide.title || "");
    const name = String(run.name || "").trim();
    out.guides = {
      name: name && name !== title ? `${title} · ${name}` : title || name,
      href: `/guides/${run.guide.game.slug}/${run.guide.slug}/track?run=${run.id}`,
    };
  }
  const ledger = newest(list(ledgers));
  if (ledger?.id != null && ledger.name) out.ledger = { name: String(ledger.name), href: `/ledger/${ledger.id}` };
  const build = newest(list(builds));
  if (build?.id != null && build.name) out.builds = { name: String(build.name), href: `/builds/${build.id}` };
  /* A group's view carries no timestamp; /mine is already newest first. */
  const group = list(groups)[0];
  if (group?.code && group.name) out.groups = { name: String(group.name), href: `/groups/${group.code}` };
  return out;
}
