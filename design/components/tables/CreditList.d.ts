/** Typographically dignified credits — never a footnote. */
export interface CreditListProps {
  credits: Array<{ role: string; name: string; href?: string; note?: string }>;
  dense?: boolean;
}
