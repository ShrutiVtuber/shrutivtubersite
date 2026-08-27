/* Editable strings, with the page's own words as the default.
 *
 * Page blocks are sections — eyebrow, heading, prose, a link. Most of the
 * words on this site are not sections: they are the line under a form, the
 * label on a button, the sentence saying why a field is optional. Those lived
 * in templates, which meant about six thousand words she could not touch
 * without a deploy, on a site whose whole premise is that she edits it.
 *
 * The rule that makes this safe to adopt one page at a time:
 *
 *   **The default lives in the template and always renders.** A row only ever
 *   overrides it. An empty table renders a complete site; a page nobody has
 *   seeded reads exactly as it was written; and a string she has never touched
 *   cannot go missing because a query failed.
 *
 * So a page reads:
 *
 *   const say = await copy("support");
 *   <p>{say("tiers.note", "Every tier is monthly and cancels in one click.")}</p>
 *
 * and `npm run copy:seed` (scripts/seed-copy.mjs) reads those same calls back
 * out of the source to register them in the admin. The template is the source
 * of truth for WHICH strings exist; the database is the source of truth for
 * what they say.
 */
import { SITE_API } from "./api";

/* The third argument is what the ADMIN calls this string. It is never
   rendered — the seeder reads it out of the source so she gets "Button on the
   one-off card" instead of "oneoff.cta". Optional, because most keys read
   fine on their own. */
export type Copy = (key: string, fallback: string, label?: string) => string;

/**
 * One page's overrides, as a function that falls back to the written words.
 *
 * Never throws and never returns nothing. A backend that is down means the
 * page renders what it was written with, which is a correct page — not an
 * error, and not a hole where a sentence should be.
 */
export async function copy(page: string): Promise<Copy> {
  let overrides: Record<string, string> = {};
  try {
    const r = await fetch(`${SITE_API}/api/content/copy/${page}`);
    if (r.ok) overrides = (await r.json())?.copy ?? {};
  } catch {
    /* The written words stand. */
  }

  return (key: string, fallback: string, _label?: string) =>
    /* `in` rather than truthiness: a row set to an empty string is a
       deliberate blank — she deleted the sentence — and falling back to the
       default there would make it impossible to remove a line. Deleting the
       row is how you go back, and the admin offers exactly that. */
    key in overrides ? overrides[key] : fallback;
}
