/* Isopsephy in the browser.
 *
 * Six systems, six tables, and NO CONVERSION BETWEEN THEM. A Greek 598 and a
 * Hebrew 598 are not a correspondence, and the page says so — matches are only
 * ever sought inside one system.
 *
 * Two rules the tradition cares about and most calculators quietly break:
 *
 *   - A letter with no value in the chosen cipher IS NOT ZERO. It is outside
 *     the cipher. It is marked with a dash, excluded from the total, and named,
 *     because a total whose basis is invisible is unreproducible. The tool
 *     never guesses which letter was meant — transliteration is the reader's
 *     decision.
 *
 *   - Devanagari is deliberately NOT ADDITIVE and this must not be "fixed".
 *     Sanskrit has no additive gematria of the Greek kind. Kaṭapayādi is a
 *     PLACE-VALUE ENCODING: four consonant series run against the digits, only
 *     the LAST consonant of a cluster counts, standalone vowels are 0, and the
 *     digits are read RIGHT TO LEFT — aṅkānāṁ vāmato gatiḥ. So it yields a
 *     number, not a sum, and no total is offered because the system does not
 *     make one.
 */
import { CIPHERS } from "./ciphers.js";

export const VIRAMA = "्";
const DEVANAGARI_VOWELS = new Set("अआइईउऊऋॠऌॡएऐओऔ");
const DEVANAGARI_MATRAS = new Set("ािीुूृॄेैोौॅॉ");

export function isKatapayadi(slug) {
  return slug === "skt-katapayadi";
}

/** Sum a string under an additive cipher, reporting what was left out. */
export function reckon(text, slug) {
  const cipher = CIPHERS[slug];
  if (!cipher) return null;
  const map = cipher.mapping;
  const tiles = [];
  let total = 0;

  for (const ch of Array.from(text)) {
    if (/\s/.test(ch)) {
      tiles.push({ ch, kind: "space" });
      continue;
    }
    const lower = ch.toLowerCase();
    const value = map[ch] ?? map[lower];
    if (value == null) {
      // Outside the cipher — not zero, and named as such.
      tiles.push({ ch, kind: "unreckonable" });
    } else {
      total += value;
      tiles.push({ ch, kind: "counted", value });
    }
  }

  const unreckonable = tiles.filter((t) => t.kind === "unreckonable").map((t) => t.ch);
  return {
    kind: "sum",
    total,
    tiles,
    unreckonable,
    partial: unreckonable.length > 0,
    reduction: reduceDigits(total),
  };
}

/** Theosophic reduction: sum the digits until one remains. */
export function reduceDigits(total) {
  const steps = [];
  let n = Math.abs(total);
  while (n > 9) {
    n = String(n).split("").reduce((t, c) => t + Number(c), 0);
    steps.push(n);
  }
  return { steps, final: n };
}

/**
 * Kaṭapayādi: a place-value encoding, read right to left.
 *
 * Returns digit tiles and the assembled number. Deliberately no total.
 */
export function katapayadi(text) {
  const map = CIPHERS["skt-katapayadi"].mapping;
  const chars = Array.from(text);
  const tiles = [];
  const digits = [];

  let pendingConsonant = null;   // only the LAST of a cluster counts
  let sawVowelSign = false;

  const flush = () => {
    if (pendingConsonant !== null) {
      digits.push(pendingConsonant.value);
      tiles.push({ ...pendingConsonant, kind: "digit" });
      pendingConsonant = null;
    }
  };

  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i];

    if (/\s/.test(ch)) { flush(); tiles.push({ ch, kind: "space" }); sawVowelSign = false; continue; }

    if (ch === VIRAMA) {
      // The consonant before a virāma is joined to what follows: it is not the
      // last of the cluster, so it does not count.
      if (pendingConsonant) tiles.push({ ...pendingConsonant, kind: "cluster" });
      pendingConsonant = null;
      tiles.push({ ch, kind: "virama" });
      continue;
    }

    if (DEVANAGARI_VOWELS.has(ch)) {
      flush();
      // A standalone vowel is zero — a value, not an absence.
      digits.push(0);
      tiles.push({ ch, kind: "digit", value: 0 });
      sawVowelSign = false;
      continue;
    }

    if (DEVANAGARI_MATRAS.has(ch)) {
      // A vowel sign closes its consonant; it carries no value of its own.
      tiles.push({ ch, kind: "matra" });
      flush();
      sawVowelSign = true;
      continue;
    }

    const value = map[ch];
    if (value == null) {
      flush();
      tiles.push({ ch, kind: "unreckonable" });
      continue;
    }
    flush();
    pendingConsonant = { ch, value };
    sawVowelSign = false;
  }
  flush();

  // aṅkānāṁ vāmato gatiḥ — the digits are read right to left.
  const assembled = digits.length ? digits.slice().reverse().join("") : "";
  const unreckonable = tiles.filter((t) => t.kind === "unreckonable").map((t) => t.ch);

  return {
    kind: "place-value",
    digits,
    assembled,
    tiles,
    unreckonable,
    partial: unreckonable.length > 0,
    /* No total. Kaṭapayādi does not make one, and inventing an additive
       figure alongside it would misrepresent the system. */
    total: null,
  };
}

export function reckonAny(text, slug) {
  return isKatapayadi(slug) ? katapayadi(text) : reckon(text, slug);
}

export const RTL = new Set(["hebrew", "arabic"]);
