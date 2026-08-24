/* Reading the stored sky for journal entries.
 *
 * The entries live in BeeRanked; this fetches only the half BeeRanked cannot
 * know. Batched on purpose — the whole point of storing these is that an index
 * of twenty entries does not cast twenty charts, and fetching them one at a
 * time would give that back.
 */
import { site } from "./api";
import type { Sky } from "../components/content/JournalSky.astro";

export async function skyFor(slug: string): Promise<Sky | null> {
  return site<Sky>(`/api/journal/sky/${encodeURIComponent(slug)}`);
}

export async function skiesFor(slugs: string[]): Promise<Record<string, Sky>> {
  if (slugs.length === 0) return {};
  const data = await site<{ skies: Record<string, Sky> }>(
    `/api/journal/skies?slugs=${encodeURIComponent(slugs.join(","))}`,
  );
  return data?.skies ?? {};
}
