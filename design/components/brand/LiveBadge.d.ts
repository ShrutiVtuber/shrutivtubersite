/** The stream-status moment. Fixed 40px min-height — no layout shift between states.
 * Meaning is carried by the word, never colour alone. */
export interface LiveBadgeProps {
  /** 'unknown' is the API-failed state: it never claims live OR offline */
  status: 'live' | 'offline' | 'unknown';
  /** Stream title (live only) */
  title?: string;
  /** Game / category (live only) */
  game?: string;
  /** Viewer count (live only) */
  viewers?: number;
  /** Human-readable next stream, e.g. "Thu 21:00" (offline only) */
  nextStream?: string;
  /** Wrap in a link, e.g. to Twitch */
  href?: string;
  /** Dot + word only */
  compact?: boolean;
}
