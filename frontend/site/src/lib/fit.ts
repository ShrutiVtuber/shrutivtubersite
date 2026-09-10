// SPDX-License-Identifier: AGPL-3.0-only
/* Fitting a heading into a box, for images drawn by the server.
 *
 * ⚠ **Its own module so it can be tested.** `skycard.ts` reaches for the
 * wheel geometry and for node:fs, which makes it awkward to import from a
 * plain node test; this has no imports at all and the test next door drives it
 * directly. That matters more than usual here, because both bugs this function
 * exists to prevent are INVISIBLE in the output: text that overruns is simply
 * cropped by the PNG, and text that is dropped leaves a card that looks
 * perfectly well-composed and is missing half a title.
 */
/**
 * A heading broken to fit a box, at the largest size that will.
 *
 * ⚠ **Written because a title ran off the edge of a card.** The horoscope card
 * this drawing came from only ever sets a SIGN NAME — twelve known strings, the
 * longest of them "Sagittarius" — so nothing there ever needed measuring. The
 * practice room puts a writer's own title in the same slot, up to a hundred and
 * twenty characters of it, and the first one tried read "TEST — bridge chec"
 * with the rest past the right-hand edge. Nothing errors: SVG text simply keeps
 * going, and the PNG is cropped at the width it was asked for.
 *
 * The measurement is an approximation, not a font metric — resvg gives no way
 * to measure before rendering. `PER_EM` is the average advance of EB Garamond
 * in mixed case, rounded UP so the estimate errs toward breaking a line early
 * rather than one character too late. Erring the other way is the bug this
 * exists to prevent.
 */
const PER_EM = 0.5;

export function fitLines(
  text: string, width: number, sizes: number[] = [72, 60, 50, 42], lines = 2,
): { lines: string[]; size: number } {
  const words = text.trim().split(/\s+/).filter(Boolean);
  if (!words.length) return { lines: [""], size: sizes[0] };

  /** Greedy wrap into as many lines as it takes. */
  const wrap = (per: number): string[] => {
    const out: string[] = [];
    let line = "";
    for (const word of words) {
      const next = line ? `${line} ${word}` : word;
      if (next.length <= per) { line = next; continue; }
      if (line) out.push(line);
      line = word;
    }
    if (line) out.push(line);
    return out;
  };

  for (const size of sizes) {
    const per = Math.floor(width / (size * PER_EM));
    if (per < 4) continue;
    const out = wrap(per);
    // ⚠ Every line, and ALL of them. An earlier version stopped wrapping once
    // it had enough lines and then declared victory, which meant a long title
    // came back as its first two lines with the rest simply gone — no
    // ellipsis, no error, and no way to tell from the card that anything was
    // missing. A title silently losing its end is worse than a visibly cut one.
    if (out.length <= lines && out.every((l) => l.length <= per)) {
      return { lines: out, size };
    }
  }

  /* Nothing fitted at any size. Cut it at the smallest and SAY so — the
     ellipsis is the whole point. */
  const size = sizes[sizes.length - 1];
  const per = Math.max(4, Math.floor(width / (size * PER_EM)));
  const out = wrap(per).slice(0, lines);
  const last = out.length - 1;
  if (last >= 0) {
    const room = Math.max(1, per - 1);
    out[last] = (out[last].length > room
      ? out[last].slice(0, room).trimEnd()
      : out[last]) + "\u2026";
  }
  return { lines: out, size };
}
