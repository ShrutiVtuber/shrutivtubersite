/* Stripe tax codes, the ones this shop actually sells under.
 *
 * Read off Stripe's own list rather than written from memory — a made-up code
 * is refused when a product is saved, and a plausible-but-wrong one is worse:
 * it is accepted, and quietly taxes a jumper as though it were a download.
 *
 * Two sets, because the right code depends on what the thing is. A digital
 * product and a physical one are never taxed the same way, so the field starts
 * from the right place when the kind is chosen instead of leaving a digital
 * default sitting on a jumper.
 */
export interface TaxCode {
  id: string;
  label: string;
}

export const DIGITAL_CODES: TaxCode[] = [
  { id: "txcd_10000000", label: "General — electronically supplied services" },
  { id: "txcd_10302000", label: "Digital book — download, kept for good" },
  { id: "txcd_10301000", label: "Audiobook" },
  { id: "txcd_10501000", label: "Digital photograph or image — download" },
  { id: "txcd_10202000", label: "Downloadable software — personal use" },
  { id: "txcd_10103100", label: "Software as a service — download, personal" },
];

export const PHYSICAL_CODES: TaxCode[] = [
  { id: "txcd_99999999", label: "General — tangible goods" },
  { id: "txcd_35010000", label: "Books, printed" },
  { id: "txcd_35020200", label: "Periodicals, printed" },
  { id: "txcd_30011000", label: "Clothing and footwear" },
  { id: "txcd_30060010", label: "Accessories, other than clothing" },
  { id: "txcd_30060007", label: "Jewellery" },
];

/** What a product of this kind starts as. */
export const DEFAULT_CODE: Record<string, string> = {
  digital: "txcd_10000000",
  physical: "txcd_99999999",
};

export const codesFor = (kind: string): TaxCode[] =>
  kind === "physical" ? PHYSICAL_CODES : DIGITAL_CODES;
