/** Days down, stations across. The primary reading on both tracker pages, and it gets printed.
 * A missing station is never a blank cell — the Moon does not rise every day, and that is a fact
 * about the sky rather than missing data. */
export interface StationTableProps {
  /** Column headers, in order — e.g. ['Sunrise','Noon','Sunset','Midnight'] */
  stations: string[];
  /** Glyph per column, set as type; pass U+FE0E where the character defaults to emoji */
  glyphs?: string[];
  /** Preset attribution per column, e.g. ['Hekate Phosphoros','Apollo',…]; omitted when preset is none */
  attributions?: string[];
  /** One entry per day. `times` is parallel to `stations`; use null for a station that does not
   *  occur that day — the cell renders the designed absent state, never a blank. */
  rows: Array<{
    date: string;
    weekday?: string;
    times: Array<string | null>;
    /** Renders the row as today */
    today?: boolean;
    /** Index of the station currently in force (today's row only) */
    currentIndex?: number;
    /** Moon phase + age, lunar table only, e.g. '◐ 11.4 d' */
    phase?: string;
  }>;
  /** Text for a null cell, e.g. 'no moonrise' */
  absentLabel?: string;
  /** Whole-table cannot-compute state — polar latitude */
  undefinedReason?: React.ReactNode;
  caption?: React.ReactNode;
}
