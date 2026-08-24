/** Numbered pagination with typographic ← → arrows and windowed ellipsis. */
export interface PaginationProps {
  page: number;
  pageCount: number;
  /** Button mode */
  onChange?: (page: number) => void;
  /** Link mode: URL for a page (journal index) */
  hrefFor?: (page: number) => string;
  /** aria-label, default "Pagination" */
  label?: string;
}
