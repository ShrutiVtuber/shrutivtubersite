/** Three export routes that are NOT equivalent, presented so the difference is legible.
 * The subscribable feed is the only one that keeps working as the year turns and the only one that
 * produces notifications, so it gets the prominence. A one-off .ics download goes stale the day
 * after it is made, and the design says so rather than letting someone find out in March. */
export interface ExportBlockProps {
  /** webcal: URL — the subscribable feed. The primary action. */
  feedHref: string;
  /** .ics snapshot download */
  fileHref: string;
  /** Filename for the download */
  fileName?: string;
  /** What the snapshot covers, e.g. '1–30 September 2026 · 120 events' */
  fileScope?: string;
  /** Per-station Google Calendar links: { label, href, glyph? } */
  googleLinks?: Array<{ label: string; href: string; glyph?: string }>;
  /** Shown under the feed action, e.g. 'Athens · Hellenic preset' */
  meta?: string;
  /** Copy-the-feed-URL handler; the component renders the URL in mono */
  onCopyFeed?: () => void;
  copyLabel?: string;
}
