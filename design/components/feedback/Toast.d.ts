/** Floating notice — info (☾), success (✓), error (✕). Tone is word+glyph, never colour alone. */
export interface ToastProps {
  tone?: 'info' | 'success' | 'error';
  title: React.ReactNode;
  body?: React.ReactNode;
  /** e.g. a ghost Button ("Undo") */
  action?: React.ReactNode;
  /** Renders the dismiss ✕ */
  onDismiss?: () => void;
}
