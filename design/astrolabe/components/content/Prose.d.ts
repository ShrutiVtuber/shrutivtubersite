/** Long-form: a reading, an article, a licence. EB Garamond at 17/1.65 with a
 * 38em measure, because these are read on a phone in bed. Glyphs inside prose keep
 * their AstroSymbols face; blockquotes take a gilt hairline, not a box. */
export interface ProseProps {
  children?: React.ReactNode;
  size?: 'prose' | 'small';
  /** A gilt drop capital on the first paragraph — her readings only, never articles. */
  drop?: boolean;
}
export declare function Prose(props: ProseProps): JSX.Element;
