/* Start a ledger (/ledger#new, handoff README §1): a name (required), the
 * difficulty (one chip; Custom says its values are asked once the ledger
 * starts), the in-game day (optional) and the courses finished (optional).
 *
 * An empty name shows the refusal note and creates nothing. Starting it
 * POSTs /api/ledger/ledgers and opens the new ledger, which shows "No
 * business yet".
 */
import { escape } from "./format.ts";
import { readAmount } from "./book.ts";

type Words = Record<string, string>;

export function mountStart(root: HTMLElement): void {
  const box = root.querySelector<HTMLElement>("[data-new]");
  if (!box) return;
  let words: Words = {};
  try { words = JSON.parse(root.dataset.words || "{}"); } catch { /* defaults */ }
  const w = (k: string) => words[k] ?? k;
  const refusal = box.querySelector<HTMLElement>("[data-new-refusal]");
  const refuse = (rows: { path: string; text: string }[] | null) => {
    if (!refusal) return;
    refusal.hidden = !rows;
    const at = refusal.querySelector<HTMLElement>("[data-note-rows]");
    if (at && rows) at.innerHTML = rows.map((r) => `<span class="lg-note-path">${escape(r.path)}</span><span class="lg-note-text">${escape(r.text)}</span>`).join("");
  };

  box.addEventListener("click", async (e) => {
    const t = e.target as HTMLElement;
    const diff = t.closest<HTMLElement>("[data-difficulty]");
    if (diff) {
      box.querySelectorAll<HTMLElement>("[data-difficulty]").forEach((b) => b.setAttribute("aria-pressed", String(b === diff)));
      const note = box.querySelector<HTMLElement>("[data-custom-note]");
      if (note) note.hidden = diff.dataset.difficulty !== "custom";
      return;
    }
    const course = t.closest<HTMLElement>("[data-course]");
    if (course) { course.setAttribute("aria-pressed", String(course.getAttribute("aria-pressed") !== "true")); return; }
    const start = t.closest<HTMLButtonElement>("[data-new-start]");
    if (!start) return;

    const nameInput = box.querySelector<HTMLInputElement>("[data-new-name]");
    const name = (nameInput?.value ?? "").trim();
    if (!name) { refuse([{ path: w("refuse.namePath"), text: w("refuse.name") }]); nameInput?.focus(); return; }
    const dayRaw = box.querySelector<HTMLInputElement>("[data-new-day]")?.value ?? "";
    const day = readAmount(dayRaw);
    if (day === undefined || (day != null && (day < 0 || !Number.isInteger(day)))) { refuse([{ path: w("refuse.dayPath"), text: w("refuse.day") }]); return; }
    refuse(null);
    const difficulty = box.querySelector<HTMLElement>("[data-difficulty][aria-pressed='true']")?.dataset.difficulty ?? "normal";
    const courses = [...box.querySelectorAll<HTMLElement>("[data-course][aria-pressed='true']")].map((b) => b.dataset.course!);
    start.disabled = true;
    try {
      const r = await fetch("/api/ledger/ledgers", {
        method: "POST", credentials: "same-origin",
        headers: { "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify({ name, difficulty, inGameDay: day ?? null, courses }),
      });
      const said = await r.json().catch(() => null);
      if (r.ok && said?.id) { window.location.assign(`/ledger/${said.id}`); return; }
      refuse([{ path: w("refuse.failedPath"), text: typeof said?.detail === "string" ? said.detail : w("refuse.failed") }]);
    } catch {
      refuse([{ path: w("refuse.failedPath"), text: w("refuse.failed") }]);
    }
    start.disabled = false;
  });
}
