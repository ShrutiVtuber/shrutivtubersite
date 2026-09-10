/** A UI icon: Material Symbols Outlined, the set the Flutter app already draws.
 * Kept rather than substituted — Apache-2.0, so it is AGPL-safe, and it costs the bundle nothing. */
export interface IconProps {
  /** Material Symbols name, e.g. "chevron_right", "cloud_off", "clear_night". */
  name: string;
  size?: number;
  tone?: 'ink' | 'soft' | 'faint' | 'gilt' | 'accent' | 'rose' | 'live' | 'hour' | 'inherit';
  /** 0 outlined (default), 1 filled — filled marks the selected tab only. */
  fill?: 0 | 1;
  weight?: number;
  /** Accessible name; omit for decorative icons that sit beside their own label. */
  label?: string;
  style?: React.CSSProperties;
}
export declare function Icon(props: IconProps): JSX.Element;
