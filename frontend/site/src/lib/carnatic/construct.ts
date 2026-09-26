/* Construction checks (FORMAT.md §4d), in words.
 *
 * They say what they see: "30 of 32 units · lands 2 units before samam",
 * "the three statements aren't the same length yet". For construct items the
 * verdict comes from them; for practice pieces they are prechecks, friendly
 * notes that never block.
 */

export interface ConstructSpec {
  input?: "konnakol" | "sargam";
  tala?: string;
  /** Counts per avartanam, resolved by the caller from talas.json. */
  counts?: number;
  nadai?: number;
  speed?: number;
  kalai?: number;
  /** Matra the phrase starts on (1-based), given by the item or stated by the learner. */
  start?: number;
  eduppu?: number;
  raga?: string;
  /** The raga's allowed swaras (arohana, avarohana, anya), for only_raga_swaras. */
  allowed?: Set<string>;
}

export interface Verdict { ok: boolean; notes: string[]; status: string; units: number; per: number }

const HOLD = new Set([",", ";", "·", "-"]);

export function units(line: string): string[] {
  const out: string[] = [];
  for (const raw of line.trim().split(/\s+/)) {
    if (!raw || raw === "|" || raw === "||") continue;
    if (raw === ";") { out.push(",", ","); continue; }
    out.push(raw);
  }
  return out;
}

export function perAvartanam(spec: ConstructSpec): number {
  const counts = spec.counts ?? 8;
  if (spec.input === "konnakol" || spec.nadai) return counts * (spec.kalai ?? 1) * (spec.nadai ?? 4);
  return counts * (spec.kalai ?? 1) * ({ 1: 1, 2: 2, 3: 4, 4: 8 } as Record<number, number>)[spec.speed ?? 1];
}

/** Where the phrase ends relative to the next samam, as a sentence. */
export function landing(n: number, spec: ConstructSpec): { lands: boolean; text: string } {
  const per = perAvartanam(spec);
  const start = (spec.start ?? 1) - 1 + (spec.eduppu ?? 0);
  const end = start + n;
  const rem = end % per;
  if (rem === 0) return { lands: true, text: "lands on samam" };
  const before = per - rem;
  return { lands: false, text: before <= per / 2 ? `lands ${before} unit${before === 1 ? "" : "s"} before samam` : `runs ${rem} unit${rem === 1 ? "" : "s"} past samam` };
}

function threeEqual(toks: string[]): boolean {
  const n = toks.length;
  for (let size = Math.floor(n / 3); size >= 1; size--) {
    for (let gap = 0; 3 * size + 2 * gap <= n; gap++) {
      if (3 * size + 2 * gap !== n) continue;
      const a = toks.slice(0, size).join(" ");
      const g1 = toks.slice(size, size + gap);
      const b = toks.slice(size + gap, 2 * size + gap).join(" ");
      const g2 = toks.slice(2 * size + gap, 2 * size + 2 * gap);
      const c = toks.slice(2 * size + 2 * gap).join(" ");
      if (a === b && b === c && g1.every((t) => HOLD.has(t)) && g2.every((t) => HOLD.has(t))) return true;
    }
  }
  return false;
}

/** The statements as the learner wrote them, split on runs of gaps. */
function statements(toks: string[]): string[] {
  const out: string[] = [];
  let cur: string[] = [];
  for (const t of toks) {
    if (HOLD.has(t)) {
      if (cur.length) out.push(cur.join(" "));
      cur = [];
    } else cur.push(t);
  }
  if (cur.length) out.push(cur.join(" "));
  return out;
}

export function check(line: string, checks: (string | Record<string, any>)[], spec: ConstructSpec): Verdict {
  const toks = units(line);
  const n = toks.length;
  const per = perAvartanam(spec);
  const notes: string[] = [];
  let ok = n > 0;
  const land = landing(n, spec);
  for (const c of checks) {
    const [name, arg] = typeof c === "string" ? [c, undefined] : Object.entries(c)[0] ?? ["", undefined];
    switch (name) {
      case "fits_tala": {
        if (n % per) {
          notes.push(`${n} units; ${(spec.tala ?? "the tala").replace(/_/g, " ")} at this speed needs ${per} per avartanam.`);
          ok = false;
        }
        break;
      }
      case "lands_on": {
        if (!land.lands) {
          notes.push(`It ${land.text}. Adjust the phrase or the gaps so the last unit ends on ${arg === "eduppu" || (arg && arg.target === "eduppu") ? "the eduppu" : "samam"}.`);
          ok = false;
        }
        break;
      }
      case "three_equal": {
        const target = arg === "last_part" ? toks.slice(Math.max(0, n - Math.max(3, Math.floor(n / 2)))) : toks;
        const good = threeEqual(toks) || (arg === "last_part" && [...Array(n).keys()].some((k) => threeEqual(toks.slice(k))));
        if (!good) {
          const st = statements(target);
          const lens = [...new Set(st.slice(-3).map((s) => s.split(" ").length))];
          notes.push(lens.length > 1 && st.length >= 3
            ? `The three statements aren't the same length yet: the last is ${st[st.length - 1]}, the others ${st[st.length - 3]}.`
            : "It isn't three identical statements with equal gaps yet.");
          ok = false;
        }
        break;
      }
      case "total_matras": {
        const want = arg === "from_start" ? per * Math.ceil(((spec.start ?? 1) - 1 + n) / per) - ((spec.start ?? 1) - 1) : arg;
        const wants = Array.isArray(want) ? want.map(Number) : [Number(want)];
        if (!wants.includes(n)) {
          notes.push(`${n} matras; this asks for ${wants.join(" or ")}.`);
          ok = false;
        }
        break;
      }
      case "groups_decreasing": {
        const groups = line.includes("|") ? line.split("|").map((g) => units(g).length).filter(Boolean) : statements(toks).map((s) => s.split(" ").length);
        const good = groups.length >= 2 && groups.every((g, i) => i === 0 || g < groups[i - 1]);
        if (!good) {
          notes.push(`The groups are ${groups.join(", ")}; a gopuccha yati gets shorter each time.`);
          ok = false;
        }
        break;
      }
      case "only_raga_swaras": {
        if (spec.allowed?.size) {
          const out = toks.filter((t) => /^[.]*[SRGMPDN][123]?'*$/.test(t))
            .map((t) => t.replace(/[.']/g, ""))
            .filter((t) => !(t === "S" || t === "P") && !spec.allowed!.has(t) && !(t.length === 1 && [...spec.allowed!].some((a) => a[0] === t)));
          if (out.length) {
            notes.push(`${[...new Set(out)].join(", ")} isn't in the raga's arohana, avarohana or anya swaras.`);
            ok = false;
          }
        }
        break;
      }
      case "direction":
        break;
      default:
        break;
    }
  }
  const status = `${n} of ${per * Math.max(1, Math.ceil(n / per))} units · ${land.text}`;
  return { ok, notes, status, units: n, per };
}
