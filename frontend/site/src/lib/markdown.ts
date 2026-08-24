/* Render the markdown that lives in the database.
 *
 * Uses Astro's own processor rather than a new dependency — @astrojs/markdown-remark
 * is already in the tree because Astro itself uses it, so this adds a name to
 * package.json and nothing to node_modules.
 *
 * The processor is created once and reused: building it per render would parse
 * the plugin chain on every request.
 */
import { createMarkdownProcessor } from "@astrojs/markdown-remark";

let processor: Awaited<ReturnType<typeof createMarkdownProcessor>> | null = null;

export async function renderMarkdown(md: string): Promise<string> {
  if (!md) return "";
  processor ??= await createMarkdownProcessor({ gfm: true, smartypants: true });
  const { code } = await processor.render(md);
  return code;
}
