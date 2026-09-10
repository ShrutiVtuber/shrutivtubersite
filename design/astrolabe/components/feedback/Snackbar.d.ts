/** A snackbar: something happened, here is the undo. Sits above the tab bar,
 * never over it. One at a time, ~4s, and it never carries an error that a screen
 * should be showing inline. */
export interface SnackbarProps {
  open?: boolean;
  children?: React.ReactNode;
  action?: string;
  onAction?: () => void;
  tone?: 'neutral' | 'good' | 'error';
  /** Lift above the tab bar. Default true. */
  above?: boolean;
}
export declare function Snackbar(props: SnackbarProps): JSX.Element;
