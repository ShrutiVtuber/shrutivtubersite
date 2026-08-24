/** Uppercase status chip — the word carries meaning; colour reinforces it. */
export interface BadgeProps {
  tone?: 'neutral' | 'accent' | 'rose' | 'live' | 'faint';
  /** Leading status dot */
  dot?: boolean;
  children: React.ReactNode;
}
