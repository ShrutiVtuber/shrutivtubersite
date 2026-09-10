/** A tap target with an icon in it. Always at least 48px even when the glyph is
 * 20px — the ring is the target, not the glyph. `label` is required: it is the
 * only name a screen reader gets. */
export interface IconButtonProps {
  /** Material Symbols name. */
  icon: string;
  /** Required accessible name. */
  label: string;
  size?: number;
  variant?: 'ghost' | 'outlined' | 'filled';
  tone?: 'ink' | 'soft' | 'faint' | 'accent' | 'gilt' | 'rose' | 'live';
  selected?: boolean;
  disabled?: boolean;
  /** A count in the corner; used on the notifications action. */
  badge?: number | string;
  onClick?: () => void;
  href?: string;
}
export declare function IconButton(props: IconButtonProps): JSX.Element;
