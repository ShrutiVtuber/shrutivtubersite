/** Quiet › trail for deep pages (journal articles, legal anchors). */
export interface BreadcrumbProps {
  /** Last item is the current page (no href needed) */
  items: Array<{ label: string; href?: string }>;
}
