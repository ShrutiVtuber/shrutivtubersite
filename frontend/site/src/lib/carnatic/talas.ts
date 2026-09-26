/* Talas, as the pages show them. The structure (counts, actions, angas) is
 * the data's (talas.json, built from research/tala); the one-line notes and
 * the "how to keep it" sentences are page copy written from it, editable
 * like any other words on the site.
 */
export interface Count { n: number; action: "clap" | "finger" | "wave" | "silent"; finger?: string; anga?: number; samam?: boolean }
export interface Tala {
  id: string; slug: string; name: string; fullName?: string; angaNotation?: string; shape: string;
  counts: Count[]; angas: number[]; notes?: string; variants?: any[]; confidence?: string; eduppu?: number; asTala?: string;
  konnakol?: any;
}

export const ACTION_LABEL: Record<string, string> = {
  clap: "Clap", wave: "Wave", silent: "·", little: "Little", ring: "Ring", middle: "Middle", index: "Index", thumb: "Thumb",
};
export const actionLabel = (c: Count) => (c.action === "finger" ? ACTION_LABEL[c.finger ?? "little"] : ACTION_LABEL[c.action]);

/** The card's one line under each practical tala (Web Learn Practice, "talas"). */
export const CARD_NOTE: Record<string, string> = {
  adi: "The most common tala.",
  adi_2_kalai: "For slower kritis and varnams.",
  rupaka_3count: "For kritis. The alankaram uses the 6-count form.",
  misra_chapu: "Claps on 1, 4, 6. Some schools: wave first, or two claps (1, 4).",
  khanda_chapu: "Claps on 1, 3, 4. Some schools: claps on 1 and 3.",
  tisra_triputa: "Tisra laghu of three.",
  khanda_ata: "Used for many varnams.",
  misra_jhampa: "With an anudrutam (one clap).",
  rupaka_chaturasra: "Rupaka alankaram and the first two Malahari geethams.",
  chaturasra_eka: "Alankaram 7.",
  tisra_eka: "Short exercises.",
  deshadi: "Performed as Adi with a delayed start. Nadopasana is in Deshadi.",
};

/** The hero line and the "how to keep it" prose on a tala's own page. */
export const HOW: Record<string, [lede: string, how: string]> = {
  adi: ["Eight counts: a laghu of four and two drutams.", "Clap on the first count and count the little, ring and middle fingers on the next three. Then clap and turn the palm up, twice. The samam, count 1, is where phrases land."],
  adi_2_kalai: ["Sixteen counts: every action of Adi done twice.", "Clap twice, count each finger twice, then clap twice and wave twice, two times over. Some schools keep the action once and wave on the second of each pair."],
  rupaka_3count: ["In practice today: clap, clap, wave. Three counts per cycle.", "Clap on the first count, clap again on the second, then turn the palm up for the third. The cycle is short, so the samam comes round quickly: listen for the phrase landing on it, not only for the clap."],
  misra_chapu: ["Seven counts, felt as 3 + 2 + 2.", "Clap on counts 1, 4 and 6 and keep the counts between silent. The groups of three, two and two are what the ear hears; the claps mark where each group begins."],
  khanda_chapu: ["Five counts, felt as 2 + 3.", "Clap on counts 1, 3 and 4 and keep the others silent: one clap for the group of two, two claps for the group of three."],
  tisra_triputa: ["Seven counts: a laghu of three and two drutams.", "Clap and count two fingers, then clap and wave, twice."],
  khanda_ata: ["Fourteen counts: two laghus of five and two drutams.", "Clap and count four fingers, twice; then clap and wave, twice. Many varnams are in this tala."],
  misra_jhampa: ["Ten counts: a laghu of seven, an anudrutam and a drutam.", "Clap and count six fingers (little, ring, middle, index, thumb, then little again), clap once for the anudrutam, then clap and wave."],
  rupaka_chaturasra: ["Six counts: a drutam and a laghu of four.", "Clap and wave, then clap and count three fingers. This is the textbook rupaka, used for the rupaka alankaram."],
  chaturasra_eka: ["Four counts: one laghu of four.", "Clap and count three fingers. Alankaram 7 is in this tala."],
  tisra_eka: ["Three counts: one laghu of three.", "Clap and count two fingers."],
  deshadi: ["Adi tala, with the song entering 1½ beats after samam.", "Keep Adi exactly as usual. The song does not start on the samam: it enters one and a half counts later, so the first syllable falls between counts 2 and 3."],
};

/* Nadai: subdivisions per count and their konnakol (talas.json gati_nadai). */
export const NADAI: [string, number, string][] = [
  ["tisra", 3, "ta ki ta"], ["chatusra", 4, "ta ka di mi"], ["khanda", 5, "ta di gi na thom"],
  ["misra", 7, "ta ki ta ta ka di mi"], ["sankeerna", 9, "ta ka di mi ta di gi na thom"],
];

/** For a card's dot row: filled = clap, small ring = finger, ring = wave, dotted = silent. */
export const dotKind = (c: Count) => c.action;

export const EVERYDAY_SULADI = new Set(["tisra_jati_triputa", "chaturasra_jati_triputa", "chaturasra_jati_rupaka", "misra_jati_jhampa", "khanda_jati_ata"]);
