/* Talking to the astrology daemon about stations.
 *
 * The daemon returns UTC instants. Rendering them is the page's job, and the
 * times must be shown where the visitor is — a station table for the wrong
 * city is indistinguishable from a right one until someone misses a dawn.
 */
import { astro } from "./api";

export interface Station {
  name: string;
  at: string | null;
  occurred: boolean;
  absentReason: string;
  dedication: string;
}
export interface StationDay {
  date: string;
  stations: Station[];
  phase?: string;
  moonAgeDays?: number | null;
  illumination?: number | null;
}
export interface StationsPayload {
  body: "sun" | "moon";
  preset: string;
  location: { lat: number; lon: number };
  start: string;
  days: number;
  maxDays: number;
  table: StationDay[];
}
export interface NextStationPayload {
  body: string;
  name: string;
  at: string;
  secondsAway: number;
  dedication: string;
  onDate: string;
}

export const SOLAR = ["sunrise", "noon", "sunset", "midnight"] as const;
export const LUNAR = ["moonrise", "culmination", "moonset", "nadir"] as const;

/** Astronomical glyphs, set as type. Never emoji, never an icon font. */
export const GLYPHS: Record<string, string> = {
  sunrise: "☉︎", noon: "☀", sunset: "☉︎", midnight: "☾︎",
  moonrise: "☾︎", culmination: "☽︎", moonset: "☾︎", nadir: "●",
};

export const PRESETS = [
  { value: "hellenic", label: "Hellenic" },
  { value: "thelemic", label: "Thelemic" },
  { value: "none", label: "None — times only" },
];

export const stations = (q: URLSearchParams) =>
  astro<StationsPayload>(`/stations?${q}`);
export const nextStation = (q: URLSearchParams) =>
  astro<NextStationPayload>(`/stations/next?${q}`);
