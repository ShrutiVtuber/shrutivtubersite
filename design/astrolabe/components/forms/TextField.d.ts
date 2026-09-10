/** A text field. Inset well, hairline, label above — not a floating label:
 * birth data and a 2,000-word reading both go in here and the label must stay put.
 * An error is a message AND a colour AND the word "Error"; never colour alone. */
export interface TextFieldProps {
  label?: string;
  value?: string;
  defaultValue?: string;
  placeholder?: string;
  helper?: string;
  /** Replaces helper, turns the well rose, and prefixes the word "Error". */
  error?: string;
  multiline?: boolean;
  rows?: number;
  disabled?: boolean;
  required?: boolean;
  type?: string;
  /** Fixed text inside the well, e.g. "°" or "GMT+3". */
  suffix?: React.ReactNode;
  prefix?: React.ReactNode;
  /** Tabular figures and looser tracking — birth times, coordinates, codes. */
  mono?: boolean;
  maxLength?: number;
  counter?: boolean;
  onChange?: (e: React.ChangeEvent) => void;
}
export declare function TextField(props: TextFieldProps): JSX.Element;
