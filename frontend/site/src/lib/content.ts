/* Page sections from the database, rendered.
 *
 * Sections are the unit the admin toggles, reorders and edits, so a page asks
 * for its sections rather than hard-coding its own prose. A page with no
 * sections is not an error — it renders its designed absent state.
 */
import { site, PATHS } from "./api";
import { renderMarkdown } from "./markdown";

export interface Section {
  key: string;
  kind: string;
  eyebrow: string;
  title: string;
  bodyMd: string;
  linkUrl: string;
  linkLabel: string;
  media: { url: string; alt: string } | null;
}

export interface RenderedSection extends Section {
  html: string;
}

export async function pageSections(page: string): Promise<RenderedSection[]> {
  const data = await site<{ page: string; sections: Section[] }>(PATHS.page(page));
  const sections = data?.sections ?? [];
  return Promise.all(
    sections.map(async (s) => ({ ...s, html: await renderMarkdown(s.bodyMd) })),
  );
}

export interface ProfilePayload {
  fields: { label: string; value: string }[];
  credits: { role: string; name: string; url?: string; note?: string }[];
}

export const profile = () => site<ProfilePayload>(PATHS.profile);
