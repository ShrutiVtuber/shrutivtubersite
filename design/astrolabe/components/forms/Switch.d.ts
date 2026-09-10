/** A settings switch on its own row. The whole row is the target (56px), the
 * switch is the affordance. State is position AND fill AND the knob's tick. */
export interface SwitchProps {
  label: string;
  description?: string;
  checked?: boolean;
  disabled?: boolean;
  onChange?: (next: boolean) => void;
}
export declare function Switch(props: SwitchProps): JSX.Element;
