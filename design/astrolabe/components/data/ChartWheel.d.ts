/** The wheel. The thing worth screenshotting, and the only drawing in the app
 * the design system makes itself — it is an instrument, not artwork.
 * ⚠ With no birth time the angles are undefined: pass housesKnown={false} and the
 * wheel drops the house ring and the ASC/MC marks rather than guessing them.
 */
export interface WheelBody { name: string; mark: string; lon: number; retro?: boolean }
export interface WheelAspect { from: number; to: number; type: 'conjunction'|'opposition'|'trine'|'square'|'sextile'; applying?: boolean }
export interface ChartWheelProps {
  /** transit — one instant · period — movement across a span, with the Moon's phase ring outside. */
  mode?: 'transit' | 'period';
  size?: number;
  bodies?: WheelBody[];
  aspects?: WheelAspect[];
  /** Twelve house cusps in ecliptic longitude. Omit when houses are unknown. */
  cusps?: number[];
  asc?: number;
  mc?: number;
  housesKnown?: boolean;
  /** Period mode: phase discs around the rim, { lon, phase }. */
  phases?: { lon: number; phase: number }[];
  /** Period mode: the span, printed at the centre. */
  span?: string;
  label?: string;
}
export declare function ChartWheel(props: ChartWheelProps): JSX.Element;
export declare const SIGNS: string[];
export declare const SIGN_NAMES: string[];
