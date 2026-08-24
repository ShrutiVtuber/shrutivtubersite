/** Rendered-markdown typography — the journal spec BeeRanked must match. */
export interface ProseProps {
  children?: React.ReactNode;
  /** Pre-rendered HTML alternative to children */
  html?: string;
  /** Content language, e.g. "el", "hi", "fr" */
  lang?: string;
  /** Signature line, e.g. "Soror Eu. A." — rendered as the ruled seal */
  byline?: string;
  className?: string;
  style?: any;
}
