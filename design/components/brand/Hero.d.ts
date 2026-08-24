/** The sky panel — one per page. Art-absent by design; character art is the enhancement. */
export interface HeroProps {
  /** Multilingual eyebrow, e.g. "Welcome · Καλώς ήρθατε · स्वागत" */
  greeting?: string;
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  /** Buttons / LiveBadge row */
  actions?: React.ReactNode;
  /** e.g. SocialLinkRow, rendered under the actions */
  footnote?: React.ReactNode;
  /** Character art URL — nullable. Absent: a hairline moon takes its place. */
  art?: string | null;
  artAlt?: string;
  /** Optional clouds texture layered into the sky at low opacity */
  clouds?: string | null;
  /** px, default 420 */
  minHeight?: number;
}
