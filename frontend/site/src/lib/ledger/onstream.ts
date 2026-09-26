/* This ledger on stream, and the one-tap switch (design_handoff_ledger_overlays
 * README §6), mounted onto OnStream.astro and SwitchBar.astro.
 *
 *   mint     POST   /api/ledger/ledgers/{id}/overlays   → the token, shown once
 *   list     (drawn by the server; kept here as rows are minted and revoked)
 *   revoke   DELETE /api/ledger/ledgers/{id}/overlays/{tokenId}, after an inline "Revoke it"
 *   switch   PUT    /api/ledger/ledgers/{id}/on-screen  {businessId}
 *
 * ⚠ The address is shown once, in the shown-once field, and never again: the
 *   list names an overlay by kind, theme, motion and date, never by address.
 * ⚠ The full address is this page's origin + the path the API returns.
 * ⚠ The switch bar is there only while at least one overlay of this ledger is
 *   minted; revoking the last one takes it away.
 *
 * `tokenRow` is pure, so the server draws the first list with it.
 */
import { escape, fill, shortDate } from "./format.ts";

export type Words = Record<string, string>;
const W = (w: Words, k: string, f = "") => (k in w ? w[k] : f || k);

export interface StreamToken { id: number; kind: string; theme: string; motion: string; createdAt: string | null; label?: string }

/** One minted overlay, by kind, theme, motion and date — never by its address. */
export function tokenRow(t: StreamToken, w: Words): string {
  const meta = fill(W(w, "row.meta", "{theme} theme · {motion} · minted {date}"), {
    theme: W(w, `theme.${t.theme}`, t.theme), motion: W(w, `motion.${t.motion}`, t.motion), date: t.createdAt ? shortDate(t.createdAt) : "",
  });
  return `<li class="lb-token" data-token="${t.id}">
    <span class="lb-token-text"><span class="lb-token-kind">${escape(W(w, `kind.${t.kind}`, t.kind))}</span><span class="lb-token-meta">${escape(meta)}</span></span>
    <span class="lb-token-act">
      <button type="button" class="lg-link" data-revoke>${escape(W(w, "revoke", "Revoke"))}</button>
      <span class="lb-token-confirm" data-confirm hidden>
        <span>${escape(W(w, "revoke.confirm", "OBS stops showing it at once."))}</span>
        <button type="button" class="lg-btn" data-variant="secondary" data-size="sm" data-revoke-yes>${escape(W(w, "revoke.yes", "Revoke it"))}</button>
        <button type="button" class="lg-link" data-revoke-no>${escape(W(w, "revoke.no", "Keep it"))}</button>
      </span>
    </span>
  </li>`;
}

export const PLAN_KINDS = ["ledger-plan-panel", "ledger-plan-card"];

async function send(path: string, method: string, body?: unknown): Promise<{ ok: boolean; status: number; body: any }> {
  try {
    const r = await fetch(path, {
      method, credentials: "same-origin",
      headers: { accept: "application/json", ...(body === undefined ? {} : { "content-type": "application/json" }) },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const said = r.status === 204 ? null : await r.json().catch(() => null);
    return { ok: r.ok, status: r.status, body: said };
  } catch {
    return { ok: false, status: 0, body: null };
  }
}

interface State { ledgerId: number; open: { id: number; name: string }[]; onScreen: number | null; tokens: StreamToken[] }

/** Mount the console and the switch bar found under `scope`. Either may be absent. */
export function mountOnStream(scope: ParentNode = document): void {
  const box = scope.querySelector<HTMLElement>("[data-stream]");
  const bar = scope.querySelector<HTMLElement>("[data-switch]");
  const host = box ?? bar;
  if (!host) return;
  let words: Words = {};
  let state: State;
  try { words = JSON.parse(host.dataset.words || "{}"); } catch { /* the defaults */ }
  try { state = JSON.parse(host.dataset.state || "{}"); } catch { return; }
  if (!state?.ledgerId) return;
  const base = `/api/ledger/ledgers/${state.ledgerId}`;
  const current = () => state.onScreen ?? state.open[0]?.id ?? null;
  const nameOf = (id: number | null) => state.open.find((b) => b.id === id)?.name ?? "";

  // ── choices ────────────────────────────────────────────────────────────
  let kind = box?.querySelector<HTMLElement>("[data-kind][aria-pressed='true']")?.dataset.kind ?? "ledger-plate";
  let edge = "";
  const theme = () => box?.querySelector<HTMLInputElement>("input[data-theme-pick]:checked")?.value ?? "ledger";
  const motion = () => box?.querySelector<HTMLInputElement>("input[data-motion-pick]:checked")?.value ?? "full";

  function summary() {
    if (!box) return;
    const out = [W(words, `kind.${kind}`, kind), fill(W(words, "summary.theme", "{theme} theme"), { theme: W(words, `theme.${theme()}`, theme()) }),
      W(words, `motionName.${motion()}`, motion())];
    if (!PLAN_KINDS.includes(kind) && current() != null) out.push(fill(W(words, "summary.on", "{business} on screen"), { business: nameOf(current()) }));
    const s = box.querySelector<HTMLElement>("[data-summary]");
    if (s) s.textContent = out.join(" · ");
  }

  function drawKind() {
    if (!box) return;
    box.querySelectorAll<HTMLElement>("[data-kind]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.kind === kind)));
    const note = box.querySelector<HTMLElement>("[data-kind-note]");
    if (note) note.textContent = W(words, `kindNote.${kind}`);
    const edges = box.querySelector<HTMLElement>("[data-edges]");
    if (edges) edges.hidden = kind !== "ledger-strip";
    const who = box.querySelector<HTMLElement>("[data-who]");
    if (who) who.hidden = PLAN_KINDS.includes(kind);
    summary();
  }

  function drawOnScreen(sent = false) {
    const on = current();
    scope.querySelectorAll<HTMLElement>("[data-on]").forEach((b) => {
      const yes = Number(b.dataset.on) === on;
      if (b.getAttribute("role") === "radio") b.setAttribute("aria-checked", String(yes));
      else b.setAttribute("aria-pressed", String(yes));
    });
    const name = bar?.querySelector<HTMLElement>("[data-switch-name]");
    if (name) name.textContent = nameOf(on);
    const note = bar?.querySelector<HTMLElement>("[data-switch-note]");
    if (note) note.textContent = sent ? W(words, "switch.sent", "sent · on stream within a second") : liveNote();
    summary();
  }

  function liveNote(): string {
    const latest = [...state.tokens].reverse().find((t) => !PLAN_KINDS.includes(t.kind)) ?? state.tokens[state.tokens.length - 1];
    return latest ? fill(W(words, "switch.live", "{kind} · live"), { kind: W(words, `kind.${latest.kind}`, latest.kind) }) : "";
  }

  function drawTokens() {
    const list = box?.querySelector<HTMLElement>("[data-tokens]");
    if (list) list.innerHTML = state.tokens.map((t) => tokenRow(t, words)).join("");
    const none = box?.querySelector<HTMLElement>("[data-tokens-none]");
    if (none) none.hidden = state.tokens.length > 0;
    // The bar is there only while something of this ledger is minted, and only when there is a business to put on screen.
    if (bar) bar.hidden = !state.tokens.length || !state.open.length;
    drawOnScreen();
  }

  function refuse(text: string) {
    const r = box?.querySelector<HTMLElement>("[data-stream-refusal]");
    if (!r) return;
    r.hidden = !text;
    const t = r.querySelector<HTMLElement>(".lg-note-text");
    if (t) t.textContent = text;
  }

  // ── events ─────────────────────────────────────────────────────────────
  box?.addEventListener("change", (e) => {
    const t = e.target as HTMLElement;
    if (t.matches("input[data-theme-pick], input[data-motion-pick]")) summary();
  });

  let putting = 0;
  async function putOnScreen(id: number) {
    if (id === current()) return;
    const was = state.onScreen;
    state.onScreen = id;
    drawOnScreen(true);
    const mine = ++putting;
    const said = await send(`${base}/on-screen`, "PUT", { businessId: id });
    if (!said.ok && mine === putting) { state.onScreen = was; drawOnScreen(); }
  }

  scope.addEventListener("click", async (e) => {
    const t = e.target as HTMLElement;
    const onBtn = t.closest<HTMLElement>("[data-on]");
    if (onBtn && (box?.contains(onBtn) || bar?.contains(onBtn))) { await putOnScreen(Number(onBtn.dataset.on)); return; }
    if (!box || !box.contains(t)) return;

    const kindBtn = t.closest<HTMLElement>("[data-kind]");
    if (kindBtn) { kind = kindBtn.dataset.kind || kind; drawKind(); return; }
    const edgeBtn = t.closest<HTMLElement>("[data-edge]");
    if (edgeBtn) {
      edge = edgeBtn.dataset.edge || "";
      box.querySelectorAll<HTMLElement>("[data-edge]").forEach((b) => b.setAttribute("aria-pressed", String(b === edgeBtn)));
      return;
    }

    if (t.closest("[data-mint]")) {
      const btn = t.closest<HTMLButtonElement>("[data-mint]")!;
      btn.disabled = true;
      refuse("");
      const said = await send(`${base}/overlays`, "POST", { kind, theme: theme(), motion: motion(), shows: kind === "ledger-strip" ? edge : "" });
      btn.disabled = false;
      if (!said.ok || !said.body?.token) {
        refuse(typeof said.body?.detail === "string" ? said.body.detail : W(words, "failed", "That did not go through. Nothing was minted; try again."));
        return;
      }
      const once = box.querySelector<HTMLElement>("[data-once]");
      const url = box.querySelector<HTMLInputElement>("[data-once-url]");
      if (url) url.value = `${location.origin}${said.body.path}`;
      const copyBtn = box.querySelector<HTMLElement>("[data-copy]");
      if (copyBtn) copyBtn.textContent = W(words, "copy", "Copy");
      if (once) once.hidden = false;
      state.tokens.push({ id: said.body.id, kind: said.body.kind, theme: said.body.theme, motion: said.body.motion, createdAt: said.body.createdAt });
      drawTokens();
      url?.focus();
      url?.select();
      return;
    }

    if (t.closest("[data-copy]")) {
      const url = box.querySelector<HTMLInputElement>("[data-once-url]");
      const copyBtn = t.closest<HTMLElement>("[data-copy]")!;
      if (!url?.value) return;
      try { await navigator.clipboard.writeText(url.value); copyBtn.textContent = W(words, "copied", "Copied"); }
      catch { url.focus(); url.select(); }
      return;
    }

    const row = t.closest<HTMLElement>("[data-token]");
    if (!row) return;
    const confirm = row.querySelector<HTMLElement>("[data-confirm]");
    const ask = row.querySelector<HTMLElement>("[data-revoke]");
    if (t.closest("[data-revoke]")) {
      if (confirm) confirm.hidden = false;
      if (ask) ask.hidden = true;
      row.querySelector<HTMLElement>("[data-revoke-yes]")?.focus();
      return;
    }
    if (t.closest("[data-revoke-no]")) {
      if (confirm) confirm.hidden = true;
      if (ask) { ask.hidden = false; ask.focus(); }
      return;
    }
    if (t.closest("[data-revoke-yes]")) {
      const id = Number(row.dataset.token);
      const said = await send(`${base}/overlays/${id}`, "DELETE");
      if (!said.ok && said.status !== 404) { refuse(W(words, "revokeFailed", "That did not go through. The overlay still draws; try again.")); return; }
      state.tokens = state.tokens.filter((x) => x.id !== id);
      drawTokens();
    }
  });

  drawKind();
  drawTokens();
}
