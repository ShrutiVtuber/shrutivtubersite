/** Multi-line field; same validation grammar as TextField, plus an optional character count. */
export interface TextAreaProps {
  label: React.ReactNode;
  hint?: React.ReactNode;
  error?: React.ReactNode;
  success?: React.ReactNode;
  required?: boolean;
  optionalLabel?: boolean;
  disabled?: boolean;
  rows?: number;
  /** With a controlled `value`, renders a tabular character count */
  maxLength?: number;
  value?: string;
  onChange?: (e: any) => void;
  placeholder?: string;
}
