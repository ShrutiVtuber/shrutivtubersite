/** The drawn moon phase disc. Correct for any fraction of the cycle and legible at 16px.
 * Colour is never the only signal: it always carries an accessible phase name.
 */
export interface MoonDiscProps {
  /** 0 new · 0.25 first quarter · 0.5 full · 0.75 last quarter */
  phase?: number;
  size?: number;
  /** Overrides the computed phase name. */
  label?: string;
  /** Show the phase name beside the disc. */
  showLabel?: boolean;
  tone?: 'gilt' | 'ink' | 'soft' | string;
}
export declare function MoonDisc(props: MoonDiscProps): JSX.Element;
export declare function phaseName(p: number): string;
