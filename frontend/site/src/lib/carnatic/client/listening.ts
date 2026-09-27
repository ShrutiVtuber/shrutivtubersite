/* The Listening room in the browser (LISTENING.md; artboards R1-R6):
 * recording cards (click to load; Shruti's section marks seek the player),
 * suggesting a recording, guess the raga (listen, guess, reveal), and
 * tapping along with a recording's beat map.
 */
import { calibratedOffset, calibrateButton, timingSelect, windowsNow } from "./timing";
import { rate } from "../beatclock";
import { loadPlayer, type Player } from "./embed";
import { boot, csrf } from "./state";
import { ctx, talaSound } from "./audio";
import { recordAttempt } from "./learner";
import { ragaKey } from "../answers";
import { judge, type Gesture } from "../gestures";
import { attachPad, clapsOnly, clapsOnlyToggle } from "./tappad";

const esc = (s: string) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const toS = (t?: string | null) => (t ? t.split(":").reduce((a, x) => a * 60 + Number(x), 0) : undefined);
const clock = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

async function send(method: string, path: string, body?: unknown) {
  const r = await fetch(path, { method, headers: { "content-type": "application/json", "x-csrf-token": csrf() }, body: body === undefined ? undefined : JSON.stringify(body) });
  let data: any = null;
  try { data = await r.json(); } catch { /* empty */ }
  return { ok: r.ok, status: r.status, data };
}

/** Recording cards: load on click; a section chip loads (if needed) and seeks. */
export function hydrateCards(root: ParentNode = document) {
  root.querySelectorAll<HTMLElement>("[data-rec-card]").forEach((card) => {
    let player: Player | null = null;
    const box = card.querySelector<HTMLElement>("[data-player]")!;
    const load = (start?: number) => {
      if (player) { if (start !== undefined) player.seek(start); return; }
      player = loadPlayer(box, card.dataset.provider!, card.dataset.url!, { start: start ?? toS(card.dataset.start), end: start !== undefined ? undefined : toS(card.dataset.end) });
    };
    card.querySelector("[data-load]")?.addEventListener("click", () => load());
    card.querySelectorAll<HTMLElement>("[data-seek]").forEach((b) => b.addEventListener("click", () => load(toS(b.dataset.seek))));
  });
}

/** "Suggest a recording" with the learner's own list beside it. */
export function hydrateSuggest(form: HTMLFormElement | null, mine: HTMLElement | null) {
  if (!form) return;
  const note = form.querySelector<HTMLElement>("[data-note]")!;
  const paintMine = async () => {
    if (!mine || !boot().signedIn) return;
    const r = await fetch("/api/carnatic/me/suggestions").then((x) => (x.ok ? x.json() : { items: [] })).catch(() => ({ items: [] }));
    const WORD: Record<string, string> = { pending: "Waiting for Shruti", approved: "Approved · now in the reference list", rejected: "Not added", held: "On hold · Shruti is checking" };
    mine.innerHTML = r.items.length ? r.items.map((s: any) => `<li><span>${esc(s.title || s.url)}</span><small class="${s.status === "approved" ? "ok" : ""}">${esc(WORD[s.status] ?? s.status)}${s.reason ? `: ${esc(s.reason)}` : ""}</small></li>`).join("")
      : `<li><small>Nothing suggested yet.</small></li>`;
    const pending = r.items.filter((s: any) => s.status === "pending").length;
    form.querySelector<HTMLElement>("[data-used]")!.textContent = `${pending} of 5 pending suggestions used`;
  };
  void paintMine();
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!boot().signedIn) { location.href = `/signin?next=${encodeURIComponent(location.pathname)}`; return; }
    const fd = new FormData(form);
    const r = await send("POST", "/api/carnatic/listening/suggestions", Object.fromEntries(fd.entries()));
    if (r.ok) {
      note.textContent = r.data.title ? `Fetched: “${r.data.title}”${r.data.channel ? ` · channel: ${r.data.channel}` : ""}. Thank you: Shruti will look at it.` : "Thank you: Shruti will look at it.";
      form.reset();
      void paintMine();
    } else {
      note.textContent = typeof r.data?.detail === "string" ? r.data.detail : r.data?.detail?.[0]?.msg ?? "That didn't go through. Try again in a moment.";
    }
  });
}

// ── guess the raga ─────────────────────────────────────────────────────────

export interface GuessPage { recordings: { id: string; provider: string; url: string; start?: string; end?: string; n: number }[]; ragas: string[]; href: (p: string) => string; lessons: Record<string, { title: string; slug: string; unit: number }> }

export async function runGuess(root: HTMLElement, page: GuessPage, want?: string | null) {
  let done: string[] = [];
  if (boot().signedIn) done = ((await fetch("/api/carnatic/me/guesses").then((r) => (r.ok ? r.json() : { items: [] })).catch(() => ({ items: [] }))).items ?? []).map((g: any) => g.recording);
  try { done = [...done, ...JSON.parse(localStorage.getItem("swara.guessed") || "[]")]; } catch { /* storage blocked */ }
  const pool = page.recordings.filter((r) => !done.includes(r.id));
  const rec = page.recordings.find((r) => r.id === want) ?? pool[Math.floor(Math.random() * pool.length)] ?? page.recordings[Math.floor(Math.random() * page.recordings.length)];
  if (!rec) { root.innerHTML = `<p class="ch-empty">No recording is ready for guessing yet. The Listening room fills as Shruti approves recordings.</p>`; return; }
  const steps = (n: number) => `<div class="li-steps">${["Listen", "Guess", "Reveal"].map((s, i) => `<span class="${i + 1 === n ? "on" : ""}"><i>${i + 1}</i>${s}</span>`).join("<hr>")}<hr></div>`;
  let confidence = "fairly";
  root.innerHTML = `${steps(1)}<h1 class="lr-title">Which raga is Recording ${rec.n}?</h1>`
    + `<div class="li-guess"><p class="li-peek">The provider's player shows the recording's own title, and so does its site. Try not to look at it: the guess is only for you.</p>`
    + `<div class="li-player" data-box><button type="button" class="lr-btn" data-load>Load Recording ${rec.n}</button><small>Nothing loads from the provider until you press this. It starts at the part Shruti chose.</small></div>`
    + `<form class="li-form" data-form><label>Your guess<span class="li-sugg"><input name="guess" autocomplete="off" required data-in><ul data-sugg hidden></ul></span></label>`
    + `<div><span class="li-form-l">How sure are you?</span><div class="lr-seg" role="group">${[["hunch", "A hunch"], ["fairly", "Fairly sure"], ["sure", "Sure"]].map(([v, l]) => `<button type="button" data-conf="${v}" aria-pressed="${v === confidence}">${l}</button>`).join("")}</div></div>`
    + `<label>What told you? (optional)<textarea name="phrases" rows="3" maxlength="1000"></textarea></label>`
    + `<div class="st-actions" style="justify-content:flex-end"><button class="lr-btn" type="submit">Commit my guess</button></div></form></div>`;
  root.querySelector("[data-load]")!.addEventListener("click", () => {
    loadPlayer(root.querySelector<HTMLElement>("[data-box]")!, rec.provider, rec.url, { start: toS(rec.start), end: toS(rec.end) });
    root.querySelector(".li-steps")!.outerHTML = steps(2);
  });
  root.querySelectorAll<HTMLElement>("[data-conf]").forEach((b) => b.addEventListener("click", () => {
    confidence = b.dataset.conf!;
    root.querySelectorAll<HTMLElement>("[data-conf]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
  }));
  const input = root.querySelector<HTMLInputElement>("[data-in]")!;
  const sugg = root.querySelector<HTMLElement>("[data-sugg]")!;
  input.addEventListener("input", () => {
    const q = ragaKey(input.value);
    const hits = q.length < 2 ? [] : page.ragas.filter((n) => ragaKey(n).startsWith(q) || n.toLowerCase().startsWith(input.value.toLowerCase())).slice(0, 6);
    sugg.hidden = !hits.length;
    sugg.innerHTML = hits.map((h) => `<li><button type="button">${esc(h)}</button></li>`).join("");
    sugg.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { input.value = b.textContent ?? ""; sugg.hidden = true; }));
  });
  root.querySelector<HTMLFormElement>("[data-form]")!.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target as HTMLFormElement);
    const r = await send("POST", "/api/carnatic/listening/guesses", { recording: rec.id, guess: String(fd.get("guess")), confidence, phrases: String(fd.get("phrases") ?? "") });
    if (!r.ok) { root.querySelector(".st-actions")!.insertAdjacentHTML("beforebegin", `<p class="ch-empty">The guess didn't go through. Try again in a moment.</p>`); return; }
    try { localStorage.setItem("swara.guessed", JSON.stringify([...new Set([...done, rec.id])])); } catch { /* storage blocked */ }
    recordAttempt({ itemId: rec.id, kind: "guess", startedAt: new Date().toISOString(), seconds: 0, result: { right: r.data.right, close: r.data.close } });
    const d = r.data;
    const lesson = (d.lessons ?? []).map((id: string) => page.lessons[id]).filter(Boolean)[0];
    const verdict = d.right ? "Yes." : d.close ? `Close: ${d.pair.guessName} and ${d.ragaName} are a pair that's easy to confuse (${d.pair.differ}). The pair is waiting in ear training. We'll bring this recording back later.`
      : "Not this time. We'll bring this recording back later.";
    root.innerHTML = `${steps(3)}<h1 class="lr-title">Recording ${rec.n}</h1><div class="li-guess">`
      + `<div class="li-player" data-box><button type="button" class="lr-btn" data-load>Load the recording</button></div>`
      + `<p class="st-note">${esc([d.composition, d.ragaName, d.recording?.instrument].filter(Boolean).join(" · "))}</p>`
      + `<div class="li-reveal"><div><span class="t-eyebrow">You said</span><b>${esc(String(fd.get("guess")))}</b><small>${esc({ hunch: "a hunch", fairly: "fairly sure", sure: "sure" }[confidence] ?? "")}</small></div>`
      + `<div class="it"><span class="t-eyebrow ch-blue">It was</span><b>${esc(d.ragaName)}</b><small>${esc([d.composition, d.composer].filter(Boolean).join(" · "))}</small></div></div>`
      + `<p class="st-note">${esc(verdict)}</p>`
      + (d.listenFor ? `<p class="lr-reccard-lf"><span class="lr-eyebrow">Listen for</span> ${esc(d.listenFor)}</p>` : "")
      + `<p class="lr-reccard-links"><a href="${esc(page.href(`/carnatic/ragas/${d.raga}`))}">${esc(d.ragaName)} · raga page</a>`
      + (lesson ? `<a href="${esc(page.href(`/carnatic/learn/${lesson.slug}`))}">Unit ${lesson.unit} · ${esc(lesson.title)}</a>` : "")
      + (d.pair ? `<a href="${esc(page.href(`/carnatic/practice/ear/pair/${d.pair.set}`))}">The pair in ear training</a>` : "") + `</p>`
      + (boot().signedIn ? `<p class="lr-reccard-links"><a href="${esc(page.href(`/carnatic/listen/recording/${rec.id}`))}">The analyses of this recording are open to you now ›</a></p>`
        : `<p class="st-note">Its analyses open to members who have guessed it: sign in, and your next guess is kept.</p>`)
      + `<div class="st-actions" style="justify-content:flex-end"><a class="lr-btn" href="${esc(page.href("/carnatic/listen/guess"))}">Another recording</a></div></div>`;
    root.querySelector("[data-load]")!.addEventListener("click", () => loadPlayer(root.querySelector<HTMLElement>("[data-box]")!, rec.provider, rec.url, { start: toS(rec.start) }));
  });
}

// ── tap along with a beat map (K.16, LISTENING.md §6) ──────────────────────

export interface TapAlong { id: string; provider: string; url: string; clipStart?: string; counts: { n: number; action: string; samam?: boolean }[]; samam: number[]; talaName: string }

export function runTapAlong(root: HTMLElement, t: TapAlong) {
  const box = root.querySelector<HTMLElement>("[data-player]")!;
  const grid = root.querySelector<HTMLElement>("[data-grid]")!;
  const avEl = root.querySelector<HTMLElement>("[data-av]")!;
  const note = root.querySelector<HTMLElement>("[data-note]")!;
  const n = t.counts.length;
  grid.style.setProperty("--n", String(Math.min(8, n)));
  grid.innerHTML = t.counts.map((c) => `<span data-c="${c.n - 1}"><b>${c.n}</b>${c.action === "finger" ? "finger" : c.action}</span>`).join("");
  const cells = [...grid.querySelectorAll<HTMLElement>("span")];
  let player: Player | null = null;
  let last = { time: 0, at: 0 };
  // The count times: between two samams the counts are evenly spaced (the beat map's own spacing).
  const countTimes: number[] = [];
  for (let i = 0; i + 1 < t.samam.length; i++) for (let c = 0; c < n; c++) countTimes.push(t.samam[i] + ((t.samam[i + 1] - t.samam[i]) * c) / n);
  const now = () => (player?.time() == null ? null : last.time + (performance.now() - last.at) / 1000);
  const results = { perfect: 0, onTime: 0, early: 0, late: 0, missed: 0 };
  const hit = new Set<number>();
  root.querySelector("[data-load]")?.addEventListener("click", () => {
    player = loadPlayer(box, t.provider, t.url, { start: toS(t.clipStart) ?? Math.max(0, (t.samam[0] ?? 0) - 4) });
    player.onTime((s) => { last = { time: s, at: performance.now() }; });
  });
  let prev = -1;
  const tick = () => {
    const s = now();
    if (s != null) {
      const idx = countTimes.findIndex((x, i) => s >= x && (i + 1 >= countTimes.length || s < countTimes[i + 1]));
      if (idx >= 0 && idx !== prev) {
        prev = idx;
        cells.forEach((c, i) => c.classList.toggle("now", i === idx % n));
        avEl.textContent = `avartanam ${Math.floor(idx / n) + 1} of ${t.samam.length - 1}`;
        if (idx % n === 0) talaSound("clap", ctx().currentTime, { samam: true });
      }
    }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
  const tap = (kind: Gesture, at: number) => {
    // The player's clock at the moment of the tap (the tap's audio time, carried back from now).
    const cur = now();
    const s = cur == null ? null : cur - Math.max(0, ctx().currentTime - at);
    if (s == null) { note.textContent = "Load the recording and press play in its player first: the grid follows it."; return; }
    let best = -1;
    for (let i = 0; i < countTimes.length; i++) if (!hit.has(i) && (best < 0 || Math.abs(countTimes[i] - s) < Math.abs(countTimes[best] - s))) best = i;
    if (best < 0) return;
    // Less this device's calibrated offset; the windows from the Timing setting, capped at 40 % of a count.
    const off = (s - countTimes[best]) * 1000 - (calibratedOffset() ?? 0);
    if (Math.abs(off) > 400) return;
    const w = windowsNow((countTimes[Math.min(best + 1, countTimes.length - 1)] - countTimes[Math.max(0, best - 1)]) / 2 || 1);
    const action = t.counts[best % n]?.action ?? "clap";
    if (clapsOnly() && action !== "clap") { note.textContent = `That count is ${action === "finger" ? "a finger count" : action === "wave" ? "a wave" : "silent"}: shown, not scored.`; return; }
    const v = judge(kind, { kind: action }, clapsOnly());
    if (!v.ok) { note.textContent = v.note; return; }
    hit.add(best);
    const cell = cells[best % n];
    cell.classList.remove("hit", "off");
    const r = rate(off, w);
    cell.classList.add(r === "perfect" || r === "onTime" ? "hit" : "off");
    results[r]++;
    note.textContent = `${results.perfect + results.onTime} on time · ${results.early} early · ${results.late} late`;
  };
  const pad = root.querySelector<HTMLElement>("[data-tap]");
  if (pad) {
    const hint = document.createElement("p");
    hint.className = "tt-hint";
    pad.insertAdjacentElement("afterend", hint);
    attachPad(pad, { onTap: tap, hint });
    const row = document.createElement("div");
    row.className = "tt-settings";
    row.append(clapsOnlyToggle(), timingSelect(), calibrateButton());
    hint.insertAdjacentElement("afterend", row);
  }
  root.querySelector("[data-finish]")?.addEventListener("click", () => {
    const of = hit.size ? Math.max(hit.size, Math.max(...hit) - Math.min(...hit) + 1) : 0;
    recordAttempt({ itemId: "K.16", kind: "tap", startedAt: new Date().toISOString(), seconds: 0, result: { ...results, missed: Math.max(0, of - hit.size), of, recording: t.id } });
    note.textContent = `Kept: ${results.perfect} perfect, ${results.onTime} on time, ${results.early} early, ${results.late} late. Results are for you only.`;
  });
}

export { clock };
