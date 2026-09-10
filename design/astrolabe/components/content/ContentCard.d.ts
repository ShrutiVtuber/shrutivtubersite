/** One of her things: a reading or an article. Same card, two kinds.
 * ⚠ Missing content is designed: no title falls back to sign and date
 * ("Scorpio · 9 Sep"); no opening line leaves the card shorter rather than
 * showing an empty paragraph. Nothing ever renders "Untitled".
 */
export interface ContentCardProps {
  kind?: 'reading' | 'article';
  title?: string;
  /** e.g. "Scorpio" — becomes the heading when there is no title. */
  sign?: string;
  /** AstroSymbols character for the sign. */
  signMark?: string;
  date: string;
  excerpt?: string;
  readingTime?: string;
  unread?: boolean;
  onOpen?: () => void;
  cover?: string;
  coverAlt?: string;
}
export declare function ContentCard(props: ContentCardProps): JSX.Element;
