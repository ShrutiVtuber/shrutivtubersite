/** An inline notice pinned under the app bar.
 * ⚠ offline does NOT mean broken. Every instrument still computes on device; only
 * her half — live status, readings, articles, offers, the practice room — is out
 * of reach. The copy must say which half is missing, never "no connection". */
export interface BannerProps {
  tone?: 'offline' | 'error' | 'note' | 'caution';
  title?: string;
  children?: React.ReactNode;
  action?: string;
  onAction?: () => void;
  onDismiss?: () => void;
  /** Override the tone's icon. */
  icon?: string;
}
export declare function Banner(props: BannerProps): JSX.Element;
