/* The one catalogue (handoff README §2, "Classes decision"): self-paced
 * lessons and live classes together, filtered by format.
 *
 * Self-paced lessons are the beginner path's sets. Live classes and workshops
 * are the site's own classes (/classes, the admin's Classes) whose address
 * starts `carnatic-`: that prefix is how a class joins this catalogue rather
 * than the site's other teaching. Times are shown in Athens time with the
 * visitor's own beside it (filled in by the browser, which knows their zone).
 *
 * The journal's school essays are the journal entries about ragas, talas,
 * tuning and the instruments; with none, the section says what will appear.
 */
import { site } from "../api";
import type { T } from "./i18n";

export interface ClassRow { title: string; kind: "self" | "live" | "workshop"; kindLabel: string; meta: string; href: string; startsAt?: string | null }

export async function schoolClasses(t: T, lessons: any): Promise<{ filters: [string, string][]; rows: ClassRow[] }> {
  const rows: ClassRow[] = [];
  for (const set of lessons?.sets ?? []) {
    const n = (set.items ?? []).filter((i: any) => !i.optional).length;
    if (!n) continue;
    rows.push({
      title: `${t(`set.${set.id}` as any) === `set.${set.id}` ? set.name : t(`set.${set.id}` as any)}, speeds 1 to 3`,
      kind: "self", kindLabel: "Self-paced", meta: `${n} lessons · free`, href: `/carnatic/lessons#${set.id}`,
    });
  }
  const courses = (await site<any[]>("/api/classes")) ?? [];
  for (const c of courses.filter((c) => typeof c.slug === "string" && c.slug.startsWith("carnatic-"))) {
    const kind = c.kind === "workshop" ? "workshop" : "live";
    const when = c.startsAt ? athens(c.startsAt) : "date to be announced";
    rows.push({ title: c.title, kind, kindLabel: kind === "workshop" ? "Workshop" : "Live class", meta: when,
                href: `/classes/${c.slug}`, startsAt: c.startsAt });
  }
  return {
    filters: [["all", t("gen.all")], ["self", "Self-paced"], ["live", "Live classes"], ["workshop", "Workshops"]],
    rows,
  };
}

export function athens(iso: string): string {
  const d = new Date(iso);
  const day = d.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "short", timeZone: "Europe/Athens" });
  const time = d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "Europe/Athens" });
  return `${day} ${time} Athens`;
}


export async function schoolJournal(limit = 3): Promise<{ href: string; title: string; meta: string }[]> {
  /* The same list the app reads (lib/carnatic/journal.ts). */
  const { schoolArticles } = await import("./journal");
  return (await schoolArticles()).slice(0, limit).map((e) => ({
    href: e.href, title: e.title,
    meta: e.date ? new Date(e.date).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "",
  }));
}
