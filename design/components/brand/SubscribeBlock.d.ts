/** Reusable newsletter subscribe block. The consent wording is part of the design, not a line
 * pinned underneath it — and because the list carries commercial intent, that intent is stated
 * at the point of subscription rather than discovered later. */
export interface SubscribeBlockProps {
  /** 'panel' = full block for /newsletter, 'inline' = end-of-page strip, 'aside' = narrow column */
  variant?: 'panel' | 'inline' | 'aside';
  heading?: React.ReactNode;
  body?: React.ReactNode;
  /** 'idle' | 'sent' — 'sent' is the double-opt-in "check your email" state */
  state?: 'idle' | 'sent';
  email?: string;
  onEmailChange?: (e: any) => void;
  onSubmit?: (e: any) => void;
  /** Marketing consent must be ticked before submit is meaningful */
  consented?: boolean;
  onConsentChange?: (e: any) => void;
  error?: React.ReactNode;
}
