/** The app's button. Filled is the one action a screen is for; outlined is the
 * alternative; text is everything else. Destructive is outlined by default —
 * nothing irreversible gets a filled button. Press deepens and sinks 1px; it
 * never scales.
 */
export interface ButtonProps {
  variant?: 'filled' | 'outlined' | 'text';
  size?: 'sm' | 'md' | 'lg';
  /** Rose instead of blue. Pair with variant="outlined" unless it is the screen's only action. */
  destructive?: boolean;
  disabled?: boolean;
  loading?: boolean;
  full?: boolean;
  /** Leaves the app — appends the ↗ mark and opens in a browser. Required for anything that takes money. */
  external?: boolean;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  href?: string;
  onClick?: (e: React.MouseEvent) => void;
  children?: React.ReactNode;
}
export declare function Button(props: ButtonProps): JSX.Element;
