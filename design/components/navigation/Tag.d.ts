/** Journal topic tag / filter pill. */
export interface TagProps {
  label: string;
  /** Link mode */
  href?: string;
  /** Selected filter state */
  active?: boolean;
  /** Post count, mono */
  count?: number;
  onClick?: () => void;
}
