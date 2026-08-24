/* Sigil geometry, in the browser.
 *
 * Runs on the reader's own machine for a reason the design states and a
 * practitioner will recognise: many hold that a statement of intent is spent
 * once drawn, and transmitting it to a server is not nothing. So the statement
 * never leaves the page — not in a request, not in the URL, and NOT IN THE
 * FILE'S METADATA when the figure is exported.
 *
 * THE GEOMETRY IS DETERMINISTIC. The same letters give the same figure, every
 * time, on any machine. A sigil you cannot reproduce is one you have to take
 * somebody's word for.
 */

const VOWELS = new Set(["A", "E", "I", "O", "U"]);

/**
 * The reduction, step by step — because a sigil you cannot reconstruct is one
 * you have to trust someone else about. Every stage is returned, not just the
 * result.
 */
export function reduce(statement, { keepVowels = false } = {}) {
  const upper = statement.toUpperCase();
  const lettersOnly = Array.from(upper).filter((c) => /[A-Z]/.test(c));
  const afterVowels = keepVowels ? lettersOnly : lettersOnly.filter((c) => !VOWELS.has(c));

  const seen = new Set();
  const unique = [];
  for (const c of afterVowels) {
    if (!seen.has(c)) { seen.add(c); unique.push(c); }
  }

  return {
    statement,
    upper,
    lettersOnly,
    afterVowels,
    unique,
    /* The reduction can consume the sentence entirely — all vowels, or every
       letter a repeat. That is a real outcome with a designed state, not an
       error. */
    exhausted: unique.length === 0,
    tooShort: unique.length === 1,
  };
}

/** Where each letter sits: 26 points around a circle, fixed for all time. */
function letterPoint(letter, radius, cx, cy) {
  const index = letter.charCodeAt(0) - 65;          // A = 0
  const angle = (index / 26) * Math.PI * 2 - Math.PI / 2;   // A at the top
  return [cx + radius * Math.cos(angle), cy + radius * Math.sin(angle)];
}

const WEIGHTS = { hairline: 1, "broad-pen": 3.5, engraved: 2 };

/**
 * Draw the figure. Pure function of (letters, options) — no randomness, no
 * clock, no machine state.
 */
export function draw(letters, { weight = "hairline", enclosure = "none", size = 512 } = {}) {
  const cx = size / 2, cy = size / 2;
  const radius = size * 0.34;
  const points = letters.map((l) => letterPoint(l, radius, cx, cy));
  if (points.length === 0) return null;

  const path = points
    .map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(3)} ${y.toFixed(3)}`)
    .join(" ");

  const stroke = WEIGHTS[weight] ?? 1;
  const start = points[0];
  const end = points[points.length - 1];

  let ring = "";
  if (enclosure === "circle") {
    ring = `<circle cx="${cx}" cy="${cy}" r="${(radius * 1.28).toFixed(3)}" fill="none" stroke="currentColor" stroke-width="${stroke}"/>`;
  } else if (enclosure === "vesica") {
    const r = radius * 1.15, dx = r * 0.5;
    ring =
      `<circle cx="${(cx - dx).toFixed(3)}" cy="${cy}" r="${r.toFixed(3)}" fill="none" stroke="currentColor" stroke-width="${stroke}"/>` +
      `<circle cx="${(cx + dx).toFixed(3)}" cy="${cy}" r="${r.toFixed(3)}" fill="none" stroke="currentColor" stroke-width="${stroke}"/>`;
  }

  /* No <title>, no <desc>, no metadata: the statement must not travel with the
     file. The figure carries the letters and nothing else. */
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" role="img" aria-label="Sigil">
  <g stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
    ${ring}
    <path d="${path}" stroke-width="${stroke}"/>
    <circle cx="${start[0].toFixed(3)}" cy="${start[1].toFixed(3)}" r="${(stroke * 2.2).toFixed(3)}" fill="currentColor" stroke="none"/>
    <path d="M${(end[0] - stroke * 3).toFixed(3)} ${(end[1] - stroke * 3).toFixed(3)} L${(end[0] + stroke * 3).toFixed(3)} ${(end[1] + stroke * 3).toFixed(3)} M${(end[0] + stroke * 3).toFixed(3)} ${(end[1] - stroke * 3).toFixed(3)} L${(end[0] - stroke * 3).toFixed(3)} ${(end[1] + stroke * 3).toFixed(3)}" stroke-width="${stroke}"/>
  </g>
</svg>`;
}

export const WEIGHT_OPTIONS = [
  { value: "hairline", label: "Hairline" },
  { value: "broad-pen", label: "Broad pen" },
  { value: "engraved", label: "Engraved" },
];
export const ENCLOSURE_OPTIONS = [
  { value: "none", label: "None" },
  { value: "circle", label: "Circle" },
  { value: "vesica", label: "Vesica" },
];
