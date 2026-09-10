/** Monospace-ish block: isopsephy tables, offer codes, the wheel's SVG source.
 * The app ships no mono face, so this is Commissioner locked to tabular figures
 * with extra tracking — close enough to read as data, and free. */
export interface CodeBlockProps {
  children?: React.ReactNode;
  label?: string;
  copyable?: boolean;
  onCopy?: () => void;
  wrap?: boolean;
  align?: 'left' | 'right' | 'center';
}
export declare function CodeBlock(props: CodeBlockProps): JSX.Element;
