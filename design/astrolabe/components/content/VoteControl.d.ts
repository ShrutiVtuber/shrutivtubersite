/** Up, down, or neither, with the running total between.
 * A vote lands by scaling the arrow to 1.06 and the count stepping — no toast,
 * no confirmation. Under reduced-motion the arrow simply fills.
 * State is fill AND colour AND aria-pressed, never colour alone. */
export interface VoteControlProps {
  value?: number;
  /** The reader's own vote: 1, 0 or -1. */
  mine?: number;
  onVote?: (v: number) => void;
  /** Signed out — visible but not operable. */
  disabled?: boolean;
  compact?: boolean;
}
export declare function VoteControl(props: VoteControlProps): JSX.Element;
