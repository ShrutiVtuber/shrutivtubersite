// SPDX-License-Identifier: AGPL-3.0-only
/**
 * Where a longitude lands on a wheel.
 *
 * This exists because the same eight lines were copied into four files and
 * were WRONG in two of them, in a way nothing catches. `180 - lon` and
 * `180 + lon` both draw a plausible-looking chart; one of them runs the zodiac
 * clockwise, which is backwards, and the only way to notice is to know that
 * Taurus should be below Aries and to go and look. Both copies carried a
 * comment saying "anticlockwise" while doing the opposite.
 *
 * So: one definition, and anything that draws a wheel imports it.
 */

/**
 * The zodiac in zodiacal order.
 *
 * NOT the same list as `SIGNS` in lib/signs.ts, which starts at Capricorn for
 * the horoscope routes and has already rotated one reading's wheel by seven
 * signs. If you want to turn a sign into an index for drawing, it is this one.
 */
export const WHEEL_SIGNS = [
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
] as const;

export const SIGN_GLYPH = [
  "♈︎", "♉︎", "♊︎", "♋︎", "♌︎", "♍︎", "♎︎", "♏︎", "♐︎", "♑︎", "♒︎", "♓︎",
] as const;

export const BODY_GLYPH: Record<string, string> = {
  Sun: "☉︎", Moon: "☾︎", Mercury: "☿︎", Venus: "♀︎", Mars: "♂︎",
  Jupiter: "♃︎", Saturn: "♄︎", Uranus: "♅︎", Neptune: "♆︎", Pluto: "♇︎",
  Rahu: "☊︎", Ketu: "☋︎",
};

/** Index of a sign name in zodiacal order, or 0 if it is not one. */
export const signIndex = (name: string): number => {
  const i = (WHEEL_SIGNS as readonly string[]).indexOf(name);
  return i < 0 ? 0 : i;
};

/**
 * Degrees measured from the start of the first house.
 *
 * With no rising sign this is the longitude unchanged — the wheel is then
 * simply the zodiac, Aries on the left. The rotation is presentation: the same
 * chart seen from a different starting sign, never a different chart.
 */
export const relativeTo = (longitude: number, risingIndex: number | null) =>
  ((longitude - (risingIndex === null ? 0 : risingIndex * 30)) % 360 + 360) % 360;

/**
 * A point on the wheel, given degrees and a radius from the centre.
 *
 * Nine o'clock is 0° and the zodiac runs ANTICLOCKWISE from there, which is
 * the direction it runs on paper. SVG's y grows downward, so the sine is
 * subtracted rather than added — that subtraction is the whole reason the
 * clockwise version looks right until you check it.
 *
 * `cx`/`cy` are the centre; a wheel drawn in its own 200×200 box passes
 * (100, 100).
 */
export const wheelPoint = (
  degrees: number, radius: number, cx: number, cy: number,
): readonly [number, number] => {
  const a = ((180 + degrees) * Math.PI) / 180;
  return [cx + radius * Math.cos(a), cy - radius * Math.sin(a)] as const;
};

/** Trim a number for SVG output — three decimals is well under a pixel. */
export const f = (n: number) => Number(n.toFixed(3));
