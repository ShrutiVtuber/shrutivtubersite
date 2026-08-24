/** Labelled text input with hint / error / success lines. Error is never colour-alone. */
export interface TextFieldProps {
  label: React.ReactNode;
  hint?: React.ReactNode;
  /** Shows the ✕ error line and invalid border */
  error?: React.ReactNode;
  /** Shows the ✓ confirmation line */
  success?: React.ReactNode;
  required?: boolean;
  /** Show an "optional" tag when not required */
  optionalLabel?: boolean;
  disabled?: boolean;
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: any) => void;
}
