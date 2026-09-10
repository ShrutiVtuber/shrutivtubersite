/** The app's surface. Four tones and no more.
 * plain — a container · tappable — it pushes somewhere · highlighted — an offer,
 * the only place the gilt ornament sells something · warning — needs attention
 * or cannot be reckoned, rose and always with a mark. */
export interface CardProps {
  tone?: 'plain' | 'tappable' | 'highlighted' | 'warning' | 'inset';
  onClick?: () => void;
  href?: string;
  /** Add the gilt hem across the top. Implied by tone="highlighted". */
  hem?: boolean;
  pad?: number;
  children?: React.ReactNode;
  style?: React.CSSProperties;
}
export declare function Card(props: CardProps): JSX.Element;
