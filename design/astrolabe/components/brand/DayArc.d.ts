/** The day, drawn: sunrise to sunset as an arc, the Sun where it actually is,
 * the Moon's phase at the end of it. Sky's header.
 *
 * It exists for two reasons. The app knows what the sky is doing, on device and
 * offline, which is a signal almost no app has. And it stops every screen looking
 * like the same stack of cards — Home has the plate, Sky has the arc, and neither
 * borrows the other's surface.
 *
 * All four inputs are real values; nothing in the drawing is decorative. */
export interface DayArcProps {
  /** "HH:MM", local. */
  sunrise?: string;
  sunset?: string;
  /** "HH:MM" now. Outside sunrise–sunset the Sun is simply not drawn. */
  now?: string;
  /** 0 new · 0.5 full. */
  phase?: number;
  /** Ruler of the current planetary hour — tints the hem and the mark. */
  ruler?: 'sun' | 'moon' | 'mars' | 'mercury' | 'jupiter' | 'venus' | 'saturn';
  height?: number;
  /** Overrides the generated accessible description. */
  label?: string;
}
export declare function DayArc(props: DayArcProps): JSX.Element;
