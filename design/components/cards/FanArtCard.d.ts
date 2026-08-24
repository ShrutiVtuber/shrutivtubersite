/** Gallery tile with the artist credit as the loudest text. Click opens the lightbox (Modal). */
export interface FanArtCardProps {
  /** Nullable — empty slots show a quiet sky tile with a ✶ */
  image?: string | null;
  title?: string;
  artist: string;
  artistHref?: string;
  /** e.g. "X", "Pixiv" */
  platform?: string;
  /** Open-in-lightbox callback */
  onOpen?: () => void;
}
