/* Where this site's own source is, and which build is answering.
 *
 * **This is a licence obligation, not a credit.** Every source file here
 * carries `AGPL-3.0-only`, and section 13 of that licence says that software
 * people interact with over a network must offer them its Corresponding
 * Source. A link in the footer is how that offer is made; without one the site
 * is running under terms it is not honouring.
 *
 * The holding page already made this offer for `shruti-astro`, the ephemeris —
 * and only for it. The daemon is a separate program under the same licence, so
 * that line was right and incomplete: it covered the thing doing the
 * arithmetic and not the thing the visitor was actually looking at.
 *
 * `SHRUTI_SOURCE_SHA` is optional and the offer stands without it. When the
 * deploy sets it the link names the exact commit that answered, which is what
 * "Corresponding Source" means literally; when it does not, the branch is
 * still an honest answer as long as deploys come from it. The wording never
 * claims more than it has.
 */
import { env } from "./env";

/** The repository. Overridable, because a project can move host. */
export const SOURCE_URL: string = env(
  "SHRUTI_SOURCE_URL",
  "https://github.com/ShrutiVtuber/shrutivtubersite",
);

/** The deployed commit, when the deploy troubles to say. */
export const SOURCE_SHA: string = env("SHRUTI_SOURCE_SHA");

/** The licence these terms come from, for linking. */
export const LICENCE_URL = "https://www.gnu.org/licenses/agpl-3.0.html";

/**
 * A link to the source of the build that is answering.
 *
 * Points at the exact commit when one is known, and at the repository when it
 * is not — never at a commit that might not be the one running.
 */
export function sourceHref(): string {
  const sha = SOURCE_SHA.trim();
  if (!sha || sha === "dev") return SOURCE_URL;
  return `${SOURCE_URL.replace(/\/+$/, "")}/tree/${sha}`;
}

/** The short commit, for showing beside the link. Empty when unknown. */
export function sourceBuild(): string {
  const sha = SOURCE_SHA.trim();
  return !sha || sha === "dev" ? "" : sha.slice(0, 7);
}
