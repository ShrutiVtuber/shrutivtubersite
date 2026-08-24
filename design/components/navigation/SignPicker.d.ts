/** The twelve signs as a primary control — the fastest path for someone arriving from search.
 * Remembers the reader's choice; a signed-in reader with a saved nativity gets theirs preselected
 * and does not have to pick at all. */
export interface SignPickerProps {
  /** Lowercase latin key, e.g. 'virgo' */
  current?: string | null;
  /** Button mode */
  onChange?: (sign: string) => void;
  /** Link mode: URL for a sign */
  hrefFor?: (sign: string) => string;
  /** Marks the sign derived from the reader's saved nativity */
  ownSign?: string | null;
  /** 'grid' = the /horoscopes index (12 tiles), 'row' = compact strip on a reading page */
  layout?: 'grid' | 'row';
}
