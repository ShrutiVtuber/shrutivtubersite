/** A row in a list: settings, places, licences, a pushed destination.
 * 56px minimum. Wrap rows in ListGroup for hairline separation on a card. */
export interface ListRowProps {
  label: string;
  description?: string;
  /** Right-aligned current value, e.g. "Athens, Greece". */
  value?: string;
  leading?: React.ReactNode;
  /** Replaces the chevron — a Switch, a Chip, a count. */
  trailing?: React.ReactNode;
  chevron?: boolean;
  /** The one row that deletes something. */
  danger?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  href?: string;
  external?: boolean;
}
export declare function ListRow(props: ListRowProps): JSX.Element;
export declare function ListGroup(props: { children: React.ReactNode; inset?: boolean }): JSX.Element;
