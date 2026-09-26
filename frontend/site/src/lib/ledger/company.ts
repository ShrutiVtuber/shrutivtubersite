/* A ledger's page (/ledger/{id}): the entry grid and the quiet settings.
 *
 * The ENTRY GRID (SPEC §3.6): one row per business, one input per line, and
 * the computed week. Tab moves along a row (the browser's own order), Enter
 * down, Shift+Enter up. A paste holding tabs or newlines fills from the
 * focused cell rightwards and downwards. An untouched cell stays visibly
 * untouched (inset, dashed, —); it is never 0. "Write week N" posts every row
 * with money in; a row without it stays unwritten and nothing marks it.
 * A business not opened yet is marked opened when its first week is written
 * (the page says so beside the grid).
 *
 * The head, the rows' figures and the total are redrawn from the answer, with
 * the same rule as the server's (lib/ledger/book.ts `companyWeek`).
 */
import { companyWeek, isBlockPaste, parsePaste, pasteCells, readAmount, stepCell, weekTotal, MONEY_LINES, type WeekRow } from "./book.ts";
import { escape, fill, listed, money } from "./format.ts";

type Words = Record<string, string>;
interface Business { id: number; name: string; opened: boolean; weeks: WeekRow[] }
interface State { ledgerId: number; n: number; businesses: Business[] }

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

const figureHtml = (v: number | null, loss: string) =>
  `${escape(money(v))}${v != null && Math.round(v) < 0 ? `<span class="lg-loss">${escape(loss)}</span>` : ""}`;

function note(box: HTMLElement | null, rows: { path: string; text: string }[] | null) {
  if (!box) return;
  box.hidden = !rows;
  const at = box.querySelector<HTMLElement>("[data-note-rows]");
  if (at && rows) at.innerHTML = rows.map((r) => `<span class="lg-note-path">${escape(r.path)}</span><span class="lg-note-text">${escape(r.text)}</span>`).join("");
}

export function mountCompany(root: HTMLElement): void {
  let words: Words = {};
  let state: State;
  try { words = JSON.parse(root.dataset.words || "{}"); } catch { /* defaults */ }
  try { state = JSON.parse(root.dataset.state || "{}"); } catch { return; }
  const w = (k: string) => words[k] ?? k;
  const $ = <T extends HTMLElement = HTMLElement>(sel: string) => root.querySelector<T>(sel);
  const base = `/api/ledger/ledgers/${state.ledgerId}`;

  // ── the head, rows and total, from the weeks ───────────────────────────
  function drawFigures() {
    const week = companyWeek(state.businesses);
    const label = $("[data-head-week]");
    if (label && week) label.textContent = fill(w(week.total != null && Math.round(week.total) < 0 ? "head.weekLoss" : "head.week"), { n: String(week.n) });
    const total = $("[data-head-total]");
    if (total) total.innerHTML = figureHtml(week?.total ?? null, w("loss"));
    for (const b of state.businesses) {
      const cell = root.querySelector<HTMLElement>(`[data-business="${b.id}"] [data-row-figure]`);
      const wk = week ? b.weeks.find((x) => x.n === week.n) : null;
      if (cell) cell.innerHTML = figureHtml(wk ? weekTotal(wk) : null, w("loss"));
    }
    const foot = $("[data-total]");
    if (foot) foot.hidden = !week;
    const footLabel = $("[data-total-label]");
    if (footLabel && week) footLabel.textContent = fill(w("total.week"), { n: String(week.n) });
    const footFig = $("[data-total-figure]");
    if (footFig) footFig.innerHTML = figureHtml(week?.total ?? null, w("loss"));
  }

  // ── the entry grid ─────────────────────────────────────────────────────
  const grid = $("[data-entry]");
  const rows = grid ? [...grid.querySelectorAll<HTMLElement>("[data-entry-row]")] : [];
  const cellAt = (row: number, col: number) =>
    grid?.querySelector<HTMLInputElement>(`input[data-row="${row}"][data-col="${col}"]`) ?? null;
  const cols = MONEY_LINES.length;

  function rowLines(row: HTMLElement): { lines: Partial<WeekRow>; bad: HTMLInputElement[] } {
    const lines: Partial<WeekRow> = {};
    const bad: HTMLInputElement[] = [];
    row.querySelectorAll<HTMLInputElement>("input[data-cell]").forEach((input) => {
      const v = readAmount(input.value);
      input.setAttribute("aria-invalid", String(v === undefined));
      if (v === undefined) bad.push(input);
      (lines as Record<string, number | null>)[input.dataset.cell!] = v ?? null;
    });
    return { lines, bad };
  }

  function drawRowWeek(row: HTMLElement) {
    const out = row.querySelector<HTMLElement>("[data-entry-week]");
    if (!out) return;
    const t = weekTotal(rowLines(row).lines);
    out.dataset.empty = t == null ? "yes" : "no";
    out.innerHTML = figureHtml(t, w("loss"));
  }

  grid?.addEventListener("input", (e) => {
    const row = (e.target as HTMLElement).closest<HTMLElement>("[data-entry-row]");
    if (row) drawRowWeek(row);
  });

  grid?.addEventListener("keydown", (e) => {
    const input = e.target as HTMLInputElement;
    if (e.key !== "Enter" || !input.matches("input[data-cell]")) return;
    e.preventDefault();
    const next = stepCell({ row: Number(input.dataset.row), col: Number(input.dataset.col) }, e.shiftKey, rows.length);
    const to = cellAt(next.row, next.col);
    if (to) { to.focus(); to.select(); }
  });

  grid?.addEventListener("paste", (e) => {
    const input = e.target as HTMLInputElement;
    if (!input.matches("input[data-cell]")) return;
    const text = e.clipboardData?.getData("text/plain") ?? "";
    if (!isBlockPaste(text)) return;
    e.preventDefault();
    const landed = pasteCells(parsePaste(text), { row: Number(input.dataset.row), col: Number(input.dataset.col) }, { rows: rows.length, cols });
    const touched = new Set<number>();
    for (const c of landed) {
      const to = cellAt(c.row, c.col);
      if (to) { to.value = c.value; touched.add(c.row); }
    }
    touched.forEach((r) => rows[r] && drawRowWeek(rows[r]));
  });

  $("[data-entry-save]")?.addEventListener("click", async (e) => {
    const btn = e.currentTarget as HTMLButtonElement;
    note($("[data-entry-saved]"), null);
    note($("[data-entry-refusal]"), null);
    const payload: Record<string, unknown>[] = [];
    const refusals: { path: string; text: string }[] = [];
    for (const row of rows) {
      const id = Number(row.dataset.entryRow);
      const b = state.businesses.find((x) => x.id === id);
      const { lines, bad } = rowLines(row);
      for (const input of bad) {
        refusals.push({ path: fill(w("refuse.path"), { business: b?.name ?? "", line: w(`line.${input.dataset.cell}`).toLowerCase() }), text: w("refuse.figure") });
      }
      if (lines.moneyIn != null) payload.push({ businessId: id, ...lines });
    }
    if (refusals.length) { note($("[data-entry-refusal]"), refusals); return; }
    if (!payload.length) { note($("[data-entry-refusal]"), [{ path: fill(w("refuse.weekPath"), { n: String(state.n) }), text: w("saved.none") }]); return; }
    btn.disabled = true;
    const said = await send(`${base}/weeks/${state.n}`, "POST", { rows: payload });
    if (!said.ok || !said.body?.ledger) {
      btn.disabled = false;
      note($("[data-entry-refusal]"), [{ path: fill(w("refuse.weekPath"), { n: String(state.n) }),
        text: typeof said.body?.detail === "string" ? said.body.detail : w("refuse.failed") }]);
      return;
    }
    const written: number[] = said.body.written ?? [];
    // Writing a first week opens a business that was not opened yet (said beside the grid).
    await Promise.all(state.businesses.filter((b) => written.includes(b.id) && !b.opened)
      .map((b) => send(`/api/ledger/businesses/${b.id}`, "PUT", { opened: true }).then((r) => { if (r.ok) b.opened = true; })));
    const fresh = said.body.ledger.businesses as { id: number; weeks: WeekRow[] }[];
    for (const b of state.businesses) b.weeks = fresh.find((x) => x.id === b.id)?.weeks ?? b.weeks;
    const names = state.businesses.filter((b) => written.includes(b.id)).map((b) => b.name);
    note($("[data-entry-saved]"), [{ path: fill(w("refuse.weekPath"), { n: String(state.n) }), text: fill(w("saved.grid"), { n: String(state.n), names: listed(names, w("and")) }) }]);
    // Written rows are cleared; a row that was skipped keeps what was typed in it.
    for (const row of rows) {
      if (!written.includes(Number(row.dataset.entryRow))) continue;
      row.querySelectorAll<HTMLInputElement>("input[data-cell]").forEach((i) => { i.value = ""; i.removeAttribute("aria-invalid"); });
      drawRowWeek(row);
    }
    state.n = (companyWeek(state.businesses)?.n ?? state.n) + 1;
    const title = $("[data-entry-title]");
    if (title) title.textContent = fill(w("entry.title"), { n: String(state.n) });
    btn.textContent = fill(w("entry.save"), { n: String(state.n) });
    btn.disabled = false;
    drawFigures();
  });

  // ── settings: rename, the day, Custom's values, delete ─────────────────
  const settings = root.querySelector<HTMLElement>("[data-settings]");
  settings?.querySelector("[data-settings-save]")?.addEventListener("click", async () => {
    const said = settings.querySelector<HTMLElement>("[data-settings-said]");
    const refusal = settings.querySelector<HTMLElement>("[data-settings-refusal]");
    note(refusal, null);
    if (said) said.textContent = "";
    const name = (settings.querySelector<HTMLInputElement>("[data-rename]")?.value ?? "").trim();
    if (!name) { note(refusal, [{ path: w("settings.namePath"), text: w("settings.name") }]); return; }
    const dayRaw = settings.querySelector<HTMLInputElement>("[data-day]")?.value ?? "";
    const day = readAmount(dayRaw);
    const body: Record<string, unknown> = { name, inGameDay: day == null || day < 0 ? null : Math.floor(day) };
    const customBox = settings.querySelector<HTMLElement>("[data-custom]");
    if (customBox) {
      const custom: Record<string, number> = {};
      customBox.querySelectorAll<HTMLInputElement>("[data-custom-key]").forEach((i) => {
        const v = readAmount(i.value);
        if (v != null) custom[i.dataset.customKey!] = v;
      });
      body.custom = Object.keys(custom).length ? custom : null;
    }
    const r = await send(base, "PUT", body);
    if (!r.ok) { note(refusal, [{ path: w("settings.namePath"), text: typeof r.body?.detail === "string" ? r.body.detail : w("settings.failed") }]); return; }
    if (said) said.textContent = w("settings.saved");
    const h1 = root.querySelector("h1");
    if (h1) h1.textContent = r.body?.name ?? name;
  });
  settings?.addEventListener("click", async (e) => {
    const t = e.target as HTMLElement;
    const confirm = settings.querySelector<HTMLElement>("[data-delete-confirm]");
    const ask = settings.querySelector<HTMLElement>("[data-delete]");
    if (t.closest("[data-delete]")) { if (confirm) confirm.hidden = false; if (ask) ask.hidden = true; settings.querySelector<HTMLElement>("[data-delete-yes]")?.focus(); }
    else if (t.closest("[data-delete-no]")) { if (confirm) confirm.hidden = true; if (ask) { ask.hidden = false; ask.focus(); } }
    else if (t.closest("[data-delete-yes]")) {
      const r = await send(base, "DELETE");
      if (r.ok || r.status === 404) window.location.assign("/ledger");
      else note(settings.querySelector<HTMLElement>("[data-settings-refusal]"), [{ path: w("settings.namePath"), text: w("settings.failed") }]);
    }
  });
}
