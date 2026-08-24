/* Sun sign from a birth date, for marking the reader's own sign.
 *
 * TROPICAL, because that is what a sun-sign horoscope means — twelve equal
 * arcs from the equinox. It is not a claim that the tropical zodiac is the
 * right one; the tool pages offer both and rank neither. It is that this
 * particular product, a monthly sun-sign reading, is a tropical convention,
 * and reading it sidereally would silently move most people one sign back.
 */
export const SIGNS = [
  "capricorn", "aquarius", "pisces", "aries", "taurus", "gemini",
  "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius",
];

/** Last day of the preceding sign, by month index. Approximate by a day at the cusps. */
const CUSPS = [19, 18, 20, 19, 20, 20, 22, 22, 22, 22, 21, 21];

export function sunSign(isoDate: string): string | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(isoDate);
  if (!m) return null;
  const month = Number(m[2]), day = Number(m[3]);
  if (month < 1 || month > 12) return null;
  return day > CUSPS[month - 1] ? SIGNS[month % 12] : SIGNS[month - 1];
}
