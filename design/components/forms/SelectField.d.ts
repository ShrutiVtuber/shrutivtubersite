/** Native select styled to the field grammar, with a typographic ▾ chevron. */
export interface SelectFieldProps {
  label: React.ReactNode;
  options: Array<string | { value: string; label: string }>;
  /** Disabled first option shown until a choice is made */
  placeholder?: string;
  hint?: React.ReactNode;
  error?: React.ReactNode;
  required?: boolean;
  disabled?: boolean;
  value?: string;
  onChange?: (e: any) => void;
}
