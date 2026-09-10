/** The ruling planetary hour, computed on device — which is why it is allowed to
 * be the app's one ambient signal: it works offline and it is always true.
 * It tints itself and the hem above it, and nothing else. Never tint a table. */
export interface HourChipProps {
  ruler?: 'sun' | 'moon' | 'mars' | 'mercury' | 'jupiter' | 'venus' | 'saturn';
  /** When this hour ends, e.g. "14:38". */
  ends?: string;
  /** Which hour of the day or night, 1–12. */
  ordinal?: number;
  /** True for a day hour, false for a night hour. */
  diurnal?: boolean;
  onClick?: () => void;
}
export declare function HourChip(props: HourChipProps): JSX.Element;
export declare const HOUR_RULERS: Record<string, { mark: string; name: string }>;
