/* The three consents, mirrored for rendering.
 *
 * The wording here must match `backend/shruti/core/consents.py` exactly,
 * because what is SHOWN is what gets STORED with the record — a form that
 * displays one sentence and files another is worse than no record at all.
 * A test asserts they agree.
 */
export const CONSENT_VERSION = "2026-09-26.1";

export interface ConsentSpec {
  kind: "account" | "nativity" | "newsletter" | "publish";
  label: string;
  wording: string;
  basis: "contract" | "consent" | "explicit-consent";
  required: boolean;
  explanation: string;
}

export const CONSENTS: ConsentSpec[] = [
  {
    kind: "account",
    label: "Create the account",
    wording:
      "I want an account on shrutivtuber.com. My email address and the " +
      "preferences I set are stored so I can sign in and read what I have " +
      "saved.",
    basis: "contract",
    required: true,
    explanation:
      "This is the account itself — an email address and the settings you " +
      "choose. Without it there is nothing to sign in to.",
  },
  {
    kind: "nativity",
    label: "Store my birth data for astrological readings",
    wording:
      "I consent to shrutivtuber.com storing my birth date, birth time and " +
      "birth place, and using them to compute astrological readings for me. " +
      "I understand this may reveal something about my philosophical beliefs, " +
      "and that I can withdraw this consent at any time, which deletes the " +
      "birth data.",
    basis: "explicit-consent",
    required: false,
    explanation:
      "Birth data used to produce an astrological reading arguably reveals " +
      "philosophical belief, which makes it special-category data. So it " +
      "gets its own decision, it is never required, and withdrawing it " +
      "deletes the saved nativity — the account survives.",
  },
  {
    kind: "newsletter",
    label: "Send me the monthly letter",
    wording:
      "I want the monthly letter by email, including offers for astrological " +
      "courses and magickal services when those open. I can unsubscribe in " +
      "one click from any issue.",
    basis: "consent",
    required: false,
    explanation:
      "One letter a month. It carries commercial offers when there are any, " +
      "and that is said here rather than buried in the privacy policy.",
  },
];

/* Asked the first time somebody makes anything public, never at signup —
 * which is why it is not in CONSENTS, the list signup and the account
 * settings render. `PublishConsent.astro` shows it; the backend refuses a
 * publish with 428 until it has been agreed to.
 */
export const PUBLISH_CONSENT: ConsentSpec = {
  kind: "publish",
  label: "What happens to what I publish",
  wording:
    "I understand that what I make public on shrutivtuber.com — a guide, " +
    "a change to somebody's guide, a reading, a comment, a group, a " +
    "contribution to a group, a shared build — is read and relied on by " +
    "other people. If I delete my account, my account and everything " +
    "private go, and what I made public stays up with my name taken off " +
    "it. Copies already posted to Discord cannot be called back.",
  basis: "contract",
  required: false,
  explanation:
    "People follow a guide for weeks and answer each other's readings. " +
    "Deleting an account removes you, not the thing they are in the " +
    "middle of using. You are asked once, before the first thing you make " +
    "public, and it stays readable on your account page.",
};
