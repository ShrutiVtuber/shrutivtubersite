/** A reference table.
 * ⚠ Dense on purpose — a practitioner reading a month wants the month on one
 * screen, so rows are ~30px and figures are 13px tabular. Do not make it airy.
 * Retrograde is ℞ AND a rose tint; today is a wash AND the word "today".
 */
export interface DataColumn {
  key: string;
  label: string;
  /** An AstroSymbols character above the label. */
  mark?: string;
  align?: 'left' | 'right' | 'center';
  width?: number | string;
  numeric?: boolean;
}
export interface DataCell { value: React.ReactNode; retro?: boolean; muted?: boolean; strong?: boolean }
export interface DataTableProps {
  columns: DataColumn[];
  /** Each row is keyed by column key; a value may be a plain value or a DataCell. `today` washes the row. */
  rows: (Record<string, any> & { id?: string; today?: boolean })[];
  caption?: string;
  stickyHead?: boolean;
  zebra?: boolean;
  onRowClick?: (row: any) => void;
  /** What an absent value reads as. Default "—". */
  emptyLabel?: string;
}
export declare function DataTable(props: DataTableProps): JSX.Element;
