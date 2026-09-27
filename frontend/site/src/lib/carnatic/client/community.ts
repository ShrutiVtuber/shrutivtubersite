/* The rooms in the browser (EXERCISES.md §2, LISTENING.md §4; artboards
 * M1-M13): a piece or an analysis with its rubric ("What readers said"),
 * "This helped me", replies to the whole piece or to one sentence or note,
 * reporting (three distinct reporters hide it until Shruti reviews it;
 * nobody is told who reported), blocking (both ways, nobody told), and the
 * editors: a practice piece with its friendly prechecks, and an analysis of
 * a recording with timestamped notes and guided prompts.
 */
import { publishing } from "../../publish-consent";
import { boot, csrf } from "./state";
import { loadPlayer, type Player } from "./embed";
import { sargamPad } from "./exercise";

const esc = (s: string) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const toS = (t?: string | null) => (t ? t.split(":").reduce((a, x) => a * 60 + Number(x), 0) : undefined);
const clock = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
const API = "/api/carnatic/community";

async function call(method: string, path: string, body?: unknown) {
  const r = await fetch(path, { method, headers: { "content-type": "application/json", "x-csrf-token": csrf() }, body: body === undefined ? undefined : JSON.stringify(body) });
  let data: any = null;
  try { data = await r.json(); } catch { /* 204 */ }
  return { ok: r.ok, status: r.status, data };
}
const detail = (d: any) => (typeof d?.detail === "string" ? d.detail : d?.detail?.detail ?? d?.detail?.[0]?.msg ?? "That didn't go through. Try again in a moment.");
const signIn = () => { location.href = `/signin?next=${encodeURIComponent(location.pathname + location.search)}`; };

const REASON_LABEL: Record<string, string> = {
  "not-about-this-exercise": "Not about music or the brief", spam: "Spam or advertising", abuse: "Rude, hurtful or harassing",
  hate: "Hateful about a group of people", sexual: "Sexual, or involving a minor", "self-harm": "Someone may need help", other: "Something else",
};

/** The report dialog: choose a reason, send, then "Report sent". */
export function report(kind: "work" | "comment", id: number) {
  if (!boot().signedIn) return signIn();
  const d = document.createElement("dialog");
  d.className = "cm-dialog";
  const reasons = ["not-about-this-exercise", "spam", "abuse", "hate", "sexual", "self-harm", "other"];
  let pick = "";
  d.innerHTML = `<h2>Report this ${kind === "work" ? "piece" : "reply"}</h2><p class="cm-soft">Nobody is told who reported, not even Shruti.</p>`
    + `<div class="cm-reasons">${reasons.map((r) => `<button type="button" data-r="${r}">${esc(REASON_LABEL[r])}</button>`).join("")}</div>`
    + `<textarea data-detail rows="2" maxlength="1000" placeholder="Anything Shruti should know (optional)"></textarea>`
    + `<div class="cm-acts"><button type="button" class="lr-link" data-cancel>Cancel</button><button type="button" class="lr-btn" data-send disabled>Send report</button></div>`;
  document.body.append(d);
  d.showModal();
  d.querySelectorAll<HTMLButtonElement>("[data-r]").forEach((b) => b.addEventListener("click", () => {
    pick = b.dataset.r!;
    d.querySelectorAll("[data-r]").forEach((x) => x.classList.toggle("on", x === b));
    d.querySelector<HTMLButtonElement>("[data-send]")!.disabled = false;
  }));
  d.querySelector("[data-cancel]")!.addEventListener("click", () => d.close());
  d.addEventListener("close", () => d.remove());
  d.querySelector("[data-send]")!.addEventListener("click", async () => {
    const r = await call("POST", `${API}/${kind === "work" ? "works" : "comments"}/${id}/report`, { reason: pick, detail: d.querySelector<HTMLTextAreaElement>("[data-detail]")!.value });
    d.innerHTML = r.ok
      ? `<h2>Report sent</h2><p>Thank you. If enough people report the same ${kind === "work" ? "piece" : "reply"}, it's hidden until Shruti looks at it. You won't see it change straight away, and nobody is told who reported.</p>`
        + `<p class="cm-soft">If this is about someone who may need help, Shruti reads those first.</p><div class="cm-acts"><button type="button" class="lr-btn" data-ok>Done</button></div>`
      : `<h2>That didn't go through</h2><p>${esc(detail(r.data))}</p><div class="cm-acts"><button type="button" class="lr-btn" data-ok>Close</button></div>`;
    d.querySelector("[data-ok]")!.addEventListener("click", () => d.close());
  });
}

/** Block: both ways, nobody told. */
export function block(userId: number, name: string) {
  if (!boot().signedIn) return signIn();
  const d = document.createElement("dialog");
  d.className = "cm-dialog";
  d.innerHTML = `<h2>Block ${esc(name)}?</h2><p>You won't see each other's pieces, analyses or replies in the rooms, and neither of you can reply to the other. ${esc(name)} isn't told. You can undo this from your page.</p>`
    + `<div class="cm-acts"><button type="button" class="lr-link" data-cancel>Cancel</button><button type="button" class="lr-btn" data-go>Block</button></div>`;
  document.body.append(d);
  d.showModal();
  d.querySelector("[data-cancel]")!.addEventListener("click", () => d.close());
  d.addEventListener("close", () => d.remove());
  d.querySelector("[data-go]")!.addEventListener("click", async () => {
    const r = await call("POST", `${API}/blocks`, { userId });
    d.innerHTML = r.ok ? `<h2>Blocked</h2><p>Done. This page will close to you now.</p><div class="cm-acts"><button type="button" class="lr-btn" data-ok>Back to the room</button></div>`
      : `<h2>That didn't go through</h2><p>${esc(detail(r.data))}</p><div class="cm-acts"><button type="button" class="lr-btn" data-ok>Close</button></div>`;
    d.querySelector("[data-ok]")!.addEventListener("click", () => { d.close(); if (r.ok) history.back(); });
  });
}

// ── reading a piece ────────────────────────────────────────────────────────

export interface WorkPage { id: number; mine: boolean; authorId: number | null; author: string; rubric: any; voted: boolean; votes: number; suspended: string | null; recording?: { provider: string; url: string; start?: string } | null }

export function hydrateWork(root: HTMLElement, w: WorkPage) {
  // the recording an analysis is about: load on click, notes' times seek it
  let player: Player | null = null;
  const box = root.querySelector<HTMLElement>("[data-player]");
  const load = (at?: number) => {
    if (!w.recording || !box) return;
    if (player) { if (at !== undefined) player.seek(at); return; }
    player = loadPlayer(box, w.recording.provider, w.recording.url, { start: at ?? toS(w.recording.start) });
  };
  root.querySelector("[data-load]")?.addEventListener("click", () => load());
  root.querySelectorAll<HTMLElement>("[data-t]").forEach((b) => b.addEventListener("click", () => load(toS(b.dataset.t))));
  root.querySelectorAll<HTMLElement>("[data-link-load]").forEach((b) => b.addEventListener("click", () => {
    loadPlayer(b.closest<HTMLElement>("[data-link-box]")!, b.dataset.provider!, b.dataset.url!);
  }));

  // vote
  const vote = root.querySelector<HTMLButtonElement>("[data-vote]");
  let voted = w.voted, votes = w.votes;
  const paintVote = () => {
    if (!vote) return;
    vote.setAttribute("aria-pressed", String(voted));
    root.querySelector("[data-votes]")!.textContent = `${votes} found this helpful · one vote each`;
  };
  vote?.addEventListener("click", async () => {
    if (!boot().signedIn) return signIn();
    const r = await call(voted ? "DELETE" : "PUT", `${API}/works/${w.id}/vote`);
    if (r.ok) { voted = !voted; votes += voted ? 1 : -1; paintVote(); }
  });
  paintVote();

  // rubric: one set per person, shown as totals
  const answers: Record<string, string> = { ...(w.rubric?.mine ?? {}) };
  root.querySelectorAll<HTMLElement>("[data-q]").forEach((row) => {
    const q = row.dataset.q!;
    row.querySelectorAll<HTMLButtonElement>("[data-a]").forEach((b) => b.addEventListener("click", async () => {
      if (!boot().signedIn) return signIn();
      if (w.mine) return;
      answers[q] = b.dataset.a!;
      const r = await call("PUT", `${API}/works/${w.id}/rubric`, { answers });
      if (!r.ok) return;
      row.querySelectorAll("[data-a]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      const totals = r.data?.totals?.[q];
      if (totals) row.querySelector("[data-totals]")!.textContent = Object.entries(totals).map(([k, v]) => `${k} ${v}`).join("   ");
    }));
  });
  root.querySelectorAll<HTMLTextAreaElement>("[data-free]").forEach((t) => t.addEventListener("change", async () => {
    if (!boot().signedIn) return signIn();
    answers[t.dataset.free!] = t.value;
    await call("PUT", `${API}/works/${w.id}/rubric`, { answers });
  }));

  // replies
  const list = root.querySelector<HTMLElement>("[data-replies]")!;
  const count = root.querySelector<HTMLElement>("[data-reply-count]")!;
  const form = root.querySelector<HTMLFormElement>("[data-reply-form]");
  let part: string | null = null;
  const chip = root.querySelector<HTMLElement>("[data-reply-part]");
  const setPart = (p: string | null, label?: string) => {
    part = p;
    root.querySelectorAll(".cm-sel").forEach((x) => x.classList.remove("cm-sel"));
    if (p) root.querySelector(`[data-part="${CSS.escape(p)}"]`)?.classList.add("cm-sel");
    if (chip) { chip.hidden = !p; chip.querySelector("span")!.textContent = label ?? ""; }
  };
  chip?.querySelector("button")?.addEventListener("click", () => setPart(null));
  root.querySelectorAll<HTMLElement>("[data-part]").forEach((el) => el.addEventListener("click", () => {
    if (!form) return;
    setPart(el.dataset.part!, el.dataset.partLabel ?? `on “${(el.textContent ?? "").trim().slice(0, 40)}…”`);
    form.querySelector("textarea")?.focus();
  }));
  const draw = (items: any[]) => {
    count.textContent = `${items.length} repl${items.length === 1 ? "y" : "ies"}`;
    list.innerHTML = items.map((c) => `<li data-c="${c.id}"><p class="cm-by"><b>${esc(c.author)}</b> <span>${esc(new Date(c.createdAt).toLocaleDateString("en-GB", { day: "numeric", month: "short" }))}</span>`
      + (c.partLabel ? ` <span class="cm-pill">${esc(c.partLabel)}</span>` : "") + (c.hidden ? ` <span class="cm-pill">hidden while Shruti reviews reports</span>` : "") + `</p>`
      + `<p class="cm-body">${esc(c.body)}</p><p class="cm-acts-row">${form ? `<button type="button" class="lr-link" data-reply-to="${esc(c.part ?? "")}" data-label="${esc(c.partLabel ?? "")}">Reply</button>` : ""}`
      + (c.mine ? `<button type="button" class="lr-link" data-del="${c.id}">Delete</button>` : `<button type="button" class="lr-link" data-rep="${c.id}">Report</button>`) + `</p></li>`).join("");
    list.querySelectorAll<HTMLElement>("[data-rep]").forEach((b) => b.addEventListener("click", () => report("comment", Number(b.dataset.rep))));
    list.querySelectorAll<HTMLElement>("[data-del]").forEach((b) => b.addEventListener("click", async () => { await call("DELETE", `${API}/comments/${b.dataset.del}`); void refresh(); }));
    list.querySelectorAll<HTMLElement>("[data-reply-to]").forEach((b) => b.addEventListener("click", () => { setPart(b.dataset.replyTo || null, b.dataset.label); form?.querySelector("textarea")?.focus(); }));
  };
  const refresh = async () => {
    const r = await fetch(`${API}/works/${w.id}/comments`).then((x) => (x.ok ? x.json() : { items: [] })).catch(() => ({ items: [] }));
    draw(r.items);
  };
  void refresh();
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!boot().signedIn) return signIn();
    const t = form.querySelector("textarea")!;
    if (!t.value.trim()) return;
    const r = await call("POST", `${API}/works/${w.id}/comments`, { body: t.value, part });
    if (r.ok) { t.value = ""; setPart(null); void refresh(); }
    else form.querySelector("[data-reply-note]")!.textContent = detail(r.data);
  });

  // the ⋯ menu
  const menu = root.querySelector<HTMLElement>("[data-menu]");
  root.querySelector("[data-menu-btn]")?.addEventListener("click", () => { if (menu) menu.hidden = !menu.hidden; });
  root.querySelector("[data-report-work]")?.addEventListener("click", () => { if (menu) menu.hidden = true; report("work", w.id); });
  root.querySelector("[data-block]")?.addEventListener("click", () => { if (menu) menu.hidden = true; if (w.authorId) block(w.authorId, w.author); });
  root.querySelector("[data-withdraw]")?.addEventListener("click", async () => {
    if (!confirm("Take this piece out of the room? Replies stay with it, out of sight.")) return;
    const r = await call("POST", `${API}/works/${w.id}/withdraw`);
    if (r.ok) location.reload();
  });
}

// ── writing ────────────────────────────────────────────────────────────────

export interface EditorPage {
  room: "carnatic-practice" | "carnatic-analysis"; subject: string; title: string; draftId: number | null;
  words?: [number, number] | null; parts: { key: string; body: string; data?: any }[];
  recording?: { provider: string; url: string; start?: string; end?: string } | null;
  script: any; tamil: any; roomHref: string; categories?: string[];
}

export function hydrateEditor(root: HTMLElement, p: EditorPage) {
  let id = p.draftId;
  const saved = root.querySelector<HTMLElement>("[data-saved]")!;
  const hints = root.querySelector<HTMLElement>("[data-hints]");
  const note = root.querySelector<HTMLElement>("[data-note]")!;
  const text = root.querySelector<HTMLTextAreaElement>("[data-text]");
  const count = root.querySelector<HTMLElement>("[data-count]");
  const link = root.querySelector<HTMLInputElement>("[data-link]");
  const title = root.querySelector<HTMLInputElement>("[data-title]");
  const summary = root.querySelector<HTMLTextAreaElement>("[data-summary]");
  const padHost = root.querySelector<HTMLElement>("[data-sargam]");
  const pad = padHost ? sargamPad(padHost, { script: p.script, tamil: p.tamil }, p.parts.find((x) => x.key === "sargam")?.body ?? "") : null;
  const notes: { t: string; category: string; body: string; notation?: string }[] = p.parts.filter((x) => x.key.startsWith("note:")).map((x) => ({ t: x.data?.t ?? "", category: x.data?.category ?? "other", body: x.body, notation: x.data?.notation }));
  const words = (s: string) => (s.trim() ? s.trim().split(/\s+/).length : 0);
  const paintCount = () => {
    if (text && count) count.textContent = `${words(text.value)} words${p.words ? ` · ${p.words[0]}-${p.words[1]}` : ""}`;
    const sc = root.querySelector<HTMLElement>("[data-scount]");
    if (summary && sc) sc.textContent = `${words(summary.value)} of up to 400 words`;
  };
  text?.addEventListener("input", paintCount);
  summary?.addEventListener("input", paintCount);
  paintCount();

  // the analysis player and notes
  let player: Player | null = null;
  const box = root.querySelector<HTMLElement>("[data-player]");
  const nowT = root.querySelector<HTMLElement>("[data-now]");
  root.querySelector("[data-load]")?.addEventListener("click", () => {
    if (!p.recording || !box) return;
    player = loadPlayer(box, p.recording.provider, p.recording.url, { start: toS(p.recording.start) });
    player.onTime((s) => { if (nowT) nowT.textContent = clock(s); const at = root.querySelector<HTMLInputElement>("[data-at]"); if (at && !at.dataset.touched) at.value = clock(s); });
  });
  const noteList = root.querySelector<HTMLElement>("[data-notes]");
  const drawNotes = () => {
    if (!noteList) return;
    notes.sort((a, b) => (toS(a.t) ?? 0) - (toS(b.t) ?? 0));
    noteList.innerHTML = notes.map((n, i) => `<li><button type="button" class="an-t" data-seek="${esc(n.t)}">${esc(n.t)}</button><div><span class="an-cat">${esc(n.category)}</span>${n.notation ? ` <span class="an-not">${esc(n.notation)}</span>` : ""}<p>${esc(n.body)}</p></div><button type="button" class="lr-link" data-rm="${i}">Remove</button></li>`).join("");
    noteList.querySelectorAll<HTMLElement>("[data-seek]").forEach((b) => b.addEventListener("click", () => player?.seek(toS(b.dataset.seek) ?? 0)));
    noteList.querySelectorAll<HTMLElement>("[data-rm]").forEach((b) => b.addEventListener("click", () => { notes.splice(Number(b.dataset.rm), 1); drawNotes(); }));
  };
  drawNotes();
  let cat = "phrase";
  root.querySelectorAll<HTMLElement>("[data-cat]").forEach((b) => b.addEventListener("click", () => {
    cat = b.dataset.cat!;
    root.querySelectorAll("[data-cat]").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
  }));
  root.querySelector<HTMLInputElement>("[data-at]")?.addEventListener("input", (e) => { (e.target as HTMLElement).dataset.touched = "1"; });
  root.querySelector("[data-add-note]")?.addEventListener("click", () => {
    const at = root.querySelector<HTMLInputElement>("[data-at]")!;
    const body = root.querySelector<HTMLTextAreaElement>("[data-note-body]")!;
    const nota = root.querySelector<HTMLInputElement>("[data-note-notation]");
    if (!body.value.trim() || toS(at.value) === undefined || Number.isNaN(toS(at.value))) { note.textContent = "A note needs a time (m:ss) and what you hear."; return; }
    notes.push({ t: at.value.trim(), category: cat, body: body.value.trim(), ...(nota?.value.trim() ? { notation: nota.value.trim() } : {}) });
    body.value = ""; if (nota) nota.value = ""; delete at.dataset.touched;
    note.textContent = "";
    drawNotes();
  });

  const parts = () => {
    const out: { key: string; body: string; data?: any }[] = [];
    if (text?.value.trim()) out.push({ key: "text", body: text.value.trim() });
    if (pad?.value().trim()) out.push({ key: "sargam", body: pad.value().trim(), data: padHost?.dataset ? { raga: padHost.dataset.raga, tala: padHost.dataset.tala, speed: padHost.dataset.speed } : {} });
    if (link?.value.trim()) out.push({ key: "link", body: link.value.trim() });
    notes.forEach((n, i) => out.push({ key: `note:${i + 1}`, body: n.body, data: { t: n.t, category: n.category, ...(n.notation ? { notation: n.notation } : {}) } }));
    if (summary?.value.trim()) out.push({ key: "summary", body: summary.value.trim() });
    return out;
  };
  const save = async (): Promise<boolean> => {
    if (!boot().signedIn) { signIn(); return false; }
    const body = { room: p.room, subject: p.subject, title: title?.value.trim() || p.title, parts: parts() };
    const r = id ? await call("PUT", `${API}/works/${id}`, { title: body.title, parts: body.parts }) : await call("POST", `${API}/works`, body);
    if (!r.ok) { note.textContent = detail(r.data); return false; }
    if (!id) { id = r.data.id; history.replaceState(null, "", `?draft=${id}`); }
    saved.textContent = `Draft · saved ${new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })}`;
    if (hints) {
      const h = await call("POST", `${API}/works/${id}/hints`);
      const list: string[] = h.data?.hints ?? [];
      hints.innerHTML = list.length ? list.map((x) => `<p>${esc(x)}</p>`).join("") : `<p>✓ Nothing to point out.</p>`;
    }
    return true;
  };
  root.querySelector("[data-save]")?.addEventListener("click", () => void save());
  root.querySelector("[data-submit]")?.addEventListener("click", async () => {
    if (!(await save())) return;
    const r = await publishing(() => fetch(`${API}/works/${id}/submit`, { method: "POST", headers: { "content-type": "application/json", "x-csrf-token": csrf() } }));
    if (r.ok) { location.href = `/carnatic/room/${id}`; return; }
    let d: any = null;
    try { d = await r.json(); } catch { /* none */ }
    note.textContent = r.status === 428 ? "Publishing needs your agreement first; nothing was published." : detail(d);
  });
}
