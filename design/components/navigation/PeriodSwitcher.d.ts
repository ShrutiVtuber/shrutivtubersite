/** Period switcher for horoscope readings — built now for periods that do not exist yet.
 * Only monthly ships at launch; daily, seasonal and yearly are authored later. Periods that are
 * not available render as ABSENT, never as errors or disabled-with-a-tooltip. */
export interface PeriodSwitcherProps {
  /** Currently shown period */
  current: 'daily' | 'monthly' | 'seasonal' | 'yearly';
  /** Which periods exist. Anything omitted is simply not rendered. */
  available?: Array<'daily' | 'monthly' | 'seasonal' | 'yearly'>;
  onChange?: (period: string) => void;
  hrefFor?: (period: string) => string;
  /** Dateline for the current period, e.g. 'September 2026' */
  label?: string;
}
