/** Buttons — blue is interactive. `live` variant is reserved for the watch-live CTA. */
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'live';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  /** Shows a spinner, hides the label, sets aria-busy */
  loading?: boolean;
  /** Renders an <a> */
  href?: string;
  type?: 'button' | 'submit';
  onClick?: (e: any) => void;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  children: React.ReactNode;
}
