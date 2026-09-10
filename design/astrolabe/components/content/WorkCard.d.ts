/** A community reading in the practice room — somebody else's, or your own.
 * Own work carries its status: draft, posted, corrected.
 * ⚠ Long content is designed: the title clamps at two lines, the body at three,
 * and a forty-character name truncates inside its row. The vote control is never
 * pushed off screen. */
export interface WorkCardProps {
  title: string;
  author?: string;
  avatar?: string;
  date: string;
  excerpt?: string;
  votes?: number;
  /** The reader's own vote: 1, 0 or -1. */
  myVote?: number;
  comments?: number;
  status?: 'draft' | 'posted' | 'corrected';
  mine?: boolean;
  onOpen?: () => void;
  onVote?: (v: number) => void;
  sign?: string;
}
export declare function WorkCard(props: WorkCardProps): JSX.Element;
