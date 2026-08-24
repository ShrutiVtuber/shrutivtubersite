/** Footer imprint — entity, virtual office, role email, registry and VAT.
 * Ships from day one: pseudonymity is off, so the imprint is the exposure and it prevents
 * a home address leaking into a WHOIS record or a takedown notice later.
 * Values arrive bracketed until company registration completes; render brackets as-is. */
export interface LegalImprintProps {
  entity?: string;
  /** Virtual office — NEVER a home address */
  street?: string;
  postcode?: string;
  city?: string;
  country?: string;
  email?: string;
  registry?: string;
  vat?: string;
  /** 'stacked' for the footer column, 'inline' for legal pages */
  layout?: 'stacked' | 'inline';
}
