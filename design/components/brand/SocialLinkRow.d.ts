/** Row of platform links with mask-tinted Simple Icons glyphs (inherit currentColor). */
export interface SocialLinkRowProps {
  links: Array<{
    /** twitch | youtube | discord | x | github | linkedin | kofi | instagram | bluesky | mastodon */
    platform: string;
    href: string;
    /** Accessible label / pill text; defaults to the platform name */
    label?: string;
  }>;
  /** 'row' = icon-only, 'pills' = bordered icon + name */
  variant?: 'row' | 'pills';
  /** Icon size in px */
  size?: number;
}
