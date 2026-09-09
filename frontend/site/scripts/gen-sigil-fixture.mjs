import { reduce, draw } from "../src/lib/sigil.js";

// Chosen to exercise the corners, not to be pretty: every weight, every
// enclosure, the vowel switch both ways, a statement the reduction eats whole,
// a one-letter remainder, punctuation and digits, and a non-Latin script.
const CASES = [
  ["My will is to finish the work", false, "hairline", "none"],
  ["My will is to finish the work", true,  "hairline", "none"],
  ["My will is to finish the work", false, "broad-pen", "circle"],
  ["My will is to finish the work", false, "engraved", "vesica"],
  ["AEIOU", false, "hairline", "none"],
  ["banana", false, "hairline", "none"],
  ["Zz", false, "engraved", "circle"],
  ["it is 2026, and — half of it! — is spent", false, "broad-pen", "vesica"],
  ["Ἑλλάς and ABC", false, "hairline", "none"],
  ["a", true, "hairline", "none"],
];

const out = [];
for (const [statement, keepVowels, weight, enclosure] of CASES) {
  const r = reduce(statement, { keepVowels });
  out.push({
    statement, keepVowels, weight, enclosure,
    lettersOnly: r.lettersOnly, afterVowels: r.afterVowels, unique: r.unique,
    exhausted: r.exhausted, tooShort: r.tooShort,
    svg: draw(r.unique, { weight, enclosure }),
  });
}
console.log(JSON.stringify(out, null, 2));
