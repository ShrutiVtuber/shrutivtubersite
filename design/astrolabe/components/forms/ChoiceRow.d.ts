/** One row of a choice: a radio (pick one — the sunrise convention) or a
 * checkbox (a consent). Both carry an optional `rule` line, because the app's
 * disagreement controls are never bare labels: each option states the rule it
 * applies, and neither option is defaulted-correct.
 * ⚠ Consents are never pre-ticked and never bundled — one row, one decision. */
export interface ChoiceRowProps {
  type?: 'radio' | 'checkbox';
  label: string;
  /** The one-line rule this option applies. */
  rule?: string;
  checked?: boolean;
  disabled?: boolean;
  name?: string;
  value?: string;
  onChange?: (value: string | boolean) => void;
}
export declare function ChoiceRow(props: ChoiceRowProps): JSX.Element;
