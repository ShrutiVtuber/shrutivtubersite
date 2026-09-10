/** An offer: a class, a reading slot, the shop, support.
 * ⚠ Nothing takes money inside the app. Every offer leaves for her own checkout
 * in a browser, and the card says so on its face — the ↗ and the words "opens in
 * your browser" are the promise that the address bar will say whose it is.
 */
export interface OfferCardProps {
  title: string;
  body?: string;
  price: string;
  /** e.g. "per month", "for six weeks". */
  cadence?: string;
  membersOnly?: boolean;
  /** Members-only and the reader is not one: stays tappable, tapping explains. */
  locked?: boolean;
  href?: string;
  onOpen?: () => void;
  /** AstroSymbols character in the eyebrow. */
  mark?: string;
  soldOut?: boolean;
}
export declare function OfferCard(props: OfferCardProps): JSX.Element;
