/* The stored reading, shaped for the record block.
 *
 * The daemon returns far more than the block shows — every body, the stations,
 * the transits — and all of it is kept in the row so a later design can show
 * more without re-casting anything. This picks out the eight lines the
 * designer's block has and writes them the way it writes them: a degree, then
 * the sign as a glyph.
 */
import { SITE_API } from "../api";
import type { SkyRecord } from "./types";

/* Tropical signs come back in English, sidereal rāśis in Sanskrit, and both
   are drawn as the same twelve glyphs. */
const SIGN: Record<string, string> = {
  Aries: "♈", Taurus: "♉", Gemini: "♊", Cancer: "♋",
  Leo: "♌", Virgo: "♍", Libra: "♎", Scorpio: "♏",
  Sagittarius: "♐", Capricorn: "♑", Aquarius: "♒", Pisces: "♓",
};

const RASHI: Record<string, string> = {
  "Meṣa": "♈", "Vṛṣabha": "♉", "Mithuna": "♊", "Karka": "♋",
  "Siṃha": "♌", "Kanyā": "♍", "Tulā": "♎", "Vṛścika": "♏",
  "Dhanu": "♐", "Makara": "♑", "Kumbha": "♒", "Mīna": "♓",
};

/** 20.0751 → "20°04′". Arc-minutes, because that is how a chart is read. */
function degrees(d: number | undefined): string {
  if (typeof d !== "number" || Number.isNaN(d)) return "";
  const whole = Math.floor(d);
  const minutes = Math.round((d - whole) * 60);
  // 59.7′ rounds to 60, which is the next degree and not "20°60′".
  const [deg, min] = minutes === 60 ? [whole + 1, 0] : [whole, minutes];
  return `${deg}°${String(min).padStart(2, "0")}′`;
}

const place = (d: number | undefined, name: string, table: Record<string, string>) => {
  const glyph = table[name];
  const arc = degrees(d);
  return glyph && arc ? `${arc} ${glyph}` : arc || "";
};

/** The record block's eight lines, or null when there is nothing to show. */
export function shape(payload: any): SkyRecord | null {
  if (!payload) return null;
  const r = payload.reading;

  /* A capture that failed still has something to say, and saying it is the
     point — the design would rather print why the sky is missing than leave a
     gap the reader has to interpret. */
  if (!r) {
    return payload.failureReason
      ? {
          sunTropical: "", sunSidereal: "", moonTropical: "", moonSidereal: "",
          tithi: "", nakshatra: "", attic: "", thelemic: "",
          rule: `Not recorded: ${payload.failureReason}.`,
        }
      : null;
  }

  const sun = r.sun ?? {};
  const moon = r.moon ?? {};
  const hindu = r.reckonings?.hindu ?? {};
  const attic = r.reckonings?.attic ?? {};
  const ruler = r.planetaryHours?.current?.ruler ?? "";

  return {
    sunTropical: place(sun.tropical?.degree, sun.tropical?.sign, SIGN),
    sunSidereal: place(sun.sidereal?.degree, sun.sidereal?.rashi, RASHI),
    moonTropical: place(moon.tropical?.degree, moon.tropical?.sign, SIGN),
    moonSidereal: place(moon.sidereal?.degree, moon.sidereal?.rashi, RASHI),
    tithi: hindu.tithi ?? "",
    nakshatra: moon.sidereal?.nakshatra ?? "",
    attic: [attic.greek, attic.day].filter(Boolean).join(" "),
    thelemic: r.reckonings?.thelemic?.formatted ?? "",
    rule: ruler ? `Hour of ${ruler}.` : "",
  };
}

export interface Moments {
  published: { sky: SkyRecord; at: string; place: string } | null;
  written: { sky: SkyRecord; at: string; place: string } | null;
}

const EMPTY: Moments = { published: null, written: null };

/**
 * Both moments for one entry.
 *
 * A 404 is the ordinary case, not a fault: most entries have a publication sky
 * and no writing sky, because only she can say when she began. The block is
 * simply not drawn.
 */
export async function moments(slug: string): Promise<Moments> {
  if (!slug) return EMPTY;
  let body: any;
  try {
    const r = await fetch(`${SITE_API}/api/journal/sky/${encodeURIComponent(slug)}`);
    if (!r.ok) return EMPTY;
    body = await r.json();
  } catch {
    return EMPTY;
  }

  const one = (p: any) => {
    const sky = shape(p);
    return sky ? { sky, at: p.at ?? "", place: p.place?.name ?? "" } : null;
  };
  return { published: one(body.published), written: one(body.written) };
}
