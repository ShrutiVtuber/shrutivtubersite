/** An eyebrow that opens a section, with an optional action and an optional
 * gilt rule beneath. Sentence case in the title; the eyebrow is uppercased by CSS. */
export interface SectionHeaderProps {
  eyebrow?: string;
  title?: string;
  /** Text of the right-hand action, e.g. "See all". */
  action?: string;
  onAction?: () => void;
  /** Close the header with a hairline rule carrying a mark. */
  rule?: boolean;
  /** The mark inside the rule; defaults to ☾. */
  mark?: string;
}
export declare function SectionHeader(props: SectionHeaderProps): JSX.Element;
