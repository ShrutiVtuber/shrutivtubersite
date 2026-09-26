/* Publish, and if the backend says the agreement is not on file yet, ask.
 *
 *   const r = await publishing(() => fetch(url, { method: "POST", … }));
 *
 * The request is sent as it is. A 428 means the person has not yet agreed to
 * what happens to public work when an account is deleted (see
 * `backend/shruti/core/publishing.py`): the dialog from
 * `components/feedback/PublishConsent.astro` opens, and on agreement the
 * decision is filed and the SAME request is sent once more. Anything else —
 * success, a refusal, a network error — comes back untouched, so a caller's
 * existing handling is unchanged.
 *
 * ⚠ The dialog must be on the page. A page that can publish renders
 * <PublishConsent /> once; without it this returns the 428 as it came, whose
 * detail sentence already says where to agree.
 */
import { PUBLISH_CONSENT } from "./consents";

const csrf = () =>
  document.cookie.split("; ").find((c) => c.startsWith("shruti_csrf="))?.split("=")[1] ?? "";

function ask(): Promise<boolean> {
  const dialog = document.querySelector<HTMLDialogElement>("[data-publish-consent]");
  if (!dialog || typeof dialog.showModal !== "function") return Promise.resolve(false);
  const box = dialog.querySelector<HTMLInputElement>('input[name="publish"]')!;
  const agree = dialog.querySelector<HTMLButtonElement>("[data-publish-consent-agree]")!;
  const cancel = dialog.querySelector<HTMLButtonElement>("[data-publish-consent-cancel]")!;
  const failed = dialog.querySelector<HTMLElement>("[data-publish-consent-failed]")!;

  // `Button` marks a disabled button twice — the property and a
  // `data-disabled` its styles read — so both move together.
  const enable = (on: boolean) => { agree.disabled = !on; agree.toggleAttribute("data-disabled", !on); };

  // Never pre-ticked: every opening starts from no.
  box.checked = false;
  enable(false);
  failed.hidden = true;

  return new Promise((resolve) => {
    const done = (answer: boolean) => {
      box.removeEventListener("change", onTick);
      agree.removeEventListener("click", onAgree);
      cancel.removeEventListener("click", onCancel);
      dialog.removeEventListener("close", onClose);
      if (dialog.open) dialog.close();
      resolve(answer);
    };
    const onTick = () => enable(box.checked);
    const onCancel = (e: Event) => { e.preventDefault(); done(false); };
    const onClose = () => done(false);                 // Escape
    const onAgree = async (e: Event) => {
      e.preventDefault();
      if (!box.checked) return;
      enable(false);
      const r = await fetch("/api/account/consents", {
        method: "POST",
        headers: { "content-type": "application/json", "x-csrf-token": csrf() },
        body: JSON.stringify({ kind: PUBLISH_CONSENT.kind, granted: true, source: "publish-dialog" }),
      }).catch(() => null);
      if (r?.ok) { done(true); return; }
      failed.hidden = false;
      enable(true);
    };
    box.addEventListener("change", onTick);
    agree.addEventListener("click", onAgree);
    cancel.addEventListener("click", onCancel);
    dialog.addEventListener("close", onClose);
    dialog.showModal();
  });
}

export async function publishing(send: () => Promise<Response>): Promise<Response> {
  const first = await send();
  if (first.status !== 428) return first;
  return (await ask()) ? send() : first;
}
