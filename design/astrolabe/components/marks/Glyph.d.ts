/** An astronomical mark set in the bundled AstroSymbols cut (29 glyphs).
 * Type, never emoji: the character is emitted with U+FE0E so no colour-emoji
 * font can claim it. Use for planets, signs, nodes, ℞, degrees.
 */
export interface GlyphProps {
  /** Key into MARKS: sun|moon|mercury|venus|mars|jupiter|saturn|uranus|neptune|pluto|node|southnode|retrograde|degree|aries…pisces */
  name?: string;
  /** A literal character, when it is not in MARKS. U+FE0E is appended for you. */
  char?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | number;
  tone?: 'ink' | 'soft' | 'faint' | 'gilt' | 'accent' | 'rose' | 'hour' | 'live' | 'inherit';
  /** Accessible name. Omit and the glyph is aria-hidden — correct when the text beside it already says it. */
  label?: string;
  style?: React.CSSProperties;
}
export declare function Glyph(props: GlyphProps): JSX.Element;
export declare const MARKS: Record<string, string>;
