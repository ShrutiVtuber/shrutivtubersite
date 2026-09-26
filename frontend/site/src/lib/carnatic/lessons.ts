/* The self-paced lessons: one per item of the beginner path, at a readable
 * address (sarali-varisai-1, alankaram-3, geetham-sri-gananatha). */
export const SET_SLUG: Record<string, string> = {
  sarali_varisai: "sarali-varisai", janta_varisai: "janta-varisai", dhatu_varisai: "dhatu-varisai",
  tara_sthayi_varisai: "tara-sthayi", mandra_sthayi_varisai: "mandra-sthayi", alankaram: "alankaram", geethams: "geetham",
};
export const SET_ORDER = ["sarali_varisai", "janta_varisai", "dhatu_varisai", "tara_sthayi_varisai", "mandra_sthayi_varisai", "alankaram", "geethams"];

export interface LessonRef { id: string; slug: string; set: string; n: number; name: string; title: string | null; item: any; index: number }

export function lessonList(data: any, setName: (id: string) => string, withOptional = false): LessonRef[] {
  const out: LessonRef[] = [];
  for (const id of SET_ORDER) {
    const set = data?.sets?.find((s: any) => s.id === id);
    if (!set) continue;
    set.items.filter((i: any) => withOptional || !i.optional).forEach((i: any, k: number) => {
      const slug = id === "geethams" ? `geetham-${i.id.replace(/_/g, "-")}` : `${SET_SLUG[id]}-${i.id.split("_").pop()?.replace(/^0/, "")}`;
      out.push({
        id: i.id, slug, set: id, n: k + 1, item: i, index: out.length,
        name: id === "geethams" ? (i.title ?? i.id).split(" (")[0] : `${setName(id)} ${k + 1}`,
        title: id === "geethams" ? i.title : i.title ?? null,
      });
    });
  }
  return out;
}

/* A paragraph per set for the lesson reader: what the exercise is for. Page
   copy, editable; the facts in it are the research's (lessons/SOURCES.md). */
export const SET_PROSE: Record<string, string> = {
  sarali_varisai: "Sarali varisai is the first exercise every Carnatic student learns: the seven swaras of Mayamalavagowla, up and down, in Adi tala. Sing or play it at the first speed with the drone until each swara lands in the middle of its pitch, then move to the second speed. Keep the tala with your hand from the first day.",
  janta_varisai: "Janta varisai doubles every swara. The repeat is where gamaka begins: the second of each pair is given a little stress. On the flute the repeat is a fingered sphuritam, a quick flick from the note below; some teachers tongue it instead.",
  dhatu_varisai: "Dhatu varisai leaps across the scale instead of stepping, so the ear has to find each swara without walking to it. Take it slowly at the first speed; the leaps are the point.",
  tara_sthayi_varisai: "Tara sthayi varisai climbs into the upper octave. Go only as high as is comfortable; if a note strains, sing or play it an octave lower for now and come back to it.",
  mandra_sthayi_varisai: "Mandra sthayi varisai goes down into the lower octave, where the voice and the flute both need a steady, unhurried breath.",
  alankaram: "Each alankaram is a pattern set in one of the seven suladi talas, so the hand learns a new tala with each one. Learn the tala in the trainer first, then keep it while you sing.",
  geethams: "The Malahari geethams are the first songs: simple melodies with words, in the rupaka and triputa talas. They are traditionally attributed to Purandara Dasa.",
};
