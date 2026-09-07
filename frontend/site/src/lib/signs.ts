/* Sun sign from a birth date, for marking the reader's own sign.
 *
 * TROPICAL, because that is what a sun-sign horoscope means — twelve equal
 * arcs from the equinox. It is not a claim that the tropical zodiac is the
 * right one; the tool pages offer both and rank neither. It is that this
 * particular product, a monthly sun-sign reading, is a tropical convention,
 * and reading it sidereally would silently move most people one sign back.
 */
/**
 * **NOT in zodiacal order.** This runs Capricorn-first because it is indexed
 * by CALENDAR MONTH for `sunSign` — January's sign is Capricorn — and the
 * whole list exists for that lookup.
 *
 * Indexing it as though it began at Aries is silently wrong and looks fine:
 * `SIGNS.indexOf("leo")` is 7, and a wheel rotated to the seventh sign of the
 * zodiac is Scorpio. That happened on the reading page. Use `ZODIAC` for
 * anything astrological.
 */
export const SIGNS = [
  "capricorn", "aquarius", "pisces", "aries", "taurus", "gemini",
  "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius",
];

/**
 * The zodiac, in its own order, named as an astrologer writes it.
 *
 * Five files had each written this array out for themselves, which is four
 * chances for one of them to be subtly different. It is here so there is
 * something correct to reach for, and so the difference from `SIGNS` above is
 * stated rather than discovered.
 */
export const ZODIAC = [
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
] as const;

/** Last day of the preceding sign, by month index. Approximate by a day at the cusps. */
const CUSPS = [19, 18, 20, 19, 20, 20, 22, 22, 22, 22, 21, 21];

export function sunSign(isoDate: string): string | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(isoDate);
  if (!m) return null;
  const month = Number(m[2]), day = Number(m[3]);
  if (month < 1 || month > 12) return null;
  return day > CUSPS[month - 1] ? SIGNS[month % 12] : SIGNS[month - 1];
}
