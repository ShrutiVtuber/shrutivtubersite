/** Almanac-style section opener: eyebrow label, display title, optional body and action. */
export interface SectionHeaderProps {
  /** Small uppercase label above the title */
  eyebrow?: string;
  title: React.ReactNode;
  /** One supporting sentence */
  body?: React.ReactNode;
  /** Optional action (e.g. a ghost Button) rendered under the body */
  action?: React.ReactNode;
  align?: 'left' | 'center';
  /** Astronomical ornament rendered before the eyebrow, e.g. "☾" */
  glyph?: string;
  /** Heading element, default h2 */
  as?: 'h1' | 'h2' | 'h3';
}
