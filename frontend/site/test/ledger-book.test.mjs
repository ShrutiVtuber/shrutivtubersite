/* The book keeps what was written, and draws nothing that was not.
 *
 * src/lib/ledger/book.ts is pure: the ledger page's entry grid, the weeks
 * chart and the week page use it in the browser, and the server draws the
 * first frame with it. No game data is needed, so everything here always runs.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import {
  weekTotal, latestWeek, companyWeek, nextWeekNumber, readAmount, isBlockPaste, parsePaste, pasteCells, stepCell,
  against, savedSentence, chartSegments, chartPath, chartScale, niceCeil, drawChart, drawBook,
} from "../src/lib/ledger/book.ts";

const wk = (n, moneyIn, rest = {}) => ({ n, moneyIn, goods: null, wages: null, rent: null, ads: null, deliveries: null, ...rest });

// ── a week's total ─────────────────────────────────────────────────────────

test("a week's total leaves an unwritten line out and never reads it as zero", () => {
  assert.equal(weekTotal(wk(6, 93561, { goods: 15363, wages: 2268 })), 75930);
  assert.equal(weekTotal(wk(6, 100, { goods: 30, rent: 0 })), 70);
  assert.equal(weekTotal(wk(6, null, { goods: 5 })), null, "a week with no money in has no total");
  assert.equal(weekTotal(wk(5, 1000, { goods: 2820 })), -1820);
});

// ── which week counts as the latest ────────────────────────────────────────

test("the company's week is the highest any business wrote, summed over those that wrote it", () => {
  const gifts = { weeks: [wk(5, 70000), wk(6, 93561, { goods: 15363, wages: 2268 })] };
  const coffee = { weeks: [wk(6, 1000, { goods: 2820 })] };
  const flowers = { weeks: [wk(5, 9480)] };            // behind: not in the sum, and not a gap
  assert.deepEqual(companyWeek([gifts, coffee, flowers]), { n: 6, total: 75930 - 1820 });
  assert.equal(nextWeekNumber([gifts, coffee, flowers]), 7);
});

test("with no week written there is no latest week, and the next is week 1", () => {
  assert.equal(companyWeek([{ weeks: [] }, {}]), null);
  assert.equal(nextWeekNumber([]), 1);
});

test("a business's latest week is its highest number, not the last in the list", () => {
  assert.equal(latestWeek([wk(7, 1), wk(3, 1), wk(9, 1), wk(8, 1)]).n, 9);
  assert.equal(latestWeek([]), null);
});

test("a latest week written with no money in counts as the week, with no total", () => {
  assert.deepEqual(companyWeek([{ weeks: [wk(4, null)] }]), { n: 4, total: null });
});

// ── reading what was typed ─────────────────────────────────────────────────

test("a figure reads as the game shows it; blank is not written; nonsense is refused", () => {
  assert.equal(readAmount("$1,370"), 1370);
  assert.equal(readAmount(" 93561 "), 93561);
  assert.equal(readAmount("−1,820"), -1820);
  assert.equal(readAmount("-$1,820"), -1820);
  assert.equal(readAmount("(400)"), -400);
  assert.equal(readAmount("25.63"), 25.63);
  assert.equal(readAmount("0"), 0, "0 is a fact, not a blank");
  assert.equal(readAmount(""), null);
  assert.equal(readAmount("—"), null);
  assert.equal(readAmount("abc"), undefined);
  assert.equal(readAmount("12abc"), undefined);
  assert.equal(readAmount("1.2.3"), undefined);
});

// ── the entry grid's paste ─────────────────────────────────────────────────

test("a paste from a sheet is rows of cells, and its trailing newline is not a row", () => {
  assert.equal(isBlockPaste("93561"), false);
  assert.equal(isBlockPaste("93561\t15363"), true);
  assert.equal(isBlockPaste("1\n2"), true);
  assert.deepEqual(parsePaste("93561\t15363\t2268\n21040\t4000\n"), [["93561", "15363", "2268"], ["21040", "4000"]]);
  assert.deepEqual(parsePaste("1\r\n2\r\n"), [["1"], ["2"]]);
  assert.deepEqual(parsePaste("a\t\tc"), [["a", "", "c"]], "an empty cell in the sheet stays empty");
});

test("a pasted block fills from the focused cell rightwards and downwards, and stops at the grid's edge", () => {
  const block = parsePaste("1\t2\t3\n4\t5\t6\n7\t8\t9");
  const landed = pasteCells(block, { row: 2, col: 4 }, { rows: 4, cols: 6 });
  assert.deepEqual(landed, [
    { row: 2, col: 4, value: "1" }, { row: 2, col: 5, value: "2" },
    { row: 3, col: 4, value: "4" }, { row: 3, col: 5, value: "5" },
  ]);
  assert.deepEqual(pasteCells([["x"]], { row: 0, col: 0 }, { rows: 1, cols: 1 }), [{ row: 0, col: 0, value: "x" }]);
});

test("Enter moves down and Shift+Enter up, holding at the edges", () => {
  assert.deepEqual(stepCell({ row: 1, col: 3 }, false, 4), { row: 2, col: 3 });
  assert.deepEqual(stepCell({ row: 3, col: 3 }, false, 4), { row: 3, col: 3 });
  assert.deepEqual(stepCell({ row: 0, col: 2 }, true, 4), { row: 0, col: 2 });
  assert.deepEqual(stepCell({ row: 2, col: 2 }, true, 4), { row: 1, col: 2 });
});

// ── against the plan, and the saved note ───────────────────────────────────

test("against the plan is a signed figure and a caret; a loss is the sign and the word", () => {
  assert.deepEqual(against(74020, 73171), { text: "+$849", caret: "▲" });
  assert.deepEqual(against(72880, 73171), { text: "−$291", caret: "▼" });
  assert.deepEqual(against(100, 100), { text: "$0", caret: "" });
  assert.deepEqual(against(100, null), { text: "—", caret: "" });
  assert.equal(savedSentence(7, 74020, 73171), "Week 7: $74,020. +$849 ▲ against the plan.");
  assert.equal(savedSentence(2, -1820, 2000), "Week 2: −$1,820, a loss. −$3,820 ▼ against the plan.");
  assert.equal(savedSentence(3, 500, null), "Week 3: $500.");
  assert.equal(savedSentence(3, 500, 500), "Week 3: $500. $0 against the plan.");
});

// ── the weeks chart ────────────────────────────────────────────────────────

test("a week not written breaks the line: a new run starts after the gap", () => {
  const pts = [{ n: 1, v: 60000 }, { n: 2, v: 70000 }, { n: 3, v: 71000 }, { n: 5, v: 74000 }, { n: 6, v: 72880 }];
  assert.deepEqual(chartSegments(pts).map((run) => run.map((p) => p.n)), [[1, 2, 3], [5, 6]]);
  assert.deepEqual(chartSegments([{ n: 4, v: 1 }, { n: 2, v: 1 }, { n: 3, v: 1 }]).map((r) => r.map((p) => p.n)), [[2, 3, 4]],
    "the order written in is not the order drawn");
  assert.deepEqual(chartSegments([{ n: 1, v: 1 }, { n: 2, v: null }, { n: 3, v: 1 }]).map((r) => r.map((p) => p.n)), [[1], [3]],
    "a week with no total is not joined across");
});

test("the path moves (M) across a gap and never draws (L) over it", () => {
  const pts = [{ n: 1, v: 0 }, { n: 2, v: 10 }, { n: 4, v: 10 }];
  const d = chartPath(pts, (n) => n * 10, (v) => 100 - v);
  assert.equal(d, "M10.0 100.0 L20.0 90.0 M40.0 90.0");
  assert.equal((d.match(/M/g) || []).length, 2);
});

test("the axis always holds zero, rounds its top, and goes below zero only for a loss", () => {
  assert.equal(niceCeil(75930), 80000);
  assert.equal(niceCeil(9480), 9500);
  assert.equal(niceCeil(0), 0);
  assert.deepEqual(chartScale([72880, 74020, 73171]), { lo: 0, hi: 75000 });
  assert.deepEqual(chartScale([9480, -1820]), { lo: -2000, hi: 9500 });
  assert.deepEqual(chartScale([]), { lo: 0, hi: 1 });
});

test("the chart draws a dot and a label for written weeks only, and nothing for the gap", () => {
  const html = drawChart([{ n: 1, v: 60000 }, { n: 2, v: 70000 }, { n: 5, v: 74000 }], 73171);
  assert.equal((html.match(/class="lb-dot"/g) || []).length, 3);
  assert.equal((html.match(/class="lb-xlabel"/g) || []).length, 3);
  assert.doesNotMatch(html, /wk 3|wk 4/);
  assert.match(html, /class="lb-plan-line"/);
  assert.match(html, /data-zero="yes"/);
  assert.equal(drawChart([], 100), "", "no week written, no chart");
});

// ── the book ───────────────────────────────────────────────────────────────

test("the book writes costs with their sign, an unwritten line as a dash, newest first", () => {
  const plan = { moneyIn: 86000, goods: 10000, wages: 940, rent: 2359, ads: 0, deliveries: 400, units: null, customers: 1459, total: 73171 };
  const html = drawBook([wk(5, 80000, { goods: 9000 }), wk(6, 93561, { goods: 15363, wages: 2268 })], plan);
  const desk = html.split('class="lb-book-phone"')[0];
  assert.ok(desk.indexOf("Week 6") < desk.indexOf("Week 5"), "the newest week is not first");
  assert.match(desk, /−\$15,363/);
  assert.match(desk, /\$0/, "the plan's $0 advertising is a fact");
  assert.match(desk, /Against the plan/);
  assert.match(desk, /\+\$2,759/);
  const rent = desk.split("Rent")[1].split("lb-book-row")[0];
  assert.match(rent, /—/, "a rent that was not written reads as nothing, not $0");
  assert.match(html, /data-book-week="6" aria-pressed="true"/, "the phone opens on the newest week");
});
