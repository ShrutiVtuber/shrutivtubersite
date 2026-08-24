/** VOD grid card. Thumb is nullable — absent, the sky stands in and the play disc stays visible. */
export interface VideoCardProps {
  title: string;
  /** Thumbnail URL — nullable; sky placeholder when absent */
  thumb?: string | null;
  platform?: 'twitch' | 'youtube';
  /** e.g. "1:41:09" */
  duration?: string;
  /** Preformatted, e.g. "3 days ago" */
  date?: string;
  href?: string;
  /** Render the loading skeleton instead */
  loading?: boolean;
}
