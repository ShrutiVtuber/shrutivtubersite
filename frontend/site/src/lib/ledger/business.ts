/* A business's page (/ledger/{id}/{business}): write a week, the book's
 * week chips at 390, and deleting the business.
 *
 * WRITE A WEEK (README §5): money in is the only line a week needs; a blank
 * line is not written and the draft total says it counts only the lines
 * written. Saving replaces any week with the same number and shows the SAVED
 * note — "Week 7: $74,020. +$849 ▲ against the plan." — and nothing else: no
 * congratulation, no count. The chart and the book redraw from the weeks.
 * A business not opened yet is marked opened when its first week is written
 * (the page says so under the button).
 */
import { drawBook, drawChart, readAmount, savedSentence, weekTotal, type PlanLines, type WeekRow } from "./book.ts";
import { escape, fill, money } from "./format.ts";

type Words = Record<string, string>;
interface State { ledgerId: number; businessId: number; opened: boolean; planned: number | null; lines: PlanLines; weeks: WeekRow[] }

async function send(path: string, method: string, body?: unknown): Promise<{ ok: boolean; status: number; body: any }> {
  try {
    const r = await fetch(path, {
      method, credentials: "same-origin",
      headers: { accept: "application/json", ...(body === undefined ? {} : { "content-type": "application/json" }) },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    return { ok: r.ok, status: r.status, body: r.status === 204 ? null : await r.json().catch(() => null) };
  } catch {
    return { ok: false, status: 0, body: null };
  }
}

function note(box: HTMLElement | null, rows: { path: string; text: string }[] | null) {
  if (!box) return;
  box.hidden = !rows;
  const at = box.querySelector<HTMLElement>("[data-note-rows]");
  if (at && rows) at.innerHTML = rows.map((r) => `<span class="lg-note-path">${escape(r.path)}</span><span class="lg-note-text">${escape(r.text)}</span>`).join("");
}

const MONEY = ["moneyIn", "goods", "wages", "rent", "ads", "deliveries"] as const;
const COUNTS = ["units", "customers"] as const;

export function mountBusiness(root: HTMLElement): void {
  let words: Words = {};
  let state: State;
  try { words = JSON.parse(root.dataset.words || "{}"); } catch { /* defaults */ }
  try { state = JSON.parse(root.dataset.state || "{}"); } catch { return; }
  const w = (k: string) => words[k] ?? k;
  const $ = <T extends HTMLElement = HTMLElement>(sel: string) => root.querySelector<T>(sel);
  const field = (k: string) => $<HTMLInputElement>(`[data-field="${k}"]`);
  let shown: number | undefined;

  function redraw() {
    const chart = drawChart(state.weeks.map((x) => ({ n: x.n, v: weekTotal(x) })), state.planned, words);
    const box = $("[data-chart]");
    if (box) { box.innerHTML = chart; box.hidden = !chart; }
    const none = $("[data-chart-none]");
    if (none) none.hidden = !!chart;
    const book = $("[data-book]");
    if (book) book.innerHTML = drawBook(state.weeks, state.lines, words, shown);
  }

  // The phone's week chips: one week at a time.
  root.addEventListener("click", (e) => {
    const chip = (e.target as HTMLElement).closest<HTMLElement>("[data-book-week]");
    if (!chip) return;
    shown = Number(chip.dataset.bookWeek);
    redraw();
    $<HTMLElement>(`[data-book-week="${shown}"]`)?.focus();
  });

  // ── the draft ──────────────────────────────────────────────────────────
  function read(): { lines: Record<string, number | null>; bad: string[] } {
    const lines: Record<string, number | null> = {};
    const bad: string[] = [];
    for (const k of [...MONEY, ...COUNTS]) {
      const input = field(k);
      const v = readAmount(input?.value);
      const wrong = v === undefined || ((COUNTS as readonly string[]).includes(k) && v != null && (v < 0 || !Number.isInteger(v)));
      input?.setAttribute("aria-invalid", String(wrong));
      if (wrong) bad.push(k);
      lines[k] = wrong ? null : (v ?? null);
    }
    return { lines, bad };
  }
  function drawDraft() {
    const t = weekTotal(read().lines as Partial<WeekRow>);
    const d = $("[data-draft]");
    if (d) d.textContent = t == null ? w("draft.none") : fill(w("draft.some"), { x: money(t) });
  }
  $("[data-write]")?.addEventListener("input", drawDraft);

  $("[data-write-save]")?.addEventListener("click", async (e) => {
    const btn = e.currentTarget as HTMLButtonElement;
    const saved = $("[data-write-saved]");
    const refusal = $("[data-write-refusal]");
    note(saved, null);
    note(refusal, null);
    const n = readAmount(field("n")?.value);
    const { lines, bad } = read();
    const refusals: { path: string; text: string }[] = [];
    if (n == null || n === undefined || !Number.isInteger(n) || n < 1 || n > 9999) refusals.push({ path: w("refuse.weekPath"), text: w("refuse.week") });
    for (const k of bad) {
      const line = w(`line.${k}`).toLowerCase();
      refusals.push((COUNTS as readonly string[]).includes(k)
        ? { path: fill(w("refuse.countPath"), { line }), text: w("refuse.count") }
        : { path: fill(w("refuse.linePath"), { line }), text: w("refuse.figure") });
    }
    if (!refusals.length && lines.moneyIn == null) refusals.push({ path: w("refuse.moneyPath"), text: w("refuse.money") });
    if (refusals.length) { note(refusal, refusals); return; }
    btn.disabled = true;
    const noteText = (field("note")?.value ?? "").trim();
    const said = await send(`/api/ledger/businesses/${state.businessId}/weeks/${n}`, "PUT", { ...lines, note: noteText || null });
    if (!said.ok || !said.body) {
      btn.disabled = false;
      note(refusal, [{ path: fill(w("saved.path"), { n: String(n) }), text: typeof said.body?.detail === "string" ? said.body.detail : w("refuse.failed") }]);
      return;
    }
    // Its first week opens a business that was not opened yet (the page says so).
    if (!state.opened) {
      const opened = await send(`/api/ledger/businesses/${state.businessId}`, "PUT", { opened: true });
      if (opened.ok) {
        state.opened = true;
        const eyebrow = $("[data-business-eyebrow]");
        if (eyebrow) eyebrow.textContent = w("eyebrow.opened");
      }
    }
    const week = said.body as WeekRow;
    state.weeks = [...state.weeks.filter((x) => x.n !== week.n), week].sort((a, b) => a.n - b.n);
    shown = week.n;
    redraw();
    note(saved, [{ path: fill(w("saved.path"), { n: String(week.n) }), text: savedSentence(week.n, weekTotal(week), state.planned, words) }]);
    for (const k of [...MONEY, ...COUNTS, "note"]) { const i = field(k); if (i) { i.value = ""; i.removeAttribute("aria-invalid"); } }
    const next = field("n");
    if (next) next.value = String(Math.max(...state.weeks.map((x) => x.n)) + 1);
    drawDraft();
    btn.disabled = false;
  });

  // ── delete, asked once ─────────────────────────────────────────────────
  const remove = $("[data-remove]");
  remove?.addEventListener("click", async (e) => {
    const t = e.target as HTMLElement;
    const confirm = remove.querySelector<HTMLElement>("[data-delete-confirm]");
    const ask = remove.querySelector<HTMLElement>("[data-delete]");
    if (t.closest("[data-delete]")) { if (confirm) confirm.hidden = false; if (ask) ask.hidden = true; remove.querySelector<HTMLElement>("[data-delete-yes]")?.focus(); }
    else if (t.closest("[data-delete-no]")) { if (confirm) confirm.hidden = true; if (ask) { ask.hidden = false; ask.focus(); } }
    else if (t.closest("[data-delete-yes]")) {
      const r = await send(`/api/ledger/businesses/${state.businessId}`, "DELETE");
      if (r.ok || r.status === 404) window.location.assign(`/ledger/${state.ledgerId}`);
      else note(remove.querySelector<HTMLElement>("[data-remove-refusal]"), [{ path: w("remove.path"), text: w("remove.failed") }]);
    }
  });

  drawDraft();
}
