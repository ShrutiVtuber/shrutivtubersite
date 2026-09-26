/* Generators (FORMAT.md §4d): endless practice from the data. Each is a pure
 * function of the published research JSON (ragas.json, talas.json,
 * lessons.json), so an answer can never drift from the raga pages.
 *
 * A generator returns an ordinary item (choice, number, sargam or text) with
 * its explanation, and a card key for spaced repetition by category
 * ("gen:mela_scale_from_number:chakra-4").
 */

export interface GenItem {
  type: "choice" | "number" | "sargam" | "text";
  text: string;
  options?: { id: string; text: string }[];
  answer: any;
  accept?: string[];
  explain: string;
  rule?: Record<string, unknown>;
  card: string;
  note?: string;
}

export interface GenData {
  melas: { number: number; name: string; chakra: { number: number; name: string; mnemonic?: string; position: number };
           swaras: string[]; semitones: number[]; arohana: string; avarohana: string; vivadi: string[];
           katapayadi?: { aksharas: string[]; used?: string[]; digits: number[] } }[];
  janyas: { id: string; name: string; parent: { number: number; name: string }; parentAlternatives?: { number: number | null; name: string; who: string; note?: string }[] }[];
  suladi: { id: string; family: string; jati: string; name?: string; angaNotation: string; angas: number[]; aksharas: number }[];
  practical: { id: string; name: string; counts: unknown[] }[];
  lessonSets?: { id: string; name: string; items: { id: string; title?: string | null; units: number; angas: number[]; repeats: Record<string, number>; optional?: boolean; unitsPerCount?: number }[] }[];
}

export type Rng = () => number;

export function rng(seed = Date.now()): Rng {
  let s = seed >>> 0 || 1;
  return () => {
    s ^= s << 13; s ^= s >>> 17; s ^= s << 5;
    return ((s >>> 0) % 1_000_000) / 1_000_000;
  };
}

const pick = <T,>(r: Rng, xs: T[]): T => xs[Math.floor(r() * xs.length)];
const int = (r: Rng, lo: number, hi: number) => lo + Math.floor(r() * (hi - lo + 1));
function shuffle<T>(r: Rng, xs: T[]): T[] {
  const a = [...xs];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(r() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
const range = (s: Record<string, any>, def: [number, number]): [number, number] =>
  Array.isArray(s.range) && s.range.length === 2 ? [Number(s.range[0]), Number(s.range[1])] : def;

const SEMITONE: Record<string, number> = { S: 0, R1: 1, R2: 2, R3: 3, G1: 2, G2: 3, G3: 4, M1: 5, M2: 6, P: 7, D1: 8, D2: 9, D3: 10, N1: 9, N2: 10, N3: 11 };
const FULL: Record<string, string> = {
  R1: "shuddha rishabha", R2: "chatushruti rishabha", R3: "shatshruti rishabha", G1: "shuddha gandhara",
  G2: "sadharana gandhara", G3: "antara gandhara", M1: "shuddha madhyama", M2: "prati madhyama",
  D1: "shuddha dhaivata", D2: "chatushruti dhaivata", D3: "shatshruti dhaivata", N1: "shuddha nishada",
  N2: "kaisiki nishada", N3: "kakali nishada",
};
const SUB = (s: string) => s.replace(/([RGMDN])([123])/g, (_m, l, n) => l + "₀₁₂₃"[Number(n)]);

type Gen = (d: GenData, s: Record<string, any>, r: Rng) => GenItem;

const GENERATORS: Record<string, Gen> = {
  mela_scale_from_number(d, s, r) {
    const [lo, hi] = range(s, [1, 72]);
    const m = pick(r, d.melas.filter((x) => x.number >= lo && x.number <= hi));
    return {
      type: "sargam", text: `Write the arohana of mela ${m.number}. (A scale, not a raga.)`, answer: m.arohana,
      rule: { variantsRequired: true, checkOctaves: s.check_octaves !== false, enharmonic: s.enharmonic ?? "reject", checkHolds: false },
      explain: `Mela ${m.number}, ${m.name}: ${m.number <= 36 ? "shuddha madhyama (M₁)" : "prati madhyama (M₂)"}, `
        + `chakra ${m.chakra.number} (${m.chakra.name}), position ${m.chakra.position} in it. ${SUB(m.arohana.replace("S'", "Ṡ"))}.`,
      card: `gen:mela_scale_from_number:chakra-${m.chakra.number}`,
    };
  },
  mela_number_from_scale(d, s, r) {
    const [lo, hi] = range(s, [1, 72]);
    const m = pick(r, d.melas.filter((x) => x.number >= lo && x.number <= hi));
    return {
      type: "number", text: `Which mela has these swaras: ${SUB(m.swaras.join(" "))}? (A scale, not a raga.)`, answer: m.number,
      explain: `${m.number <= 36 ? "M₁ puts it in 1-36" : "M₂ puts it in 37-72"}; R and G make chakra ${m.chakra.number} (${m.chakra.name}), `
        + `which holds melas ${(m.chakra.number - 1) * 6 + 1}-${m.chakra.number * 6}; D and N give position ${m.chakra.position} in it: `
        + `${(m.chakra.number - 1) * 6} + ${m.chakra.position} = ${m.number}, ${m.name}.`,
      card: `gen:mela_number_from_scale:chakra-${m.chakra.number}`,
    };
  },
  katapayadi(d, s, r) {
    const m = pick(r, d.melas.filter((x) => x.katapayadi?.digits?.length));
    const k = m.katapayadi!;
    const digits = k.digits.join("");
    return {
      type: "number", text: `Find the number hidden in the name ${m.name}.`, answer: m.number,
      explain: `The first two syllables are ${k.aksharas.join(" and ")}, giving ${k.digits.join(" and ")}; read backwards, ${digits} becomes ${m.number}.`,
      card: "gen:katapayadi",
    };
  },
  vivadi_spot(d, s, r) {
    const n = Number(s.options ?? 4);
    const viv = pick(r, d.melas.filter((x) => x.vivadi?.length));
    const others = shuffle(r, d.melas.filter((x) => !x.vivadi?.length)).slice(0, n - 1);
    const opts = shuffle(r, [viv, ...others]);
    return {
      type: "choice", text: "Which of these melas is vivadi?",
      options: opts.map((m) => ({ id: String(m.number), text: `${m.number} ${m.name}` })), answer: String(viv.number),
      explain: `${viv.number} ${viv.name} has ${viv.vivadi.map(SUB).join(" and ")} side by side: two notes on neighbouring keys that share a pitch region.`,
      card: "gen:vivadi_spot",
    };
  },
  chakra_of(d, s, r) {
    const [lo, hi] = range(s, [1, 72]);
    const m = pick(r, d.melas.filter((x) => x.number >= lo && x.number <= hi));
    const names = [...new Map(d.melas.map((x) => [x.chakra.number, x.chakra.name])).entries()].sort((a, b) => a[0] - b[0]);
    const opts = shuffle(r, [m.chakra.name, ...shuffle(r, names.map((x) => x[1]).filter((x) => x !== m.chakra.name)).slice(0, 3)]);
    return {
      type: "choice", text: `Which chakra is mela ${m.number} in?`, options: opts.map((x) => ({ id: x, text: x })), answer: m.chakra.name,
      explain: `Six melas to a chakra: ${m.number} is in chakra ${m.chakra.number}, ${m.chakra.name}${m.chakra.mnemonic ? ` (${m.chakra.mnemonic})` : ""}.`,
      card: "gen:chakra_of",
    };
  },
  swarasthana_semitones(d, s, r) {
    const name = pick(r, Object.keys(FULL));
    return {
      type: "number", text: `How many semitones from Sa to ${SUB(name)} (${FULL[name]})?`, answer: SEMITONE[name], rule: { unit: "semitones" },
      explain: `${SUB(name)}, ${FULL[name]}, sits ${SEMITONE[name]} semitone${SEMITONE[name] === 1 ? "" : "s"} above Sa.`,
      card: `gen:swarasthana_semitones:${name[0]}`,
    };
  },
  enharmonic_name(d, s, r) {
    const m = pick(r, d.melas);
    const note = pick(r, m.swaras.filter((x) => x !== "S" && x !== "P"));
    const st = SEMITONE[note];
    const same = Object.entries(SEMITONE).filter(([k, v]) => v === st && k !== note).map(([k]) => k);
    const opts = shuffle(r, [note, ...same]).map((x) => ({ id: x, text: SUB(x) }));
    if (opts.length < 2) return GENERATORS.swarasthana_semitones(d, s, r);
    return {
      type: "choice", text: `In mela ${m.number}, ${m.name}, the note ${st} semitones above Sa is spelled as?`, options: opts, answer: note,
      explain: `Each mela has one R, one G, one D and one N in order; mela ${m.number} (${SUB(m.swaras.join(" "))}) spells it ${SUB(note)}.`,
      card: "gen:enharmonic_name",
    };
  },
  janya_parent(d, s, r) {
    const j = pick(r, d.janyas.filter((x) => x.parent?.number));
    const alts = (j.parentAlternatives ?? []).filter((a) => a.number);
    return {
      type: "number", text: `Which mela is ${j.name} usually filed under? (its number)`, answer: j.parent.number,
      accept: s.accept_alternatives ? alts.map((a) => String(a.number)) : [],
      explain: `${j.name} is filed under ${j.parent.number} ${j.parent.name}.`
        + (alts.length ? ` Some sources file it under ${alts.map((a) => `${a.number} (${a.who})`).join("; ")}, which is also accepted.` : "")
        + " A parent is a classification, not a history of the raga.",
      card: "gen:janya_parent",
    };
  },
  tala_counts(d, s, r) {
    const t = pick(r, d.suladi);
    return {
      type: "number", text: `How many aksharas in ${t.jati} jati ${t.family}?`, answer: t.aksharas,
      explain: `${t.jati[0].toUpperCase() + t.jati.slice(1)} jati ${t.family} is ${t.angaNotation}: ${t.angas.join(" + ")} = ${t.aksharas}.`,
      card: `gen:tala_counts:${t.family}`,
    };
  },
  tala_name_from_angas(d, s, r) {
    const pool = s.families ? d.suladi.filter((t) => s.families.includes(t.family) && t.jati === "chaturasra") : d.suladi;
    const t = pick(r, pool.length ? pool : d.suladi);
    const asksFamily = !s.show_jati;
    const names = asksFamily ? [...new Set(d.suladi.map((x) => x.family))] : [...new Set(d.suladi.map((x) => `${x.jati} jati ${x.family}`))];
    const answer = asksFamily ? t.family : `${t.jati} jati ${t.family}`;
    const opts = shuffle(r, [answer, ...shuffle(r, names.filter((x) => x !== answer)).slice(0, 3)]);
    return {
      type: "choice", text: `Name the tala ${t.angaNotation}.`, options: opts.map((x) => ({ id: x, text: x })), answer,
      explain: `${t.angaNotation} is ${t.jati} jati ${t.family}${t.name ? ` (${t.name})` : ""}: ${t.angas.join(" + ")} = ${t.aksharas} aksharas.`,
      card: `gen:tala_name_from_angas:${t.family}`,
    };
  },
  matras_per_avartanam(d, s, r) {
    const talas: string[] = s.talas ?? ["adi"];
    const id = pick(r, talas);
    const counts = d.practical.find((t) => t.id === id)?.counts.length ?? d.suladi.find((t) => t.id === id)?.aksharas ?? 8;
    const chapu = /chapu/.test(id);
    const kalai = chapu ? 1 : pick(r, (s.kalai ?? [1]) as number[]);
    const nadai = pick(r, (s.nadai ?? s.gati ?? [4]) as number[]);
    const name = d.practical.find((t) => t.id === id)?.name ?? id.replace(/_/g, " ");
    const NADAI: Record<number, string> = { 3: "tisra", 4: "chatusra", 5: "khanda", 7: "misra", 9: "sankeerna" };
    const total = counts * kalai * nadai;
    return {
      type: "number", text: `${name}${chapu ? "" : `, ${kalai} kalai`}, ${NADAI[nadai]} nadai: how many matras in one avartanam?`, answer: total,
      explain: `${counts} counts${chapu ? "" : ` × ${kalai} kalai`} × ${nadai} matras a count = ${total}.`,
      card: `gen:matras_per_avartanam:${NADAI[nadai]}`,
    };
  },
  mora_start(d, s, r) {
    const nadai = Array.isArray(s.nadai) ? pick(r, s.nadai as number[]) : Number(s.nadai ?? 4);
    const counts = d.practical.find((t) => t.id === (s.tala ?? "adi"))?.counts.length ?? 8;
    const space = counts * Number(s.kalai ?? 1) * nadai;
    const [plo, phi] = s.P ?? [2, 7];
    const [glo, ghi] = s.G ?? [0, 3];
    let P = int(r, plo, phi), G = int(r, glo, ghi);
    while (3 * P + 2 * G > space) { P = Math.max(1, P - 1); G = Math.max(0, G - 1); }
    const start = space - (3 * P + 2 * G) + 1;
    const NADAI: Record<number, string> = { 3: "tisra", 4: "chatusra", 5: "khanda", 7: "misra", 9: "sankeerna" };
    const text = (s.text_template as string | undefined)?.replace("{P}", String(P)).replace("{G}", String(G))
      ?? `A mora of P = ${P}, G = ${G} in Adi, ${NADAI[nadai]} nadai (${space} matras), landing on the next samam. The phrase fills the space: on which matra does it start?`;
    return {
      type: "number", text, answer: start,
      explain: `The mora is 3P + 2G = ${3 * P} + ${2 * G} = ${3 * P + 2 * G} matras; ${space} − ${3 * P + 2 * G} + 1 = ${start}.`,
      card: "gen:mora_start",
    };
  },
  varisai_repeats(d, s, r) {
    const sets = (d.lessonSets ?? []).filter((x) => !s.sets || s.sets.includes(x.id));
    const set = pick(r, sets.length ? sets : d.lessonSets ?? []);
    if (!set) return GENERATORS.matras_per_avartanam(d, { talas: ["adi"], kalai: [1], nadai: [4] }, r);
    const item = pick(r, set.items.filter((i) => !i.optional));
    const speed = pick(r, (s.speeds ?? [1, 2, 3]) as number[]);
    const per = item.angas.reduce((a, b) => a + b, 0) * (item.unitsPerCount ?? 1) * ({ 1: 1, 2: 2, 3: 4 } as Record<number, number>)[speed];
    const times = item.repeats[String(speed)] ?? 1;
    const idx = set.items.indexOf(item) + 1;
    return {
      type: "number", text: `${set.name} ${idx} at speed ${speed}: how many times through to land on samam?`, answer: times,
      explain: `It is ${item.units} notes; one avartanam at speed ${speed} holds ${per}. The fewest times through that end on samam: ${times}.`,
      card: `gen:varisai_repeats:${set.id}`,
    };
  },
};

export const GENERATOR_NAMES = Object.keys(GENERATORS);

export function generate(name: string, data: GenData, settings: Record<string, any> = {}, seed?: number): GenItem | null {
  const g = GENERATORS[name];
  if (!g || !data.melas?.length) return null;
  try {
    return g(data, settings, rng(seed));
  } catch {
    return null;
  }
}
