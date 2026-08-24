/** One stream on the almanac — date plate, title, dual-timezone times (authored in Athens). */
export interface ScheduleItemProps {
  title: string;
  /** ISO datetime with offset, e.g. "2026-08-27T21:00:00+03:00" */
  startISO: string;
  durationMin?: number;
  /** Game / category / topic line */
  topic?: string;
  status?: 'upcoming' | 'live' | 'past';
  /** Which timezone leads the display — pair with TimezoneToggle */
  tz?: 'local' | 'athens';
  href?: string;
}
