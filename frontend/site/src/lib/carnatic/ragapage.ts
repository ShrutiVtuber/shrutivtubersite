/* A raga page's content, from the data: the three fully written pages
 * (featured.json: Mohanam, Bhairavi, Begada) as drawn, and every other janya
 * and melakarta raga generated from janya.json in the same layout — phrases
 * first, the summary scale second, then the swaras with a role, the variants,
 * the compositions and the tradition box (research response §A; DECISIONS
 * ragas §2, §3, §12). Confidence travels with every item.
 */
import type { Raga, Ragas } from "./data";
import type { Lang } from "./i18n";

type Loc = Record<string, string> | string | null | undefined;
const pick = (v: Loc, lang: Lang): string => (v == null ? "" : typeof v === "string" ? v : v[lang] ?? v.en ?? "");

export interface RolesView { key: "jiva" | "nyasa" | "graha"; value: string | null; note: string; confidence: string; sources: string[] }
export interface RagaView {
  kind: string; tags: string[]; cited: string;
  phrases: { line: string; note: string; confidence: string; source?: string; subs?: string[] }[];
  character: { text: string; who?: string; confidence?: string }[];
  arohana: string; avarohana: string; scaleNote: string;
  roles: RolesView[];
  variant: { intro: string; options: { line: string; attr: string }[] } | null;
  disagreements: string[];
  compositions: { title: string; form: string; composer: string; tala: string }[];
  compositionsNote: string;
  tradition: string;
  related: string[];
  confidence: string; confidenceNote: string; sources: string[];
  featured: boolean;
}

const JATI_FROM = (r: Raga) => r.classification.jati;
const host = (u?: string) => {
  try { return u ? new URL(u).hostname.replace(/^www\./, "") : ""; } catch { return ""; }
};

function roleNote(agreement: string | undefined): [string, string] {
  const a = (agreement ?? "").toLowerCase();
  if (!a) return ["", "high"];
  if (a.includes("single") || a.includes("one source")) return ["one source", "low"];
  if (a.includes("disputed")) return ["disputed", "medium"];
  if (a.includes("largely") || a.includes("most")) return ["most sources", "medium"];
  if (a.includes("agree")) return ["sources agree", "high"];
  return [agreement ?? "", "medium"];
}

export function ragaView(r: Raga, all: Ragas, featured: any, lang: Lang): RagaView {
  const f = featured?.ragas?.[r.id];
  if (f) {
    return {
      featured: true,
      kind: pick(f.kind, lang), tags: (f.tags?.[lang] ?? f.tags?.en ?? []) as string[], cited: f.cited ?? "",
      phrases: f.phrases.map((p: any) => ({ line: p.sargam, note: pick(p.note, lang), confidence: p.confidence ?? "high", subs: Array.isArray(p.showVariants) ? p.showVariants : undefined })),
      character: [{ text: pick(f.character, lang), confidence: f.characterConfidence }],
      arohana: f.arohana, avarohana: f.avarohana, scaleNote: pick(f.scaleNote, lang),
      roles: (["jiva", "nyasa", "graha"] as const).map((k) => ({
        key: k, value: f.roles[k].value, note: pick(f.roles[k].note, lang), confidence: f.roles[k].confidence ?? "medium",
        sources: (r as any)[k]?.sources ?? [],
      })),
      variant: f.variant ? { intro: pick(f.variant.intro, lang), options: f.variant.options.map((o: any) => ({ line: o.line, attr: pick(o.attr, lang) })) } : null,
      disagreements: [],
      compositions: f.compositions,
      compositionsNote: pick(f.compositionsNote, lang),
      tradition: pick(f.tradition, lang),
      related: [...(f.related ?? [])],
      confidence: r.confidence, confidenceNote: pick(f.confidenceNote, lang), sources: r.sources ?? [],
    };
  }

  /* Generated from janya.json. */
  const cls = r.classification;
  const kindBits = [r.kind === "melakarta" ? `Melakarta raga · ${r.number ?? r.parent.number}` : "Janya raga",
    cls.bhashanga ? "bhashanga" : "", cls.vakra ? "vakra" : "", r.kind === "janya" ? JATI_FROM(r) : ""].filter(Boolean);
  const tags = [JATI_FROM(r), cls.bhashanga ? "bhashanga" : "upanga", r.tier === 1 ? "first pieces" : r.tier === 3 ? "for later" : "",
    r.hindustani ? "Hindustani-derived" : ""].filter(Boolean);
  const cited = [...new Set(r.prayogas.map((p) => host(p.source)).filter(Boolean))].slice(0, 4).join(", ");
  const roles = (["jiva", "nyasa", "graha"] as const).map((k) => {
    const v = (r as any)[k] as Raga["jiva"];
    const [note, confidence] = roleNote(v?.agreement);
    const disputed = (v?.agreement ?? "").toLowerCase().includes("disputed");
    const value = v?.value?.length && !disputed ? v.value.join(" ") : null;
    return {
      key: k, value, sources: v?.sources ?? [],
      note: value ? note : v?.value?.length ? "Disputed; not shown as a fact." : "No source found.",
      confidence: value ? confidence : "low",
    };
  });
  const alt = r.parentAlternatives.filter((a) => a.number);
  const scaleNote = alt.length
    ? `Some sources place ${r.name} under mela ${alt.map((a) => `${a.number} (${a.name})`).join(" or ")} instead of ${r.parent.number}.`
    : "";
  const variants = (r.variants ?? []).filter((v) => v.arohana || v.avarohana);
  const variant = variants.length ? {
    intro: "Sources give this raga's scale more than one way. The common form is shown first; the others are named with who gives them.",
    options: [
      { line: `${r.arohana} · ${r.avarohana}`, attr: "Common practice" },
      ...variants.slice(0, 3).map((v) => ({ line: `${v.arohana ?? r.arohana} · ${v.avarohana ?? r.avarohana}`, attr: `Some schools · ${shorten(v.who ?? "")}` })),
    ],
  } : null;
  const siblings = all.janyas.filter((x) => x.parent.number === r.parent.number && x.id !== r.id).map((x) => x.id);
  const performedParent = all.performed.find((x) => x.number === r.parent.number)?.id;
  return {
    featured: false,
    kind: kindBits.join(" · "), tags, cited,
    phrases: r.prayogas.map((p) => ({ line: annotate(p.sargam, r), note: p.note ?? "", confidence: r.confidence, source: p.source })),
    character: r.gamakaCharacter.slice(0, 3).map((g) => ({ text: g.text, who: g.attribution, confidence: g.confidence })),
    arohana: annotate(r.arohana, r), avarohana: annotate(r.avarohana, r), scaleNote,
    roles, variant,
    disagreements: r.disagreements ?? [],
    compositions: r.compositions.map((c) => ({ title: c.title, form: c.form, composer: shorten(c.composer), tala: c.tala })),
    compositionsNote: "",
    tradition: r.timeRasa?.value ?? "",
    related: [...(performedParent && performedParent !== r.id ? [performedParent] : []), ...siblings].slice(0, 5),
    confidence: r.confidence, confidenceNote: r.confidence === "high" ? "" : r.confidence === "low" ? "Thin or conflicting sources; check with a teacher." : "Some sources differ on the details.",
    sources: r.sources ?? [],
  };
}

/** Mark anya swaras (from outside the parent mela) with !a so the scale draws them in rose. */
function annotate(scale: string, r: Raga): string {
  const anya = new Set((r.anya ?? []).map((a: any) => (typeof a === "string" ? a : a?.swara)).filter(Boolean));
  if (!anya.size) return scale;
  return scale.split(/\s+/).map((t) => (anya.has(t.replace(/['.]/g, "")) ? `${t}!a` : t)).join(" ");
}

function shorten(s: string): string {
  const first = s.split(/[;(]/)[0].trim();
  return first.length > 90 ? first.slice(0, 88) + "…" : first;
}
