/** Two or three segments, never more — beyond three it is a tab bar or a list.
 * Sky uses three (Stations · Hours · Coming); Letters uses two (Reckoning · Sigil). */
export interface SegmentedControlProps {
  segments: ({ id: string; label: string } | string)[];
  active: string;
  onChange?: (id: string) => void;
  /** Accessible name for the tablist. */
  label?: string;
}
export declare function SegmentedControl(props: SegmentedControlProps): JSX.Element;
