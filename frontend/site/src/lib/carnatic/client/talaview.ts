/* Moves a tala grid's playhead and pips, and the hand, from a TalaClock. */
import type { TalaClock } from "./tala";
import { ctx } from "./audio";

const LABEL: Record<string, string> = { clap: "Clap", wave: "Wave", silent: "Silent count", little: "Little", ring: "Ring", middle: "Middle", index: "Index", thumb: "Thumb" };

export function bindTalaView(clock: TalaClock, grid: HTMLElement | null, hand: HTMLElement | null, extra?: (i: number) => void) {
  const cells = grid ? Array.from(grid.querySelectorAll<HTMLElement>("[data-index]")) : [];
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  clock.onCount = (i) => {
    cells.forEach((c) => c.classList.toggle("is-now", Number(c.dataset.index) === i));
    cells.forEach((c) => c.querySelectorAll(".tg-pips i").forEach((p) => p.classList.remove("on")));
    const c = clock.counts[i];
    if (hand) {
      hand.removeAttribute("data-lifting");
      hand.dataset.state = c.action;
      hand.dataset.finger = c.finger ?? "";
      const label = hand.querySelector<HTMLElement>("[data-hand-label]");
      const cap = hand.querySelector<HTMLElement>("[data-hand-caption]");
      if (label) label.textContent = LABEL[c.action === "finger" ? c.finger ?? "little" : c.action];
      if (cap) cap.textContent = `count ${c.n}${c.samam ? " · samam" : ""}`;
    }
    extra?.(i);
  };
  clock.onMatra = (i, m) => {
    const cell = cells.find((c) => Number(c.dataset.index) === i);
    cell?.querySelectorAll(".tg-pips i").forEach((p, k) => p.classList.toggle("on", k <= m));
  };
  clock.onFrame = () => {
    /* A clap lifts 120 ms before it lands (25 % of a count above 120 a minute). */
    if (!hand || reduce) return;
    const cur = clock.times.filter((t) => t.at <= ctx().currentTime).pop();
    if (!cur) return;
    const next = clock.counts[(cur.index + 1) % clock.counts.length];
    const lead = clock.bpm > 120 ? clock.countSeconds * 0.25 : 0.12;
    if (next.action === "clap" && cur.at + clock.countSeconds - ctx().currentTime < lead + 1 / 60) hand.dataset.lifting = "";
  };
  clock.onStop = () => {
    cells.forEach((c) => c.classList.remove("is-now"));
  };
}
