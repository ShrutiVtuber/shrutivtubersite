/** Authored quiet-state — dashed field, moon-phase glyph, honest copy. */
export interface EmptyStateProps {
  /** Astronomical glyph, default "○" (new moon) */
  glyph?: string;
  title: React.ReactNode;
  body?: React.ReactNode;
  action?: React.ReactNode;
  compact?: boolean;
}
