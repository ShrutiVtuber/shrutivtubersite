/** An authored empty state. Quiet and honest — never a shrug, never a fake.
 * ⚠ The drawing is optional and its absence is designed: with no art the mark
 * ring holds the same height, so the screen does not reflow when her artwork lands.
 */
export interface EmptyStateProps {
  /** An AstroSymbols character for the ring. Default ☾. */
  mark?: string;
  /** Her drawing, when one exists for this state. */
  art?: string;
  artAlt?: string;
  title?: string;
  body?: string;
  action?: React.ReactNode;
  secondary?: React.ReactNode;
  compact?: boolean;
}
export declare function EmptyState(props: EmptyStateProps): JSX.Element;
