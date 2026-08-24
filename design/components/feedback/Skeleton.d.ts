/** Loading placeholder — opacity pulse (motion-safe), veil surface. */
export interface SkeletonProps {
  variant?: 'line' | 'text' | 'rect' | 'circle';
  width?: number | string;
  height?: number | string;
  /** For variant="text": number of lines (last one short) */
  lines?: number;
  style?: any;
}
