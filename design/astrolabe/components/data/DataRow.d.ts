/** A label and a value joined by an almanac dotted leader. Used wherever the app
 * states a fact: chart data, place, provenance, a licence version. */
export interface DataRowProps {
  label: string;
  value: React.ReactNode;
  /** An AstroSymbols character before the label. */
  mark?: string;
  leader?: boolean;
  mono?: boolean;
  tone?: 'ink' | 'soft' | 'faint' | 'rose' | 'accent' | 'gilt';
  small?: boolean;
}
export declare function DataRow(props: DataRowProps): JSX.Element;
