/** Press-kit numeral — serif tabular value, uppercase label, optional note and rose glyph. */
export interface StatBlockProps {
  /** Preformatted, e.g. "1.2k", "38%" */
  value: React.ReactNode;
  label: string;
  /** e.g. "past 90 days" */
  note?: string;
  /** Rose ornament, e.g. "☾" */
  glyph?: string;
}
