/* Her adjustments to the three themes, as one stylesheet every overlay
 * wears. Read at render; a missing answer means the design's defaults. */
import { SITE_API } from "./api";

export async function themeCss(): Promise<string> {
  try {
    const r = await fetch(`${SITE_API}/api/overlay/themes`);
    if (!r.ok) return "";
    const data = await r.json();
    return typeof data?.css === "string" ? data.css : "";
  } catch {
    return "";
  }
}
