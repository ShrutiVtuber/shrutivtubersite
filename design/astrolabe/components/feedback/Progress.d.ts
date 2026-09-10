/** Four shapes of waiting.
 * bar — determinate: a language pack downloading · ring — indeterminate, inline
 * refresh — the pull-to-refresh puck, a gilt arc, because the sky turning is the
 * app's own idiom · skeleton — the shape of the thing that is coming, never a
 * grey box with no shape. */
export interface ProgressProps {
  kind?: 'bar' | 'ring' | 'refresh' | 'skeleton';
  /** 0–100, for kind="bar". */
  value?: number;
  size?: number;
  label?: string;
}
export declare function Progress(props: ProgressProps): JSX.Element;
export declare function Skeleton(props: { lines?: number; title?: boolean; height?: number }): JSX.Element;
