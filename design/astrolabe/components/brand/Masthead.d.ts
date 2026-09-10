/** Home's one brand surface: cloak navy, a thin scatter of stars, a gold hem,
 * and a slot for her portrait.
 * ⚠ Art-absent is a designed state, not a fallback — with no portrait the plate
 * keeps its proportions and the greeting takes the width, so the app looks
 * finished before a single drawing arrives.
 */
export interface MastheadProps {
  /** e.g. "Good evening" — written for the hour, on device. */
  greeting: string;
  /** One line under it: the sky's state in her voice. */
  line?: string;
  /** Portrait PNG (transparent, bottom-anchored). Omit for the art-absent state. */
  portrait?: string;
  portraitAlt?: string;
  /** Warms the plate and turns the hem rose. */
  live?: boolean;
  /** Chips or a LiveBanner slotted under the greeting. */
  children?: React.ReactNode;
  height?: number;
}
export declare function Masthead(props: MastheadProps): JSX.Element;
