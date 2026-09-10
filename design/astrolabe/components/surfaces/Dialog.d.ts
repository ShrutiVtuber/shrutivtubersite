/** Two dialogs.
 * small — a confirm: one question, two buttons, the destructive one outlined.
 * fullscreen — the sky drawer: reference material that wants the whole screen but
 * is not a place in the app, so it closes rather than pops. */
export interface DialogProps {
  open?: boolean;
  size?: 'small' | 'fullscreen';
  title: string;
  subtitle?: string;
  onClose?: () => void;
  actions?: React.ReactNode;
  children?: React.ReactNode;
}
export declare function Dialog(props: DialogProps): JSX.Element;
