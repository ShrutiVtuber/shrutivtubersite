/** The next station, with a live countdown. Reused on the solar tracker, the lunar tracker and
 * Day at a Glance — someone opening any of them at four in the afternoon wants "sunset in 2h 14m"
 * before they want a table. */
export interface NextStationProps {
  /** e.g. 'Sunset', 'Moonrise', 'Hour of Mercury' */
  name: string;
  /** Glyph set as type, e.g. '☉' — pass with U+FE0E where the character defaults to emoji */
  glyph?: string;
  /** Local clock time of the station, e.g. '20:05' */
  at: string;
  /** Preformatted remaining time, e.g. '2h 14m' */
  inLabel: string;
  /** The station currently in force, e.g. 'Noon — since 13:29' */
  currentName?: string;
  currentSince?: string;
  /** Preset attribution, e.g. 'Hekate Enodia' — omitted when the preset is 'none' */
  attribution?: string;
  /** 0–1, drives the hairline progress rule between current and next */
  progress?: number;
  /** 'hero' on the tracker pages, 'block' inside Day at a Glance */
  size?: 'hero' | 'block';
  /** When the station cannot be computed at all — polar latitude */
  undefinedReason?: React.ReactNode;
}
