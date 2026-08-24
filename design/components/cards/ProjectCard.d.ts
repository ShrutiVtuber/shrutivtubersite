/** An instrument in the portfolio — Theourgia, BeeRanked, and what follows. */
export interface ProjectCardProps {
  name: string;
  /** One italic line under the name */
  tagline?: string;
  description?: string;
  status?: 'active' | 'maintained' | 'archived';
  repoHref?: string;
  liveHref?: string;
  /** Nullable — absent shows the sky with a "screenshot pending" plate */
  screenshot?: string | null;
  /** Mono footnote, e.g. "AGPL-3.0 · self-hosted · federation" */
  meta?: string;
}
