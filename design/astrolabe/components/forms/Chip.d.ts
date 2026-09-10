/** Chips. Three kinds, and they do not mix on one row.
 * choice — pick one of a set (sign, house system, ayanāṁśa)
 * filter — pick any number; selected carries a tick as well as a tint
 * meta — not interactive; a fact with a size on it (language packs) */
export interface ChipProps {
  kind?: 'choice' | 'filter' | 'meta';
  selected?: boolean;
  disabled?: boolean;
  leading?: React.ReactNode;
  trailing?: React.ReactNode;
  /** Right-hand figure, e.g. "2.1 MB" or a count. */
  meta?: string;
  onClick?: () => void;
  children?: React.ReactNode;
}
export declare function Chip(props: ChipProps): JSX.Element;
