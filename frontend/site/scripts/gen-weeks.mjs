/* Every week id the site computes for a long stretch of days, plus the days
 * each id maps back to. The app's Dart is held against this — ISO weeks are
 * subtle enough (Thursday decides the year) that agreeing with my own reading
 * of the rule proves nothing. */
import { isoWeek, weekDays, currentCovers } from "../src/lib/periods.ts";

const out = [];
// Fifteen years, including every awkward new year.
for (let t = Date.UTC(2020, 0, 1); t <= Date.UTC(2035, 0, 10); t += 86400000) {
  const d = new Date(t);
  const id = isoWeek(d);
  out.push({ day: d.toISOString().slice(0, 10), week: id, days: weekDays(id) });
}
console.log(JSON.stringify(out));
