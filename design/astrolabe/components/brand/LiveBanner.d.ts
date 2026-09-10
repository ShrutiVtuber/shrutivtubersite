/** Live is a state the app is IN, not a badge on a card.
 * live — the plate warms, the hem goes rose, the dot pulses.
 * offline — a quiet line with the next stream if one is known.
 * unknown — her side was unreachable. Never says "offline", never fakes liveness.
 * Stamp data-live="true" on the shell to turn the whole app's ornament rose.
 */
export interface LiveBannerProps {
  status?: 'live' | 'offline' | 'unknown';
  /** The stream's title when live. */
  title?: string;
  game?: string;
  viewers?: number;
  /** e.g. "Thursday 20:00 Athens" — shown when offline and known. */
  nextStream?: string;
  onOpen?: () => void;
  compact?: boolean;
}
export declare function LiveBanner(props: LiveBannerProps): JSX.Element;
