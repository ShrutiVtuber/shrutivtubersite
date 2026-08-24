/** Press-kit asset row — preview on checkerboard (transparency), sky, or ink; mono meta; download action. */
export interface AssetDownloadCardProps {
  name: string;
  /** e.g. "PNG · 2778×1000 · transparent · 412 KB" */
  meta?: string;
  /** Usually an <img>; nullable */
  preview?: React.ReactNode;
  /** Surface behind the preview */
  previewOn?: 'checker' | 'sky' | 'ink';
  href: string;
  /** download attribute value */
  filename?: string;
}
